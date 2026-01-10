from ..errors import AddonsPathNotFound
from .context import ProjectContext
from ..controllers import ControllerChain
from .menu_tree import MenuTree, MenuNode
from ..enums import MenuState
from .signals import (
    Signal,
    RequireAddonsPath,
    ChooseAddons,
    CreateModule,
    RequireModulePath,
    ChooseModule,
    RequireMenuPlacement,
)
from .types import Result, Ok, Err
from .manifest import ManifestEditor


class ContextResolver:
    ADDONS_DIRS = {'addons', 'custom_addons'}
    MAX_ROOT_DEPTH = 4

    def __init__(self, controllers: ControllerChain | None = None):
        self.controllers = controllers
        self.steps = [
            '_resolve_addons',
            '_resolve_missing_module_intent',
            '_resolve_module',
            '_resolve_menu',
            '_resolve_manifest',
            '_validate'
        ]

    def resolve(self, ctx: ProjectContext) -> Result[ProjectContext, Signal]:
        for step_name in self.steps:
            step = getattr(self, step_name)
            if not step:
                continue

            res = step(ctx)
            if isinstance(res, Err):
                return res

        return Ok(ctx)

    def _resolve_addons(self, ctx: ProjectContext):
        
        if ctx.has_addons:
            return Ok(None)

        if ctx.create_addons:
            ctx.addons_path = ctx.cwd / 'addons'
            return

        p = ctx.cwd
        depth = 0
        addons_candidates = []

        while p != p.parent and depth < self.MAX_ROOT_DEPTH:
            # inside module
            if (p / "__manifest__.py").exists():
                ctx.module_path = p
                ctx.module_name = p.name
                ctx.root = p.parent.parent
                addons_candidates = [p.parent]
                break

            # inside addons
            if p.name in self.ADDONS_DIRS:
                ctx.root = p.parent
                addons_candidates = [p]
                break

            # root containing addons dirs
            found = [
                p / name for name in self.ADDONS_DIRS
                if (p / name).exists()
            ]
            if found:
                ctx.root = p
                addons_candidates = found
                break

            p = p.parent
            depth += 1

        if not addons_candidates:
            return Err(RequireAddonsPath())

        if len(addons_candidates) == 1:  # todo auto in signals?
            ctx.addons_path = addons_candidates[0]
        else:
            return Err(ChooseAddons(paths=addons_candidates))

    def _resolve_missing_module_intent(self, ctx: ProjectContext):
        if ctx.has_module:
            return Ok(None)

        p = ctx.cwd

        if p.exists():
            return

        if ctx.addons_path is None:
            return

        if p.parent == ctx.addons_path:
            return Err(CreateModule(path=p))
        # todo -> _resolve_module flow

    def _resolve_module(self, ctx: ProjectContext):
        if ctx.has_module:
            return Ok(None)

        if ctx.addons_path is None:
            raise AddonsPathNotFound 

        modules = []
        if ctx.addons_path.exists():
            modules = [
                p for p in ctx.addons_path.iterdir()
                if p.is_dir() and (p / "__manifest__.py").exists()
            ]

        if not modules:
            return Err(RequireModulePath())

        if len(modules) == 1:
            ctx.module_path = modules[0]
            ctx.module_name = modules[0].name
            return
        return Err(ChooseModule(modules=modules))

    def _resolve_menu(self, ctx: ProjectContext):
        if ctx.has_menu:
            return Ok(None)

        # insert node
        if ctx.menu_tree and ctx.menu_parent is not None:
            ctx.menu_tree.insert(
                parent=ctx.menu_parent,
                index=ctx.menu_index,
                node=self._menu_node(ctx)
            )
            ctx.menu_state = MenuState.READY
            return Ok(ctx)

        # parse
        path = ctx.menu_xml_path
        if path and path.exists():
            tree = MenuTree(path)
            if not tree.is_empty():
                ctx.menu_tree = tree
                return Err(RequireMenuPlacement())

        # new menu
        self._create_default_menu(ctx)
        ctx.menu_state = MenuState.READY
        return Ok(None)

    def _create_default_menu(self, ctx: ProjectContext) -> None:
        tree = MenuTree.empty()
        root_menu = MenuNode(
            id=f'{ctx.module_name}_root',
            attrs={
                "id": f'{ctx.module_name}_root',
                "name": ctx.module_name.replace('_', ' ').capitalize(),
            },
            comments_before=['Top menu item']
        )

        model_menu = self._menu_node(ctx, root_menu)
        root_menu.insert(0, model_menu)
        tree.add_root(root_menu)
        ctx.menu_tree = tree

    def _menu_node(self, ctx: ProjectContext, parent=None) -> MenuNode:
        return MenuNode(
            id=ctx.menu_id,
            attrs={
                "id": ctx.menu_id,
                "name": ctx.model_str,
                "action": ctx.action_xml_id,
            },
            parent=parent
        )

    def _validate(self, ctx: ProjectContext):
        if not ctx.addons_path:
            raise RuntimeError("addons_path unresolved")

        if not ctx.module_path and not ctx.create_module:
            raise RuntimeError("module unresolved")

    def _step(self, name: str, ctx: ProjectContext):
        if self.controllers:
            self.controllers.on_step(name, ctx)

    def _resolve_manifest(self, ctx: ProjectContext):
        path = ctx.manifest_path
        if not path.exists():
            return

        ctx.manifest = ManifestEditor(path)
        ctx.manifest.ensure_data_item(
            f'views/{ctx.view_file_name}',
            before="views/menu.xml",
        )
