# `nexoria.babylonjs`

> An alternative 3D engine: declare a Babylon.js scene of primitive meshes in Python.

| | |
|---|---|
| **Import** | `from nexoria.babylonjs import BabylonScene, BabylonMesh` |
| **Enabled by** | `App(babylonjs=True)` |
| **Library** | `@babylonjs/core` 9.23.0 via the import map |
| **Adapter** | `runtime/babylon-adapter.js`; `window.__nexoria__.babylon.{scenes,mountNew}`; event `nexoria:babylon:ready` |

```python
scene = BabylonScene(background="#0b0b12")
scene.add(BabylonMesh("sphere", color="#22d3ee", animate="rotate_y"))
el("div", scene.to_element())
```

`BabylonMesh.type` is one of `box`, `sphere`, `ground`, `cylinder`, `torus`; `animate` supports `rotate_y` and `rotate_x`. The camera is an arc-rotate style camera driven by `camera_alpha`, `camera_beta`, `camera_radius`.

## API reference

### Classes

#### `class BabylonScene(meshes: list[BabylonMesh] = ..., background: str = '#0b0b12', camera_alpha: float = -1.57, camera_beta: float = 1.2, camera_radius: float = 6.0, width: str = '100%', height: str = '480px') -> None`

A Babylon.js scene rendered into a `<canvas>`.

scene = BabylonScene() scene.add(BabylonMesh("sphere", color="#22d3ee", animate="rotate_y")) el("div", scene.to_element())

- **`.add(mesh: BabylonMesh) -> 'BabylonScene'`**
- **`.to_dict() -> dict`**
- **`.to_element()`**

#### `class BabylonMesh(type: str = 'box', size: float = 1.0, color: str = '#4477ff', position: tuple = (0, 0, 0), rotation: tuple = (0, 0, 0), animate: Optional[str] = None, key: Optional[str] = None) -> None`

One primitive mesh: `type` is "box"|"sphere"|"ground"|"cylinder"|"torus".

- **`.to_dict() -> dict`**

### Constants

| Name | Value |
|---|---|
| `BABYLONJS_IMPORTS` | `{'@babylonjs/core': 'https://unpkg.com/@babylonjs/core@9.23.0/index.js'}` |
| `BABYLONJS_ADAPTER_TAG` | `'<script src="/_nexoria/babylon-adapter.js" type="module" defer></script>'` |
| `BABYLONJS_CDN` | `'https://unpkg.com/@babylonjs/core@9.23.0/index.js'` |
