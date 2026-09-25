"""
Nexoria example: three fully client-side `nexoria.std` families in
one page -- `nexoria.std.webtools` (tooltip, copy-to-clipboard,
modal, accordion, tabs), `nexoria.std.alert` (banner, toast, inline
alert), and `nexoria.std.scroll` (progress bar, back-to-top,
in-page anchor links, a scrollable container).

Every interaction here (open a modal, switch a tab, dismiss a
banner, scroll to an anchor) is a literal `onclick=`/inline-script
attribute baked in at render time -- there is no server round-trip
and no Python `State`, which is why this page needs no `Component`
event wiring at all beyond `render()`.

Run:
    pip install nexoria
    cd examples/std_interactive_demo
    python app.py
    # open http://127.0.0.1:8000, then scroll down
"""

from nexoria import App, Component, el, Router, Stylesheet

from nexoria.std.webtools import tooltip, copy_button, modal_dialog, accordion, tabs
from nexoria.std.alert import alert_banner, toast, inline_alert
from nexoria.std.scroll import (
    scroll_runtime, scroll_progress_bar, scroll_to_top_button,
    anchor_link, smooth_scroll_container,
)


def _card(*children, styles: Stylesheet, id_: str = None):
    cls = styles.scoped_class(
        "card", padding="28px", margin_bottom="24px",
        border="1px solid var(--nx-border)", border_radius="var(--nx-radius)",
        background="var(--nx-surface)",
    )
    props = {"class_": cls}
    if id_:
        props["id_"] = id_
    return el("div", *children, **props)


class InteractiveDemo(Component):
    styles = Stylesheet()

    def render(self):
        return el(
            "div",
            # Shared runtime for the scroll-progress bar / back-to-top
            # button -- rendered once per page.
            scroll_runtime(),
            scroll_progress_bar(color="var(--nx-primary)"),
            scroll_to_top_button(threshold=300),

            el("nav",
               el("span", "\u2b21 Nexoria \u00b7 std.webtools / alert / scroll", class_="nx-brand"),
               el("div",
                  anchor_link("Alerts", "alerts-section"),
                  anchor_link("Webtools", "webtools-section"),
                  anchor_link("Scroll", "scroll-section"),
                  style={"display": "flex", "gap": "18px"}),
               class_="nx-nav"),

            el("div",
                el("h1", "Interactive nexoria.std components", style={"margin_bottom": "24px"}),

                # -- Alerts -----------------------------------------------
                el("h2", "Alerts", id_="alerts-section"),
                _card(
                    alert_banner(
                        "Your trial ends in 3 days.",
                        variant="warning", title="Heads up",
                    ),
                    el("div", style={"height": "12px"}),
                    inline_alert("Passwords don't match", variant="danger"),
                    styles=self.styles,
                ),
                # A toast mounted directly in the page tree (per the
                # module's guidance: mount it where it should appear
                # rather than pre-rendering a stack of them). It slides
                # in on load and auto-dismisses after `duration` ms --
                # each instance carries its own id, so several could
                # coexist if you mounted more than one.
                toast("Saved!", variant="success", duration=4000, position="bottom-right"),

                # -- Webtools ----------------------------------------------
                el("h2", "Webtools", id_="webtools-section", style={"margin_top": "16px"}),
                _card(
                    el("div",
                       tooltip(el("span", "Hover me", class_="nx-badge"),
                               "Tooltips need no shared runtime"),
                       el("span", style={"width": "16px", "display": "inline-block"}),
                       copy_button("pip install nexoria", label="Copy install command"),
                       style={"display": "flex", "align_items": "center", "gap": "8px",
                              "margin_bottom": "20px"}),
                    modal_dialog(
                        "View order details", 
                        el("p", "Order #1029 -- 3 items, shipped Tuesday."),
                        el("p", "Total: $84.00", style={"font_weight": "700"}),
                        title="Order #1029",
                    ),
                    el("div", style={"height": "24px"}),
                    accordion([
                        {"title": "What's included?", "content": "Everything in the Pro plan, plus priority support."},
                        {"title": "Can I cancel anytime?", "content": "Yes -- no lock-in, cancel from account settings."},
                        {"title": "Do you offer a free trial?", "content": "14 days, no credit card required."},
                    ], allow_multiple=False),
                    el("div", style={"height": "24px"}),
                    tabs([
                        {"label": "Overview", "content": el("p", "A tabbed panel switcher, no shared runtime.")},
                        {"label": "Specs", "content": el("p", "Server-rendered; tab switching is purely client-side.")},
                        {"label": "Reviews", "content": el("p", "\u2605\u2605\u2605\u2605\u2605 -- \"Just works.\"")},
                    ]),
                    styles=self.styles,
                ),

                # -- Scroll --------------------------------------------------
                el("h2", "Scroll tools", id_="scroll-section", style={"margin_top": "16px"}),
                _card(
                    el("p", "A scrollable container that doesn't scroll the whole page:",
                       style={"color": "var(--nx-text-muted)"}),
                    smooth_scroll_container(
                        *[el("p", f"Line {i + 1} inside the scrollable panel.") for i in range(20)],
                        height="200px",
                    ),
                    el("p", "The progress bar at the very top of the page, and the "
                            "\u2191 back-to-top button in the corner, both track the "
                            "*page's* scroll position instead.",
                       style={"color": "var(--nx-text-muted)", "margin_top": "16px"}),
                    styles=self.styles,
                ),

                # Padding so there's real page height to scroll through,
                # which is what drives the progress bar / back-to-top button.
                el("div", style={"height": "60vh"}),
                el("p", "Scrolled all the way down \u2014 try the \u2191 button.",
                   style={"text_align": "center", "color": "var(--nx-text-muted)"}),

                class_="nx-container",
            ),
        )


router = Router()
router.add("/", InteractiveDemo, name="home")

app = App(name="Nexoria std.webtools/alert/scroll Demo", router=router, debug=True)

if __name__ == "__main__":
    app.run(reload=True)
