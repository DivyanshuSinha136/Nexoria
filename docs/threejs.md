# `nexoria.threejs`

> Describe a Three.js scene declaratively in Python; a small adapter builds real `THREE.*` objects in the browser.

| | |
|---|---|
| **Import** | `from nexoria.threejs import Scene, Mesh, Light, Camera` |
| **Enabled by** | `App(threejs=True)` |
| **Library** | Three.js 0.165.0 from unpkg, via the shared import map (`"three"`) |
| **Adapter** | `runtime/three-adapter.js` (ES module) |
| **Python dependency** | none |
| **Needs** | A browser with WebGL/GPU |

## Quick start

```python
from nexoria import App, Component, el, Router
from nexoria.threejs import Scene, Mesh, Light, Camera

class Cube(Component):
    def render(self):
        scene = Scene(
            camera=Camera(position=(0, 1, 4)),
            lights=[Light("ambient", intensity=0.6), Light("directional", position=(3, 5, 2))],
            background="#14141f",
        )
        scene.add(Mesh(geometry="box", color="#6366f1", animate="rotate_y"))
        return el("div", el("h1", "3D"), scene.to_element())

app = App(name="3D", router=Router().add("/", Cube), threejs=True)
```

## How it works

`Scene.to_element()` returns `<div class="nx-three-scene" data-nx-scene='{…json…}' style="width:…;height:…">`. On load the adapter parses the JSON, builds camera, lights and meshes, appends a `WebGLRenderer` canvas, runs a `requestAnimationFrame` loop and handles window resize.

## Supported values (as implemented by the adapter)

| Field | Values |
|---|---|
| `Mesh.geometry` | `"box"`, `"sphere"`, `"plane"`, `"torus"` — **any other value falls back to a box** (the "custom glTF url" mentioned in the dataclass comment is not implemented; for glTF/VRM use [`vroid`](vroid.md) or raw JS) |
| `Mesh.material` | `"standard"` (default), `"basic"`, `"phong"` |
| `Mesh.animate` | `"rotate_y"`, `"rotate_x"` (0.01 rad per frame) |
| `Camera.kind` | `"perspective"` (uses `fov`), `"orthographic"` (frustum derived from the container size) |
| `Light.kind` | `"ambient"`, `"directional"`, `"point"` |

There is no orbit control or picking; the scene is display-only. `Mesh.key` is serialised but not used by the adapter.

## API reference

### Classes

#### `class Scene(camera: Camera = ..., lights: list[Light] = ..., meshes: list[Mesh] = ..., background: str = '#0b0b12', width: str = '100%', height: str = '480px') -> None`

Scene(camera: 'Camera' = <factory>, lights: 'list[Light]' = <factory>, meshes: 'list[Mesh]' = <factory>, background: 'str' = '#0b0b12', width: 'str' = '100%', height: 'str' = '480px')

- **`.add(mesh: Mesh) -> 'Scene'`**
- **`.to_dict() -> dict`**
- **`.to_element()`** — Return a Nexoria `Element` (a <canvas> + data attribute) for use in render().

#### `class Mesh(geometry: str = 'box', material: str = 'standard', color: str = '#4477ff', position: tuple = (0, 0, 0), rotation: tuple = (0, 0, 0), scale: tuple = (1, 1, 1), key: Optional[str] = None, animate: Optional[str] = None) -> None`

Mesh(geometry: 'str' = 'box', material: 'str' = 'standard', color: 'str' = '#4477ff', position: 'tuple' = (0, 0, 0), rotation: 'tuple' = (0, 0, 0), scale: 'tuple' = (1, 1, 1), key: 'Optional[str]' = None, animate: 'Optional[str]' = None)

- **`.to_dict() -> dict`**

#### `class Light(kind: str = 'ambient', color: str = '#ffffff', intensity: float = 1.0, position: tuple = (5, 5, 5)) -> None`

Light(kind: 'str' = 'ambient', color: 'str' = '#ffffff', intensity: 'float' = 1.0, position: 'tuple' = (5, 5, 5))

- **`.to_dict() -> dict`**

#### `class Camera(kind: str = 'perspective', fov: float = 75, position: tuple = (0, 0, 5), look_at: tuple = (0, 0, 0)) -> None`

Camera(kind: 'str' = 'perspective', fov: 'float' = 75, position: 'tuple' = (0, 0, 5), look_at: 'tuple' = (0, 0, 0))

- **`.to_dict() -> dict`**
