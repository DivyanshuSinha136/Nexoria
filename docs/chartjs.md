# `nexoria.chartjs`

> Declare a Chart.js chart in Python; the adapter renders it onto a `<canvas>`.

| | |
|---|---|
| **Import** | `from nexoria.chartjs import Chart, Dataset` |
| **Enabled by** | `App(chartjs=True)` |
| **Library** | Chart.js 4.5.1 and `@kurkle/color` 0.4.0 (its color dependency) from unpkg, via the shared import map |
| **Adapter** | `runtime/chartjs-adapter.js`; exposes `window.__nexoria__.chartjs.charts` |

```python
from nexoria import App, Component, el, Router
from nexoria.chartjs import Chart, Dataset

class Report(Component):
    def render(self):
        chart = Chart(
            type="bar",
            labels=["Jan", "Feb", "Mar"],
            datasets=[Dataset("Revenue", [12, 19, 14], backgroundColor="#6366f1")],
            options={"responsive": True},
        )
        return el("div", el("h1", "Report"), chart.to_element())

app = App(name="Report", router=Router().add("/", Report), chartjs=True)
```

- `Chart(type, labels, datasets, options={}, width="100%", height="320px")` — `type` is any Chart.js type (`bar`, `line`, `pie`, `doughnut`, `radar`, `polarArea`, `bubble`, `scatter`, …).
- `Dataset(label, data, **extra)` — extra keyword args are Chart.js dataset options (`backgroundColor`, `borderColor`, `tension`, `fill`, …), included verbatim.
- `options` is Chart.js's own options object, passed through untouched.
- Renders `<canvas class="nx-chartjs-canvas" data-nx-chart='{…}'>`.

Prefer zero-dependency SVG charts? See [`std.charts`](std/charts.md).

## API reference

### Classes

#### `class Chart(type: str, labels: list[Any], datasets: list[Dataset], options: dict[str, Any] = ..., width: str = '100%', height: str = '320px') -> None`

A Chart.js chart. `type` is any Chart.js chart type ("bar", "line", "pie", "doughnut", "radar", "polarArea", "bubble", "scatter", ...). `options` is Chart.js's own options object, passed through verbatim (scales, plugins, responsive, etc.) -- Nexoria doesn't reshape it.

- **`.to_dict() -> dict`**
- **`.to_element()`**

#### `class Dataset(label: str, data: list[Any], **extra: Any)`

One Chart.js dataset. `label` and `data` are the common case; any other Chart.js dataset option (`backgroundColor`, `borderColor`, `tension`, `fill`, ...) can be passed as extra keyword args and is included verbatim.

- **`.to_dict() -> dict`**

### Constants

| Name | Value |
|---|---|
| `CHARTJS_CDN` | `'https://unpkg.com/chart.js@4.5.1/dist/chart.js'` |
| `CHARTJS_IMPORTS` | `{'chart.js': 'https://unpkg.com/chart.js@4.5.1/dist/chart.js', '@kurkle/color': 'https://unpkg.com/@kurkle/color@0.4.0/dist/color.esm.js'}` |
| `CHARTJS_ADAPTER_TAG` | `'<script src="/_nexoria/chartjs-adapter.js" type="module" defer></script>'` |
| `CHARTJS_RUNTIME_TAG` | `'<script type="importmap">{"imports": {"chart.js": "https://unpkg.com/chart.js@4.5.1/dist/chart.js", "@kurkle/color": "https://unpkg.com/@kurkle/color@0.4.0/dist/color.esm.js"}}</script>\n<script src="/_nexoria/chartjs-adapter.js" type="module" defer></script>'` |
