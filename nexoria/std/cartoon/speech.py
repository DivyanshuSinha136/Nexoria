"""
nexoria.std.cartoon.speech
=============================
Comic-style speech and thought bubbles, built from a bordered box
plus a CSS-triangle tail (no image assets, no JS).

The tail is the classic "double triangle" CSS trick: a larger
outline-colored triangle sits behind a slightly smaller fill-colored
one, offset a few pixels toward the bubble, so the tail reads as
outlined the same way the bubble body is.
"""

from __future__ import annotations
from typing import Tuple

from ...core.element import el, Element

# (outline-triangle style overrides, fill-triangle style overrides) per direction
_TAILS = {
    "left": (
        {"left": "26px", "bottom": "-17px", "border_width": "18px 13px 0 13px"},
        {"left": "29px", "bottom": "-13px", "border_width": "15px 10px 0 10px"},
    ),
    "right": (
        {"right": "26px", "bottom": "-17px", "border_width": "18px 13px 0 13px"},
        {"right": "29px", "bottom": "-13px", "border_width": "15px 10px 0 10px"},
    ),
    "bottom": (
        {"left": "50%", "bottom": "-17px", "transform": "translateX(-50%)", "border_width": "18px 13px 0 13px"},
        {"left": "50%", "bottom": "-12px", "transform": "translateX(-50%)", "border_width": "15px 10px 0 10px"},
    ),
}


def _tail_elements(direction: str, fill_color: str) -> Tuple[Element, Element]:
    outline_pos, fill_pos = _TAILS.get(direction, _TAILS["left"])
    outline = el("span", style={
        "position": "absolute", "width": "0", "height": "0", "border_style": "solid",
        "border_color": "var(--nx-cartoon-ink) transparent transparent transparent",
        **outline_pos,
    })
    fill = el("span", style={
        "position": "absolute", "width": "0", "height": "0", "border_style": "solid",
        "border_color": f"{fill_color} transparent transparent transparent",
        **fill_pos,
    })
    return outline, fill


def speech_bubble(text: str, *, direction: str = "left", color: str = "var(--nx-cartoon-paper)") -> Element:
    """
    `speech_bubble("Let's build something!", direction="left")`.
    `direction`: which side the pointer tail sits on -- "left" | "right" | "bottom".
    """
    outline_tail, fill_tail = _tail_elements(direction, color)
    return el(
        "div",
        el("p", text, style={"margin": "0", "font_weight": "700", "color": "var(--nx-cartoon-ink)"}),
        outline_tail, fill_tail,
        style={
            "position": "relative", "display": "inline-block",
            "background": color, "border": "3px solid var(--nx-cartoon-ink)",
            "border_radius": "20px", "padding": "16px 22px", "max_width": "320px",
        },
    )


def thought_bubble(text: str, *, color: str = "var(--nx-cartoon-paper)") -> Element:
    """`thought_bubble("...maybe cartoons AND premium components?")` -- a cloud-tail dreamy variant."""
    dots = el(
        "div",
        *[
            el("span", style={
                "display": "block", "width": f"{10 - i * 3}px", "height": f"{10 - i * 3}px",
                "border_radius": "50%", "background": color,
                "border": "2px solid var(--nx-cartoon-ink)", "margin_top": "6px",
            })
            for i in range(3)
        ],
        style={"display": "flex", "flex_direction": "column", "align_items": "flex-start", "margin_top": "4px", "margin_left": "20px"},
    )

    return el(
        "div",
        el(
            "div",
            el("p", text, style={"margin": "0", "font_weight": "700", "color": "var(--nx-cartoon-ink)", "font_style": "italic"}),
            style={
                "background": color, "border": "3px solid var(--nx-cartoon-ink)",
                "border_radius": "26px", "padding": "18px 24px", "max_width": "320px",
            },
        ),
        dots,
    )
