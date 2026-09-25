# `nexoria.render`

> Turns an `Element` tree into HTML (SSR) and computes the minimal patch list between two trees (the differ).

| | |
|---|---|
| **Import** | `from nexoria.render import render_to_html, diff, Patch` · `from nexoria.render.diff import hot_path_active` · `from nexoria.render.html import render_document` |
| **Source** | `nexoria/render/html.py`, `nexoria/render/diff.py` |
| **Enabled by** | Always on |
| **Acceleration** | C++ VDOM → PyO3 Rust → pure Python, chosen automatically |

---

## 1. HTML serialization (`html.py`)

`render_to_html(root, indent=0, pretty=False, raw=False) -> str` recursively serialises an `Element`.

- Attribute values are HTML-escaped; boolean attributes (`checked`, `disabled`, `hidden`, `controls`, `autoplay`, `loop`, `muted`, `playsinline`, `required`, …) render bare when truthy and are omitted when falsy.
- Event handlers are never inlined. Each registered handler adds `data-nx-on-<event>="<handler_id>"`.
- Void tags render as `<br/>`.
- **Raw-text elements.** The children of `<script>` and `<style>` are emitted verbatim (not HTML-escaped), because browsers do not decode entities there. The only transformation is `</` → `<\/` so a string containing `</script>` cannot close the tag early — a no-op escape that is valid inside both JS and JSON strings.
- `pretty=True` indents output (useful in tests/debugging).

`render_document(body_html, hydration_script, title, extra_head, stylesheets)` wraps the body in the full document:

1. `<meta charset>` and viewport.
2. `<title>` (escaped).
3. A **blocking inline script** that sets `data-nx-theme` from `localStorage`/`prefers-color-scheme` before any CSS is applied.
4. Optional stylesheet links and `extra_head` (built by `App._build_head`).
5. `<div id="nx-root">…body…</div>`
6. `<script src="/_nexoria/runtime.js" defer>` and `<script id="nx-hydration-data" type="application/json">…</script>`.

## 2. The differ (`diff.py`)

`diff(old, new) -> list[Patch]` — either argument may be `None`. `Patch(kind, path, payload)` addresses a node by a **child-index path** relative to the root element.

| `kind` | Meaning | `payload` |
|---|---|---|
| `text` | Change a text node | new string |
| `replace` | Swap a node (different tag, or text↔element) | new node dict |
| `insert` | Insert a node at `path` | node dict |
| `remove` | Delete the node at `path` | `None` |
| `update_props` | Replace props **and** event ids on an element | `{"props": {...}, "events": {...}}` |

Algorithm (identical in all three backends):

1. `None`/`None` → nothing; `None`→node → `insert`; node→`None` → `remove`.
2. Text vs text → `text` patch if changed.
3. Different tag, or text vs element → `replace`.
4. Same tag → `update_props` if props **or handler ids** differ, then diff the children.
5. Children: if **both** lists are fully keyed, match by key; otherwise match by position.

### Backend selection

```python
from nexoria.render.diff import hot_path_active
hot_path_active()      # "cpp" | "rust" | "python"
```

Order: native C++ (`nexoria._nexoria_vdom_cpp`) > PyO3 Rust (`nexoria._nexoria_rs`) > pure Python. All three are covered by the same vectors in `tests/test_render_and_diff.py`. See [`rust_ext`](rust_ext.md) and [`native`](native.md).

### Consequences worth knowing

- **Handler ids are regenerated on every render** (`h1`, `h2`, …). Any element that has an `on_*` handler therefore produces an `update_props` patch on every re-render, even if nothing else changed. This is by design: it is what keeps the server's handler map and the DOM's `data-nx-on-*` attributes in sync.
- Patches address nodes by index, so text nodes matter: `el("p", "a", "b")` has **two** text children. Avoid adjacent literal strings if you can; use one f-string.

### Known limitations of keyed lists

The keyed path addresses each surviving child by its **new** index, emits removals by **old** index in ascending order, and emits **no move operations**. Simulating the client's sequential patch application against the current differ gives:

| Change to a fully keyed list | Result |
|---|---|
| append, prepend, insert in the middle | correct |
| remove one item (first / middle / last) | correct |
| edit an item's content, keys unchanged | correct |
| **reorder** existing items | no patches emitted — DOM keeps the old order |
| **remove two or more** items in one update | second removal targets a shifted index — wrong node removed |
| **remove an item and edit another** in one update | edit can land on the wrong node |

Unkeyed lists (position-based) handle append/remove-from-end/remove-from-start correctly. If your UI reorders or bulk-removes, either change one thing per event or force a wider re-render by giving the list wrapper a new tag/`key`.

## API reference

### Classes

#### `class Patch(kind: str, path: list[int], payload: Any = None) -> None`

A single DOM mutation instruction, addressed by child-index path.

- **`.to_dict() -> dict`**

### Functions

#### `render_to_html(root: Element, indent: int = 0, pretty: bool = False, raw: bool = False) -> str`

Recursively render an Element (or Component.render() output) to HTML.

`raw` is True while inside a <script>/<style> element: text children are emitted verbatim (only guarding against a literal "</" that would prematurely close the tag) instead of HTML-escaped.

#### `diff(old: Optional[Element], new: Optional[Element]) -> list[Patch]`

Public entry point. Returns an ordered list of Patch objects.
