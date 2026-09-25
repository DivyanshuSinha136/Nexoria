"""
Nexoria example: nexoria.std.lib -- the dark, dev-tool/terminal-styled
component family (the look of Nexoria's own landing page). Builds a
full marketing page purely from ready-made `nexoria.std` components:
a sticky navbar, a split hero with a live syntax-highlighted code
window, a connected "request journey" step pipeline, a numbered
feature grid, an integrations strip, an install call-to-action, and
a footer -- no hand-rolled `el()` trees, no CSS file, no CDN asset.

Run:
    pip install nexoria
    cd examples/std_lib_demo
    python app.py
    # open http://127.0.0.1:8000
"""

from nexoria import App, Component, el, Router

from nexoria.std.icons import Icon
from nexoria.std.lib import (
    lib_keyframes, lib_grid_background,
    lib_navbar, lib_footer,
    lib_hero, pipeline_steps, feature_trio, integrations_row, install_cta,
)


APP_CODE = '''from nexoria import App, Component, el, State, Router

class Counter(Component):
    def setup(self):
        self.state = State({"count": 0})

    def render(self):
        return el("div",
            el("h1", "Nexoria Counter"),
            el("p", f"Clicked {self.state['count']} times"),
            el("button", "Increment", on_click=lambda e: self.state.update(
                count=self.state["count"] + 1)),
        )

router = Router()
router.add("/", Counter)
app = App(name="My App", router=router)
app.run(reload=True)
'''


class Home(Component):
    def render(self):
        return el(
            "div",
            # Shared assets for the "lib" family -- declared once per page.
            lib_keyframes(),
            lib_grid_background(),

            lib_navbar(
                "Nexoria",
                glyph=Icon("lightning-charge-fill", size="16px", color="#03141a"),
                version="v0.1.0",
                links=[
                    ("Architecture", "#architecture"),
                    ("Features", "#features"),
                    ("Integrations", "#integrations"),
                ],
                github_href="https://github.com/DivyanshuSinha136/nexoria",
            ),

            lib_hero(
                "Full-stack in",
                highlight="pure Python.",
                eyebrow="Python, all the way through",
                subtitle=(
                    "Describe your entire UI as a tree of Python objects. "
                    "Nexoria renders it to real HTML for the first paint and "
                    "keeps the DOM in sync with live, WebSocket-pushed patches."
                ),
                primary_cta="Start building",
                primary_href="#install",
                secondary_cta="Explore source",
                secondary_href="https://github.com/DivyanshuSinha136/nexoria",
                stats=["Zero JSX", "~4KB client runtime", "Rust hot path (optional)"],
                code=APP_CODE,
                code_filename="app.py",
                animate=True,
            ),

            pipeline_steps(
                [
                    {"icon": Icon("filetype-py"), "number": "01",
                     "title": "Python tree", "desc": "Components, routes, and state -- one Python process."},
                    {"icon": Icon("lightning-fill"), "number": "02",
                     "title": "SSR first paint", "desc": "The server renders straight to real HTML."},
                    {"icon": Icon("arrow-repeat"), "number": "03",
                     "title": "Live diff", "desc": "An event fires, render() runs again, a minimal patch is computed."},
                    {"icon": Icon("broadcast"), "number": "04",
                     "title": "WebSocket patch", "desc": "The patch is applied directly to the DOM -- no reloads."},
                ],
                eyebrow="THE REQUEST JOURNEY",
                title="Python in. Live interface out.",
                subtitle="Every interaction takes the same round trip, end to end.",
            ),

            feature_trio(
                [
                    {"icon": Icon("lightning-fill"), "number": "01", "title": "Server-rendered first",
                     "desc": "Fast first paint, no client-side hydration framework to ship.",
                     "tag": ["SSR", "REAL HTML"], "color": "cyan"},
                    {"icon": Icon("puzzle-fill"), "number": "02", "title": "Fully modular",
                     "desc": "Swap the router, state store, renderer, or Rust hot path independently.",
                     "tag": ["MODULAR"], "color": "pink"},
                    {"icon": Icon("shield-lock-fill"), "number": "03", "title": "Never breaks",
                     "desc": "The Rust diff engine auto-falls back to pure Python if it isn't built.",
                     "tag": ["SAFE FALLBACK"], "color": "cyan"},
                ],
                eyebrow="WHY NEXORIA",
                title="A small runtime. A very big surface.",
                subtitle="Batteries included for 3D, charts, video, grids, animation, and more.",
            ),

            integrations_row(
                [
                    {"icon": Icon("box-fill"), "name": "ThreeJS", "desc": "Declarative 3D scenes"},
                    {"icon": Icon("stars"), "name": "GSAP", "desc": "Timelines in Python"},
                    {"icon": Icon("bar-chart-fill"), "name": "Chart.js", "desc": "Live dashboards"},
                    {"icon": Icon("play-btn-fill"), "name": "video.js", "desc": "Themeable video"},
                    {"icon": Icon("table"), "name": "AG Grid", "desc": "Sortable data grids"},
                    {"icon": Icon("bootstrap-fill"), "name": "Bootstrap", "desc": "Classic component classes"},
                ],
                eyebrow="ONE FRAMEWORK, MANY SURFACES",
                title="Batteries included. Complexity optional.",
            ),

            install_cta(
                "Your full stack starts with one command.",
                "pip install nexoria",
                eyebrow="SHIP SOMETHING",
                tagline="Cross-platform. Production-grade. Open source.",
                github_href="https://github.com/DivyanshuSinha136/nexoria",
                docs_href="/docs",
            ),

            lib_footer(
                "Nexoria",
                tagline="Built by Divyanshu Sinha \u00b7 Pythonaibrain",
                links=[("GitHub", "https://github.com/DivyanshuSinha136/nexoria"), ("MIT License", "#")],
            ),

            style={"background": "var(--nx-bg)"},
        )


router = Router()
router.add("/", Home, name="home")

app = App(name="Nexoria std.lib Demo", router=router, debug=True)

if __name__ == "__main__":
    app.run(reload=True)
