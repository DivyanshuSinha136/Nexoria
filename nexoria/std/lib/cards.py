"""
nexoria.std.lib.cards
========================
Surface containers for the "lib" family: a mac-style code editor
window with a tiny built-in Python highlighter (matching the
"app.py" panel on the Nexoria landing page), a numbered feature
card, and a small integration/adapter chip.
"""

from __future__ import annotations
import re
from typing import Any, Optional, Sequence

from ...core.element import el, Element
from .badges import live_badge

_PY_KEYWORDS = (
    "def class return import from as if elif else for while in not and or "
    "is lambda with try except finally raise yield pass break continue "
    "global nonlocal assert del True False None self async await"
).split()

_TOKEN_RE = re.compile(
    r"(?P<comment>#.*)"
    r'|(?P<string>f?r?"(?:[^"\\]|\\.)*"|f?r?\'(?:[^\'\\]|\\.)*\')'
    r"|(?P<decorator>@\w+)"
    r"|(?P<number>\b\d+\.?\d*\b)"
    r"|(?P<keyword>\b(?:" + "|".join(_PY_KEYWORDS) + r")\b)"
    r"|(?P<name>\b[A-Za-z_]\w*\b)"
)

_TOKEN_COLORS = {
    "comment": "#586380",
    "string": "#6ee7a8",
    "decorator": "var(--nx-lib-pink)",
    "number": "#ffb454",
    "keyword": "var(--nx-lib-pink)",
}


def _highlight_python(code: str) -> list:
    """Tiny, best-effort tokenizer -- not a real parser, just enough
    to color a short snippet the way a syntax-highlighted editor
    would (keywords, strings, numbers, comments, decorators, and a
    rough guess at class/call names)."""
    nodes: list = []
    pos = 0
    for m in _TOKEN_RE.finditer(code):
        if m.start() > pos:
            nodes.append(code[pos:m.start()])
        kind = m.lastgroup
        text = m.group()
        if kind == "name":
            if text[:1].isupper():
                color = "var(--nx-lib-cyan-soft)"  # looks like a class/type
            elif code[m.end():m.end() + 1] == "(":
                color = "var(--nx-text)"  # looks like a call
            else:
                color = "#c9d1e0"
            nodes.append(el("span", text, style={"color": color}))
        else:
            nodes.append(el("span", text, style={"color": _TOKEN_COLORS.get(kind, "#c9d1e0")}))
        pos = m.end()
    if pos < len(code):
        nodes.append(code[pos:])
    return nodes


def code_window(
    code: str,
    *,
    filename: str = "app.py",
    language: str = "python",
    live: bool = True,
    class_: Optional[str] = None,
) -> Element:
    """
    `code_window('from nexoria import App\\n...', filename="app.py")`.
    A mac-style editor window (traffic-light dots, filename, an
    optional pulsing "LIVE" pip) with the code lightly
    syntax-highlighted when `language == "python"` (any other value
    renders the code as plain mono text). Needs
    `nexoria.std.lib.theme.lib_keyframes()` rendered once on the page
    for the live dot to pulse.
    """
    dots = el(
        "div",
        *[
            el("span", style={
                "width": "10px", "height": "10px", "border_radius": "50%",
                "background": c, "display": "inline-block",
            })
            for c in ("#ff5f56", "#ffbd2e", "#27c93f")
        ],
        style={"display": "flex", "gap": "7px", "flex": "1"},
    )
    header = el(
        "div",
        dots,
        el("div", filename, style={
            "font_family": "var(--nx-font-mono)", "font_size": "0.78rem",
            "color": "var(--nx-text-muted)", "flex": "1", "text_align": "center",
        }),
        el("div", live_badge("LIVE") if live else "", style={"flex": "1", "display": "flex", "justify_content": "flex-end"}),
        style={
            "display": "flex", "align_items": "center",
            "padding": "14px 18px", "background": "var(--nx-lib-code-chrome)",
            "border_bottom": "1px solid var(--nx-border)",
        },
    )

    body_nodes = _highlight_python(code) if language == "python" else [code]
    body = el("pre", *body_nodes, style={
        "margin": "0", "padding": "22px 24px", "white_space": "pre",
        "overflow_x": "auto", "font_family": "var(--nx-font-mono)",
        "font_size": "0.84rem", "line_height": "1.7", "color": "#c9d1e0",
    })

    return el(
        "div", header, body,
        style={
            "background": "var(--nx-lib-code-bg)",
            "border": "1px solid var(--nx-border)",
            "border_radius": "var(--nx-radius)",
            "overflow": "hidden",
            "box_shadow": "0 24px 60px rgba(0,0,0,0.45)",
        },
        class_=class_,
    )


def lib_feature_card(
    title: str,
    desc: str,
    *,
    number: Optional[str] = None,
    icon: Optional[Element] = None,
    tag: Optional[Sequence[str]] = None,
    color: str = "cyan",
) -> Element:
    """
    `lib_feature_card("Server-rendered first", "The first request returns real HTML.", number="01", icon=Icon("lightning-fill"), tag=["SSR", "REAL HTML"])`.
    `color`: "cyan" | "pink" | "muted" -- tints the icon and tag.
    """
    from .badges import lib_tag_row

    fg = {"cyan": "var(--nx-lib-cyan)", "pink": "var(--nx-lib-pink)"}.get(color, "var(--nx-text-muted)")

    head = []
    if icon is not None:
        head.append(el("div", icon, style={
            "width": "38px", "height": "38px", "border_radius": "10px",
            "display": "flex", "align_items": "center", "justify_content": "center",
            "background": "var(--nx-surface-alt)", "color": fg, "font_size": "1.2rem",
        }))
    if number:
        head.append(el("div", number, style={
            "margin_left": "auto", "font_family": "var(--nx-font-mono)",
            "font_size": "0.78rem", "color": "var(--nx-text-muted)",
        }))

    kids = []
    if head:
        kids.append(el("div", *head, style={"display": "flex", "align_items": "center", "margin_bottom": "22px"}))
    kids.append(el("h3", title, style={"margin": "0 0 10px 0", "font_size": "1.05rem", "color": "var(--nx-text)"}))
    kids.append(el("p", desc, style={
        "margin": "0", "color": "var(--nx-text-muted)", "line_height": "1.6", "font_size": "0.9rem",
        "flex": "1",
    }))
    if tag:
        kids.append(el("div", lib_tag_row(tag, color=color), style={"margin_top": "22px"}))

    return el("div", *kids, style={
        "display": "flex", "flex_direction": "column",
        "background": "var(--nx-surface)", "border": "1px solid var(--nx-border)",
        "border_radius": "var(--nx-radius)", "padding": "28px",
        "min_height": "200px",
    })


def integration_chip(name: str, desc: str, *, icon: Optional[Element] = None) -> Element:
    """
    `integration_chip("GSAP", "Timelines in Python", icon=Icon("stars"))`.
    A small bordered adapter/integration tile, like the "batteries
    included" logo row on the Nexoria landing page.
    """
    head = []
    if icon is not None:
        head.append(el("div", icon, style={
            "width": "30px", "height": "30px", "border_radius": "8px",
            "display": "flex", "align_items": "center", "justify_content": "center",
            "background": "var(--nx-surface-alt)", "color": "var(--nx-lib-cyan)", "font_size": "1rem",
        }))
    return el(
        "div",
        el("div", *head, el("div", name, style={"font_weight": "700", "font_size": "0.92rem", "color": "var(--nx-text)"}),
           style={"display": "flex", "align_items": "center", "gap": "10px", "margin_bottom": "6px"}),
        el("div", desc, style={"color": "var(--nx-text-muted)", "font_size": "0.8rem"}),
        style={
            "background": "var(--nx-surface)", "border": "1px solid var(--nx-border)",
            "border_radius": "var(--nx-radius-sm)", "padding": "16px 18px",
        },
    )
