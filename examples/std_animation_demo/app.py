"""
Nexoria example: nexoria.std.animation -- both halves of the package
in one page.

1. Scroll-aware / runtime animations: entrance reveals (`animate_in`),
   a count-up stat (`animated_counter`), a typewriter line
   (`typewriter_text`), a "decrypting" scramble reveal
   (`scramble_text`), a per-word staggered split (`split_text`), an
   animated stroke-draw SVG (`draw_svg`), and a hover path morph
   (`morph_svg`) -- all driven by one small `IntersectionObserver`
   runtime, no CDN.

2. The pure-Python CSS `@keyframes` engine: a couple of the built-in
   animate.css-style presets (`animated`) plus a hand-defined
   `Keyframes` registered on `ANIMATION_ENGINE`.

`nexoria.std.svg.PathBuilder` supplies the two paths used by
`draw_svg`/`morph_svg`.

Run:
    pip install nexoria
    cd examples/std_animation_demo
    python app.py
    # open http://127.0.0.1:8000, then scroll down
"""

from nexoria import App, Component, el, Router, Stylesheet

from nexoria.std.svg import PathBuilder
from nexoria.std.animation import (
    animation_runtime, reveal_styles, animate_in,
    animated_counter, typewriter_text, scramble_text, split_text,
    draw_svg, morph_svg,
    ANIMATION_ENGINE, animated, keyframes_style,
)


def _section(*children, styles: Stylesheet):
    cls = styles.scoped_class(
        "section",
        padding="64px 24px",
        max_width="880px",
        margin="0 auto",
        border_bottom="1px solid var(--nx-border)",
    )
    return el("section", *children, class_=cls)


class AnimationDemo(Component):
    styles = Stylesheet()

    def render(self):
        star_a = (
            PathBuilder().move_to(50, 5)
            .line_to(61, 39).line_to(97, 39).line_to(68, 60)
            .line_to(79, 95).line_to(50, 74).line_to(21, 95)
            .line_to(32, 60).line_to(3, 39).line_to(39, 39)
            .close()
        )
        blob_b = (
            PathBuilder().move_to(50, 10)
            .line_to(90, 30).line_to(90, 70).line_to(50, 90)
            .line_to(10, 70).line_to(10, 30)
            .close()
        )
        stroke_path = (
            PathBuilder().move_to(10, 60)
            .cubic_to(25, 10, 45, 10, 50, 50)
            .cubic_to(55, 90, 75, 90, 90, 40)
        )

        # A custom CSS @keyframes animation, defined once and reused
        # via the AnimationEngine -- no hand-written CSS file.
        ANIMATION_ENGINE.define("nx-demo-wiggle") \
            .at(0, transform="rotate(0deg)") \
            .at(25, transform="rotate(6deg)") \
            .at(75, transform="rotate(-6deg)") \
            .at(100, transform="rotate(0deg)")

        return el(
            "div",
            # Shared runtime + styles for the scroll-aware system, and
            # the <style> tag carrying every registered @keyframes --
            # each rendered exactly once per page.
            animation_runtime(), reveal_styles(), keyframes_style(),

            el("nav",
               el("span", "\u2b21 Nexoria \u00b7 std.animation", class_="nx-brand"),
               class_="nx-nav"),

            _section(
                el("h1", "Scroll down to trigger the reveals", style={"margin_bottom": "8px"}),
                el("p", "Every effect below plays once its element enters the viewport.",
                   style={"color": "var(--nx-text-muted)"}),
                styles=self.styles,
            ),

            _section(
                animate_in(el("h2", "Fade up"), effect="fade-up"),
                animate_in(el("p", "Slide left"), effect="slide-left", delay=100),
                animate_in(el("p", "Zoom in"), effect="zoom-in", delay=200),
                styles=self.styles,
            ),

            _section(
                el("h2", "Count-up stat"),
                el("div", animated_counter(48200, prefix="$", suffix=" raised"),
                   style={"font_size": "3rem", "font_weight": "800", "color": "var(--nx-primary)"}),
                styles=self.styles,
            ),

            _section(
                el("h2", "Typewriter"),
                typewriter_text("Write your whole stack in Python.", speed=35, tag="p",
                                 class_="nx-badge"),
                styles=self.styles,
            ),

            _section(
                el("h2", "Scramble reveal"),
                scramble_text("DECRYPTING...", speed=30, reveal_delay=40, tag="p"),
                styles=self.styles,
            ),

            _section(
                el("h2", "Per-word stagger"),
                split_text("Ship a real website in an afternoon", by="words",
                            effect="fade-up", stagger=80),
                styles=self.styles,
            ),

            _section(
                el("h2", "Animated stroke draw"),
                el("p", "Watch the line draw itself in.", style={"color": "var(--nx-text-muted)"}),
                draw_svg(el(
                    "svg",
                    stroke_path.to_element(fill="none", stroke="var(--nx-primary)",
                                            style={"stroke_width": "3"}),
                    viewBox="0 0 100 100",
                    style={"width": "220px", "height": "180px"},
                ), duration=1800),
                styles=self.styles,
            ),

            _section(
                el("h2", "Path morph (hover)"),
                el("p", "Hover the shape -- star morphs to hexagon.", style={"color": "var(--nx-text-muted)"}),
                morph_svg(star_a.d, blob_b.d, trigger="hover", stroke="var(--nx-accent)"),
                styles=self.styles,
            ),

            _section(
                el("h2", "CSS keyframes engine"),
                el("p", "Built-in presets and a hand-defined animation, both via ANIMATION_ENGINE.",
                   style={"color": "var(--nx-text-muted)"}),
                el("div",
                   animated("Bounce preset", name="bounce", duration="1.2s",
                            iteration_count="infinite", tag="span", class_="nx-badge"),
                   el("span", "\U0001F514", style={
                       **ANIMATION_ENGINE.style("nx-demo-wiggle", duration="1s",
                                                 iteration_count="infinite"),
                       "display": "inline-block", "font_size": "2rem", "margin_left": "24px",
                   }),
                   style={"display": "flex", "align_items": "center", "gap": "12px"}),
                styles=self.styles,
            ),
        )


router = Router()
router.add("/", AnimationDemo, name="home")

app = App(name="Nexoria std.animation Demo", router=router, debug=True)

if __name__ == "__main__":
    app.run(reload=True)
