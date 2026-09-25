"""
Nexoria example: nexoria.std.physics2d, nexoria.std.observer,
nexoria.std.svg, and nexoria.std.icons in one page.

- `nexoria.std.physics2d`: a GSAP-Physics2DPlugin-style launched icon
  that bounces off the page, plus a one-click confetti burst -- both
  driven by one `requestAnimationFrame` loop, no CDN, no license.
- `nexoria.std.observer`: a swipe/scroll/drag region reporting raw
  gesture direction, in the spirit of GSAP's commercial Observer.
- `nexoria.std.svg`: `PathBuilder` drawing a circle, a rounded rect,
  and a Catmull-Rom spline through a handful of points -- all pure
  Python, no hand-written `d="..."` strings.
- `nexoria.std.icons`: a small gallery pulled from the 1,800+ bundled
  Bootstrap Icons, rendered as real inline SVG (fully offline).

Run:
    pip install nexoria
    cd examples/std_physics_observer_demo
    python app.py
    # open http://127.0.0.1:8000
"""

from nexoria import App, Component, el, Router, Stylesheet

from nexoria.std.icons import Icon, icon_count
from nexoria.std.svg import PathBuilder, svg_canvas
from nexoria.std.physics2d import physics2d_runtime, physics2d_element, physics2d_burst
from nexoria.std.observer import observer_runtime, observer_region


ICON_NAMES = [
    "rocket-takeoff-fill", "lightning-charge-fill", "stars", "heart-fill",
    "gem", "puzzle-fill", "cpu-fill", "cloud-fill",
    "shield-lock-fill", "lightbulb-fill", "compass-fill", "bell-fill",
]


class PhysicsObserverDemo(Component):
    styles = Stylesheet()

    def render(self):
        card = self.styles.scoped_class(
            "card", padding="28px", margin_bottom="24px",
            border="1px solid var(--nx-border)", border_radius="var(--nx-radius)",
            background="var(--nx-surface)",
        )
        stage = self.styles.scoped_class(
            "stage", position="relative", height="220px", overflow="hidden",
            border="1px dashed var(--nx-border)", border_radius="var(--nx-radius-sm)",
        )
        swipe_box = self.styles.scoped_class(
            "swipe-box", height="140px", display="flex", align_items="center",
            justify_content="center", background="var(--nx-bg)",
            border="1px dashed var(--nx-border)", border_radius="var(--nx-radius-sm)",
            user_select="none", cursor="grab", font_size="0.95rem",
            color="var(--nx-text-muted)",
        )
        icon_tile = self.styles.scoped_class(
            "icon-tile", display="flex", flex_direction="column", align_items="center",
            gap="8px", padding="16px", border="1px solid var(--nx-border)",
            border_radius="var(--nx-radius-sm)", background="var(--nx-bg)",
        )

        # -- SVG shapes built purely with PathBuilder --------------------
        circle = PathBuilder().circle(50, 50, 40)
        rounded = PathBuilder().rounded_rect(10, 10, 80, 80, 16)
        spline = PathBuilder().smooth_through(
            [(5, 60), (25, 15), (50, 70), (75, 20), (95, 55)], closed=False,
        )

        return el(
            "div",
            physics2d_runtime(),
            observer_runtime(),

            el("nav",
               el("span", "\u2b21 Nexoria \u00b7 physics2d / observer / svg / icons", class_="nx-brand"),
               class_="nx-nav"),

            el("div",
                el("h1", "Physics, gestures, paths, and icons", style={"margin_bottom": "24px"}),

                # -- Physics2D ------------------------------------------------
                el("h2", "Physics2D"),
                el("div",
                    el("p", "A rocket launches on load and bounces off the floor of this box:",
                       style={"color": "var(--nx-text-muted)"}),
                    el("div",
                       physics2d_element(
                           el("span", "\U0001F680", style={"font-size": "28px"}),
                           velocity=380, angle=-65, gravity=900, spin=200,
                           floor="parent", bounce=0.55, trigger="auto",
                           style={"position": "absolute", "left": "20px", "bottom": "10px"},
                       ),
                       class_=stage),
                    el("div", style={"height": "16px"}),
                    el("p", "One click, one confetti burst -- built entirely on "
                            "`physics2d_element(trigger=\"event\")`:",
                       style={"color": "var(--nx-text-muted)"}),
                    physics2d_burst("Ship it!", count=30, direction=-90, spread=140),
                    class_=card),

                # -- Observer ---------------------------------------------------
                el("h2", "Observer (swipe / drag / wheel)"),
                el("div",
                    el("p", "Scroll or drag inside the box -- direction reported live below:",
                       style={"color": "var(--nx-text-muted)"}),
                    observer_region(
                        el("div", "Swipe, drag, or scroll me", id_="nx-observer-label", class_=swipe_box),
                        on_up_js="document.getElementById('nx-observer-out').textContent='\u2191 up'",
                        on_down_js="document.getElementById('nx-observer-out').textContent='\u2193 down'",
                        on_left_js="document.getElementById('nx-observer-out').textContent='\u2190 left'",
                        on_right_js="document.getElementById('nx-observer-out').textContent='\u2192 right'",
                        on_click_js="document.getElementById('nx-observer-out').textContent='(clicked)'",
                        tolerance=10,
                    ),
                    el("div", "Last gesture: ", el("strong", "none yet", id_="nx-observer-out"),
                       style={"margin_top": "12px", "color": "var(--nx-text-muted)"}),
                    class_=card),

                # -- SVG PathBuilder ---------------------------------------------
                el("h2", "SVG paths (PathBuilder)"),
                el("div",
                    el("div",
                       svg_canvas(circle.to_element(fill="var(--nx-primary)"),
                                  view_box="0 0 100 100", width=110, height=110),
                       svg_canvas(rounded.to_element(fill="none", stroke="var(--nx-accent)",
                                                      style={"stroke_width": "4"}),
                                  view_box="0 0 100 100", width=110, height=110),
                       svg_canvas(spline.to_element(fill="none", stroke="var(--nx-success)",
                                                     style={"stroke_width": "3"}),
                                  view_box="0 0 100 100", width=110, height=110),
                       style={"display": "flex", "gap": "20px", "flex_wrap": "wrap"}),
                    class_=card),

                # -- Icons --------------------------------------------------------
                el("h2", f"Icons ({icon_count()} bundled, fully offline)"),
                el("div",
                    el("div",
                       *[el("div",
                            Icon(name, size="28px", color="var(--nx-primary)"),
                            el("span", name, style={"font_size": "0.72rem",
                                                     "color": "var(--nx-text-muted)",
                                                     "text_align": "center"}),
                            class_=icon_tile)
                         for name in ICON_NAMES],
                       style={"display": "grid",
                              "grid_template_columns": "repeat(auto-fill, minmax(96px, 1fr))",
                              "gap": "12px"}),
                    class_=card),

                class_="nx-container",
            ),
        )


router = Router()
router.add("/", PhysicsObserverDemo, name="home")

app = App(name="Nexoria std.physics2d/observer/svg/icons Demo", router=router, debug=True)

if __name__ == "__main__":
    app.run(reload=True)
