"""
nexoria.std.charts.gauge
===========================
A single-value radial gauge (`radial_gauge`) -- a ring that sweeps
from empty to `value / max_value` via an animated `stroke-dashoffset`
on a `<circle>`. Unlike the line chart's stroke-draw, a circle's
circumference is exact (`2 * pi * r`), so the target offset is
computed analytically in Python -- no `getTotalLength()` needed, just
a plain CSS transition (see `nexoria.std.charts.styles`).
"""

from __future__ import annotations
import math
from typing import Any, Dict, Optional

from ...core.element import el, Element


def radial_gauge(
    value: float,
    *,
    max_value: float = 100.0,
    min_value: float = 0.0,
    size: int = 160,
    thickness: int = 14,
    color: str = "var(--nx-primary)",
    track_color: str = "var(--nx-border)",
    label: Optional[str] = None,
    animate: bool = True,
    duration: int = 1000,
    delay: int = 0,
    class_: Optional[str] = None,
) -> Element:
    """
    `radial_gauge(72, label="72%")` -- a single-stat ring gauge, the
    radial counterpart to `nexoria.std.premium.stat_card`. `label`
    defaults to the bare `value`; pass your own (with a `%`, unit,
    etc.) or `label=""` to omit it.
    """
    frac = 0.0 if max_value <= min_value else max(0.0, min(1.0, (value - min_value) / (max_value - min_value)))
    r = size / 2 - thickness / 2 - 2
    cx = cy = size / 2
    circumference = 2 * math.pi * r
    target_offset = circumference * (1 - frac)

    common: Dict[str, Any] = {
        "cx": cx, "cy": cy, "r": r, "fill": "none",
        "style": {"stroke_width": str(thickness), "stroke_linecap": "round"},
    }
    track = el("circle", stroke=track_color, **common)

    value_style: Dict[str, Any] = {
        "stroke_width": str(thickness), "stroke_linecap": "round",
        "transform": "rotate(-90deg)", "transform_origin": "center",
    }
    value_props: Dict[str, Any] = {"cx": cx, "cy": cy, "r": r, "fill": "none", "stroke": color}
    if animate:
        value_style["stroke_dasharray"] = f"{circumference:.3f}"
        value_style["stroke_dashoffset"] = f"{circumference:.3f}"
        value_style["--nx-gauge-offset"] = f"{target_offset:.3f}"
        value_style["--nx-chart-duration"] = f"{duration}ms"
        value_style["--nx-chart-delay"] = f"{delay}ms"
        value_props["data_nx_chart_gauge"] = "true"
    else:
        value_style["stroke_dasharray"] = f"{circumference:.3f}"
        value_style["stroke_dashoffset"] = f"{target_offset:.3f}"
    value_props["style"] = value_style
    ring = el("circle", el("title", label if label is not None else _fmt(value)), **value_props)

    shown_label = _fmt(value) if label is None else label
    text = (
        el(
            "text", shown_label, x=cx, y=cy,
            style={"text_anchor": "middle", "dominant_baseline": "middle", "font_weight": "700", "font_size": f"{size * 0.16:.0f}px"},
            class_="nx-chart-axis-label",
        )
        if shown_label
        else None
    )

    kids = [track, ring] + ([text] if text is not None else [])
    svg_props: Dict[str, Any] = {
        "viewBox": f"0 0 {size} {size}", "width": "100%",
        "style": {"max_width": f"{size}px", "height": "auto", "overflow": "visible"},
    }
    if class_:
        svg_props["class_"] = class_
    return el("svg", *kids, **svg_props)


def _fmt(v: float) -> str:
    v = float(v)
    return str(int(v)) if v.is_integer() else f"{v:g}"
