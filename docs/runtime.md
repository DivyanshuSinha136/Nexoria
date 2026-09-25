# `runtime` — the browser side

> `nexoria/runtime/` holds every file served to the browser under `/_nexoria/`: the hydration/patch client, base CSS, the favicon, and one small adapter per optional integration.

| | |
|---|---|
| **Source** | `nexoria/runtime/` |
| **Served by** | `App` (`GET /_nexoria/{filename}`) or the Go edge server (from an in-memory cache) |
| **Dependencies** | none — hand-written, no build step required |
| **Related** | [`render`](render.md), [`core`](core.md), [`tools`](tools.md) |

## Files

| File | Size | Role |
|---|---:|---|
| `runtime.js` | 6.5 KB | Hydration, WebSocket client, patch applier, event delegation, theme toggle |
| `base.css` | 5.2 KB | The `nx-*` base classes, reset, theme-toggle and spinner |
| `falcon-nexoria.svg` / `.ico` | 59 KB / 104 KB | Default favicon (framework mark) |
| `three-adapter.js` | 3.2 KB | `nexoria.threejs` → Three.js scene |
| `gsap-adapter.js` | 4.3 KB | `nexoria.gsap` → GSAP timelines + plugin registration |
| `chartjs-adapter.js` | 1.0 KB | `nexoria.chartjs` → Chart.js |
| `videojs-adapter.js` | 5.7 KB | `nexoria.videojs` → video.js |
| `aggrid-adapter.js` | 1.5 KB | `nexoria.aggrid` → AG Grid |
| `spline-adapter.js` | 1.5 KB | `nexoria.spline` → Spline runtime |
| `vroid-adapter.js` | 3.5 KB | `nexoria.vroid` → three-vrm |
| `babylon-adapter.js` | 3.1 KB | `nexoria.babylonjs` → Babylon.js |
| `bootstrap-adapter.js` | 2.3 KB | Tooltip/popover init; syncs `data-bs-theme` with `data-nx-theme` |
| `qrcode-adapter.js`, `barcode-adapter.js`, `shiki-adapter.js`, `openlayers-adapter.js`, `webcam-adapter.js` | 0.8–2.4 KB | One per integration |

(Sizes are unminified source.)

## `runtime.js`

An IIFE that:

1. Reads the JSON in `#nx-hydration-data` (route, tree, component name, **session id**).
2. Opens `ws(s)://<host>/_nexoria/live`, reconnecting with exponential back-off (500 ms → 8 s).
3. **Delegates events.** One capture-phase listener per event type (`click`, `input`, `change`, `submit`, `keydown`, `keyup`) walks up from the target looking for `data-nx-on-<type>`; on a hit it sends
   ```json
   {"event": "click", "handler_id": "h3", "session": "<id>", "payload": {"value": null, "key": null}}
   ```
   `payload.value` is `event.target.value` when the target has one; `payload.key` is `event.key`. `submit` events are `preventDefault()`-ed.
4. **Applies patches** (`text`, `replace`, `insert`, `remove`, `update_props`) sequentially to the DOM, addressing nodes by child-index path starting at the first element child of `#nx-root`. There is no client-side virtual DOM.
5. Exposes `window.__nexoria__ = { hydration, applyPatches, sessionId, toggleTheme }`, **merging** into any namespace adapters already created.

Only the six event types above are delegated. Other events (`mouseover`, `focus`, `scroll`, …) can't be bound with `on_*`; use a literal `onmouseover="…"` attribute or a [`Script`](js.md).

If the socket is closed when an event fires, the event is dropped (no queue).

## Adapter convention

Every adapter follows one pattern:

- Server-side wrapper emits an element with a class (`nx-chartjs-canvas`, `nx-qrcode`, …) and a `data-nx-*` attribute holding a JSON spec.
- The adapter scans for that class on load and builds the real library object.
- It registers a namespace on `window.__nexoria__.<name>` and, for most, a `mountNew()` to re-scan after DOM changes it can't see. Several also dispatch a `nexoria:<name>:ready` `CustomEvent`.

| Namespace | Useful members |
|---|---|
| `gsap` | `timelines`, `plugins`, `ready` (promise), `play/pause/restart/reverse(name)` |
| `videojs` | `players`, `get/play/pause/dispose(id)`, `mountNew()`; event `nexoria:videojs:ready` |
| `aggrid` | `grids`, `get(id)`, `setRowData(id, rows)`, `mountNew()`; event `nexoria:aggrid:ready` |
| `spline` | `apps`, `get(id)`, `mountNew()`; event `nexoria:spline:ready` |
| `vroid` | `avatars`, `get(id)`, `mountNew()`; event `nexoria:vroid:ready` |
| `babylon` | `scenes`, `mountNew()`; event `nexoria:babylon:ready` |
| `openlayers` | `get(id)`, `mountNew()`; event `nexoria:openlayers:ready` |
| `webcam` | `instances`, `get/start/stop/flip/snap(id)`, `mountNew()`; event `nexoria:webcam:snap` |
| `qrcode` | `instances`, `mountNew()` |
| `barcode`, `shiki`, `bootstrap` | `mountNew()` |
| `chartjs` | `charts` |

Because adapters mount on load, widgets added by a **later WebSocket patch** are not auto-mounted (except where Tailwind's own observer applies). Call the relevant `mountNew()` after such a patch (for example from a literal `onclick`).

## `base.css`

Reset plus: `nx-container`, `nx-card`, `nx-nav`, `nx-btn`, `nx-btn-ghost`, `nx-btn-danger`, `nx-badge`, `nx-row`, `nx-stack`, `nx-center`, `nx-spinner`, `nx-theme-toggle`, all driven by the `--nx-*` variables from [`style`](style.md).

## Production hashing

`nexoria build` copies `runtime.js` and every `*-adapter.js` to `dist/` with content-hashed names and records them in `dist/manifest.json` — see [`tools`](tools.md). `App` itself continues to serve the un-hashed `/_nexoria/*` files; wiring `dist/` into your deployment (e.g. a CDN) is up to you.
