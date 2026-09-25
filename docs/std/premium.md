# `nexoria.std.premium`

> A restrained, SaaS/landing-page component family: deep surfaces, gold/indigo accents, soft elevation.

| | |
|---|---|
| **Import** | `from nexoria.std.premium import premium_button, hero_section, …` |
| **Theme** | `PREMIUM_THEME` (a `Theme` subclass adding `--nx-premium-gold`, `-gold-soft`, `-glass-bg`, `-glass-border`, `-ring`) — pass it as `App(theme=PREMIUM_THEME)`; see [the theming note](../std.md#apply-the-family-theme-important) |
| **One-per-page helper** | `premium_keyframes()` — needed for `shimmer=True`, `glow=True`, `hero_section(animate=True)` |

## Components

| Function | Notes |
|---|---|
| `premium_button(*children, variant, size, href, on_click, icon, full_width, shimmer, disabled, class_)` | `size`: `sm|md|lg`. With `href` it renders as a link. |
| `premium_badge(text, variant)` | `primary | gold | success | danger | neutral` |
| `premium_avatar(src=, initials=, size, status)` | `status`: `online | busy | away` |
| `premium_card(*children, title, subtitle, elevated, glow, class_)` | `glow` pulses a gold glow |
| `glass_panel(*children)` | `backdrop-filter: blur` surface |
| `stat_card(label, value, icon, trend)` | `trend` is shown as given — prefix `-` yourself for declines |
| `pricing_card(plan, price, period, features, highlighted, cta_*)` | `highlighted` = recommended plan |
| `hero_section(title, subtitle, eyebrow, cta_*, secondary_cta_*, animate)` | Up to two CTAs |
| `feature_grid([{"icon", "title", "desc"}])` | `icon` optional |
| `testimonial(quote, author, role, avatar_src, rating)` | Stars rendered as `★` |
| `premium_navbar(brand, links, cta_*, sticky)` | `links` = `(label, href)` pairs; `brand` may be a string or any element/wrapper |
| `premium_footer(brand, columns, socials, tagline)` | `columns=[{"title", "links": [...]}]` |

```python
from nexoria.std.premium import premium_button, stat_card, premium_keyframes
el("div", premium_keyframes(),
   stat_card("Revenue", "$482K", trend="+12.4%"),
   premium_button("Get Started", href="/signup", shimmer=True))
```

## API reference

### Classes

#### `class PremiumTheme(name: str = 'nexoria-premium', primary: str = '#6366f1', primary_hover: str = '#4f46e5', accent: str = '#22d3ee', background: str = '#0b0b12', surface: str = '#14141f', surface_alt: str = '#1b1b29', border: str = '#26263a', text: str = '#f3f3f7', text_muted: str = '#9797ad', success: str = '#22c55e', danger: str = '#ef4444', warning: str = '#f59e0b', radius: str = '14px', radius_sm: str = '8px', font: str = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-s..., font_mono: str = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace", space: str = '8px', shadow: str = '0 10px 30px rgba(0,0,0,0.35)', gold: str = '#d4af37', gold_soft: str = '#f1dfa3', glass_bg: str = 'rgba(20, 20, 31, 0.55)', glass_border: str = 'rgba(255, 255, 255, 0.10)', highlight_ring: str = 'rgba(99, 102, 241, 0.45)') -> None`

PremiumTheme(name: 'str' = 'nexoria-premium', primary: 'str' = '#6366f1', primary_hover: 'str' = '#4f46e5', accent: 'str' = '#22d3ee', background: 'str' = '#0b0b12', surface: 'str' = '#14141f', surface_alt: 'str' = '#1b1b29', border: 'str' = '#26263a', text: 'str' = '#f3f3f7', text_muted: 'str' = '#9797ad', success: 'str' = '#22c55e', danger: 'str' = '#ef4444', warning: 'str' = '#f59e0b', radius: 'str' = '14px', radius_sm: 'str' = '8px', font: 'str' = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif", font_mono: 'str' = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace", space: 'str' = '8px', shadow: 'str' = '0 10px 30px rgba(0,0,0,0.35)', gold: 'str' = '#d4af37', gold_soft: 'str' = '#f1dfa3', glass_bg: 'str' = 'rgba(20, 20, 31, 0.55)', glass_border: 'str' = 'rgba(255, 255, 255, 0.10)', highlight_ring: 'str' = 'rgba(99, 102, 241, 0.45)')

- **`.to_css_vars() -> str`**

### Functions

#### `premium_keyframes()`

A `<style>` `Element` carrying every premium `@keyframes` block. Drop it once anywhere in your root layout (e.g. next to `nexoria.style.components.theme_toggle_button`) before using `premium_card(glow=True)`, `premium_button(shimmer=True)`, or `hero_section(..., animate=True)`.

#### `premium_button(*children: Any, variant: str = 'primary', size: str = 'md', href: Optional[str] = None, on_click: Optional[Callable] = None, icon: Optional[Element] = None, full_width: bool = False, shimmer: bool = False, disabled: bool = False, class_: Optional[str] = None) -> Element`

`premium_button("Get Started", variant="primary", href="/signup")`

`variant`: "primary" | "outline" | "ghost" | "gold" `shimmer`: adds a moving highlight sweep; requires `nexoria.std.premium.theme.premium_keyframes()` to be rendered once on the page.

#### `premium_badge(text: str, *, variant: str = 'primary') -> Element`

`premium_badge("New", variant="gold")`. variant: primary | gold | success | danger | neutral.

#### `premium_avatar(*, src: Optional[str] = None, initials: Optional[str] = None, size: str = 'md', status: Optional[str] = None) -> Element`

`premium_avatar(initials="DS", status="online")` or `premium_avatar(src="/me.jpg", size="lg")`.

#### `premium_card(*children: Any, title: Optional[str] = None, subtitle: Optional[str] = None, elevated: bool = True, glow: bool = False, class_: Optional[str] = None) -> Element`

A general-purpose surface card. `glow` pulses a soft gold glow (needs `premium_keyframes()` rendered once on the page).

#### `glass_panel(*children: Any, class_: Optional[str] = None) -> Element`

Frosted glass surface (`backdrop-filter: blur`) for hero overlays and floating callouts over imagery or gradients.

#### `stat_card(label: str, value: str, *, icon: Optional[Element] = None, trend: Optional[str] = None) -> Element`

A KPI tile: `stat_card("Revenue", "$482K", trend="+12.4%")`. `trend` is shown as-is; prefix it with "-" yourself for a decline (kept as plain text rather than inferring sign, so locales that don't use a leading "-" for negatives aren't misrendered).

#### `pricing_card(plan: str, price: str, *, period: str = '/mo', features: Sequence[str] = (), highlighted: bool = False, cta_text: str = 'Get Started', cta_href: str = '#', cta_shimmer: bool = False, cta_icon: Optional[Element] = None, cta_on_click: Optional[Callable] = None) -> Element`

A pricing-plan tile with a feature checklist and a CTA button. `highlighted=True` renders it as the "recommended" plan (gold border + badge, slightly raised).

#### `hero_section(title: str, *, subtitle: Optional[str] = None, eyebrow: Optional[str] = None, cta_text: Optional[str] = None, cta_href: str = '#', cta_shimmer: bool = False, cta_icon: Optional[Element] = None, cta_variant: str = 'primary', cta_on_click: Optional[Callable] = None, secondary_cta_text: Optional[str] = None, secondary_cta_href: str = '#', secondary_cta_shimmer: bool = False, secondary_cta_icon: Optional[Element] = None, secondary_cta_variant: str = 'outline', secondary_cta_on_click: Optional[Callable] = None, animate: bool = False) -> Element`

Full-width hero with an optional eyebrow label, subtitle, and up to two CTAs. `animate=True` fades the content up on load (needs `premium_keyframes()` rendered once on the page).

#### `feature_grid(features: Sequence[Mapping[str, Any]]) -> Element`

`feature_grid([{"icon": Icon("mdi:rocket"), "title": "Fast", "desc": "..."}])`. Each item needs `title` and `desc`; `icon` is optional.

#### `testimonial(quote: str, author: str, *, role: Optional[str] = None, avatar_src: Optional[str] = None, rating: Optional[int] = 5) -> Element`

`testimonial("This shipped our landing page in a day.", "Priya N.", role="Founder, Acme")`.

#### `premium_navbar(brand: Any, *, links: Sequence[tuple] = (), cta_text: Optional[str] = None, cta_href: str = '#', cta_shimmer: bool = False, cta_icon: Optional[Element] = None, cta_variant: str = 'primary', cta_on_click: Optional[Callable] = None, sticky: bool = True) -> Element`

`premium_navbar("Acme", links=[("Product", "/product"), ("Pricing", "/pricing")], cta_text="Sign up")`. `links` is a sequence of `(label, href)` pairs. `brand` may be a string or any `Element`/`.to_element()`-able wrapper (e.g. a logo `nexoria.iconify.Icon` next to text -- pass a list as `brand` and it'll be spread as the brand block's children).

#### `premium_footer(brand: Any, *, columns: Sequence[dict] = (), socials: Sequence[tuple] = (), tagline: Optional[str] = None) -> Element`

`premium_footer("Acme", columns=[{"title": "Product", "links": [("Pricing", "/pricing")]}], socials=[("Twitter", "https://x.com/...")])`.

### Constants

| Name | Value |
|---|---|
| `PREMIUM_THEME` | `PremiumTheme(name='nexoria-premium', primary='#6366f1', primary_hover='#4f46e5', accent='#22d3ee', background='#0b0b12', surface='#14141f', surface_alt='#1b1b29', border='#26263a', text='#f3f3f7', text_muted='#9797ad', success='#22c55e', danger='#ef4444', warning='#f59e0b', radius='14px', radius_sm='8px', font="-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif", font_mono="…` |
| `PREMIUM_KEYFRAMES_CSS` | `'@keyframes nx-premium-shimmer {\n  0% { background-position: -200% 0; }\n  100% { background-position: 200% 0; }\n}\n@keyframes nx-premium-fade-up {\n  from { opacity: 0; transform: translateY(14px); }\n  to { opacity: 1; transform: translateY(0); }\n}\n@keyframes nx-premium-glow {\n  0%, 100% { box-shadow: 0 0 0 rgba(212, 175, 55, 0); }\n  50% { box-shadow: 0 0 26px rgba(212, 175, 55, 0.35); }\n}'` |
