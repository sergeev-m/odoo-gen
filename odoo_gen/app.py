import click
from pathlib import Path

from odoo_gen.plan.executor import PlanExecutor
from odoo_gen.plan.strategies import WriteStrategy

from . import generators as gn
from .errors import OdooGenError
from .core.context import ProjectContext
from .core.resolver import ContextResolver
from .core.types import Ok, Err
from .controllers import (
    ControllerChain,
    InteractiveController,
    VerboseController,
)
from .enums import MenuState


class OdooGenApp:
    def __init__(
        self,
        *,
        model,
        path,
        verbose,
        menu,
        no_views,
        force,
        skip_existing,
        debug
    ) -> None:
        self.debug = debug
        self.ctx = ProjectContext(
            cwd=Path(path).resolve() if path else Path.cwd(),
            model=model,
            menu_state=MenuState.NEED if menu else MenuState.SKIP,
            no_views=no_views,
            debug=debug
        )

        self.controllers = ControllerChain([
            InteractiveController(),
            VerboseController() if verbose else None,
        ])

        self.resolver = ContextResolver(self.controllers)
        self.generators = [
            gn.ModuleScaffoldGenerator(),
            gn.ModelGenerator(),
            gn.AccessGenerator(),
            gn.ViewGenerator(),
            # gn.MenuGenerator() if menu else None,
            gn.MenuGenerator(),
        ]
        self.write_strategy = WriteStrategy(
            force=force,
            skip=skip_existing,
        )

    def run(self):
        try:
            self._run_signal_loop()
            self._build_plan()
            self._execute()
        except OdooGenError as e:
            click.secho(str(e), fg="red")
            raise SystemExit(1)
        except FileExistsError as e:
            click.secho(
                (
                    f'file {str(e)} already exist, use flag:\n'
                    '   --skip-existing\n'
                    '   -f or --force for overwrite existing files'
                ), fg="red"
            )
        except Exception as e:
            if self.debug:
                raise
            click.secho("Unexpected error", fg="red")
            click.secho(str(e), fg="red")
            raise SystemExit(1)

    def _run_signal_loop(self):
        while True:
            result = self.resolver.resolve(self.ctx)

            match result:
                case Ok(value=ctx):
                    self.ctx = ctx
                    break

                case Err(error=signal):
                    if (
                        signal.can_auto_resolve(self.ctx)
                        and signal.auto_resolve(self.ctx)
                    ):
                        continue

                    if self.controllers.handle_signal(signal, self.ctx):
                        continue

                    raise OdooGenError(str(signal))

    def _execute(self):
        self.controllers.before_generate(self.ctx)

        executor = PlanExecutor(
            controllers=self.controllers,
            write_strategy=self.write_strategy,
        )
        executor.execute(self.ctx)

        self.controllers.after_generate(self.ctx)

    def _build_plan(self):
        gens = [
            (i, g)
            for i, g in enumerate(self.generators)
            if g and g.is_applicable(self.ctx)
        ]

        gens.sort(key=lambda x: (x[1].priority, x[0]))

        plan = []
        for _, gen in gens:
            plan.extend(gen.plan(self.ctx))

        self.ctx.plan = plan
        return plan
