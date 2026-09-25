# `nexoria.std.cartoon`

> Playful comic-book components: chunky outlined buttons and cards, speech bubbles, sticker badges, emoji avatars, blob progress.

| | |
|---|---|
| **Import** | `from nexoria.std.cartoon import cartoon_button, speech_bubble, …` |
| **Theme** | `CARTOON_THEME` — tokens `--nx-cartoon-coral`, `sunshine`, `mint`, `sky`, `grape`, `ink`, `paper`; apply with `App(theme=CARTOON_THEME)` ([why](../std.md#apply-the-family-theme-important)) |
| **One-per-page helper** | `cartoon_keyframes()` — needed for `wiggle`, `tilt`, `pop`, `bounce` |

| Function | Notes |
|---|---|
| `cartoon_button(*children, color, href, on_click, icon, size, wiggle, disabled)` | `size`: `sm|md|lg` |
| `cartoon_card(*children, title, sticker, color, tilt)` | `tilt=True` (default) rotates slightly, straightening on hover (pure `onmouseover`) |
| `comic_panel(*children, caption)` | A borderless strip of cards with a caption |
| `speech_bubble(text, direction, color)` | `left | right | bottom` tail |
| `thought_bubble(text, color)` | Cloud tail |
| `sticker_badge(text, shape, color, pop)` | `circle | star | burst` |
| `cartoon_avatar(emoji, size, bg, bounce)` | Flat colour circle + emoji |
| `blob_progress(value, max_value, color, label, emoji)` | Percentage computed and clamped to 0–100 for you |

```python
from nexoria.std.cartoon import cartoon_button, speech_bubble, cartoon_keyframes
el("div", cartoon_keyframes(), speech_bubble("Let's build!"), cartoon_button("Go", wiggle=True))
```

## API reference

### Classes

#### `class CartoonTheme(name: str = 'nexoria-cartoon', primary: str = '#6366f1', primary_hover: str = '#4f46e5', accent: str = '#22d3ee', background: str = '#0b0b12', surface: str = '#14141f', surface_alt: str = '#1b1b29', border: str = '#26263a', text: str = '#f3f3f7', text_muted: str = '#9797ad', success: str = '#22c55e', danger: str = '#ef4444', warning: str = '#f59e0b', radius: str = '14px', radius_sm: str = '8px', font: str = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-s..., font_mono: str = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace", space: str = '8px', shadow: str = '0 10px 30px rgba(0,0,0,0.35)', coral: str = '#FF6B6B', sunshine: str = '#FFD93D', mint: str = '#4ECDC4', sky: str = '#6FA8FF', grape: str = '#B892FF', ink: str = '#1F1B24', paper: str = '#FFFDF6') -> None`

CartoonTheme(name: 'str' = 'nexoria-cartoon', primary: 'str' = '#6366f1', primary_hover: 'str' = '#4f46e5', accent: 'str' = '#22d3ee', background: 'str' = '#0b0b12', surface: 'str' = '#14141f', surface_alt: 'str' = '#1b1b29', border: 'str' = '#26263a', text: 'str' = '#f3f3f7', text_muted: 'str' = '#9797ad', success: 'str' = '#22c55e', danger: 'str' = '#ef4444', warning: 'str' = '#f59e0b', radius: 'str' = '14px', radius_sm: 'str' = '8px', font: 'str' = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif", font_mono: 'str' = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace", space: 'str' = '8px', shadow: 'str' = '0 10px 30px rgba(0,0,0,0.35)', coral: 'str' = '#FF6B6B', sunshine: 'str' = '#FFD93D', mint: 'str' = '#4ECDC4', sky: 'str' = '#6FA8FF', grape: 'str' = '#B892FF', ink: 'str' = '#1F1B24', paper: 'str' = '#FFFDF6')

- **`.to_css_vars() -> str`**

### Functions

#### `cartoon_keyframes()`

A `<style>` `Element` carrying every cartoon `@keyframes` block. Drop it once anywhere in your root layout before using `cartoon_button(wiggle=True)`, `cartoon_card(tilt=True)`, `sticker_badge(pop=True)`, or `cartoon_avatar(bounce=True)`.

#### `cartoon_button(*children: Any, color: str = 'var(--nx-cartoon-coral)', href: Optional[str] = None, on_click: Optional[Callable] = None, icon: Optional[Element] = None, size: str = 'md', wiggle: bool = False, disabled: bool = False) -> Element`

`cartoon_button("Let's go!", color="var(--nx-cartoon-mint)", icon=Icon("mdi:rocket"))`.

`wiggle=True` gives it a playful idle wiggle (needs `cartoon_keyframes()` rendered once on the page). Click gives a satisfying "press" (shadow collapses, button shifts down) via plain `onmousedown`/`onmouseup` -- no JS bundle needed.

#### `cartoon_card(*children: Any, title: Optional[str] = None, sticker: Optional[Element] = None, color: str = 'var(--nx-cartoon-paper)', tilt: bool = True) -> Element`

`cartoon_card("Panel text", title="Chapter 1", sticker=Icon("mdi:star"))`. `tilt=True` (default) gives it a slight rotation that straightens out on hover -- purely `onmouseover`/`onmouseout`, no JS bundle.

#### `comic_panel(*children: Any, caption: Optional[str] = None) -> Element`

A borderless strip of `cartoon_card`s in a row, with an optional caption underneath.

#### `speech_bubble(text: str, *, direction: str = 'left', color: str = 'var(--nx-cartoon-paper)') -> Element`

`speech_bubble("Let's build something!", direction="left")`. `direction`: which side the pointer tail sits on -- "left" | "right" | "bottom".

#### `thought_bubble(text: str, *, color: str = 'var(--nx-cartoon-paper)') -> Element`

`thought_bubble("...maybe cartoons AND premium components?")` -- a cloud-tail dreamy variant.

#### `sticker_badge(text: str, *, shape: str = 'circle', color: str = 'var(--nx-cartoon-sunshine)', pop: bool = False) -> Element`

`sticker_badge("NEW!", shape="star", color="var(--nx-cartoon-coral)")`. `shape`: "circle" | "star" | "burst". `pop=True` gives it a one-shot pop-in animation on mount (needs `cartoon_keyframes()`).

#### `cartoon_avatar(*, emoji: str = '🦸', size: str = 'md', bg: str = 'var(--nx-cartoon-sky)', bounce: bool = False) -> Element`

`cartoon_avatar(emoji="🚀", bg="var(--nx-cartoon-mint)")` -- a flat-color circle with a big emoji.

#### `blob_progress(value: float, *, max_value: float = 100, color: str = 'var(--nx-cartoon-mint)', label: Optional[str] = None, emoji: str = '🐘') -> Element`

`blob_progress(65, label="Level up!")`. `value`/`max_value` are plain numbers; the percentage is computed and clamped to [0, 100] here, so callers never hand in an already-normalized percentage.

### Constants

| Name | Value |
|---|---|
| `CARTOON_THEME` | `CartoonTheme(name='nexoria-cartoon', primary='#6366f1', primary_hover='#4f46e5', accent='#22d3ee', background='#0b0b12', surface='#14141f', surface_alt='#1b1b29', border='#26263a', text='#f3f3f7', text_muted='#9797ad', success='#22c55e', danger='#ef4444', warning='#f59e0b', radius='14px', radius_sm='8px', font="-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif", font_mono="…` |
| `CARTOON_KEYFRAMES_CSS` | `'@keyframes nx-cartoon-wiggle {\n  0%, 100% { transform: rotate(-2deg); }\n  50% { transform: rotate(2deg); }\n}\n@keyframes nx-cartoon-bounce {\n  0%, 100% { transform: translateY(0); }\n  50% { transform: translateY(-8px); }\n}\n@keyframes nx-cartoon-pop {\n  0% { transform: scale(0.85); opacity: 0; }\n  60% { transform: scale(1.08); opacity: 1; }\n  100% { transform: scale(1); }\n}\n@keyframes nx-cartoon-float …` |
