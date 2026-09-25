# `nexoria.std.observer`

> Dependency-free wheel and pointer-drag normalisation, in the spirit of GSAP's Observer plugin.

| | |
|---|---|
| **Import** | `from nexoria.std.observer import observer_runtime, observer_region` |
| **Needs** | `observer_runtime()` once per page |

```python
observer_runtime()
observer_region(
    el("div", "Swipe or scroll me"),
    on_up_js="console.log('up!')", on_down_js="console.log('down!')",
    tolerance=10, target="self",          # or target="window"
)
```

Callbacks: `on_up_js`, `on_down_js`, `on_left_js`, `on_right_js`, `on_change_js`, `on_hover_enter_js`, `on_hover_leave_js`, `on_click_js`, `on_press_js`, `on_release_js`.

**Every `on_*_js` is a literal JavaScript snippet**, not a Python callable: `up/down/left/right` are synthesised gestures the browser has no native event for, so they are client-side by necessity. Each snippet runs with `event`, `deltaX`, `deltaY` and `el` in scope. Mouse, touch and pen are unified through Pointer Events. `tolerance` (pixels) is the movement threshold; `prevent_default=True` by default. Use [`js()`](../js.md) to build snippets from Python values safely.

## API reference

### Functions

#### `observer_runtime() -> Element`

A `<script>` `Element` carrying the Observer engine. Render it once per page.

#### `observer_region(*children: Any, on_up_js: Optional[str] = None, on_down_js: Optional[str] = None, on_left_js: Optional[str] = None, on_right_js: Optional[str] = None, on_change_js: Optional[str] = None, on_hover_enter_js: Optional[str] = None, on_hover_leave_js: Optional[str] = None, on_click_js: Optional[str] = None, on_press_js: Optional[str] = None, on_release_js: Optional[str] = None, tolerance: float = 8, prevent_default: bool = True, target: str = 'self', class_: Optional[str] = None, style: Optional[dict] = None) -> Element`

`observer_region(el("div", "Swipe or scroll me"), on_up_js="console.log('up!')", on_down_js="console.log('down!')")`.

Every `on_*_js` parameter is a literal JavaScript snippet (like `onclick=` elsewhere in `nexoria.std`) run when that gesture fires -- **not** a Python callable (Nexoria's `on_click=` convention is reserved for real DOM event names dispatched back to the server; these are synthesized, higher-level gestures the browser has no native event for, so they can only run client-side). Each snippet runs with `event`, `deltaX`, `deltaY`, and `el` (this element) in scope.

`on_up_js`/`on_down_js`/`on_left_js`/`on_right_js` fire once per gesture "tick" (debounced ~200ms while it continues) once the combined wheel/drag movement exceeds `tolerance` px in that direction -- mirrors GSAP Observer's `onUp`/`onDown`/`onLeft`/ `onRight`. `on_change_js` fires on every raw movement, undebounced, for continuous tracking (a drag-to-rotate knob, a parallax layer). `on_press_js`/`on_release_js` fire on pointer down/up (mouse, touch, or pen -- unified via Pointer Events). `on_hover_enter_js`/`on_hover_leave_js`/`on_click_js` are plain mouse events, included here so one component covers the common cases GSAP's Observer does.

`target="window"` listens on the whole window instead of just this element (for page-wide scroll/swipe direction, with this `<div>` only holding the config) -- but every hover/click/press listener still watches this element itself, in either mode.

`prevent_default=True` (the default) calls `event.preventDefault()` on wheel events, matching GSAP Observer's default…

### Constants

| Name | Value |
|---|---|
| `OBSERVER_RUNTIME_JS` | `'(function () {\n  if (window.__nxObserver) return;\n  window.__nxObserver = true;\n\n  function fire(elm, name, ev, dx, dy) {\n    var js = elm.getAttribute("data-nx-observer-" + name);\n    if (!js) return;\n    try {\n      var fn = new Function("event", "deltaX", "deltaY", "el", js);\n      fn(ev \|\| null, dx \|\| 0, dy \|\| 0, elm);\n    } catch (e) {\n      console.error("nexoria observer handler error:", e);\n  …` |
