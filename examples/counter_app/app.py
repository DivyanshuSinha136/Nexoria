"""
Nexoria example: a stateful counter, server-rendered and hydrated with
live patch updates over WebSocket -- no client-side JS framework code
required from the app author.

Styling: uses the framework's default modern theme + base classes
(nx-card, nx-btn, nx-nav, ...) plus a small component-scoped Stylesheet
for layout that's specific to this page.

Run:
    pip install nexoria
    python app.py
    # open http://127.0.0.1:8000
"""

from nexoria import App, Component, el, State, Router, Stylesheet
from nexoria.style import theme_toggle_button


class Counter(Component):
    # Component-scoped styles: content-hashed class names, so this never
    # collides with another component's ".hero" even in a bigger app.
    styles = Stylesheet()

    def setup(self):
        self.state = State({"count": 0})

    def render(self):
        hero = self.styles.scoped_class(
            "hero",
            display="flex",
            flex_direction="column",
            align_items="center",
            gap="20px",
            text_align="center",
        )
        count_display = self.styles.scoped_class(
            "count-display",
            font_size="clamp(2.5rem, 2rem + 3vw, 4.5rem)",
            font_weight="800",
            color="var(--nx-primary)",  # fallback if background-clip:text is unsupported
            background="linear-gradient(135deg, var(--nx-primary), var(--nx-accent))",
            **{"-webkit-background-clip": "text", "-webkit-text-fill-color": "transparent"},
        )

        return el("div",
            el("nav",
                el("span", "\u2b21 Nexoria", class_="nx-brand"),
                el("div",
                    el("a", "About", href="/about"),
                    theme_toggle_button(),
                    class_="nx-row",
                ),
                class_="nx-nav",
            ),
            el("div",
                el("div",
                    el("span", "Live \u00b7 WebSocket patched", class_="nx-badge"),
                    el("h1", "The Nexoria Counter"),
                    el("p", "State lives in Python. The DOM updates itself.",
                       style={"color": "var(--nx-text-muted)"}),
                    el("div", str(self.state["count"]), class_=count_display),
                    el("div",
                        el("button", "Increment", class_="nx-btn",
                           on_click=lambda e: self.state.update(count=self.state["count"] + 1)),
                        el("button", "Reset", class_="nx-btn nx-btn-ghost",
                           on_click=lambda e: self.state.update(count=0)),
                        class_="nx-row nx-center",
                    ),
                    class_=hero,
                ),
                class_="nx-card",
            ),
            class_="nx-container",
        )


class About(Component):
    def render(self):
        return el("div",
            el("nav",
                el("span", "\u2b21 Nexoria", class_="nx-brand"),
                el("a", "Home", href="/"),
                class_="nx-nav",
            ),
            el("div",
                el("h1", "About this app"),
                el("p", "Built with Nexoria -- a modular, production-grade "
                        "Python web framework. Part of the Pythonaibrain "
                        "ecosystem."),
                el("p", "This page and the counter both use the framework's "
                        "default dark theme and base component classes "
                        "(nx-card, nx-btn, nx-nav) with zero custom CSS "
                        "written by hand."),
                class_="nx-card",
            ),
            class_="nx-container",
        )


router = Router()
router.add("/", Counter, name="home")
router.add("/about", About, name="about")

app = App(name="Nexoria Counter Example", router=router, debug=True)

if __name__ == "__main__":
    app.run(reload=True)
