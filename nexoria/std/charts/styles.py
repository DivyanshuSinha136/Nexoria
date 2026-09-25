"""
nexoria.std.charts.styles
============================
Base CSS shared by every `nexoria.std.charts` component: the
before/after transition rules `charts_runtime()` triggers by flipping
a `.nx-charted` class on (same `data-nx-*` + `IntersectionObserver` +
class-flip idea as `nexoria.std.animation.reveal`), plus the small
legend/axis chrome every chart type reuses. Per-instance timing
(duration/delay/stagger) travels as inline CSS custom properties
(`--nx-chart-duration`, `--nx-chart-delay`) set per element, same
trick as `reveal_styles()`, so these rules never need to be
duplicated per instance.
"""

from __future__ import annotations
from ...core.element import el, Element

CHART_STYLES_CSS = """
[data-nx-chart-bar] {
  transition-property: transform;
  transition-duration: var(--nx-chart-duration, 900ms);
  transition-delay: var(--nx-chart-delay, 0ms);
  transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
  transform-box: fill-box;
}
[data-nx-chart-bar="v"] { transform: scaleY(0); transform-origin: 50% 100%; }
[data-nx-chart-bar="v"].nx-charted { transform: scaleY(1); }
[data-nx-chart-bar="h"] { transform: scaleX(0); transform-origin: 0% 50%; }
[data-nx-chart-bar="h"].nx-charted { transform: scaleX(1); }

[data-nx-chart-wedge] {
  transform: scale(0);
  transform-origin: center;
  transform-box: fill-box;
  transition: transform var(--nx-chart-duration, 700ms) cubic-bezier(0.34, 1.56, 0.64, 1)
    var(--nx-chart-delay, 0ms);
}
[data-nx-chart-wedge].nx-charted { transform: scale(1); }

[data-nx-chart-area] {
  opacity: 0;
  transition: opacity var(--nx-chart-duration, 900ms) ease var(--nx-chart-delay, 0ms);
}
[data-nx-chart-area].nx-charted { opacity: 1; }

[data-nx-chart-dot] {
  opacity: 0;
  transform: scale(0);
  transform-origin: center;
  transform-box: fill-box;
  transition: opacity var(--nx-chart-duration, 400ms) ease var(--nx-chart-delay, 0ms),
    transform var(--nx-chart-duration, 400ms) cubic-bezier(0.34, 1.56, 0.64, 1) var(--nx-chart-delay, 0ms);
}
[data-nx-chart-dot].nx-charted { opacity: 1; transform: scale(1); }

[data-nx-chart-gauge] {
  transition: stroke-dashoffset var(--nx-chart-duration, 1000ms) cubic-bezier(0.16, 1, 0.3, 1)
    var(--nx-chart-delay, 0ms);
}
[data-nx-chart-gauge].nx-charted { stroke-dashoffset: var(--nx-gauge-offset, 0); }

.nx-chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 10px;
  font-size: 0.85rem;
  color: var(--nx-text-muted);
  font-family: var(--nx-font);
}
.nx-chart-legend-item { display: inline-flex; align-items: center; gap: 6px; }
.nx-chart-legend-swatch { width: 10px; height: 10px; border-radius: 3px; flex: none; }
.nx-chart-axis-label { fill: var(--nx-text-muted); font-size: 11px; font-family: var(--nx-font); }
.nx-chart-grid-line { stroke: var(--nx-border); stroke-width: 1; shape-rendering: crispEdges; }
""".strip()


def chart_styles() -> Element:
    """A `<style>` `Element` carrying the shared chart CSS. Render it
    once per page, alongside `charts_runtime()`."""
    return el("style", CHART_STYLES_CSS)
