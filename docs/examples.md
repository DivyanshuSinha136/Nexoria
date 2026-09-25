# `examples/` — runnable demo apps

> Thirteen self-contained apps, each a single `app.py` you can run with `python app.py` (default `http://127.0.0.1:8000`).

| Example | Shows | Flags / packages |
|---|---|---|
| `counter_app` | Stateful counter, two routes, base classes + scoped `Stylesheet` | core, state, router, style |
| `blog_demo` | "Inkwell" blog: home, `/posts/:slug`, about, colophon — built from `nexoria.std.*` | routing with params, `std` |
| `ecommerce_demo` | Catalog, product detail, cart, checkout with steppers and a QR confirmation | `gsap`, `iconify`, `qrcode`, theme toggle |
| `threejs_demo` | A spinning 3D cube in an `nx-card` | `threejs=True` |
| `gsap_demo` | Timeline entrance + ScrollTrigger reveal + client-side play/pause | `gsap=True, gsap_plugins=["ScrollTrigger"]` |
| `dashboard_demo` | Chart.js chart and a themed video.js player with a demo plugin | `chartjs=True, videojs=True` |
| `bootstrap_demo` | Bootstrap 5 with a `BootstrapTheme`, tooltips/popovers | `bootstrap=True` |
| `aggrid_tailwind_demo` | AG Grid plus Tailwind Play CDN | `aggrid=True, tailwind=True` |
| `premium_cartoon_landing_demo` | Premium hero/nav/pricing above a cartoon section | `std.premium`, `std.cartoon` |
| `std_lib_demo` | The full dark landing page from `std.lib` components only | `std.lib` |
| `std_animation_demo` | Every runtime animation plus the keyframes engine | `std.animation` |
| `std_interactive_demo` | Tooltip, copy, modal, accordion, tabs, alerts, scroll tools — all client-side | `std.webtools/alert/scroll` |
| `std_physics_observer_demo` | Bouncing icon, confetti burst, observer gestures, SVG paths, icons | `std.physics2d/observer/svg/icons` |

## Running one

```bash
pip install nexoria
cd examples/counter_app
python app.py                # http://127.0.0.1:8000
```

The apps that need CDN libraries (`threejs`, `gsap`, `chartjs`, `videojs`, `bootstrap`, `aggrid`, `iconify`, `qrcode`) need internet access in the browser. The `std_*` demos need none. If a demo styles itself with a family theme's variables, remember [the theming note](std.md#apply-the-family-theme-important).

Each demo's module docstring describes what it demonstrates and how to run it.
