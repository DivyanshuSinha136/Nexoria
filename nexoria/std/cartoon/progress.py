"""
nexoria.std.cartoon.progress
===============================
A chunky, comic-styled progress bar: thick outline track, flat-color
fill, and a little emoji "blob" riding the leading edge.
"""

from __future__ import annotations
from typing import Optional

from ...core.element import el, Element


def blob_progress(
    value: float,
    *,
    max_value: float = 100,
    color: str = "var(--nx-cartoon-mint)",
    label: Optional[str] = None,
    emoji: str = "\U0001F418",
) -> Element:
    """
    `blob_progress(65, label="Level up!")`. `value`/`max_value` are
    plain numbers; the percentage is computed and clamped to
    [0, 100] here, so callers never hand in an already-normalized
    percentage.
    """
    pct = 0.0 if max_value <= 0 else min(100.0, max(0.0, (value / max_value) * 100))

    fill = el("div", style={
        "height": "100%", "width": f"{pct}%", "background": color,
        "border_radius": "999px", "transition": "width 0.3s ease",
    })
    blob = el("span", emoji, style={
        "position": "absolute", "top": "50%", "left": f"{pct}%",
        "transform": "translate(-50%, -50%)", "font_size": "1.4rem",
    })
    track = el(
        "div", fill, blob,
        style={
            "position": "relative", "height": "22px", "background": "var(--nx-cartoon-paper)",
            "border": "3px solid var(--nx-cartoon-ink)", "border_radius": "999px",
            "overflow": "visible",
        },
    )

    kids = [track]
    if label:
        kids.insert(0, el("div", label, style={
            "font_weight": "800", "color": "var(--nx-cartoon-ink)", "margin_bottom": "8px",
        }))
    return el("div", *kids)
