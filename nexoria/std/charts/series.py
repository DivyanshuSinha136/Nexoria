"""
nexoria.std.charts.series
============================
Shared input normalization for `nexoria.std.charts.line`/`.bar`:
both accept either a bare list of numbers (a single, unnamed series)
or a list of `{"name": ..., "values": [...], "color": ...}` dicts
(one or more named series) -- `normalize_series()` turns either shape
into a consistent list of `SeriesSpec` so the chart-drawing code
itself only has to handle one shape.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Union

from .palette import color_for

Number = Union[int, float]


@dataclass
class SeriesSpec:
    name: Optional[str]
    values: List[Number]
    color: str


def normalize_series(
    series: Union[Sequence[Number], Sequence[Dict[str, Any]]],
    colors: Optional[Sequence[str]] = None,
) -> List[SeriesSpec]:
    """
    Accepts `[10, 20, 15]` (one unnamed series) or
    `[{"name": "2024", "values": [10, 20, 15], "color": "#f00"}, ...]`
    (one or more named series, `color` optional -- falls back to the
    palette by position) and always returns a list of `SeriesSpec`.
    """
    if not series:
        return []
    if isinstance(series[0], dict):
        out: List[SeriesSpec] = []
        for i, s in enumerate(series):
            out.append(SeriesSpec(
                name=s.get("name"),
                values=list(s.get("values", [])),
                color=s.get("color") or color_for(i, colors),
            ))
        return out
    # a flat list of numbers -> a single unnamed series
    return [SeriesSpec(name=None, values=list(series), color=color_for(0, colors))]


def max_len(specs: Sequence[SeriesSpec]) -> int:
    return max((len(s.values) for s in specs), default=0)


def value_bounds(specs: Sequence[SeriesSpec]) -> "tuple[float, float]":
    """The (min, max) across every value in every series. `(0, 1)`
    when there's no data at all."""
    all_values = [v for s in specs for v in s.values]
    if not all_values:
        return 0.0, 1.0
    return min(all_values), max(all_values)
