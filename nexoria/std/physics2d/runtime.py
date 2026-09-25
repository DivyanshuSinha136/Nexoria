"""
nexoria.std.physics2d.runtime
================================
A small, dependency-free engine in the spirit of GSAP's
Physics2DPlugin: give an element an initial `velocity` and `angle`,
optional `gravity`, `friction`, `spin`, and `bounce`, and it flies
via `requestAnimationFrame`, moved with a `transform: translate()
rotate()` (so it never disturbs layout).

Call `physics2d_runtime()` once anywhere in your page.
"""

from __future__ import annotations

from ...core.element import el, Element

PHYSICS2D_RUNTIME_JS = r"""
(function () {
  if (window.__nxPhysics2D) return;
  window.__nxPhysics2D = true;

  function startOne(elm) {
    if (elm.getAttribute("data-nx-physics2d-running") === "true") return;
    elm.setAttribute("data-nx-physics2d-running", "true");
    elm.removeAttribute("data-nx-physics2d-settled");

    var v = parseFloat(elm.getAttribute("data-nx-physics2d-velocity")) || 0;
    var angleDeg = parseFloat(elm.getAttribute("data-nx-physics2d-angle")) || 0;
    var gravity = parseFloat(elm.getAttribute("data-nx-physics2d-gravity")) || 0;
    var friction = Math.min(0.99, Math.max(0, parseFloat(elm.getAttribute("data-nx-physics2d-friction")) || 0));
    var spin = parseFloat(elm.getAttribute("data-nx-physics2d-spin")) || 0;
    var bounce = parseFloat(elm.getAttribute("data-nx-physics2d-bounce")) || 0;
    var floorMode = elm.getAttribute("data-nx-physics2d-floor") || "none";
    var removeOnSettle = elm.getAttribute("data-nx-physics2d-remove-on-settle") === "true";

    var rad = angleDeg * Math.PI / 180;
    var vx = v * Math.cos(rad);
    var vy = v * Math.sin(rad);
    var x = 0, y = 0, rot = 0;
    var settled = false;

    // The floor is computed once, as a translate-space limit, from
    // the element's starting position -- a lightweight approximation
    // (no re-measurement mid-flight), good enough for a physics toy
    // but not for a page that scrolls/resizes mid-animation.
    var floorLimit = Infinity;
    if (floorMode === "viewport") {
      var startRect = elm.getBoundingClientRect();
      floorLimit = window.innerHeight - startRect.bottom;
    } else if (floorMode === "parent") {
      var parent = elm.offsetParent;
      if (parent) floorLimit = parent.clientHeight - elm.offsetTop - elm.offsetHeight;
    }

    var last = performance.now();
    function step(now) {
      var dt = Math.min(0.05, (now - last) / 1000);
      last = now;

      vy += gravity * dt;
      var damp = Math.pow(1 - friction, dt * 60);
      vx *= damp;
      vy *= damp;

      x += vx * dt;
      y += vy * dt;
      rot += spin * dt;

      if (floorLimit !== Infinity && y >= floorLimit) {
        y = floorLimit;
        if (bounce > 0 && Math.abs(vy) > 30) {
          vy = -vy * bounce;
          vx = vx * bounce;
        } else {
          vy = 0;
          vx *= 0.9;
          settled = Math.abs(vx) < 5;
        }
      }

      elm.style.transform = "translate(" + x.toFixed(2) + "px, " + y.toFixed(2) + "px) rotate(" + rot.toFixed(2) + "deg)";

      if (!settled) {
        requestAnimationFrame(step);
      } else {
        elm.setAttribute("data-nx-physics2d-running", "false");
        elm.setAttribute("data-nx-physics2d-settled", "true");
        if (removeOnSettle) elm.remove();
      }
    }
    requestAnimationFrame(step);
  }

  document.querySelectorAll("[data-nx-physics2d]").forEach(function (elm) {
    var trigger = elm.getAttribute("data-nx-physics2d-trigger") || "auto";
    if (trigger === "auto") {
      startOne(elm);
    } else if (trigger === "click") {
      elm.addEventListener("click", function () { startOne(elm); });
    } else if (trigger === "hover") {
      elm.addEventListener("mouseenter", function () { startOne(elm); });
    } else if (trigger === "event") {
      elm.addEventListener("nx:physics2d:start", function () { startOne(elm); });
    }
  });
})();
""".strip()


def physics2d_runtime() -> Element:
    """A `<script>` `Element` carrying the Physics2D engine. Render it once per page."""
    return el("script", PHYSICS2D_RUNTIME_JS)
