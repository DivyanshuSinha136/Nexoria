# `nexoria.bootstrap`

> Bootstrap 5 as an alternative (or complement) to Nexoria's own styling, with a CSS-variable theme and auto-initialised tooltips/popovers.

| | |
|---|---|
| **Import** | `from nexoria.bootstrap import BootstrapTheme` |
| **Enabled by** | `App(bootstrap=True, bootstrap_theme=…, bootstrap_icons=True)` |
| **Library** | Bootstrap 5.3.3 (CSS + bundle JS with Popper) and optionally Bootstrap Icons 1.11.3 from jsDelivr — classic tags, not the import map |
| **Adapter** | `runtime/bootstrap-adapter.js`; `window.__nexoria__.bootstrap.mountNew(root)` |

```python
from nexoria import App, Router
from nexoria.bootstrap import BootstrapTheme

app = App(
    name="B5", router=router, bootstrap=True, bootstrap_icons=True,
    bootstrap_theme=BootstrapTheme(primary="#6366f1", border_radius="0.75rem"),
)
# markup just works:
el("button", "Open", class_="btn btn-primary", **{"data-bs-toggle": "modal", "data-bs-target": "#m"})
```

- Most components (collapse, dropdown, modal, …) self-activate from `data-bs-*` attributes — no Python helpers needed.
- **Tooltips and popovers** need `new bootstrap.Tooltip(el)`; the adapter initialises every `[data-bs-toggle="tooltip"|"popover"]` at load. After later DOM changes call `window.__nexoria__.bootstrap.mountNew()`.
- **Theme sync.** A `MutationObserver` keeps Bootstrap's `data-bs-theme` on `<html>` in step with Nexoria's `data-nx-theme`, so one toggle ([`theme_toggle_button`](style.md#dark--light-toggle)) drives both.
- `BootstrapTheme` overrides `--bs-*` variables (`primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`, `body_bg`, `body_color`, `border_radius`, `font_family_base`, and `variables={"name": value}` for anything else). It renders one `<style>:root{…}</style>` after Bootstrap's stylesheet so it wins the cascade.
- Hyphenated attributes such as `data-bs-toggle` can be written `data_bs_toggle="…"` (auto-hyphenated) or via `**{"data-bs-toggle": …}`.

## API reference

### Classes

#### `class BootstrapTheme(primary: Optional[str] = None, secondary: Optional[str] = None, success: Optional[str] = None, danger: Optional[str] = None, warning: Optional[str] = None, info: Optional[str] = None, light: Optional[str] = None, dark: Optional[str] = None, body_bg: Optional[str] = None, body_color: Optional[str] = None, border_radius: Optional[str] = None, font_family_base: Optional[str] = None, variables: dict[str, str] = ...) -> None`

Bootstrap 5.3+ exposes its entire palette as CSS custom properties (`--bs-primary`, `--bs-body-bg`, `--bs-border-radius`, ...) -- override any of them without touching Sass or a build step.

Renders to a single `<style>:root{...}</style>` tag placed after the core Bootstrap stylesheet, so these values win via normal CSS cascade order. `variables` passes any other `--bs-*` custom property through verbatim by its bare name (no `--bs-` prefix needed).

- **`.to_css_vars() -> dict[str, str]`**
- **`.to_style_tag() -> str`**

### Constants

| Name | Value |
|---|---|
| `BOOTSTRAP_VERSION` | `'5.3.3'` |
| `BOOTSTRAP_CSS_CDN` | `'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css'` |
| `BOOTSTRAP_JS_CDN` | `'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js'` |
| `BOOTSTRAP_ICONS_VERSION` | `'1.11.3'` |
| `BOOTSTRAP_ICONS_CSS_CDN` | `'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css'` |
| `BOOTSTRAP_CSS_TAG` | `'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">'` |
| `BOOTSTRAP_CORE_SCRIPT_TAG` | `'<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>'` |
| `BOOTSTRAP_ADAPTER_TAG` | `'<script src="/_nexoria/bootstrap-adapter.js" defer></script>'` |
| `BOOTSTRAP_ICONS_TAG` | `'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">'` |
| `BOOTSTRAP_RUNTIME_TAG` | `'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">\n<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>\n<script src="/_nexoria/bootstrap-adapter.js" defer></script>'` |
