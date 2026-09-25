# `nexoria.std.typography`

> A typography engine: self-hosted `@font-face` fonts (variable fonts included) and a fluid, `clamp()`-based type scale.

| | |
|---|---|
| **Import** | `from nexoria.std.typography import font_face, font_stack, type_style, styled_text, typography_style_tag, TypographyEngine, TypeScale, …` |
| **Needs** | `typography_style_tag()` once per page (emits `@font-face` blocks, `--nx-text-*`/`--nx-leading-*` and `--nx-font-*` variables) |

```python
from nexoria.std.typography import font_face, font_stack, styled_text, type_style, typography_style_tag

font_face("Inter", "/static/Inter.woff2", weight="100 900")        # variable font
font_face("Inter", "/static/Inter-Italic.woff2", style="italic", weight="100 900")
font_stack("body", "Inter", fallback="system-ui, sans-serif")       # → --nx-font-body

el("div",
   typography_style_tag(),                                          # once per page
   styled_text("Fluid headline", step="3xl", tag="h1", family="body", weight=700),
   el("p", "Body copy", style=type_style("base")))
```

- **Type scale.** The default `TypeScale.modular()` generates steps `xs, sm, base, lg, xl, 2xl, 3xl, 4xl, 5xl`, interpolating each size between a gentler ratio (1.125) at the minimum viewport (20 rem) and a bolder one (1.25) at the maximum (64 rem). `fluid_clamp("1rem", "1.5rem")` builds a single `clamp()`. Add or override steps with `.step(name, min_size, max_size, line_height=, weight=, letter_spacing=)`.
- **Fonts.** `FontFace` builds one `@font-face`; `.source(url, format=, tech=)` adds fallback formats (format guessed from `.woff2/.woff/.ttf/.otf/.eot`). `display` defaults to `swap`. Supports `weight` ranges for variable fonts, `stretch`, and `unicode_range`.
- **Module-level shorthands** operate on the default `TYPOGRAPHY_ENGINE`; create your own `TypographyEngine(scale=…)` for isolation.
- Output is consumed either as `style=` dicts (`type_style`) or as CSS variables.

## API reference

### Classes

#### `class FontFace(family: str, url: Optional[str] = None, *, format: Optional[str] = None, weight: Union[str, int] = 'normal', style: str = 'normal', display: str = 'swap', stretch: Optional[str] = None, unicode_range: Optional[str] = None)`

One `@font-face` rule, built either all at once or step by step.

Register more than one `FontFace` under the same `family` (one per weight/style combination) to build out a full custom family -- `TypographyEngine.font_face()` collects every one you define into a single `style_tag()`.

- **`.source(url: str, *, format: Optional[str] = None, tech: Optional[str] = None) -> 'FontFace'`** — Add another `src:` entry (a fallback format for this same weight/style) and return `self`, so calls can be chained.
- **`.to_css() -> str`** — The raw `@font-face { ... }` block.
- **`.to_element()`** — A standalone `<style>` `Element` carrying just this `@font-face` rule -- most apps will instead register it on a `TypographyEngine` and render `engine.style_tag()` once, so every registered font ships in a single `<style>`.

#### `class FontSource(url: str, format: Optional[str] = None, tech: Optional[str] = None) -> None`

One entry in a `@font-face`'s `src:` list. `format` is guessed from the file extension when omitted; `tech` is the optional CSS Fonts 4 `tech(...)` hint (e.g. `"variations"`, `"color-COLRv1"`) for browsers that support font-format negotiation.

- **`.to_src() -> str`**

#### `class TypeStep(name: str, min_size: Union[int, float, str], max_size: Union[int, float, str], line_height: Optional[Union[int, float, str]] = None, weight: Optional[Union[int, str]] = None, letter_spacing: Optional[str] = None) -> None`

One named rung of a `TypeScale`. `min_size`/`max_size` are parsed by `fluid_clamp()` (rem/px/em strings or bare numbers); `line_height`/`weight`/`letter_spacing` are optional companions a component can pull alongside the size (see `TypographyEngine.style()`).

- **`.clamp(*, min_viewport: str = '20rem', max_viewport: str = '64rem') -> str`**

#### `class TypeScale(*, min_viewport: Union[int, float, str] = '20rem', max_viewport: Union[int, float, str] = '64rem', steps: Optional[Sequence[TypeStep]] = None)`

A named collection of `TypeStep`s sharing one `min_viewport` / `max_viewport` fluid range.

`min_viewport`/`max_viewport` default to `"20rem"`/`"64rem"` (~320px/~1024px -- small phone to a modest desktop window); pass your own to widen or narrow where the fluid growth happens.

- **`.clamp(name: str) -> str`** — The raw `clamp(...)` (or fixed-size) `font-size` value for a registered step.
- **`.modular(*, base: Union[int, float] = 1.0, ratio_min: float = 1.125, ratio_max: float = 1.25, steps: Sequence[str] = ('xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl'), base_step: str = 'base', min_viewport: Union[int, float, str] = '20rem', max_viewport: Union[int, float, str] = '64rem') -> 'TypeScale'`** — Generate a full fluid scale from one base size and two modular ratios -- a gentler `ratio_min` at `min_viewport`, a bolder `ratio_max` at `max_viewport` -- so every step grows *both* in absolute size and in how aggressively it scales with the viewport (headings get noticeably more fluid than body te…
- **`.step(name: str, min_size: Union[int, float, str], max_size: Union[int, float, str], *, line_height: Optional[Union[int, float, str]] = None, weight: Optional[Union[int, str]] = None, letter_spacing: Optional[str] = None) -> 'TypeScale'`** — Add (or overwrite) a step and return `self`, so calls can be chained.
- **`.to_css_vars(*, prefix: str = '--nx-text-') -> str`** — A `:root { --nx-text-<step>: clamp(...); ... }` block for every registered step (plus `--nx-leading-<step>` wherever a step sets `line_height`) -- render it once per page, or let `TypographyEngine.style_tag()` include it automatically.

#### `class TypographyEngine(*, scale: Optional[TypeScale] = None)`

`TYPOGRAPHY_ENGINE = TypographyEngine()` (module-level default, pre-loaded with a sensible fluid `TypeScale.modular()`) is enough to start using the type scale immediately -- register your own fonts on it as you get them.

Make your own with `TypographyEngine(scale=my_scale)` for full control over the fluid range, or keep the default and just add steps with `.step(...)`.

- **`.family(name: str) -> str`** — The assembled `font-family` value for a registered stack (or, if `name` isn't a registered stack, `name` returned as-is -- so passing a raw CSS family list through `style()` works too).
- **`.font_face(family: str, url: Optional[str] = None, *, format: Optional[str] = None, weight: Union[str, int] = 'normal', style: str = 'normal', display: str = 'swap', stretch: Optional[str] = None, unicode_range: Optional[str] = None) -> FontFace`** — Register a new custom font file and return the `FontFace` -- chain `.source(url, format=...)` on it for extra fallback formats, or call `font_face()` again with the same `family` for another weight/style (e.g. a separate bold cut):
- **`.stack(name: str, *families: str, fallback: Optional[str] = 'sans-serif') -> str`** — Define a named font stack token -- your registered custom family plus a system fallback chain, exposed as a `--nx-font-<name>` CSS variable and usable by name from `style()`/`text()`:
- **`.step(name: str, min_size: Union[int, float, str], max_size: Union[int, float, str], **opts: Any) -> 'TypographyEngine'`** — Shorthand for `self.scale.step(...)`, returning `self` so calls can be chained.
- **`.style(step: str, *, family: Optional[str] = None, weight: Optional[Union[int, str]] = None, letter_spacing: Optional[str] = None) -> dict`** — A `style=` dict for a registered type step -- `font-size` (the fluid `clamp()`), plus `line-height`/`font-weight`/ `letter-spacing` wherever the step (or an override passed here) sets one, plus `font-family` when `family` names a registered `.stack(...)` (or any raw CSS family list):
- **`.style_tag()`** — A single `<style>` `Element` carrying every registered `@font-face` block, the type scale's `--nx-text-*`/ `--nx-leading-*` custom properties, and every `--nx-font-*` stack token. Render it once, anywhere in your root layout, before any element uses `.style()`/`.text()`/a `--nx-font-*` or `--nx-text…
- **`.text(*children: Any, step: str = 'base', family: Optional[str] = None, weight: Optional[Union[int, str]] = None, letter_spacing: Optional[str] = None, tag: str = 'p', class_: Optional[str] = None, style: Optional[dict] = None, **opts: Any)`** — The fastest path to a piece of styled text -- wraps `children` in `tag` (a `<p>` by default) with `style(...)` already applied:

### Functions

#### `fluid_clamp(min_size: Union[int, float, str], max_size: Union[int, float, str], *, min_viewport: Union[int, float, str] = '20rem', max_viewport: Union[int, float, str] = '64rem') -> str`

A `clamp(MIN, PREFERRED, MAX)` expression that linearly interpolates between `min_size` (at `min_viewport`, ~320px by default) and `max_size` (at `max_viewport`, ~1024px by default), e.g. `fluid_clamp("1rem", "1.5rem")` -> `"clamp(1rem, 0.7143rem + 1.4286vw, 1.5rem)"`.

Falls back to a plain fixed size (no `clamp()`) when there's no viewport range to interpolate across or the two sizes are equal.

#### `font_face(family: str, url: Optional[str] = None, **opts: Any) -> FontFace`

Module-level shorthand for `TYPOGRAPHY_ENGINE.font_face(...)`.

#### `font_stack(name: str, *families: str, fallback: Optional[str] = 'sans-serif') -> str`

Module-level shorthand for `TYPOGRAPHY_ENGINE.stack(...)`.

#### `type_style(step: str, **opts: Any) -> dict`

Module-level shorthand for `TYPOGRAPHY_ENGINE.style(...)`.

#### `styled_text(*children: Any, **opts: Any)`

Module-level shorthand for `TYPOGRAPHY_ENGINE.text(...)`.

#### `typography_style_tag()`

`TYPOGRAPHY_ENGINE.style_tag()` -- render once per page.

### Constants

| Name | Value |
|---|---|
| `DEFAULT_SCALE_STEPS` | `('xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl')` |
| `TYPOGRAPHY_ENGINE` | `TypographyEngine(_faces=[], _stacks={}, scale=TypeScale(min_viewport='20rem', max_viewport='64rem', steps={'xs': TypeStep(name='xs', min_size='0.790123rem', max_size='0.64rem', line_height=None, weight=None, letter_spacing=None), 'sm': TypeStep(name='sm', min_size='0.888889rem', max_size='0.8rem', line_height=None, weight=None, letter_spacing=None), 'base': TypeStep(name='base', min_size='1rem', max_size='1rem', l…` |
