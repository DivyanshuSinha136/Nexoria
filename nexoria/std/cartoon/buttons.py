"""
nexoria.std.cartoon.buttons
==============================
A chunky, comic-styled button: thick dark outline, flat fill color,
and a hard offset shadow that "presses in" on click.
"""

from __future__ import annotations
from typing import Any, Callable, Optional

from ...core.element import el, Element

_SIZES = {
    "sm": ("8px 16px", "0.85rem", "3px"),
    "md": ("12px 22px", "1rem", "4px"),
    "lg": ("16px 30px", "1.15rem", "5px"),
}


def cartoon_button(
    *children: Any,
    color: str = "var(--nx-cartoon-coral)",
    href: Optional[str] = None,
    on_click: Optional[Callable] = None,
    icon: Optional[Element] = None,
    size: str = "md",
    wiggle: bool = False,
    disabled: bool = False,
) -> Element:
    """
    `cartoon_button("Let's go!", color="var(--nx-cartoon-mint)", icon=Icon("mdi:rocket"))`.

    `wiggle=True` gives it a playful idle wiggle (needs
    `cartoon_keyframes()` rendered once on the page). Click gives a
    satisfying "press" (shadow collapses, button shifts down) via
    plain `onmousedown`/`onmouseup` -- no JS bundle needed.
    """
    padding, font_size, shadow_offset = _SIZES.get(size, _SIZES["md"])
    style: dict[str, Any] = {
        "display": "inline-flex", "align_items": "center", "gap": "8px",
        "justify_content": "center", "padding": padding, "font_size": font_size,
        "font_weight": "800", "color": "var(--nx-cartoon-ink)",
        "background": color, "border": "3px solid var(--nx-cartoon-ink)",
        "border_radius": "16px",
        "box_shadow": f"{shadow_offset} {shadow_offset} 0 var(--nx-cartoon-ink)",
        "cursor": "pointer" if not disabled else "not-allowed",
        "opacity": "0.5" if disabled else "1",
        "text_decoration": "none",
        "transition": "transform 0.08s ease, box-shadow 0.08s ease",
    }
    if wiggle and not disabled:
        style["animation"] = "nx-cartoon-wiggle 2.2s ease-in-out infinite"

    kids = []
    if icon is not None:
        kids.append(icon)
    kids.extend(children)

    props: dict[str, Any] = {"style": style}
    if not disabled:
        props["onmousedown"] = "this.style.transform='translate(3px,3px)';this.style.boxShadow='0 0 0 var(--nx-cartoon-ink)'"
        props["onmouseup"] = f"this.style.transform='translate(0,0)';this.style.boxShadow='{shadow_offset} {shadow_offset} 0 var(--nx-cartoon-ink)'"
        props["onmouseleave"] = f"this.style.transform='translate(0,0)';this.style.boxShadow='{shadow_offset} {shadow_offset} 0 var(--nx-cartoon-ink)'"
        if on_click is not None:
            props["on_click"] = on_click
    else:
        props["disabled"] = True
        props["aria_disabled"] = "true"

    if href and not disabled:
        props["href"] = href
        return el("a", *kids, **props)
    return el("button", *kids, type="button", **props)
