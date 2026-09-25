"""
nexoria.threejs.scene
========================
Optional 3D layer. Describe a Three.js scene declaratively in Python;
Nexoria serializes it to a JSON scene-graph that the client runtime's
ThreeJS adapter (`runtime/three-adapter.js`, loaded only when a scene
is present) turns into real `THREE.*` objects. Three.js itself is
pulled from CDN (or a bundled copy via the Node build) — never a
Python dependency, keeping `pip install nexoria` lightweight.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

THREEJS_CDN = "https://unpkg.com/three@0.165.0/build/three.module.js"
# Split into import-map entries + adapter tag (rather than one combined
# string) so App._build_head() can merge entries from every enabled
# ESM-based integration (ThreeJS, GSAP, Chart.js) into a SINGLE
# `<script type="importmap">` -- browsers only honor one import map per
# document, so each feature emitting its own would silently break
# whichever loaded second when more than one is enabled at once.
THREEJS_IMPORTS = {"three": THREEJS_CDN}
THREEJS_ADAPTER_TAG = '<script src="/_nexoria/three-adapter.js" type="module" defer></script>'
# Kept for anyone importing this directly; App itself uses the split
# constants above instead so multiple integrations merge correctly.
THREEJS_RUNTIME_TAG = (
    f'<script type="importmap">{{"imports": {{"three": "{THREEJS_CDN}"}}}}</script>\n'
    f'{THREEJS_ADAPTER_TAG}'
)


@dataclass
class Camera:
    kind: str = "perspective"          # "perspective" | "orthographic"
    fov: float = 75
    position: tuple = (0, 0, 5)
    look_at: tuple = (0, 0, 0)

    def to_dict(self) -> dict:
        return {"kind": self.kind, "fov": self.fov, "position": self.position, "lookAt": self.look_at}


@dataclass
class Light:
    kind: str = "ambient"              # "ambient" | "directional" | "point"
    color: str = "#ffffff"
    intensity: float = 1.0
    position: tuple = (5, 5, 5)

    def to_dict(self) -> dict:
        return {"kind": self.kind, "color": self.color, "intensity": self.intensity, "position": self.position}


@dataclass
class Mesh:
    geometry: str = "box"              # "box" | "sphere" | "plane" | "torus" | custom glTF url
    material: str = "standard"         # "standard" | "basic" | "phong"
    color: str = "#4477ff"
    position: tuple = (0, 0, 0)
    rotation: tuple = (0, 0, 0)
    scale: tuple = (1, 1, 1)
    key: Optional[str] = None
    animate: Optional[str] = None      # e.g. "rotate_y" for a simple built-in animation

    def to_dict(self) -> dict:
        return {
            "geometry": self.geometry, "material": self.material, "color": self.color,
            "position": self.position, "rotation": self.rotation, "scale": self.scale,
            "key": self.key, "animate": self.animate,
        }


@dataclass
class Scene:
    camera: Camera = field(default_factory=Camera)
    lights: list[Light] = field(default_factory=lambda: [Light()])
    meshes: list[Mesh] = field(default_factory=list)
    background: str = "#0b0b12"
    width: str = "100%"
    height: str = "480px"

    def add(self, mesh: Mesh) -> "Scene":
        self.meshes.append(mesh)
        return self

    def to_dict(self) -> dict:
        return {
            "camera": self.camera.to_dict(),
            "lights": [l.to_dict() for l in self.lights],
            "meshes": [m.to_dict() for m in self.meshes],
            "background": self.background,
            "width": self.width,
            "height": self.height,
        }

    def to_element(self):
        """Return a Nexoria `Element` (a <canvas> + data attribute) for use in render()."""
        from ..core.element import el
        import json
        return el(
            "div",
            **{
                "class": "nx-three-scene",
                "data-nx-scene": json.dumps(self.to_dict()),
                "style": f"width:{self.width};height:{self.height};",
            },
        )
