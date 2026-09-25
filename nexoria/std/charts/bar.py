"""
nexoria.std.charts.bar
=========================
An animated SVG bar chart: single-series or grouped multi-series,
vertical or horizontal. Bars grow in from the baseline via a CSS
`transform: scale*()` transition (see `nexoria.std.charts.styles`) --
no JS math needed, unlike the line chart's stroke-draw, since a
rectangle's target size is known up front.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Union

from ...core.element import el, Element
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


def bar_chart(
    categories: Sequence[str],
    series: Union[Sequence[Number], Sequence[Dict[str, Any]]],
    *,
    width: int = 640,
    height: int = 320,
    horizontal: bool = False,
    grid: bool = True,
    value_axis: bool = True,
    value_min: Optional[float] = None,
    value_max: Optional[float] = None,
    value_ticks: int = 5,
    colors: Optional[Sequence[str]] = None,
    bar_gap: float = 0.28,
    group_gap: float = 0.15,
    corner_radius: int = 4,
    animate: bool = True,
    duration: int = 900,
    delay: int = 0,
    stagger: int = 60,
    legend: bool = True,
    class_: Optional[str] = None,
) -> Element:
    """
    `bar_chart(["Mon", "Tue", "Wed"], [10, 14, 9])` for a single
    series, or
    `bar_chart(["Q1", "Q2"], [{"name": "2024", "values": [10, 14]}, {"name": "2025", "values": [13, 18]}])`
    for grouped bars (one cluster of bars per category, one bar per
    series, side by side). `horizontal=True` lays categories down the
    y-axis instead, useful for long category names or ranking lists.
    Each bar gets a native `<title>` tooltip (category + series +
    value) -- zero JS, works everywhere.

    Needs `chart_styles()` and `charts_runtime()` rendered once per
    page for the grow-in animation; without them bars render at full
    size immediately.
    """
    specs = normalize_series(series, colors)
    n_cat = len(categories)
    if n_cat == 0 or not specs:
        empty_props: Dict[str, Any] = {"width": width, "height": height}
        if class_:
            empty_props["class_"] = class_
        return el("svg", **empty_props)
    n_series = len(specs)
    lo, hi = value_bounds(specs)
    lo = min(lo, 0)  # bars always grow from a zero baseline
    if value_min is not None:
        lo = value_min
    if value_max is not None:
        hi = value_max
    ticks = nice_ticks(lo, hi, value_ticks) if (grid or value_axis) else [lo, hi]
    domain_lo, domain_hi = min(ticks[0], lo), max(ticks[-1], hi)

    label_gutter = 60 if horizontal else 28
    value_gutter = 44 if value_axis else 12
    pad_top, pad_right = 14, 16

    kids: List[Element] = []

    if horizontal:
        pad_left = label_gutter
        plot_w = max(1, width - pad_left - pad_right)
        plot_h = max(1, height - pad_top - value_gutter)
        value_scale = LinearScale((domain_lo, domain_hi), (pad_left, pad_left + plot_w))
        cat_band = plot_h / n_cat
        baseline_x = value_scale.to_px(0)

        if grid:
            for t in ticks:
                gx = value_scale.to_px(t)
                kids.append(el("line", x1=gx, y1=pad_top, x2=gx, y2=pad_top + plot_h, class_="nx-chart-grid-line"))
        if value_axis:
            for t in ticks:
                gx = value_scale.to_px(t)
                kids.append(el("text", _fmt_tick(t), x=gx, y=pad_top + plot_h + 16, style={"text_anchor": "middle"}, class_="nx-chart-axis-label"))

        bar_thickness = (cat_band * (1 - bar_gap)) / n_series
        for c_i, cat in enumerate(categories):
            cy0 = pad_top + c_i * cat_band + (cat_band * bar_gap) / 2
            kids.append(el("text", str(cat), x=pad_left - 8, y=cy0 + (cat_band * (1 - bar_gap)) / 2, style={"text_anchor": "end", "dominant_baseline": "middle"}, class_="nx-chart-axis-label"))
            for s_i, spec in enumerate(specs):
                if c_i >= len(spec.values):
                    continue
                v = spec.values[c_i]
                y = cy0 + s_i * bar_thickness
                x_end = value_scale.to_px(v)
                x0, x1 = (baseline_x, x_end) if x_end >= baseline_x else (x_end, baseline_x)
                rect_width = max(0.5, x1 - x0)
                title = f"{cat}{' — ' + spec.name if spec.name else ''}: {_fmt_tick(v)}"
                props: Dict[str, Any] = {
                    "x": x0, "y": y, "width": rect_width, "height": max(0.5, bar_thickness * (1 - group_gap)),
                    "rx": corner_radius, "fill": spec.color,
                }
                if animate:
                    props["data_nx_chart_bar"] = "h"
                    props["style"] = {"--nx-chart-duration": f"{duration}ms", "--nx-chart-delay": f"{delay + (c_i * n_series + s_i) * stagger}ms"}
                kids.append(el("rect", el("title", title), **props))
    else:
        pad_left = value_gutter
        plot_w = max(1, width - pad_left - pad_right)
        plot_h = max(1, height - pad_top - label_gutter)
        value_scale = LinearScale((domain_lo, domain_hi), (pad_top + plot_h, pad_top))
        cat_band = plot_w / n_cat
        baseline_y = value_scale.to_px(0)

        if grid:
            for t in ticks:
                gy = value_scale.to_px(t)
                kids.append(el("line", x1=pad_left, y1=gy, x2=pad_left + plot_w, y2=gy, class_="nx-chart-grid-line"))
        if value_axis:
            for t in ticks:
                gy = value_scale.to_px(t)
                kids.append(el("text", _fmt_tick(t), x=pad_left - 8, y=gy, style={"text_anchor": "end", "dominant_baseline": "middle"}, class_="nx-chart-axis-label"))

        bar_width = (cat_band * (1 - bar_gap)) / n_series
        for c_i, cat in enumerate(categories):
            cx0 = pad_left + c_i * cat_band + (cat_band * bar_gap) / 2
            kids.append(el("text", str(cat), x=cx0 + (cat_band * (1 - bar_gap)) / 2, y=pad_top + plot_h + 18, style={"text_anchor": "middle"}, class_="nx-chart-axis-label"))
            for s_i, spec in enumerate(specs):
                if c_i >= len(spec.values):
                    continue
                v = spec.values[c_i]
                x = cx0 + s_i * bar_width
                y_end = value_scale.to_px(v)
                y0, y1 = (y_end, baseline_y) if y_end <= baseline_y else (baseline_y, y_end)
                rect_height = max(0.5, y1 - y0)
                title = f"{cat}{' — ' + spec.name if spec.name else ''}: {_fmt_tick(v)}"
                props: Dict[str, Any] = {
                    "x": x, "y": y0, "width": max(0.5, bar_width * (1 - group_gap)), "height": rect_height,
                    "rx": corner_radius, "fill": spec.color,
                }
                if animate:
                    props["data_nx_chart_bar"] = "v"
                    props["style"] = {"--nx-chart-duration": f"{duration}ms", "--nx-chart-delay": f"{delay + (c_i * n_series + s_i) * stagger}ms"}
                kids.append(el("rect", el("title", title), **props))

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


def _fmt_tick(v: Number) -> str:
    v = float(v)
    return str(int(v)) if v.is_integer() else f"{v:g}"
