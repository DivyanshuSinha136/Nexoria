"""
nexoria.std.lib.navigation
=============================
Site chrome for the "lib" family: a top navbar with a glyph-tile
brand mark, a version pill and a GitHub CTA, and a minimal footer
with a "framework online" status pip.
"""

from __future__ import annotations
from typing import Any, Optional, Sequence

from ...core.element import el, Element
from .buttons import lib_button
from .badges import live_badge


def lib_navbar(
    brand: str,
    *,
    glyph: Optional[Element] = None,
    version: Optional[str] = None,
    links: Sequence[tuple] = (),
    github_href: Optional[str] = None,
    sticky: bool = True,
) -> Element:
    """
    `lib_navbar("Nexoria", version="v0.1.0", links=[("Architecture", "#architecture"), ("Runtime", "#runtime")], github_href="https://github.com/...")`.
    `links` is a sequence of `(label, href)` pairs. `glyph` is an
    optional small `Element` (icon/logo mark) shown in the gradient
    brand tile; a single letter is used when omitted.
    """
    mark = glyph if glyph is not None else brand[:1].upper()
    brand_kids = [
        el("div", mark, style={
            "width": "32px", "height": "32px", "border_radius": "8px",
            "background": "linear-gradient(135deg, var(--nx-lib-cyan), var(--nx-lib-pink))",
            "display": "flex", "align_items": "center", "justify_content": "center",
            "color": "#03141a", "font_weight": "800", "font_size": "0.95rem",
        }),
        el("span", brand, style={"font_weight": "700", "font_size": "1.05rem", "color": "var(--nx-text)"}),
    ]
    if version:
        brand_kids.append(el("span", version, style={
            "font_family": "var(--nx-font-mono)", "font_size": "0.72rem",
            "color": "var(--nx-text-muted)", "border": "1px solid var(--nx-border)",
            "border_radius": "999px", "padding": "2px 9px",
        }))

    link_els = [
        el("a", label, href=href, style={
            "color": "var(--nx-text-muted)", "text_decoration": "none",
            "font_size": "0.88rem", "font_weight": "500",
        }, onmouseover="this.style.color='var(--nx-text)'", onmouseout="this.style.color='var(--nx-text-muted)'")
        for label, href in links
    ]

    right: list[Any] = []
    if github_href:
        right.append(lib_button("GitHub", variant="solid", size="sm", href=github_href))

    style = {
        "display": "flex", "align_items": "center", "justify_content": "space-between",
        "padding": "16px 32px", "background": "var(--nx-bg)",
        "border_bottom": "1px solid var(--nx-border)",
    }
    if sticky:
        style.update({"position": "sticky", "top": "0", "z_index": "40"})

    return el(
        "nav",
        el("div", *brand_kids, style={"display": "flex", "align_items": "center", "gap": "12px"}),
        el("div", *link_els, style={"display": "flex", "align_items": "center", "gap": "28px"}),
        el("div", *right, style={"display": "flex", "align_items": "center", "gap": "14px"}),
        style=style,
    )


def lib_footer(
    brand: str,
    *,
    tagline: Optional[str] = None,
    links: Sequence[tuple] = (),
    status_label: str = "Framework online",
) -> Element:
    """
    `lib_footer("Nexoria", tagline="Built by ... \u00b7 Team", links=[("GitHub", "#"), ("MIT License", "#")])`.
    A slim bottom bar: brand + tagline on the left, plain text links
    and a pulsing "online" status pip on the right.
    """
    link_els = [
        el("a", label, href=href, style={
            "color": "var(--nx-text-muted)", "text_decoration": "none", "font_size": "0.82rem",
        })
        for label, href in links
    ]
    return el(
        "footer",
        el(
            "div",
            el("div", brand, style={"font_weight": "700", "font_size": "0.95rem", "color": "var(--nx-text)"}),
            *([el("div", tagline, style={"color": "var(--nx-text-muted)", "font_size": "0.78rem", "margin_top": "2px"})] if tagline else []),
        ),
        el(
            "div", *link_els, live_badge(status_label),
            style={"display": "flex", "align_items": "center", "gap": "26px"},
        ),
        style={
            "display": "flex", "align_items": "center", "justify_content": "space-between",
            "flex_wrap": "wrap", "gap": "16px", "padding": "24px 32px",
            "border_top": "1px solid var(--nx-border)", "background": "var(--nx-bg)",
        },
    )
