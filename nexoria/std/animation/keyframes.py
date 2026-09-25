"""
nexoria.std.animation.keyframes
==================================
A plain-Python builder for real CSS `@keyframes` blocks -- full
keyframe support (any number of steps, any offset, any properties),
not just a handful of hard-coded `@keyframes` strings. This is what
`nexoria.std.premium.theme.PREMIUM_KEYFRAMES_CSS`,
`nexoria.std.cartoon.theme.CARTOON_KEYFRAMES_CSS` and
`nexoria.std.lib.theme.LIB_KEYFRAMES_CSS` are, generalized into a
reusable type any component (or app) can build its own animations
with -- see `nexoria.std.animation.engine.AnimationEngine` for the
higher-level piece that turns a `Keyframes` into ready-to-use
`animation:` styles.

No CDN asset, no client adapter, no `App(...)` flag -- pure Python,
same "plain import" contract as the rest of `nexoria.std` (compare
`nexoria.gsap`, which *does* need `App(gsap=True)` and a browser-side
GSAP bundle to animate real DOM nodes from server-described tweens;
`nexoria.std.animation` instead compiles straight to native CSS
animations, so there's nothing to load).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Union


def _format_offset(offset: Union[int, float, str]) -> str:
    """`0` -> `"0%"`, `50` -> `"50%"`, `12.5` -> `"12.5%"`; strings
    (`"from"`, `"to"`, `"0%"`, or a combined selector like
    `"0%, 100%"`) pass through untouched."""
    if isinstance(offset, str):
        return offset
    return f"{offset:g}%"


def _format_decls(props: dict) -> str:
    return " ".join(f"{k.replace('_', '-')}: {v};" for k, v in props.items())


@dataclass
class Keyframes:
    """
    One `@keyframes` animation, built either all at once or step by
    step:

        # all at once -- frames is a plain selector -> declaration
        # map, same convention as `nexoria.style.stylesheet.Stylesheet`
        Keyframes("fade-in-up", {
            "from": {"opacity": 0, "transform": "translateY(16px)"},
            "to": {"opacity": 1, "transform": "translateY(0)"},
        })

        # step by step -- offsets are auto-formatted to "N%"
        Keyframes("wiggle-box") \\
            .at(0, transform="rotate(0deg)") \\
            .at(50, transform="rotate(8deg)") \\
            .at(100, transform="rotate(0deg)")

        # multiple offsets sharing one frame -- pass the combined
        # selector as a string, same as raw CSS
        Keyframes("blink").at("0%, 100%", opacity=1).at("50%", opacity=0)

    `name` must be a valid CSS identifier -- it's what you pass to
    `AnimationEngine.style(name, ...)` / the `animation-name` CSS
    property.
    """
    name: str
    frames: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __init__(self, name: str, frames: Optional[dict] = None):
        self.name = name
        self.frames = dict(frames) if frames else {}

    def at(self, offset: Union[int, float, str], **props: Any) -> "Keyframes":
        """Add (or merge into) the frame at `offset`. Returns `self`
        so calls can be chained."""
        key = _format_offset(offset)
        self.frames[key] = {**self.frames.get(key, {}), **props}
        return self

    def to_css(self) -> str:
        """The raw `@keyframes name { ... }` block."""
        body = "\n".join(f"  {selector} {{ {_format_decls(props)} }}" for selector, props in self.frames.items())
        return f"@keyframes {self.name} {{\n{body}\n}}"

    def to_element(self):
        """A standalone `<style>` `Element` carrying just this
        animation -- most apps will instead register it on an
        `AnimationEngine` and render `engine.style_tag()` once, so
        every registered animation ships in a single `<style>`."""
        from ...core.element import el
        return el("style", self.to_css())
