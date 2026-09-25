# Nexoria — Questions & Answers

The "why" behind the design, plus practical answers and troubleshooting. Related: [ARCHITECTURE.md](ARCHITECTURE.md), [FLOWCHART.md](FLOWCHART.md), [TOP-LEVEL-API-REFRANCE.md](TOP-LEVEL-API-REFRANCE.md).

**Sections:** [A. Concept and philosophy](#a-concept-and-philosophy) · [B. Rendering and interactivity](#b-rendering-and-interactivity) · [C. Styling and the standard library](#c-styling-and-the-standard-library) · [D. Integrations](#d-integrations) · [E. Native tiers and tooling](#e-native-tiers-and-tooling) · [F. Deployment and scaling](#f-deployment-and-scaling) · [G. How do I…?](#g-how-do-i) · [H. Troubleshooting](#h-troubleshooting) · [I. Known limitations](#i-known-limitations)

---

## A. Concept and philosophy

### What is Nexoria?
A Python web framework in which the whole page — structure, behaviour, styling — is written in Python. You build a tree with `el()`, put it in a `Component.render()`, and Nexoria server-renders it to real HTML, hydrates it with a small JavaScript runtime, and keeps it live by sending DOM patches over a WebSocket.

### Why write the frontend in Python at all?
So one person (or one team) can ship a full-stack interface without maintaining a second language, a bundler chain, a client-side state library and an API layer between them. The server already owns the data; making it own the UI removes the synchronisation problem entirely.

### Why no JSX and no template language?
A tree of function calls is just Python: you get loops, conditionals, functions, type checkers, refactoring tools and unit tests for free, and nothing new to learn. `el("ul", *[el("li", x) for x in items])` is the whole "template syntax".

### Why server-rendered first?
The first response is complete HTML: fast first paint, works without JavaScript, indexable by crawlers, and shareable as a plain URL. Interactivity is layered on afterwards instead of being a prerequisite for seeing anything.

### Why patches over a WebSocket instead of a client-side SPA?
State lives in one place (the server), so the browser cannot drift from it, and secrets and business logic never reach the client. The cost is that every server-handled interaction costs a network round trip; interactions that must be instant use client-side attributes instead (see the next answer).

### <a id="server-handler-vs-client-attribute"></a><a name="server-handler-vs-client-attribute"></a>Why are there two ways to attach behaviour: `on_click=` and `onclick=`?
They are different on purpose.

| | `on_click=callable` | `onclick="js string"` |
|---|---|---|
| Runs | On the **server** (Python) | In the **browser** (JavaScript) |
| Latency | One round trip | None |
| Can change `State` | Yes | No |
| Typical use | Add to cart, submit, navigate state | Open a modal, switch a tab, copy text, scroll |

Nexoria's standard library uses the second style for micro-interactions so they work instantly and independent of server state, and reserves `on_*` for things your Python code must decide.

### Why does `el()` use `class_`, `for_`, `id_`, `type_`?
Those names collide with Python keywords or builtins, so they get a trailing underscore that `el()` strips. Any other attribute name is used as written.

### Why is `State` per component instance and not global or per user?
It makes the mental model tiny: one page load = one component = one state, living for as long as that tab's socket is open. Sharing between tabs or users is deliberately left to your own storage (database, cache), where you can control consistency.

### Why is there no reactive auto-update when I mutate state in a background task?
Re-rendering is driven by handled events: handler runs → `render()` → diff → patch. `App._schedule_rerender` is currently a no-op, so a background task changing `State` will not push to the browser by itself. Structure live updates as events (for example a client-side timer that fires a handler) until push-on-change lands.

### Why are event handler ids regenerated on every render?
Handler ids come from a process-wide counter, and each `el()` call mints new ones. After each render the server replaces its handler map and the differ sends an `update_props` patch so the DOM's `data-nx-on-*` attributes match. It guarantees a stale id can never fire a handler that no longer exists, at the price of extra small patches.

### Why only six delegated event types?
The runtime delegates `click`, `input`, `change`, `submit`, `keydown` and `keyup` — the events that drive forms and buttons — with a single capture-phase listener each, which keeps the runtime tiny and handler wiring O(1) regardless of page size. For anything else (`mouseover`, `scroll`, `focus`), use a literal attribute or a `Script`.

### Why does the handler payload contain only `value` and `key`?
It is the minimum that covers inputs and keyboard interaction without serialising DOM events (which are large and not JSON-safe). If you need more, read it in a client-side snippet and pass it through an input's `value`.

### Why Starlette and uvicorn?
Starlette is a small, well-tested ASGI toolkit with first-class WebSocket support; uvicorn is the standard fast ASGI server. Nexoria's `App` is a plain ASGI callable, so it also runs under any other ASGI server.

### Why a hand-written ~6.5 KB runtime rather than a bundled framework?
The client has only three jobs: read the hydration JSON, forward events, and apply patches. That is small enough to read in one sitting, has zero dependencies and needs no build step. `nexoria build` can still hash it for caching.

### Why is `nexoria/ssr/` empty?
It is a reserved placeholder. SSR lives in `nexoria.render` and `App`.

### How is Nexoria different from other Python UI frameworks?
The distinguishing choices are: real server-rendered HTML on the first request, a tiny fixed client runtime with an explicit patch protocol, no template language, optional native accelerators with automatic fallbacks, and first-class declarative adapters for popular JavaScript libraries. It does not try to be a data-app toolkit or a JavaScript replacement.

---

## B. Rendering and interactivity

### How does a click become a UI change?
`runtime.js` finds the nearest ancestor with `data-nx-on-click`, sends `{event, handler_id, session, payload}` over the socket; the server runs the handler, re-renders, diffs against the stored tree and replies with patches. See [FLOWCHART §3](FLOWCHART.md#3-event--patch-cycle).

### Can handlers be `async`?
Yes. If a handler returns an awaitable the server awaits it before re-rendering. Synchronous handlers run directly on the event loop, so keep them short.

### Why did my page stop responding after an error in a handler?
An unhandled exception in a handler ends the live loop and drops the session (re-raised only when `App(debug=True)`); nothing is sent to the browser. Catch errors inside handlers and record them in `State`, then render them.

### Why did my keyed list reorder incorrectly?
The keyed differ addresses children by their **new** index and emits no move operation, so reorders produce no patches, and removing several items in one update misapplies. See [render](render.md#known-limitations-of-keyed-lists). Change one thing per event, or change the container's `key` to force a re-render of the list.

### Why did my custom 404 page return status 200?
Only the built-in not-found page returns 404. A component registered with `set_not_found` is rendered like any other page (status 200). If status codes matter (SEO, monitoring), place a reverse proxy rule in front, or don't register a not-found component and rely on the built-in page.

### Do query parameters work?
Yes: they are passed to the component as props (`/search?q=py` → `props["q"]`), after path parameters.

### Do links do client-side navigation?
No. Links are ordinary anchors; each navigation is a normal page load with a fresh component instance and session.

### Do `on_mount` / `on_unmount` run?
Not currently — only `setup()` and `render()` are invoked.

### How do I run something when the page loads?
Do it in `setup()` (once per page load, on the server), or use `nexoria.js.Script(code, on_ready=True)` for client-side code.

### How do I keep some input's value in state?
Use `on_input=lambda e: self.state.update(q=e["value"])` and render `value=self.state["q"]`. The handler payload is a dict with `value` and `key`.

### How do I safely put a Python value into JavaScript?
Use `js("fn({x})", x=value)`. It JSON-encodes values, so quotes and `</script>` cannot break out. Never build JS with f-strings from untrusted input.

---

## C. Styling and the standard library

### Why CSS variables (`--nx-*`) rather than a Sass/utility pipeline?
Runtime-switchable theming with no build step: swapping a `Theme`, toggling light/dark, or mixing design systems is just changing variable values.

### Why does the light/dark toggle not flash?
A tiny blocking inline script in `<head>` sets `data-nx-theme` from `localStorage` (or `prefers-color-scheme`) before any CSS is parsed.

### Why do my `premium` / `cartoon` / `lib` components look uncoloured?
Their accent colours come from family-specific variables (`--nx-premium-gold`, `--nx-cartoon-coral`, `--nx-lib-cyan`, …) that only exist if you apply the family theme: `App(theme=PREMIUM_THEME)` (or `CARTOON_THEME` / `LIB_THEME`). See [std → apply the family theme](std.md#apply-the-family-theme-important), including how to mix families on one page.

### Why do my scoped classes have different names on another machine?
The class hash comes from the Rust `hash_asset` when the extension is loaded (10 hex characters) and from `blake2b` otherwise (8 hex). Behaviour is identical; only the name differs. Don't hard-code generated names.

### Why does a scoped class created after an event have no styling?
Scoped-class CSS is emitted in `<head>` with the first response only. Create every class a page may need during the first render, or use inline `style=`.

### Why are animations/charts not moving?
Each moving component needs its one-per-page helper: `animation_runtime()` + `reveal_styles()` (reveals, counters, text effects), `keyframes_style()` (keyframes engine), `charts_runtime()` + `chart_styles()` (chart entrances), `physics2d_runtime()`, `observer_runtime()`, `scroll_runtime()`, `premium_keyframes()` / `cartoon_keyframes()` / `lib_keyframes()`. Without them, components render statically.

### Why two `Icon` classes?
`nexoria.iconify.Icon` is a web component that fetches from Iconify's API (150k+ icons, needs network). `nexoria.std.icons.Icon` renders 2,078 vendored Bootstrap Icons as inline SVG with no network. Use the former for breadth, the latter for reliability.

### Why does `std` need no `App` flag?
It is pure Python: styling is inline, and interactivity is either literal HTML attributes or small inline scripts that guard against double registration. There is nothing external to load.

### Why are there three charting options?
`std.charts` (SVG, zero dependencies, ideal for dashboards/KPIs), `nexoria.chartjs` (full Chart.js feature set via CDN), and plain `std.svg` (draw your own). Pick by need.

### `animate_in` vs GSAP — which should I use?
`std.animation` covers reveals, counters, text effects and keyframes with no dependency. Use GSAP (`nexoria.gsap`) for timelines, scroll-scrubbing and its plugin ecosystem.

---

## D. Integrations

### Why CDN-loaded libraries instead of bundling them?
Nothing is added to the Python install, versions are pinned in code, and pages that don't use a library never load it. If you need offline or CSP-strict deployments, self-host the files and change the URLs.

### Why one merged import map?
Browsers honour a single import map per document. Nexoria merges every enabled ES-module integration's entries (three, gsap, chart.js, aggrid, spline, …) into one.

### Why do video.js, OpenLayers, Bootstrap and Tailwind use classic script tags?
Their ES builds are deep dependency chains that don't resolve cleanly through an import map; their UMD/global builds are self-contained.

### Why do widgets I add after an event not appear?
Adapters mount once at page load. For elements inserted by later patches, call `window.__nexoria__.<name>.mountNew()` (for example from a literal `onclick`).

### Why is `Grid(theme="alpine")` unstyled?
Only the **Quartz** theme CSS is linked automatically. Add the CSS for other AG Grid themes yourself.

### Why does `Mesh(geometry="model.glb")` show a box?
The Three.js adapter supports `box`, `sphere`, `plane`, `torus`; unknown values fall back to a box. For glTF/VRM avatars use [`vroid`](vroid.md).

### Is `nexoria.translate` reliable?
It uses Google's unofficial web endpoint, with no guarantees. Prefer the official Cloud Translation API for anything critical.

### Why does Shiki load from esm.sh?
Its dependency tree is too deep to hand-assemble as an import map, so it uses a bundling CDN. Self-host if that trust posture doesn't suit you.

---

## E. Native tiers and tooling

### Do I need Rust, C++, Go or CUDA?
No. Every tier is optional and has a fallback. The framework runs on pure Python with only its five PyPI dependencies.

### Why have three differs (Python, Rust, C++)?
Python is the always-available reference; the PyO3 Rust build is the easy, wheel-friendly acceleration; the C++ engine is the "maximum speed" tier. They share one algorithm and one test-vector suite, and the fastest available wins automatically. Check with `hot_path_active()` or `nexoria doctor`.

### Why does the C++ VDOM depend on a Rust crate?
Diff keys are strings whose lifetimes are easy to get wrong in C++ (dangling pointers, missing terminators, double frees). The Rust `nexoria-safety-core` interner owns every string and hands C++ a stable integer id, so key comparison is an integer equality check and the memory-safety-critical part lives in a memory-safe language. Every export is wrapped in `catch_unwind` so a panic can't cross the FFI boundary.

### Why isn't the GPU used for the VDOM diff?
A single tree diff is branchy, pointer-chasing work that suits CPUs. The GPU tier is for genuinely parallel batch operations (`batch_hash`, `batch_row_diff`).

### Why does the JS engine use QuickJS-ng and not V8 or Node?
It is small, embeddable and compiles with a normal C++ toolchain — no Node install needed at runtime. The trade-off: no DOM, no Node built-ins, no event loop, no native add-ons. It runs the pure-JS subset of npm, not everything.

### Why does the npm client fetch only one package without dependencies?
It is a minimal fetch-and-extract helper (no resolver, no lockfile, no install scripts) — safer and simpler, at the cost of not handling packages with transitive dependencies.

### Why a Go server in front of Python?
To give production a fast, cache-backed static path, gzip, real timeouts and a built-in request firewall, in one dependency-free binary, without reimplementing routing/rendering. It reverse-proxies everything dynamic (including WebSocket upgrades) to the unchanged Python app on loopback.

### Why doesn't `native build` run automatically at install time?
Compiling C++/Rust/Go/CUDA needs toolchains most users don't have. You opt in with `nexoria native build`; `nexoria doctor` tells you exactly what is and isn't active.

### Why `doctor` says a module is "built for a different interpreter"?
Compiled modules are tied to interpreter version, OS and architecture (ABI tag). A `.so` built for CPython 3.12 Linux won't load on 3.13 or Windows. Rebuild with the interpreter you actually run.

### Why does `nexoria build` write `dist/` but nothing changes in my app?
`App` serves the un-hashed `/_nexoria/*` runtime and doesn't read `manifest.json`. Publish `dist/` yourself (CDN/proxy) and reference the hashed files. See [tools](tools.md).

### Why Node.js for the build tool if the framework is Python?
esbuild and Tailwind's CLI are Node-based and best-in-class. Node is needed only at build time, and `nexoria build` skips gracefully if it is absent.

---

## F. Deployment and scaling

### How do I deploy?
Simplest: `python app.py` (or `uvicorn app:app`) behind a TLS-terminating reverse proxy that forwards WebSocket upgrades on `/_nexoria/live`. Better: build the Go edge server (`nexoria native build --with-go-server`) and let `App.run()` place it in front automatically, with a firewall.

### Can I run multiple workers?
Sessions are stored in each process's memory, so a socket must reach the same process that rendered the page. Run one worker per address or use sticky routing (by IP hash or session cookie); otherwise events are silently ignored.

### What happens if the server restarts?
Open pages lose their sessions; their events are ignored until the page is reloaded (which creates a new session). The runtime reconnects the socket automatically with back-off.

### How much memory does a page cost?
One component instance, one element tree and one handler map, held from page load until the socket closes.

### Is the Python-only path safe to expose to the internet?
It has no firewall, rate limiting or CORS handling. Use the Go edge (firewall on by default) or a hardened reverse proxy.

### How do I serve static files?
Behind the Go edge, `static_dir` is served natively at `/static`. On the plain-uvicorn path `/static` is currently shadowed by the catch-all route ([details](core.md#known-issues)); serve files from a reverse proxy/CDN or mount your own `StaticFiles` before the catch-all.

### Can I package it as a desktop or mobile app?
Desktop: `nexoria build-desktop` scaffolds Electron around your local Python server. Mobile: `nexoria build-mobile` scaffolds a Capacitor shell that loads your **deployed** server URL — it is not an offline app. See [desktop](desktop.md), [mobile](mobile.md).

---

## G. How do I…?

### …add authentication or redirect unauthenticated users?
Use a middleware that returns a redirect response, or a route guard (`guards=[...]`, which receives path params only). Cookies come from `request.cookies` in middleware.

### …add my own third-party library?
Follow the adapter pattern ([ARCHITECTURE §9](ARCHITECTURE.md#9-integration-adapter-architecture)): a dataclass whose `to_element()` emits a `div` with a class and a JSON `data-*` spec; a small adapter that scans for the class; then load the library with a `Script` or your own `<script>` in an `el("script", src=…)`.

### …run raw JavaScript?
`Script("…", on_ready=True)` for a block; `JSFunction` to define callable functions; `js()` to embed values safely. See [js](js.md).

### …embed a chart with no JavaScript library?
`std.charts` (SVG, zero dependencies) — see [charts](std/charts.md).

### …mix design systems on one page?
Keep the default theme and declare only the family tokens you use ([recipe](std.md#apply-the-family-theme-important)).

### …test my app?
Use Starlette's `TestClient`: `client.get("/")` for SSR and `client.websocket_connect("/_nexoria/live")` for events (the repo's `tests/test_websocket_interactivity.py` is a template). Read the session id and handler ids from the hydration JSON.

### …write my own component?
A function that returns `el(...)`. No base class needed:

```python
def price_tag(amount):
    return el("span", f"${amount:,.2f}", class_="nx-badge")
```

### …check which native tiers are active?
`nexoria doctor` (or `--json`), or in code: `from nexoria.render.diff import hot_path_active`.

---

## H. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `/static/...` returns the styled 404 | Catch-all route shadows the static mount (plain-uvicorn path) | Use the Go edge, a proxy/CDN, or mount `StaticFiles` first |
| Family colours missing | Family theme not applied | `App(theme=PREMIUM_THEME)` etc. |
| Animation/chart appears but never moves | One-per-page helper not rendered | See "Why are animations/charts not moving?" |
| Clicking does nothing after an error | Handler exception ended the live channel | Reload; catch errors in handlers |
| Clicking does nothing after a server restart | Session no longer exists | Reload the page |
| Clicking does nothing with several workers | Socket reached a worker without the session | One worker or sticky sessions |
| Widget added by an event is blank | Adapter mounted only at load | `window.__nexoria__.<lib>.mountNew()` |
| AG Grid looks unstyled | Non-Quartz theme requested | Link the theme CSS yourself |
| `RuntimeError` from `run(reload=True)` | App not bound to a top-level variable in a `.py` file | Assign `app = App(...)` at module level |
| `ValueError` at `App(...)` about a GSAP plugin | Unknown plugin name | Use a name from `GSAP_ALL_PLUGINS` |
| `ValueError` from `run(firewall=…)` | Unknown firewall key | Use the documented keys |
| `NativeEngineUnavailable` from `Runtime()` | JS engine not built | `nexoria native build` (not `--vdom-only`) |
| `IconNotFoundError` | Name not in the vendored set | `list_icons()` / `has_icon()` |
| `ERROR tests/test_std.py::testimonial` | pytest collects the imported `testimonial` function | Alias the import (see [tests](tests.md)) |
| Webcam blank | Not HTTPS/localhost, or permission denied | Serve over HTTPS; allow camera |
| 3D scene blank | No WebGL | Try another browser/GPU setting |

---

## I. Known limitations

The complete, current list is in [ARCHITECTURE §15](ARCHITECTURE.md#15-known-limitations-summary). In short: `/static` shadowing on the plain path, custom-404 status, silent handler-exception behaviour, no push on background state changes, unused lifecycle hooks, keyed-diff reorder/multi-remove, scoped-CSS timing, family-theme requirement, placeholder CORS middleware, un-served `dist/`, and AG Grid's single auto-linked theme.
