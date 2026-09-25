"""
nexoria.std.charts.runtime
=============================
A single small, dependency-free `<script>` that powers every
`nexoria.std.charts` entrance animation: bars growing up from the
baseline, pie/donut wedges popping in, area fills fading in, dots
popping in, gauge arcs sweeping to value -- all pure CSS transitions
triggered by one shared `IntersectionObserver` flipping a
`.nx-charted` class on (see `nexoria.std.charts.styles`). Line/area
strokes are the one exception that needs actual JS math (an SVG
path's rendered length isn't knowable ahead of time for a curved
line), handled the same `getTotalLength()` + animated
`stroke-dashoffset` way as `nexoria.std.animation.svg.draw_svg`.

No CDN asset, no build step -- call `charts_runtime()` once anywhere
in your page (it's a no-op if rendered more than once, guarded by
`window.__nxCharts`).
"""

from __future__ import annotations

from ...core.element import el, Element

CHARTS_RUNTIME_JS = r"""
(function () {
  if (window.__nxCharts) return;
  window.__nxCharts = true;

  function onReady(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  // -- generic "flip .nx-charted on once visible" observer -------------
  function watchClassFlip(selector, threshold) {
    var els = document.querySelectorAll(selector);
    if (!els.length) return;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        if (el.getAttribute("data-nx-charted") === "true") return;
        el.setAttribute("data-nx-charted", "true");
        observer.unobserve(el);
        // rAF so the just-set starting state has been painted before
        // the class flip kicks off the CSS transition.
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            el.classList.add("nx-charted");
          });
        });
      });
    }, { threshold: threshold });
    els.forEach(function (el) { observer.observe(el); });
  }

  // -- animated line/area strokes ---------------------------------------
  function initLines() {
    var paths = document.querySelectorAll("[data-nx-chart-line]");
    if (!paths.length) return;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var path = entry.target;
        if (!entry.isIntersecting) return;
        if (path.getAttribute("data-nx-charted") === "true") return;
        path.setAttribute("data-nx-charted", "true");
        observer.unobserve(path);

        var duration = parseFloat(path.getAttribute("data-nx-chart-duration")) || 1200;
        var delay = parseFloat(path.getAttribute("data-nx-chart-delay")) || 0;
        var len = 0;
        try { len = path.getTotalLength(); } catch (e) { len = 0; }
        if (!len) return;
        path.style.strokeDasharray = len + " " + len;
        path.style.strokeDashoffset = len;
        path.style.transition = "stroke-dashoffset " + duration + "ms cubic-bezier(.16,1,.3,1) " + delay + "ms";
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            path.style.strokeDashoffset = "0";
          });
        });
      });
    }, { threshold: 0.2 });
    paths.forEach(function (p) { observer.observe(p); });
  }

  onReady(function () {
    watchClassFlip("[data-nx-chart-bar]", 0.2);
    watchClassFlip("[data-nx-chart-wedge]", 0.2);
    watchClassFlip("[data-nx-chart-area]", 0.2);
    watchClassFlip("[data-nx-chart-dot]", 0.2);
    watchClassFlip("[data-nx-chart-gauge]", 0.3);
    initLines();
  });
})();
""".strip()


def charts_runtime() -> Element:
    """A `<script>` `Element` carrying the full charts animation
    runtime. Render it once per page, alongside `chart_styles()`."""
    return el("script", CHARTS_RUNTIME_JS)
