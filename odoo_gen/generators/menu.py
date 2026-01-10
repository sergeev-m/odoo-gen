from .base import BaseGenerator
from odoo_gen.core.context import ProjectContext
from odoo_gen.enums import WriteMode
from odoo_gen.enums import MenuState


class MenuGenerator(BaseGenerator):
    priority = 40

    def is_applicable(self, ctx: ProjectContext) -> bool:
        return ctx.menu_state != MenuState.SKIP
    
    def plan(self, ctx: ProjectContext):
        if not self.is_applicable(ctx) or not ctx.menu_tree:
            return []

        return [
            self._write(
                path=ctx.menu_xml_path,
                content=ctx.menu_tree.serialize(),
                mode=WriteMode.MODIFY,
                details=f"Create menu item"
            ),
        ]
