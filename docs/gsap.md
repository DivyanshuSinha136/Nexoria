# `nexoria.gsap`

> Describe GSAP tweens and timelines in Python; the adapter runs them against elements already on the page.

| | |
|---|---|
| **Import** | `from nexoria.gsap import Tween, Timeline, Animation` |
| **Enabled by** | `App(gsap=True)`; plugins via `App(gsap=True, gsap_plugins=[...])` |
| **Library** | GSAP 3.15.0 from unpkg (`"gsap"` in the shared import map; each plugin as `"gsap/<Name>"`) |
| **Adapter** | `runtime/gsap-adapter.js` |
| **Python dependency** | none |

## Quick start

```python
from nexoria import App, Component, el, Router
from nexoria.gsap import Tween, Timeline, Animation

class Hero(Component):
    def render(self):
        anim = Animation(
            Timeline(
                Tween(".hero-title", opacity=0, y=20, from_vars=True, duration=0.6),
                Tween(".hero-sub",   opacity=0, y=20, from_vars=True, duration=0.6, position="-=0.3"),
            ),
            name="hero-intro",
        )
        return el("div",
            el("h1", "Hello", class_="hero-title"),
            el("p", "World", class_="hero-sub"),
            el("button", "Replay", onclick=anim.restart_attr()),   # client-side, no server round-trip
            anim.to_element(),
        )

app = App(name="Animated", router=Router().add("/", Hero), gsap=True)
```

## Concepts

- **Targets are CSS selectors** for elements rendered elsewhere in your tree — give them `class_`/`id`.
- `Tween(target, from_vars=False, position=None, **vars)`: `vars` go to `gsap.to()` (or `gsap.from()` when `from_vars=True`) verbatim.
- `Timeline(*children, repeat=0, yoyo=False, paused=False)` sequences tweens and nested timelines; `position` on a tween is GSAP's position parameter.
- `Animation(root, name, autoplay=True)` → `.to_element()` emits an inert `<script type="application/json" class="nx-gsap-anim">` marker. The adapter builds the timeline, registers it under `name`, and autoplays it unless `autoplay=False` or the timeline is `paused`.
- Control from the client with `play_attr()`, `pause_attr()`, `restart_attr()`, `reverse_attr()` — plain `onclick=` strings calling `window.__nexoria__.gsap.<action>(name)`.

## Plugins

Every official GSAP plugin can be enabled by name (all are free since GSAP's 2025 relicense). Names are validated at `App(...)` construction — a typo raises `ValueError`:

`ScrollTrigger`, `ScrollToPlugin`, `ScrollSmoother`, `Draggable`, `Flip`, `Observer`, `MotionPathPlugin`, `MotionPathHelper`, `DrawSVGPlugin`, `MorphSVGPlugin`, `Physics2DPlugin`, `PhysicsPropsPlugin`, `InertiaPlugin`, `PixiPlugin`, `EaselPlugin`, `TextPlugin`, `SplitText`, `ScrambleTextPlugin`, `CustomEase`, `CustomBounce`, `CustomWiggle`, `GSDevTools`.

```python
App(gsap=True, gsap_plugins=["ScrollTrigger"])
Tween(".card", opacity=0, y=40, from_vars=True, scrollTrigger={"trigger": ".card", "start": "top 85%"})
```

`gsap_plugins` only takes effect together with `gsap=True`. Enabled plugins add `"gsap/<Name>"` import-map entries and a `<script id="nx-gsap-plugins">` JSON marker; the adapter `import()`s each and calls `gsap.registerPlugin()` **before** mounting animations (so animations attach one tick later than on a plugin-free page; wait on `window.__nexoria__.gsap.ready` if you need to know).

Looking for dependency-free animation without GSAP? See [`std.animation`](std/animation.md) and [`std.physics2d`](std/physics2d.md).

## API reference

### Classes

#### `class Tween(target: str, from_vars: bool = False, position: Optional[Union[str, float]] = None, **vars: Any)`

One GSAP tween. `target` is a CSS selector matching element(s) already rendered elsewhere on the page (give them a `class_`/`id` in `el(...)` to target them). Extra keyword args become GSAP "vars" verbatim (`opacity`, `x`, `y`, `scale`, `rotation`, `duration`, `ease`, `stagger`, ... -- anything GSAP's `.to()`/`.from()` accepts).

`position` only matters inside a `Timeline` -- it's GSAP's timeline position parameter (e.g. `"-=0.3"` to overlap with the previous tween).

- **`.to_dict() -> dict`**

#### `class Timeline(*children: Union['Tween', 'Timeline'], repeat: int = 0, yoyo: bool = False, paused: bool = False)`

An ordered sequence of Tweens (or nested Timelines), played as a single GSAP timeline.

- **`.to_dict() -> dict`**

#### `class Animation(root: Union[Tween, Timeline], name: str, autoplay: bool = True) -> None`

Top-level wrapper attaching a Tween/Timeline to the page. Call `.to_element()` and include the result anywhere in a `render()` return value (it emits an inert `<script type="application/json">` marker, not visible UI) -- the client adapter finds it, builds the real GSAP timeline, names it, and autoplays it unless `autoplay=False` or the timeline itself is `paused=True`.

Trigger it later (e.g. from a button, purely client-side, no server round-trip) with the onclick helpers.

- **`.pause_attr() -> str`**
- **`.play_attr() -> str`**
- **`.restart_attr() -> str`**
- **`.reverse_attr() -> str`**
- **`.to_dict() -> dict`**
- **`.to_element()`**

### Functions

#### `gsap_plugin_imports(plugins) -> dict[str, str]`

Import-map entries for the given plugin names, e.g. ``["ScrollTrigger"]`` -> ``{"gsap/ScrollTrigger": "https://unpkg.com/gsap@.../ScrollTrigger.js"}``. Merged into the app-wide import map alongside the core ``"gsap"`` entry. Raises ``ValueError`` on an unrecognized plugin name (see ``GSAP_ALL_PLUGINS``).

#### `gsap_plugin_config_tag(plugins) -> str`

Inert ``<script type="application/json">`` marker listing the enabled plugin names, read by the client adapter on load so it knows which modules to dynamically `import()` and `gsap.registerPlugin()` before mounting any animation. Empty string (no tag) if there are no plugins.

### Constants

| Name | Value |
|---|---|
| `GSAP_CDN` | `'https://unpkg.com/gsap@3.15.0/index.js'` |
| `GSAP_VERSION` | `'3.15.0'` |
| `GSAP_RUNTIME_TAG` | `'<script type="importmap">{"imports": {"gsap": "https://unpkg.com/gsap@3.15.0/index.js"}}</script>\n<script src="/_nexoria/gsap-adapter.js" type="module" defer></script>'` |
| `GSAP_ALL_PLUGINS` | `('ScrollTrigger', 'ScrollToPlugin', 'ScrollSmoother', 'Draggable', 'Flip', 'Observer', 'MotionPathPlugin', 'MotionPathHelper', 'DrawSVGPlugin', 'MorphSVGPlugin', 'Physics2DPlugin', 'PhysicsPropsPlugin', 'InertiaPlugin', 'PixiPlugin', 'EaselPlugin', 'TextPlugin', 'SplitText', 'ScrambleTextPlugin', 'CustomEase', 'CustomBounce', 'CustomWiggle', 'GSDevTools')` |
| `GSAP_PLUGIN_CDN_BASE` | `'https://unpkg.com/gsap@3.15.0'` |
| `GSAP_PLUGIN_CONFIG_ID` | `'nx-gsap-plugins'` |
