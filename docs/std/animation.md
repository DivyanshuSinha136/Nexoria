# `nexoria.std.animation`

> Two animation systems in one package: a **scroll-aware runtime** (reveals, counters, text effects, SVG draw/morph) and a **pure-Python CSS `@keyframes` engine** with animate.css-style presets. No dependencies.

| | |
|---|---|
| **Import** | `from nexoria.std.animation import animate_in, animated, animation_runtime, …` |
| **Needs** | Runtime part: `animation_runtime()` (+ `reveal_styles()` for reveals/`split_text`) once per page. Keyframes part: `keyframes_style()` once per page. |
| **Not the same as** | [`nexoria.gsap`](../gsap.md) (real GSAP via CDN, needs `App(gsap=True)`) |

## Part 1 — scroll-aware runtime

```python
from nexoria.std.animation import (animation_runtime, reveal_styles, animate_in, animated_counter,
                                   typewriter_text, scramble_text, split_text, draw_svg, morph_svg)

el("div",
   animation_runtime(), reveal_styles(),                        # once per page
   animate_in(el("h2", "Welcome"), effect="fade-up", delay=150),
   animated_counter(48200, prefix="$", suffix=" raised"),
   typewriter_text("Write your whole stack in Python.", speed=35),
   scramble_text("DECRYPTING...", speed=30, reveal_delay=40),
   split_text("Ship a real website", by="words", effect="fade-up", stagger=80),
   morph_svg("M10 80 L50 10 L90 80 Z", "M10 50 L50 90 L90 50 Z", trigger="hover"))
```

| Function | Behaviour |
|---|---|
| `animate_in(*children, effect, duration=600, delay=0, once=True)` | Reveals children when scrolled into view (`IntersectionObserver`) |
| `animated_counter(target, prefix, suffix, decimals, duration)` | Counts up with ease-out; final value is static text if JS never runs |
| `typewriter_text(text, speed)` | Types on scroll-in; full text present as fallback |
| `scramble_text(text, chars, speed, reveal_delay)` | Random characters settle into the text |
| `split_text(text, by="chars"|"words", effect, stagger, duration)` | Splits server-side into one span per unit; built on the reveal system |
| `draw_svg(svg, duration, delay, stagger)` | Animated stroke reveal. Hyphenated SVG attributes like `stroke-width` must go through `style=` |
| `morph_svg(path_a, path_b, …, trigger="hover")` | **Lightweight coordinate lerp**, not arbitrary-topology morphing. Smooth only when both paths have the same number of numeric coordinates; otherwise it snaps to the target. |

## Part 2 — CSS `@keyframes` engine

```python
from nexoria.std.animation import animate, animated, keyframes_style, ANIMATION_ENGINE, Keyframes

el("h1", "Welcome!", style=animate("fade-in-up", duration="0.6s"))     # a preset → style dict
animated("Welcome!", name="fade-in-up", duration="0.6s", tag="h1")     # or a wrapper

ANIMATION_ENGINE.define("wiggle-box").at(0, transform="rotate(0deg)").at(50, transform="rotate(8deg)").at(100, transform="rotate(0deg)")
el("div", style=ANIMATION_ENGINE.style("wiggle-box", duration="1s", iteration_count="infinite"))

keyframes_style()      # once per page: one <style> with every @keyframes registered
```

- `Keyframes(name, frames=None)` builds a block all at once (`{"from": {...}, "to": {...}}`) or with `.at(offset, **props)`.
- `AnimationEngine(presets=True)`: `register`, `define`, `names`, `css` (the `animation:` shorthand), `style`, `combine(*specs)` (several animations on one element), `props(name, on_start=, on_iteration=, on_end=, **opts)` (adds literal `onanimation*` attributes), `style_tag()`.
- `ANIMATION_ENGINE` is the default instance, preloaded with `PRESETS`. **21 presets:** `fade-in`, `fade-out`, `fade-in-up`, `fade-in-down`, `fade-in-left`, `fade-in-right`, `slide-in-up`, `slide-in-down`, `slide-in-left`, `slide-in-right`, `zoom-in`, `zoom-out`, `flip-in`, `spin`, `pulse`, `ping`, `bounce`, `shake`, `wobble`, `heartbeat`, `rubber-band`.
- Everything compiles to native CSS animations, independent of the observer runtime.

## API reference

### Classes

#### `class Keyframes(name: str, frames: Optional[dict] = None)`

One `@keyframes` animation, built either all at once or step by step.

`name` must be a valid CSS identifier -- it's what you pass to `AnimationEngine.style(name, ...)` / the `animation-name` CSS property.

- **`.at(offset: Union[int, float, str], **props: Any) -> 'Keyframes'`** — Add (or merge into) the frame at `offset`. Returns `self` so calls can be chained.
- **`.to_css() -> str`** — The raw `@keyframes name { ... }` block.
- **`.to_element()`** — A standalone `<style>` `Element` carrying just this animation -- most apps will instead register it on an `AnimationEngine` and render `engine.style_tag()` once, so every registered animation ships in a single `<style>`.

#### `class AnimationEngine(*, presets: bool = True)`

`ANIMATION_ENGINE = AnimationEngine()` (module-level default, pre-loaded with every `nexoria.std.animation.presets.PRESETS` entry) is enough for most apps -- import it directly, or make your own with `AnimationEngine(presets=False)` for a clean slate.

- **`.combine(*specs: Union[str, Tuple[str, dict]]) -> dict`** — Run several animations on the same element at once (CSS's comma-separated `animation` shorthand):
- **`.css(name: str, *, duration: Union[str, float] = '1s', delay: Union[str, float] = '0s', timing_function: str = 'ease', iteration_count: Union[str, int] = 1, direction: str = 'normal', fill_mode: str = 'none', play_state: str = 'running') -> str`** — The `animation` shorthand value for a registered animation, e.g. `"nx-anim-fade-in-up 0.6s ease 0s 1 normal both running"`. Numeric `duration`/`delay` are treated as seconds.
- **`.define(name: str, frames: Optional[dict] = None) -> Keyframes`** — Build, register and return a new `Keyframes` in one call:
- **`.props(name: str, *, on_start: Optional[str] = None, on_iteration: Optional[str] = None, on_end: Optional[str] = None, **opts: Any) -> dict`** — `style` plus the literal `onanimationstart=`/`onanimationiteration=`/ `onanimationend=` HTML attributes (raw JS strings, handled by the browser -- same trick `nexoria.std`'s hover states use, see `nexoria/std/__init__.py`; no server round-trip, no JS bundle). Spread the result straight into `el(...)…
- **`.register(keyframes: Keyframes, *, as_name: Optional[str] = None) -> Keyframes`** — Add an existing `Keyframes` under `as_name` (defaults to `keyframes.name`). Returns it unchanged, for chaining.
- **`.style(name: str, **opts: Any) -> dict`** — `{"animation": self.css(name, **opts)}` -- spread or merge straight into an `el(..., style={...})` dict.
- **`.style_tag()`** — A single `<style>` `Element` carrying every `@keyframes` block currently registered on this engine (presets you actually reference are cheap to include unconditionally -- unused `@keyframes` rules cost nothing at runtime). Render it once, anywhere in your root layout, before any element uses `.style…

### Functions

#### `animation_runtime() -> Element`

A `<script>` `Element` carrying the full animation runtime -- scroll reveal, counters, typewriter, scramble text, `draw_svg`, and `morph_svg`. Render it once per page.

#### `reveal_styles() -> Element`

A `<style>` `Element` carrying the reveal base rules. Render it once per page, alongside `animation_runtime()`.

#### `animate_in(*children: Any, effect: str = 'fade-up', duration: int = 600, delay: int = 0, once: bool = True, class_: Optional[str] = None) -> Element`

`animate_in(el("h2", "Welcome"), effect="fade-up", delay=150)`.

`effect`: "fade" | "fade-up" | "fade-down" | "slide-left" | "slide-right" | "zoom-in". `once=False` re-plays the animation every time the element re-enters the viewport.

Needs `reveal_styles()` and `animation_runtime()` (from `nexoria.std.animation`) rendered once per page.

#### `animated_counter(target: float, *, prefix: str = '', suffix: str = '', decimals: int = 0, duration: int = 1500, class_: Optional[str] = None) -> Element`

`animated_counter(48200, prefix="$", suffix=" users")`. Counts up from 0 to `target` (ease-out) the moment it scrolls into view. Needs `animation_runtime()` rendered once per page. Renders the final value as static text if JS never runs (e.g. no-JS clients), so nothing is left blank.

#### `typewriter_text(text: str, *, speed: int = 40, tag: str = 'span', class_: Optional[str] = None) -> Element`

`typewriter_text("Write your whole stack in Python.", speed=35)`. Types `text` out one character at a time once it scrolls into view. Needs `animation_runtime()` rendered once per page. Renders the full text as a fallback (overwritten once JS types it out), so nothing is left blank without JS.

#### `scramble_text(text: str, *, chars: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', speed: int = 40, reveal_delay: int = 35, tag: str = 'span', class_: Optional[str] = None) -> Element`

`scramble_text("DECRYPTING...", speed=30, reveal_delay=40)`.

`speed` is the ms between scramble frames; `reveal_delay` is the ms between locking in each successive real character (so a higher `reveal_delay` relative to `speed` locks characters in more slowly). Spaces are never scrambled. Needs `animation_runtime()` rendered once per page. Renders the final text as a static fallback if JS never runs.

#### `split_text(text: str, *, by: str = 'chars', effect: str = 'fade-up', stagger: int = 30, duration: int = 500, tag: str = 'span', class_: Optional[str] = None) -> Element`

`split_text("Ship a real website", by="words", effect="fade-up", stagger=80)`.

`by`: "chars" | "words". `effect`: any `animate_in()` effect ("fade", "fade-up", "fade-down", "slide-left", "slide-right", "zoom-in"). `stagger` is the ms delay added per character/word. Needs `reveal_styles()` and `animation_runtime()` (from `nexoria.std.animation`) rendered once per page -- same as `animate_in()`, which this is built on top of.

#### `draw_svg(svg: Element, *, duration: int = 1500, delay: int = 0, stagger: int = 100) -> Element`

`draw_svg(el("svg", el("path", d="M10 10 L90 90", fill="none", stroke="var(--nx-primary)", style={"stroke_width": "3"}), viewBox="0 0 100 100"))`. (`stroke-width` -- like any hyphenated SVG attribute -- needs to go through `style=` rather than as a direct keyword, since Python identifiers can't contain hyphens; `el()`'s `style=` dict is the one place underscores get auto-converted to hyphens.)

Wraps an existing `<svg>` `Element` (built the normal way with `el()`) and tags it to animate every drawable shape inside (`path`, `circle`, `ellipse`, `line`, `polyline`, `polygon`, `rect`) as if hand-drawn, in document order, `stagger` ms apart, once it scrolls into view. Shapes need `fill="none"` and a visible `stroke` for the effect to read -- a filled shape will still "draw" its outline, but the fill will already be visible underneath it. Needs `animation_runtime()` rendered once per page.

#### `morph_svg(path_a: str, path_b: str, *, viewBox: str = '0 0 100 100', fill: str = 'none', stroke: str = 'var(--nx-primary)', stroke_width: str = '3', duration: int = 800, trigger: str = 'hover', width: str = '120px', height: str = '120px') -> Element`

`morph_svg("M10 80 L50 10 L90 80 Z", "M10 50 L50 90 L90 50 Z", trigger="hover")`.

Renders `path_a` and morphs it toward `path_b` on `trigger`: "hover" | "click" | "scroll" (into view) | "auto" (immediately on load). See the module docstring for when this can and can't smoothly interpolate. Needs `animation_runtime()` rendered once per page.

#### `animate(name: str, **opts: Any) -> dict`

Module-level shorthand for `ANIMATION_ENGINE.style(name, **opts)`.

#### `animated(*children: Any, name: str, tag: str = 'div', class_: Optional[str] = None, style: Optional[dict] = None, on_start: Optional[str] = None, on_iteration: Optional[str] = None, on_end: Optional[str] = None, **opts: Any)`

The fastest path to an animated chunk of markup -- wraps `children` in `tag` (a `<div>` by default) with the animation already applied.

Anything not consumed by the animation (`class_`, extra `style`, or any other `el()` prop) passes straight through. Uses the shared `ANIMATION_ENGINE` -- register custom animations there first if `name` isn't one of `nexoria.std.animation.presets.PRESETS`.

#### `keyframes_style()`

`ANIMATION_ENGINE.style_tag()` -- render once per page.

### Constants

| Name | Value |
|---|---|
| `ANIMATION_RUNTIME_JS` | `'(function () {\n  if (window.__nxAnim) return;\n  window.__nxAnim = true;\n\n  function onReady(fn) {\n    if (document.readyState === "loading") {\n      document.addEventListener("DOMContentLoaded", fn);\n    } else {\n      fn();\n    }\n  }\n\n  // -- scroll reveal -------------------------------------------------\n  function initReveal() {\n    var observer = new IntersectionObserver(function (entries) {\n  …` |
| `REVEAL_STYLES_CSS` | `'[data-nx-reveal] {\n  opacity: 0;\n  transition-property: opacity, transform;\n  transition-duration: var(--nx-reveal-duration, 600ms);\n  transition-delay: var(--nx-reveal-delay, 0ms);\n  transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1);\n  will-change: opacity, transform;\n}\n[data-nx-reveal="fade"] { transform: none; }\n[data-nx-reveal="fade-up"] { transform: translateY(28px); }\n[data-nx-reveal="fade…` |
| `PRESETS` | `{'fade-in': Keyframes(name='nx-anim-fade-in', frames={'from': {'opacity': 0}, 'to': {'opacity': 1}}), 'fade-out': Keyframes(name='nx-anim-fade-out', frames={'from': {'opacity': 1}, 'to': {'opacity': 0}}), 'fade-in-up': Keyframes(name='nx-anim-fade-in-up', frames={'from': {'opacity': 0, 'transform': 'translateY(24px)'}, 'to': {'opacity': 1, 'transform': 'translateY(0)'}}), 'fade-in-down': Keyframes(name='nx-anim-fa…` |
| `PRESET_NAMES` | `('fade-in', 'fade-out', 'fade-in-up', 'fade-in-down', 'fade-in-left', 'fade-in-right', 'slide-in-up', 'slide-in-down', 'slide-in-left', 'slide-in-right', 'zoom-in', 'zoom-out', 'flip-in', 'spin', 'pulse', 'ping', 'bounce', 'shake', 'wobble', 'heartbeat', 'rubber-band')` |
| `ANIMATION_ENGINE` | `AnimationEngine(_registry={'fade-in': Keyframes(name='nx-anim-fade-in', frames={'from': {'opacity': 0}, 'to': {'opacity': 1}}), 'fade-out': Keyframes(name='nx-anim-fade-out', frames={'from': {'opacity': 1}, 'to': {'opacity': 0}}), 'fade-in-up': Keyframes(name='nx-anim-fade-in-up', frames={'from': {'opacity': 0, 'transform': 'translateY(24px)'}, 'to': {'opacity': 1, 'transform': 'translateY(0)'}}), 'fade-in-down': …` |
