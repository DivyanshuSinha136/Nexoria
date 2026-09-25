"""
nexoria.std.svg
==================
Low-level SVG drawing support for `nexoria.std`: `PathBuilder`, a
fluent builder for `<path d="...">` data with full command coverage
(move, line, horizontal/vertical shorthand, cubic and quadratic
Bezier curves and their smooth shorthand forms, elliptical arcs,
close-path -- absolute and relative), plus shape helpers built on top
(`circle`, `rounded_rect`, `smooth_through` for a curve fit through
arbitrary points) and small `<svg>`/`<path>` wrapper convenience.

No CDN, no client adapter, no `App(...)` flag -- pure Python, same
"plain import" contract as the rest of `nexoria.std`.

    from nexoria.std.svg import PathBuilder, svg_canvas

    heart = PathBuilder().move_to(12, 21) \\
        .cubic_to(3, 13, 3, 8, 7.5, 5.5) \\
        .cubic_to(10, 4, 12, 6, 12, 6) \\
        .cubic_to(12, 6, 14, 4, 16.5, 5.5) \\
        .cubic_to(21, 8, 21, 13, 12, 21) \\
        .close()

    svg_canvas(heart.to_element(fill="var(--nx-danger)"), view_box="0 0 24 24")
"""

from __future__ import annotations

from .path import PathBuilder
from .canvas import svg_canvas, svg_path

__all__ = ["PathBuilder", "svg_canvas", "svg_path"]
