"""
nexoria.std.observer.region
==============================
A container tagged for `nexoria.std.observer.runtime`: give it plain
JS snippets for whichever directions/events you care about, and the
runtime wires up the underlying `wheel`/`pointer*` listeners for you.
"""

from __future__ import annotations
from typing import Any, Optional

from ...core.element import el, Element


def observer_region(
    *children: Any,
    on_up_js: Optional[str] = None,
    on_down_js: Optional[str] = None,
    on_left_js: Optional[str] = None,
    on_right_js: Optional[str] = None,
    on_change_js: Optional[str] = None,
    on_hover_enter_js: Optional[str] = None,
    on_hover_leave_js: Optional[str] = None,
    on_click_js: Optional[str] = None,
    on_press_js: Optional[str] = None,
    on_release_js: Optional[str] = None,
    tolerance: float = 8,
    prevent_default: bool = True,
    target: str = "self",
    class_: Optional[str] = None,
    style: Optional[dict] = None,
) -> Element:
    """
    `observer_region(el("div", "Swipe or scroll me"), on_up_js="console.log('up!')", on_down_js="console.log('down!')")`.

    Every `on_*_js` parameter is a literal JavaScript snippet (like
    `onclick=` elsewhere in `nexoria.std`) run when that gesture
    fires -- **not** a Python callable (Nexoria's `on_click=`
    convention is reserved for real DOM event names dispatched back
    to the server; these are synthesized, higher-level gestures the
    browser has no native event for, so they can only run client-side).
    Each snippet runs with `event`, `deltaX`, `deltaY`, and `el` (this
    element) in scope.

    `on_up_js`/`on_down_js`/`on_left_js`/`on_right_js` fire once per
    gesture "tick" (debounced ~200ms while it continues) once the
    combined wheel/drag movement exceeds `tolerance` px in that
    direction -- mirrors GSAP Observer's `onUp`/`onDown`/`onLeft`/
    `onRight`. `on_change_js` fires on every raw movement, undebounced,
    for continuous tracking (a drag-to-rotate knob, a parallax
    layer). `on_press_js`/`on_release_js` fire on pointer down/up
    (mouse, touch, or pen -- unified via Pointer Events).
    `on_hover_enter_js`/`on_hover_leave_js`/`on_click_js` are plain
    mouse events, included here so one component covers the common
    cases GSAP's Observer does.

    `target="window"` listens on the whole window instead of just
    this element (for page-wide scroll/swipe direction, with this
    `<div>` only holding the config) -- but every hover/click/press
    listener still watches this element itself, in either mode.

    `prevent_default=True` (the default) calls
    `event.preventDefault()` on wheel events, matching GSAP
    Observer's default -- set `False` if you still want the page to
    scroll normally alongside your own handlers.

    Needs `observer_runtime()` rendered once per page.
    """
    props: dict[str, Any] = {
        "class_": class_,
        "data_nx_observer": "true",
        "data_nx_observer_tolerance": str(tolerance),
        "data_nx_observer_prevent_default": "true" if prevent_default else "false",
        "data_nx_observer_target": target,
    }
    if style:
        props["style"] = style

    for name, js in (
        ("up", on_up_js), ("down", on_down_js), ("left", on_left_js), ("right", on_right_js),
        ("change", on_change_js),
        ("hoverenter", on_hover_enter_js), ("hoverleave", on_hover_leave_js),
        ("click", on_click_js), ("press", on_press_js), ("release", on_release_js),
    ):
        if js:
            props[f"data_nx_observer_{name}"] = js

    return el("div", *children, **props)
