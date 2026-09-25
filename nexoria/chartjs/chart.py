"""
nexoria.chartjs.chart
========================
Optional charting layer. Describe a Chart.js chart declaratively in
Python; Nexoria serializes it to the JSON config Chart.js itself
expects, and the client adapter (`runtime/chartjs-adapter.js`, loaded
only when `App(chartjs=True)` is set) instantiates a real `Chart`
against a `<canvas>`. Chart.js itself is pulled from CDN as an ES
module -- never a Python dependency.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import json

CHARTJS_CDN = "https://unpkg.com/chart.js@4.5.1/dist/chart.js"
# chart.js's ESM entry imports one real external dependency internally
# (its color-parsing helper) -- both must be present in the import map
# or the browser throws "Failed to resolve module specifier
# '@kurkle/color'". Verified transitively (not just the top-level
# file's own imports) against the actual published package contents.
KURKLE_COLOR_CDN = "https://unpkg.com/@kurkle/color@0.4.0/dist/color.esm.js"
CHARTJS_IMPORTS = {"chart.js": CHARTJS_CDN, "@kurkle/color": KURKLE_COLOR_CDN}
CHARTJS_ADAPTER_TAG = '<script src="/_nexoria/chartjs-adapter.js" type="module" defer></script>'
CHARTJS_RUNTIME_TAG = (
    f'<script type="importmap">{json.dumps({"imports": CHARTJS_IMPORTS})}</script>\n'
    f'{CHARTJS_ADAPTER_TAG}'
)


@dataclass
class Dataset:
    """
    One Chart.js dataset. `label` and `data` are the common case; any
    other Chart.js dataset option (`backgroundColor`, `borderColor`,
    `tension`, `fill`, ...) can be passed as extra keyword args and is
    included verbatim.

        Dataset("Revenue", [10, 20, 15], backgroundColor="#6366f1")
    """
    label: str
    data: list[Any]
    extra: dict[str, Any] = field(default_factory=dict)

    def __init__(self, label: str, data: list[Any], **extra: Any):
        self.label = label
        self.data = data
        self.extra = extra

    def to_dict(self) -> dict:
        return {"label": self.label, "data": self.data, **self.extra}


@dataclass
class Chart:
    """
    A Chart.js chart. `type` is any Chart.js chart type ("bar", "line",
    "pie", "doughnut", "radar", "polarArea", "bubble", "scatter", ...).
    `options` is Chart.js's own options object, passed through verbatim
    (scales, plugins, responsive, etc.) -- Nexoria doesn't reshape it.

        Chart(
            type="bar",
            labels=["Jan", "Feb", "Mar"],
            datasets=[Dataset("Revenue", [10, 20, 15], backgroundColor="#6366f1")],
            options={"responsive": True},
        )
    """
    type: str
    labels: list[Any]
    datasets: list[Dataset]
    options: dict[str, Any] = field(default_factory=dict)
    width: str = "100%"
    height: str = "320px"

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "data": {
                "labels": self.labels,
                "datasets": [d.to_dict() for d in self.datasets],
            },
            "options": self.options,
        }

    def to_element(self):
        from ..core.element import el
        return el(
            "canvas",
            **{
                "class": "nx-chartjs-canvas",
                "data-nx-chart": json.dumps(self.to_dict()),
                "style": f"width:{self.width};height:{self.height};",
            },
        )
