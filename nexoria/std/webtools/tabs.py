"""
nexoria.std.webtools.tabs
=============================
A tabbed panel switcher. Each tab button, when clicked, activates
its own panel and deactivates its siblings by walking up to the
shared `data-nx-tabs` container -- so, like `accordion()`, no shared
runtime and no manually-managed ids are needed even with several tab
groups on one page.
"""

from __future__ import annotations
from typing import Any, Mapping, Sequence

from ...core.element import el, Element

_INACTIVE_STYLE = {
    "padding": "10px 18px", "border": "none", "border_bottom": "2px solid transparent",
    "background": "none", "cursor": "pointer", "font_weight": "600", "font_size": "0.92rem",
    "color": "var(--nx-text)",
}
_ACTIVE_STYLE = {
    **_INACTIVE_STYLE,
    "border_bottom": "2px solid var(--nx-primary)", "color": "var(--nx-primary)", "font_weight": "700",
}


def tabs(items: Sequence[Mapping[str, Any]], *, active: int = 0) -> Element:
    """
    `tabs([{"label": "Overview", "content": el("p", "...")}, {"label": "Specs", "content": el("p", "...")}])`.
    Each item needs `label` and `content`. `active` is the index of
    the tab shown initially.
    """
    switch_js_for = lambda i: (
        "var group=this.closest('[data-nx-tabs]');"
        "group.querySelectorAll('[data-nx-tab-btn]').forEach(function(b){"
        "b.style.borderBottom='2px solid transparent';b.style.color='var(--nx-text)';b.style.fontWeight='600';});"
        "group.querySelectorAll('[data-nx-tab-panel]').forEach(function(p){p.style.display='none';});"
        "this.style.borderBottom='2px solid var(--nx-primary)';this.style.color='var(--nx-primary)';this.style.fontWeight='700';"
        f"group.querySelector('[data-nx-tab-panel=\"{i}\"]').style.display='block';"
    )

    tab_buttons = [
        el(
            "button", item.get("label", f"Tab {i + 1}"),
            type="button", onclick=switch_js_for(i), data_nx_tab_btn="true",
            style=_ACTIVE_STYLE if i == active else _INACTIVE_STYLE,
        )
        for i, item in enumerate(items)
    ]
    panels = [
        el(
            "div", item.get("content", ""),
            data_nx_tab_panel=str(i),
            style={"display": "block" if i == active else "none", "padding": "18px 4px"},
        )
        for i, item in enumerate(items)
    ]

    return el(
        "div",
        el("div", *tab_buttons, style={"display": "flex", "gap": "4px", "border_bottom": "1px solid var(--nx-border)"}),
        el("div", *panels),
        data_nx_tabs="true",
    )
