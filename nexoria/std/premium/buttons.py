"""
nexoria.std.premium.buttons
==============================
A polished call-to-action button with three variants and an optional
shimmer sweep. Renders as `<a>` when `href` is given, `<button>`
otherwise, so it works equally well as a nav CTA or a form action.
"""

from __future__ import annotations
from typing import Any, Callable, Optional

from ...core.element import el, Element

_SIZES = {
    "sm": ("8px 16px", "0.85rem"),
    "md": ("12px 24px", "0.95rem"),
    "lg": ("16px 32px", "1.05rem"),
}


def _variant_style(variant: str) -> dict:
    if variant == "primary":
        return {
            "background": "linear-gradient(135deg, var(--nx-primary), var(--nx-accent))",
            "color": "#ffffff",
            "border": "1px solid transparent",
        }
    if variant == "outline":
        return {
            "background": "transparent",
            "color": "var(--nx-primary)",
            "border": "1.5px solid var(--nx-primary)",
        }
    if variant == "gold":
        return {
            "background": "linear-gradient(135deg, var(--nx-premium-gold-soft), var(--nx-premium-gold))",
            "color": "#1a1406",
            "border": "1px solid transparent",
        }
    # "ghost"
    return {
        "background": "var(--nx-surface-alt)",
        "color": "var(--nx-text)",
        "border": "1px solid var(--nx-border)",
    }


def premium_button(
    *children: Any,
    variant: str = "primary",
    size: str = "md",
    href: Optional[str] = None,
    on_click: Optional[Callable] = None,
    icon: Optional[Element] = None,
    full_width: bool = False,
    shimmer: bool = False,
    disabled: bool = False,
    class_: Optional[str] = None,
) -> Element:
    """
    `premium_button("Get Started", variant="primary", href="/signup")`

    `variant`: "primary" | "outline" | "ghost" | "gold"
    `shimmer`: adds a moving highlight sweep; requires
      `nexoria.std.premium.theme.premium_keyframes()` to be rendered
      once on the page.
    """
    padding, font_size = _SIZES.get(size, _SIZES["md"])
    style = {
        "display": "inline-flex",
        "align_items": "center",
        "gap": "8px",
        "justify_content": "center",
        "padding": padding,
        "font_size": font_size,
        "font_weight": "600",
        "border_radius": "var(--nx-radius-sm)",
        "cursor": "pointer" if not disabled else "not-allowed",
        "opacity": "0.55" if disabled else "1",
        "text_decoration": "none",
        "transition": "transform 0.15s ease, box-shadow 0.15s ease",
        "width": "100%" if full_width else "auto",
        "box_shadow": "0 6px 18px rgba(0,0,0,0.18)",
        **_variant_style(variant),
    }
    if shimmer and not disabled:
        style.update({
            "background_size": "200% 100%",
            "animation": "nx-premium-shimmer 2.4s linear infinite",
        })

    kids = []
    if icon is not None:
        kids.append(icon)
    kids.extend(children)

    props: dict[str, Any] = {
        "style": style,
        "class": class_,
        "onmouseover": (
            "" if disabled else
            "this.style.transform='translateY(-2px)';"
            "this.style.boxShadow='0 10px 24px rgba(0,0,0,0.28)'"
        ),
        "onmouseout": (
            "" if disabled else
            "this.style.transform='translateY(0)';"
            "this.style.boxShadow='0 6px 18px rgba(0,0,0,0.18)'"
        ),
    }
    if not disabled and on_click is not None:
        props["on_click"] = on_click
    if disabled:
        props["disabled"] = True
        props["aria_disabled"] = "true"

    if href and not disabled:
        props["href"] = href
        return el("a", *kids, **props)
    return el("button", *kids, type="button", **props)
