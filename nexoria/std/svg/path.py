"""
nexoria.std.svg.path
=======================
`PathBuilder` -- a fluent builder for the SVG `<path d="...">` mini
language, with full command coverage (move, line, horizontal/vertical
shorthand, cubic and quadratic Bezier curves plus their "smooth"
shorthand forms, elliptical arcs, close-path) in both absolute and
relative form, so you never have to hand-format path-data strings.

    from nexoria.std.svg import PathBuilder

    heart = (
        PathBuilder()
        .move_to(12, 21)
        .cubic_to(3, 13, 3, 8, 7.5, 5.5)
        .cubic_to(10, 4, 12, 6, 12, 6)
        .cubic_to(12, 6, 14, 4, 16.5, 5.5)
        .cubic_to(21, 8, 21, 13, 12, 21)
        .close()
    )
    el("svg", heart.to_element(fill="var(--nx-danger)"), view_box="0 0 24 24")

No CDN, no client adapter, no `App(...)` flag -- pure Python, same
"plain import" contract as the rest of `nexoria.std`. Every drawing
method returns `self`, so calls chain; `.to_element()` follows the
`.to_element()` protocol the rest of the framework's declarative
wrappers use (`Icon`, `Animation`, ...), so a bare `PathBuilder()...`
chain also drops straight into `el(...)` as a child without calling
`.to_element()` yourself -- see `nexoria.core.element._coerce_child`.
"""

from __future__ import annotations
import math
from typing import Iterable, List, Optional, Sequence, Tuple, Union

Point = Tuple[float, float]

# 4/3 * (sqrt(2) - 1) -- the standard "kappa" constant for approximating
# a quarter-circle arc with a single cubic Bezier control-point offset.
_KAPPA = 0.5522847498


def _fmt(n: Union[int, float]) -> str:
    """Compact number formatting for path data: `10` -> `"10"`,
    `10.5` -> `"10.5"`, `10.0` -> `"10"` -- no scientific notation,
    no trailing zeros."""
    n = float(n)
    if n.is_integer():
        return str(int(n))
    return f"{n:.4f}".rstrip("0").rstrip(".")


class PathBuilder:
    """
    Build an SVG path's `d` attribute one command at a time. Tracks
    the current point (and each subpath's start point, for `.close()`)
    so `.current_point` / `.start_point` are always available -- handy
    for chaining shapes relative to where the pen left off.
    """

    __slots__ = ("_commands", "_current", "_start")

    def __init__(self) -> None:
        self._commands: List[str] = []
        self._current: Point = (0.0, 0.0)
        self._start: Point = (0.0, 0.0)

    # -- internals ------------------------------------------------------

    def _emit(self, letter: str, *nums: Union[int, float]) -> "PathBuilder":
        self._commands.append(letter + ",".join(_fmt(n) for n in nums) if nums else letter)
        return self

    # -- move ---------------------------------------------------------------

    def move_to(self, x: float, y: float) -> "PathBuilder":
        """`M x,y` -- start a new subpath at an absolute point."""
        self._current = self._start = (x, y)
        return self._emit("M", x, y)

    def move_by(self, dx: float, dy: float) -> "PathBuilder":
        """`m dx,dy` -- start a new subpath, relative to the current point."""
        x, y = self._current[0] + dx, self._current[1] + dy
        self._current = self._start = (x, y)
        return self._emit("m", dx, dy)

    # -- lines ------------------------------------------------------------

    def line_to(self, x: float, y: float) -> "PathBuilder":
        """`L x,y`."""
        self._current = (x, y)
        return self._emit("L", x, y)

    def line_by(self, dx: float, dy: float) -> "PathBuilder":
        """`l dx,dy`."""
        self._current = (self._current[0] + dx, self._current[1] + dy)
        return self._emit("l", dx, dy)

    def horizontal_to(self, x: float) -> "PathBuilder":
        """`H x` -- a horizontal line to an absolute x, same y."""
        self._current = (x, self._current[1])
        return self._emit("H", x)

    def horizontal_by(self, dx: float) -> "PathBuilder":
        """`h dx`."""
        self._current = (self._current[0] + dx, self._current[1])
        return self._emit("h", dx)

    def vertical_to(self, y: float) -> "PathBuilder":
        """`V y` -- a vertical line to an absolute y, same x."""
        self._current = (self._current[0], y)
        return self._emit("V", y)

    def vertical_by(self, dy: float) -> "PathBuilder":
        """`v dy`."""
        self._current = (self._current[0], self._current[1] + dy)
        return self._emit("v", dy)

    # -- cubic Bezier curves ------------------------------------------------

    def cubic_to(self, x1: float, y1: float, x2: float, y2: float, x: float, y: float) -> "PathBuilder":
        """`C x1,y1 x2,y2 x,y` -- a cubic Bezier with two explicit
        control points, ending at an absolute `(x, y)`."""
        self._current = (x, y)
        return self._emit("C", x1, y1, x2, y2, x, y)

    def cubic_by(self, dx1: float, dy1: float, dx2: float, dy2: float, dx: float, dy: float) -> "PathBuilder":
        """`c dx1,dy1 dx2,dy2 dx,dy` -- relative cubic Bezier."""
        self._current = (self._current[0] + dx, self._current[1] + dy)
        return self._emit("c", dx1, dy1, dx2, dy2, dx, dy)

    def smooth_cubic_to(self, x2: float, y2: float, x: float, y: float) -> "PathBuilder":
        """`S x2,y2 x,y` -- a cubic Bezier whose first control point
        mirrors the previous curve's second control point (only
        meaningful right after another `C`/`S`)."""
        self._current = (x, y)
        return self._emit("S", x2, y2, x, y)

    def smooth_cubic_by(self, dx2: float, dy2: float, dx: float, dy: float) -> "PathBuilder":
        """`s dx2,dy2 dx,dy`."""
        self._current = (self._current[0] + dx, self._current[1] + dy)
        return self._emit("s", dx2, dy2, dx, dy)

    # -- quadratic Bezier curves ---------------------------------------------

    def quad_to(self, x1: float, y1: float, x: float, y: float) -> "PathBuilder":
        """`Q x1,y1 x,y` -- a quadratic Bezier with one control point."""
        self._current = (x, y)
        return self._emit("Q", x1, y1, x, y)

    def quad_by(self, dx1: float, dy1: float, dx: float, dy: float) -> "PathBuilder":
        """`q dx1,dy1 dx,dy`."""
        self._current = (self._current[0] + dx, self._current[1] + dy)
        return self._emit("q", dx1, dy1, dx, dy)

    def smooth_quad_to(self, x: float, y: float) -> "PathBuilder":
        """`T x,y` -- a quadratic Bezier whose control point mirrors
        the previous curve's (only meaningful right after `Q`/`T`)."""
        self._current = (x, y)
        return self._emit("T", x, y)

    def smooth_quad_by(self, dx: float, dy: float) -> "PathBuilder":
        """`t dx,dy`."""
        self._current = (self._current[0] + dx, self._current[1] + dy)
        return self._emit("t", dx, dy)

    # -- elliptical arc -----------------------------------------------------

    def arc_to(
        self, rx: float, ry: float, x: float, y: float, *,
        x_axis_rotation: float = 0, large_arc: bool = False, sweep: bool = True,
    ) -> "PathBuilder":
        """`A rx,ry x-axis-rotation large-arc-flag,sweep-flag x,y`."""
        self._current = (x, y)
        return self._emit("A", rx, ry, x_axis_rotation, int(large_arc), int(sweep), x, y)

    def arc_by(
        self, rx: float, ry: float, dx: float, dy: float, *,
        x_axis_rotation: float = 0, large_arc: bool = False, sweep: bool = True,
    ) -> "PathBuilder":
        """`a rx,ry x-axis-rotation large-arc-flag,sweep-flag dx,dy`."""
        self._current = (self._current[0] + dx, self._current[1] + dy)
        return self._emit("a", rx, ry, x_axis_rotation, int(large_arc), int(sweep), dx, dy)

    # -- close --------------------------------------------------------------

    def close(self) -> "PathBuilder":
        """`Z` -- straight-line back to the current subpath's start."""
        self._current = self._start
        return self._emit("Z")

    # -- shape helpers, built from the primitives above ----------------------

    def circle(self, cx: float, cy: float, r: float) -> "PathBuilder":
        """
        Append a full circle, approximated with four cubic Bezier arcs
        (the standard `kappa`-constant technique -- visually
        indistinguishable from a true circle, and unlike SVG's native
        `A` arc command, stays a pure C-only path, which matters for
        tools that only morph between same-command-type paths, e.g.
        GSAP's `MorphSVGPlugin` -- see `nexoria.gsap`).
        """
        k = r * _KAPPA
        return (
            self.move_to(cx + r, cy)
            .cubic_to(cx + r, cy + k, cx + k, cy + r, cx, cy + r)
            .cubic_to(cx - k, cy + r, cx - r, cy + k, cx - r, cy)
            .cubic_to(cx - r, cy - k, cx - k, cy - r, cx, cy - r)
            .cubic_to(cx + k, cy - r, cx + r, cy - k, cx + r, cy)
            .close()
        )

    def rounded_rect(self, x: float, y: float, width: float, height: float, rx: float, ry: Optional[float] = None) -> "PathBuilder":
        """Append a rounded rectangle, corners drawn as quarter-circle
        arcs (`A`)."""
        ry = rx if ry is None else ry
        return (
            self.move_to(x + rx, y)
            .line_to(x + width - rx, y)
            .arc_to(rx, ry, x + width, y + ry, sweep=True)
            .line_to(x + width, y + height - ry)
            .arc_to(rx, ry, x + width - rx, y + height, sweep=True)
            .line_to(x + rx, y + height)
            .arc_to(rx, ry, x, y + height - ry, sweep=True)
            .line_to(x, y + ry)
            .arc_to(rx, ry, x + rx, y, sweep=True)
            .close()
        )

    def smooth_through(self, points: Sequence[Point], *, closed: bool = False, tension: float = 1.0) -> "PathBuilder":
        """
        Append a smooth curve running *through* every point in
        `points` -- unlike `cubic_to`/`quad_to`, which place control
        points explicitly, this derives them from the points
        themselves (a Catmull-Rom spline, converted to a sequence of
        `C` segments), the way a chart/sparkline library smooths a
        line of data. `tension` (0-1+) controls how tightly the curve
        hugs the straight-line path between points -- `0` degenerates
        to straight `L` segments, `1` (the default) is a standard
        Catmull-Rom curve. `closed=True` also curves smoothly from
        the last point back to the first.

            spark = PathBuilder().smooth_through([(0, 40), (20, 10), (40, 30), (60, 5), (80, 20)])
        """
        pts = list(points)
        if len(pts) < 2:
            raise ValueError("smooth_through() needs at least 2 points")

        self.move_to(*pts[0])
        n = len(pts)

        def _get(i: int) -> Point:
            if closed:
                return pts[i % n]
            return pts[max(0, min(n - 1, i))]

        segment_count = n if closed else n - 1
        for i in range(segment_count):
            p0, p1, p2, p3 = _get(i - 1), _get(i), _get(i + 1), _get(i + 2)
            c1 = (p1[0] + (p2[0] - p0[0]) / 6.0 * tension, p1[1] + (p2[1] - p0[1]) / 6.0 * tension)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6.0 * tension, p2[1] - (p3[1] - p1[1]) / 6.0 * tension)
            self.cubic_to(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])

        if closed:
            self.close()
        return self

    # -- output ---------------------------------------------------------

    @property
    def current_point(self) -> Point:
        """The pen's current absolute position."""
        return self._current

    @property
    def start_point(self) -> Point:
        """The current subpath's start point (where `.close()` returns to)."""
        return self._start

    def build(self) -> str:
        """The full `d` attribute value."""
        return " ".join(self._commands)

    @property
    def d(self) -> str:
        """Alias for `.build()` -- reads naturally as `path.d`."""
        return self.build()

    def __str__(self) -> str:
        return self.build()

    def __repr__(self) -> str:  # pragma: no cover
        return f"PathBuilder({self.build()!r})"

    def to_element(self, **props):
        """A real `<path d="...">` `Element`. Any extra keyword
        (`fill=`, `stroke=`, `class_=`, ...) is forwarded to `el()`
        verbatim, same convention as every other `.to_element()`
        wrapper in the framework."""
        from ...core.element import el
        return el("path", d=self.build(), **props)
