# `nexoria.std.webtools`

> General UI utilities: tooltip, copy-to-clipboard, modal, accordion, tabs. Fully client-side, no shared runtime.

| | |
|---|---|
| **Import** | `from nexoria.std.webtools import tooltip, copy_button, modal_dialog, accordion, tabs` |

```python
tooltip(Icon("info-circle"), "Synced 2 minutes ago", position="top")          # top|bottom|left|right
copy_button("pip install nexoria", label="Copy", copied_label="Copied!")
modal_dialog("View details", el("p", "…"), title="Order #1029")
accordion([{"title": "What's included?", "content": "Everything in Pro."}], allow_multiple=False)
tabs([{"label": "Overview", "content": el("p", "…")}, {"label": "Specs", "content": el("p", "…")}], active=0)
```

- Interactions are literal `onclick`/`onmouseover` attributes acting on the component's own subtree, so any number can coexist on a page.
- `copy_button` bakes `text_to_copy` into the handler as a literal — keep it to short strings; it uses `navigator.clipboard` (HTTPS/localhost) and flashes `copied_label` for 1.5 s.
- `accordion(allow_multiple=False)` closes other panels when one opens, via a small per-panel handler.
- `modal_dialog(trigger_label, *children, title, close_label="Done", id_, trigger_variant="button")` renders a trigger and the dialog.

## API reference

### Functions

#### `tooltip(content: Any, tooltip_text: str, *, position: str = 'top') -> Element`

`tooltip(Icon("mdi:information"), "Synced 2 minutes ago")`. `content` is whatever should be hovered (text, an icon, a button...); `tooltip_text` is the bubble shown on hover. `position`: "top" | "bottom" | "left" | "right".

#### `copy_button(text_to_copy: str, *, label: str = 'Copy', copied_label: str = 'Copied!', class_: Optional[str] = None) -> Element`

`copy_button("npm install nexoria")`. Copies `text_to_copy` to the clipboard via `navigator.clipboard`, flashing `copied_label` for 1.5s. `text_to_copy` is baked into the click handler as a literal, so keep it to short strings (a command, a code, a link) -- for large or dynamic content, add your own `on_click` handler instead.

#### `modal_dialog(trigger_label: str, *children: Any, title: Optional[str] = None, close_label: str = 'Done', id_: Optional[str] = None, trigger_variant: str = 'button') -> Element`

`modal_dialog("View details", el("p", "..."), title="Order #1029")`.

`trigger_variant="button"` renders a plain styled `<button>` for `trigger_label`; pass `"link"` to render it as an inline text link instead (handy inside a sentence or table row).

#### `accordion(items: Sequence[Mapping[str, Any]], *, allow_multiple: bool = True) -> Element`

`accordion([{"title": "What's included?", "content": "Everything in Pro."}])`. Each item needs `title` and `content` (a string or an `Element`). `allow_multiple=False` closes any other open panel when one is opened (accordion-style exclusivity) via a small per-click sweep over sibling panels.

#### `tabs(items: Sequence[Mapping[str, Any]], *, active: int = 0) -> Element`

`tabs([{"label": "Overview", "content": el("p", "...")}, {"label": "Specs", "content": el("p", "...")}])`. Each item needs `label` and `content`. `active` is the index of the tab shown initially.
