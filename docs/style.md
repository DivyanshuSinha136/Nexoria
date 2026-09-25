# `nexoria.style`

> Design tokens (`Theme`), CSS-in-Python (`Stylesheet`), a persisted dark/light toggle, and the `nx-*` base classes.

| | |
|---|---|
| **Import** | `from nexoria import Stylesheet, Theme, DEFAULT_THEME, LIGHT_THEME` · `from nexoria.style import theme_toggle_button` |
| **Source** | `nexoria/style/theme.py`, `stylesheet.py`, `components.py`; CSS in `nexoria/runtime/base.css` |
| **Enabled by** | Always on |
| **Uses** | The Rust `hash_asset` for class-name fingerprints when built, else `hashlib.blake2b` |

## `Theme` — design tokens

A `Theme` is a dataclass rendered as CSS custom properties on `:root`.

| Field | CSS variable | Default (dark) |
|---|---|---|
| `primary`, `primary_hover`, `accent` | `--nx-primary`, `--nx-primary-hover`, `--nx-accent` | `#6366f1`, `#4f46e5`, `#22d3ee` |
| `background`, `surface`, `surface_alt`, `border` | `--nx-bg`, `--nx-surface`, `--nx-surface-alt`, `--nx-border` | `#0b0b12`, `#14141f`, `#1b1b29`, `#26263a` |
| `text`, `text_muted` | `--nx-text`, `--nx-text-muted` | `#f3f3f7`, `#9797ad` |
| `success`, `danger`, `warning` | `--nx-success`, `--nx-danger`, `--nx-warning` | `#22c55e`, `#ef4444`, `#f59e0b` |
| `radius`, `radius_sm`, `space`, `shadow` | `--nx-radius`, `--nx-radius-sm`, `--nx-space`, `--nx-shadow` | `14px`, `8px`, `8px`, … |
| `font`, `font_mono` | `--nx-font`, `--nx-font-mono` | system stack / JetBrains Mono stack |

```python
App(name="x", router=router, theme=Theme(primary="#ff6b35"))
```

`LIGHT_THEME` overrides the surfaces/text for light mode. It is emitted as `:root[data-nx-theme="light"] { … }`, so it only takes effect when the `data-nx-theme="light"` attribute is set on `<html>`.

## Dark / light toggle

- An inline, blocking `<script>` in `<head>` reads `localStorage["nx-theme"]` (falling back to `prefers-color-scheme`) and sets `data-nx-theme` **before** CSS is parsed — no flash of the wrong theme.
- `theme_toggle_button(icon="🌓", class_="nx-theme-toggle")` returns a `<button>` wired to `window.__nexoria__.toggleTheme()`, which flips the attribute and persists the choice. It is purely client-side.
- `App(light_theme=None)` removes the light override.

## `Stylesheet` — CSS in Python

```python
from nexoria import Stylesheet

sheet = Stylesheet({".card:hover": {"transform": "translateY(-2px)"}})
sheet.add(".title", font_size="2rem", color="var(--nx-text)")      # underscores → hyphens
cls = sheet.scoped_class("hero", padding="32px", gap="16px")       # e.g. "nx-hero-1a2b3c4d5e"
sheet.to_css()
```

- `add(selector, **props)` merges declarations; vendor-prefixed keys must be passed via unpacking: `**{"-webkit-background-clip": "text"}`.
- `merge(other)` returns a **new** stylesheet (the argument wins on conflicts).
- `scoped_class(name, **props)` registers `.nx-<name>-<hash>` where the hash fingerprints the sorted declarations. Identical input returns the same class name (idempotent across renders); two components can both use `"card"` without colliding.
- `to_css()` renders one rule per line. `bool(sheet)` is `False` when empty.

Where stylesheets are used: `App(styles=…)` (global) and `Component.styles` (per routed component) are merged into one `<style>` block at first render.

### Things to know

- The hash function differs by tier: the Rust build yields 10 hex characters, the Python fallback 8. The generated class **names** therefore differ between environments (behaviour is identical). Don't hard-code them in snapshot tests.
- Scoped-class CSS is delivered with the **first** HTML response only. A class first created during a *later* re-render (after an event) will not have its CSS on the page. Define classes that a page might need on first render, or use inline `style=`.

## Base classes (`runtime/base.css`)

`nx-container`, `nx-card`, `nx-nav`, `nx-btn`, `nx-btn-ghost`, `nx-btn-danger`, `nx-badge`, `nx-row`, `nx-stack`, `nx-center`, `nx-spinner`, `nx-theme-toggle`. They read the `--nx-*` variables, so changing a `Theme` re-skins them.

## API reference

### Classes

#### `class Stylesheet(rules: Optional[dict[str, dict[str, str]]] = None)`

- **`.add(selector: str, **props: str) -> 'Stylesheet'`**
- **`.merge(other: Optional['Stylesheet']) -> 'Stylesheet'`** — Return a new Stylesheet combining `self` and `other` (other wins on conflicts).
- **`.scoped_class(name: str, **props: str) -> str`** — Register a content-hashed, collision-proof class name for the given declarations and return it, e.g. `nx-card-a1b2c3d4`. Calling this again with identical `name`+`props` returns the same class name (idempotent across re-renders).
- **`.to_css() -> str`**

#### `class Theme(name: str = 'nexoria-default', primary: str = '#6366f1', primary_hover: str = '#4f46e5', accent: str = '#22d3ee', background: str = '#0b0b12', surface: str = '#14141f', surface_alt: str = '#1b1b29', border: str = '#26263a', text: str = '#f3f3f7', text_muted: str = '#9797ad', success: str = '#22c55e', danger: str = '#ef4444', warning: str = '#f59e0b', radius: str = '14px', radius_sm: str = '8px', font: str = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-s..., font_mono: str = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace", space: str = '8px', shadow: str = '0 10px 30px rgba(0,0,0,0.35)') -> None`

Theme(name: 'str' = 'nexoria-default', primary: 'str' = '#6366f1', primary_hover: 'str' = '#4f46e5', accent: 'str' = '#22d3ee', background: 'str' = '#0b0b12', surface: 'str' = '#14141f', surface_alt: 'str' = '#1b1b29', border: 'str' = '#26263a', text: 'str' = '#f3f3f7', text_muted: 'str' = '#9797ad', success: 'str' = '#22c55e', danger: 'str' = '#ef4444', warning: 'str' = '#f59e0b', radius: 'str' = '14px', radius_sm: 'str' = '8px', font: 'str' = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif", font_mono: 'str' = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace", space: 'str' = '8px', shadow: 'str' = '0 10px 30px rgba(0,0,0,0.35)')

- **`.to_css_vars() -> str`**

### Functions

#### `theme_toggle_button(icon: str = '🌓', class_: str = 'nx-theme-toggle') -> Element`

A dark/light mode toggle button. Purely client-side (no server round-trip) -- flips `document.documentElement[data-nx-theme]` and persists the choice to localStorage. Requires `App(light_theme=...)` to not be disabled (it's on, with `nexoria.style.LIGHT_THEME`, by default) so there's a CSS variable set to switch to.

### Constants

| Name | Value |
|---|---|
| `DEFAULT_THEME` | `Theme(name='nexoria-default', primary='#6366f1', primary_hover='#4f46e5', accent='#22d3ee', background='#0b0b12', surface='#14141f', surface_alt='#1b1b29', border='#26263a', text='#f3f3f7', text_muted='#9797ad', success='#22c55e', danger='#ef4444', warning='#f59e0b', radius='14px', radius_sm='8px', font="-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif", font_mono="'JetBra…` |
| `LIGHT_THEME` | `Theme(name='nexoria-light', primary='#6366f1', primary_hover='#4f46e5', accent='#22d3ee', background='#f7f7fb', surface='#ffffff', surface_alt='#f0f0f6', border='#e4e4ee', text='#16161f', text_muted='#68687d', success='#22c55e', danger='#ef4444', warning='#f59e0b', radius='14px', radius_sm='8px', font="-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif", font_mono="'JetBrain…` |
