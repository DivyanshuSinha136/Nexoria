"""
nexoria.std.charts.line
==========================
An animated SVG line chart (`line_chart`), its filled-area sibling
(`area_chart`), and a bare-bones inline `sparkline` -- all built from
plain `<svg>`/`<path>` `Element`s and `nexoria.std.svg.PathBuilder`
(no chart-drawing dependency, no canvas, no CDN). The line itself
"draws in" via an animated `stroke-dashoffset` (see
`nexoria.std.charts.runtime`), the same technique as
`nexoria.std.animation.svg.draw_svg`.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Union

from ...core.element import el, Element
from ..svg import PathBuilder
from .palette import color_for
from .scale import LinearScale, nice_ticks
from .series import Number, SeriesSpec, max_len, normalize_series, value_bounds


def _legend(specs: Sequence[SeriesSpec]) -> Optional[Element]:
    named = [s for s in specs if s.name]
    if not named:
        return None
    items = [
        el(
            "span",
            el("span", class_="nx-chart-legend-swatch", style={"background": s.color}),
            s.name,
            class_="nx-chart-legend-item",
        )
        for s in named
    ]
    return el("div", *items, class_="nx-chart-legend")


def line_chart(
    series: Union[Sequence[Number], Sequence[Dict[str, Any]]],
    *,
    labels: Optional[Sequence[str]] = None,
    width: int = 640,
    height: int = 320,
    smooth: bool = True,
    area: bool = False,
    area_opacity: float = 0.16,
    dots: bool = True,
    grid: bool = True,
    y_axis: bool = True,
    x_axis: bool = True,
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
    y_ticks: int = 5,
    colors: Optional[Sequence[str]] = None,
    stroke_width: int = 3,
    animate: bool = True,
    duration: int = 1200,
    delay: int = 0,
    stagger: int = 150,
    legend: bool = True,
    class_: Optional[str] = None,
) -> Element:
    """
    `line_chart([12, 19, 14, 22, 30, 26], labels=["Mon", ..., "Sat"])`
    for a single series, or
    `line_chart([{"name": "2024", "values": [...]}, {"name": "2025", "values": [...]}])`
    for several. `smooth=True` fits a Catmull-Rom curve through each
    series (`PathBuilder.smooth_through`); `area=True` also fills
    under each line. Each value gets a native `<title>` tooltip
    (series name + value) -- zero JS, works everywhere.

    Needs `chart_styles()` and `charts_runtime()` (from
    `nexoria.std.charts`) rendered once per page for the entrance
    animation; without them the chart still renders fully drawn.
    """
    specs = normalize_series(series, colors)
    n = max_len(specs)
    if n == 0:
        empty_props: Dict[str, Any] = {"width": width, "height": height}
        if class_:
            empty_props["class_"] = class_
        return el("svg", **empty_props)
    lo, hi = value_bounds(specs)
    if y_min is not None:
        lo = y_min
    if y_max is not None:
        hi = y_max
    ticks = nice_ticks(lo, hi, y_ticks) if (grid or y_axis) else [lo, hi]
    domain_lo, domain_hi = min(ticks[0], lo), max(ticks[-1], hi)

    pad_left = 44 if y_axis else 12
    pad_bottom = 28 if x_axis else 12
    pad_top = 14
    pad_right = 16
    plot_w = max(1, width - pad_left - pad_right)
    plot_h = max(1, height - pad_top - pad_bottom)

    x_scale = LinearScale((0, max(1, n - 1)), (pad_left, pad_left + plot_w))
    y_scale = LinearScale((domain_lo, domain_hi), (pad_top + plot_h, pad_top))

    kids: List[Element] = []

    if grid:
        for t in ticks:
            gy = y_scale.to_px(t)
            kids.append(el("line", x1=pad_left, y1=gy, x2=pad_left + plot_w, y2=gy, class_="nx-chart-grid-line"))

    if y_axis:
        for t in ticks:
            gy = y_scale.to_px(t)
            kids.append(el(
                "text", _fmt_tick(t), x=pad_left - 8, y=gy,
                style={"text_anchor": "end", "dominant_baseline": "middle"},
                class_="nx-chart-axis-label",
            ))

    if x_axis and labels:
        step = max(1, (n - 1) // 6) if n > 7 else 1  # thin out labels on wide series
        for i in range(0, n, step):
            if i >= len(labels):
                break
            lx = x_scale.to_px(i)
            kids.append(el(
                "text", str(labels[i]), x=lx, y=pad_top + plot_h + 18,
                style={"text_anchor": "middle"}, class_="nx-chart-axis-label",
            ))

    baseline_y = y_scale.to_px(max(domain_lo, 0) if domain_lo <= 0 <= domain_hi else domain_lo)

    for s_i, spec in enumerate(specs):
        points = [(x_scale.to_px(i), y_scale.to_px(v)) for i, v in enumerate(spec.values)]
        if len(points) < 2:
            continue
        builder = PathBuilder()
        if smooth:
            builder.smooth_through(points)
        else:
            builder.move_to(*points[0])
            for p in points[1:]:
                builder.line_to(*p)
        line_delay = delay + s_i * stagger

        if area:
            area_builder = PathBuilder()
            if smooth:
                area_builder.smooth_through(points)
            else:
                area_builder.move_to(*points[0])
                for p in points[1:]:
                    area_builder.line_to(*p)
            area_builder.line_to(points[-1][0], baseline_y).line_to(points[0][0], baseline_y).close()
            area_props: Dict[str, Any] = {"fill": spec.color, "style": {"fill_opacity": str(area_opacity)}}
            if animate:
                area_props["data_nx_chart_area"] = "true"
                area_props["style"] = {
                    "fill_opacity": str(area_opacity),
                    "--nx-chart-duration": f"{duration}ms",
                    "--nx-chart-delay": f"{line_delay}ms",
                }
            kids.append(area_builder.to_element(**area_props))

        line_props: Dict[str, Any] = {
            "fill": "none", "stroke": spec.color,
            "style": {"stroke_width": str(stroke_width), "stroke_linecap": "round", "stroke_linejoin": "round"},
        }
        if animate:
            line_props["data_nx_chart_line"] = "true"
            line_props["data_nx_chart_duration"] = str(duration)
            line_props["data_nx_chart_delay"] = str(line_delay)
        kids.append(builder.to_element(**line_props))

        if dots:
            for i, (px, py) in enumerate(points):
                title = f"{spec.name + ': ' if spec.name else ''}{_fmt_tick(spec.values[i])}"
                dot_props: Dict[str, Any] = {"r": 3.5, "fill": spec.color, "stroke": "var(--nx-bg)", "style": {"stroke_width": "2"}}
                if animate:
                    dot_props["data_nx_chart_dot"] = "true"
                    dot_props["style"] = {
                        "stroke_width": "2",
                        "--nx-chart-duration": "400ms",
                        "--nx-chart-delay": f"{line_delay + i * (stagger // 4 or 20)}ms",
                    }
                kids.append(el("circle", el("title", title), cx=px, cy=py, **dot_props))

    svg_props: Dict[str, Any] = {
        "viewBox": f"0 0 {width} {height}", "width": "100%",
        "style": {"max_width": f"{width}px", "height": "auto", "overflow": "visible"},
    }
    if class_:
        svg_props["class_"] = class_
    svg = el("svg", *kids, **svg_props)

    if legend:
        legend_el = _legend(specs)
        if legend_el is not None:
            return el("div", svg, legend_el)
    return svg


def area_chart(series, **kwargs) -> Element:
    """`area_chart(...)` -- `line_chart(..., area=True)`. Accepts the
    exact same arguments as `line_chart`."""
    kwargs.setdefault("area", True)
    return line_chart(series, **kwargs)


def sparkline(
    values: Sequence[Number],
    *,
    width: int = 120,
    height: int = 32,
    color: str = "var(--nx-primary)",
    stroke_width: int = 2,
    fill: bool = False,
    smooth: bool = True,
    animate: bool = True,
    duration: int = 900,
) -> Element:
    """
    `sparkline([4, 6, 5, 8, 7, 9, 12])`. A bare inline mini line chart
    with no axes/grid/legend/tooltips -- for a stat card or a table
    cell. Drop it next to `nexoria.std.premium.stat_card` for a
    trend indicator.
    """
    n = len(values)
    if n < 2:
        return el("svg", width=width, height=height)
    lo, hi = min(values), max(values)
    pad = 2
    x_scale = LinearScale((0, n - 1), (pad, width - pad))
    y_scale = LinearScale((lo, hi), (height - pad, pad))
    points = [(x_scale.to_px(i), y_scale.to_px(v)) for i, v in enumerate(values)]

    builder = PathBuilder()
    if smooth:
        builder.smooth_through(points)
    else:
        builder.move_to(*points[0])
        for p in points[1:]:
            builder.line_to(*p)

    kids: List[Element] = []
    if fill:
        area_builder = PathBuilder()
        if smooth:
            area_builder.smooth_through(points)
        else:
            area_builder.move_to(*points[0])
            for p in points[1:]:
                area_builder.line_to(*p)
        area_builder.line_to(points[-1][0], height - pad).line_to(points[0][0], height - pad).close()
        kids.append(area_builder.to_element(fill=color, style={"fill_opacity": "0.15"}))

    line_props: Dict[str, Any] = {
        "fill": "none", "stroke": color,
        "style": {"stroke_width": str(stroke_width), "stroke_linecap": "round", "stroke_linejoin": "round"},
    }
    if animate:
        line_props["data_nx_chart_line"] = "true"
        line_props["data_nx_chart_duration"] = str(duration)
    kids.append(builder.to_element(**line_props))

    return el("svg", *kids, viewBox=f"0 0 {width} {height}", width=width, height=height, style={"overflow": "visible"})


def _fmt_tick(v: Number) -> str:
    v = float(v)
    return str(int(v)) if v.is_integer() else f"{v:g}"
