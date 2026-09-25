"""
nexoria.std.premium.navigation
=================================
Site-level chrome: a sticky navbar with a brand, link row and CTA,
and a multi-column footer.
"""

from __future__ import annotations
from typing import Any, Optional, Sequence

from ...core.element import el, Element
from .buttons import premium_button


def premium_navbar(
    brand: Any,
    *,
    links: Sequence[tuple] = (),
    cta_text: Optional[str] = None,
    cta_href: str = "#",
    cta_shimmer: bool = False,
    cta_icon: Optional[Element] = None,
    cta_variant: str = "primary",
    cta_on_click: Optional[Callable] = None,
    sticky: bool = True,
) -> Element:
    """
    `premium_navbar("Acme", links=[("Product", "/product"), ("Pricing", "/pricing")], cta_text="Sign up")`.
    `links` is a sequence of `(label, href)` pairs. `brand` may be a
    string or any `Element`/`.to_element()`-able wrapper (e.g. a logo
    `nexoria.iconify.Icon` next to text -- pass a list as `brand` and
    it'll be spread as the brand block's children).
    """
    brand_kids = brand if isinstance(brand, (list, tuple)) else [brand]
    link_els = [
        el("a", label, href=href, style={
            "color": "var(--nx-text-muted)", "text_decoration": "none", "font_size": "0.92rem",
            "font_weight": "500",
        }, onmouseover="this.style.color='var(--nx-text)'", onmouseout="this.style.color='var(--nx-text-muted)'")
        for label, href in links
    ]

    right = list(link_els)
    if cta_text:
        right.append(premium_button(cta_text, size="sm", href=cta_href, shimmer=cta_shimmer, icon= cta_icon,
                                    variant= cta_variant, on_click= cta_on_click))

    style = {
        "display": "flex", "align_items": "center", "justify_content": "space-between",
        "padding": "16px 32px", "background": "var(--nx-surface)",
        "border_bottom": "1px solid var(--nx-border)",
    }
    if sticky:
        style.update({"position": "sticky", "top": "0", "z_index": "40"})

    return el(
        "nav",
        el("div", *brand_kids, style={"font_weight": "800", "font_size": "1.2rem", "color": "var(--nx-text)"}),
        el("div", *right, style={"display": "flex", "align_items": "center", "gap": "28px"}),
        style=style,
    )


def premium_footer(
    brand: Any,
    *,
    columns: Sequence[dict] = (),
    socials: Sequence[tuple] = (),
    tagline: Optional[str] = None,
) -> Element:
    """
    `premium_footer("Acme", columns=[{"title": "Product", "links": [("Pricing", "/pricing")]}], socials=[("Twitter", "https://x.com/...")])`.
    """
    col_els = []
    for col in columns:
        col_links = [
            el("a", label, href=href, style={
                "display": "block", "color": "var(--nx-text-muted)", "text_decoration": "none",
                "font_size": "0.88rem", "margin_bottom": "10px",
            })
            for label, href in col.get("links", [])
        ]
        col_els.append(el(
            "div",
            el("div", col.get("title", ""), style={"font_weight": "700", "margin_bottom": "14px", "color": "var(--nx-text)"}),
            *col_links,
        ))

    social_els = [
        el("a", label, href=href, style={"color": "var(--nx-text-muted)", "text_decoration": "none", "font_size": "0.85rem"})
        for label, href in socials
    ]

    return el(
        "footer",
        el(
            "div",
            el("div",
               el("div", brand, style={"font_weight": "800", "font_size": "1.1rem", "color": "var(--nx-text)", "margin_bottom": "8px"}),
               *([el("p", tagline, style={"color": "var(--nx-text-muted)", "font_size": "0.88rem", "max_width": "260px"})] if tagline else []),
            ),
            *col_els,
            style={
                "display": "grid", "grid_template_columns": "1.4fr repeat(auto-fit, minmax(140px, 1fr))",
                "gap": "32px", "padding": "48px 32px 24px 32px",
            },
        ),
        el(
            "div", *social_els,
            style={
                "display": "flex", "gap": "20px", "padding": "20px 32px",
                "border_top": "1px solid var(--nx-border)",
            },
        ),
        style={"background": "var(--nx-surface)"},
    )
