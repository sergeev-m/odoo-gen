from .steps import PlanStep
from odoo_gen.enums import WriteMode, StepAction


class PlanExecutor:
    def __init__(self, controllers=None, write_strategy=None):
        self.controllers = controllers
        self.write_strategy = write_strategy

    def execute(self, ctx):
        if not ctx.plan:
            return

        for step in ctx.plan:
            self._before_step(step, ctx)
            self._execute_step(step)
            self._after_step(step, ctx)

    # ---------- hooks ----------

    def _before_step(self, step: PlanStep, ctx):
        if self.controllers:
            self.controllers.before_step(step, ctx)

    def _after_step(self, step: PlanStep, ctx):
        if self.controllers:
            self.controllers.after_step(step, ctx)

    # ---------- actions ----------

    def _mkdir(self, step: PlanStep):
        step.path.mkdir(parents=True, exist_ok=True)

    def _write(self, step: PlanStep):
        exists = step.path.exists()
        
        mode = (
            self.write_strategy.resolve(step.mode, exists)
            if self.write_strategy
            else step.mode
        )

        if mode is None:
            return

        step.path.parent.mkdir(parents=True, exist_ok=True)

        if mode in (WriteMode.CREATE, WriteMode.OVERWRITE, WriteMode.MODIFY):
            step.path.write_text(step.content or '')
            return

        elif mode == WriteMode.APPEND:
            self._append(step)

    def _append(self, step: PlanStep):
        if step.path.exists():
            existing = step.path.read_text()
            if step.content and step.content in existing:
                return
            step.path.write_text(existing + (step.content or ""))
        else:
            step.path.write_text(step.content or "")

    def _execute_step(self, step: PlanStep):
        if step.action == StepAction.MKDIR:
            self._mkdir(step)

        elif step.action == StepAction.WRITE:
            self._write(step)
