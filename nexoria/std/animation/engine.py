"""
nexoria.std.animation.engine
===============================
`AnimationEngine` -- the piece that turns a registered `Keyframes`
into a ready-to-use `animation:` CSS value (and, when you want one,
the matching `onanimationend=`/`onanimationstart=`/`onanimationiteration=`
literal-HTML attributes -- see `props()`), plus a single `<style>`
tag carrying every `@keyframes` block a page actually uses.

Ships with a small animate.css-style preset library
(`nexoria.std.animation.presets`) already registered, and happily
takes custom `Keyframes` too, so it's the one place "proper"
animation work happens for `nexoria.std`: real, GPU-accelerated CSS
animations, declared once in Python, with full control over
duration/delay/easing/iteration-count/direction/fill-mode/play-state
-- no CDN, no client JS bundle, no `App(...)` flag (contrast
`nexoria.gsap`, which needs both to drive tweens against the DOM
from the browser).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence, Tuple, Union

from .keyframes import Keyframes
from .presets import PRESETS


@dataclass
class AnimationEngine:
    """
    `ANIMATION_ENGINE = AnimationEngine()` (module-level default,
    pre-loaded with every `nexoria.std.animation.presets.PRESETS`
    entry) is enough for most apps -- import it directly, or make
    your own with `AnimationEngine(presets=False)` for a clean slate.

        from nexoria.std.animation import ANIMATION_ENGINE, keyframes_style

        el("div", "Hi", style=ANIMATION_ENGINE.style("fade-in-up", duration="0.6s"))
        ...
        keyframes_style()   # once per page, in your root layout
    """
    _registry: dict = field(default_factory=dict)

    def __init__(self, *, presets: bool = True):
        self._registry: dict[str, Keyframes] = {}
        if presets:
            for short_name, kf in PRESETS.items():
                self.register(kf, as_name=short_name)

    # -- registration ------------------------------------------------

    def register(self, keyframes: Keyframes, *, as_name: Optional[str] = None) -> Keyframes:
        """Add an existing `Keyframes` under `as_name` (defaults to
        `keyframes.name`). Returns it unchanged, for chaining."""
        self._registry[as_name or keyframes.name] = keyframes
        return keyframes

    def define(self, name: str, frames: Optional[dict] = None) -> Keyframes:
        """
        Build, register and return a new `Keyframes` in one call:

            spin_slow = engine.define("spin-slow", {"from": {"transform": "rotate(0deg)"}, "to": {"transform": "rotate(360deg)"}})
            # or step by step:
            engine.define("wiggle-box").at(0, transform="rotate(0deg)").at(50, transform="rotate(8deg)").at(100, transform="rotate(0deg)")
        """
        kf = Keyframes(name, frames)
        self.register(kf)
        return kf

    def __contains__(self, name: str) -> bool:
        return name in self._registry

    @property
    def names(self) -> Tuple[str, ...]:
        """Every animation name currently registered (presets + custom)."""
        return tuple(self._registry.keys())

    def _resolve(self, name: str) -> Keyframes:
        try:
            return self._registry[name]
        except KeyError:
            raise KeyError(
                f"No animation named {name!r} registered on this AnimationEngine. "
                f"Call .define(name, ...) or .register(Keyframes(...)) first, or use "
                f"one of the built-in presets: {', '.join(sorted(self._registry))}."
            ) from None

    # -- consuming -----------------------------------------------------

    def css(
        self,
        name: str,
        *,
        duration: Union[str, float] = "1s",
        delay: Union[str, float] = "0s",
        timing_function: str = "ease",
        iteration_count: Union[str, int] = 1,
        direction: str = "normal",
        fill_mode: str = "none",
        play_state: str = "running",
    ) -> str:
        """The `animation` shorthand value for a registered
        animation, e.g. `"nx-anim-fade-in-up 0.6s ease 0s 1 normal both running"`.
        Numeric `duration`/`delay` are treated as seconds."""
        kf = self._resolve(name)
        dur = f"{duration}s" if isinstance(duration, (int, float)) else duration
        dly = f"{delay}s" if isinstance(delay, (int, float)) else delay
        return f"{kf.name} {dur} {timing_function} {dly} {iteration_count} {direction} {fill_mode} {play_state}"

    def style(self, name: str, **opts: Any) -> dict:
        """`{"animation": self.css(name, **opts)}` -- spread or merge
        straight into an `el(..., style={...})` dict."""
        return {"animation": self.css(name, **opts)}

    def combine(self, *specs: Union[str, Tuple[str, dict]]) -> dict:
        """
        Run several animations on the same element at once (CSS's
        comma-separated `animation` shorthand):

            engine.combine("fade-in", ("pulse", {"duration": "2s", "iteration_count": "infinite", "delay": "0.6s"}))

        Each spec is either a bare registered name (defaults) or a
        `(name, opts)` pair.
        """
        parts = []
        for spec in specs:
            if isinstance(spec, str):
                parts.append(self.css(spec))
            else:
                name, opts = spec
                parts.append(self.css(name, **opts))
        return {"animation": ", ".join(parts)}

    def props(
        self,
        name: str,
        *,
        on_start: Optional[str] = None,
        on_iteration: Optional[str] = None,
        on_end: Optional[str] = None,
        **opts: Any,
    ) -> dict:
        """
        `style` plus the literal `onanimationstart=`/`onanimationiteration=`/
        `onanimationend=` HTML attributes (raw JS strings, handled by
        the browser -- same trick `nexoria.std`'s hover states use,
        see `nexoria/std/__init__.py`; no server round-trip, no JS
        bundle). Spread the result straight into `el(...)`:

            el("div", "Done!", **engine.props("fade-in-up", duration="0.6s", on_end="this.classList.add('settled')"))
        """
        result: dict[str, Any] = {"style": self.style(name, **opts)}
        if on_start:
            result["onanimationstart"] = on_start
        if on_iteration:
            result["onanimationiteration"] = on_iteration
        if on_end:
            result["onanimationend"] = on_end
        return result

    def style_tag(self):
        """
        A single `<style>` `Element` carrying every `@keyframes`
        block currently registered on this engine (presets you
        actually reference are cheap to include unconditionally --
        unused `@keyframes` rules cost nothing at runtime). Render it
        once, anywhere in your root layout, before any element uses
        `.style()`/`.props()`/`.combine()`.
        """
        from ...core.element import el
        css = "\n\n".join(kf.to_css() for kf in self._registry.values())
        return el("style", css)


ANIMATION_ENGINE = AnimationEngine()


def animate(name: str, **opts: Any) -> dict:
    """Module-level shorthand for `ANIMATION_ENGINE.style(name, **opts)`."""
    return ANIMATION_ENGINE.style(name, **opts)


def animated(
    *children: Any,
    name: str,
    tag: str = "div",
    class_: Optional[str] = None,
    style: Optional[dict] = None,
    on_start: Optional[str] = None,
    on_iteration: Optional[str] = None,
    on_end: Optional[str] = None,
    **opts: Any,
):
    """
    The fastest path to an animated chunk of markup -- wraps
    `children` in `tag` (a `<div>` by default) with the animation
    already applied:

        animated("Welcome!", name="fade-in-up", duration="0.6s", tag="h1")
        animated(icon, name="spin", duration="1.2s", iteration_count="infinite")

    Anything not consumed by the animation (`class_`, extra `style`,
    or any other `el()` prop) passes straight through. Uses the
    shared `ANIMATION_ENGINE` -- register custom animations there
    first if `name` isn't one of `nexoria.std.animation.presets.PRESETS`.
    """
    from ...core.element import el
    props = ANIMATION_ENGINE.props(name, on_start=on_start, on_iteration=on_iteration, on_end=on_end, **opts)
    merged_style = {**(style or {}), **props.pop("style")}
    return el(tag, *children, style=merged_style, class_=class_, **props)


def keyframes_style():
    """`ANIMATION_ENGINE.style_tag()` -- render once per page."""
    return ANIMATION_ENGINE.style_tag()
