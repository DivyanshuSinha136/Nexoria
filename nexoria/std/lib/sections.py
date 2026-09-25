"""
nexoria.std.lib.sections
===========================
Page-level building blocks for the "lib" family: a split hero with a
code window, a connected step pipeline, a numbered feature grid, an
integrations strip, and a bottom install call-to-action -- enough to
assemble a landing page shaped like Nexoria's own.
"""

from __future__ import annotations
from typing import Any, Mapping, Optional, Sequence

from ...core.element import el, Element
from .badges import lib_pill, lib_eyebrow, stat_chip_row
from .buttons import lib_button
from .cards import code_window, lib_feature_card, integration_chip


def lib_hero(
    title: str,
    *,
    highlight: Optional[str] = None,
    eyebrow: Optional[str] = None,
    subtitle: Optional[str] = None,
    primary_cta: Optional[str] = None,
    primary_href: str = "#",
    secondary_cta: Optional[str] = None,
    secondary_href: str = "#",
    stats: Sequence[str] = (),
    code: Optional[str] = None,
    code_filename: str = "app.py",
    animate: bool = False,
) -> Element:
    """
    `lib_hero("Full-stack in", highlight="pure Python.", eyebrow="Python, all the way through", subtitle="No JSX. No templates.", primary_cta="Start building", code="from nexoria import App\\n...")`.

    `highlight` is rendered as its own line in a cyan-to-pink
    gradient (the "pure Python." treatment); `code` renders a
    `code_window()` alongside the copy when given, otherwise the
    copy spans full width. `animate=True` fades the copy in on load
    (needs `nexoria.std.lib.theme.lib_keyframes()` rendered once on
    the page).
    """
    copy_kids = []
    if eyebrow:
        copy_kids.append(lib_pill(eyebrow))
    heading_kids = [title]
    if highlight:
        heading_kids = [
            el("div", title),
            el("div", highlight, style={
                "background": "linear-gradient(90deg, var(--nx-lib-cyan), var(--nx-lib-pink))",
                "-webkit-background-clip": "text", "background-clip": "text",
                "color": "transparent",
            }),
        ]
    copy_kids.append(el("h1", *heading_kids, style={
        "font_size": "clamp(2.4rem, 5.5vw, 3.8rem)", "font_weight": "800",
        "line_height": "1.1", "margin": "18px 0 20px 0", "color": "var(--nx-text)",
    }))
    if subtitle:
        copy_kids.append(el("p", subtitle, style={
            "font_size": "1.05rem", "color": "var(--nx-text-muted)",
            "line_height": "1.65", "margin": "0 0 32px 0", "max_width": "480px",
        }))

    ctas = []
    if primary_cta:
        ctas.append(lib_button(primary_cta, trailing_icon=el("span", "\u2192"), variant="solid", size="lg", href=primary_href))
    if secondary_cta:
        ctas.append(lib_button(secondary_cta, variant="outline", size="lg", href=secondary_href))
    if ctas:
        copy_kids.append(el("div", *ctas, style={"display": "flex", "gap": "14px", "flex_wrap": "wrap", "margin_bottom": "28px"}))

    if stats:
        copy_kids.append(stat_chip_row(stats))

    copy_style: dict[str, Any] = {"flex": "1", "min_width": "300px"}
    if animate:
        copy_style["animation"] = "nx-lib-rise 0.7s ease both"
    copy = el("div", *copy_kids, style=copy_style)

    row_kids = [copy]
    if code:
        row_kids.append(el("div", code_window(code, filename=code_filename), style={"flex": "1", "min_width": "320px"}))

    return el(
        "section",
        el("div", *row_kids, style={
            "display": "flex", "gap": "56px", "align_items": "center",
            "flex_wrap": "wrap", "max_width": "1180px", "margin": "0 auto",
            "padding": "88px 24px",
        }),
        style={"background": "var(--nx-bg)", "position": "relative"},
    )


def pipeline_steps(
    steps: Sequence[Mapping[str, Any]],
    *,
    eyebrow: Optional[str] = None,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
) -> Element:
    """
    `pipeline_steps([{"icon": Icon("filetype-py"), "number": "01", "title": "Python tree", "desc": "Components, routes, state"}, ...], eyebrow="THE REQUEST JOURNEY", title="Python in. Live interface out.")`.
    A horizontal row of circular icon nodes connected by a line, each
    labeled with a number and a title/description -- the "request
    journey" diagram from the Nexoria landing page.
    """
    head = []
    if eyebrow:
        head.append(lib_eyebrow(eyebrow))
    if title:
        head.append(el("h2", title, style={"font_size": "2rem", "font_weight": "800", "color": "var(--nx-text)", "margin": "0 0 14px 0"}))
    if subtitle:
        head.append(el("p", subtitle, style={"color": "var(--nx-text-muted)", "font_size": "1rem", "max_width": "560px", "line_height": "1.6"}))

    nodes = []
    for i, s in enumerate(steps):
        node_kids = []
        if s.get("icon") is not None:
            node_kids.append(s["icon"])
        node = el("div", *node_kids, style={
            "width": "60px", "height": "60px", "border_radius": "50%",
            "border": "1px solid var(--nx-lib-cyan)", "display": "flex",
            "align_items": "center", "justify_content": "center",
            "color": "var(--nx-lib-cyan)", "font_size": "1.3rem",
            "background": "var(--nx-bg)", "position": "relative", "z_index": "1",
        })
        nodes.append(el(
            "div",
            node,
            el("div", s.get("number", f"{i + 1:02d}"), style={
                "font_family": "var(--nx-font-mono)", "font_size": "0.72rem",
                "color": "var(--nx-lib-pink)", "margin": "18px 0 6px 0",
            }),
            el("div", s.get("title", ""), style={"font_weight": "700", "font_size": "1.02rem", "color": "var(--nx-text)", "margin_bottom": "4px"}),
            el("div", s.get("desc", ""), style={"color": "var(--nx-text-muted)", "font_size": "0.85rem"}),
            style={"flex": "1", "min_width": "160px"},
        ))

    track = el(
        "div", *nodes,
        style={
            "display": "flex", "gap": "24px", "position": "relative",
            "background_image": "linear-gradient(var(--nx-border), var(--nx-border))",
            "background_repeat": "no-repeat", "background_size": "100% 1px",
            "background_position": "left 30px",
        },
    )

    return el(
        "section",
        el("div", *head, track, style={"max_width": "1180px", "margin": "0 auto", "padding": "88px 24px"}),
        style={"background": "var(--nx-bg)"},
    )


def feature_trio(
    features: Sequence[Mapping[str, Any]],
    *,
    eyebrow: Optional[str] = None,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
) -> Element:
    """
    `feature_trio([{"icon": Icon("lightning-fill"), "number": "01", "title": "Server-rendered first", "desc": "...", "tag": ["SSR", "REAL HTML"], "color": "cyan"}, ...], eyebrow="WHY NEXORIA", title="A small runtime. A very big surface.")`.
    A responsive grid of `lib_feature_card`s under a section heading.
    """
    head = []
    if eyebrow:
        head.append(lib_eyebrow(eyebrow))
    if title:
        head.append(el("h2", title, style={"font_size": "2.1rem", "font_weight": "800", "color": "var(--nx-text)", "margin": "0 0 14px 0", "line_height": "1.2"}))
    if subtitle:
        head.append(el("p", subtitle, style={"color": "var(--nx-text-muted)", "font_size": "1rem", "max_width": "480px", "line_height": "1.6"}))

    cards = [
        lib_feature_card(
            f.get("title", ""), f.get("desc", ""),
            number=f.get("number"), icon=f.get("icon"),
            tag=f.get("tag"), color=f.get("color", "cyan"),
        )
        for f in features
    ]
    grid = el("div", *cards, style={
        "display": "grid", "grid_template_columns": "repeat(auto-fit, minmax(260px, 1fr))",
        "gap": "20px",
    })

    return el(
        "section",
        el("div", *head, grid, style={"max_width": "1180px", "margin": "0 auto", "padding": "88px 24px"}),
        style={"background": "var(--nx-bg)"},
    )


def integrations_row(
    items: Sequence[Mapping[str, Any]],
    *,
    eyebrow: Optional[str] = None,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
) -> Element:
    """
    `integrations_row([{"icon": Icon("stars"), "name": "GSAP", "desc": "Timelines in Python"}, ...], eyebrow="ONE FRAMEWORK, MANY SURFACES", title="Batteries included. Complexity optional.")`.
    A responsive grid of `integration_chip`s -- the adapter/logo row.
    """
    head = []
    if eyebrow:
        head.append(lib_eyebrow(eyebrow))
    if title:
        head.append(el("h2", title, style={"font_size": "2rem", "font_weight": "800", "color": "var(--nx-text)", "margin": "0 0 12px 0", "line_height": "1.2"}))
    if subtitle:
        head.append(el("p", subtitle, style={"color": "var(--nx-text-muted)", "font_size": "0.95rem", "max_width": "440px", "line_height": "1.6"}))

    chips = [integration_chip(i.get("name", ""), i.get("desc", ""), icon=i.get("icon")) for i in items]
    grid = el("div", *chips, style={
        "display": "grid", "grid_template_columns": "repeat(auto-fit, minmax(180px, 1fr))",
        "gap": "14px",
    })

    return el(
        "section",
        el("div", *head, grid, style={"max_width": "1180px", "margin": "0 auto", "padding": "88px 24px"}),
        style={"background": "var(--nx-bg)"},
    )


def install_cta(
    title: str,
    command: str,
    *,
    eyebrow: Optional[str] = None,
    tagline: Optional[str] = None,
    github_href: Optional[str] = None,
    docs_href: Optional[str] = None,
) -> Element:
    """
    `install_cta("Your full stack starts with one command.", "pip install nexoria", eyebrow="SHIP SOMETHING", tagline="Cross-platform. Production-grade. Open source.", github_href="https://github.com/...", docs_href="/docs")`.
    The closing panel: a big line of copy next to a copyable install
    command, with optional repo/docs links underneath.
    """
    head = []
    if eyebrow:
        head.append(lib_eyebrow(eyebrow))
    head.append(el("h2", title, style={
        "font_size": "clamp(1.8rem, 4vw, 2.6rem)", "font_weight": "800",
        "color": "var(--nx-text)", "line_height": "1.2", "margin": "0",
    }))
    if tagline:
        head.append(el("p", tagline, style={"color": "var(--nx-text-muted)", "margin": "14px 0 0 0"}))

    links = []
    if github_href:
        links.append(el("a", "View repository", href=github_href, style={"color": "var(--nx-text-muted)", "text_decoration": "none", "font_size": "0.88rem"}))
    if docs_href:
        links.append(el("a", "Read documentation", href=docs_href, style={"color": "var(--nx-text-muted)", "text_decoration": "none", "font_size": "0.88rem"}))

    command_box = el(
        "div",
        el("div",
           el("span", "$", style={"color": "var(--nx-lib-cyan)", "margin_right": "10px"}),
           el("span", command, style={"color": "var(--nx-text)"}),
           style={"font_family": "var(--nx-font-mono)", "font_size": "0.95rem"}),
        el("span", "COPY", style={
            "font_family": "var(--nx-font-mono)", "font_size": "0.7rem",
            "color": "var(--nx-lib-cyan)", "letter_spacing": "0.06em",
            "cursor": "pointer",
        }, onclick=f"navigator.clipboard && navigator.clipboard.writeText('{command}')"),
        style={
            "display": "flex", "align_items": "center", "justify_content": "space-between",
            "background": "var(--nx-bg)", "border": "1px solid var(--nx-border)",
            "border_radius": "var(--nx-radius-sm)", "padding": "16px 20px",
            "gap": "20px", "flex_wrap": "wrap",
        },
    )

    right = el("div", command_box, *([el("div", *links, style={"display": "flex", "gap": "24px", "margin_top": "14px"})] if links else []),
               style={"flex": "1", "min_width": "280px"})

    panel = el(
        "div",
        el("div", *head, style={"flex": "1", "min_width": "280px"}),
        right,
        style={
            "display": "flex", "gap": "40px", "flex_wrap": "wrap",
            "align_items": "center", "background": "var(--nx-surface)",
            "border": "1px solid var(--nx-border)", "border_radius": "20px",
            "padding": "48px",
        },
    )

    return el(
        "section",
        el("div", panel, style={"max_width": "1180px", "margin": "0 auto", "padding": "48px 24px 88px 24px"}),
        style={"background": "var(--nx-bg)"},
    )
