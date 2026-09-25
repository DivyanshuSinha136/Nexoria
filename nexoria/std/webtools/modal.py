"""
nexoria.std.webtools.modal
==============================
A trigger button + overlay dialog pair. Open/close is plain
`style.display` toggling via literal `onclick=` handlers -- no
Python state, no server round-trip -- so it works the moment it's
rendered, with no `Component` wiring required. Each modal gets its
own id (auto-generated unless you pass one), so several can coexist
on one page.
"""

from __future__ import annotations
from typing import Any, Optional
import uuid

from ...core.element import el, Element


def modal_dialog(
    trigger_label: str,
    *children: Any,
    title: Optional[str] = None,
    close_label: str = "Done",
    id_: Optional[str] = None,
    trigger_variant: str = "button",
) -> Element:
    """
    `modal_dialog("View details", el("p", "..."), title="Order #1029")`.

    `trigger_variant="button"` renders a plain styled `<button>` for
    `trigger_label`; pass `"link"` to render it as an inline text
    link instead (handy inside a sentence or table row).
    """
    modal_id = id_ or f"nx-modal-{uuid.uuid4().hex[:8]}"
    open_js = f"document.getElementById('{modal_id}').style.display='flex'"
    close_js = f"document.getElementById('{modal_id}').style.display='none'"

    if trigger_variant == "link":
        trigger = el("a", trigger_label, href="#", onclick=f"event.preventDefault();{open_js}",
                     style={"color": "var(--nx-primary)", "cursor": "pointer", "text_decoration": "underline"})
    else:
        trigger = el("button", trigger_label, type="button", onclick=open_js, style={
            "padding": "10px 20px", "border_radius": "var(--nx-radius-sm)", "border": "1px solid var(--nx-border)",
            "background": "var(--nx-primary)", "color": "#ffffff", "font_weight": "600", "cursor": "pointer",
        })

    header = []
    if title:
        header.append(el("h3", title, style={"margin": "0", "font_size": "1.1rem"}))
    header.append(el(
        "button", "\u2715", type="button", aria_label="Close", onclick=close_js,
        style={"background": "none", "border": "none", "cursor": "pointer", "font_size": "1rem", "color": "var(--nx-text-muted)"},
    ))

    overlay = el(
        "div",
        el(
            "div",
            el("div", *header, style={"display": "flex", "align_items": "center", "justify_content": "space-between", "margin_bottom": "16px"}),
            el("div", *children, style={"margin_bottom": "20px"}),
            el("button", close_label, type="button", onclick=close_js, style={
                "padding": "10px 20px", "border_radius": "var(--nx-radius-sm)", "border": "1px solid var(--nx-border)",
                "background": "var(--nx-surface-alt)", "cursor": "pointer",
            }),
            style={
                "background": "var(--nx-surface)", "border_radius": "var(--nx-radius)",
                "padding": "28px", "max_width": "480px", "width": "90%",
                "box_shadow": "var(--nx-shadow)",
            },
            onclick="event.stopPropagation()",
        ),
        id_=modal_id,
        onclick=close_js,
        style={
            "display": "none", "position": "fixed", "inset": "0", "z_index": "1200",
            "background": "rgba(0,0,0,0.5)", "align_items": "center", "justify_content": "center",
        },
    )

    return el("div", trigger, overlay)
