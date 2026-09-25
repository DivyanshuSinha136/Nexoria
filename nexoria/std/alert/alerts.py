"""
nexoria.std.alert.alerts
===========================
Feedback surfaces: a dismissible full-width banner, an
auto-dismissing corner toast, and a small inline alert for form/field
messages. All dismiss/timeout behavior is a couple of literal
`onclick=`/inline `<script>` lines -- no server round-trip, no JS
bundle -- same convention as the rest of `nexoria.std`.
"""

from __future__ import annotations
from typing import Any, Optional
import uuid

from ...core.element import el, Element

_VARIANTS = {
    "info": ("rgba(99, 102, 241, 0.12)", "var(--nx-primary)", "\u2139"),
    "success": ("rgba(34, 197, 94, 0.12)", "var(--nx-success)", "\u2713"),
    "warning": ("rgba(245, 158, 11, 0.12)", "var(--nx-warning)", "\u26A0"),
    "danger": ("rgba(239, 68, 68, 0.12)", "var(--nx-danger)", "\u2715"),
}

_TOAST_POSITIONS = {
    "top-right": {"top": "20px", "right": "20px"},
    "top-left": {"top": "20px", "left": "20px"},
    "bottom-right": {"bottom": "20px", "right": "20px"},
    "bottom-left": {"bottom": "20px", "left": "20px"},
}


def alert_banner(
    message: str,
    *,
    variant: str = "info",
    title: Optional[str] = None,
    dismissible: bool = True,
    icon: Optional[Element] = None,
) -> Element:
    """
    `alert_banner("Your trial ends in 3 days.", variant="warning", title="Heads up")`.
    `variant`: "info" | "success" | "warning" | "danger".
    """
    bg, fg, default_icon = _VARIANTS.get(variant, _VARIANTS["info"])
    body = []
    if title:
        body.append(el("div", title, style={"font_weight": "700", "margin_bottom": "2px"}))
    body.append(el("div", message, style={"color": "var(--nx-text)", "font_size": "0.92rem"}))

    kids = [
        el("span", icon if icon is not None else default_icon, style={"font_size": "1.1rem", "color": fg, "flex_shrink": "0"}),
        el("div", *body, style={"flex": "1"}),
    ]
    if dismissible:
        kids.append(el(
            "button", "\u2715",
            type="button",
            aria_label="Dismiss",
            onclick="this.closest('[data-nx-alert]').style.display='none'",
            style={
                "background": "none", "border": "none", "cursor": "pointer",
                "color": "var(--nx-text-muted)", "font_size": "0.9rem", "padding": "0 0 0 8px",
            },
        ))

    return el(
        "div", *kids,
        data_nx_alert="true",
        style={
            "display": "flex", "align_items": "flex-start", "gap": "12px",
            "background": bg, "border_radius": "var(--nx-radius-sm)",
            "padding": "14px 16px", "border": f"1px solid {fg}",
        },
    )


def inline_alert(message: str, *, variant: str = "info") -> Element:
    """A compact, non-dismissible alert line for forms/fields: `inline_alert("Passwords don't match", variant="danger")`."""
    _, fg, default_icon = _VARIANTS.get(variant, _VARIANTS["info"])
    return el(
        "div",
        el("span", default_icon, style={"font_size": "0.85rem"}),
        el("span", message, style={"font_size": "0.85rem"}),
        style={"display": "flex", "align_items": "center", "gap": "6px", "color": fg},
    )


def toast(
    message: str,
    *,
    variant: str = "info",
    title: Optional[str] = None,
    duration: int = 4000,
    position: str = "bottom-right",
) -> Element:
    """
    `toast("Saved!", variant="success")`. Slides in, then dismisses
    itself after `duration` ms (or immediately on click). Pass
    `duration=0` to require a manual dismiss.

    Renders as a fixed-position element -- mount it directly in your
    page tree (e.g. conditionally, from a `Component`'s `render()`)
    rather than pre-rendering a stack of them; each carries its own
    unique id so several can coexist.
    """
    bg, fg, default_icon = _VARIANTS.get(variant, _VARIANTS["info"])
    pos = _TOAST_POSITIONS.get(position, _TOAST_POSITIONS["bottom-right"])
    toast_id = f"nx-toast-{uuid.uuid4().hex[:8]}"

    body = []
    if title:
        body.append(el("div", title, style={"font_weight": "700", "margin_bottom": "2px"}))
    body.append(el("div", message, style={"font_size": "0.9rem"}))

    node = el(
        "div",
        el("span", default_icon, style={"font_size": "1.05rem", "color": fg}),
        el("div", *body, style={"flex": "1"}),
        id_=toast_id,
        onclick="this.remove()",
        style={
            "position": "fixed", **pos, "z_index": "1000",
            "display": "flex", "align_items": "flex-start", "gap": "10px",
            "background": "var(--nx-surface)", "color": "var(--nx-text)",
            "border": f"1px solid {fg}", "border_radius": "var(--nx-radius-sm)",
            "padding": "14px 18px", "box_shadow": "var(--nx-shadow)",
            "max_width": "320px", "cursor": "pointer",
            "animation": "nx-toast-in 0.25s ease both",
        },
    )

    kids = [node]
    if duration and duration > 0:
        kids.append(el("script", (
            f"setTimeout(function(){{var t=document.getElementById('{toast_id}');"
            f"if(t)t.remove();}}, {int(duration)});"
        )))
    kids.append(el("style", (
        "@keyframes nx-toast-in {"
        "from { opacity: 0; transform: translateY(12px); }"
        "to { opacity: 1; transform: translateY(0); } }"
    )))
    return el("div", *kids)
