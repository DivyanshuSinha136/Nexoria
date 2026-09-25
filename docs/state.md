# `nexoria.state`

> A tiny reactive dictionary (`State`) and a hook-style `use_state`.

| | |
|---|---|
| **Import** | `from nexoria import State, use_state` |
| **Source** | `nexoria/state/store.py` |
| **Enabled by** | Always on |
| **Depends on** | nothing |

## `State`

`State` behaves like a dict whose writes notify subscribers.

```python
from nexoria import State

s = State({"count": 0, "items": []})
s["count"] = 1                    # same as s.set("count", 1)
s.update(count=2, loading=True)   # one notification for several keys
print(s["count"], "count" in s, list(s), s.to_dict())
```

- Writes (`update`, `set`, `__setitem__`) always notify — there is no equality check, so setting the same value still notifies.
- Mutating a value **in place** (`s["items"].append(x)`) does **not** notify; assign a new list or call `s.set("items", s["items"])`.
- Reads that miss raise `KeyError`; there is no `get()` with a default.
- `State` is **per component instance**, and a component instance is created **per page load**. State is therefore per browser tab and lives in server memory; it is not shared between users or tabs.

### How updates reach the browser

Subscribers are registered with the private `_on_change(callback)`. In the current `App`, re-rendering is driven by the WebSocket event loop, not by state notifications: a handler mutates state, the server then calls `render()` and diffs. See [FLOWCHART](FLOWCHART.md#3-event--patch-cycle).

## `use_state`

```python
get, set_ = use_state(0)
set_(get() + 1)
```

Returns a `(getter, setter)` pair backed by a closure. The setter calls any callbacks in `setter._listeners`. It is a small helper for functional render helpers and is independent of `App`'s re-render loop — for UI that must update after a click, use a `Component` with `State`.

## API reference

### Classes

#### `class State(initial: dict | None = None)`

- **`.set(key: str, value: Any) -> None`**
- **`.to_dict() -> dict`**
- **`.update(**kwargs: Any) -> None`**

### Functions

#### `use_state(initial: Any) -> tuple[Callable[[], Any], Callable[[Any], None]]`

Hook-style helper for use inside functional render helpers.

count, set_count = use_state(0)
