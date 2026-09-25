"""
nexoria.std.webtools.accordion
==================================
A vertically-stacked, collapsible list of sections. Each header
toggles its own panel via a literal `onclick=` that flips both the
panel's `display` and the header's chevron rotation -- no shared
runtime, no ids needed, since `this` and `nextElementSibling` always
resolve to the exact pair being clicked.
"""

from __future__ import annotations
from typing import Any, Mapping, Sequence

from ...core.element import el, Element


def accordion(items: Sequence[Mapping[str, Any]], *, allow_multiple: bool = True) -> Element:
    """
    `accordion([{"title": "What's included?", "content": "Everything in Pro."}])`.
    Each item needs `title` and `content` (a string or an `Element`).
    `allow_multiple=False` closes any other open panel when one is
    opened (accordion-style exclusivity) via a small per-click sweep
    over sibling panels.
    """
    rows = []
    for item in items:
        toggle_js = (
            "var panel=this.nextElementSibling;"
            "var open=panel.style.display==='block';"
            "panel.style.display=open?'none':'block';"
            "this.querySelector('[data-nx-chevron]').style.transform=open?'rotate(0deg)':'rotate(180deg)';"
        )
        if not allow_multiple:
            toggle_js = (
                "var self=this;"
                "var group=self.closest('[data-nx-accordion]');"
                "group.querySelectorAll(':scope > [data-nx-accordion-row] > div').forEach(function(p){"
                "if(p!==self.nextElementSibling){p.style.display='none';}});"
                "group.querySelectorAll('[data-nx-chevron]').forEach(function(c){"
                "if(c!==self.querySelector('[data-nx-chevron]')){c.style.transform='rotate(0deg)';}});"
            ) + toggle_js

        header = el(
            "button", item.get("title", ""),
            el("span", "\u25BE", data_nx_chevron="true", style={"transition": "transform 0.15s ease", "margin_left": "auto"}),
            type="button", onclick=toggle_js,
            style={
                "display": "flex", "align_items": "center", "gap": "8px", "width": "100%",
                "text_align": "left", "padding": "14px 4px", "background": "none", "border": "none",
                "cursor": "pointer", "font_weight": "700", "font_size": "0.95rem", "color": "var(--nx-text)",
            },
        )
        panel = el("div", item.get("content", ""), style={
            "display": "none", "padding": "0 4px 16px 4px", "color": "var(--nx-text-muted)", "font_size": "0.9rem", "line_height": "1.6",
        })
        rows.append(el("div", header, panel, data_nx_accordion_row="true", style={"border_bottom": "1px solid var(--nx-border)"}))

    return el("div", *rows, data_nx_accordion="true")
