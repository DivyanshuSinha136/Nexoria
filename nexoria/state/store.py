"""
nexoria.state.store
=====================
Minimal reactive state primitive. `State` behaves like a dict but notifies
subscribers (usually a Component's re-render scheduler) on mutation.
For simple cases, `use_state()` gives a hook-style pair, mirroring the
ergonomics of modern JS frameworks while staying pure Python.
"""

from __future__ import annotations
from typing import Any, Callable, Iterator


class State:
    def __init__(self, initial: dict | None = None):
        self._data: dict[str, Any] = dict(initial or {})
        self._subscribers: list[Callable[[], None]] = []

    def _on_change(self, callback: Callable[[], None]) -> None:
        self._subscribers.append(callback)

    def _notify(self) -> None:
        for cb in self._subscribers:
            cb()

    def update(self, **kwargs: Any) -> None:
        self._data.update(kwargs)
        self._notify()

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._notify()

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def to_dict(self) -> dict:
        return dict(self._data)

    def __repr__(self) -> str:  # pragma: no cover
        return f"State({self._data!r})"


def use_state(initial: Any) -> tuple[Callable[[], Any], Callable[[Any], None]]:
    """
    Hook-style helper for use inside functional render helpers:

        count, set_count = use_state(0)
    """
    box = {"value": initial}
    listeners: list[Callable[[], None]] = []

    def get() -> Any:
        return box["value"]

    def setter(new_value: Any) -> None:
        box["value"] = new_value
        for cb in listeners:
            cb()

    setter._listeners = listeners  # type: ignore[attr-defined]
    return get, setter
