"""
Inkwell — a modern blog, written entirely in Python with Nexoria.

No React, no JSX, no template language. Every page is a Python function
that returns an element tree, server-rendered by Nexoria and kept live
over its WebSocket patch channel. The UI is assembled from the Nexoria
standard library (`nexoria.std.*`).

Run:
    python app.py        # http://127.0.0.1:8000
"""

from nexoria import App, Component, el, State, Router, Stylesheet

# --- Nexoria standard library -------------------------------------------
from nexoria.std.premium import (
    premium_navbar,
    premium_footer,
    premium_button,
    premium_badge,
    premium_card,
    hero_section,
    feature_grid,
    stat_card,
    testimonial,
    premium_keyframes,
)
from nexoria.std.lib import code_window, lib_keyframes, lib_pill
from nexoria.std.animation import (
    animation_runtime,
    reveal_styles,
    animate_in,
    animated_counter,
    keyframes_style,
)
from nexoria.std.scroll import (
    scroll_runtime,
    scroll_progress_bar,
    scroll_to_top_button,
)
from nexoria.std.webtools import copy_button, accordion
from nexoria.std.alert import inline_alert

from posts import POSTS, POSTS_BY_SLUG, all_tags, posts_for_tag


SITE = "Inkwell"
TAGLINE = "Field notes on building the web in pure Python."

NAV_LINKS = [("Archive", "/"), ("About", "/about"), ("Colophon", "/colophon")]


# ---------------------------------------------------------------- chrome
def page_runtime():
    """Styles + scripts every page needs, rendered once per page."""
    return el(
        "div",
        premium_keyframes(),
        lib_keyframes(),
        keyframes_style(),
        animation_runtime(),
        reveal_styles(),
        scroll_runtime(),
        scroll_progress_bar(color="var(--nx-accent)"),
        scroll_to_top_button(threshold=420),
    )


def site_nav():
    return premium_navbar(
        [el("span", "\u2712\ufe0e  "), el("span", SITE)],
        links=NAV_LINKS,
        cta_text="Subscribe",
        cta_href="/about",
        cta_shimmer=True,
    )


def site_footer():
    return premium_footer(
        SITE,
        tagline=TAGLINE,
        columns=[
            {"title": "Reading", "links": [(p["title"], f"/posts/{p['slug']}") for p in POSTS[:3]]},
            {"title": "Site", "links": NAV_LINKS},
        ],
        socials=[("Nexoria", "https://github.com/DivyanshuSinha136/nexoria")],
    )


def shell(*children):
    return el(
        "div",
        page_runtime(),
        site_nav(),
        el("main", *children),
        site_footer(),
        style={"background": "var(--nx-bg)", "min_height": "100vh"},
    )


def container(*children, width="1060px", pad="0 24px 72px 24px"):
    return el("div", *children, style={"max_width": width, "margin": "0 auto", "padding": pad})


def section_title(text, kicker=None):
    kids = []
    if kicker:
        kids.append(lib_pill(kicker, color="cyan"))
    kids.append(
        el("h2", text, style={
            "font_size": "clamp(1.5rem, 1.1rem + 1.6vw, 2.1rem)",
            "font_weight": "800",
            "margin": "14px 0 26px 0",
            "color": "var(--nx-text)",
        })
    )
    return el("div", *kids, style={"margin_top": "56px"})


# ------------------------------------------------------------- home page
class Home(Component):
    styles = Stylesheet()

    def setup(self):
        self.state = State({"tag": "All"})

    def _grid(self):
        return self.styles.scoped_class(
            "post-grid",
            display="grid",
            grid_template_columns="repeat(auto-fill, minmax(290px, 1fr))",
            gap="22px",
        )

    def _cover(self, post):
        return el(
            "a",
            el("span", post["tag"], style={
                "background": "rgba(0,0,0,0.32)",
                "color": "#fff",
                "padding": "5px 12px",
                "border_radius": "999px",
                "font_size": "0.72rem",
                "font_weight": "700",
                "letter_spacing": "0.05em",
                "text_transform": "uppercase",
            }),
            href=f"/posts/{post['slug']}",
            style={
                "display": "flex",
                "align_items": "flex-end",
                "padding": "16px",
                "height": "132px",
                "border_radius": "var(--nx-radius)",
                "background": post["accent"],
                "text_decoration": "none",
                "margin_bottom": "18px",
            },
        )

    def _card(self, post, delay=0):
        return animate_in(
            premium_card(
                self._cover(post),
                el("div",
                   el("span", post["date"]),
                   el("span", "\u00b7", style={"margin": "0 8px"}),
                   el("span", f"{post['read']} read"),
                   style={"color": "var(--nx-text-muted)", "font_size": "0.8rem"}),
                el("a", post["title"], href=f"/posts/{post['slug']}", style={
                    "display": "block",
                    "margin": "10px 0 10px 0",
                    "font_size": "1.18rem",
                    "font_weight": "750",
                    "line_height": "1.35",
                    "color": "var(--nx-text)",
                    "text_decoration": "none",
                }),
                el("p", post["excerpt"], style={
                    "margin": "0 0 18px 0",
                    "color": "var(--nx-text-muted)",
                    "font_size": "0.94rem",
                    "line_height": "1.65",
                }),
                premium_button("Read the post \u2192", variant="ghost", size="sm",
                               href=f"/posts/{post['slug']}"),
            ),
            effect="fade-up",
            delay=delay,
        )

    def _filters(self):
        current = self.state["tag"]
        chips = []
        for tag in ["All"] + all_tags():
            active = tag == current
            chips.append(
                el("button", tag,
                   on_click=(lambda e, t=tag: self.state.update(tag=t)),
                   style={
                       "padding": "8px 16px",
                       "border_radius": "999px",
                       "cursor": "pointer",
                       "font_size": "0.85rem",
                       "font_weight": "650",
                       "border": "1px solid var(--nx-border)",
                       "background": "var(--nx-primary)" if active else "var(--nx-surface)",
                       "color": "#fff" if active else "var(--nx-text-muted)",
                   })
            )
        return el("div", *chips, style={
            "display": "flex", "flex_wrap": "wrap", "gap": "10px", "margin_bottom": "26px",
        })

    def render(self):
        visible = posts_for_tag(self.state["tag"])
        featured = POSTS[0]

        return shell(
            hero_section(
                "Writing the web in pure Python",
                eyebrow=SITE,
                subtitle=TAGLINE + " Built with Nexoria — components, state and "
                                  "styling all in Python, server-rendered and "
                                  "patched live.",
                cta_text="Start reading",
                cta_href=f"/posts/{featured['slug']}",
                cta_shimmer=True,
                secondary_cta_text="About this blog",
                secondary_cta_href="/about",
                animate=True,
            ),
            container(
                el("div",
                   stat_card("Posts published", str(len(POSTS)), trend="+2 this month"),
                   stat_card("Topics covered", str(len(all_tags()))),
                   premium_card(
                       el("div", el("span", "Words read here "),
                          animated_counter(18400, suffix="+"),
                          style={"color": "var(--nx-text)", "font_weight": "700"}),
                       el("p", "Counting quietly while you scroll.",
                          style={"margin": "8px 0 0 0", "color": "var(--nx-text-muted)",
                                 "font_size": "0.88rem"}),
                   ),
                   style={
                       "display": "grid",
                       "grid_template_columns": "repeat(auto-fit, minmax(230px, 1fr))",
                       "gap": "18px",
                       "margin_top": "-36px",
                   }),
                section_title("Latest writing", kicker="Archive"),
                self._filters(),
                el("div",
                   *[self._card(p, delay=i * 80) for i, p in enumerate(visible)],
                   class_=self._grid()),
                section_title("Why this stack", kicker="Under the hood"),
                feature_grid([
                    {"icon": "\U0001F40D", "title": "Pure Python UI",
                     "desc": "Pages are functions returning element trees. No JSX, "
                             "no template dialect, nothing to compile."},
                    {"icon": "\u26A1", "title": "Live patching",
                     "desc": "State lives on the server; only the changed parts of "
                             "the page travel to the browser."},
                    {"icon": "\U0001F9F1", "title": "Standard library",
                     "desc": "Navbars, cards, heroes, accordions and animations "
                             "come ready-made from nexoria.std."},
                ]),
                section_title("The whole page, in one idea", kicker="Source"),
                code_window(
                    'from nexoria import App, Component, el, Router\n'
                    'from nexoria.std.premium import premium_card\n\n'
                    'class Home(Component):\n'
                    '    def render(self):\n'
                    '        return el("div",\n'
                    '            *[premium_card(el("h2", p["title"]))\n'
                    '              for p in POSTS],\n'
                    '        )\n\n'
                    'router = Router()\n'
                    'router.add("/", Home)\n'
                    'app = App(name="Inkwell", router=router)\n',
                    filename="app.py",
                ),
                animate_in(
                    testimonial(
                        "I wrote a whole blog without opening a single .jsx file. "
                        "The only language in the repository is Python.",
                        "Divyanshu Sinha",
                        role="author, Nexoria",
                    ),
                    effect="zoom-in",
                ),
            ),
        )


# ------------------------------------------------------------- post page
class PostPage(Component):
    styles = Stylesheet()

    def _prose(self):
        return self.styles.scoped_class(
            "prose",
            max_width="68ch",
            margin="0 auto",
            font_size="1.08rem",
            line_height="1.85",
            color="var(--nx-text)",
        )

    def _block(self, block):
        kind, value = block
        if kind == "h":
            return el("h2", value, style={
                "margin": "44px 0 14px 0", "font_size": "1.45rem",
                "font_weight": "750", "color": "var(--nx-text)",
            })
        if kind == "quote":
            return el("blockquote", value, style={
                "margin": "34px 0",
                "padding": "4px 0 4px 22px",
                "border_left": "3px solid var(--nx-accent)",
                "font_size": "1.22rem",
                "font_style": "italic",
                "color": "var(--nx-text)",
            })
        if kind == "list":
            return el("ul",
                      *[el("li", item, style={"margin_bottom": "10px"}) for item in value],
                      style={"margin": "22px 0", "padding_left": "22px",
                             "color": "var(--nx-text-muted)"})
        if kind == "code":
            return el("div", code_window(value, filename="snippet.py", live=False),
                      style={"margin": "30px 0"})
        return el("p", value, style={"margin": "0 0 22px 0", "color": "var(--nx-text-muted)"})

    def render(self):
        slug = self.props.get("slug")
        post = POSTS_BY_SLUG.get(slug)
        if post is None:
            return NotFound().render()

        others = [p for p in POSTS if p["slug"] != slug][:3]

        return shell(
            el("header",
               container(
                   el("div",
                      premium_badge(post["tag"], variant="gold"),
                      el("span", f"{post['date']} \u00b7 {post['read']} read",
                         style={"color": "rgba(255,255,255,0.82)", "font_size": "0.85rem"}),
                      style={"display": "flex", "align_items": "center", "gap": "14px",
                             "margin_bottom": "18px"}),
                   el("h1", post["title"], style={
                       "font_size": "clamp(2rem, 1.4rem + 2.8vw, 3.1rem)",
                       "font_weight": "820", "line_height": "1.15",
                       "margin": "0 0 16px 0", "color": "#fff", "max_width": "22ch",
                   }),
                   el("p", post["excerpt"], style={
                       "margin": "0", "max_width": "60ch", "font_size": "1.08rem",
                       "line_height": "1.7", "color": "rgba(255,255,255,0.88)",
                   }),
                   pad="72px 24px 76px 24px"),
               style={"background": post["accent"]}),
            container(
                el("article",
                   *[animate_in(self._block(b), effect="fade-up") for b in post["body"]],
                   class_=self._prose(),
                   style={"padding_top": "48px"}),
                el("div",
                   copy_button(f"http://127.0.0.1:8000/posts/{post['slug']}",
                               label="Copy link", copied_label="Link copied"),
                   premium_button("Back to archive", variant="outline", size="sm", href="/"),
                   style={"display": "flex", "gap": "12px", "justify_content": "center",
                          "margin": "48px 0 0 0", "flex_wrap": "wrap"}),
                section_title("Keep reading", kicker="Next up"),
                el("div",
                   *[premium_card(
                       el("div", p["tag"], style={"color": "var(--nx-accent)",
                                                  "font_size": "0.75rem",
                                                  "font_weight": "700",
                                                  "text_transform": "uppercase",
                                                  "letter_spacing": "0.06em"}),
                       el("a", p["title"], href=f"/posts/{p['slug']}", style={
                           "display": "block", "margin": "10px 0 6px 0",
                           "font_weight": "700", "color": "var(--nx-text)",
                           "text_decoration": "none", "line_height": "1.4",
                       }),
                       el("p", f"{p['date']} \u00b7 {p['read']} read",
                          style={"margin": "0", "color": "var(--nx-text-muted)",
                                 "font_size": "0.82rem"}),
                   ) for p in others],
                   style={"display": "grid",
                          "grid_template_columns": "repeat(auto-fit, minmax(230px, 1fr))",
                          "gap": "18px"}),
            ),
        )


# ------------------------------------------------------ about / colophon
class About(Component):
    def render(self):
        return shell(
            hero_section(
                "About Inkwell",
                eyebrow="Hello",
                subtitle="A small publication about building web software without "
                         "leaving Python.",
                animate=True,
            ),
            container(
                inline_alert("Every page you are reading was produced by Python "
                             "functions — no React, no JSX, no templates.",
                             variant="info"),
                section_title("Frequently asked", kicker="Details"),
                accordion([
                    {"title": "What runs this site?",
                     "content": "Nexoria: a Python web framework that renders "
                                "component trees on the server and patches the "
                                "browser over a live socket."},
                    {"title": "Where does the design come from?",
                     "content": "The Nexoria standard library — navbars, cards, "
                                "heroes, badges, accordions and animations — plus "
                                "a small amount of component-scoped styling."},
                    {"title": "How do new posts get added?",
                     "content": "A dictionary is appended to posts.py. One dynamic "
                                "route turns every entry into its own page."},
                    {"title": "Is there a JavaScript build step?",
                     "content": "No. The framework ships its own tiny runtime; the "
                                "blog itself contains no application JavaScript."},
                ], allow_multiple=False),
                section_title("Say hello", kicker="Contact"),
                premium_card(
                    el("p", "Replies are slow but genuine. Reach out through the "
                            "Nexoria repository linked in the footer.",
                       style={"margin": "0 0 18px 0", "color": "var(--nx-text-muted)"}),
                    premium_button("Open the repository", variant="primary", size="sm",
                                   href="https://github.com/DivyanshuSinha136/nexoria"),
                ),
            ),
        )


class Colophon(Component):
    def render(self):
        return shell(
            hero_section(
                "Colophon",
                eyebrow="How it is made",
                subtitle="The pieces behind the pages.",
                animate=True,
            ),
            container(
                feature_grid([
                    {"icon": "\U0001F9E9", "title": "nexoria.std.premium",
                     "desc": "Navbar, hero, cards, badges, buttons, footer, "
                             "testimonial and stat tiles."},
                    {"icon": "\U0001F4DC", "title": "nexoria.std.lib",
                     "desc": "The editor-style code windows and the small status "
                             "pills above each section."},
                    {"icon": "\u2728", "title": "nexoria.std.animation",
                     "desc": "Scroll-aware reveals for cards and paragraphs, plus "
                             "the count-up number on the home page."},
                    {"icon": "\U0001F5B1\ufe0f", "title": "nexoria.std.scroll",
                     "desc": "Reading progress bar at the top and the back-to-top "
                             "button."},
                    {"icon": "\U0001F9F0", "title": "nexoria.std.webtools",
                     "desc": "Copy-link button on articles and the FAQ accordion."},
                    {"icon": "\U0001F4E3", "title": "nexoria.std.alert",
                     "desc": "The inline note on the about page."},
                ]),
                section_title("Posting a new article", kicker="Workflow"),
                code_window(
                    'POSTS.append({\n'
                    '    "slug": "my-new-post",\n'
                    '    "title": "Something worth writing down",\n'
                    '    "excerpt": "A sentence for the archive card.",\n'
                    '    "date": "2026-09-22",\n'
                    '    "read": "4 min",\n'
                    '    "tag": "Craft",\n'
                    '    "accent": "linear-gradient(135deg, #6366f1, #22d3ee)",\n'
                    '    "body": [("p", "First paragraph.")],\n'
                    '})\n',
                    filename="posts.py",
                ),
            ),
        )


class NotFound(Component):
    def render(self):
        return shell(
            hero_section(
                "That page went missing",
                eyebrow="404",
                subtitle="The address does not match anything in the archive.",
                cta_text="Back to the archive",
                cta_href="/",
                animate=True,
            ),
        )


# -------------------------------------------------------------- the app
router = Router()
router.add("/", Home, name="home")
router.add("/posts/:slug", PostPage, name="post")
router.add("/about", About, name="about")
router.add("/colophon", Colophon, name="colophon")
router.set_not_found(NotFound)

app = App(
    name=SITE,
    router=router,
    description=TAGLINE,
    debug=True,
)

if __name__ == "__main__":
    import os

    app.run(
        port=8000,
        reload=True,
    )
