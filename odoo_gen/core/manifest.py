import ast

from pathlib import Path

from odoo_gen.errors import ManifestParseError


class ManifestEditor:
    def __init__(self, path: Path):
        self.path = path
        self.raw = path.read_text()
        self.tree = ast.parse(self.raw)

        if len(self.tree.body) != 1 or not isinstance(self.tree.body[0], ast.Expr):
            raise ManifestParseError("Manifest must be a single dict expression")

        expr = self.tree.body[0].value
        if not isinstance(expr, ast.Dict):
            raise ManifestParseError("Manifest is not a dict")

    # ---------- public API ----------
    def ensure_data_item(
        self,
        value: str,
        *,
        after: str | None = None,
        before: str | None = None,
    ):
        data_node = self._find_data_node()
        if not data_node:
            raise ManifestParseError("data key not found in manifest")

        data_src = ast.get_source_segment(self.raw, data_node)
        if not data_src:
            raise ManifestParseError("cannot extract data source")

        lines = data_src.splitlines()

        if any(value in line for line in lines):
            return  # already exists

        new_line = self._format_item(value, lines)

        if before:
            lines = self._insert_before(lines, before, new_line)
        elif after:
            lines = self._insert_after(lines, after, new_line)
        else:
            lines.insert(-1, new_line)

        new_data_src = "\n".join(lines)
        self.raw = self.raw.replace(data_src, new_data_src)

    # ---------- internals ----------
    def _find_data_node(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Dict):
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value == "data":
                        return v
        return None

    def _format_item(self, value: str, lines: list[str]) -> str:
        indent = self._detect_indent(lines)
        return f'{indent}"{value}",'

    def _detect_indent(self, lines: list[str]) -> str:
        for line in lines[1:]:
            stripped = line.lstrip()
            if stripped and stripped.startswith(("'", '"')):
                return line[: len(line) - len(stripped)]
        return "    "

    def _insert_after(self, lines: list[str], after: str, new_line: str):
        for i, line in enumerate(lines):
            if after in line:
                return lines[: i + 1] + [new_line] + lines[i + 1 :]
        return lines[:-1] + [new_line] + [lines[-1]]

    def _insert_before(self, lines: list[str], before: str, new_line: str) -> list[str]:
        for i, line in enumerate(lines):
            if before in line:
                return lines[:i] + [new_line] + lines[i:]

        lines.insert(-1, new_line)
        return lines
