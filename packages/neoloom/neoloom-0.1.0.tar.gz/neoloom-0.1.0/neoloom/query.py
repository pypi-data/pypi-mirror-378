from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple, Type

from .db import Neo4jOGM
from .nodes.node import BaseNode


@dataclass(frozen=True)
class Q:
    # Simple Q object supporting AND/OR for future expansion
    conditions: Tuple[Tuple[str, Any], ...]
    operator: str = "AND"

    def __and__(self, other: "Q") -> "Q":
        return Q(self.conditions + other.conditions, operator="AND")

    def __or__(self, other: "Q") -> "Q":
        return Q(self.conditions + other.conditions, operator="OR")

    @staticmethod
    def from_kwargs(**kwargs: Any) -> "Q":
        return Q(tuple(kwargs.items()))


def apply_q_to_ogm(ogm, alias: str, q: Q) -> None:
    condition_type = "AND"
    for key, value in q.conditions:
        # support simple lookups like field__gt
        if "__" in key:
            field, op = key.split("__", 1)
            operator = {
                "gt": "gt",
                "gte": "gte",
                "lt": "lt",
                "lte": "lte",
                "eq": "eq",
            }.get(op, "eq")
            ogm.where(
                alias=alias,
                field=field,
                operator=operator,
                value=value,
                condition_type=condition_type,
            )
        else:
            ogm.filter(alias=alias, filters={key: value}, condition_type=condition_type)
        if q.operator == "OR":
            condition_type = "OR"


class QuerySet(Iterable):
    def __init__(self, model: Type[BaseNode], ogm: Neo4jOGM) -> None:
        self.model = model
        self._ogm = ogm
        self._alias = model.__name__.lower()
        self._q: List[Q] = []
        self._order_by: List[Tuple[str, bool]] = []
        self._limit: int | None = None

    def filter(self, q: Q | None = None, **kwargs: Any) -> "QuerySet":
        if q is None and kwargs:
            q = Q.from_kwargs(**kwargs)
        if q is not None:
            self._q.append(q)
        return self

    def order_by(self, *fields: str) -> "QuerySet":
        for f in fields:
            if f.startswith("-"):
                self._order_by.append((f[1:], False))
            else:
                self._order_by.append((f, True))
        return self

    def limit(self, n: int) -> "QuerySet":
        self._limit = n
        return self

    def _build(self):
        ogm = self._ogm
        ogm.match_node(alias=self._alias, label=self.model.__name__)
        # Apply all Qs with AND/OR semantics
        for q in self._q:
            apply_q_to_ogm(ogm, self._alias, q)
        if self._order_by:
            for field, asc in self._order_by:
                ogm.order_by(self._alias, field, ascending=asc)
        if self._limit is not None:
            ogm.limit(self._limit)
        ogm.return_(self._alias + "{.*}")

    def __iter__(self):
        self._build()
        rows = self._ogm.execute()
        for row in rows:
            yield self.model.deserialize(row[self._alias])
