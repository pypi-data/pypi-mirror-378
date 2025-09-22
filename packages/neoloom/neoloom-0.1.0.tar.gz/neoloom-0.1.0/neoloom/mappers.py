from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, TypeVar

from .db import Neo4jOGM
from .nodes.node import BaseNode


T = TypeVar("T", bound=BaseNode)


class NodeMapper:
    def __init__(self, model: Type[T]) -> None:
        self.model = model

    def _label(self) -> str:
        return self.model.__name__

    def insert(self, ogm: Neo4jOGM, instance: T) -> T:
        props: Dict[str, Any] = {
            key: getattr(instance, key) for key, field in instance._fields.items()
        }
        ogm.create_node(
            alias=self._label().lower(), label=self._label(), properties=props
        ).execute()
        return instance

    def update(
        self, ogm: Neo4jOGM, instance: T, match_by: Optional[Dict[str, Any]] = None
    ) -> T:
        if not match_by:
            # default: use unique fields if present
            match_by = {
                k: getattr(instance, k)
                for k in instance._fields.keys()
                if k in getattr(instance, "_BaseNode__unique__", [])
            }
        if not match_by:
            raise ValueError(
                "No match_by provided and no unique fields available for update"
            )
        ogm.match_node(alias=self._label().lower(), label=self._label()).filter(
            self._label().lower(), match_by
        )
        set_props: Dict[str, Any] = {
            key: getattr(instance, key) for key in instance._fields.keys()
        }
        ogm.set_properties(alias=self._label().lower(), properties=set_props).execute()
        return instance

    def find(self, ogm: Neo4jOGM, **filters: Any) -> List[T]:
        records = (
            ogm.match_node(alias=self._label().lower(), label=self._label())
            .filter(alias=self._label().lower(), filters=filters)
            .return_(self._label().lower() + "{.*}")
            .execute()
        )
        results: List[T] = []
        for record in records:
            data = record[self._label().lower()]
            instance = self.model.deserialize(data)
            element_id = (
                data.get("id") or data.get("element_id") or data.get("elementId")
            )
            if element_id:
                setattr(instance, "_element_id", element_id)
            results.append(instance)
        return results
