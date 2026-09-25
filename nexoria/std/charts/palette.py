"""
nexoria.std.charts.palette
=============================
The default series palette every chart in `nexoria.std.charts` falls
back to when no explicit `colors=` is given. Pulled from the base
theme's CSS custom properties (`--nx-primary`, `--nx-accent`, ...)
rather than hard-coded hex values, so charts automatically re-color
to match `App(theme=...)` the same way `nx-btn`/`nx-card` do.
"""

from __future__ import annotations
from typing import List, Optional, Sequence

DEFAULT_PALETTE: List[str] = [
    "var(--nx-primary)",
    "var(--nx-accent)",
    "var(--nx-success)",
    "var(--nx-warning)",
    "var(--nx-danger)",
    "var(--nx-primary-hover)",
]


def color_for(index: int, colors: Optional[Sequence[str]] = None) -> str:
    """The color for series/slice/bar `index`, cycling through
    `colors` (or `DEFAULT_PALETTE` when `colors` is `None`/empty)."""
    palette = list(colors) if colors else DEFAULT_PALETTE
    return palette[index % len(palette)]
