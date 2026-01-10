from .base import BaseGenerator
from odoo_gen.plan.steps import WriteMode
from odoo_gen.core.context import ProjectContext
from odoo_gen.plan.steps import PlanStep


class AccessGenerator(BaseGenerator):
    priority = 30

    def generate(self):
        pass

    def is_applicable(self, ctx: ProjectContext) -> bool:
            return bool(ctx.model)

    def plan(self, ctx: ProjectContext) -> list[PlanStep]:
        if not ctx.module_path:
            return []

        return [
            self._write(
                ctx.security_dir / 'ir.model.access.csv',
                self._render_access(ctx),
                mode=WriteMode.APPEND,
                details='Update access.csv'
            ),
        ]
