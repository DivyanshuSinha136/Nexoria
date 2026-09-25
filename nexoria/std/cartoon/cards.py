"""
nexoria.std.cartoon.cards
============================
A comic-panel-style card: thick ink outline, hard offset shadow, flat
color fill, and an optional slight tilt + hover-straighten for a
hand-drawn feel. Plus a plain multi-panel comic strip wrapper.
"""

from __future__ import annotations
from typing import Any, Optional

from ...core.element import el, Element


def cartoon_card(
    *children: Any,
    title: Optional[str] = None,
    sticker: Optional[Element] = None,
    color: str = "var(--nx-cartoon-paper)",
    tilt: bool = True,
) -> Element:
    """
    `cartoon_card("Panel text", title="Chapter 1", sticker=Icon("mdi:star"))`.
    `tilt=True` (default) gives it a slight rotation that straightens
    out on hover -- purely `onmouseover`/`onmouseout`, no JS bundle.
    """
    rotation = "-1.5deg"
    style: dict[str, Any] = {
        "position": "relative",
        "background": color,
        "border": "3px solid var(--nx-cartoon-ink)",
        "border_radius": "18px",
        "box_shadow": "6px 6px 0 var(--nx-cartoon-ink)",
        "padding": "24px",
        "transform": f"rotate({rotation})" if tilt else "none",
        "transition": "transform 0.2s ease",
    }

    kids = []
    if sticker is not None:
        kids.append(el("div", sticker, style={
            "position": "absolute", "top": "-16px", "right": "-16px",
            "font_size": "1.8rem", "filter": "drop-shadow(2px 2px 0 var(--nx-cartoon-ink))",
        }))
    if title:
        kids.append(el("h3", title, style={
            "margin": "0 0 12px 0", "font_size": "1.15rem", "font_weight": "800",
            "color": "var(--nx-cartoon-ink)",
        }))
    kids.extend(children)

    props: dict[str, Any] = {"style": style}
    if tilt:
        props["onmouseover"] = "this.style.transform='rotate(0deg) translateY(-3px)'"
        props["onmouseout"] = f"this.style.transform='rotate({rotation})'"

    return el("div", *kids, **props)


def comic_panel(*children: Any, caption: Optional[str] = None) -> Element:
    """A borderless strip of `cartoon_card`s in a row, with an optional caption underneath."""
    kids = [el("div", *children, style={
        "display": "flex", "gap": "18px", "flex_wrap": "wrap", "justify_content": "center",
    })]
    if caption:
        kids.append(el("p", caption, style={
            "text_align": "center", "margin_top": "16px", "font_weight": "700",
            "color": "var(--nx-cartoon-ink)",
        }))
    return el("div", *kids)
