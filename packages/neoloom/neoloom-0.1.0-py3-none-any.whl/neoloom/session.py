from __future__ import annotations

from typing import Any, Dict, Optional, Type, TypeVar, Generic, List

from neo4j import Driver

from .db import Neo4jOGM


T = TypeVar("T")


class IdentityMap:
    def __init__(self) -> None:
        self._node_cache: Dict[str, Any] = {}

    @staticmethod
    def _key(model_cls: Type[Any], element_id: str) -> str:
        return f"{model_cls.__name__}:{element_id}"

    def get(self, model_cls: Type[T], element_id: Optional[str]) -> Optional[T]:
        if not element_id:
            return None
        return self._node_cache.get(self._key(model_cls, element_id))

    def set(self, model_cls: Type[T], element_id: str, instance: T) -> None:
        self._node_cache[self._key(model_cls, element_id)] = instance


class UnitOfWork:
    def __init__(self) -> None:
        self.new_objects: List[Any] = []
        self.dirty_objects: List[Any] = []
        self.removed_objects: List[Any] = []

    def register_new(self, obj: Any) -> None:
        self.new_objects.append(obj)

    def register_dirty(self, obj: Any) -> None:
        self.dirty_objects.append(obj)

    def register_removed(self, obj: Any) -> None:
        self.removed_objects.append(obj)

    def clear(self) -> None:
        self.new_objects.clear()
        self.dirty_objects.clear()
        self.removed_objects.clear()


class Session:
    """
    Session coordinates Unit of Work and provides an identity map.
    Wraps a Neo4j driver and exposes a high-level API for repositories/mappers.
    """

    def __init__(
        self,
        driver: Driver = None,
        uri: str = None,
        user: str = None,
        password: str = None,
    ) -> None:
        self._ogm = Neo4jOGM(
            uri=uri, user=user, password=password, graph_driver=driver
        )  # Query builder + executor
        self.identity_map = IdentityMap()
        self.uow = UnitOfWork()

    def ogm(self) -> Neo4jOGM:
        return self._ogm

    def begin(self) -> "Session":
        return self

    def commit(self) -> None:
        # Naive commit: insert new, update dirty, delete removed
        for obj in self.uow.new_objects:
            # Domain models are expected to expose a .save(ogm) for now
            obj.save(self._ogm)
        for obj in self.uow.dirty_objects:
            obj.save(self._ogm, update=True)
        # Deletions can be implemented in future
        self.uow.clear()

    def rollback(self) -> None:
        self.uow.clear()

    def close(self) -> None:
        self._ogm.close()

    # Convenience to get a repository for a model
    def repository_for(self, model_cls: Type[T]):
        from .repository import Repository

        return Repository(self, model_cls)

    # Optional hint: attach OGM to instances for lazy relations
    def attach_ogm_hint(self, instance: Any) -> None:
        setattr(instance, "_ogm_hint", self._ogm)
