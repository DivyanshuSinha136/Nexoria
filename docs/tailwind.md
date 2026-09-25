# `nexoria.tailwind`

> Tailwind CSS via the Play CDN for prototyping, plus a real purged build for production.

| | |
|---|---|
| **Import** | `from nexoria.tailwind import TailwindConfig` |
| **Enabled by** | `App(tailwind=True, tailwind_config=TailwindConfig(...), tailwind_plugins=[...])` |
| **Library** | `https://cdn.tailwindcss.com` (classic script) |
| **Production path** | `nexoria build` compiles `dist/tailwind.css` — see [`tools`](tools.md) |

## Prototyping (Play CDN)

```python
app = App(
    name="TW", router=router, tailwind=True,
    tailwind_config=TailwindConfig(dark_mode="class", theme_extend={"colors": {"brand": "#6366f1"}}),
    tailwind_plugins=["forms", "typography"],      # → ?plugins=forms,typography
)
el("div", "Hello", class_="p-6 rounded-xl bg-brand text-white")
```

Tailwind JIT-compiles classes in the browser and, through its own `MutationObserver`, also styles elements added by Nexoria's WebSocket patches. Tailwind documents this mode as **not for production** (whole engine shipped, no purging).

`TailwindConfig(theme_extend={}, dark_mode=None, extra={})` renders `tailwind.config = {…}`; `extra` passes any other top-level key, e.g. `{"corePlugins": {"preflight": False}}` to stop Tailwind's reset from fighting `base.css`.

## Production

Create `static/tailwind.css` (or `./tailwind.css` or `src/input.css`) containing `@import "tailwindcss";` (Tailwind v4 CSS-first — no `tailwind.config.js`) and install `@tailwindcss/cli`. `nexoria build` then writes a minified, purged `dist/tailwind.css` and records it in `manifest.json`. Link it from your own static setup; no `App` flag is needed for the compiled path.

## API reference

### Classes

#### `class TailwindConfig(theme_extend: dict[str, Any] = ..., dark_mode: Optional[str] = None, extra: dict[str, Any] = ...) -> None`

Maps onto the Play CDN's runtime `tailwind.config = {...}` object (https://tailwindcss.com/docs/installation/play-cdn#using-a-plugin).

`extra` passes any other top-level Tailwind config key through verbatim (e.g. `{"corePlugins": {"preflight": False}}` to disable Tailwind's own CSS reset if it's fighting with Nexoria's `base.css`).

- **`.to_dict() -> dict`**

### Functions

#### `tailwind_cdn_url(plugins: Optional[list[str]] = None) -> str`

The Play CDN supports official plugins (forms, typography, container queries, aspect-ratio) via a query string: https://tailwindcss.com/docs/installation/play-cdn#using-a-plugin

#### `tailwind_runtime_tag(config: Optional[TailwindConfig] = None, plugins: Optional[list[str]] = None) -> str`

### Constants

| Name | Value |
|---|---|
| `TAILWIND_CDN` | `'https://cdn.tailwindcss.com'` |
