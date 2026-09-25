"""
nexoria.std.lib.buttons
==========================
CTA buttons for the "lib" family: a solid off-white pill (e.g.
"Start building") and a bordered ghost/outline button (e.g. "Explore
source"), matching the Nexoria landing page's hero CTAs. Renders as
`<a>` when `href` is given, `<button>` otherwise.
"""

from __future__ import annotations
from typing import Any, Callable, Optional

from ...core.element import el, Element

_SIZES = {
    "sm": ("8px 16px", "0.82rem"),
    "md": ("12px 22px", "0.9rem"),
    "lg": ("14px 28px", "0.95rem"),
}


def _variant_style(variant: str) -> dict:
    if variant == "solid":
        return {
            "background": "var(--nx-text)",
            "color": "var(--nx-bg)",
            "border": "1px solid transparent",
        }
    if variant == "cyan":
        return {
            "background": "linear-gradient(135deg, var(--nx-lib-cyan), var(--nx-lib-cyan-soft))",
            "color": "#03211f",
            "border": "1px solid transparent",
        }
    if variant == "ghost":
        return {
            "background": "transparent",
            "color": "var(--nx-text-muted)",
            "border": "1px solid transparent",
        }
    # "outline"
    return {
        "background": "transparent",
        "color": "var(--nx-text)",
        "border": "1px solid var(--nx-border)",
    }


def lib_button(
    *children: Any,
    variant: str = "solid",
    size: str = "md",
    href: Optional[str] = None,
    on_click: Optional[Callable] = None,
    icon: Optional[Element] = None,
    trailing_icon: Optional[Element] = None,
    full_width: bool = False,
    disabled: bool = False,
    class_: Optional[str] = None,
) -> Element:
    """
    `lib_button("Start building", trailing_icon=el("span", "\u2192"))`
    `lib_button("Explore source", variant="outline")`

    `variant`: "solid" | "outline" | "ghost" | "cyan".
    """
    padding, font_size = _SIZES.get(size, _SIZES["md"])
    style = {
        "display": "inline-flex",
        "align_items": "center",
        "gap": "9px",
        "justify_content": "center",
        "padding": padding,
        "font_size": font_size,
        "font_weight": "600",
        "border_radius": "999px",
        "cursor": "pointer" if not disabled else "not-allowed",
        "opacity": "0.5" if disabled else "1",
        "text_decoration": "none",
        "transition": "transform 0.15s ease, opacity 0.15s ease, border-color 0.15s ease",
        "width": "100%" if full_width else "auto",
        **_variant_style(variant),
    }

    kids = []
    if icon is not None:
        kids.append(icon)
    kids.extend(children)
    if trailing_icon is not None:
        kids.append(trailing_icon)

    props: dict[str, Any] = {
        "style": style,
        "class": class_,
        "onmouseover": "" if disabled else "this.style.transform='translateY(-1px)';this.style.opacity='0.88'",
        "onmouseout": "" if disabled else "this.style.transform='translateY(0)';this.style.opacity='1'",
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
