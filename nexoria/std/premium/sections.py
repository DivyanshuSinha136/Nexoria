"""
nexoria.std.premium.sections
===============================
Larger, page-level building blocks: a hero banner, a feature grid,
and a testimonial. Assemble a landing page from a handful of these
plus `nexoria.std.premium.navigation`.
"""

from __future__ import annotations
from typing import Any, Mapping, Optional, Sequence

from ...core.element import el, Element
from .badges import premium_avatar
from .buttons import premium_button


def hero_section(
    title: str,
    *,
    subtitle: Optional[str] = None,
    eyebrow: Optional[str] = None,
    cta_text: Optional[str] = None,
    cta_href: str = "#",
    cta_shimmer: bool = False,
    cta_icon: Optional[Element] = None,
    cta_variant: str = "primary",
    cta_on_click: Optional[Callable] = None,
    secondary_cta_text: Optional[str] = None,
    secondary_cta_href: str = "#",
    secondary_cta_shimmer: bool = False,
    secondary_cta_icon: Optional[Element] = None,
    secondary_cta_variant: str = "outline",
    secondary_cta_on_click: Optional[Callable] = None,
    animate: bool = False,
) -> Element:
    """
    Full-width hero with an optional eyebrow label, subtitle, and up
    to two CTAs. `animate=True` fades the content up on load (needs
    `premium_keyframes()` rendered once on the page).
    """
    content_style: dict[str, Any] = {
        "max_width": "720px", "margin": "0 auto", "text_align": "center",
        "padding": "96px 24px",
    }
    if animate:
        content_style["animation"] = "nx-premium-fade-up 0.6s ease both"

    kids = []
    if eyebrow:
        kids.append(el("div", eyebrow, style={
            "color": "var(--nx-accent)", "font_weight": "700", "font_size": "0.85rem",
            "letter_spacing": "0.08em", "text_transform": "uppercase", "margin_bottom": "12px",
        }))
    kids.append(el("h1", title, style={
        "font_size": "clamp(2.2rem, 5vw, 3.4rem)", "font_weight": "800",
        "line_height": "1.15", "margin": "0 0 16px 0", "color": "var(--nx-text)",
    }))
    if subtitle:
        kids.append(el("p", subtitle, style={
            "font_size": "1.15rem", "color": "var(--nx-text-muted)", "margin": "0 0 32px 0",
            "line_height": "1.6",
        }))

    ctas = []
    if cta_text:
        ctas.append(premium_button(cta_text, variant=cta_variant, size="lg", href=cta_href,
                                   shimmer= cta_shimmer, icon= cta_icon, on_click= cta_on_click))
    if secondary_cta_text:
        ctas.append(premium_button(secondary_cta_text, variant=secondary_cta_variant, size="lg", href=secondary_cta_href,
                                   shimmer= secondary_cta_shimmer, icon= secondary_cta_icon, on_click= cta_on_click))
    if ctas:
        kids.append(el("div", *ctas, style={"display": "flex", "gap": "16px", "justify_content": "center", "flex_wrap": "wrap"}))

    return el("section", el("div", *kids, style=content_style), style={"background": "var(--nx-bg)"})


def feature_grid(features: Sequence[Mapping[str, Any]]) -> Element:
    """
    `feature_grid([{"icon": Icon("mdi:rocket"), "title": "Fast", "desc": "..."}])`.
    Each item needs `title` and `desc`; `icon` is optional.
    """
    tiles = []
    for f in features:
        head = []
        if f.get("icon") is not None:
            head.append(el("div", f["icon"], style={"font_size": "1.8rem", "margin_bottom": "14px", "color": "var(--nx-primary)"}))
        tiles.append(el(
            "div", *head,
            el("h3", f.get("title", ""), style={"margin": "0 0 8px 0", "font_size": "1.05rem", "color": "var(--nx-text)"}),
            el("p", f.get("desc", ""), style={"margin": "0", "color": "var(--nx-text-muted)", "line_height": "1.6", "font_size": "0.92rem"}),
            style={
                "background": "var(--nx-surface)", "border": "1px solid var(--nx-border)",
                "border_radius": "var(--nx-radius)", "padding": "26px",
            },
        ))
    return el("div", *tiles, style={
        "display": "grid", "grid_template_columns": "repeat(auto-fit, minmax(240px, 1fr))",
        "gap": "20px",
    })


def testimonial(
    quote: str,
    author: str,
    *,
    role: Optional[str] = None,
    avatar_src: Optional[str] = None,
    rating: Optional[int] = 5,
) -> Element:
    """`testimonial("This shipped our landing page in a day.", "Priya N.", role="Founder, Acme")`."""
    stars = el("div", "\u2605" * max(0, min(5, rating or 0)), style={"color": "var(--nx-premium-gold)", "margin_bottom": "12px"}) if rating else None
    return el(
        "figure",
        *([stars] if stars else []),
        el("blockquote", f"\u201c{quote}\u201d", style={
            "margin": "0 0 20px 0", "font_size": "1.05rem", "line_height": "1.6",
            "color": "var(--nx-text)", "font_style": "italic",
        }),
        el(
            "figcaption",
            premium_avatar(src=avatar_src, initials=author, size="sm"),
            el("div",
               el("div", author, style={"font_weight": "700", "font_size": "0.9rem"}),
               *([el("div", role, style={"color": "var(--nx-text-muted)", "font_size": "0.82rem"})] if role else []),
            ),
            style={"display": "flex", "align_items": "center", "gap": "12px"},
        ),
        style={
            "background": "var(--nx-surface)", "border": "1px solid var(--nx-border)",
            "border_radius": "var(--nx-radius)", "padding": "26px", "margin": "0",
        },
    )
