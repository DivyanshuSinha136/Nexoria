# `tests/` — the test suite

> `pytest` suite covering rendering, diffing, the WebSocket round-trip, every integration's serialisation, the `std` library, and the native tiers.

| | |
|---|---|
| **Run** | `pip install -e .[dev] && pytest -q` (the `dev` extra installs `pytest`, `pytest-asyncio`, `black`, `ruff`; also `pip install httpx` for Starlette's `TestClient`) |
| **Size** | 18 files, ~250 tests |
| **Last observed run** | 246 passed, 4 skipped, 1 collection error (see below) |

| File | Focus |
|---|---|
| `test_app.py` | SSR routes, 404, runtime asset, health |
| `test_websocket_interactivity.py` | Full click → patch round-trip, unknown session ignored, session cleanup on disconnect |
| `test_render_and_diff.py` | HTML serialisation and differ vectors (shared by Python, Rust and C++ backends) |
| `test_reload_resolution.py` | `run(reload=True)` module/variable discovery |
| `test_styling.py`, `test_modern_defaults.py` | `Theme`, `Stylesheet`, toggle, head contents, SEO/OG, favicon |
| `test_gsap.py`, `test_chartjs_videojs.py`, `test_aggrid_spline_vroid_tailwind.py`, `test_bootstrap.py`, `test_more_adapters.py` | Each integration's element/JSON output and head tags |
| `test_js_in_python.py` | `js()`, `Script`, `JSFunction` |
| `test_std.py`, `test_std_charts.py`, `test_std_icons.py` | The `std` families |
| `test_native.py`, `test_gpu.py`, `test_desktop_mobile.py` | Embedded JS engine and npm client, GPU tier fallbacks, scaffolders |

Tests that need a compiled tier or the network **skip** when it is unavailable.

## Known issue: one collection error

`tests/test_std.py` imports the component function `testimonial` at module level. Because the name starts with `test`, pytest collects it as a test function and fails on its missing fixtures (`ERROR tests/test_std.py::testimonial`). It is a naming artefact, not a product bug. Fix by importing the module (`from nexoria.std import premium`) or aliasing (`from nexoria.std.premium import testimonial as testimonial_card`).

## Tooling

Reload behaviour, the WebSocket path and SSR are tested with Starlette's `TestClient` (its `httpx` integration currently emits a deprecation warning suggesting `httpx2`).
