from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from lxml import etree as ET


@dataclass
class MenuNode:
    id: str
    attrs: dict
    parent: Optional['MenuNode'] = None
    parent_id: Optional[str] = None
    children: list['MenuNode'] = field(default_factory=list)
    el: Optional[ET._Element] = None
    comments_before: list[ET._Comment] = field(default_factory=list)

    def index(self, node: 'MenuNode'):
        return self.children.index(node)

    def insert(self, index: int, node: 'MenuNode'):
        node.parent = self
        self.children.insert(index, node)
        self._recompute_seq()

    def remove(self, node):
        if node in self.children:
            self.children.remove(node)
            node.parent = None

    def _recompute_seq(self):
        seq = 10
        for node in self.children:
            node.attrs['sequence'] = str(seq)
            seq += 10

    @property
    def sequence(self) -> int:
        return int(self.attrs.get("sequence", 0))

    @property
    def depth(self) -> int:
        if self.parent:
            return self.parent.depth + 1
        return 0

    def __str__(self):
        name = self.__repr__()
        return f"{'  ' * self.depth}{name} ({self.id})"
    
    def __repr__(self) -> str:
        name = self.attrs.get("name", self.id)
        return name

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        for c in self.children:
            yield c


class MenuTree:
    def __init__(
        self,
        path: Path,
        remove_blank_text=True,
        remove_comments=False
    ):
        parser = ET.XMLParser(
            remove_blank_text=remove_blank_text,
            remove_comments=remove_comments
        )
        self.xml_tree = ET.parse(path, parser)
        self.root = self.xml_tree.getroot()

        self.nodes_by_id = {}
        self.nodes = []

        self._parse()

    @classmethod
    def empty(cls):
        self = cls.__new__(cls)
        self.xml_tree = None
        self.root = ET.Element("odoo")
        self.nodes_by_id = {}
        self.nodes = []
        return self

    def is_empty(self) -> bool:
        return not self.nodes

    def add_root(self, node: MenuNode):
        self.nodes.append(node)

    def add_child(self, parent: MenuNode, node: MenuNode):
        parent.children.append(node)
        node.parent = parent

    def insert(self, parent: MenuNode, index: int, node: MenuNode):
        parent.insert(index, node)

    def _parse(self) -> None:
        pending_comments = []

        for el in self.root.iter():
            if isinstance(el, ET._Comment):
                pending_comments.append(el)
                continue

            if el.tag != "menuitem":
                continue

            menu_id = el.get("id")
            if not menu_id:
                continue

            parent_id = el.get("parent")

            if parent_id is None:
                parent_el = el.getparent()
                if (
                    parent_el is not None
                    and parent_el.tag == "menuitem"
                    and parent_el.get("id")
                ):
                    parent_id = parent_el.get("id")

            node = MenuNode(
                id=menu_id,
                attrs=el.attrib,
                el=el,
                parent_id=parent_id,
                comments_before=pending_comments,
            )

            pending_comments = []

            if menu_id not in self.nodes_by_id:
                self.nodes_by_id[menu_id] = node

        self._build_tree()

    def _build_tree(self):
        for node in self.nodes_by_id.values():
            if node.parent_id and node.parent_id in self.nodes_by_id:
                parent = self.nodes_by_id[node.parent_id]
                node.parent = parent
                parent.children.append(node)
            else:
                self.nodes.append(node)

        for node in self.nodes_by_id.values():
            node.children.sort(key=lambda n: n.sequence)

        self.nodes.sort(key=lambda n: n.sequence)

    def to_lxml(self) -> ET.Element:
        odoo = ET.Element("odoo")

        for node in self.nodes:
            self._append_node(odoo, node)

        return odoo

    def _append_node(self, parent_el: ET.Element, node: MenuNode):
        for c in node.comments_before:
            if isinstance(c, str):
                parent_el.append(ET.Comment(c))
            else:
                parent_el.append(ET.Comment(c.text))

        el = ET.Element("menuitem", **node.attrs)
        parent_el.append(el)

        for child in node.children:
            self._append_node(el, child)

    def serialize(self) -> str:
        root = self.to_lxml()
        return ET.tostring(
            root,
            pretty_print=True,
            encoding="utf-8",
            xml_declaration=True,
        ).decode("utf-8")

    def getchildren(self):
        out = []

        def walk(nodes):
            for n in nodes:
                out.append(n)
                walk(n.children)

        walk(self.nodes)
        return out

    def __iter__(self):
        for el in self.getchildren():
            yield el
