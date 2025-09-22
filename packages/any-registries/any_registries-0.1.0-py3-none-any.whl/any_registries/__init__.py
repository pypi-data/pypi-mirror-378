from __future__ import annotations

from collections.abc import Callable, Iterable
import os
from pathlib import Path
from typing import Generic, Self, TypeVar
from .exceptions import ItemNotRegistered
TYPE_KEY = TypeVar("TYPE_KEY")
TYPE_TARGET = TypeVar("TYPE_TARGET")


class Registry(Generic[TYPE_KEY, TYPE_TARGET]):
    def __init__(
        self: Self,
        base_path: str | None = None,
        auto_loads: list | None = None,
        key: Callable | None = None,
        lazy_load: bool = True,
    ) -> None:
        self._registry: dict[TYPE_KEY, TYPE_TARGET] = {}
        self._loaded = False
        self.auto_loads = auto_loads or []
        self.key_getter = key
        self.base_path = os.environ.get("PROJECT_ROOT") or os.environ.get("BASE_DIR") or base_path or os.getcwd()
        if not lazy_load:
            self._ensure_loaded()

    def auto_load(self: Self, *patterns: str) -> Self:
        self.auto_loads.extend(patterns)
        self._loaded = False
        return self

    def force_load(self: Self) -> Registry:
        return self._ensure_loaded()

    def _ensure_loaded(self: Self) -> Self:
        if not self._loaded and self.auto_loads:
            from importlib import import_module

            modules = []
            for pattern in self.auto_loads:
                modules += Path(self.base_path).glob(pattern)

            for f in modules:
                if f.is_file() and not f.name.endswith("__init__.py"):
                    module_path = Path(f).relative_to(self.base_path)
                    module_namespace = ".".join(module_path.with_suffix("").parts)
                    import_module(module_namespace)
            self._loaded = True
        return self

    def register(
        self: Self,
        key: Iterable[TYPE_KEY] | TYPE_KEY | None = None,
        multiple_keys: bool = False,
    ) -> Callable:
        def registry(target: TYPE_TARGET) -> TYPE_TARGET:
            if self.key_getter and key is None:
                self._registry[self.key_getter(target)] = target
            elif multiple_keys and isinstance(key, Iterable):
                for k in key:
                    self._registry[k] = target
            else:
                self._registry[key] = target
            return target

        return registry

    @property
    def registry(self: Self) -> dict[TYPE_KEY, TYPE_TARGET]:
        self._ensure_loaded()
        return self._registry

    def get(self: Self, key: TYPE_KEY) -> TYPE_TARGET:
        self._ensure_loaded()
        try:
            return self._registry[key]
        except KeyError as e:
            raise ItemNotRegistered(f"Item with key '{key}' is not registered.") from e
