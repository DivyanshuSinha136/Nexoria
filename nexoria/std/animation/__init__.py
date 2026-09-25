"""
nexoria.std.animation
========================
Two complementary animation systems for `nexoria.std`, importable
together with no CDN dependency:

1. **Scroll-aware / runtime animations** -- entrance reveals, count-up
   numbers, typewriter text, scramble-reveal text, staggered
   per-character/word splits, and two SVG effects (drawn strokes,
   lightweight path morphing), all driven by one small
   `IntersectionObserver`-based runtime.

2. **Pure-Python CSS `@keyframes` animations** -- a full `@keyframes`
   builder (`Keyframes`) for expressing any animation, an
   `AnimationEngine` that turns a registered animation into a
   ready-to-use `animation:` style (plus matching
   `onanimationend=`-style hooks), and a small animate.css-style
   preset library so most components never need to hand-write a
   keyframe at all.

Neither system needs a CDN asset, a client adapter, or an
`App(...)` flag -- same "plain import" contract as the rest of
`nexoria.std` (contrast `nexoria.gsap`, which needs `App(gsap=True)`
and a browser GSAP bundle to drive tweens against the DOM from
server-described specs).

    from nexoria.std.animation import (
        # runtime / scroll-aware animations
        animation_runtime, reveal_styles, animate_in,
        animated_counter, typewriter_text, scramble_text, split_text,
        draw_svg, morph_svg,

        # CSS keyframes engine
        Keyframes, AnimationEngine, ANIMATION_ENGINE,
        PRESETS, PRESET_NAMES,
        animate, animated, keyframes_style,
    )

Render `animation_runtime()` and `reveal_styles()` once anywhere in
your root layout to enable the first system, then use the rest of
that group as needed throughout the page -- `split_text()` needs only
`reveal_styles()`/`animation_runtime()` (same as `animate_in()`,
which it's built on); everything else in that group needs
`animation_runtime()`.

For the CSS keyframes engine, define or use a preset and apply it via
`style=`:

    # 1. use a preset straight away
    el("h1", "Welcome!", style=animate("fade-in-up", duration="0.6s"))

    # 2. or the one-liner wrapper
    animated("Welcome!", name="fade-in-up", duration="0.6s", tag="h1")

    # 3. define your own
    ANIMATION_ENGINE.define("wiggle-box") \\
        .at(0, transform="rotate(0deg)") \\
        .at(50, transform="rotate(8deg)") \\
        .at(100, transform="rotate(0deg)")
    el("div", style=ANIMATION_ENGINE.style("wiggle-box", duration="1s", iteration_count="infinite"))

    # once per page, anywhere in your root layout:
    keyframes_style()

For declarative GSAP-powered tweens/timelines against a CDN-loaded
animation library instead, see `nexoria.gsap` (`App(gsap=True)`).
See `draw_svg`/`morph_svg`'s module docstring
(`nexoria.std.animation.svg`) for what `morph_svg()` can and can't
smoothly interpolate.
"""

from __future__ import annotations

# -- Scroll-aware / runtime animations --------------------------------
from .runtime import ANIMATION_RUNTIME_JS, animation_runtime
from .reveal import REVEAL_STYLES_CSS, reveal_styles, animate_in
from .text import animated_counter, typewriter_text
from .scramble import scramble_text
from .split import split_text
from .svg import draw_svg, morph_svg

# -- Pure-Python CSS @keyframes engine --------------------------------
from .keyframes import Keyframes
from .presets import PRESETS, PRESET_NAMES
from .engine import AnimationEngine, ANIMATION_ENGINE, animate, animated, keyframes_style

__all__ = [
    # runtime / scroll-aware animations
    "ANIMATION_RUNTIME_JS", "animation_runtime",
    "REVEAL_STYLES_CSS", "reveal_styles", "animate_in",
    "animated_counter", "typewriter_text",
    "scramble_text", "split_text",
    "draw_svg", "morph_svg",

    # CSS keyframes engine
    "Keyframes",
    "PRESETS", "PRESET_NAMES",
    "AnimationEngine", "ANIMATION_ENGINE",
    "animate", "animated", "keyframes_style",
]