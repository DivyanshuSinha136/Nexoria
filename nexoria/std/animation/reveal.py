"""
nexoria.std.animation.reveal
===============================
Scroll-triggered entrance animations. `animate_in(...)` wraps content
in a marker `<div>`; `nexoria.std.animation.runtime.animation_runtime()`
watches it with `IntersectionObserver` and flips a `.nx-revealed`
class on when it scrolls into view. The actual before/after CSS lives
in `reveal_styles()` (a raw `@keyframes`-adjacent stylesheet -- see
`nexoria.std.premium.theme` for why this is a plain CSS string rather
than a `Stylesheet` rule) so the per-instance duration/delay (set as
inline CSS custom properties) can vary without duplicating the rules.
"""

from __future__ import annotations
from typing import Any, Optional

from ...core.element import el, Element

REVEAL_STYLES_CSS = """
[data-nx-reveal] {
  opacity: 0;
  transition-property: opacity, transform;
  transition-duration: var(--nx-reveal-duration, 600ms);
  transition-delay: var(--nx-reveal-delay, 0ms);
  transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
  will-change: opacity, transform;
}
[data-nx-reveal="fade"] { transform: none; }
[data-nx-reveal="fade-up"] { transform: translateY(28px); }
[data-nx-reveal="fade-down"] { transform: translateY(-28px); }
[data-nx-reveal="slide-left"] { transform: translateX(40px); }
[data-nx-reveal="slide-right"] { transform: translateX(-40px); }
[data-nx-reveal="zoom-in"] { transform: scale(0.9); }
[data-nx-reveal].nx-revealed {
  opacity: 1;
  transform: none;
}
""".strip()


def reveal_styles() -> Element:
    """A `<style>` `Element` carrying the reveal base rules. Render it once per page, alongside `animation_runtime()`."""
    return el("style", REVEAL_STYLES_CSS)


def animate_in(
    *children: Any,
    effect: str = "fade-up",
    duration: int = 600,
    delay: int = 0,
    once: bool = True,
    class_: Optional[str] = None,
) -> Element:
    """
    `animate_in(el("h2", "Welcome"), effect="fade-up", delay=150)`.

    `effect`: "fade" | "fade-up" | "fade-down" | "slide-left" |
      "slide-right" | "zoom-in". `once=False` re-plays the animation
      every time the element re-enters the viewport.

    Needs `reveal_styles()` and `animation_runtime()` (from
    `nexoria.std.animation`) rendered once per page.
    """
    style = {
        "--nx-reveal-duration": f"{duration}ms",
        "--nx-reveal-delay": f"{delay}ms",
    }
    props: dict[str, Any] = {
        "style": style,
        "class_": class_,
        "data_nx_reveal": effect,
    }
    if not once:
        props["data_nx_reveal_once"] = "false"
    return el("div", *children, **props)
