"""
nexoria.std.cartoon.badges
=============================
A sticker-style badge (circle/star/burst) and a big, friendly emoji
avatar -- the cartoon family's answer to `nexoria.std.premium.badges`.
"""

from __future__ import annotations
from typing import Optional

from ...core.element import el, Element

_AVATAR_SIZES = {"sm": "40px", "md": "56px", "lg": "80px"}


def sticker_badge(text: str, *, shape: str = "circle", color: str = "var(--nx-cartoon-sunshine)", pop: bool = False) -> Element:
    """
    `sticker_badge("NEW!", shape="star", color="var(--nx-cartoon-coral)")`.
    `shape`: "circle" | "star" | "burst". `pop=True` gives it a
    one-shot pop-in animation on mount (needs `cartoon_keyframes()`).
    """
    style: dict = {
        "display": "inline-flex", "align_items": "center", "justify_content": "center",
        "background": color, "border": "3px solid var(--nx-cartoon-ink)",
        "color": "var(--nx-cartoon-ink)", "font_weight": "800", "font_size": "0.8rem",
        "padding": "10px 14px", "text_transform": "uppercase", "letter_spacing": "0.03em",
        "transform": "rotate(-6deg)",
    }
    if shape == "circle":
        style.update({"border_radius": "50%", "padding": "16px", "transform": "rotate(0deg)"})
    elif shape == "burst":
        # a jagged "explosion" look via a sharp-cornered rotated square,
        # simple and dependency-free (no clip-path polygon needed)
        style.update({"border_radius": "6px", "transform": "rotate(-8deg)"})
    else:  # "star" -- five-pointed via clip-path, flat color fill
        style.update({
            "clip_path": "polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)",
            "border": "none", "width": "72px", "height": "72px", "padding": "0",
        })
    if pop:
        style["animation"] = "nx-cartoon-pop 0.4s ease both"

    return el("span", text, style=style)


def cartoon_avatar(*, emoji: str = "\U0001F9B8", size: str = "md", bg: str = "var(--nx-cartoon-sky)", bounce: bool = False) -> Element:
    """`cartoon_avatar(emoji="\U0001F680", bg="var(--nx-cartoon-mint)")` -- a flat-color circle with a big emoji."""
    dim = _AVATAR_SIZES.get(size, _AVATAR_SIZES["md"])
    style = {
        "display": "inline-flex", "align_items": "center", "justify_content": "center",
        "width": dim, "height": dim, "border_radius": "50%",
        "background": bg, "border": "3px solid var(--nx-cartoon-ink)",
        "font_size": f"calc({dim} * 0.55)", "line_height": "1",
    }
    if bounce:
        style["animation"] = "nx-cartoon-bounce 1.6s ease-in-out infinite"
    return el("div", emoji, style=style)
