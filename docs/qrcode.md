# `nexoria.qrcode`

> Stylable QR codes (colours, dot styles, embedded logo) using qr-code-styling.

| | |
|---|---|
| **Import** | `from nexoria.qrcode import QRCode` |
| **Enabled by** | `App(qrcode=True)` |
| **Library** | `qr-code-styling` 1.9.2 (classic script, unpkg); self-contained |
| **Adapter** | `runtime/qrcode-adapter.js`; `window.__nexoria__.qrcode.{instances,mountNew}` |

```python
QRCode("https://example.com", dot_color="#6366f1", dots_type="rounded", size=240)
```

Fields: `data`, `size=200`, `dot_color`, `background_color`, `dots_type` (`square | dots | rounded | classy | classy-rounded | extra-rounded`), `image` (logo URL), `options` (passed straight to qr-code-styling). Renders `<div class="nx-qrcode" data-nx-qrcode='{…}'>`.

## API reference

### Classes

#### `class QRCode(data: str, size: int = 200, dot_color: str = '#000000', background_color: str = '#ffffff', dots_type: str = 'square', image: Optional[str] = None, options: dict[str, Any] = ...) -> None`

A stylable QR code, rendered client-side.

`options` passes straight through to qr-code-styling's own constructor options (gradients, corner styles, embedded image, ...).

- **`.to_dict() -> dict`**
- **`.to_element()`**

### Constants

| Name | Value |
|---|---|
| `QRCODE_CDN` | `'https://unpkg.com/qr-code-styling@1.9.2/lib/qr-code-styling.js'` |
| `QRCODE_SCRIPT_TAG` | `'<script src="https://unpkg.com/qr-code-styling@1.9.2/lib/qr-code-styling.js"></script>'` |
| `QRCODE_ADAPTER_TAG` | `'<script src="/_nexoria/qrcode-adapter.js" defer></script>'` |
