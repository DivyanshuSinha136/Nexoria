# `nexoria.spline`

> Embed a scene exported from [Spline](https://spline.design) by its `.splinecode` URL.

| | |
|---|---|
| **Import** | `from nexoria.spline import SplineScene` |
| **Enabled by** | `App(spline=True)` |
| **Library** | `@splinetool/runtime` 2.0.14 (self-contained ES build) via the import map |
| **Adapter** | `runtime/spline-adapter.js`; `window.__nexoria__.spline.{apps,get,mountNew}`; event `nexoria:spline:ready` |
| **Needs** | WebGL-capable browser |

```python
scene = SplineScene("https://prod.spline.design/abc123/scene.splinecode", height="520px")
el("div", scene.to_element(),
   el("button", "Spin", onclick=scene.emit_event_attr("mouseDown", "Cube")))
```

`SplineScene(url, width="100%", height="480px", background=None, scene_id=None)`; `scene_id` auto-generates. `emit_event_attr(event, object_name)` returns a client-side `onclick` string that calls `app.emitEvent(...)` on the loaded Spline `Application` (guarded so it does nothing before the scene loads). Use `window.__nexoria__.spline.get(id)` for the full `Application`.

## API reference

### Classes

#### `class SplineScene(url: str, width: str = '100%', height: str = '480px', background: Optional[str] = None, scene_id: Optional[str] = None) -> None`

A Spline scene, referenced by its exported `.splinecode` URL (from Spline's own "Export > Code Export > Viewer code" panel, or a file you host yourself).

`events` maps Spline object names to a `nexoria.core.element`-style `onclick=`-equivalent: since Spline objects aren't real DOM nodes, interaction is wired through the runtime's own event API instead -- see `.on_click_attr(object_name)` for a plain `onclick=` string you can attach to an ordinary button to trigger a named Spline event (`app.emitEvent('mouseDown', objectName)`), and `window.__nexoria__.spline.get(id)` for direct access to the loaded `Application` instance for anything more advanced.

- **`.emit_event_attr(event_name: str, object_name: str) -> str`** — A plain `onclick=`-style string (purely client-side, no server round-trip) that tells this scene's loaded Spline `Application` to emit an event for a named object -- e.g. to trigger an interaction Spline's own editor defined:
- **`.to_dict() -> dict`**
- **`.to_element()`**

### Constants

| Name | Value |
|---|---|
| `SPLINE_IMPORTS` | `{'@splinetool/runtime': 'https://unpkg.com/@splinetool/runtime@2.0.14/build/runtime.js'}` |
| `SPLINE_ADAPTER_TAG` | `'<script src="/_nexoria/spline-adapter.js" type="module" defer></script>'` |
| `SPLINE_CDN` | `'https://unpkg.com/@splinetool/runtime@2.0.14/build/runtime.js'` |
