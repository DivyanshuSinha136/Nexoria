"""
nexoria.style.components
===========================
A couple of ready-made, purely client-side UI bits that don't need a
server round-trip -- unlike `on_click=` handlers (which dispatch to
Python over the live WebSocket channel), these use plain HTML
attributes wired to small helpers `runtime.js` already exposes on
`window.__nexoria__`.
"""

from __future__ import annotations
from ..core.element import el, Element


def theme_toggle_button(icon: str = "\U0001F313", class_: str = "nx-theme-toggle") -> Element:
    """
    A dark/light mode toggle button. Purely client-side (no server
    round-trip) -- flips `document.documentElement[data-nx-theme]` and
    persists the choice to localStorage. Requires `App(light_theme=...)`
    to not be disabled (it's on, with `nexoria.style.LIGHT_THEME`, by
    default) so there's a CSS variable set to switch to.
    """
    return el(
        "button", icon,
        class_=class_,
        onclick="window.__nexoria__.toggleTheme()",
        aria_label="Toggle dark/light theme",
        type="button",
    )
