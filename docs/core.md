# `nexoria.core`

> The heart of the framework: the `App` (an ASGI application), the `Component` base class, and the `Element` virtual-DOM node with its `el()` builder.

| | |
|---|---|
| **Import** | `from nexoria import App, Component, el, Element` (also `from nexoria.core import text`) |
| **Source** | `nexoria/core/app.py`, `component.py`, `element.py` |
| **Enabled by** | Always on |
| **Depends on** | `starlette` (ASGI), `uvicorn` (server) |
| **Related** | [`render`](render.md), [`state`](state.md), [`router`](router.md), [`style`](style.md), [`runtime`](runtime.md) |

---

## 1. `Element` and `el()` — the UI primitive

Every Nexoria UI is a tree of `Element` objects. You almost never construct one directly; you call `el()`.

```python
from nexoria import el

tree = el("div",
    el("h1", "Hello"),
    el("button", "Click", class_="nx-btn", on_click=lambda e: print("clicked", e)),
    class_="nx-card",
)
```

### What `el()` does

| Rule | Behaviour |
|---|---|
| **Keyword remap** | `class_` → `class`, `for_` → `for`, `id_` → `id`, `type_` → `type` (only these four; they clash with Python keywords/builtins). |
| **Hyphenation** | Props that start with `data_` or `aria_` have underscores turned into hyphens: `data_user_id="7"` → `data-user-id="7"`, `aria_label="x"` → `aria-label="x"`. Other props are passed through untouched — for any other hyphenated attribute use dict-unpacking: `el("svg", **{"stroke-width": 2})`. |
| **Style dicts** | `style={"font_size": "1rem", "color": "red"}` becomes `"font-size: 1rem; color: red"`. A plain string is passed through. |
| **Children coercion** | `str`/`int`/`float` become text nodes; `None` is dropped; lists/tuples are flattened one level (so `*[…]` and `[…]` both work); any object with a callable `.to_element()` (an `Icon`, `Chart`, `Grid`, `QRCode`, `Animation`, `PathBuilder`, …) is converted automatically. |
| **Keys** | `key=` is removed from the props (never rendered) and stored on the node; the differ uses it to track list items across renders. |
| **Event handlers** | Any prop named `on_<event>` whose value is callable is removed from the props and stored in the element's handler registry with a fresh id (`h1`, `h2`, …). The rendered HTML carries `data-nx-on-<event>="<id>"` instead of inline JS. |
| **Literal HTML handlers** | `onclick="…"` (no underscore, a *string*) is **not** an event handler in Nexoria's sense — it is a normal HTML attribute executed by the browser with no server round-trip. Both styles are used deliberately across the framework (see the [Q&A](Q-A.md#server-handler-vs-client-attribute)). |

`Element` uses `__slots__` and exposes: `tag`, `props`, `children`, `key`, `text`, `is_text()`, `is_void()`, `to_dict()`. Void tags (`br`, `img`, `input`, `meta`, …) render self-closing.

`to_dict()` is the wire format used by both the differ and the hydration payload:

```json
{"t": "el", "tag": "button", "props": {}, "events": {"click": "h1"}, "key": null,
 "children": [{"t": "text", "v": "Increment"}]}
```

---

## 2. `Component`

A component is a plain Python class with a `render()` that returns an `Element`.

```python
from nexoria import Component, el, State, Stylesheet

class Counter(Component):
    styles = Stylesheet()                 # optional, component-scoped CSS

    def setup(self):                      # runs once, in __init__
        self.state = State({"count": 0})

    def render(self):
        cls = self.styles.scoped_class("box", padding="24px")
        return el("div",
            el("p", f"Clicked {self.state['count']} times"),
            el("button", "Increment", class_="nx-btn",
               on_click=lambda e: self.state.update(count=self.state["count"] + 1)),
            class_=f"nx-card {cls}",
        )
```

- `__init__(**props)` stores `self.props` and calls `setup()`. A routed component receives **path parameters** (`/users/:id` → `props["id"]`) and **query parameters** as props.
- `render()` is called once per HTTP request (first paint) and again after every handled event.
- `styles` is a class-level `Stylesheet`; the `App` merges it into the page `<head>` automatically.
- Lifecycle hooks `on_mount()` / `on_unmount()` exist on the base class, but **the current `App` does not invoke them** (only `setup()` and `render()` run). Treat them as reserved.

---

## 3. `App`

`App` *is* an ASGI application (`await app(scope, receive, send)`), so it can be served by any ASGI host. It wraps a Starlette app with five routes.

### Constructor

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

| Parameter | Meaning |
|---|---|
| `name` | Page `<title>`, `og:title`, and the name shown in logs. |
| `router` | A [`Router`](router.md); an empty one is created if omitted. |
| `static_dir` | Directory mounted at `/static` (see the [known issue](#known-issues) below). |
| Integration flags | Each `True` flag makes `_build_head()` emit that library's CDN tags and adapter script. See the per-package pages ([three.js](threejs.md), [GSAP](gsap.md), …). |
| `gsap_plugins` | List of GSAP plugin names (validated eagerly — a typo raises `ValueError` at construction). |
| `videojs_plugins` | List of `VideoPlugin(name, src)` loaded between video.js core and the adapter. |
| `theme` / `light_theme` | Dark tokens (default `DEFAULT_THEME`) and the light override. `light_theme=None` disables the toggle. |
| `styles` | An app-wide `Stylesheet`. |
| `description`, `og_image` | Emit `<meta name="description">` / Open Graph tags. Omitted when `None`. |
| `favicon` | Defaults to the bundled falcon SVG (+ `.ico` fallback). A path overrides it; `None` disables it (`/favicon.ico` then returns 204). |
| `debug` | Starlette debug mode; also re-raises exceptions inside the WebSocket loop. |

### Methods

| Method | Description |
|---|---|
| `app.use(middleware)` | Register a [`Middleware`](middleware.md); returns `self`. |
| `@app.route(path, name=None)` | Decorator that registers the class on the router. |
| `app.run(host="127.0.0.1", port=8000, reload=False, native=None, firewall=None)` | Start serving. See below. |

### `run()` — three serving modes

1. **`reload=True`** — uvicorn's autoreloader. Nexoria inspects the call stack to find the module-level variable your `App` is bound to and hands uvicorn a `"module:variable"` string, so `app.run(reload=True)` just works from `python app.py`. It raises a clear `RuntimeError` if the app is not bound to a top-level variable in a real `.py` file. `native` is ignored in this mode.
2. **`native=None/True`** and a compiled Go binary exists — uvicorn is started on a free loopback port in a background thread and `nexoria-server` is spawned in front of it (static assets + firewall + reverse proxy). If the binary is missing, exits within 1.5 s, or the backend is slow to start, Nexoria prints a warning and **falls back to plain uvicorn**. See [native](native.md#4-go-edge-server).
3. **Otherwise** — plain `uvicorn.run(app)`.

`firewall={...}` only applies to mode 2. Valid keys: `enabled`, `allow`, `deny`, `rate_limit`, `rate_burst`, `max_body_bytes`, `trust_x_forwarded_for`. Unknown keys raise `ValueError` immediately.

### HTTP surface

| Route | Handler |
|---|---|
| `GET /{path}` | SSR: run middleware → resolve route → `render()` → HTML document + hydration payload |
| `WS /_nexoria/live` | Event → handler → re-render → diff → `patch` message |
| `GET /_nexoria/health` | `{"status": "ok", "framework": "nexoria"}` |
| `GET /_nexoria/{filename}` | Bundled runtime files (`runtime.js`, `base.css`, `*-adapter.js`, the falcon icons). Filename is reduced to its basename; unknown files 404. |
| `GET /favicon.ico` | 307 redirect to the configured icon, or 204 if `favicon=None` |
| `/static/*` | `StaticFiles(static_dir)` when `static_dir` is set |

### Session model

On every page request the `App` creates a `session_id`, stores `{component, tree, handlers}` in an in-process dict (`App._sessions`), and puts the id in the hydration payload. When an event arrives over the socket, the server looks the session up, runs the handler, calls `render()` again, diffs against the stored tree, replaces the stored tree and handler map (handler ids are regenerated on every render), and sends the patches. The session is dropped when its socket disconnects.

### What goes in `<head>`

`_build_head()` emits, in order: `base.css` link → theme CSS variables → light-theme override → merged app + component `Stylesheet` → SEO/OG meta → favicon links → **one merged `<script type="importmap">`** for every ESM-based integration → adapter scripts → per-integration CSS/script tags (Iconify, QR, OpenLayers, video.js, Bootstrap, Tailwind). A single import map is essential because browsers honour only one per document.

### Known issues

These come from reading and exercising the current source; they are documented here so you can plan around them.

- **`/static` is shadowed on the plain-uvicorn path.** The catch-all SSR route `/{path:path}` is registered before the `/static` mount, so `GET /static/app.css` reaches the SSR handler and returns the styled 404 page. Behind the Go edge server `/static` is served natively and works. Workaround: serve static files from a reverse proxy/CDN, or mount your own `StaticFiles` ahead of the catch-all on `app._asgi`.
- **A custom not-found page returns HTTP 200.** Only the built-in 404 (no `set_not_found`) uses status 404.
- **State changes outside an event handler are not pushed.** `App._schedule_rerender` is a no-op; re-render happens only after a client event is handled.
- **Sessions live in process memory.** A page whose socket never connects leaves its session in `_sessions`; and with several worker processes a socket may reach a worker that doesn't know the session (events are then silently ignored until reload).
- **An exception inside an event handler ends the live channel.** The WebSocket loop catches it in a blanket `except` (re-raised only with `debug=True`), drops the session in `finally`, and sends no error message — the page simply stops responding until it is reloaded. Catch and handle errors inside your handlers (for example write an error message into `State`).
- **`on_mount` / `on_unmount` are never called.**
- **Middleware runs for SSR page requests only** — not for the WebSocket, `/_nexoria/*`, or `/favicon.ico`.

---

## API reference

### Classes

#### `class App(name: str = 'Nexoria App', router: Optional[Router] = None, static_dir: Optional[str] = None, threejs: bool = False, gsap: bool = False, gsap_plugins: Optional[list[str]] = None, chartjs: bool = False, videojs: bool = False, videojs_plugins: Optional[list[VideoPlugin]] = None, aggrid: bool = False, spline: bool = False, vroid: bool = False, tailwind: bool = False, tailwind_config: Optional[TailwindConfig] = None, tailwind_plugins: Optional[list[str]] = None, bootstrap: bool = False, bootstrap_theme: Optional[BootstrapTheme] = None, bootstrap_icons: bool = False, babylonjs: bool = False, iconify: bool = False, shiki: bool = False, qrcode: bool = False, barcode: bool = False, openlayers: bool = False, webcam: bool = False, debug: bool = False, theme: Optional[Theme] = None, light_theme: Optional[Theme] = LIGHT_THEME, styles: Optional[Stylesheet] = None, description: Optional[str] = None, favicon: Optional[str] = '/_nexoria/falcon-nexoria.svg', og_image: Optional[str] = None)`

- **`.route(path: str, name: Optional[str] = None)`** — Decorator form: @app.route("/about")
- **`.run(host: str = '127.0.0.1', port: int = 8000, reload: bool = False, native: Optional[bool] = None, firewall: Optional[dict] = None) -> None`** — Start the dev/production server.
- **`.use(middleware: Middleware) -> 'App'`**

#### `class Component(**props: Any)`

Subclass and implement `render()`.

Optionally declare component-scoped CSS via `styles`.

`App` automatically merges a routed component's `styles` into the page's `<style>` block alongside the app-level theme — no manual wiring required.

- **`.on_mount() -> None`** — Called once the component's DOM has been attached (client-side).
- **`.on_unmount() -> None`** — Called just before the component is removed from the tree.
- **`.render() -> Element`**
- **`.setup() -> None`** — Called once at construction. Initialize `self.state` here.

#### `class Element(tag: Optional[str] = None, props: Optional[dict] = None, children: Optional[list] = None, text: Optional[str] = None, key: Optional[Union[str, int]] = None)`

A single virtual DOM node (tag, text, or component placeholder).

- **`.is_text() -> bool`**
- **`.is_void() -> bool`**
- **`.to_dict() -> dict`** — Serialize to a plain dict (used for the JSON patch protocol).

### Functions

#### `el(tag: str, *children: Union[Element, str, int, float], **props: Any) -> Element`

Build an Element.

- `class_` is remapped to `class`, `for_` to `for` (Python keyword clashes). - Bare strings/numbers passed as children become text nodes automatically. - Keys go through `key=` and are used by the differ to track identity across re-renders (important for lists).

#### `text(value: Any) -> Element`
