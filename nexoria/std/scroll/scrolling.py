"""
nexoria.std.scroll.scrolling
================================
Page-scrolling tools: a "back to top" button that appears past a
threshold, a top-of-page scroll progress bar, smooth in-page anchor
links, and a scrollable panel. The threshold/progress-bar behavior
needs one shared listener -- `scroll_runtime()` -- rendered once per
page; everything else is self-contained (`scrollIntoView`/`scrollTo`
calls in a literal `onclick=`, no server round-trip).
"""

from __future__ import annotations
from typing import Any, Optional

from ...core.element import el, Element

SCROLL_RUNTIME_JS = r"""
(function () {
  if (window.__nxScroll) return;
  window.__nxScroll = true;

  function update() {
    var doc = document.documentElement;
    var scrolled = doc.scrollTop || document.body.scrollTop;
    var height = (doc.scrollHeight || document.body.scrollHeight) - doc.clientHeight;
    var pct = height > 0 ? (scrolled / height) * 100 : 0;

    document.querySelectorAll("[data-nx-scroll-progress]").forEach(function (bar) {
      bar.style.width = pct + "%";
    });
    document.querySelectorAll("[data-nx-scroll-top-threshold]").forEach(function (btn) {
      var threshold = parseFloat(btn.getAttribute("data-nx-scroll-top-threshold")) || 300;
      btn.style.display = scrolled > threshold ? "inline-flex" : "none";
    });
  }

  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", update);
  } else {
    update();
  }
})();
""".strip()


def scroll_runtime() -> Element:
    """A `<script>` `Element` powering `scroll_progress_bar()` and `scroll_to_top_button()`. Render it once per page."""
    return el("script", SCROLL_RUNTIME_JS)


def scroll_progress_bar(*, color: str = "var(--nx-primary)", height: str = "4px") -> Element:
    """A fixed bar at the top of the page whose width tracks scroll progress. Needs `scroll_runtime()`."""
    return el("div", data_nx_scroll_progress="true", style={
        "position": "fixed", "top": "0", "left": "0", "width": "0%", "height": height,
        "background": color, "z_index": "1100", "transition": "width 0.1s linear",
    })


def scroll_to_top_button(*, threshold: int = 300, label: str = "\u2191") -> Element:
    """A "back to top" button, hidden until the page is scrolled past `threshold` px. Needs `scroll_runtime()`."""
    return el(
        "button", label,
        type="button",
        aria_label="Scroll to top",
        onclick="window.scrollTo({top: 0, behavior: 'smooth'})",
        data_nx_scroll_top_threshold=str(threshold),
        style={
            "display": "none", "position": "fixed", "bottom": "24px", "right": "24px",
            "z_index": "1100", "width": "44px", "height": "44px", "border_radius": "50%",
            "border": "none", "background": "var(--nx-primary)", "color": "#ffffff",
            "font_size": "1.1rem", "cursor": "pointer", "box_shadow": "var(--nx-shadow)",
            "align_items": "center", "justify_content": "center",
        },
    )


def anchor_link(label: str, target_id: str, *, offset: int = 0, class_: Optional[str] = None) -> Element:
    """
    `anchor_link("Pricing", "pricing")`. Smoothly scrolls to the
    element with `id="pricing"` instead of the browser's instant
    jump, and (unlike a plain `#pricing` href) doesn't touch the URL
    hash. `offset` shifts the stop point up by that many pixels
    (e.g. to clear a sticky navbar).
    """
    target = target_id.lstrip("#")
    js = (
        f"event.preventDefault();"
        f"var t=document.getElementById('{target}');"
        f"if(t){{var y=t.getBoundingClientRect().top+window.pageYOffset-{int(offset)};"
        f"window.scrollTo({{top:y, behavior:'smooth'}});}}"
    )
    return el("a", label, href=f"#{target}", onclick=js, class_=class_)


def smooth_scroll_container(*children: Any, height: str = "400px", class_: Optional[str] = None) -> Element:
    """A scrollable panel with native smooth scrolling for its internal content (e.g. a chat log, a long list)."""
    return el(
        "div", *children,
        class_=class_,
        style={
            "height": height, "overflow_y": "auto", "scroll_behavior": "smooth",
            "border": "1px solid var(--nx-border)", "border_radius": "var(--nx-radius-sm)",
        },
    )
