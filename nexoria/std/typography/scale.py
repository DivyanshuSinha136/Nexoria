"""
nexoria.std.typography.scale
===============================
Fluid type scales: sizes that grow smoothly between a `min_viewport`
and a `max_viewport` via a single `clamp()` -- no media queries, no
JS `ResizeObserver`, just one CSS declaration per step (the
"fluid type" recipe popularized by utopia.fyi). This is what
`TypographyEngine` renders as `--nx-text-*` custom properties; build
one directly if you just want the scale without the font-registry
half of `nexoria.std.typography`.

    from nexoria.std.typography import TypeScale

    scale = TypeScale.modular()          # sensible eight-step default
    # or by hand:
    scale = TypeScale() \\
        .step("base", "1rem", "1.125rem") \\
        .step("lg",   "1.25rem", "1.5rem", line_height=1.3)

    el("h1", "Hi", style={"font-size": scale.clamp("lg")})
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Sequence, Union


def _rem(value: Union[int, float, str]) -> float:
    """Parse a CSS length into a bare rem float. Accepts a bare
    number (treated as rem already), an `"Nrem"` string, an `"Npx"`
    string (16px = 1rem), or an `"Nem"` string (treated as rem)."""
    if isinstance(value, (int, float)):
        return float(value)
    v = value.strip()
    if v.endswith("rem"):
        return float(v[:-3])
    if v.endswith("px"):
        return float(v[:-2]) / 16.0
    if v.endswith("em"):
        return float(v[:-2])
    return float(v)


def fluid_clamp(
    min_size: Union[int, float, str],
    max_size: Union[int, float, str],
    *,
    min_viewport: Union[int, float, str] = "20rem",
    max_viewport: Union[int, float, str] = "64rem",
) -> str:
    """
    A `clamp(MIN, PREFERRED, MAX)` expression that linearly
    interpolates between `min_size` (at `min_viewport`, ~320px by
    default) and `max_size` (at `max_viewport`, ~1024px by default),
    e.g. `fluid_clamp("1rem", "1.5rem")` ->
    `"clamp(1rem, 0.7143rem + 1.4286vw, 1.5rem)"`.

    Falls back to a plain fixed size (no `clamp()`) when there's no
    viewport range to interpolate across or the two sizes are equal.
    """
    min_r, max_r = _rem(min_size), _rem(max_size)
    min_vw, max_vw = _rem(min_viewport), _rem(max_viewport)
    if max_vw == min_vw or max_r == min_r:
        return f"{min_r:g}rem"
    slope = (max_r - min_r) / (max_vw - min_vw)
    intercept = min_r - slope * min_vw
    slope_vw = slope * 100  # rem-per-100vw -> a `vw` coefficient
    lo, hi = (min_r, max_r) if min_r <= max_r else (max_r, min_r)
    return f"clamp({lo:g}rem, {intercept:g}rem + {slope_vw:g}vw, {hi:g}rem)"


@dataclass
class TypeStep:
    """One named rung of a `TypeScale`. `min_size`/`max_size` are
    parsed by `fluid_clamp()` (rem/px/em strings or bare numbers);
    `line_height`/`weight`/`letter_spacing` are optional companions
    a component can pull alongside the size (see
    `TypographyEngine.style()`)."""
    name: str
    min_size: Union[int, float, str]
    max_size: Union[int, float, str]
    line_height: Optional[Union[int, float, str]] = None
    weight: Optional[Union[int, str]] = None
    letter_spacing: Optional[str] = None

    def clamp(self, *, min_viewport: str = "20rem", max_viewport: str = "64rem") -> str:
        return fluid_clamp(self.min_size, self.max_size, min_viewport=min_viewport, max_viewport=max_viewport)


DEFAULT_SCALE_STEPS: tuple = ("xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl")


@dataclass
class TypeScale:
    """
    A named collection of `TypeStep`s sharing one `min_viewport` /
    `max_viewport` fluid range.

        scale = TypeScale().step("base", "1rem", "1.125rem")
                            .step("lg", "1.25rem", "1.5rem")

    `min_viewport`/`max_viewport` default to `"20rem"`/`"64rem"`
    (~320px/~1024px -- small phone to a modest desktop window); pass
    your own to widen or narrow where the fluid growth happens.
    """
    min_viewport: Union[int, float, str] = "20rem"
    max_viewport: Union[int, float, str] = "64rem"
    steps: dict = field(default_factory=dict)

    def __init__(
        self,
        *,
        min_viewport: Union[int, float, str] = "20rem",
        max_viewport: Union[int, float, str] = "64rem",
        steps: Optional[Sequence[TypeStep]] = None,
    ):
        self.min_viewport = min_viewport
        self.max_viewport = max_viewport
        self.steps: dict[str, TypeStep] = {}
        for s in steps or ():
            self.steps[s.name] = s

    def step(
        self,
        name: str,
        min_size: Union[int, float, str],
        max_size: Union[int, float, str],
        *,
        line_height: Optional[Union[int, float, str]] = None,
        weight: Optional[Union[int, str]] = None,
        letter_spacing: Optional[str] = None,
    ) -> "TypeScale":
        """Add (or overwrite) a step and return `self`, so calls can
        be chained."""
        self.steps[name] = TypeStep(
            name, min_size, max_size,
            line_height=line_height, weight=weight, letter_spacing=letter_spacing,
        )
        return self

    @classmethod
    def modular(
        cls,
        *,
        base: Union[int, float] = 1.0,
        ratio_min: float = 1.125,
        ratio_max: float = 1.25,
        steps: Sequence[str] = DEFAULT_SCALE_STEPS,
        base_step: str = "base",
        min_viewport: Union[int, float, str] = "20rem",
        max_viewport: Union[int, float, str] = "64rem",
    ) -> "TypeScale":
        """
        Generate a full fluid scale from one base size and two
        modular ratios -- a gentler `ratio_min` at `min_viewport`, a
        bolder `ratio_max` at `max_viewport` -- so every step grows
        *both* in absolute size and in how aggressively it scales
        with the viewport (headings get noticeably more fluid than
        body text, without hand-tuning each one). Called with no
        arguments this is a sensible eight-step default
        (`xs`...`5xl`, `base` = 1rem) good enough to use immediately.
        """
        scale = cls(min_viewport=min_viewport, max_viewport=max_viewport)
        base_index = list(steps).index(base_step)
        for i, name in enumerate(steps):
            power = i - base_index
            mn = base * (ratio_min ** power)
            mx = base * (ratio_max ** power)
            scale.steps[name] = TypeStep(name, f"{mn:g}rem", f"{mx:g}rem")
        return scale

    def _resolve(self, name: str) -> TypeStep:
        try:
            return self.steps[name]
        except KeyError:
            raise KeyError(
                f"No type step named {name!r} registered on this TypeScale. "
                f"Call .step(name, ...) first, or use one of: {', '.join(sorted(self.steps))}."
            ) from None

    def clamp(self, name: str) -> str:
        """The raw `clamp(...)` (or fixed-size) `font-size` value for
        a registered step."""
        return self._resolve(name).clamp(min_viewport=self.min_viewport, max_viewport=self.max_viewport)

    def __contains__(self, name: str) -> bool:
        return name in self.steps

    def to_css_vars(self, *, prefix: str = "--nx-text-") -> str:
        """A `:root { --nx-text-<step>: clamp(...); ... }` block for
        every registered step (plus `--nx-leading-<step>` wherever a
        step sets `line_height`) -- render it once per page, or let
        `TypographyEngine.style_tag()` include it automatically."""
        lines = []
        for name, step in self.steps.items():
            lines.append(f"  {prefix}{name}: {step.clamp(min_viewport=self.min_viewport, max_viewport=self.max_viewport)};")
            if step.line_height is not None:
                lines.append(f"  --nx-leading-{name}: {step.line_height};")
        body = "\n".join(lines)
        return f":root {{\n{body}\n}}"
