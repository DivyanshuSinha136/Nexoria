# `nexoria.std` — the standard component library

> Thirteen pure-Python component families: three visual design systems, icons, feedback surfaces, animation, charts, SVG tools, typography, scrolling and utility widgets. No CDN asset, no `App(...)` flag.

| | |
|---|---|
| **Import** | `from nexoria.std.premium import premium_button` … or `from nexoria import std; std.premium.premium_button` |
| **Source** | `nexoria/std/` (about 6,900 lines of Python + 2,078 vendored SVG icons) |
| **Enabled by** | Nothing — plain imports |
| **Depends on** | Only the rest of Nexoria |

## The families

| Package | Purpose | Page |
|---|---|---|
| `std.premium` | Polished SaaS/landing look: buttons, cards, glass panels, stat/pricing cards, hero, feature grid, testimonial, navbar, footer | [premium](std/premium.md) |
| `std.cartoon` | Playful comic look: chunky buttons/cards, comic panels, speech/thought bubbles, sticker badges, emoji avatars, blob progress | [cartoon](std/cartoon.md) |
| `std.lib` | Dark dev-tool look (the Nexoria landing page): pills, code window, feature cards, hero, pipeline steps, install CTA, navbar/footer | [lib](std/lib.md) |
| `std.icons` | 2,078 Bootstrap Icons as inline SVG, offline | [icons](std/icons.md) |
| `std.alert` | Banner, toast, inline alert | [alert](std/alert.md) |
| `std.animation` | Scroll-aware reveals, counters, typewriter, scramble, split text, SVG draw/morph **and** a CSS `@keyframes` engine with 21 presets | [animation](std/animation.md) |
| `std.observer` | GSAP-Observer-style wheel/drag/hover/click callbacks | [observer](std/observer.md) |
| `std.physics2d` | GSAP-Physics2D-style projectile motion and confetti burst | [physics2d](std/physics2d.md) |
| `std.scroll` | Progress bar, back-to-top, smooth anchors, scroll container | [scroll](std/scroll.md) |
| `std.svg` | `PathBuilder` and SVG wrappers | [svg](std/svg.md) |
| `std.charts` | Animated SVG line/area/bar/pie/donut/sparkline/gauge | [charts](std/charts.md) |
| `std.typography` | `@font-face` registry + fluid `clamp()` type scale | [typography](std/typography.md) |
| `std.webtools` | Tooltip, copy button, modal, accordion, tabs | [webtools](std/webtools.md) |

## Conventions shared by every component

- **A component is a function returning an `Element`** (or taking `*children`). It drops straight into `el()` trees and `Component.render()`. No base class, no registration.
- **Look ships as inline `style=`** plus the `--nx-*` CSS variables, so it renders correctly wherever it is dropped.
- **Hover/press micro-interactions use literal HTML attributes** (`onmouseover=`, `onmousedown=`, `onclick=`) — executed by the browser, no server round-trip. `on_click=` (a Python callable) is still accepted where sensible and is dispatched to the server the normal way.
- **One-per-page helpers.** Components that need `@keyframes` or a script expect you to render a helper **once** anywhere in your root layout: `premium_keyframes()`, `cartoon_keyframes()`, `lib_keyframes()`, `keyframes_style()`, `animation_runtime()` + `reveal_styles()`, `scroll_runtime()`, `charts_runtime()` + `chart_styles()`, `physics2d_runtime()`, `observer_runtime()`, `typography_style_tag()`. Without them components still render statically; you just don't get the motion.
- **The runtimes are idempotent** (`window.__nxAnim`, `__nxScroll`, `__nxCharts`, …), so rendering a helper twice is harmless.

## Apply the family theme (important)

`premium`, `cartoon` and `lib` colour themselves with family-specific CSS variables — `--nx-premium-gold`, `--nx-cartoon-coral`, `--nx-lib-cyan`, and so on. They are **only defined if you pass the family theme to the app**:

```python
from nexoria.std.cartoon import CARTOON_THEME
app = App(name="x", router=router, theme=CARTOON_THEME)     # also re-colours nx-btn, nx-card, …
```

Without it the variables are undefined (the components reference them without fallbacks), so accents such as gold or coral will not render. `PREMIUM_THEME`, `CARTOON_THEME` and `LIB_THEME` each extend the base `Theme` (so they also re-skin `nx-*` classes); `LIB_THEME` additionally swaps the base surfaces for near-black.

Only one `theme=` fits an app. To **mix families on one page**, keep the default theme and declare just the tokens you need:

```python
from nexoria import Stylesheet
tokens = Stylesheet({":root": {
    "--nx-premium-gold": "#d4af37", "--nx-premium-gold-soft": "#f1dfa3",
    "--nx-cartoon-coral": "#FF6B6B", "--nx-cartoon-sunshine": "#FFD93D",
    "--nx-cartoon-mint": "#4ECDC4", "--nx-cartoon-sky": "#6FA8FF",
    "--nx-cartoon-ink": "#1F1B24", "--nx-cartoon-paper": "#FFFDF6",
}})
app = App(name="x", router=router, styles=tokens)
```

(Use `PREMIUM_THEME.to_css_vars()` / `CARTOON_THEME.to_css_vars()` / `LIB_THEME.to_css_vars()` to see every token each family defines.)

## Quick tour

```python
from nexoria import App, Component, el, Router
from nexoria.std.premium import premium_navbar, hero_section, pricing_card, premium_keyframes, PREMIUM_THEME
from nexoria.std.animation import animation_runtime, reveal_styles, animate_in, animated_counter
from nexoria.std.charts import chart_styles, charts_runtime, line_chart, radial_gauge

class Home(Component):
    def render(self):
        return el("div",
            premium_keyframes(), animation_runtime(), reveal_styles(), chart_styles(), charts_runtime(),
            premium_navbar("Acme", links=[("Pricing", "/pricing")], cta_text="Sign up"),
            hero_section("Build fast", subtitle="Ship it today", cta_text="Get started", animate=True),
            animate_in(el("h2", "Trusted"), effect="fade-up"),
            animated_counter(48200, prefix="$", suffix=" raised"),
            pricing_card("Pro", "$29", features=["Unlimited projects"], highlighted=True),
            line_chart([12, 19, 14, 22, 30], labels=["Mon", "Tue", "Wed", "Thu", "Fri"]),
            radial_gauge(72, label="72%"),
        )

app = App(name="Acme", router=Router().add("/", Home), theme=PREMIUM_THEME)
```

Runnable pages that combine many families: `examples/premium_cartoon_landing_demo`, `examples/std_lib_demo`, `examples/blog_demo` (see [examples](examples.md)).
