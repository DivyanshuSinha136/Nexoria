# `nexoria.std.lib`

> The dark, dev-tool look of Nexoria's own landing page: near-black surfaces, cyan/pink accents, mono type, code-editor chrome.

| | |
|---|---|
| **Import** | `from nexoria.std.lib import lib_hero, code_window, …` |
| **Theme** | `LIB_THEME` — tokens `--nx-lib-cyan`, `cyan-soft`, `pink`, `pink-soft`, `code-bg`, `code-chrome`, `grid-line` and near-black base surfaces; apply with `App(theme=LIB_THEME)` ([why](../std.md#apply-the-family-theme-important)) |
| **One-per-page helper** | `lib_keyframes()` — for the pulsing live dot and animated hero |

## Building blocks and sections

| Function | Notes |
|---|---|
| `lib_pill`, `lib_eyebrow`, `live_badge`, `lib_tag`, `lib_tag_row`, `stat_chip_row` | Small labels; `color`: `cyan | pink | muted` |
| `lib_button(*children, variant, size, href, on_click, icon, trailing_icon, full_width, disabled)` | `variant`: `solid | outline` |
| `code_window(code, filename, language, live)` | Mac-style editor window. A **best-effort Python tokenizer** colours keywords, strings, numbers, comments, decorators and a rough class/call guess — not a real parser. Any other `language` renders plain mono text. |
| `lib_feature_card`, `integration_chip` | Numbered feature tile; adapter tile |
| `lib_hero(title, highlight, eyebrow, subtitle, primary_cta, secondary_cta, stats, code, …)` | Split hero with an optional live code window |
| `pipeline_steps`, `feature_trio`, `integrations_row`, `install_cta` | Section layouts taking lists of dicts |
| `lib_navbar`, `lib_footer`, `lib_grid_background` | Site chrome and graph-paper background |

```python
from nexoria.std.lib import lib_navbar, lib_hero, install_cta, lib_keyframes
el("div", lib_keyframes(),
   lib_navbar("Nexoria", version="v0.1.0", github_href="https://github.com/DivyanshuSinha136/nexoria"),
   lib_hero("Full-stack in", highlight="pure Python.", subtitle="No JSX. No templates.",
            primary_cta="Start building", code="from nexoria import App\n..."),
   install_cta("Start with one command.", "pip install nexoria"))
```

## API reference

### Classes

#### `class LibTheme(name: str = 'nexoria-lib', primary: str = '#6366f1', primary_hover: str = '#4f46e5', accent: str = '#22d3ee', background: str = '#05070d', surface: str = '#0a0e17', surface_alt: str = '#0f1420', border: str = '#1b2333', text: str = '#e7ebf5', text_muted: str = '#7c8aa8', success: str = '#22c55e', danger: str = '#ef4444', warning: str = '#f59e0b', radius: str = '14px', radius_sm: str = '8px', font: str = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-s..., font_mono: str = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace", space: str = '8px', shadow: str = '0 10px 30px rgba(0,0,0,0.35)', cyan: str = '#22e5e5', cyan_soft: str = '#8ff7f0', pink: str = '#ff4f81', pink_soft: str = '#ff9ab8', code_bg: str = '#0a0f1a', code_chrome: str = '#141a29', grid_line: str = 'rgba(94, 234, 212, 0.055)') -> None`

LibTheme(name: 'str' = 'nexoria-lib', primary: 'str' = '#6366f1', primary_hover: 'str' = '#4f46e5', accent: 'str' = '#22d3ee', background: 'str' = '#05070d', surface: 'str' = '#0a0e17', surface_alt: 'str' = '#0f1420', border: 'str' = '#1b2333', text: 'str' = '#e7ebf5', text_muted: 'str' = '#7c8aa8', success: 'str' = '#22c55e', danger: 'str' = '#ef4444', warning: 'str' = '#f59e0b', radius: 'str' = '14px', radius_sm: 'str' = '8px', font: 'str' = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif", font_mono: 'str' = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace", space: 'str' = '8px', shadow: 'str' = '0 10px 30px rgba(0,0,0,0.35)', cyan: 'str' = '#22e5e5', cyan_soft: 'str' = '#8ff7f0', pink: 'str' = '#ff4f81', pink_soft: 'str' = '#ff9ab8', code_bg: 'str' = '#0a0f1a', code_chrome: 'str' = '#141a29', grid_line: 'str' = 'rgba(94, 234, 212, 0.055)')

- **`.to_css_vars() -> str`**

### Functions

#### `lib_keyframes()`

A `<style>` `Element` carrying every lib `@keyframes` block. Drop it once anywhere in your root layout before using `live_badge()`'s pulsing dot, `lib_hero(animate=True)`, or a gradient-animated `lib_heading(..., animate=True)`.

#### `lib_grid_background(*, class_ = None)`

A faint, full-bleed graph-paper grid `<div>` (absolutely positioned -- give its parent `position: relative`), matching the subtle grid behind the Nexoria hero. Layer page content over it in a sibling element.

#### `lib_pill(text: str, *, dot: bool = True, color: str = 'cyan') -> Element`

`lib_pill("Python, all the way through")`. A small rounded, bordered chip with an optional colored status dot -- the hero badge style. `color`: "cyan" | "pink" | "muted".

#### `lib_eyebrow(text: str, *, color: str = 'cyan') -> Element`

`lib_eyebrow("WHY NEXORIA")`. An uppercase, letter-spaced section label with no border/background -- used above section headings.

#### `live_badge(label: str = 'LIVE', *, color: str = 'cyan', pulse: bool = True) -> Element`

`live_badge()` / `live_badge("Framework online")`. A small colored dot next to an uppercase mono label; the dot pulses when `pulse=True` (needs `nexoria.std.lib.theme.lib_keyframes()` rendered once on the page).

#### `lib_tag(text: str, *, color: str = 'pink') -> Element`

`lib_tag("SSR · REAL HTML")`. A small uppercase mono tag used under feature cards -- pass parts already joined with " · " or build one from a sequence with `lib_tag_row`.

#### `lib_tag_row(parts: Sequence[str], *, color: str = 'pink') -> Element`

`lib_tag_row(["SSR", "REAL HTML"])` -> `lib_tag("SSR · REAL HTML")`.

#### `stat_chip_row(stats: Sequence[str], *, color: str = 'cyan') -> Element`

`stat_chip_row(["~4KB runtime", "0 JSX", "MIT licensed"])`. A row of small mono stats separated by dots, like the strip under the Nexoria hero. The first word of each stat (if it looks like a value, e.g. "~4KB") is tinted; pass plain strings otherwise.

#### `lib_button(*children: Any, variant: str = 'solid', size: str = 'md', href: Optional[str] = None, on_click: Optional[Callable] = None, icon: Optional[Element] = None, trailing_icon: Optional[Element] = None, full_width: bool = False, disabled: bool = False, class_: Optional[str] = None) -> Element`

`lib_button("Start building", trailing_icon=el("span", "→"))` `lib_button("Explore source", variant="outline")`

`variant`: "solid" | "outline" | "ghost" | "cyan".

#### `code_window(code: str, *, filename: str = 'app.py', language: str = 'python', live: bool = True, class_: Optional[str] = None) -> Element`

`code_window('from nexoria import App\n...', filename="app.py")`. A mac-style editor window (traffic-light dots, filename, an optional pulsing "LIVE" pip) with the code lightly syntax-highlighted when `language == "python"` (any other value renders the code as plain mono text). Needs `nexoria.std.lib.theme.lib_keyframes()` rendered once on the page for the live dot to pulse.

#### `lib_feature_card(title: str, desc: str, *, number: Optional[str] = None, icon: Optional[Element] = None, tag: Optional[Sequence[str]] = None, color: str = 'cyan') -> Element`

`lib_feature_card("Server-rendered first", "The first request returns real HTML.", number="01", icon=Icon("lightning-fill"), tag=["SSR", "REAL HTML"])`. `color`: "cyan" | "pink" | "muted" -- tints the icon and tag.

#### `integration_chip(name: str, desc: str, *, icon: Optional[Element] = None) -> Element`

`integration_chip("GSAP", "Timelines in Python", icon=Icon("stars"))`. A small bordered adapter/integration tile, like the "batteries included" logo row on the Nexoria landing page.

#### `lib_hero(title: str, *, highlight: Optional[str] = None, eyebrow: Optional[str] = None, subtitle: Optional[str] = None, primary_cta: Optional[str] = None, primary_href: str = '#', secondary_cta: Optional[str] = None, secondary_href: str = '#', stats: Sequence[str] = (), code: Optional[str] = None, code_filename: str = 'app.py', animate: bool = False) -> Element`

`lib_hero("Full-stack in", highlight="pure Python.", eyebrow="Python, all the way through", subtitle="No JSX. No templates.", primary_cta="Start building", code="from nexoria import App\n...")`.

`highlight` is rendered as its own line in a cyan-to-pink gradient (the "pure Python." treatment); `code` renders a `code_window()` alongside the copy when given, otherwise the copy spans full width. `animate=True` fades the copy in on load (needs `nexoria.std.lib.theme.lib_keyframes()` rendered once on the page).

#### `pipeline_steps(steps: Sequence[Mapping[str, Any]], *, eyebrow: Optional[str] = None, title: Optional[str] = None, subtitle: Optional[str] = None) -> Element`

`pipeline_steps([{"icon": Icon("filetype-py"), "number": "01", "title": "Python tree", "desc": "Components, routes, state"}, ...], eyebrow="THE REQUEST JOURNEY", title="Python in. Live interface out.")`. A horizontal row of circular icon nodes connected by a line, each labeled with a number and a title/description -- the "request journey" diagram from the Nexoria landing page.

#### `feature_trio(features: Sequence[Mapping[str, Any]], *, eyebrow: Optional[str] = None, title: Optional[str] = None, subtitle: Optional[str] = None) -> Element`

`feature_trio([{"icon": Icon("lightning-fill"), "number": "01", "title": "Server-rendered first", "desc": "...", "tag": ["SSR", "REAL HTML"], "color": "cyan"}, ...], eyebrow="WHY NEXORIA", title="A small runtime. A very big surface.")`. A responsive grid of `lib_feature_card`s under a section heading.

#### `integrations_row(items: Sequence[Mapping[str, Any]], *, eyebrow: Optional[str] = None, title: Optional[str] = None, subtitle: Optional[str] = None) -> Element`

`integrations_row([{"icon": Icon("stars"), "name": "GSAP", "desc": "Timelines in Python"}, ...], eyebrow="ONE FRAMEWORK, MANY SURFACES", title="Batteries included. Complexity optional.")`. A responsive grid of `integration_chip`s -- the adapter/logo row.

#### `install_cta(title: str, command: str, *, eyebrow: Optional[str] = None, tagline: Optional[str] = None, github_href: Optional[str] = None, docs_href: Optional[str] = None) -> Element`

`install_cta("Your full stack starts with one command.", "pip install nexoria", eyebrow="SHIP SOMETHING", tagline="Cross-platform. Production-grade. Open source.", github_href="https://github.com/...", docs_href="/docs")`. The closing panel: a big line of copy next to a copyable install command, with optional repo/docs links underneath.

#### `lib_navbar(brand: str, *, glyph: Optional[Element] = None, version: Optional[str] = None, links: Sequence[tuple] = (), github_href: Optional[str] = None, sticky: bool = True) -> Element`

`lib_navbar("Nexoria", version="v0.1.0", links=[("Architecture", "#architecture"), ("Runtime", "#runtime")], github_href="https://github.com/...")`. `links` is a sequence of `(label, href)` pairs. `glyph` is an optional small `Element` (icon/logo mark) shown in the gradient brand tile; a single letter is used when omitted.

#### `lib_footer(brand: str, *, tagline: Optional[str] = None, links: Sequence[tuple] = (), status_label: str = 'Framework online') -> Element`

`lib_footer("Nexoria", tagline="Built by ... · Team", links=[("GitHub", "#"), ("MIT License", "#")])`. A slim bottom bar: brand + tagline on the left, plain text links and a pulsing "online" status pip on the right.

### Constants

| Name | Value |
|---|---|
| `LIB_THEME` | `LibTheme(name='nexoria-lib', primary='#6366f1', primary_hover='#4f46e5', accent='#22d3ee', background='#05070d', surface='#0a0e17', surface_alt='#0f1420', border='#1b2333', text='#e7ebf5', text_muted='#7c8aa8', success='#22c55e', danger='#ef4444', warning='#f59e0b', radius='14px', radius_sm='8px', font="-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif", font_mono="'JetBrai…` |
| `LIB_KEYFRAMES_CSS` | `'@keyframes nx-lib-pulse {\n  0%, 100% { opacity: 1; transform: scale(1); }\n  50% { opacity: 0.35; transform: scale(0.7); }\n}\n@keyframes nx-lib-gradient-shift {\n  0% { background-position: 0% 50%; }\n  100% { background-position: 200% 50%; }\n}\n@keyframes nx-lib-rise {\n  from { opacity: 0; transform: translateY(16px); }\n  to { opacity: 1; transform: translateY(0); }\n}\n@keyframes nx-lib-blink {\n  0%, 49% …` |
