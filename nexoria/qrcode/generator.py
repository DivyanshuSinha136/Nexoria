"""
nexoria.qrcode.generator
===========================
Optional QR code generation using qr-code-styling (stylable QR codes:
custom colors, gradients, embedded logos, dot styles). Verified:
lib/qr-code-styling.js bundles its own dependency (qrcode-generator)
internally -- zero external imports in the actual file.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import json

QRCODE_VERSION = "1.9.2"
QRCODE_CDN = f"https://unpkg.com/qr-code-styling@{QRCODE_VERSION}/lib/qr-code-styling.js"
# UMD bundle (window.QRCodeStyling global) -- not an ES module, so a
# classic <script> tag, not the shared import map.
QRCODE_SCRIPT_TAG = f'<script src="{QRCODE_CDN}"></script>'
QRCODE_ADAPTER_TAG = '<script src="/_nexoria/qrcode-adapter.js" defer></script>'


@dataclass
class QRCode:
    """
    A stylable QR code, rendered client-side.

        QRCode("https://example.com", dot_color="#6366f1", size=240)

    `options` passes straight through to qr-code-styling's own
    constructor options (gradients, corner styles, embedded image, ...).
    """
    data: str
    size: int = 200
    dot_color: str = "#000000"
    background_color: str = "#ffffff"
    dots_type: str = "square"  # "square" | "dots" | "rounded" | "classy" | "classy-rounded" | "extra-rounded"
    image: Optional[str] = None  # logo URL to embed
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        merged = dict(self.options)
        merged.setdefault("width", self.size)
        merged.setdefault("height", self.size)
        merged.setdefault("data", self.data)
        merged.setdefault("dotsOptions", {"color": self.dot_color, "type": self.dots_type})
        merged.setdefault("backgroundOptions", {"color": self.background_color})
        if self.image:
            merged.setdefault("image", self.image)
        return merged

    def to_element(self):
        from ..core.element import el
        return el(
            "div",
            **{"class": "nx-qrcode", "data-nx-qrcode": json.dumps(self.to_dict())},
            style=f"width:{self.size}px;height:{self.size}px;",
        )
