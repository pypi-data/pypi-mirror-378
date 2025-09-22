from __future__ import annotations

from typing import Any, Callable, Iterable, List


class LazyRelationshipProxy(Iterable):
    def __init__(self, loader: Callable[[], List[Any]]) -> None:
        self._loader = loader
        self._loaded = False
        self._items: List[Any] = []

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._items = list(self._loader() or [])
            self._loaded = True

    def __iter__(self):
        self._ensure_loaded()
        return iter(self._items)

    def __len__(self) -> int:
        self._ensure_loaded()
        return len(self._items)

    def __getitem__(self, index: int) -> Any:
        self._ensure_loaded()
        return self._items[index]
