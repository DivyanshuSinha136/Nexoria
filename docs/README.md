# Nexoria Documentation

Nexoria is a Python-native web framework: you describe the interface as a tree of Python objects, the server renders it to real HTML, and a tiny client runtime keeps it live with DOM patches over a WebSocket. This folder documents every part of the project.

> Version 0.1.0 · MIT · Author Divyanshu Sinha · Ecosystem: Pythonaibrain

## Start here

| If you want to… | Read |
|---|---|
| Understand how it all fits together | [ARCHITECTURE.md](ARCHITECTURE.md) |
| See the request/event/build flows as diagrams | [FLOWCHART.md](FLOWCHART.md) |
| Look up a class, function, flag or endpoint | [TOP-LEVEL-API-REFRANCE.md](TOP-LEVEL-API-REFRANCE.md) |
| Find out *why* something is the way it is, or fix a problem | [Q-A.md](Q-A.md) |
| Learn one package in depth | the per-package pages below |

---

## Getting started

### 1. Install

```bash
pip install nexoria            # from PyPI
# or from a checkout:
pip install -e .
```

Requires Python ≥ 3.9. No Node, Rust, C++ or Go is needed to run apps.

### 2. Your first app

```python
# app.py
from nexoria import App, Component, Router, State, el

class Counter(Component):
    def setup(self):
        self.state = State({"count": 0})

    def render(self):
        return el("div",
            el("h1", f"Count: {self.state['count']}"),
            el("button", "Increment", class_="nx-btn",
               on_click=lambda e: self.state.update(count=self.state["count"] + 1)),
            class_="nx-card nx-container",
        )

router = Router().add("/", Counter)
app = App(name="Counter", router=router)

if __name__ == "__main__":
    app.run(reload=True)          # http://127.0.0.1:8000
```

```bash
python app.py
```

View source in the browser: the page is complete HTML. Click the button: the server updates state, re-renders, and the browser receives a two-patch update.

### 3. Add a second page with a parameter

```python
class User(Component):
    def render(self):
        return el("h1", f"User {self.props['id']}")

router.add("/users/:id", User)          # /users/42  →  User(id="42")
```

### 4. Add something from the standard library

```python
from nexoria.std.premium import premium_button, stat_card
from nexoria.std.charts import line_chart, chart_styles, charts_runtime

el("div", chart_styles(), charts_runtime(),
   stat_card("Revenue", "$482K", trend="+12.4%"),
   line_chart([12, 19, 14, 22, 30], labels=["Mon", "Tue", "Wed", "Thu", "Fri"]),
   premium_button("Get started", href="/signup"))
```

### 5. Turn on a third-party library

```python
from nexoria.chartjs import Chart, Dataset
app = App(name="Report", router=router, chartjs=True)       # flag adds the CDN + adapter
Chart(type="bar", labels=["A", "B"], datasets=[Dataset("Sales", [3, 5])]).to_element()
```

### 6. Ship it

```bash
nexoria doctor                              # what is active, what is missing
nexoria native build --with-go-server       # optional: fast, firewalled edge server
python app.py                               # App.run() uses it automatically if built
```

---

## Documentation map

### Cross-cutting

| Document | Contents |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Principles, layers, repository layout, rendering, live protocol, differ, adapters, native tiers, scaling, security, limitations |
| [FLOWCHART.md](FLOWCHART.md) | 13 Mermaid diagrams: SSR, hydration, event cycle, differ, router, `run()`, Go edge, head assembly, adapters, native selection, build pipelines, theme toggle |
| [TOP-LEVEL-API-REFRANCE.md](TOP-LEVEL-API-REFRANCE.md) | Package-root API, `App`/`Component`/`el`/`State`/`Router`/`Stylesheet`, sub-package index, CLI, HTTP/WebSocket surface, browser globals, env vars |
| [Q-A.md](Q-A.md) | Design rationale, how-tos, troubleshooting, limitations |

### Core framework

| Page | Folder | Summary |
|---|---|---|
| [core](core.md) | `nexoria/core/` | `App`, `Component`, `Element`/`el()` |
| [state](state.md) | `nexoria/state/` | `State`, `use_state` |
| [router](router.md) | `nexoria/router/` | Routes, params, wildcard, guards |
| [render](render.md) | `nexoria/render/` | HTML serialiser, differ, backends |
| [style](style.md) | `nexoria/style/` | `Theme`, `Stylesheet`, dark/light toggle |
| [middleware](middleware.md) | `nexoria/middleware/` | Request hooks |
| [cache](cache.md) | `nexoria/cache/` | Fingerprinting |
| [runtime](runtime.md) | `nexoria/runtime/` | Browser runtime, base CSS, adapters |
| [cli](cli.md) | `nexoria/cli/` | The `nexoria` command |
| [js](js.md) | `nexoria/js/` | `js()`, `Script`, `JSFunction` |
| [ssr](ssr.md) | `nexoria/ssr/` | Empty/reserved |

### Standard library — [std](std.md)

[premium](std/premium.md) · [cartoon](std/cartoon.md) · [lib](std/lib.md) · [icons](std/icons.md) · [alert](std/alert.md) · [animation](std/animation.md) · [observer](std/observer.md) · [physics2d](std/physics2d.md) · [scroll](std/scroll.md) · [svg](std/svg.md) · [charts](std/charts.md) · [typography](std/typography.md) · [webtools](std/webtools.md)

### Third-party integrations

| Page | Library | App flag |
|---|---|---|
| [threejs](threejs.md) | Three.js | `threejs=True` |
| [babylonjs](babylonjs.md) | Babylon.js | `babylonjs=True` |
| [vroid](vroid.md) | three-vrm / VRM avatars | `vroid=True` |
| [spline](spline.md) | Spline | `spline=True` |
| [gsap](gsap.md) | GSAP + plugins | `gsap=True`, `gsap_plugins=[…]` |
| [chartjs](chartjs.md) | Chart.js | `chartjs=True` |
| [videojs](videojs.md) | video.js | `videojs=True` |
| [aggrid](aggrid.md) | AG Grid Community | `aggrid=True` |
| [openlayers](openlayers.md) | OpenLayers | `openlayers=True` |
| [bootstrap](bootstrap.md) | Bootstrap 5 | `bootstrap=True` |
| [tailwind](tailwind.md) | Tailwind CSS | `tailwind=True` |
| [iconify](iconify.md) | Iconify | `iconify=True` |
| [shiki](shiki.md) | Shiki | `shiki=True` |
| [qrcode](qrcode.md) | qr-code-styling | `qrcode=True` |
| [barcode](barcode.md) | bwip-js | `barcode=True` |
| [webcam](webcam.md) | webcam-easy | `webcam=True` |
| [translate](translate.md) | Google Translate (server-side) | — |

### Native, packaging and tooling

| Page | Folder | Summary |
|---|---|---|
| [native](native.md) | `nexoria/native/` | Rust safety core, C++ VDOM, QuickJS engine + npm client, Go edge server, CUDA |
| [rust_ext](rust_ext.md) | `nexoria/rust_ext/` | PyO3 differ and hashing |
| [desktop](desktop.md) | `nexoria/desktop/` | Electron scaffold |
| [mobile](mobile.md) | `nexoria/mobile/` | Capacitor scaffold |
| [tools](tools.md) | `tools/` | Node production build |
| [examples](examples.md) | `examples/` | 13 runnable demos |
| [tests](tests.md) | `tests/` | Test suite |

---

## Conventions used in these docs

- **API reference** sections at the bottom of each page are generated from the live source (signatures and docstrings), so they match the code shipped in this version.
- **Known issues** are called out where they apply. They are behaviours observed in the current source, not opinions; the summary table is in [ARCHITECTURE §15](ARCHITECTURE.md#15-known-limitations-summary).
- Code samples are checked to import and run against this version.
