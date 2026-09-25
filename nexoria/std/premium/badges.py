"""
nexoria.std.premium.badges
=============================
Small status/label chips and a circular avatar, both sized off the
same `sm`/`md`/`lg` scale the rest of `nexoria.std.premium` uses.
"""

from __future__ import annotations
from typing import Optional

from ...core.element import el, Element

_BADGE_COLORS = {
    "primary": ("rgba(99, 102, 241, 0.15)", "var(--nx-primary)"),
    "gold": ("rgba(212, 175, 55, 0.18)", "var(--nx-premium-gold)"),
    "success": ("rgba(34, 197, 94, 0.15)", "var(--nx-success)"),
    "danger": ("rgba(239, 68, 68, 0.15)", "var(--nx-danger)"),
    "neutral": ("var(--nx-surface-alt)", "var(--nx-text-muted)"),
}

_AVATAR_SIZES = {"sm": "32px", "md": "44px", "lg": "64px"}
_STATUS_COLORS = {"online": "var(--nx-success)", "busy": "var(--nx-danger)", "away": "var(--nx-warning)"}


def premium_badge(text: str, *, variant: str = "primary") -> Element:
    """`premium_badge("New", variant="gold")`. variant: primary | gold | success | danger | neutral."""
    bg, fg = _BADGE_COLORS.get(variant, _BADGE_COLORS["primary"])
    return el(
        "span", text,
        style={
            "display": "inline-flex",
            "align_items": "center",
            "padding": "4px 12px",
            "border_radius": "999px",
            "font_size": "0.75rem",
            "font_weight": "600",
            "letter_spacing": "0.02em",
            "background": bg,
            "color": fg,
        },
    )


def premium_avatar(
    *,
    src: Optional[str] = None,
    initials: Optional[str] = None,
    size: str = "md",
    status: Optional[str] = None,
) -> Element:
    """
    `premium_avatar(initials="DS", status="online")` or
    `premium_avatar(src="/me.jpg", size="lg")`.
    """
    dim = _AVATAR_SIZES.get(size, _AVATAR_SIZES["md"])
    wrapper_style = {"position": "relative", "display": "inline-block", "width": dim, "height": dim}

    if src:
        core = el(
            "img",
            src=src,
            alt=initials or "avatar",
            style={
                "width": "100%", "height": "100%", "border_radius": "50%",
                "object_fit": "cover", "border": "2px solid var(--nx-surface)",
            },
        )
    else:
        core = el(
            "div", (initials or "?")[:2].upper(),
            style={
                "width": "100%", "height": "100%", "border_radius": "50%",
                "display": "flex", "align_items": "center", "justify_content": "center",
                "background": "linear-gradient(135deg, var(--nx-primary), var(--nx-accent))",
                "color": "#ffffff", "font_weight": "700", "font_size": "0.9rem",
                "border": "2px solid var(--nx-surface)",
            },
        )

    kids = [core]
    if status:
        kids.append(el("span", style={
            "position": "absolute", "bottom": "-1px", "right": "-1px",
            "width": "10px", "height": "10px", "border_radius": "50%",
            "background": _STATUS_COLORS.get(status, "var(--nx-text-muted)"),
            "border": "2px solid var(--nx-surface)",
        }))
    return el("div", *kids, style=wrapper_style)
