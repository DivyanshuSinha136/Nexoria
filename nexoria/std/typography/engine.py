"""
nexoria.std.typography.engine
================================
`TypographyEngine` -- the piece that turns registered `FontFace`s and
a `TypeScale` into ready-to-use `font-family`/`font-size` `style=`
dicts (see `style()`/`text()`), plus a single `<style>` tag carrying
every `@font-face` block and `:root` custom property a page actually
needs. It's the one place "proper" typography work happens for
`nexoria.std`: real, self-hosted `@font-face` fonts and a fluid type
scale, declared once in Python -- no Google Fonts `<link>`, no CDN,
no `App(...)` flag.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Union

from .fontface import FontFace
from .scale import TypeScale


@dataclass
class TypographyEngine:
    """
    `TYPOGRAPHY_ENGINE = TypographyEngine()` (module-level default,
    pre-loaded with a sensible fluid `TypeScale.modular()`) is enough
    to start using the type scale immediately -- register your own
    fonts on it as you get them:

        from nexoria.std.typography import TYPOGRAPHY_ENGINE, typography_style_tag

        TYPOGRAPHY_ENGINE.font_face("Inter", "/static/fonts/Inter-Var.woff2", weight="100 900")
        TYPOGRAPHY_ENGINE.stack("body", "Inter", fallback="-apple-system, sans-serif")

        el("p", "Hi", style=TYPOGRAPHY_ENGINE.style("base", family="body"))
        ...
        typography_style_tag()   # once per page, in your root layout

    Make your own with `TypographyEngine(scale=my_scale)` for full
    control over the fluid range, or keep the default and just add
    steps with `.step(...)`.
    """
    _faces: list = field(default_factory=list)
    _stacks: dict = field(default_factory=dict)
    scale: TypeScale = field(default_factory=TypeScale.modular)

    def __init__(self, *, scale: Optional[TypeScale] = None):
        self._faces: list[FontFace] = []
        self._stacks: dict[str, str] = {}
        self.scale = scale if scale is not None else TypeScale.modular()

    # -- fonts -----------------------------------------------------------

    def font_face(
        self,
        family: str,
        url: Optional[str] = None,
        *,
        format: Optional[str] = None,
        weight: Union[str, int] = "normal",
        style: str = "normal",
        display: str = "swap",
        stretch: Optional[str] = None,
        unicode_range: Optional[str] = None,
    ) -> FontFace:
        """
        Register a new custom font file and return the `FontFace` --
        chain `.source(url, format=...)` on it for extra fallback
        formats, or call `font_face()` again with the same `family`
        for another weight/style (e.g. a separate bold cut):

            engine.font_face("Space Grotesk", "/static/fonts/SpaceGrotesk-Regular.woff2")
            engine.font_face("Space Grotesk", "/static/fonts/SpaceGrotesk-Bold.woff2", weight="700")
        """
        face = FontFace(
            family, url, format=format, weight=weight, style=style,
            display=display, stretch=stretch, unicode_range=unicode_range,
        )
        self._faces.append(face)
        return face

    def stack(self, name: str, *families: str, fallback: Optional[str] = "sans-serif") -> str:
        """
        Define a named font stack token -- your registered custom
        family plus a system fallback chain, exposed as a
        `--nx-font-<name>` CSS variable and usable by name from
        `style()`/`text()`:

            engine.stack("display", "Space Grotesk", fallback="-apple-system, sans-serif")
            engine.stack("body", "Inter", "system-ui", fallback="sans-serif")

        Returns the assembled `font-family` CSS value.
        """
        quoted = [f'"{f}"' if " " in f and not f.startswith('"') else f for f in families]
        parts = quoted + ([fallback] if fallback else [])
        value = ", ".join(parts)
        self._stacks[name] = value
        return value

    def family(self, name: str) -> str:
        """The assembled `font-family` value for a registered stack
        (or, if `name` isn't a registered stack, `name` returned
        as-is -- so passing a raw CSS family list through `style()`
        works too)."""
        return self._stacks.get(name, name)

    @property
    def stack_names(self) -> tuple:
        return tuple(self._stacks.keys())

    # -- scale -------------------------------------------------------------

    def step(
        self,
        name: str,
        min_size: Union[int, float, str],
        max_size: Union[int, float, str],
        **opts: Any,
    ) -> "TypographyEngine":
        """Shorthand for `self.scale.step(...)`, returning `self` so
        calls can be chained."""
        self.scale.step(name, min_size, max_size, **opts)
        return self

    # -- consuming ------------------------------------------------------------

    def style(
        self,
        step: str,
        *,
        family: Optional[str] = None,
        weight: Optional[Union[int, str]] = None,
        letter_spacing: Optional[str] = None,
    ) -> dict:
        """
        A `style=` dict for a registered type step -- `font-size`
        (the fluid `clamp()`), plus `line-height`/`font-weight`/
        `letter-spacing` wherever the step (or an override passed
        here) sets one, plus `font-family` when `family` names a
        registered `.stack(...)` (or any raw CSS family list):

            el("h1", "Hi", style=engine.style("3xl", family="display"))
        """
        s = self.scale._resolve(step)
        out: dict[str, Any] = {"font-size": self.scale.clamp(step)}
        if s.line_height is not None:
            out["line-height"] = s.line_height
        ls = letter_spacing if letter_spacing is not None else s.letter_spacing
        if ls is not None:
            out["letter-spacing"] = ls
        w = weight if weight is not None else s.weight
        if w is not None:
            out["font-weight"] = w
        if family is not None:
            out["font-family"] = self.family(family)
        return out

    def text(
        self,
        *children: Any,
        step: str = "base",
        family: Optional[str] = None,
        weight: Optional[Union[int, str]] = None,
        letter_spacing: Optional[str] = None,
        tag: str = "p",
        class_: Optional[str] = None,
        style: Optional[dict] = None,
        **opts: Any,
    ):
        """
        The fastest path to a piece of styled text -- wraps
        `children` in `tag` (a `<p>` by default) with `style(...)`
        already applied:

            engine.text("Nexoria", step="4xl", family="display", tag="h1", weight=700)

        Anything not consumed here (`class_`, extra `style`, or any
        other `el()` prop) passes straight through.
        """
        from ...core.element import el
        merged = {**self.style(step, family=family, weight=weight, letter_spacing=letter_spacing), **(style or {})}
        return el(tag, *children, style=merged, class_=class_, **opts)

    def style_tag(self):
        """
        A single `<style>` `Element` carrying every registered
        `@font-face` block, the type scale's `--nx-text-*`/
        `--nx-leading-*` custom properties, and every `--nx-font-*`
        stack token. Render it once, anywhere in your root layout,
        before any element uses `.style()`/`.text()`/a `--nx-font-*`
        or `--nx-text-*` variable.
        """
        from ...core.element import el
        blocks = [face.to_css() for face in self._faces]
        blocks.append(self.scale.to_css_vars())
        if self._stacks:
            body = "\n".join(f"  --nx-font-{name}: {value};" for name, value in self._stacks.items())
            blocks.append(f":root {{\n{body}\n}}")
        return el("style", "\n\n".join(blocks))


TYPOGRAPHY_ENGINE = TypographyEngine()


def font_face(family: str, url: Optional[str] = None, **opts: Any) -> FontFace:
    """Module-level shorthand for `TYPOGRAPHY_ENGINE.font_face(...)`."""
    return TYPOGRAPHY_ENGINE.font_face(family, url, **opts)


def font_stack(name: str, *families: str, fallback: Optional[str] = "sans-serif") -> str:
    """Module-level shorthand for `TYPOGRAPHY_ENGINE.stack(...)`."""
    return TYPOGRAPHY_ENGINE.stack(name, *families, fallback=fallback)


def type_style(step: str, **opts: Any) -> dict:
    """Module-level shorthand for `TYPOGRAPHY_ENGINE.style(...)`."""
    return TYPOGRAPHY_ENGINE.style(step, **opts)


def styled_text(*children: Any, **opts: Any):
    """Module-level shorthand for `TYPOGRAPHY_ENGINE.text(...)`."""
    return TYPOGRAPHY_ENGINE.text(*children, **opts)


def typography_style_tag():
    """`TYPOGRAPHY_ENGINE.style_tag()` -- render once per page."""
    return TYPOGRAPHY_ENGINE.style_tag()
