"""
nexoria.std
=============
Nexoria's built-in "standard library" of ready-made web components --
the batteries that ship with the framework so a real page can be put
together without hand-rolling every button and card from `el()`.

Each family lives in its own sub-package so you only pull in the
look (or tool) you actually want:

    nexoria.std.premium    -- polished, business/SaaS-grade components
                              (buttons, cards, navbars, pricing tables,
                              hero sections, testimonials, badges...)
    nexoria.std.cartoon    -- playful, comic-styled components (bouncy
                              buttons, sticker badges, speech bubbles,
                              blob progress bars, tilted cards...)
    nexoria.std.lib        -- dark, dev-tool/terminal-styled components
                              (the look of Nexoria's own landing page:
                              near-black surfaces, cyan/pink accents,
                              code-editor chrome, mono type)
    nexoria.std.icons      -- 2,078 Bootstrap Icons, vendored as SVG
                              data and rendered as real inline `<svg>`
                              Elements -- no CDN, no icon font, unlike
                              `nexoria.iconify`/`nexoria.bootstrap`'s
                              `BOOTSTRAP_ICONS_TAG`.
    nexoria.std.alert      -- feedback surfaces: dismissible banner,
                              auto-dismissing toast, inline alert.
    nexoria.std.animation  -- scroll-aware runtime animations (reveals,
                              count-up, typewriter, scramble, split-
                              text, SVG draw/morph) plus a pure-Python
                              CSS `@keyframes` engine and preset library.
    nexoria.std.observer   -- dependency-free wheel/pointer-drag engine
                              (directional callbacks, raw delta, hover,
                              press/release, click) -- GSAP Observer-alike.
    nexoria.std.physics2d  -- dependency-free projectile/burst engine
                              (velocity, gravity, friction, spin, floor
                              bounce) -- GSAP Physics2DPlugin-alike.
    nexoria.std.scroll     -- page-scrolling tools: back-to-top button,
                              top progress bar, smooth anchor links,
                              scrollable container.
    nexoria.std.svg        -- low-level SVG drawing support: a fluent
                              `PathBuilder` for `<path d="...">` data,
                              shape helpers, and `<svg>`/`<path>` wrappers.
    nexoria.std.charts     -- animated SVG charts built on `std.svg`:
                              line/area, bar (vertical/horizontal,
                              grouped), pie/donut, sparkline, and a
                              single-value radial gauge -- entrance
                              animations (grow, draw-in, pop, sweep)
                              via one small IntersectionObserver
                              runtime, no chart-library dependency.
    nexoria.std.typography -- a custom typography engine: self-hosted
                              `@font-face` fonts (variable fonts
                              included) plus a fluid `clamp()`-based
                              type scale, consumed as `style=` dicts
                              or `--nx-font-*`/`--nx-text-*` variables.
    nexoria.std.webtools   -- general-purpose UI utilities: tooltip,
                              copy-to-clipboard button, modal dialog,
                              accordion, tabs.

All of them follow the same conventions as the rest of the framework:

  * every component is a plain function that returns an `Element`
    (or, where it takes children, a `*children` -> `Element`), so it
    drops straight into `el()` trees and `Component.render()` bodies
    -- no base class to subclass, no required wiring.
  * static look-and-feel ships as inline `style=` (via `el()`'s own
    dict -> CSS-string convenience) plus theme CSS variables
    (`--nx-*`, `--nx-premium-*`, `--nx-cartoon-*`), so a component
    renders correctly wherever it's dropped in, with zero setup.
  * hover/press micro-interactions use plain `onmouseover=`/
    `onmouseout=`/`onmousedown=` attributes (not `on_*`, so they're
    literal HTML handled by the browser -- see `nexoria.core.element`
    and `nexoria.style.components.theme_toggle_button` for the same
    trick) -- no server round-trip, no JS bundle required.
  * `on_click=` is still accepted wherever it makes sense and is
    dispatched the normal Nexoria way (Component state -> re-render).
  * animated components (`nexoria.std.cartoon`'s wiggle/bounce/pop,
    `nexoria.std.premium`'s shimmer/fade-up) need their `@keyframes`
    declared once per page -- call `cartoon_keyframes()` /
    `premium_keyframes()` (each returns a plain `<style>` `Element`)
    anywhere in your root layout, same idea as
    `nexoria.bootstrap`'s adapter tag: opt in once, use everywhere.

Nothing here is registered on `App` (no `App(std=True)` flag) because
there's no CDN asset or client adapter to load -- it's pure Python,
so a plain import is all you need:

    from nexoria.std.premium import premium_button, hero_section
    from nexoria.std.cartoon import cartoon_button, speech_bubble
    from nexoria.std.lib import lib_button, lib_hero
    from nexoria.std.icons import Icon
    from nexoria.std.alert import toast
    from nexoria.std.animation import reveal_styles, animate_in
    from nexoria.std.observer import observer_runtime, observer_region
    from nexoria.std.physics2d import physics2d_runtime, physics2d_burst
    from nexoria.std.scroll import scroll_to_top_button
    from nexoria.std.svg import PathBuilder, svg_canvas
    from nexoria.std.charts import line_chart, bar_chart, pie_chart, chart_styles, charts_runtime
    from nexoria.std.typography import font_face, font_stack, styled_text
    from nexoria.std.webtools import tooltip, modal_dialog
    el("button", Icon("cart-fill", size="1.1rem"), " Add to cart")

Each sub-package is also importable as a plain namespace off
`nexoria.std` itself (e.g. `nexoria.std.premium.premium_button`),
which is what the imports below expose.
"""

from __future__ import annotations

from . import premium
from . import cartoon
from . import lib
from . import icons
from . import alert
from . import animation
from . import observer
from . import physics2d
from . import scroll
from . import svg
from . import charts
from . import typography
from . import webtools

__all__ = [
    "premium",
    "cartoon",
    "lib",
    "icons",
    "alert",
    "animation",
    "observer",
    "physics2d",
    "scroll",
    "svg",
    "charts",
    "typography",
    "webtools",
]
