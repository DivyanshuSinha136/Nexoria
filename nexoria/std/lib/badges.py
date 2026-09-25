"""
nexoria.std.lib.badges
=========================
Small labels for the "lib" family: a dotted pill (hero eyebrow, e.g.
"Python, all the way through"), an uppercase section eyebrow (e.g.
"WHY NEXORIA"), a pulsing "LIVE"/status pip, and a colon-separated
mono tag (e.g. "SSR \u00b7 REAL HTML").
"""

from __future__ import annotations
from typing import Optional, Sequence

from ...core.element import el, Element

_ACCENTS = {
    "cyan": ("var(--nx-lib-cyan)", "rgba(34, 229, 229, 0.12)", "rgba(34, 229, 229, 0.35)"),
    "pink": ("var(--nx-lib-pink)", "rgba(255, 79, 129, 0.12)", "rgba(255, 79, 129, 0.35)"),
    "muted": ("var(--nx-text-muted)", "var(--nx-surface-alt)", "var(--nx-border)"),
}


def lib_pill(text: str, *, dot: bool = True, color: str = "cyan") -> Element:
    """
    `lib_pill("Python, all the way through")`. A small rounded,
    bordered chip with an optional colored status dot -- the hero
    badge style. `color`: "cyan" | "pink" | "muted".
    """
    fg, _bg, border = _ACCENTS.get(color, _ACCENTS["cyan"])
    kids = []
    if dot:
        kids.append(el("span", style={
            "width": "6px", "height": "6px", "border_radius": "50%",
            "background": fg, "display": "inline-block", "flex_shrink": "0",
        }))
    kids.append(el("span", text))
    return el(
        "div", *kids,
        style={
            "display": "inline-flex", "align_items": "center", "gap": "8px",
            "padding": "6px 14px", "border_radius": "999px",
            "border": f"1px solid {border}",
            "background": "var(--nx-surface)",
            "color": "var(--nx-text-muted)",
            "font_size": "0.8rem", "font_family": "var(--nx-font-mono)",
        },
    )


def lib_eyebrow(text: str, *, color: str = "cyan") -> Element:
    """
    `lib_eyebrow("WHY NEXORIA")`. An uppercase, letter-spaced section
    label with no border/background -- used above section headings.
    """
    fg, _bg, _border = _ACCENTS.get(color, _ACCENTS["cyan"])
    return el("div", text.upper(), style={
        "color": fg, "font_family": "var(--nx-font-mono)",
        "font_size": "0.78rem", "font_weight": "700",
        "letter_spacing": "0.12em", "margin_bottom": "14px",
    })


def live_badge(label: str = "LIVE", *, color: str = "cyan", pulse: bool = True) -> Element:
    """
    `live_badge()` / `live_badge("Framework online")`. A small
    colored dot next to an uppercase mono label; the dot pulses when
    `pulse=True` (needs `nexoria.std.lib.theme.lib_keyframes()`
    rendered once on the page).
    """
    fg, _bg, _border = _ACCENTS.get(color, _ACCENTS["cyan"])
    dot_style = {
        "width": "6px", "height": "6px", "border_radius": "50%",
        "background": fg, "display": "inline-block", "flex_shrink": "0",
        "box_shadow": f"0 0 8px {fg}",
    }
    if pulse:
        dot_style["animation"] = "nx-lib-pulse 1.8s ease-in-out infinite"
    return el(
        "div",
        el("span", style=dot_style),
        el("span", label, style={
            "font_family": "var(--nx-font-mono)", "font_size": "0.72rem",
            "letter_spacing": "0.06em", "color": "var(--nx-text-muted)",
        }),
        style={"display": "inline-flex", "align_items": "center", "gap": "7px"},
    )


def lib_tag(text: str, *, color: str = "pink") -> Element:
    """
    `lib_tag("SSR \u00b7 REAL HTML")`. A small uppercase mono tag used
    under feature cards -- pass parts already joined with " \u00b7 " or
    build one from a sequence with `lib_tag_row`.
    """
    fg, _bg, _border = _ACCENTS.get(color, _ACCENTS["pink"])
    return el("div", text.upper(), style={
        "font_family": "var(--nx-font-mono)", "font_size": "0.72rem",
        "font_weight": "700", "letter_spacing": "0.08em", "color": fg,
    })


def lib_tag_row(parts: Sequence[str], *, color: str = "pink") -> Element:
    """`lib_tag_row(["SSR", "REAL HTML"])` -> `lib_tag("SSR \u00b7 REAL HTML")`."""
    return lib_tag(" \u00b7 ".join(parts), color=color)


def stat_chip_row(stats: Sequence[str], *, color: str = "cyan") -> Element:
    """
    `stat_chip_row(["~4KB runtime", "0 JSX", "MIT licensed"])`. A row
    of small mono stats separated by dots, like the strip under the
    Nexoria hero. The first word of each stat (if it looks like a
    value, e.g. "~4KB") is tinted; pass plain strings otherwise.
    """
    fg, _bg, _border = _ACCENTS.get(color, _ACCENTS["cyan"])
    items = []
    for i, s in enumerate(stats):
        if i:
            items.append(el("span", "\u2022", style={
                "color": "var(--nx-border)", "font_size": "0.8rem",
            }))
        parts = s.split(" ", 1)
        head_style = {"color": fg, "font_weight": "700"}
        if len(parts) == 2:
            items.append(el(
                "span",
                el("span", parts[0], style=head_style), " " + parts[1],
                style={"font_size": "0.82rem", "color": "var(--nx-text-muted)", "font_family": "var(--nx-font-mono)"},
            ))
        else:
            items.append(el("span", s, style={
                "font_size": "0.82rem", "color": "var(--nx-text-muted)", "font_family": "var(--nx-font-mono)",
            }))
    return el("div", *items, style={"display": "flex", "align_items": "center", "gap": "12px", "flex_wrap": "wrap"})
