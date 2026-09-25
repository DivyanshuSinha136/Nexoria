"""
nexoria.spline.scene
=======================
Optional 3D layer for scenes exported from Spline (spline.design).
Reference an exported `.splinecode` scene URL declaratively in Python;
the client adapter (`runtime/spline-adapter.js`, loaded only when
`App(spline=True)` is set) loads it via Spline's own runtime into a
`<canvas>`. `@splinetool/runtime` itself is pulled from CDN as an ES
module -- never a Python dependency.

Verified dependency chain: `@splinetool/runtime`'s ESM build bundles
all of its own dependencies (`@splinetool/animation-core`, `on-change`,
`semver-compare`) internally -- zero external imports beyond the
package itself, so a single import-map entry is sufficient (same
situation as Three.js/GSAP).

Honest scope: this renders real WebGL content, exactly like
`nexoria.threejs.Scene` -- it needs an actual browser with a GPU/WebGL
context. There's no server-side or headless way to verify the pixels
it produces; what's verified here is that the declarative spec is
correctly built and serialized, and that the runtime's own dependency
chain is genuinely self-contained (checked against the real published
package, not assumed).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import json

SPLINE_RUNTIME_VERSION = "2.0.14"
SPLINE_CDN = f"https://unpkg.com/@splinetool/runtime@{SPLINE_RUNTIME_VERSION}/build/runtime.js"
SPLINE_IMPORTS = {"@splinetool/runtime": SPLINE_CDN}
SPLINE_ADAPTER_TAG = '<script src="/_nexoria/spline-adapter.js" type="module" defer></script>'


@dataclass
class SplineScene:
    """
    A Spline scene, referenced by its exported `.splinecode` URL (from
    Spline's own "Export > Code Export > Viewer code" panel, or a
    file you host yourself).

        SplineScene("https://prod.spline.design/abc123/scene.splinecode")

    `events` maps Spline object names to a `nexoria.core.element`-style
    `onclick=`-equivalent: since Spline objects aren't real DOM nodes,
    interaction is wired through the runtime's own event API instead --
    see `.on_click_attr(object_name)` for a plain `onclick=` string you
    can attach to an ordinary button to trigger a named Spline event
    (`app.emitEvent('mouseDown', objectName)`), and
    `window.__nexoria__.spline.get(id)` for direct access to the loaded
    `Application` instance for anything more advanced.
    """
    url: str
    width: str = "100%"
    height: str = "480px"
    background: Optional[str] = None  # CSS color; None leaves Spline's own scene background
    scene_id: Optional[str] = None

    def __post_init__(self):
        if self.scene_id is None:
            import uuid
            self.scene_id = f"nx-spline-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        return {"url": self.url, "background": self.background}

    def to_element(self):
        from ..core.element import el
        style = f"width:{self.width};height:{self.height};display:block;"
        if self.background:
            style += f"background:{self.background};"
        return el(
            "canvas",
            id=self.scene_id,
            **{"class": "nx-spline-canvas", "data-nx-spline": json.dumps(self.to_dict())},
            style=style,
        )

    def emit_event_attr(self, event_name: str, object_name: str) -> str:
        """
        A plain `onclick=`-style string (purely client-side, no server
        round-trip) that tells this scene's loaded Spline `Application`
        to emit an event for a named object -- e.g. to trigger an
        interaction Spline's own editor defined:

            el("button", "Spin", onclick=scene.emit_event_attr("mouseDown", "Cube"))
        """
        return (
            f"window.__nexoria__.spline.get('{self.scene_id}') && "
            f"window.__nexoria__.spline.get('{self.scene_id}').emitEvent("
            f"'{event_name}', '{object_name}')"
        )
