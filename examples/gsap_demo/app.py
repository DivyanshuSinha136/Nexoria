"""
Nexoria example: declarative GSAP animation. Describe a timeline in
pure Python; the client adapter (gsap-adapter.js) builds a real GSAP
timeline against the actual rendered elements. Autoplays on load, and
a button controls it purely client-side (no server round-trip).

Also enables the ScrollTrigger plugin (App(gsap_plugins=["ScrollTrigger"]))
to show a second card animate in as it scrolls into view -- any of
nexoria.gsap.GSAP_ALL_PLUGINS can be turned on the same way.
"""

from nexoria import App, Component, el, Router, Stylesheet
from nexoria.gsap import Tween, Timeline, Animation


class HeroIntro(Component):
    styles = Stylesheet()

    def render(self):
        anim = Animation(
            Timeline(
                Tween(".hero-title", opacity=0, y=20, from_vars=True, duration=0.6, ease="power2.out"),
                Tween(".hero-sub", opacity=0, y=20, from_vars=True, duration=0.6, position="-=0.3"),
                Tween(".hero-cube", opacity=0, scale=0.5, rotation=-45, from_vars=True,
                      duration=0.8, position="-=0.4", ease="back.out(1.7)"),
            ),
            name="hero-intro",
        )

        cube = self.styles.scoped_class(
            "cube",
            width="64px", height="64px", margin="24px auto 0",
            background="linear-gradient(135deg, var(--nx-primary), var(--nx-accent))",
            border_radius="var(--nx-radius-sm)",
        )

        # ScrollTrigger-powered reveal: once "ScrollTrigger" is passed to
        # App(gsap_plugins=[...]), the adapter registers the plugin before
        # mounting anything, so a Tween's vars can use `scrollTrigger`
        # freely, same as any other GSAP var.
        scroll_anim = Animation(
            Tween(".scroll-card", opacity=0, y=40, from_vars=True, duration=0.7,
                  ease="power2.out",
                  scrollTrigger={"trigger": ".scroll-card", "start": "top 85%"}),
            name="scroll-reveal",
        )

        spacer = self.styles.scoped_class("spacer", height="80vh")

        return el("div",
            el("nav", el("span", "\u2b21 Nexoria", class_="nx-brand"), class_="nx-nav"),
            el("div",
                el("span", "GSAP Demo", class_="nx-badge"),
                el("h1", "Animated with GSAP", class_="hero-title"),
                el("p", "Declared in Python, animated by the real GSAP engine.",
                   class_="hero-sub", style={"color": "var(--nx-text-muted)"}),
                el("div", class_=f"hero-cube {cube}"),
                el("div",
                    el("button", "Replay", class_="nx-btn", onclick=anim.restart_attr()),
                    el("button", "Reverse", class_="nx-btn nx-btn-ghost", onclick=anim.reverse_attr()),
                    class_="nx-row nx-center",
                    style={"margin_top": "20px"},
                ),
                anim.to_element(),
                class_="nx-card",
            ),
            el("div", class_=spacer),
            el("div",
                el("p", "Scroll down to trigger this with ScrollTrigger."),
                scroll_anim.to_element(),
                class_="nx-card scroll-card",
            ),
            class_="nx-container",
        )


router = Router()
router.add("/", HeroIntro)

app = App(
    name="Nexoria GSAP Demo",
    router=router,
    gsap=True,
    gsap_plugins=["ScrollTrigger"],
    debug=True,
)

if __name__ == "__main__":
    app.run(reload=True)
