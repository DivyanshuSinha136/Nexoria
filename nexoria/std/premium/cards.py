"""
nexoria.std.premium.cards
============================
Surface containers for the premium family: a general-purpose card, a
frosted-glass variant, a stat/KPI tile, and a pricing-plan card.
"""

from __future__ import annotations
from typing import Any, Optional, Sequence

from ...core.element import el, Element
from .badges import premium_badge
from .buttons import premium_button


def premium_card(
    *children: Any,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    elevated: bool = True,
    glow: bool = False,
    class_: Optional[str] = None,
) -> Element:
    """
    A general-purpose surface card. `glow` pulses a soft gold glow
    (needs `premium_keyframes()` rendered once on the page).
    """
    style = {
        "background": "var(--nx-surface)",
        "border": "1px solid var(--nx-border)",
        "border_radius": "var(--nx-radius)",
        "padding": "28px",
        "box_shadow": "var(--nx-shadow)" if elevated else "none",
    }
    if glow:
        style["animation"] = "nx-premium-glow 3s ease-in-out infinite"

    header = []
    if title:
        header.append(el("h3", title, style={"margin": "0 0 4px 0", "font_size": "1.15rem", "color": "var(--nx-text)"}))
    if subtitle:
        header.append(el("p", subtitle, style={"margin": "0 0 16px 0", "color": "var(--nx-text-muted)", "font_size": "0.9rem"}))

    return el("div", *header, *children, style=style, class_=class_)


def glass_panel(*children: Any, class_: Optional[str] = None) -> Element:
    """
    Frosted glass surface (`backdrop-filter: blur`) for hero
    overlays and floating callouts over imagery or gradients.
    """
    return el(
        "div", *children,
        style={
            "background": "var(--nx-premium-glass-bg)",
            "border": "1px solid var(--nx-premium-glass-border)",
            "border_radius": "var(--nx-radius)",
            "backdrop_filter": "blur(16px)",
            "-webkit-backdrop-filter": "blur(16px)",
            "padding": "24px",
        },
        class_=class_,
    )


def stat_card(label: str, value: str, *, icon: Optional[Element] = None, trend: Optional[str] = None) -> Element:
    """
    A KPI tile: `stat_card("Revenue", "$482K", trend="+12.4%")`.
    `trend` is shown as-is; prefix it with "-" yourself for a decline
    (kept as plain text rather than inferring sign, so locales that
    don't use a leading "-" for negatives aren't misrendered).
    """
    top = []
    if icon is not None:
        top.append(el("div", icon, style={"font_size": "1.4rem", "margin_bottom": "8px"}))
    return el(
        "div",
        *top,
        el("div", label, style={"font_size": "0.85rem", "color": "var(--nx-text-muted)", "margin_bottom": "6px"}),
        el("div", value, style={"font_size": "1.8rem", "font_weight": "700", "color": "var(--nx-text)"}),
        *([el("div", trend, style={"font_size": "0.85rem", "color": "var(--nx-success)", "margin_top": "4px"})] if trend else []),
        style={
            "background": "var(--nx-surface)",
            "border": "1px solid var(--nx-border)",
            "border_radius": "var(--nx-radius)",
            "padding": "22px",
            "box_shadow": "var(--nx-shadow)",
        },
    )


def pricing_card(
    plan: str,
    price: str,
    *,
    period: str = "/mo",
    features: Sequence[str] = (),
    highlighted: bool = False,
    cta_text: str = "Get Started",
    cta_href: str = "#",
    cta_shimmer: bool = False,
    cta_icon: Optional[Element] = None,
    cta_on_click: Optional[Callable] = None,
) -> Element:
    """
    A pricing-plan tile with a feature checklist and a CTA button.
    `highlighted=True` renders it as the "recommended" plan (gold
    border + badge, slightly raised).
    """
    border = "2px solid var(--nx-premium-gold)" if highlighted else "1px solid var(--nx-border)"
    transform = "translateY(-8px)" if highlighted else "none"

    feature_rows = [
        el("li", "\u2713  " + f, style={"padding": "6px 0", "color": "var(--nx-text)", "font_size": "0.92rem", "list_style": "none"})
        for f in features
    ]

    header_kids = [el("h3", plan, style={"margin": "0 0 4px 0", "font_size": "1.1rem"})]
    if highlighted:
        header_kids.append(premium_badge("Most Popular", variant="gold"))

    return el(
        "div",
        el("div", *header_kids, style={"display": "flex", "align_items": "center", "gap": "8px", "margin_bottom": "12px"}),
        el(
            "div",
            el("span", price, style={"font_size": "2.2rem", "font_weight": "800"}),
            el("span", period, style={"color": "var(--nx-text-muted)", "margin_left": "4px"}),
            style={"margin_bottom": "18px"},
        ),
        el("ul", *feature_rows, style={"padding": "0", "margin": "0 0 22px 0"}),
        premium_button(cta_text, variant="gold" if highlighted else "primary", href=cta_href, full_width=True, shimmer= cta_shimmer, icon= cta_icon, on_click= cta_on_click),
        style={
            "background": "var(--nx-surface)",
            "border": border,
            "border_radius": "var(--nx-radius)",
            "padding": "28px",
            "box_shadow": "0 14px 34px rgba(0,0,0,0.22)" if highlighted else "var(--nx-shadow)",
            "transform": transform,
        },
    )
