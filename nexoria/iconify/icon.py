"""
nexoria.iconify.icon
=======================
Optional icon layer using Iconify (150k+ icons from 200+ open-source
icon sets, one unified API). Verified: iconify-icon's ESM build has
zero external imports (@iconify/types is a types-only declared
dependency, unused at runtime -- confirmed empty in the actual bundle).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

ICONIFY_VERSION = "3.0.2"
ICONIFY_CDN = f"https://unpkg.com/iconify-icon@{ICONIFY_VERSION}/dist/iconify-icon.min.js"
ICONIFY_SCRIPT_TAG = f'<script src="{ICONIFY_CDN}" type="module"></script>'


@dataclass
class Icon:
    """
    An icon from any Iconify set (e.g. "mdi:home", "lucide:star",
    "logos:python"). Renders as the real `<iconify-icon>` web component
    -- icon data is fetched from Iconify's public API on demand and
    cached, no icon-set package to install.

        Icon("mdi:home", size="24px", color="var(--nx-primary)")
    """
    name: str
    size: Optional[str] = None
    color: Optional[str] = None
    inline: bool = False

    def to_element(self):
        from ..core.element import el
        style_parts = []
        if self.size:
            style_parts.append(f"font-size:{self.size};")
        if self.color:
            style_parts.append(f"color:{self.color};")
        props = {"icon": self.name}
        if style_parts:
            props["style"] = "".join(style_parts)
        if self.inline:
            props["inline"] = True
        return el("iconify-icon", **props)
