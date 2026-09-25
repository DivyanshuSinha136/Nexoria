# Nexoria — Top-Level API Reference

Everything importable from the `nexoria` package root, plus the public surface of every sub-package, the CLI, the HTTP/WebSocket protocol and the browser globals.

> The file name keeps its original spelling (`REFRANCE`) so existing links keep working.

**Contents:** 1. [Package root](#1-package-root) · 2. [`App`](#2-app) · 3. [`Component`](#3-component) · 4. [`el` / `Element`](#4-el--element) · 5. [`State` / `use_state`](#5-state--use_state) · 6. [`Router` / `Route`](#6-router--route) · 7. [`Stylesheet` / `Theme`](#7-stylesheet--theme) · 8. [Metadata](#8-metadata) · 9. [Sub-package index](#9-sub-package-index) · 10. [CLI](#10-cli) · 11. [HTTP and WebSocket surface](#11-http-and-websocket-surface) · 12. [Browser globals](#12-browser-globals) · 13. [Environment variables](#13-environment-variables)

---

## 1. Package root

```python
from nexoria import (
    App, Component, Element, el,
    State, use_state,
    Router, Route,
    Stylesheet, Theme, DEFAULT_THEME, LIGHT_THEME,
    __version__, __author__, __ecosystem__, __license__,
)
```

| Name | Kind | One-line description | Docs |
|---|---|---|---|
| `App` | class | ASGI application; owns router, middleware, themes, integrations; `run()` serves it | [core](core.md) |
| `Component` | class | Base class for pages/widgets: `setup()`, `render()` | [core](core.md) |
| `Element` | class | Virtual-DOM node | [core](core.md) |
| `el` | function | Element builder: `el(tag, *children, **props)` | [core](core.md) |
| `State` | class | Reactive dict | [state](state.md) |
| `use_state` | function | `(getter, setter)` pair | [state](state.md) |
| `Router`, `Route` | classes | Path router | [router](router.md) |
| `Stylesheet` | class | CSS-in-Python with scoped classes | [style](style.md) |
| `Theme` | dataclass | Design tokens → CSS variables | [style](style.md) |
| `DEFAULT_THEME`, `LIGHT_THEME` | instances | The dark default and the light override | [style](style.md) |

Also importable but not re-exported at the root: `from nexoria.core import text`, `from nexoria.style import theme_toggle_button`, `from nexoria.middleware import Middleware, CORSMiddleware, LoggingMiddleware`.

---

## 2. `App`

```text
App(
    name: str = 'Nexoria App',
    router: Optional[Router] = None,
    static_dir: Optional[str] = None,
    threejs: bool = False,
    gsap: bool = False,
    gsap_plugins: Optional[list[str]] = None,
    chartjs: bool = False,
    videojs: bool = False,
    videojs_plugins: Optional[list[VideoPlugin]] = None,
    aggrid: bool = False,
    spline: bool = False,
    vroid: bool = False,
    tailwind: bool = False,
    tailwind_config: Optional[TailwindConfig] = None,
    tailwind_plugins: Optional[list[str]] = None,
    bootstrap: bool = False,
    bootstrap_theme: Optional[BootstrapTheme] = None,
    bootstrap_icons: bool = False,
    babylonjs: bool = False,
    iconify: bool = False,
    shiki: bool = False,
    qrcode: bool = False,
    barcode: bool = False,
    openlayers: bool = False,
    webcam: bool = False,
    debug: bool = False,
    theme: Optional[Theme] = None,
    light_theme: Optional[Theme] = LIGHT_THEME,
    styles: Optional[Stylesheet] = None,
    description: Optional[str] = None,
    favicon: Optional[str] = '/_nexoria/falcon-nexoria.svg',
    og_image: Optional[str] = None,
)
```

**Instance methods**

| Method | Returns | Description |
|---|---|---|
| `use(middleware)` | `self` | Register a middleware (runs before routing for page requests) |
| `route(path, name=None)` | decorator | Register the decorated `Component` class on the router |
| `run(host="127.0.0.1", port=8000, reload=False, native=None, firewall=None)` | `None` | Serve the app (see below) |

**Attributes** you may read or set: `name`, `router`, `theme`, `light_theme`, `styles`, `middlewares`, `debug`, `favicon`, `description`, `og_image`, `static_dir`, and the integration flags (`threejs_enabled`, `gsap_enabled`, …). `app._asgi` is the underlying Starlette application if you need to add routes or wrap it with ASGI middleware.

**`run()` parameters**

| Parameter | Description |
|---|---|
| `host`, `port` | Bind address. |
| `reload` | `True` → uvicorn autoreload. The app must be assigned to a top-level variable in a `.py` file. `native` is ignored. |
| `native` | `None` (default): use the Go edge server if its binary exists. `True`: try it, warn and fall back on failure. `False`: never. |
| `firewall` | Dict for the Go edge firewall. Keys: `enabled`, `allow`, `deny`, `rate_limit`, `rate_burst`, `max_body_bytes`, `trust_x_forwarded_for`. Unknown keys raise `ValueError`. |

`App` is itself callable as ASGI: `uvicorn.run(app)` or `uvicorn module:app` also work (without the native tier).

Integration parameters are documented on their own pages: [three.js](threejs.md) · [GSAP](gsap.md) · [Chart.js](chartjs.md) · [video.js](videojs.md) · [AG Grid](aggrid.md) · [Spline](spline.md) · [VRoid](vroid.md) · [Babylon.js](babylonjs.md) · [Bootstrap](bootstrap.md) · [Tailwind](tailwind.md) · [Iconify](iconify.md) · [Shiki](shiki.md) · [QR](qrcode.md) · [Barcode](barcode.md) · [OpenLayers](openlayers.md) · [Webcam](webcam.md).

---

## 3. `Component`

```python
class Component:
    styles: ClassVar[Stylesheet]      # optional, class-level
    def __init__(self, **props): ...  # stores self.props, then calls setup()
    def setup(self) -> None: ...      # override: create State, etc.
    def render(self) -> Element: ...  # override: return the UI (required)
    def on_mount(self): ...           # defined but not invoked by App
    def on_unmount(self): ...         # defined but not invoked by App
```

`render()` must return an `Element` (a `Component` subclass that doesn't override it raises `NotImplementedError`).

---

## 4. `el` / `Element`

```text
el(tag: str, *children, key=None, **props) -> Element
text(value) -> Element                      # from nexoria.core
```

| Prop convention | Result |
|---|---|
| `class_`, `for_`, `id_`, `type_` | `class`, `for`, `id`, `type` |
| `data_foo_bar="x"`, `aria_label="x"` | `data-foo-bar`, `aria-label` |
| `style={"font_size": "1rem"}` or `"…"` | inline CSS string |
| `on_click=fn`, `on_input=fn`, `on_change=fn`, `on_submit=fn`, `on_keydown=fn`, `on_keyup=fn` | server handler (`fn(payload: dict)`, may be `async`) |
| `onclick="js"`, `onmouseover="js"`, … | literal browser attribute (client-side) |
| `key=…` | diff identity for list items; not rendered |
| boolean props | rendered bare when truthy, omitted when falsy |

**Handler payload:** `{"value": <event.target.value or None>, "key": <event.key or None>}`.

**Children:** `str/int/float` → text; `None` dropped; lists/tuples flattened; objects with `.to_element()` converted.

`Element` attributes/methods: `tag`, `props`, `children`, `key`, `text`, `is_text()`, `is_void()`, `to_dict()`.

---

## 5. `State` / `use_state`

```python
s = State({"count": 0})
s["count"] = 1;  s.set("count", 1);  s.update(count=2, other=3)
"count" in s;  list(s);  s.to_dict()

get, set_ = use_state(initial)
```

See [state](state.md) for notification semantics and caveats.

---

## 6. `Router` / `Route`

```text
router = Router()
router.add(path, component, name=None, guards=None) -> Router
router.set_not_found(component) -> Router
router.match(path) -> tuple[Route | None, dict]      # (None, {}) when nothing matches
router.resolve(path, **extra_props) -> Component | None
```

Patterns: static segments, `:param`, trailing `*` (delivered as prop `wildcard`). First match wins; failing guards skip a route. See [router](router.md).

---

## 7. `Stylesheet` / `Theme`

```text
sheet = Stylesheet(rules=None)
sheet.add(selector, **props) -> Stylesheet
sheet.merge(other) -> Stylesheet          # new object
sheet.scoped_class(name, **props) -> str  # "nx-<name>-<hash>"
sheet.to_css() -> str

Theme(...)                                # dataclass of design tokens
theme.to_css_vars() -> str                # ":root { --nx-… }"
```

Full field list and default values: [style](style.md).

---

## 8. Metadata

| Name | Value |
|---|---|
| `nexoria.__version__` | `"0.1.0"` |
| `nexoria.__author__` | `"Divyanshu Sinha"` |
| `nexoria.__ecosystem__` | `"Pythonaibrain"` |
| `nexoria.__license__` | `"MIT"` |
| Python | `>= 3.9` |
| Runtime dependencies | `starlette>=0.37`, `uvicorn[standard]>=0.29`, `jinja2>=3.1`, `watchfiles>=0.21`, `rich>=13.7` |

---

## 9. Sub-package index

Every public name each package exports (`__all__`). Click through for signatures and usage.

| Package | Public names | Page |
|---|---|---|
| `nexoria.core` | `App`, `Component`, `el`, `Element`, `text` | [core](core.md) |
| `nexoria.state` | `State`, `use_state` | [state](state.md) |
| `nexoria.router` | `Router`, `Route` | [router](router.md) |
| `nexoria.render` | `render_to_html`, `diff`, `Patch` | [render](render.md) |
| `nexoria.style` | `Stylesheet`, `Theme`, `DEFAULT_THEME`, `LIGHT_THEME`, `theme_toggle_button` | [style](style.md) |
| `nexoria.middleware` | `Middleware`, `CORSMiddleware`, `LoggingMiddleware` | [middleware](middleware.md) |
| `nexoria.cache` | `fingerprint` | [cache](cache.md) |
| `nexoria.js` | `js`, `Script`, `JSFunction` | [js](js.md) |
| `nexoria.translate` | `translate`, `Translation` | [translate](translate.md) |
| `nexoria.threejs` | `Scene`, `Mesh`, `Light`, `Camera` | [threejs](threejs.md) |
| `nexoria.babylonjs` | `BabylonScene`, `BabylonMesh`, `BABYLONJS_IMPORTS`, `BABYLONJS_ADAPTER_TAG`, `BABYLONJS_CDN` | [babylonjs](babylonjs.md) |
| `nexoria.vroid` | `VRMAvatar`, `VROID_IMPORTS`, `VROID_ADAPTER_TAG`, `VRM_CDN` | [vroid](vroid.md) |
| `nexoria.spline` | `SplineScene`, `SPLINE_IMPORTS`, `SPLINE_ADAPTER_TAG`, `SPLINE_CDN` | [spline](spline.md) |
| `nexoria.gsap` | `Tween`, `Timeline`, `Animation`, `GSAP_CDN`, `GSAP_VERSION`, `GSAP_RUNTIME_TAG`, `GSAP_ALL_PLUGINS`, `GSAP_PLUGIN_CDN_BASE`, `GSAP_PLUGIN_CONFIG_ID`, `gsap_plugin_imports`, `gsap_plugin_config_tag` | [gsap](gsap.md) |
| `nexoria.chartjs` | `Chart`, `Dataset`, `CHARTJS_CDN`, `CHARTJS_IMPORTS`, `CHARTJS_ADAPTER_TAG`, `CHARTJS_RUNTIME_TAG` | [chartjs](chartjs.md) |
| `nexoria.videojs` | `VideoPlayer`, `Track`, `VideoTheme`, `ControlBar`, `VideoPlugin`, `VIDEOJS_JS_CDN`, `VIDEOJS_CSS_CDN`, `VIDEOJS_CSS_TAG`, `VIDEOJS_CORE_SCRIPT_TAG`, `VIDEOJS_ADAPTER_TAG`, `VIDEOJS_RUNTIME_TAG` | [videojs](videojs.md) |
| `nexoria.aggrid` | `Grid`, `Column`, `AGGRID_IMPORTS`, `AGGRID_ADAPTER_TAG`, `AGGRID_THEMES`, `AGGRID_CDN` | [aggrid](aggrid.md) |
| `nexoria.openlayers` | `Map`, `OL_CSS_TAG`, `OL_CORE_SCRIPT_TAG`, `OL_ADAPTER_TAG`, `OL_JS_CDN` | [openlayers](openlayers.md) |
| `nexoria.bootstrap` | `BootstrapTheme`, `BOOTSTRAP_VERSION`, `BOOTSTRAP_CSS_CDN`, `BOOTSTRAP_JS_CDN`, `BOOTSTRAP_ICONS_VERSION`, `BOOTSTRAP_ICONS_CSS_CDN`, `BOOTSTRAP_CSS_TAG`, `BOOTSTRAP_CORE_SCRIPT_TAG`, `BOOTSTRAP_ADAPTER_TAG`, `BOOTSTRAP_ICONS_TAG`, `BOOTSTRAP_RUNTIME_TAG` | [bootstrap](bootstrap.md) |
| `nexoria.tailwind` | `TailwindConfig`, `TAILWIND_CDN`, `tailwind_cdn_url`, `tailwind_runtime_tag` | [tailwind](tailwind.md) |
| `nexoria.iconify` | `Icon`, `ICONIFY_CDN`, `ICONIFY_SCRIPT_TAG` | [iconify](iconify.md) |
| `nexoria.shiki` | `CodeBlock`, `SHIKI_IMPORTS`, `SHIKI_ADAPTER_TAG`, `SHIKI_CDN` | [shiki](shiki.md) |
| `nexoria.qrcode` | `QRCode`, `QRCODE_CDN`, `QRCODE_SCRIPT_TAG`, `QRCODE_ADAPTER_TAG` | [qrcode](qrcode.md) |
| `nexoria.barcode` | `Barcode`, `BWIPJS_IMPORTS`, `BWIPJS_ADAPTER_TAG`, `BWIPJS_CDN` | [barcode](barcode.md) |
| `nexoria.webcam` | `Webcam`, `WEBCAM_IMPORTS`, `WEBCAM_ADAPTER_TAG`, `WEBCAM_CDN` | [webcam](webcam.md) |
| `nexoria.desktop` | `scaffold_electron` | [desktop](desktop.md) |
| `nexoria.mobile` | `scaffold_capacitor` | [mobile](mobile.md) |
| `nexoria.native` | `npm`, `gpu`, `Runtime`, `js_available` | [native](native.md) |
| `nexoria.cli` | — | [cli](cli.md) |
| `nexoria.std.premium` | `PremiumTheme`, `PREMIUM_THEME`, `PREMIUM_KEYFRAMES_CSS`, `premium_keyframes`, `premium_button`, `premium_badge`, `premium_avatar`, `premium_card`, `glass_panel`, `stat_card`, `pricing_card`, `hero_section`, `feature_grid`, `testimonial`, `premium_navbar`, `premium_footer` | [std/premium](std/premium.md) |
| `nexoria.std.cartoon` | `CartoonTheme`, `CARTOON_THEME`, `CARTOON_KEYFRAMES_CSS`, `cartoon_keyframes`, `cartoon_button`, `cartoon_card`, `comic_panel`, `speech_bubble`, `thought_bubble`, `sticker_badge`, `cartoon_avatar`, `blob_progress` | [std/cartoon](std/cartoon.md) |
| `nexoria.std.lib` | `LibTheme`, `LIB_THEME`, `LIB_KEYFRAMES_CSS`, `lib_keyframes`, `lib_grid_background`, `lib_pill`, `lib_eyebrow`, `live_badge`, `lib_tag`, `lib_tag_row`, `stat_chip_row`, `lib_button`, `code_window`, `lib_feature_card`, `integration_chip`, `lib_hero`, `pipeline_steps`, `feature_trio`, `integrations_row`, `install_cta`, `lib_navbar`, `lib_footer` | [std/lib](std/lib.md) |
| `nexoria.std.icons` | `Icon`, `IconNotFoundError`, `list_icons`, `has_icon`, `icon_count` | [std/icons](std/icons.md) |
| `nexoria.std.alert` | `alert_banner`, `toast`, `inline_alert` | [std/alert](std/alert.md) |
| `nexoria.std.animation` | `ANIMATION_RUNTIME_JS`, `animation_runtime`, `REVEAL_STYLES_CSS`, `reveal_styles`, `animate_in`, `animated_counter`, `typewriter_text`, `scramble_text`, `split_text`, `draw_svg`, `morph_svg`, `Keyframes`, `PRESETS`, `PRESET_NAMES`, `AnimationEngine`, `ANIMATION_ENGINE`, `animate`, `animated`, `keyframes_style` | [std/animation](std/animation.md) |
| `nexoria.std.observer` | `OBSERVER_RUNTIME_JS`, `observer_runtime`, `observer_region` | [std/observer](std/observer.md) |
| `nexoria.std.physics2d` | `PHYSICS2D_RUNTIME_JS`, `physics2d_runtime`, `physics2d_element`, `physics2d_burst` | [std/physics2d](std/physics2d.md) |
| `nexoria.std.scroll` | `SCROLL_RUNTIME_JS`, `scroll_runtime`, `scroll_progress_bar`, `scroll_to_top_button`, `anchor_link`, `smooth_scroll_container` | [std/scroll](std/scroll.md) |
| `nexoria.std.svg` | `PathBuilder`, `svg_canvas`, `svg_path` | [std/svg](std/svg.md) |
| `nexoria.std.charts` | `CHART_STYLES_CSS`, `chart_styles`, `CHARTS_RUNTIME_JS`, `charts_runtime`, `DEFAULT_PALETTE`, `color_for`, `LinearScale`, `nice_ticks`, `line_chart`, `area_chart`, `sparkline`, `bar_chart`, `pie_chart`, `donut_chart`, `radial_gauge` | [std/charts](std/charts.md) |
| `nexoria.std.typography` | `FontFace`, `FontSource`, `TypeStep`, `TypeScale`, `fluid_clamp`, `DEFAULT_SCALE_STEPS`, `TypographyEngine`, `TYPOGRAPHY_ENGINE`, `font_face`, `font_stack`, `type_style`, `styled_text`, `typography_style_tag` | [std/typography](std/typography.md) |
| `nexoria.std.webtools` | `tooltip`, `copy_button`, `modal_dialog`, `accordion`, `tabs` | [std/webtools](std/webtools.md) |

---

## 10. CLI

| Command | Purpose |
|---|---|
| `nexoria new NAME [--force]` | Scaffold an app |
| `nexoria dev [--module app] [--host] [--port]` | Dev server with autoreload |
| `nexoria build` | Production asset build (Node) |
| `nexoria doctor [--json]` | Native-tier and toolchain report |
| `nexoria native status \| build \| clean` | Manage native tiers |
| `nexoria build-desktop`, `build-mobile` | Electron / Capacitor scaffolds |
| `nexoria --version`, `--no-color` | Global flags |

Details and flags: [cli](cli.md).

---

## 11. HTTP and WebSocket surface

| Endpoint | Method | Description |
|---|---|---|
| `/{any path}` | GET | Server-rendered page |
| `/_nexoria/live` | WebSocket | Event in, `patch` out |
| `/_nexoria/health` | GET | `{"status": "ok", "framework": "nexoria"}` |
| `/_nexoria/{file}` | GET | Bundled runtime assets |
| `/favicon.ico` | GET | 307 to the icon (204 if `favicon=None`) |
| `/static/*` | GET | `static_dir` (see [known issue](core.md#known-issues) on the plain-Python path) |
| `/_nexoria/native-health`, `/_nexoria/firewall-status` | GET | Go edge server only |

**Hydration payload** (`<script id="nx-hydration-data" type="application/json">`): `{"route", "tree", "component", "session"}`.

**Client → server:** `{"event", "handler_id", "session", "payload": {"value", "key"}}`

**Server → client:** `{"type": "patch", "patches": [{"op", "path", "payload"}, …]}` with `op ∈ {text, replace, insert, remove, update_props}`.

---

## 12. Browser globals

`window.__nexoria__` = `{ hydration, applyPatches, sessionId, toggleTheme, <adapter namespaces…> }`. Adapter members are listed in [runtime](runtime.md#adapter-convention).

DOM events dispatched by adapters: `nexoria:aggrid:ready`, `nexoria:babylon:ready`, `nexoria:openlayers:ready`, `nexoria:spline:ready`, `nexoria:videojs:ready`, `nexoria:vroid:ready`, `nexoria:webcam:snap`.

---

## 13. Environment variables

| Variable | Effect |
|---|---|
| `NO_COLOR`, `NEXORIA_NO_COLOR` | Force plain CLI output |
| `NEXORIA_PYTHON` | Interpreter the Electron scaffold launches (default `python3`) |
| `NEXORIA_DESKTOP` | Set to `1` by the Electron scaffold when it starts your app |
