"""
nexoria.barcode.generator
============================
Optional barcode generation using bwip-js (100+ symbologies: Code128,
QR, EAN, UPC, PDF417, DataMatrix, ...). Verified: dist/bwip-js.mjs (the
browser ESM build -- distinct from the package's Node-targeted "main"
entry, dist/bwip-js-node.js) has zero external imports.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import json

BWIPJS_VERSION = "4.11.4"
BWIPJS_CDN = f"https://unpkg.com/bwip-js@{BWIPJS_VERSION}/dist/bwip-js.mjs"
BWIPJS_IMPORTS = {"bwip-js": BWIPJS_CDN}
BWIPJS_ADAPTER_TAG = '<script src="/_nexoria/barcode-adapter.js" type="module" defer></script>'


@dataclass
class Barcode:
    """
    A barcode, rendered client-side onto a `<canvas>`.

        Barcode("0123456789128", symbology="code128", include_text=True)
        Barcode("https://example.com", symbology="qrcode")

    `symbology` is any bwip-js BCID (bar code identifier): "code128",
    "ean13", "upca", "qrcode", "datamatrix", "pdf417", "azteccode", ...
    `options` passes straight through to bwip-js's own options object.
    """
    text: str
    symbology: str = "code128"
    scale: float = 3
    height: float = 10
    include_text: bool = True
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        merged = dict(self.options)
        merged.setdefault("bcid", self.symbology)
        merged.setdefault("text", self.text)
        merged.setdefault("scale", self.scale)
        merged.setdefault("height", self.height)
        merged.setdefault("includetext", self.include_text)
        return merged

    def to_element(self):
        from ..core.element import el
        return el("canvas", **{"class": "nx-barcode", "data-nx-barcode": json.dumps(self.to_dict())})
