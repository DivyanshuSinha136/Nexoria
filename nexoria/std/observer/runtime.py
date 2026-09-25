"""
nexoria.std.observer.runtime
===============================
A small, dependency-free engine in the spirit of GSAP's Observer
(https://gsap.com/docs/v3/Plugins/Observer/): it normalizes wheel
scrolling and pointer drag (which covers mouse, touch, and pen --
see MDN's Pointer Events) into one stream of directional callbacks
-- up/down/left/right, a raw delta stream, hover, press/release, and
click -- so you can build swipe/scroll-driven interactions without
juggling `wheel`/`pointerdown`/`pointermove`/`pointerup` yourself.

Call `observer_runtime()` once anywhere in your page.
"""

from __future__ import annotations

from ...core.element import el, Element

OBSERVER_RUNTIME_JS = r"""
(function () {
  if (window.__nxObserver) return;
  window.__nxObserver = true;

  function fire(elm, name, ev, dx, dy) {
    var js = elm.getAttribute("data-nx-observer-" + name);
    if (!js) return;
    try {
      var fn = new Function("event", "deltaX", "deltaY", "el", js);
      fn(ev || null, dx || 0, dy || 0, elm);
    } catch (e) {
      console.error("nexoria observer handler error:", e);
    }
  }

  function setup(elm) {
    var tolerance = parseFloat(elm.getAttribute("data-nx-observer-tolerance")) || 8;
    var preventDefault = elm.getAttribute("data-nx-observer-prevent-default") !== "false";
    var target = elm.getAttribute("data-nx-observer-target") === "window" ? window : elm;

    var lockUntil = 0;
    function direction(dx, dy, ev) {
      fire(elm, "change", ev, dx, dy);
      var now = performance.now();
      if (now < lockUntil) return;
      if (Math.abs(dx) < tolerance && Math.abs(dy) < tolerance) return;
      lockUntil = now + 200; // debounce repeats while a gesture continues, similar to GSAP's feel
      if (Math.abs(dx) > Math.abs(dy)) {
        fire(elm, dx > 0 ? "right" : "left", ev, dx, dy);
      } else {
        fire(elm, dy > 0 ? "down" : "up", ev, dx, dy);
      }
    }

    // wheel / trackpad scroll
    target.addEventListener("wheel", function (ev) {
      if (preventDefault) ev.preventDefault();
      direction(ev.deltaX, ev.deltaY, ev);
    }, { passive: !preventDefault });

    // pointer drag (unifies mouse, touch, and pen)
    var dragging = false, startX = 0, startY = 0, lastX = 0, lastY = 0;
    target.addEventListener("pointerdown", function (ev) {
      dragging = true;
      startX = lastX = ev.clientX;
      startY = lastY = ev.clientY;
      fire(elm, "press", ev, 0, 0);
    });
    window.addEventListener("pointermove", function (ev) {
      if (!dragging) return;
      var dx = ev.clientX - lastX, dy = ev.clientY - lastY;
      lastX = ev.clientX;
      lastY = ev.clientY;
      direction(dx, dy, ev);
    });
    window.addEventListener("pointerup", function (ev) {
      if (!dragging) return;
      dragging = false;
      fire(elm, "release", ev, ev.clientX - startX, ev.clientY - startY);
    });

    // hover + click
    elm.addEventListener("mouseenter", function (ev) { fire(elm, "hoverenter", ev, 0, 0); });
    elm.addEventListener("mouseleave", function (ev) { fire(elm, "hoverleave", ev, 0, 0); });
    elm.addEventListener("click", function (ev) { fire(elm, "click", ev, 0, 0); });
  }

  document.querySelectorAll("[data-nx-observer]").forEach(setup);
})();
""".strip()


def observer_runtime() -> Element:
    """A `<script>` `Element` carrying the Observer engine. Render it once per page."""
    return el("script", OBSERVER_RUNTIME_JS)
