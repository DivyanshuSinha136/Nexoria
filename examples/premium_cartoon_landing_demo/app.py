"""
Nexoria example: a landing page built entirely from `nexoria.std`
built-in components -- a premium hero/nav/pricing section up top,
and a playful cartoon section further down, showing both component
families can share one page.

Run:
    pip install nexoria
    python app.py
    # open http://127.0.0.1:8000
"""

from nexoria import App, Component, el, Router

from nexoria.std.premium import (
    premium_keyframes, premium_navbar, hero_section, feature_grid,
    pricing_card, testimonial, premium_footer,
)
from nexoria.std.cartoon import (
    cartoon_keyframes, cartoon_button, cartoon_card, comic_panel,
    speech_bubble, sticker_badge,
)


class Landing(Component):
    def render(self):
        return el(
            "div",
            # keyframes for both families, declared once
            premium_keyframes(),
            cartoon_keyframes(),

            premium_navbar(
                "Nexoria",
                links=[("Features", "#features"), ("Pricing", "#pricing"), ("Fun", "#fun")],
                cta_text="Get Started",
                cta_href="#pricing",
            ),
            hero_section(
                "Ship a real website in pure Python",
                subtitle="Nexoria's std library ships premium AND cartoon components out of the box.",
                eyebrow="Nexoria std",
                cta_text="See pricing",
                cta_href="#pricing",
                secondary_cta_text="Read the docs",
                animate=True,
            ),
            el("section", feature_grid([
                {"title": "Zero build step", "desc": "Server-render Python, hydrate with a tiny runtime."},
                {"title": "Two component families", "desc": "Premium for SaaS pages, cartoon for playful ones."},
                {"title": "No CSS files", "desc": "Every std component ships its own styling inline."},
            ]), id="features", style={"padding": "64px 32px"}),

            el("section", el(
                "div",
                pricing_card("Starter", "$0", features=["1 project", "Community support"]),
                pricing_card("Pro", "$29", features=["Unlimited projects", "Priority support", "Custom domain"], highlighted=True),
                pricing_card("Team", "$99", features=["Everything in Pro", "5 seats", "SSO"]),
                style={"display": "grid", "grid_template_columns": "repeat(auto-fit, minmax(240px, 1fr))", "gap": "24px", "max_width": "1000px", "margin": "0 auto"},
            ), id="pricing", style={"padding": "64px 32px", "background": "var(--nx-surface)"}),

            el("section",
               testimonial("We had a landing page live before lunch.", "Priya N.", role="Founder, Acme"),
               style={"max_width": "560px", "margin": "0 auto", "padding": "64px 32px"}),

            el("section",
               el("h2", "Or make it fun \U0001F389", style={"text_align": "center", "color": "var(--nx-cartoon-ink)"}),
               comic_panel(
                   cartoon_card(
                       speech_bubble("Python on the frontend?!", direction="bottom"),
                       title="Panel 1", color="var(--nx-cartoon-sky)",
                   ),
                   cartoon_card(
                       "Yep -- one framework, one language.",
                       title="Panel 2", sticker=sticker_badge("WOW", shape="star"),
                       color="var(--nx-cartoon-sunshine)",
                   ),
                   caption="- The Nexoria std library",
               ),
               el("div", cartoon_button("Try it now", wiggle=True, color="var(--nx-cartoon-coral)"),
                  style={"text_align": "center", "margin_top": "28px"}),
               id="fun", style={"padding": "64px 32px", "background": "var(--nx-cartoon-paper)"}),

            premium_footer(
                "Nexoria",
                columns=[{"title": "Product", "links": [("Features", "#features"), ("Pricing", "#pricing")]}],
                socials=[("GitHub", "https://github.com/DivyanshuSinha136/nexoria")],
                tagline="Write your entire frontend and backend in Python.",
            ),
        )


router = Router()
router.add("/", Landing)

app = App(name="Nexoria std Demo", router=router, debug=True)

if __name__ == "__main__":
    app.run(reload=True)
