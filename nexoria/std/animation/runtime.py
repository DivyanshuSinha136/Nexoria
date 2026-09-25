"""
nexoria.std.animation.runtime
================================
A single small, dependency-free `<script>` that powers every
`nexoria.std.animation` component: scroll-triggered reveals, count-up
numbers, typewriter text, scramble text, `draw_svg`, and `morph_svg`.
`split_text` needs no runtime code of its own -- it's built entirely
from the reveal system below, one `<span>` per character/word with a
staggered `transition-delay`. All driven by `IntersectionObserver` +
plain DOM APIs -- no CDN asset, no build step, same "drop it once in
your root layout" idea as `nexoria.bootstrap`'s adapter tag, just
without the CDN dependency.

Call `animation_runtime()` once anywhere in your page (it's a no-op
if you happen to render it more than once -- the script guards
itself with `window.__nxAnim`).
"""

from __future__ import annotations

from ...core.element import el, Element

ANIMATION_RUNTIME_JS = r"""
(function () {
  if (window.__nxAnim) return;
  window.__nxAnim = true;

  function onReady(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  // -- scroll reveal -------------------------------------------------
  function initReveal() {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var el = entry.target;
        var once = el.getAttribute("data-nx-reveal-once") !== "false";
        if (entry.isIntersecting) {
          el.classList.add("nx-revealed");
          if (once) observer.unobserve(el);
        } else if (!once) {
          el.classList.remove("nx-revealed");
        }
      });
    }, { threshold: 0.15 });
    document.querySelectorAll("[data-nx-reveal]").forEach(function (el) {
      observer.observe(el);
    });
  }

  // -- count-up numbers ------------------------------------------------
  function initCounters() {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        if (el.getAttribute("data-nx-counted") === "true") return;
        el.setAttribute("data-nx-counted", "true");
        observer.unobserve(el);

        var target = parseFloat(el.getAttribute("data-nx-counter")) || 0;
        var duration = parseFloat(el.getAttribute("data-nx-counter-duration")) || 1500;
        var prefix = el.getAttribute("data-nx-counter-prefix") || "";
        var suffix = el.getAttribute("data-nx-counter-suffix") || "";
        var decimals = parseInt(el.getAttribute("data-nx-counter-decimals") || "0", 10);
        var start = performance.now();

        function frame(now) {
          var progress = Math.min(1, (now - start) / duration);
          var eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
          var value = target * eased;
          el.textContent = prefix + value.toFixed(decimals) + suffix;
          if (progress < 1) requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
      });
    }, { threshold: 0.4 });
    document.querySelectorAll("[data-nx-counter]").forEach(function (el) {
      observer.observe(el);
    });
  }

  // -- typewriter text --------------------------------------------------
  function initTypewriter() {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        if (el.getAttribute("data-nx-typed") === "true") return;
        el.setAttribute("data-nx-typed", "true");
        observer.unobserve(el);

        var full = el.getAttribute("data-nx-typewriter") || "";
        var speed = parseFloat(el.getAttribute("data-nx-typewriter-speed")) || 40;
        el.textContent = "";
        var i = 0;
        (function step() {
          if (i > full.length) return;
          el.textContent = full.slice(0, i);
          i += 1;
          setTimeout(step, speed);
        })();
      });
    }, { threshold: 0.4 });
    document.querySelectorAll("[data-nx-typewriter]").forEach(function (el) {
      observer.observe(el);
    });
  }

  // -- scramble text --------------------------------------------------
  function initScramble() {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        if (el.getAttribute("data-nx-scrambled") === "true") return;
        el.setAttribute("data-nx-scrambled", "true");
        observer.unobserve(el);

        var full = el.getAttribute("data-nx-scramble") || "";
        var pool = el.getAttribute("data-nx-scramble-chars") || "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        var frameSpeed = parseFloat(el.getAttribute("data-nx-scramble-speed")) || 40;
        var revealDelay = parseFloat(el.getAttribute("data-nx-scramble-reveal-delay")) || 35;
        var locked = 0;
        var frame = 0;

        function randomChar() {
          return pool.charAt(Math.floor(Math.random() * pool.length));
        }

        function tick() {
          if (locked >= full.length) {
            el.textContent = full;
            return;
          }
          // every `revealDelay` frames, lock in one more real character
          if (frame > 0 && frame % Math.max(1, Math.round(revealDelay / frameSpeed)) === 0) {
            locked += 1;
          }
          var out = "";
          for (var i = 0; i < full.length; i++) {
            if (i < locked || full.charAt(i) === " ") {
              out += full.charAt(i);
            } else {
              out += randomChar();
            }
          }
          el.textContent = out;
          frame += 1;
          setTimeout(tick, frameSpeed);
        }
        tick();
      });
    }, { threshold: 0.4 });
    document.querySelectorAll("[data-nx-scramble]").forEach(function (el) {
      observer.observe(el);
    });
  }

  // -- DrawSVG (stroke reveal) ------------------------------------------
  function initDrawSVG() {
    function drawableShapes(svg) {
      return svg.querySelectorAll("path, circle, ellipse, line, polyline, polygon, rect");
    }

    function runDraw(svg) {
      var duration = parseFloat(svg.getAttribute("data-nx-drawsvg-duration")) || 1500;
      var delay = parseFloat(svg.getAttribute("data-nx-drawsvg-delay")) || 0;
      var stagger = parseFloat(svg.getAttribute("data-nx-drawsvg-stagger")) || 100;
      var shapes = drawableShapes(svg);
      shapes.forEach(function (shape, i) {
        var len = 0;
        try { len = shape.getTotalLength(); } catch (e) { len = 0; }
        if (!len) return;
        shape.style.strokeDasharray = len + " " + len;
        shape.style.strokeDashoffset = len;
        shape.style.transition = "stroke-dashoffset " + duration + "ms ease " +
          (delay + i * stagger) + "ms";
        // force a layout flush so the transition actually animates
        // from the just-set starting offset, then flip to 0
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            shape.style.strokeDashoffset = "0";
          });
        });
      });
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var svg = entry.target;
        if (!entry.isIntersecting) return;
        if (svg.getAttribute("data-nx-drawn") === "true") return;
        svg.setAttribute("data-nx-drawn", "true");
        observer.unobserve(svg);
        runDraw(svg);
      });
    }, { threshold: 0.25 });
    document.querySelectorAll("[data-nx-drawsvg]").forEach(function (svg) {
      observer.observe(svg);
    });
  }

  // -- MorphSVG (lightweight coordinate-lerp morph) ---------------------
  function initMorphSVG() {
    // Extracts the numeric coordinates out of a path "d" string,
    // in order, along with the non-numeric "skeleton" they slot into.
    // Morphing only smoothly interpolates when both paths have the
    // same *number* of coordinates (same command structure) -- this
    // is a lightweight lerp, not a true arbitrary-topology morph like
    // GSAP's commercial MorphSVGPlugin. When counts differ, it snaps
    // straight to the target shape instead of interpolating.
    function parsePath(d) {
      var nums = (d.match(/-?\d*\.?\d+(?:e-?\d+)?/g) || []).map(Number);
      var skeleton = d.split(/-?\d*\.?\d+(?:e-?\d+)?/g);
      return { nums: nums, skeleton: skeleton };
    }

    function build(skeleton, nums) {
      var out = skeleton[0];
      for (var i = 0; i < nums.length; i++) {
        out += (Math.round(nums[i] * 1000) / 1000) + skeleton[i + 1];
      }
      return out;
    }

    function morph(path) {
      var from = path.getAttribute("d") || "";
      var to = path.getAttribute("data-nx-morph-to") || "";
      var duration = parseFloat(path.getAttribute("data-nx-morph-duration")) || 800;
      if (!to) return;

      var a = parsePath(from);
      var b = parsePath(to);
      if (a.nums.length !== b.nums.length) {
        // can't lerp mismatched shapes -- snap instantly
        path.setAttribute("d", to);
        return;
      }
      var start = performance.now();
      function frame(now) {
        var progress = Math.min(1, (now - start) / duration);
        var eased = progress < 0.5 ? 4 * progress * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 3) / 2; // ease-in-out-cubic
        var nums = a.nums.map(function (v, i) { return v + (b.nums[i] - v) * eased; });
        path.setAttribute("d", build(a.skeleton, nums));
        if (progress < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }

    document.querySelectorAll("[data-nx-morph-trigger]").forEach(function (path) {
      var trigger = path.getAttribute("data-nx-morph-trigger");
      if (trigger === "hover") {
        var target = path.closest("svg") || path;
        target.addEventListener("mouseenter", function () { morph(path); });
      } else if (trigger === "click") {
        var target2 = path.closest("svg") || path;
        target2.addEventListener("click", function () { morph(path); });
      } else if (trigger === "scroll") {
        var observer = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            observer.unobserve(path);
            morph(path);
          });
        }, { threshold: 0.4 });
        observer.observe(path);
      } else {
        // "auto" -- run once, immediately
        morph(path);
      }
    });
  }

  onReady(function () {
    initReveal();
    initCounters();
    initTypewriter();
    initScramble();
    initDrawSVG();
    initMorphSVG();
  });
})();
""".strip()


def animation_runtime() -> Element:
    """
    A `<script>` `Element` carrying the full animation runtime --
    scroll reveal, counters, typewriter, scramble text, `draw_svg`,
    and `morph_svg`. Render it once per page.
    """
    return el("script", ANIMATION_RUNTIME_JS)
