from odoo_gen.enums import WriteMode
from .base import BaseGenerator
from odoo_gen.core.context import ProjectContext


class ModuleScaffoldGenerator(BaseGenerator):
    priority = 10
    
    def is_applicable(self, ctx: ProjectContext) -> bool:
        return ctx.create_module is True

    def plan(self, ctx):
        if not ctx.create_module:
            return []

        return [
            self._mkdir(ctx.module_path, "Create module"),
            self._mkdir(ctx.models_dir),
            self._mkdir(ctx.views_dir),
            self._mkdir(ctx.security_dir),

            self._write(
                ctx.manifest_path,
                self._render_manifest(ctx),
                mode=WriteMode.CREATE,
                details="Create __manifest__.py"
            ),
            self._write(
                ctx.module_path / "__init__.py",
                "from . import models\n",
                mode=WriteMode.CREATE,
            ),
            self._write(
                ctx.models_dir / "__init__.py",
                "",
                mode=WriteMode.CREATE,
            ),
        ]
