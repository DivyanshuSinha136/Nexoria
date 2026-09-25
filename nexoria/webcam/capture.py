"""
nexoria.webcam.capture
=========================
Optional webcam capture using webcam-easy (getUserMedia wrapper: start/
stop/snap/flip-camera). Verified: src/webcam-easy.js is a real ES
module (`export default class Webcam`) with zero external imports.

Requires HTTPS (or localhost) and the user's camera permission --
browser security requirements for getUserMedia, not a Nexoria
limitation.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import json
import uuid

WEBCAM_VERSION = "1.1.1"
WEBCAM_CDN = f"https://unpkg.com/webcam-easy@{WEBCAM_VERSION}/src/webcam-easy.js"
WEBCAM_IMPORTS = {"webcam-easy": WEBCAM_CDN}
WEBCAM_ADAPTER_TAG = '<script src="/_nexoria/webcam-adapter.js" type="module" defer></script>'


@dataclass
class Webcam:
    """
    A live webcam preview with snapshot capture.

        cam = Webcam(camera_id="my-cam")
        el("div",
           cam.to_element(),
           el("button", "Snap", onclick=cam.snap_attr()),
           el("button", "Switch camera", onclick=cam.flip_attr()))

    Access the last captured frame (a data URL) via
    `window.__nexoria__.webcam.get(camera_id).lastSnapshot`, or listen
    for the `nexoria:webcam:snap` DOM event.
    """
    facing_mode: str = "user"  # "user" (front) | "environment" (rear)
    width: str = "480px"
    height: str = "360px"
    autostart: bool = True
    camera_id: Optional[str] = None

    def __post_init__(self):
        if self.camera_id is None:
            self.camera_id = f"nx-webcam-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        return {"facingMode": self.facing_mode, "autostart": self.autostart}

    def to_element(self):
        from ..core.element import el
        return el(
            "video",
            id=self.camera_id,
            autoplay=True, playsinline=True, muted=True,
            **{"class": "nx-webcam-video", "data-nx-webcam": json.dumps(self.to_dict())},
            style=f"width:{self.width};height:{self.height};background:#000;",
        )

    def snap_attr(self) -> str:
        return f"window.__nexoria__.webcam.snap('{self.camera_id}')"

    def flip_attr(self) -> str:
        return f"window.__nexoria__.webcam.flip('{self.camera_id}')"

    def stop_attr(self) -> str:
        return f"window.__nexoria__.webcam.stop('{self.camera_id}')"
