# `nexoria.std.charts`

> Animated SVG charts built entirely on `PathBuilder` and `el()` — no `<canvas>`, no chart library, no CDN.

| | |
|---|---|
| **Import** | `from nexoria.std.charts import line_chart, bar_chart, pie_chart, radial_gauge, chart_styles, charts_runtime, …` |
| **Needs** | `chart_styles()` and `charts_runtime()` once per page for entrance animations. Without them charts render fully drawn. `animate=False` opts a chart out. |
| **Alternative** | [`nexoria.chartjs`](../chartjs.md) (full Chart.js, needs a CDN) |

```python
el("div", chart_styles(), charts_runtime(),
   line_chart([12, 19, 14, 22, 30], labels=["Mon", "Tue", "Wed", "Thu", "Fri"], area=True),
   bar_chart(["Q1", "Q2", "Q3"], [{"name": "2024", "values": [12, 19, 14]}, {"name": "2025", "values": [15, 21, 18]}]),
   donut_chart([{"name": "Chrome", "value": 64}, {"name": "Safari", "value": 19}, {"name": "Other", "value": 17}], center_label="100"),
   sparkline([4, 6, 5, 8, 7, 9, 12]),
   radial_gauge(72, label="72%"))
```

| Function | Notes |
|---|---|
| `line_chart(series, labels, smooth=True, area, dots, grid, y_axis, x_axis, y_min, y_max, y_ticks, colors, …)` | Multi-series; curved via `smooth_through`. `area_chart` = `line_chart(area=True)`. |
| `bar_chart(categories, series, horizontal, grid, value_axis, …)` | Vertical/horizontal, grouped for multiple series |
| `pie_chart(data, inner_radius=0.0, gap_deg, center_label, …)` / `donut_chart` | Wedges built from `PathBuilder.arc_to`; donut defaults `inner_radius=0.62` |
| `sparkline(values, width=120, height=32, fill, …)` | Bare inline mini chart |
| `radial_gauge(value, max_value=100, min_value=0, size, thickness, color, label, …)` | Single stat ring |

`series`/`data` accept a bare list of numbers (one unnamed series/slice) or dicts: `{"name", "values", "color"?}` for series and `{"name", "value", "color"?}` for slices. Colours default to `DEFAULT_PALETTE` (`--nx-primary`, `--nx-accent`, `--nx-success`, `--nx-warning`, `--nx-danger`, `--nx-primary-hover`), cycling. Every point/bar/wedge has a native `<title>` tooltip — zero JS. Helpers: `LinearScale`, `nice_ticks`, `color_for`.

## API reference

### Classes

#### `class LinearScale(domain: Tuple[float, float], range_: Tuple[float, float]) -> None`

Maps a numeric `domain` `(min, max)` onto a pixel `range_` `(min, max)` and back. `range_` is given start-to-end in the *data* sense (e.g. `(height, 0)` for a y-axis, since SVG y grows downward but data value should grow upward).

- **`.to_px(value: float) -> float`**

### Functions

#### `chart_styles() -> Element`

A `<style>` `Element` carrying the shared chart CSS. Render it once per page, alongside `charts_runtime()`.

#### `charts_runtime() -> Element`

A `<script>` `Element` carrying the full charts animation runtime. Render it once per page, alongside `chart_styles()`.

#### `color_for(index: int, colors: Optional[Sequence[str]] = None) -> str`

The color for series/slice/bar `index`, cycling through `colors` (or `DEFAULT_PALETTE` when `colors` is `None`/empty).

#### `nice_ticks(min_v: float, max_v: float, count: int = 5) -> List[float]`

A list of evenly-spaced, human-friendly tick values spanning (at least) `[min_v, max_v]` -- e.g. `nice_ticks(0, 87, 5)` -> `[0, 20, 40, 60, 80, 100]`. Always includes both a tick at or below `min_v` and one at or above `max_v`.

#### `line_chart(series: Union[Sequence[Number], Sequence[Dict[str, Any]]], *, labels: Optional[Sequence[str]] = None, width: int = 640, height: int = 320, smooth: bool = True, area: bool = False, area_opacity: float = 0.16, dots: bool = True, grid: bool = True, y_axis: bool = True, x_axis: bool = True, y_min: Optional[float] = None, y_max: Optional[float] = None, y_ticks: int = 5, colors: Optional[Sequence[str]] = None, stroke_width: int = 3, animate: bool = True, duration: int = 1200, delay: int = 0, stagger: int = 150, legend: bool = True, class_: Optional[str] = None) -> Element`

`line_chart([12, 19, 14, 22, 30, 26], labels=["Mon", ..., "Sat"])` for a single series, or `line_chart([{"name": "2024", "values": [...]}, {"name": "2025", "values": [...]}])` for several. `smooth=True` fits a Catmull-Rom curve through each series (`PathBuilder.smooth_through`); `area=True` also fills under each line. Each value gets a native `<title>` tooltip (series name + value) -- zero JS, works everywhere.

Needs `chart_styles()` and `charts_runtime()` (from `nexoria.std.charts`) rendered once per page for the entrance animation; without them the chart still renders fully drawn.

#### `area_chart(series, **kwargs) -> Element`

`area_chart(...)` -- `line_chart(..., area=True)`. Accepts the exact same arguments as `line_chart`.

#### `sparkline(values: Sequence[Number], *, width: int = 120, height: int = 32, color: str = 'var(--nx-primary)', stroke_width: int = 2, fill: bool = False, smooth: bool = True, animate: bool = True, duration: int = 900) -> Element`

`sparkline([4, 6, 5, 8, 7, 9, 12])`. A bare inline mini line chart with no axes/grid/legend/tooltips -- for a stat card or a table cell. Drop it next to `nexoria.std.premium.stat_card` for a trend indicator.

#### `bar_chart(categories: Sequence[str], series: Union[Sequence[Number], Sequence[Dict[str, Any]]], *, width: int = 640, height: int = 320, horizontal: bool = False, grid: bool = True, value_axis: bool = True, value_min: Optional[float] = None, value_max: Optional[float] = None, value_ticks: int = 5, colors: Optional[Sequence[str]] = None, bar_gap: float = 0.28, group_gap: float = 0.15, corner_radius: int = 4, animate: bool = True, duration: int = 900, delay: int = 0, stagger: int = 60, legend: bool = True, class_: Optional[str] = None) -> Element`

`bar_chart(["Mon", "Tue", "Wed"], [10, 14, 9])` for a single series, or `bar_chart(["Q1", "Q2"], [{"name": "2024", "values": [10, 14]}, {"name": "2025", "values": [13, 18]}])` for grouped bars (one cluster of bars per category, one bar per series, side by side). `horizontal=True` lays categories down the y-axis instead, useful for long category names or ranking lists. Each bar gets a native `<title>` tooltip (category + series + value) -- zero JS, works everywhere.

Needs `chart_styles()` and `charts_runtime()` rendered once per page for the grow-in animation; without them bars render at full size immediately.

#### `pie_chart(data: Union[Sequence[Number], Sequence[Dict[str, Any]]], *, size: int = 240, inner_radius: float = 0.0, colors: Optional[Sequence[str]] = None, gap_deg: float = 1.5, animate: bool = True, duration: int = 700, delay: int = 0, stagger: int = 90, legend: bool = True, center_label: Optional[str] = None, class_: Optional[str] = None) -> Element`

`pie_chart([{"name": "Chrome", "value": 64}, {"name": "Safari", "value": 19}, {"name": "Other", "value": 17}])`, or a plain `pie_chart([64, 19, 17])` for unnamed slices. `inner_radius` (`0`-`0.9`, as a fraction of the outer radius) turns it into a donut -- `donut_chart()` is a thin wrapper with a more sensible default. Each wedge gets a native `<title>` tooltip (name + percentage) -- zero JS, works everywhere.

Needs `chart_styles()` and `charts_runtime()` rendered once per page for the pop-in animation; without them wedges render at full size immediately.

#### `donut_chart(data, *, inner_radius: float = 0.62, **kwargs) -> Element`

`donut_chart(...)` -- `pie_chart(..., inner_radius=0.62)` by default. Pass `center_label="1,240"` to show a total in the middle of the ring.

#### `radial_gauge(value: float, *, max_value: float = 100.0, min_value: float = 0.0, size: int = 160, thickness: int = 14, color: str = 'var(--nx-primary)', track_color: str = 'var(--nx-border)', label: Optional[str] = None, animate: bool = True, duration: int = 1000, delay: int = 0, class_: Optional[str] = None) -> Element`

`radial_gauge(72, label="72%")` -- a single-stat ring gauge, the radial counterpart to `nexoria.std.premium.stat_card`. `label` defaults to the bare `value`; pass your own (with a `%`, unit, etc.) or `label=""` to omit it.

### Constants

| Name | Value |
|---|---|
| `CHART_STYLES_CSS` | `'[data-nx-chart-bar] {\n  transition-property: transform;\n  transition-duration: var(--nx-chart-duration, 900ms);\n  transition-delay: var(--nx-chart-delay, 0ms);\n  transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1);\n  transform-box: fill-box;\n}\n[data-nx-chart-bar="v"] { transform: scaleY(0); transform-origin: 50% 100%; }\n[data-nx-chart-bar="v"].nx-charted { transform: scaleY(1); }\n[data-nx-chart-bar…` |
| `CHARTS_RUNTIME_JS` | `'(function () {\n  if (window.__nxCharts) return;\n  window.__nxCharts = true;\n\n  function onReady(fn) {\n    if (document.readyState === "loading") {\n      document.addEventListener("DOMContentLoaded", fn);\n    } else {\n      fn();\n    }\n  }\n\n  // -- generic "flip .nx-charted on once visible" observer -------------\n  function watchClassFlip(selector, threshold) {\n    var els = document.querySelectorAll…` |
| `DEFAULT_PALETTE` | `['var(--nx-primary)', 'var(--nx-accent)', 'var(--nx-success)', 'var(--nx-warning)', 'var(--nx-danger)', 'var(--nx-primary-hover)']` |
