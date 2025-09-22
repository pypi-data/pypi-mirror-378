from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from .session import Session
from .mappers import NodeMapper
from .nodes.node import BaseNode


T = TypeVar("T", bound=BaseNode)


class Repository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]) -> None:
        self.session = session
        self.model = model
        self.mapper = NodeMapper(model)

    def add(self, instance: T) -> T:
        self.session.uow.register_new(instance)
        # attach ogm hint for lazy relations
        self.session.attach_ogm_hint(instance)
        return instance

    def update(self, instance: T, match_by: Optional[Dict[str, Any]] = None) -> T:
        self.session.uow.register_dirty(instance)
        return instance

    def get(self, **filters: Any) -> Optional[T]:
        items = self.find(**filters)
        return items[0] if items else None

    def find(self, **filters: Any) -> List[T]:
        results = self.mapper.find(self.session.ogm(), **filters)
        for inst in results:
            self.session.attach_ogm_hint(inst)
            element_id = getattr(inst, "_element_id", None)
            if element_id:
                self.session.identity_map.set(self.model, element_id, inst)
        return results

    def delete(self, instance: T) -> None:
        self.session.uow.register_removed(instance)

    def commit_now(self) -> None:
        # Immediate commit option
        for obj in self.session.uow.new_objects:
            if isinstance(obj, self.model):
                self.mapper.insert(self.session.ogm(), obj)
        for obj in self.session.uow.dirty_objects:
            if isinstance(obj, self.model):
                self.mapper.update(self.session.ogm(), obj)
        self.session.uow.clear()
