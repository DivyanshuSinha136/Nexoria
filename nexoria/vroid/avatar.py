"""
nexoria.vroid.avatar
=======================
Optional 3D layer for displaying VRM avatars (the format produced by
VRoid Studio and the wider VRM/VRoid ecosystem). Reference a `.vrm`
file URL declaratively in Python; the client adapter
(`runtime/vroid-adapter.js`, loaded only when `App(vroid=True)` is set)
loads and renders it with a real Three.js scene + `@pixiv/three-vrm`
(the standard, official VRM loader plugin for Three.js).

Verified dependency chain: `@pixiv/three-vrm`'s ESM build bundles all
of its own `@pixiv/three-vrm-*` sub-packages internally -- its only
external import is `three` itself (a declared peer dependency).
Loading a VRM also needs Three.js's `GLTFLoader` (VRM is built on
glTF), which lives at `three/examples/jsm/loaders/GLTFLoader.js` --
checked recursively against the real published `three` package and
confirmed to depend on nothing beyond `three` itself, so a `"three/"`
prefix entry in the import map (in addition to the exact `"three"`
entry ThreeJS/GSAP-adjacent code already needs) is enough to resolve
it.

Honest scope: like `nexoria.threejs.Scene` and `nexoria.spline.SplineScene`,
this renders real WebGL content -- it needs an actual browser with a
GPU/WebGL context, and there's no server-side or headless way to
verify the pixels it produces. What's verified here is the dependency
chain above (against the real published packages) and that the
declarative spec is built and serialized correctly.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import json
import uuid

from ..threejs.scene import THREEJS_CDN

VRM_VERSION = "3.5.5"
VRM_CDN = f"https://unpkg.com/@pixiv/three-vrm@{VRM_VERSION}/lib/three-vrm.module.js"
_THREE_BASE = THREEJS_CDN.rsplit("/build/", 1)[0] + "/"
VROID_IMPORTS = {
    "three": THREEJS_CDN,
    "three/": _THREE_BASE,  # enables "three/examples/jsm/..." (GLTFLoader) resolution
    "@pixiv/three-vrm": VRM_CDN,
}
VROID_ADAPTER_TAG = '<script src="/_nexoria/vroid-adapter.js" type="module" defer></script>'


@dataclass
class VRMAvatar:
    """
    A VRM avatar (from VRoid Studio or anywhere else in the VRM
    ecosystem), rendered with a real Three.js scene.

        VRMAvatar("/static/avatar.vrm", camera_position=(0, 1.2, 3))

    Spring-bone physics and look-at are driven automatically each
    frame (the adapter calls the loaded VRM's own `.update(delta)`).
    For anything beyond the basics here (custom lighting, animation
    clips, expression control), use `window.__nexoria__.vroid.get(id)`
    to reach the real Three.js scene/camera/VRM instance directly.
    """
    url: str
    width: str = "100%"
    height: str = "480px"
    background: str = "#0b0b12"
    camera_position: tuple = (0, 1.2, 3)
    look_at: tuple = (0, 1, 0)
    auto_rotate: bool = False
    avatar_id: Optional[str] = None

    def __post_init__(self):
        if self.avatar_id is None:
            self.avatar_id = f"nx-vroid-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "background": self.background,
            "cameraPosition": list(self.camera_position),
            "lookAt": list(self.look_at),
            "autoRotate": self.auto_rotate,
        }

    def to_element(self):
        from ..core.element import el
        return el(
            "div",
            id=self.avatar_id,
            **{"class": "nx-vroid-avatar", "data-nx-vroid": json.dumps(self.to_dict())},
            style=f"width:{self.width};height:{self.height};",
        )
