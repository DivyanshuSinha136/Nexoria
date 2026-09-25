# `nexoria.webcam`

> Live camera preview with snapshot, camera flip and stop, via webcam-easy.

| | |
|---|---|
| **Import** | `from nexoria.webcam import Webcam` |
| **Enabled by** | `App(webcam=True)` |
| **Library** | `webcam-easy` 1.1.1 (import map) |
| **Adapter** | `runtime/webcam-adapter.js`; `window.__nexoria__.webcam.{instances,get,start,stop,flip,snap,mountNew}`; event `nexoria:webcam:snap` (`detail.dataUrl`) |
| **Needs** | HTTPS or `localhost`, and the user's camera permission (browser requirements) |

```python
cam = Webcam(camera_id="my-cam", facing_mode="user")
el("div", cam.to_element(),
   el("button", "Snap", onclick=cam.snap_attr()),
   el("button", "Switch", onclick=cam.flip_attr()),
   el("button", "Stop", onclick=cam.stop_attr()))
```

`Webcam(facing_mode="user", width="480px", height="360px", autostart=True, camera_id=None)` — `autostart=False` leaves the preview stopped until you call `start`.

The last frame is a data URL at `window.__nexoria__.webcam.get("my-cam").lastSnapshot`, and is also delivered in the `nexoria:webcam:snap` event.

## API reference

### Classes

#### `class Webcam(facing_mode: str = 'user', width: str = '480px', height: str = '360px', autostart: bool = True, camera_id: Optional[str] = None) -> None`

A live webcam preview with snapshot capture.

Access the last captured frame (a data URL) via `window.__nexoria__.webcam.get(camera_id).lastSnapshot`, or listen for the `nexoria:webcam:snap` DOM event.

- **`.flip_attr() -> str`**
- **`.snap_attr() -> str`**
- **`.stop_attr() -> str`**
- **`.to_dict() -> dict`**
- **`.to_element()`**

### Constants

| Name | Value |
|---|---|
| `WEBCAM_IMPORTS` | `{'webcam-easy': 'https://unpkg.com/webcam-easy@1.1.1/src/webcam-easy.js'}` |
| `WEBCAM_ADAPTER_TAG` | `'<script src="/_nexoria/webcam-adapter.js" type="module" defer></script>'` |
| `WEBCAM_CDN` | `'https://unpkg.com/webcam-easy@1.1.1/src/webcam-easy.js'` |
