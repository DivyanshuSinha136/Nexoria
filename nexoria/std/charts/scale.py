"""
nexoria.std.charts.scale
===========================
Small, dependency-free scale math shared by every `nexoria.std.charts`
component: mapping a data domain onto a pixel range, and picking
human-friendly axis ticks ("nice numbers" -- the same rounding trick
every real charting library uses so an axis reads `0, 25, 50, 75,
100` instead of `0, 23.7, 47.4, ...`).
"""

from __future__ import annotations
import math
from typing import List, Tuple


class LinearScale:
    """
    Maps a numeric `domain` `(min, max)` onto a pixel `range_`
    `(min, max)` and back. `range_` is given start-to-end in the
    *data* sense (e.g. `(height, 0)` for a y-axis, since SVG y grows
    downward but data value should grow upward).

        y = LinearScale((0, 100), (chart_height, 0))
        y.to_px(50)   # -> chart_height / 2
    """

    __slots__ = ("domain_min", "domain_max", "range_min", "range_max")

    def __init__(self, domain: Tuple[float, float], range_: Tuple[float, float]) -> None:
        self.domain_min, self.domain_max = domain
        self.range_min, self.range_max = range_
        if self.domain_max == self.domain_min:
            # A flat/constant series -- widen the domain by 1 so
            # division below never hits a zero span.
            self.domain_max = self.domain_min + 1

    def to_px(self, value: float) -> float:
        t = (value - self.domain_min) / (self.domain_max - self.domain_min)
        return self.range_min + t * (self.range_max - self.range_min)


def nice_number(value: float, round_: bool) -> float:
    """The "nicest" number close to `value` -- 1, 2, 5 or 10 times a
    power of ten -- used to round either a raw span (`round_=False`)
    up to a clean ceiling, or a tick step (`round_=True`) to the
    nearest clean step."""
    if value == 0:
        return 0.0
    exponent = math.floor(math.log10(value))
    fraction = value / (10 ** exponent)
    if round_:
        if fraction < 1.5:
            nice_fraction = 1.0
        elif fraction < 3:
            nice_fraction = 2.0
        elif fraction < 7:
            nice_fraction = 5.0
        else:
            nice_fraction = 10.0
    else:
        if fraction <= 1:
            nice_fraction = 1.0
        elif fraction <= 2:
            nice_fraction = 2.0
        elif fraction <= 5:
            nice_fraction = 5.0
        else:
            nice_fraction = 10.0
    return nice_fraction * (10 ** exponent)


def nice_ticks(min_v: float, max_v: float, count: int = 5) -> List[float]:
    """
    A list of evenly-spaced, human-friendly tick values spanning
    (at least) `[min_v, max_v]` -- e.g. `nice_ticks(0, 87, 5)` ->
    `[0, 20, 40, 60, 80, 100]`. Always includes both a tick at or
    below `min_v` and one at or above `max_v`.
    """
    if min_v == max_v:
        min_v, max_v = min_v - 1, max_v + 1
    span = nice_number(max_v - min_v, False)
    step = nice_number(span / max(1, count - 1), True)
    if step == 0:
        return [min_v, max_v]
    nice_min = math.floor(min_v / step) * step
    nice_max = math.ceil(max_v / step) * step
    ticks = []
    t = nice_min
    # guard against float drift producing one tick too many/few
    while t <= nice_max + step * 1e-9:
        ticks.append(round(t, 10))
        t += step
    return ticks
