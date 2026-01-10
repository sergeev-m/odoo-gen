import questionary

from pathlib import Path
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import TextArea

from odoo_gen.core.context import ProjectContext
from odoo_gen.core.menu_tree import MenuNode, MenuTree
from .base import BaseController
from ..core.signals import (
    ChooseAddons,
    ChooseModule,
    CreateModule,
    RequireAddonsPath,
    RequireModulePath,
    RequireMenuPlacement,
)


class InteractiveController(BaseController):
    def on_signal(self, signal, ctx: ProjectContext):
        if isinstance(signal, RequireAddonsPath):
            return self._handle_addons_not_found(ctx)

        if isinstance(signal, ChooseAddons) :
            return self._handle_ambiguous_addons(signal.paths, ctx)

        if isinstance(signal, RequireModulePath):
            return self._handle_missing_module(ctx)

        if isinstance(signal, CreateModule):
            return self._handle_missing_module(ctx, signal.path)

        if isinstance(signal, ChooseModule):
            return self._handle_ambiguous_modules(signal.modules, ctx)

        if isinstance(signal, RequireMenuPlacement):
            return self._handle_menu_placement(ctx)

        return False

    def _handle_addons_not_found(self, ctx):
        if self._confirm('addons directory not found. Create it?'):
            ctx.create_addons = True
        return True

    def _handle_ambiguous_addons(self, paths: list[Path], ctx):
        result = self._select_from_list(paths, 'Select addons directory')
        ctx.addons_path = result
        return True

    def _handle_missing_module(self, ctx, path: Path | None = None):
        module_name = path.name if path else ''
        msg = 'Module %snot found. Create it?' % (f'{module_name} ' or '')

        if self._confirm(msg):
            if not module_name:
                module_name = input('input module name:')
            
            if module_name and ctx.addons_path:
                ctx.module_name = module_name
                ctx.module_path = ctx.addons_path / module_name
                ctx.create_module = True
        return True

    def _handle_ambiguous_modules(self, modules: list[Path], ctx):
        module_path = self._select_from_list(modules, 'Select module')
        ctx.module_path = module_path
        ctx.module_name = module_path.name
        return True

    def _confirm(self, text: str) -> bool:
        if not questionary.confirm(text).ask():
            raise SystemExit(1)
        return True

    def _select_from_list(self, items, title):
        choices = [
            questionary.Choice(
                title=str(p),
                value=p,
                shortcut_key=str(i),
            )
            for i, p in enumerate(items, 1)
        ]

        choices.append(
            questionary.Choice(
                title="Cancel",
                value=False,
                shortcut_key="q",
            )
        )

        result = questionary.select(
            title,
            choices=choices,
            use_shortcuts=True,
        ).ask()

        if not result:
            raise SystemExit(0)
        
        return result

    def _handle_menu_placement(self, ctx):
        ui = InteractiveMenuInserter(ctx)
        ui.run()
        return True


class InteractiveMenuInserter:
    def __init__(self, ctx: ProjectContext):
        self.ctx = ctx
        self.tree: MenuTree = ctx.menu_tree

        self.expanded: set[str] = {n.id for n in self.tree.nodes}
        self.visible: list[MenuNode] = []
        self.cursor: int = 0
        self.parent: MenuNode | None = None
        
        self.output = TextArea(
            text="",
            read_only=True,
            scrollbar=True,
            wrap_lines=False,
        )
        container = HSplit([self.output])
        kb = self._bindings()
        self.app = Application(
            layout=Layout(container),
            key_bindings=kb,
            mouse_support=True,
            full_screen=True,
        )

        self._rebuild_visible()
        self._refresh()

    # ---------------- build visible ----------------
    def _rebuild_visible(self):
        self.visible = []

        def walk(node):
            self.visible.append(node)
            if node.id in self.expanded:
                for c in node:
                    walk(c)

        for n in self.tree.nodes:
            walk(n)

        self._sync_cursor()
    
    def _refresh(self):
        self._rebuild_visible()
        self._sync_cursor()
        self.output.text = self._render()

    # ---------------- render ----------------
    def _render(self) -> str:
        lines: list[str] = []

        if self.ctx.debug:
            lines.append(
                f"cursor={self.cursor}\n"
                f"parent={self.parent}\n"
            )

        if self.parent is None:
            self._render_parent_selection(lines)
            lines.append("")
            lines.append("Press Enter to select parent menu")
        else:
            self._render_index_selection(lines)
            lines.append("")
            lines.append("Press Enter to confirm index")

        return "\n".join(lines)

    def _render_parent_selection(self, lines):
        for i, node in enumerate(self.visible):
            lines.append(self._draw_node(node, highlight=(i == self.cursor)))

    def _render_index_selection(self, lines):
        parent = self.parent
        idx = self.cursor
        children = parent.children

        for node in self.visible:
            if node.parent is parent:
                pos = children.index(node)
                if pos == idx:
                    lines.append(self._draw_preview(node.depth))

            lines.append(self._draw_node(node))

            if node is parent and not children:
                lines.append(self._draw_preview(node.depth + 1))

            if node.parent is parent:
                pos = children.index(node) + 1
                if pos == idx and idx == len(children):
                    lines.append(self._draw_preview(parent.depth + 1))

    def _draw_node(self, node, highlight=False):
        pref = "│  " * node.depth
        mark = "▶ " if highlight else "  "
        arrow = (
            "▾" if node.children and node.id in self.expanded
            else "▸" if node.children
            else " "
        )
        name = node.attrs.get("name", node.id)
        return f"{mark}{pref}{arrow} {name}"

    def _draw_preview(self, depth):
        return "  " + "│  " * depth + ">>> INSERT HERE <<<"

    # ---------------- helpers ----------------
    def _sync_cursor(self):
        if self.parent is None:
            self.cursor = max(0, min(self.cursor, len(self.visible) - 1))
        else:
            self.cursor = max(0, min(self.cursor, len(self.parent.children)))

    # ---------------- keys ----------------
    def _bindings(self):
        kb = KeyBindings()

        @kb.add("up")
        def _(e):
            self.cursor -= 1
            self._refresh()

        @kb.add("down")
        def _(e):
            self.cursor += 1
            self._refresh()

        @kb.add("right")
        def _(e):
            if self.parent is None:
                el = self.visible[self.cursor]
                if len(el):
                    self.expanded.add(el.id)
                    self._refresh()

        @kb.add("left")
        def _(e):
            if self.parent is None:
                el = self.visible[self.cursor]
                if len(el):
                    self.expanded.discard(el.id)
                    self._refresh()

        @kb.add("enter")
        def _(e):
            if self.parent is None:
                self.parent = self.visible[self.cursor]
                self.expanded.add(self.parent.id)
                self.cursor = 0
                self._refresh()
            else:
                self._confirm()
                e.app.exit(True)
        
        @kb.add("q")
        @kb.add("c-c")
        def _(e):
            "Quit when control-c or q is pressed."
            e.app.exit()
            raise SystemExit
        
        @kb.add('d')
        def _(e):
            "Delete"
            el = self.visible[self.cursor]
            if el.parent:
                el.parent.remove(el)
            self._refresh()
        
        return kb
    
    # ---------------- insert ----------------
    def _confirm(self):
        self.ctx.menu_parent = self.parent
        self.ctx.menu_index = self.cursor

    # ---------------- run ----------------
    def run(self):
        self.app.run()
