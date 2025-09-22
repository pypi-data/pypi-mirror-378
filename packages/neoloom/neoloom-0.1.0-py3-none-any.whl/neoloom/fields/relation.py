from typing import Any

from neoloom.fields.base import BaseRelation
from neoloom.nodes.node import BaseNode


class Relationship(BaseRelation):
    def __init__(self, related_node: Any = BaseNode, rel_type: str = None, type_: Any = None, default=None,
                 nullable=True, direction="->", **kwargs):
        super().__init__(related_node, **kwargs)
