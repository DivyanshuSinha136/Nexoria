"""
nexoria.std.webtools.tooltip
================================
A hover tooltip and a copy-to-clipboard button. Both are fully
self-contained: no shared runtime, no unique ids -- `this` in the
inline handler always refers to the exact element being hovered or
clicked, so instances never collide.
"""

from __future__ import annotations
from typing import Any, Optional

from ...core.element import el, Element

_POSITIONS = {
    "top": {"bottom": "calc(100% + 8px)", "left": "50%", "transform": "translateX(-50%)"},
    "bottom": {"top": "calc(100% + 8px)", "left": "50%", "transform": "translateX(-50%)"},
    "left": {"right": "calc(100% + 8px)", "top": "50%", "transform": "translateY(-50%)"},
    "right": {"left": "calc(100% + 8px)", "top": "50%", "transform": "translateY(-50%)"},
}


def tooltip(content: Any, tooltip_text: str, *, position: str = "top") -> Element:
    """
    `tooltip(Icon("mdi:information"), "Synced 2 minutes ago")`.
    `content` is whatever should be hovered (text, an icon, a
    button...); `tooltip_text` is the bubble shown on hover.
    `position`: "top" | "bottom" | "left" | "right".
    """
    pos_style = _POSITIONS.get(position, _POSITIONS["top"])
    bubble = el(
        "span", tooltip_text,
        class_="nx-tooltip-bubble",
        style={
            "position": "absolute", "white_space": "nowrap",
            "background": "var(--nx-cartoon-ink, #1a1a1a)", "color": "#ffffff",
            "font_size": "0.78rem", "padding": "6px 10px", "border_radius": "6px",
            "opacity": "0", "visibility": "hidden", "pointer_events": "none",
            "transition": "opacity 0.12s ease", "z_index": "50",
            **pos_style,
        },
    )
    return el(
        "span", content, bubble,
        style={"position": "relative", "display": "inline-block"},
        onmouseover="this.querySelector('.nx-tooltip-bubble').style.opacity='1';this.querySelector('.nx-tooltip-bubble').style.visibility='visible'",
        onmouseout="this.querySelector('.nx-tooltip-bubble').style.opacity='0';this.querySelector('.nx-tooltip-bubble').style.visibility='hidden'",
    )


def copy_button(text_to_copy: str, *, label: str = "Copy", copied_label: str = "Copied!", class_: Optional[str] = None) -> Element:
    """
    `copy_button("npm install nexoria")`. Copies `text_to_copy` to
    the clipboard via `navigator.clipboard`, flashing `copied_label`
    for 1.5s. `text_to_copy` is baked into the click handler as a
    literal, so keep it to short strings (a command, a code, a
    link) -- for large or dynamic content, add your own
    `on_click` handler instead.
    """
    escaped = text_to_copy.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    js = (
        f"navigator.clipboard.writeText('{escaped}');"
        f"var el=this;var original=el.textContent;el.textContent='{copied_label}';"
        f"setTimeout(function(){{el.textContent=original;}}, 1500);"
    )
    return el(
        "button", label,
        type="button",
        onclick=js,
        class_=class_,
        style={
            "display": "inline-flex", "align_items": "center", "gap": "6px",
            "padding": "6px 14px", "font_size": "0.85rem", "font_weight": "600",
            "border": "1px solid var(--nx-border)", "border_radius": "var(--nx-radius-sm)",
            "background": "var(--nx-surface-alt)", "color": "var(--nx-text)", "cursor": "pointer",
        },
    )
