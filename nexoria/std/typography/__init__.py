"""
nexoria.std.typography
=========================
A custom typography engine for `nexoria.std`: register your own,
self-hosted `@font-face` fonts (variable fonts included) and a fluid
`clamp()`-based type scale, then consume both as plain `style=` dicts
or `--nx-font-*`/`--nx-text-*` CSS custom properties -- no Google
Fonts `<link>`, no CDN, no `App(...)` flag, same "plain import"
contract as the rest of `nexoria.std`.

Two pieces, usable separately or together:

1. **Fonts** -- `FontFace`/`FontSource` build real `@font-face`
   rules from your own font files (self-hosted `.woff2`/`.woff`/
   `.ttf`/etc., including a single variable-font file covering a
   whole weight/width/slant range via `weight="100 900"`).

2. **Scale** -- `TypeStep`/`TypeScale` build a fluid type scale: each
   step is a `clamp(min, preferred, max)` that grows smoothly between
   a `min_viewport` and `max_viewport`, no media queries needed.
   `TypeScale.modular()` generates a full eight-step scale from one
   base size and two modular ratios.

`TypographyEngine` (and the shared `TYPOGRAPHY_ENGINE` instance) ties
both together: register fonts and named font "stacks" (a custom
family plus its system fallback chain), then pull a ready `style=`
dict for any step/stack pairing via `style()`, wrap text in one call
via `text()`, and render everything -- every `@font-face`, every
`--nx-text-*`/`--nx-leading-*`, every `--nx-font-*` -- in a single
`<style>` tag with `style_tag()`.

    from nexoria.std.typography import (
        FontFace, FontSource,
        TypeStep, TypeScale, fluid_clamp,
        TypographyEngine, TYPOGRAPHY_ENGINE,
        font_face, font_stack, type_style, styled_text, typography_style_tag,
    )

    # register a custom font and a named stack
    font_face("Space Grotesk", "/static/fonts/SpaceGrotesk-Var.woff2", weight="300 700")
    font_stack("display", "Space Grotesk", fallback="-apple-system, sans-serif")

    # use it
    el("h1", "Nexoria", style=type_style("4xl", family="display", weight=700))
    styled_text("Ship faster.", step="lg", family="display", tag="p")

    # once per page, anywhere in your root layout:
    typography_style_tag()

Prefer your own registry over the shared one? `TypographyEngine()`
(optionally with `scale=TypeScale.modular(base=1.125, ...)`) gives
you a clean slate with the same API.
"""

from __future__ import annotations

from .fontface import FontFace, FontSource
from .scale import TypeStep, TypeScale, fluid_clamp, DEFAULT_SCALE_STEPS
from .engine import (
    TypographyEngine, TYPOGRAPHY_ENGINE,
    font_face, font_stack, type_style, styled_text, typography_style_tag,
)

__all__ = [
    "FontFace", "FontSource",
    "TypeStep", "TypeScale", "fluid_clamp", "DEFAULT_SCALE_STEPS",
    "TypographyEngine", "TYPOGRAPHY_ENGINE",
    "font_face", "font_stack", "type_style", "styled_text", "typography_style_tag",
]
