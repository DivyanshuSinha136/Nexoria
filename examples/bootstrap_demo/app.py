"""
Nexoria example: Bootstrap 5 integration. Bootstrap's own utility/
component classes work straight out of `el(..., class_="...")` once
`App(bootstrap=True)` loads the CSS + JS bundle; a CSS-variable
BootstrapTheme re-skins the palette with no Sass build step, and
tooltips/popovers are auto-initialized by the client adapter (the one
piece of Bootstrap that needs real JS, not just data attributes).
"""

from nexoria import App, Component, el, Router
from nexoria.bootstrap import BootstrapTheme


class Home(Component):
    def render(self):
        return el("div",
            el("nav",
                el("div", "Nexoria", class_="container-fluid navbar-brand"),
                class_="navbar navbar-expand-lg navbar-dark bg-primary mb-4",
            ),
            el("div",
                el("h1", "Styled with Bootstrap", class_="mb-3"),
                el("p", "Declared in Python, rendered with real Bootstrap classes.",
                   class_="text-body-secondary"),
                el("div",
                    el("button", "Primary", class_="btn btn-primary me-2"),
                    el("button", "Outline", class_="btn btn-outline-secondary me-2"),
                    el("button", "Hover me", class_="btn btn-info",
                       data_bs_toggle="tooltip", data_bs_placement="top",
                       title="Auto-initialized by the adapter"),
                    class_="mb-4",
                ),
                el("div", "This alert uses Bootstrap's own component classes.",
                   class_="alert alert-success", role="alert"),
                class_="container",
            ),
        )


router = Router()
router.add("/", Home)

app = App(
    name="Nexoria Bootstrap Demo",
    router=router,
    bootstrap=True,
    bootstrap_theme=BootstrapTheme(primary="#6366f1", border_radius="0.75rem"),
    bootstrap_icons=True,
    debug=True,
)

if __name__ == "__main__":
    app.run(reload=True)
