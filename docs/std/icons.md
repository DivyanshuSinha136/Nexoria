# `nexoria.std.icons`

> 2,078 [Bootstrap Icons](https://icons.getbootstrap.com) vendored as SVG files and rendered as real inline `<svg>` elements — no CDN, no icon font, no network.

| | |
|---|---|
| **Import** | `from nexoria.std.icons import Icon, list_icons, has_icon, icon_count` |
| **Data** | `nexoria/std/icons/data/*.svg` (MIT-licensed set; licence file included) |
| **Not to be confused with** | [`nexoria.iconify.Icon`](../iconify.md) (CDN web component, 150k+ icons) |

```python
from nexoria.std.icons import Icon
el("button", Icon("cart-fill", size="1.1rem"), " Add to cart")
Icon("check-circle", color="var(--nx-success)", title="Done")
```

- Names are the file stems: `house`, `alarm-fill`, `bag-plus`, … Use `list_icons()` / `has_icon(name)` to look them up.
- `Icon(name, size=None, color=None, class_=None, title=None)`; an unknown name raises `IconNotFoundError` (a `KeyError`) listing how many icons are available.
- Files are parsed once and cached (`lru_cache`) for the process lifetime, then converted to an `Element` tree, so repeated use is cheap.

## API reference

### Classes

#### `class Icon(name: str, size: Optional[str] = None, color: Optional[str] = None, class_: Optional[str] = None, title: Optional[str] = None) -> None`

A single Bootstrap Icon, rendered as a real inline `<svg>` element tree built from the bundled, offline SVG data (no CDN, no icon font, no `iconify-icon` web component).

`size` sets both width and height (defaults to the SVG's own 16x16 viewBox-driven size, i.e. "1em"-ish at the surrounding font size if left as None -- pass an explicit size for predictable layout). `color` overrides `fill` (Bootstrap Icons ship with `fill="currentColor"`, so the default already inherits from CSS `color` with no override needed -- `color=` is a convenience for setting it independently of text color).

- **`.to_element()`**

#### `class IconNotFoundError()`

Raised when a requested icon name has no matching bundled SVG.

### Functions

#### `list_icons() -> list[str]`

All bundled icon names, sorted (e.g. 'house', 'alarm-fill', ...).

#### `has_icon(name: str) -> bool`

#### `icon_count() -> int`
