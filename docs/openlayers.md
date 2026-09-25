# `nexoria.openlayers`

> Interactive maps with OpenLayers: OSM or custom XYZ tiles and simple markers.

| | |
|---|---|
| **Import** | `from nexoria.openlayers import Map` |
| **Enabled by** | `App(openlayers=True)` |
| **Library** | OpenLayers 10.10.0 pre-bundled `dist/ol.js` (global `window.ol`) + `ol.css` from unpkg — classic tags, not the import map |
| **Adapter** | `runtime/openlayers-adapter.js`; `window.__nexoria__.openlayers.{maps,get,mountNew}`; event `nexoria:openlayers:ready` |

```python
from nexoria.openlayers import Map
Map(center=(-0.1276, 51.5072), zoom=11, markers=[(-0.1276, 51.5072)])     # lon, lat (EPSG:4326)
Map(tile_source={"url": "https://tiles.example.com/{z}/{x}/{y}.png", "attributions": "© Example"})
```

`tile_source` is `"osm"` (default, no key) or a dict with `url` and `attributions`. Alias it on import (`from nexoria.openlayers import Map as OLMap`) if `Map` collides with a name in your own code.

## API reference

### Classes

#### `class Map(center: tuple = (0, 0), zoom: float = 2, tile_source: Any = 'osm', markers: list[tuple] = ..., width: str = '100%', height: str = '480px', map_id: Optional[str] = None) -> None`

An OpenLayers map, rendered into a `<div>`.

`tile_source` is "osm" (OpenStreetMap, the default, no API key) or a `{"url": "https://.../{z}/{x}/{y}.png", "attributions": "..."}` dict for a custom XYZ tile source. `markers` places simple pin markers at `(lon, lat)` coordinates.

- **`.to_dict() -> dict`**
- **`.to_element()`**

### Constants

| Name | Value |
|---|---|
| `OL_CSS_TAG` | `'<link rel="stylesheet" href="https://unpkg.com/ol@10.10.0/ol.css">'` |
| `OL_CORE_SCRIPT_TAG` | `'<script src="https://unpkg.com/ol@10.10.0/dist/ol.js"></script>'` |
| `OL_ADAPTER_TAG` | `'<script src="/_nexoria/openlayers-adapter.js" defer></script>'` |
| `OL_JS_CDN` | `'https://unpkg.com/ol@10.10.0/dist/ol.js'` |
