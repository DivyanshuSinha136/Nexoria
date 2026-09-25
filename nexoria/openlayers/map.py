"""
nexoria.openlayers.map
=========================
Optional mapping layer using OpenLayers (tile layers, vector layers,
GeoJSON, interactions -- a full-featured open-source mapping library).

OpenLayers' raw npm ESM source pulls in 5 real direct dependencies
(pbf, rbush, earcut, geotiff, zarrita) whose own transitive trees run
20+ packages deep -- hand-assembling that import map would be fragile
and unmaintainable. OpenLayers publishes its own pre-bundled,
genuinely self-contained distribution for exactly this CDN use case
(dist/ol.js, verified to have zero external imports across its
1M-character bundle) -- used here instead. That bundle is a classic
global-attaching script (`window.ol`), not an ES module, so -- like
video.js -- it's loaded via a plain `<script>` tag rather than the
shared import map.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import json

OL_VERSION = "10.10.0"
OL_JS_CDN = f"https://unpkg.com/ol@{OL_VERSION}/dist/ol.js"
OL_CSS_CDN = f"https://unpkg.com/ol@{OL_VERSION}/ol.css"
OL_CSS_TAG = f'<link rel="stylesheet" href="{OL_CSS_CDN}">'
OL_CORE_SCRIPT_TAG = f'<script src="{OL_JS_CDN}"></script>'
OL_ADAPTER_TAG = '<script src="/_nexoria/openlayers-adapter.js" defer></script>'


@dataclass
class Map:
    """
    An OpenLayers map, rendered into a `<div>`.

        Map(center=(-0.1276, 51.5072), zoom=11)   # London, lon/lat (EPSG:4326)

    `tile_source` is "osm" (OpenStreetMap, the default, no API key) or
    a `{"url": "https://.../{z}/{x}/{y}.png", "attributions": "..."}`
    dict for a custom XYZ tile source. `markers` places simple pin
    markers at `(lon, lat)` coordinates.
    """
    center: tuple = (0, 0)
    zoom: float = 2
    tile_source: Any = "osm"
    markers: list[tuple] = field(default_factory=list)
    width: str = "100%"
    height: str = "480px"
    map_id: Optional[str] = None

    def __post_init__(self):
        if self.map_id is None:
            import uuid
            self.map_id = f"nx-ol-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        return {
            "center": list(self.center),
            "zoom": self.zoom,
            "tileSource": self.tile_source,
            "markers": [list(m) for m in self.markers],
        }

    def to_element(self):
        from ..core.element import el
        return el(
            "div",
            id=self.map_id,
            **{"class": "nx-ol-map", "data-nx-ol": json.dumps(self.to_dict())},
            style=f"width:{self.width};height:{self.height};",
        )
