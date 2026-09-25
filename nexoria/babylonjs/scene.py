"""
nexoria.babylonjs.scene
==========================
Optional 3D layer using Babylon.js (an alternative engine to
nexoria.threejs.Scene). Describe a scene declaratively in Python;
the client adapter (runtime/babylon-adapter.js, loaded only when
App(babylonjs=True) is set) builds a real Babylon.js scene.

Verified dependency chain: scanned all 3322 .js files in
@babylonjs/core's published package -- zero external static imports.
Genuinely self-contained, same situation as Three.js.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import json

BABYLON_VERSION = "9.23.0"
BABYLONJS_CDN = f"https://unpkg.com/@babylonjs/core@{BABYLON_VERSION}/index.js"
BABYLONJS_IMPORTS = {"@babylonjs/core": BABYLONJS_CDN}
BABYLONJS_ADAPTER_TAG = '<script src="/_nexoria/babylon-adapter.js" type="module" defer></script>'


@dataclass
class BabylonMesh:
    """One primitive mesh: `type` is "box"|"sphere"|"ground"|"cylinder"|"torus"."""
    type: str = "box"
    size: float = 1.0
    color: str = "#4477ff"
    position: tuple = (0, 0, 0)
    rotation: tuple = (0, 0, 0)
    animate: Optional[str] = None  # "rotate_y", etc.
    key: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "type": self.type, "size": self.size, "color": self.color,
            "position": list(self.position), "rotation": list(self.rotation),
            "animate": self.animate,
        }


@dataclass
class BabylonScene:
    """
    A Babylon.js scene rendered into a `<canvas>`.

        scene = BabylonScene()
        scene.add(BabylonMesh("sphere", color="#22d3ee", animate="rotate_y"))
        el("div", scene.to_element())
    """
    meshes: list[BabylonMesh] = field(default_factory=list)
    background: str = "#0b0b12"
    camera_alpha: float = -1.57
    camera_beta: float = 1.2
    camera_radius: float = 6.0
    width: str = "100%"
    height: str = "480px"

    def add(self, mesh: BabylonMesh) -> "BabylonScene":
        self.meshes.append(mesh)
        return self

    def to_dict(self) -> dict:
        return {
            "meshes": [m.to_dict() for m in self.meshes],
            "background": self.background,
            "camera": {"alpha": self.camera_alpha, "beta": self.camera_beta, "radius": self.camera_radius},
        }

    def to_element(self):
        from ..core.element import el
        return el(
            "canvas",
            **{"class": "nx-babylon-scene", "data-nx-babylon": json.dumps(self.to_dict())},
            style=f"width:{self.width};height:{self.height};display:block;touch-action:none;",
        )
