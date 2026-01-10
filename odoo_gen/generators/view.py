from .base import BaseGenerator
from odoo_gen.core.context import ProjectContext
from odoo_gen.plan.steps import PlanStep, WriteMode


class ViewGenerator(BaseGenerator):
    priority = 40
    
    def is_applicable(self, ctx: ProjectContext) -> bool:
        return not ctx.no_views

    def plan(self, ctx: ProjectContext) -> list[PlanStep]:
        if not ctx.model:
            return []

        return [
            self._mkdir(ctx.views_dir),
            self._write(
                ctx.view_path,
                self._render_view(ctx),
                mode=WriteMode.CREATE,
                details=f"Create view {ctx.view_file_name}"
            ),
            self._write(
                ctx.manifest_path,
                self._render_manifest(ctx),
                mode=WriteMode.MODIFY,
                details="Update __manifest__.py (data section)"
            )
        ]
