# `nexoria.barcode`

> 100+ barcode symbologies (Code 128, EAN, UPC, QR, PDF417, DataMatrix, Aztec, …) via bwip-js.

| | |
|---|---|
| **Import** | `from nexoria.barcode import Barcode` |
| **Enabled by** | `App(barcode=True)` |
| **Library** | `bwip-js` 4.11.4 browser ESM build (import map) |
| **Adapter** | `runtime/barcode-adapter.js`; `window.__nexoria__.barcode.mountNew()` |

```python
Barcode("0123456789128", symbology="code128", include_text=True)
Barcode("https://example.com", symbology="qrcode")
```

`symbology` is any bwip-js BCID. `scale`, `height`, `include_text` map to `scale`, `height`, `includetext`; `options` passes straight through. Renders `<canvas class="nx-barcode" data-nx-barcode='{…}'>`.

## API reference

### Classes

#### `class Barcode(text: str, symbology: str = 'code128', scale: float = 3, height: float = 10, include_text: bool = True, options: dict[str, Any] = ...) -> None`

A barcode, rendered client-side onto a `<canvas>`.

`symbology` is any bwip-js BCID (bar code identifier): "code128", "ean13", "upca", "qrcode", "datamatrix", "pdf417", "azteccode", ... `options` passes straight through to bwip-js's own options object.

- **`.to_dict() -> dict`**
- **`.to_element()`**

### Constants

| Name | Value |
|---|---|
| `BWIPJS_IMPORTS` | `{'bwip-js': 'https://unpkg.com/bwip-js@4.11.4/dist/bwip-js.mjs'}` |
| `BWIPJS_ADAPTER_TAG` | `'<script src="/_nexoria/barcode-adapter.js" type="module" defer></script>'` |
| `BWIPJS_CDN` | `'https://unpkg.com/bwip-js@4.11.4/dist/bwip-js.mjs'` |
