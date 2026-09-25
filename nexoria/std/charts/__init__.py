"""
nexoria.std.charts
=====================
An animated, SVG-based chart library for `nexoria.std` -- line, area,
bar, pie/donut, sparkline and single-value radial gauge, built
entirely from `Element`/`nexoria.std.svg.PathBuilder`. No chart
library dependency, no `<canvas>`, no CDN asset, no `App(...)` flag --
same "plain import" contract as the rest of `nexoria.std` (contrast
`nexoria.chartjs`, which needs `App(chartjs=True)` and a CDN-loaded
Chart.js bundle).

    from nexoria.std.charts import (
        chart_styles, charts_runtime,
        line_chart, area_chart, sparkline,
        bar_chart,
        pie_chart, donut_chart,
        radial_gauge,
    )

Render `chart_styles()` and `charts_runtime()` once anywhere in your
root layout to enable the entrance animations (bars growing up,
lines drawing in, wedges popping in, gauges sweeping to value) --
every chart function still renders fully, fully-drawn, without them
(`animate=False` opts a single chart out explicitly).

Series input is flexible everywhere a chart takes one: a bare list of
numbers for a single unnamed series (`[10, 20, 15]`), or a list of
`{"name": ..., "values": [...], "color": ...}` dicts for one or more
named series (`color` optional -- falls back to the shared
`DEFAULT_PALETTE` by position, same tokens `--nx-primary`/
`--nx-accent`/... the rest of the framework uses, so charts re-color
with `App(theme=...)` automatically). Every data point/bar/wedge gets
a native `<title>` tooltip -- no JS, works everywhere.

    line_chart([12, 19, 14, 22, 30, 26], labels=["Mon", ..., "Sat"])
    bar_chart(["Q1", "Q2", "Q3"], [
        {"name": "2024", "values": [12, 19, 14]},
        {"name": "2025", "values": [15, 22, 18]},
    ])
    pie_chart([{"name": "Chrome", "value": 64}, {"name": "Safari", "value": 19}, {"name": "Other", "value": 17}])
    donut_chart([64, 19, 17], center_label="100%")
    radial_gauge(72, label="72%")
    sparkline([4, 6, 5, 8, 7, 9, 12])
"""

from __future__ import annotations

from .styles import CHART_STYLES_CSS, chart_styles
from .runtime import CHARTS_RUNTIME_JS, charts_runtime
from .palette import DEFAULT_PALETTE, color_for
from .scale import LinearScale, nice_ticks
from .line import line_chart, area_chart, sparkline
from .bar import bar_chart
from .pie import pie_chart, donut_chart
from .gauge import radial_gauge

__all__ = [
    "CHART_STYLES_CSS", "chart_styles",
    "CHARTS_RUNTIME_JS", "charts_runtime",
    "DEFAULT_PALETTE", "color_for",
    "LinearScale", "nice_ticks",
    "line_chart", "area_chart", "sparkline",
    "bar_chart",
    "pie_chart", "donut_chart",
    "radial_gauge",
]
