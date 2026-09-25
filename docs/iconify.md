# `nexoria.iconify`

> 150,000+ icons from 200+ sets through one API, rendered as the `<iconify-icon>` web component.

| | |
|---|---|
| **Import** | `from nexoria.iconify import Icon` |
| **Enabled by** | `App(iconify=True)` |
| **Library** | `iconify-icon` 3.0.2 (classic module script, unpkg); icon data is fetched from Iconify's public API on demand and cached |
| **Adapter** | none |

```python
Icon("mdi:home", size="24px", color="var(--nx-primary)")
el("div", Icon("logos:python"), " Python")
```

`Icon(name, size=None, color=None, inline=False)` → `<iconify-icon icon="mdi:home" style="font-size:24px;color:…">`. Icons need network access to Iconify's API at view time.

**Offline alternative:** [`std.icons`](std/icons.md) vendors 2,078 Bootstrap Icons as inline SVG with no network at all. The two classes are both called `Icon` but live in different modules.

## API reference

### Classes

#### `class Icon(name: str, size: Optional[str] = None, color: Optional[str] = None, inline: bool = False) -> None`

An icon from any Iconify set (e.g. "mdi:home", "lucide:star", "logos:python"). Renders as the real `<iconify-icon>` web component -- icon data is fetched from Iconify's public API on demand and cached, no icon-set package to install.

- **`.to_element()`**

### Constants

| Name | Value |
|---|---|
| `ICONIFY_CDN` | `'https://unpkg.com/iconify-icon@3.0.2/dist/iconify-icon.min.js'` |
| `ICONIFY_SCRIPT_TAG` | `'<script src="https://unpkg.com/iconify-icon@3.0.2/dist/iconify-icon.min.js" type="module"></script>'` |
