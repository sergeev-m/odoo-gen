from .base import BaseGenerator
from odoo_gen.plan.steps import WriteMode
from odoo_gen.core.context import ProjectContext
from odoo_gen.plan.steps import PlanStep


class ModelGenerator(BaseGenerator):
    priority = 20

    def is_applicable(self, ctx: ProjectContext) -> bool:
        return bool(ctx.model)

    def plan(self, ctx: ProjectContext) -> list[PlanStep]:
        if not ctx.model:
            return []

        return [
            self._mkdir(ctx.models_dir),
            self._write(
                ctx.model_path,
                self._render_model(ctx),
                mode=WriteMode.CREATE,
                details=f"Create model {ctx.model_underscore}"
            ),
            self._write(
                ctx.models_dir / "__init__.py",
                f"from . import {ctx.module_model}\n",
                mode=WriteMode.APPEND,
                details=f"Update models __init__"
            ),
        ]

    def generate(self, ctx: ProjectContext):
        pass  # todo plan --> generate
