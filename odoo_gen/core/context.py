from dataclasses import dataclass
from pathlib import Path

from odoo_gen.core.manifest import ManifestEditor
from odoo_gen.plan.steps import PlanStep
from .menu_tree import MenuTree, MenuNode
from ..enums import MenuState
from .manifest import ManifestEditor


@dataclass(slots=True)
class ProjectContext:
    cwd: Path
    model: str
    
    inherit: bool = False
    
    debug: bool = False
    
    root: Path | None = None
    addons_path: Path | None = None
    module_name: str | None = None
    module_path: Path | None = None

    # intentions
    create_module: bool = False
    create_addons: bool = False
    addons_candidates: list[Path] | None = None
    module_candidates: list[Path] | None = None

    no_views: bool = False

    #menu
    menu_file: Path | None = None
    menu_tree: MenuTree | None = None
    menu_parent: MenuNode | None = None
    menu_index: int = 0
    menu_state: MenuState = MenuState.SKIP

    manifest: ManifestEditor | None = None
    
    plan: list[PlanStep] | None = None

    # -------- naming --------
    @property
    def model_class_name(self) -> str | None:
        return ''.join(
            part.capitalize()
            for part in self.model.replace('.', '_').split('_')
        )

    @property
    def model_str(self) -> str:
        return self.model.capitalize().replace('.', ' ').replace('_', ' ').replace('.', ' ')

    @property
    def model_underscore(self) -> str:
        return f'{self.model.replace('.', '_')}'

    @property
    def module_model(self) -> str:
        return f'{self.module_name}.{self.model}'

    @property
    def action_xml_id(self):
        return f'action_{self.model_underscore}'

    @property
    def menu_id(self):
        return f'menu_{self.model_underscore}'

    # -------- paths --------
    @property
    def models_dir(self) -> Path:
        return self.module_path / 'models'

    @property
    def views_dir(self) -> Path:
        return self.module_path / 'views'

    @property
    def security_dir(self) -> Path:
        return self.module_path / "security"

    @property
    def model_path(self) -> Path:
        return self.models_dir / f'{self.module_name}.{self.model_underscore}.py'

    @property
    def view_file_name(self) -> str:
        return f'{self.module_name}.{self.model_underscore}.xml'

    @property
    def view_path(self) -> Path:
        return self.views_dir / self.view_file_name

    @property
    def menu_xml_path(self) -> Path | None:
        return self.views_dir / 'menu.xml'

    @property
    def manifest_path(self) -> Path:
        return self.module_path / "__manifest__.py"

    # resolver helpers
    @property
    def has_addons(self) -> bool:
        return self.addons_path is not None

    @property
    def has_module(self) -> bool:
        return self.module_path is not None

    @property
    def has_menu(self) -> bool:
        return self.menu_state != MenuState.NEED
