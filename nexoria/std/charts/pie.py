"""
nexoria.std.charts.pie
=========================
An animated SVG pie chart (`pie_chart`) and its ring-shaped sibling
(`donut_chart`), both built as `<path>` wedges from
`nexoria.std.svg.PathBuilder.arc_to`. Each wedge pops in with a
`transform: scale()` entrance (see `nexoria.std.charts.styles`),
staggered slice by slice.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from ...core.element import el, Element
from ..svg import PathBuilder
from .palette import color_for

Number = Union[int, float]


def _polar(cx: float, cy: float, r: float, theta: float) -> Tuple[float, float]:
    """A point at angle `theta` radians clockwise from 12 o'clock,
    `r` away from `(cx, cy)`."""
    return (cx + r * math.sin(theta), cy - r * math.cos(theta))


def _normalize(data: Union[Sequence[Number], Sequence[Dict[str, Any]]], colors: Optional[Sequence[str]]) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data[0], dict):
        return [
            {"name": d.get("name"), "value": float(d.get("value", 0)), "color": d.get("color") or color_for(i, colors)}
            for i, d in enumerate(data)
        ]
    return [{"name": None, "value": float(v), "color": color_for(i, colors)} for i, v in enumerate(data)]


def _wedge_path(cx: float, cy: float, r: float, inner_r: float, theta0: float, theta1: float) -> str:
    full_circle = (theta1 - theta0) >= 2 * math.pi - 1e-9
    large_arc = (theta1 - theta0) > math.pi

    if full_circle:
        # A single 360-degree slice -- arcs to the same point are
        # degenerate, so split it into two half-sweeps instead.
        theta_mid = theta0 + math.pi
        if inner_r <= 0:
            builder = PathBuilder().move_to(*_polar(cx, cy, r, theta0))
            builder.arc_to(r, r, *_polar(cx, cy, r, theta_mid), large_arc=False, sweep=True)
            builder.arc_to(r, r, *_polar(cx, cy, r, theta0), large_arc=False, sweep=True)
            builder.close()
            return builder.build()
        builder = PathBuilder().move_to(*_polar(cx, cy, r, theta0))
        builder.arc_to(r, r, *_polar(cx, cy, r, theta_mid), large_arc=False, sweep=True)
        builder.arc_to(r, r, *_polar(cx, cy, r, theta0), large_arc=False, sweep=True)
        builder.line_to(*_polar(cx, cy, inner_r, theta0))
        builder.arc_to(inner_r, inner_r, *_polar(cx, cy, inner_r, theta_mid), large_arc=False, sweep=False)
        builder.arc_to(inner_r, inner_r, *_polar(cx, cy, inner_r, theta0), large_arc=False, sweep=False)
        builder.close()
        return builder.build()

    outer_start = _polar(cx, cy, r, theta0)
    outer_end = _polar(cx, cy, r, theta1)
    builder = PathBuilder()
    if inner_r <= 0:
        builder.move_to(cx, cy).line_to(*outer_start)
        builder.arc_to(r, r, *outer_end, large_arc=large_arc, sweep=True)
        builder.close()
        return builder.build()

    inner_start = _polar(cx, cy, inner_r, theta0)
    inner_end = _polar(cx, cy, inner_r, theta1)
    builder.move_to(*inner_start).line_to(*outer_start)
    builder.arc_to(r, r, *outer_end, large_arc=large_arc, sweep=True)
    builder.line_to(*inner_end)
    builder.arc_to(inner_r, inner_r, *inner_start, large_arc=large_arc, sweep=False)
    builder.close()
    return builder.build()


def _legend(items: Sequence[Dict[str, Any]], total: float) -> Optional[Element]:
    if not any(i["name"] for i in items):
        return None
    parts = [
        el(
            "span",
            el("span", class_="nx-chart-legend-swatch", style={"background": i["color"]}),
            f"{i['name']} ({i['value'] / total * 100:.0f}%)" if i["name"] else "",
            class_="nx-chart-legend-item",
        )
        for i in items
        if i["name"]
    ]
    return el("div", *parts, class_="nx-chart-legend")


def pie_chart(
    data: Union[Sequence[Number], Sequence[Dict[str, Any]]],
    *,
    size: int = 240,
    inner_radius: float = 0.0,
    colors: Optional[Sequence[str]] = None,
    gap_deg: float = 1.5,
    animate: bool = True,
    duration: int = 700,
    delay: int = 0,
    stagger: int = 90,
    legend: bool = True,
    center_label: Optional[str] = None,
    class_: Optional[str] = None,
) -> Element:
    """
    `pie_chart([{"name": "Chrome", "value": 64}, {"name": "Safari", "value": 19}, {"name": "Other", "value": 17}])`,
    or a plain `pie_chart([64, 19, 17])` for unnamed slices.
    `inner_radius` (`0`-`0.9`, as a fraction of the outer radius) turns
    it into a donut -- `donut_chart()` is a thin wrapper with a more
    sensible default. Each wedge gets a native `<title>` tooltip
    (name + percentage) -- zero JS, works everywhere.

    Needs `chart_styles()` and `charts_runtime()` rendered once per
    page for the pop-in animation; without them wedges render at full
    size immediately.
    """
    items = _normalize(data, colors)
    total = sum(i["value"] for i in items)
    if total <= 0:
        empty_props: Dict[str, Any] = {"width": size, "height": size}
        if class_:
            empty_props["class_"] = class_
        return el("svg", **empty_props)

    cx = cy = size / 2
    r = size / 2 - 4
    inner_r = max(0.0, min(0.92, inner_radius)) * r
    gap = math.radians(gap_deg) if len(items) > 1 else 0.0

    kids: List[Element] = []
    theta = 0.0
    for i, item in enumerate(items):
        frac = item["value"] / total
        sweep_angle = frac * 2 * math.pi
        theta0, theta1 = theta + gap / 2, theta + sweep_angle - gap / 2
        theta1 = max(theta0, theta1)
        d = _wedge_path(cx, cy, r, inner_r, theta0, theta1)
        title = f"{item['name'] + ': ' if item['name'] else ''}{frac * 100:.1f}%"
        props: Dict[str, Any] = {"d": d, "fill": item["color"]}
        if animate:
            props["data_nx_chart_wedge"] = "true"
            props["style"] = {"--nx-chart-duration": f"{duration}ms", "--nx-chart-delay": f"{delay + i * stagger}ms"}
        kids.append(el("path", el("title", title), **props))
        theta += sweep_angle

    if center_label and inner_r > 0:
        kids.append(el(
            "text", center_label, x=cx, y=cy,
            style={"text_anchor": "middle", "dominant_baseline": "middle", "font_weight": "700"},
            class_="nx-chart-axis-label",
        ))

    svg_props: Dict[str, Any] = {
        "viewBox": f"0 0 {size} {size}", "width": "100%",
        "style": {"max_width": f"{size}px", "height": "auto", "overflow": "visible"},
    }
    if class_:
        svg_props["class_"] = class_
    svg = el("svg", *kids, **svg_props)

    if legend:
        legend_el = _legend(items, total)
        if legend_el is not None:
            return el("div", svg, legend_el)
    return svg


def donut_chart(data, *, inner_radius: float = 0.62, **kwargs) -> Element:
    """`donut_chart(...)` -- `pie_chart(..., inner_radius=0.62)` by
    default. Pass `center_label="1,240"` to show a total in the
    middle of the ring."""
    return pie_chart(data, inner_radius=inner_radius, **kwargs)
