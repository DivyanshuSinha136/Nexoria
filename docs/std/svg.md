# `nexoria.std.svg`

> A fluent builder for SVG `<path d="…">` data plus thin `<svg>`/`<path>` wrappers. It is the foundation of [`std.charts`](charts.md).

| | |
|---|---|
| **Import** | `from nexoria.std.svg import PathBuilder, svg_canvas, svg_path` |

```python
from nexoria.std.svg import PathBuilder, svg_canvas

heart = (PathBuilder().move_to(12, 21)
         .cubic_to(3, 13, 3, 8, 7.5, 5.5).cubic_to(10, 4, 12, 6, 12, 6)
         .cubic_to(12, 6, 14, 4, 16.5, 5.5).cubic_to(21, 8, 21, 13, 12, 21).close())
svg_canvas(heart.to_element(fill="var(--nx-danger)"), view_box="0 0 24 24", width=32, height=32)
```

## `PathBuilder`

Every method returns `self`; the pen position is tracked (`.current_point`, `.start_point`).

| Group | Methods (absolute / relative) |
|---|---|
| Move / line | `move_to`/`move_by`, `line_to`/`line_by`, `horizontal_to`/`horizontal_by`, `vertical_to`/`vertical_by` |
| Cubic Bézier | `cubic_to`/`cubic_by`, `smooth_cubic_to`/`smooth_cubic_by` (`S`/`s`) |
| Quadratic Bézier | `quad_to`/`quad_by`, `smooth_quad_to`/`smooth_quad_by` (`T`/`t`) |
| Arc | `arc_to`/`arc_by` (`rx, ry, …, x_axis_rotation=0, large_arc=False, sweep=True`) |
| Close | `close()` |
| Shapes | `circle(cx, cy, r)` (four cubic arcs — stays pure `C`, which matters for tools that morph between same-command paths such as GSAP's MorphSVG), `rounded_rect(x, y, w, h, rx, ry=None)`, `smooth_through(points, closed=False, tension=1.0)` (Catmull-Rom through points, as used for chart lines) |
| Output | `build()`, `.d`, `str(builder)` → the `d` string; `to_element(**props)` → a `<path>` `Element` (props forwarded to `el()`) |

Because `PathBuilder` has `.to_element()`, a bare builder can be passed as a child to `el(...)`. `svg_canvas(*children, view_box="0 0 100 100", width, height, class_)` fills in `xmlns`/`viewBox`; `svg_path(builder_or_d, **props)` accepts a builder or a string.

## API reference

### Classes

#### `class PathBuilder() -> None`

Build an SVG path's `d` attribute one command at a time. Tracks the current point (and each subpath's start point, for `.close()`) so `.current_point` / `.start_point` are always available -- handy for chaining shapes relative to where the pen left off.

- **`.arc_by(rx: float, ry: float, dx: float, dy: float, *, x_axis_rotation: float = 0, large_arc: bool = False, sweep: bool = True) -> 'PathBuilder'`** — `a rx,ry x-axis-rotation large-arc-flag,sweep-flag dx,dy`.
- **`.arc_to(rx: float, ry: float, x: float, y: float, *, x_axis_rotation: float = 0, large_arc: bool = False, sweep: bool = True) -> 'PathBuilder'`** — `A rx,ry x-axis-rotation large-arc-flag,sweep-flag x,y`.
- **`.build() -> str`** — The full `d` attribute value.
- **`.circle(cx: float, cy: float, r: float) -> 'PathBuilder'`** — Append a full circle, approximated with four cubic Bezier arcs (the standard `kappa`-constant technique -- visually indistinguishable from a true circle, and unlike SVG's native `A` arc command, stays a pure C-only path, which matters for tools that only morph between same-command-type paths, e.g. G…
- **`.close() -> 'PathBuilder'`** — `Z` -- straight-line back to the current subpath's start.
- **`.cubic_by(dx1: float, dy1: float, dx2: float, dy2: float, dx: float, dy: float) -> 'PathBuilder'`** — `c dx1,dy1 dx2,dy2 dx,dy` -- relative cubic Bezier.
- **`.cubic_to(x1: float, y1: float, x2: float, y2: float, x: float, y: float) -> 'PathBuilder'`** — `C x1,y1 x2,y2 x,y` -- a cubic Bezier with two explicit control points, ending at an absolute `(x, y)`.
- **`.horizontal_by(dx: float) -> 'PathBuilder'`** — `h dx`.
- **`.horizontal_to(x: float) -> 'PathBuilder'`** — `H x` -- a horizontal line to an absolute x, same y.
- **`.line_by(dx: float, dy: float) -> 'PathBuilder'`** — `l dx,dy`.
- **`.line_to(x: float, y: float) -> 'PathBuilder'`** — `L x,y`.
- **`.move_by(dx: float, dy: float) -> 'PathBuilder'`** — `m dx,dy` -- start a new subpath, relative to the current point.
- **`.move_to(x: float, y: float) -> 'PathBuilder'`** — `M x,y` -- start a new subpath at an absolute point.
- **`.quad_by(dx1: float, dy1: float, dx: float, dy: float) -> 'PathBuilder'`** — `q dx1,dy1 dx,dy`.
- **`.quad_to(x1: float, y1: float, x: float, y: float) -> 'PathBuilder'`** — `Q x1,y1 x,y` -- a quadratic Bezier with one control point.
- **`.rounded_rect(x: float, y: float, width: float, height: float, rx: float, ry: Optional[float] = None) -> 'PathBuilder'`** — Append a rounded rectangle, corners drawn as quarter-circle arcs (`A`).
- **`.smooth_cubic_by(dx2: float, dy2: float, dx: float, dy: float) -> 'PathBuilder'`** — `s dx2,dy2 dx,dy`.
- **`.smooth_cubic_to(x2: float, y2: float, x: float, y: float) -> 'PathBuilder'`** — `S x2,y2 x,y` -- a cubic Bezier whose first control point mirrors the previous curve's second control point (only meaningful right after another `C`/`S`).
- **`.smooth_quad_by(dx: float, dy: float) -> 'PathBuilder'`** — `t dx,dy`.
- **`.smooth_quad_to(x: float, y: float) -> 'PathBuilder'`** — `T x,y` -- a quadratic Bezier whose control point mirrors the previous curve's (only meaningful right after `Q`/`T`).
- **`.smooth_through(points: Sequence[Point], *, closed: bool = False, tension: float = 1.0) -> 'PathBuilder'`** — Append a smooth curve running *through* every point in `points` -- unlike `cubic_to`/`quad_to`, which place control points explicitly, this derives them from the points themselves (a Catmull-Rom spline, converted to a sequence of `C` segments), the way a chart/sparkline library smooths a line of dat…
- **`.to_element(**props)`** — A real `<path d="...">` `Element`. Any extra keyword (`fill=`, `stroke=`, `class_=`, ...) is forwarded to `el()` verbatim, same convention as every other `.to_element()` wrapper in the framework.
- **`.vertical_by(dy: float) -> 'PathBuilder'`** — `v dy`.
- **`.vertical_to(y: float) -> 'PathBuilder'`** — `V y` -- a vertical line to an absolute y, same x.

### Functions

#### `svg_canvas(*children: Any, view_box: str = '0 0 100 100', width: Optional[Union[str, int]] = None, height: Optional[Union[str, int]] = None, class_: Optional[str] = None) -> Element`

`svg_canvas(PathBuilder().circle(50, 50, 40).to_element(fill="var(--nx-primary)"), view_box="0 0 100 100")`. A bare `<svg>` with `xmlns`/`viewBox` filled in so you don't have to repeat them at every call site.

#### `svg_path(path: Union[PathBuilder, str], **props: Any) -> Element`

`svg_path(PathBuilder().move_to(0, 0).line_to(10, 10), stroke="black", fill="none")` or `svg_path("M0,0 L10,10", stroke="black")`. Accepts either a `PathBuilder` (its `.build()` is used) or an already-built `d` string -- a thin convenience over `el("path", d=..., **props)` for the string case; `PathBuilder.to_element()` does the same thing when you already have a builder in hand.
