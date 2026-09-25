# `nexoria.vroid`

> Display a VRM avatar (VRoid Studio and the VRM ecosystem) with Three.js and `@pixiv/three-vrm`.

| | |
|---|---|
| **Import** | `from nexoria.vroid import VRMAvatar` |
| **Enabled by** | `App(vroid=True)` (may be combined with `threejs=True`) |
| **Library** | `@pixiv/three-vrm` 3.5.5 + Three.js (same pinned URL as [`threejs`](threejs.md)); the import map also has a `"three/"` prefix so `three/examples/jsm/loaders/GLTFLoader.js` resolves |
| **Adapter** | `runtime/vroid-adapter.js`; `window.__nexoria__.vroid.{avatars,get,mountNew}`; event `nexoria:vroid:ready` |
| **Needs** | WebGL-capable browser |

```python
avatar = VRMAvatar("/static/avatar.vrm", camera_position=(0, 1.2, 3), auto_rotate=True)
el("div", avatar.to_element())
```

Spring-bone physics and look-at run every frame (the adapter calls the VRM's own `update(delta)`). For lighting, animation clips or expressions, use `window.__nexoria__.vroid.get(id)` to reach the Three.js scene, camera and VRM instance.

## API reference

### Classes

#### `class VRMAvatar(url: str, width: str = '100%', height: str = '480px', background: str = '#0b0b12', camera_position: tuple = (0, 1.2, 3), look_at: tuple = (0, 1, 0), auto_rotate: bool = False, avatar_id: Optional[str] = None) -> None`

A VRM avatar (from VRoid Studio or anywhere else in the VRM ecosystem), rendered with a real Three.js scene.

Spring-bone physics and look-at are driven automatically each frame (the adapter calls the loaded VRM's own `.update(delta)`). For anything beyond the basics here (custom lighting, animation clips, expression control), use `window.__nexoria__.vroid.get(id)` to reach the real Three.js scene/camera/VRM instance directly.

- **`.to_dict() -> dict`**
- **`.to_element()`**

### Constants

| Name | Value |
|---|---|
| `VROID_IMPORTS` | `{'three': 'https://unpkg.com/three@0.165.0/build/three.module.js', 'three/': 'https://unpkg.com/three@0.165.0/', '@pixiv/three-vrm': 'https://unpkg.com/@pixiv/three-vrm@3.5.5/lib/three-vrm.module.js'}` |
| `VROID_ADAPTER_TAG` | `'<script src="/_nexoria/vroid-adapter.js" type="module" defer></script>'` |
| `VRM_CDN` | `'https://unpkg.com/@pixiv/three-vrm@3.5.5/lib/three-vrm.module.js'` |
