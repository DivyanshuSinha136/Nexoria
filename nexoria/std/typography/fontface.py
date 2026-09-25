"""
nexoria.std.typography.fontface
==================================
A plain-Python builder for real CSS `@font-face` rules -- the piece
that lets you self-host and register *custom* font files (variable
fonts included) instead of reaching for a Google Fonts `<link>` or a
CDN. This is the low-level type any component (or app) registers
fonts with -- see `nexoria.std.typography.engine.TypographyEngine`
for the higher-level piece that turns a registered `FontFace` into
ready-to-use `font-family`/CSS-variable tokens.

    from nexoria.std.typography import FontFace

    inter = FontFace("Inter", "/static/fonts/Inter-Var.woff2",
                      weight="100 900", style="normal") \\
        .source("/static/fonts/Inter-Var.woff", format="woff")

    el("style", inter.to_css())   # or hand it to a TypographyEngine

`weight`/`style` accept a range (`"100 900"` / `"oblique 0deg 12deg"`)
for a single variable-font file that covers a whole axis -- no need
to register one `FontFace` per static weight.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Union

_FORMAT_BY_EXT = {
    ".woff2": "woff2",
    ".woff": "woff",
    ".ttf": "truetype",
    ".otf": "opentype",
    ".eot": "embedded-opentype",
    ".svg": "svg",
}


def _guess_format(url: str) -> Optional[str]:
    """Infer a `format("...")` hint from a file extension so most
    calls don't need to pass `format=` explicitly."""
    lower = url.lower().split("?")[0].split("#")[0]
    for ext, fmt in _FORMAT_BY_EXT.items():
        if lower.endswith(ext):
            return fmt
    return None


@dataclass
class FontSource:
    """One entry in a `@font-face`'s `src:` list. `format` is
    guessed from the file extension when omitted; `tech` is the
    optional CSS Fonts 4 `tech(...)` hint (e.g. `"variations"`,
    `"color-COLRv1"`) for browsers that support font-format
    negotiation."""
    url: str
    format: Optional[str] = None
    tech: Optional[str] = None

    def to_src(self) -> str:
        fmt = self.format or _guess_format(self.url)
        part = f'url("{self.url}")'
        if fmt:
            part += f' format("{fmt}")'
        if self.tech:
            part += f" tech({self.tech})"
        return part


@dataclass
class FontFace:
    """
    One `@font-face` rule, built either all at once or step by step:

        # all at once
        FontFace("Inter", "/static/fonts/Inter-Var.woff2", weight="100 900")

        # step by step -- extra sources are fallback formats for the
        # *same* family/weight/style (the browser picks the first it
        # understands), not separate weights
        FontFace("Space Grotesk", weight="700", style="normal") \\
            .source("/static/fonts/SpaceGrotesk-Bold.woff2") \\
            .source("/static/fonts/SpaceGrotesk-Bold.woff", format="woff")

    Register more than one `FontFace` under the same `family` (one
    per weight/style combination) to build out a full custom family
    -- `TypographyEngine.font_face()` collects every one you define
    into a single `style_tag()`.
    """
    family: str
    sources: list = field(default_factory=list)
    weight: Union[str, int] = "normal"
    style: str = "normal"
    display: str = "swap"
    stretch: Optional[str] = None
    unicode_range: Optional[str] = None

    def __init__(
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
    ):
        self.family = family
        self.sources: list[FontSource] = []
        self.weight = weight
        self.style = style
        self.display = display
        self.stretch = stretch
        self.unicode_range = unicode_range
        if url:
            self.source(url, format=format)

    def source(self, url: str, *, format: Optional[str] = None, tech: Optional[str] = None) -> "FontFace":
        """Add another `src:` entry (a fallback format for this same
        weight/style) and return `self`, so calls can be chained."""
        self.sources.append(FontSource(url, format=format, tech=tech))
        return self

    def to_css(self) -> str:
        """The raw `@font-face { ... }` block."""
        if not self.sources:
            raise ValueError(
                f"FontFace {self.family!r} has no sources -- call .source(url) "
                f"(or pass url= to FontFace(...)) at least once."
            )
        src = ",\n       ".join(s.to_src() for s in self.sources)
        decls = [
            f'  font-family: "{self.family}";',
            f"  src: {src};",
            f"  font-weight: {self.weight};",
            f"  font-style: {self.style};",
            f"  font-display: {self.display};",
        ]
        if self.stretch:
            decls.append(f"  font-stretch: {self.stretch};")
        if self.unicode_range:
            decls.append(f"  unicode-range: {self.unicode_range};")
        body = "\n".join(decls)
        return f"@font-face {{\n{body}\n}}"

    def to_element(self):
        """A standalone `<style>` `Element` carrying just this
        `@font-face` rule -- most apps will instead register it on a
        `TypographyEngine` and render `engine.style_tag()` once, so
        every registered font ships in a single `<style>`."""
        from ...core.element import el
        return el("style", self.to_css())
