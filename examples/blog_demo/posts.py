"""
Blog content for the Nexoria blog.

Plain Python data — no templates, no JSX. Each post is a dict; `body` is a
list of blocks rendered by `app.py` into Nexoria elements.

Block kinds:
    ("p", "paragraph text")
    ("h", "section heading")
    ("quote", "pull quote")
    ("list", ["item one", "item two"])
    ("code", "print('hello')")
"""

POSTS = [
    {
        "slug": "hello-nexoria",
        "title": "Building a blog with nothing but Python",
        "excerpt": "No JSX, no template language, no client framework. Just "
                   "functions that return elements, rendered on the server "
                   "and patched live over a socket.",
        "date": "2026-09-14",
        "read": "5 min",
        "tag": "Framework",
        "accent": "linear-gradient(135deg, #6366f1, #22d3ee)",
        "body": [
            ("p", "Most web stacks ask you to learn a second language just to "
                  "describe a page: a template dialect, or JSX. Nexoria "
                  "removes that layer. A page is a Python function that "
                  "returns a tree of elements, and the framework turns that "
                  "tree into HTML."),
            ("h", "Elements are values"),
            ("p", "Because markup is made of ordinary Python values, every "
                  "tool you already use keeps working: list comprehensions "
                  "for repetition, plain functions for reuse, and normal "
                  "conditionals instead of template tags."),
            ("code", "el(\"article\",\n"
                     "    el(\"h2\", post[\"title\"]),\n"
                     "    el(\"p\", post[\"excerpt\"]),\n"
                     "    class_=\"nx-card\",\n"
                     ")"),
            ("h", "State stays on the server"),
            ("p", "When state changes, Nexoria re-renders the tree in Python, "
                  "diffs it, and sends only the differences to the browser. "
                  "The reading experience feels like a single-page app, but "
                  "there is no application JavaScript to write or ship."),
            ("quote", "The page is a function of your data. Change the data, "
                      "and the document follows."),
        ],
    },
    {
        "slug": "styling-without-a-css-file",
        "title": "Styling without hunting through a CSS file",
        "excerpt": "Component-scoped styles are declared next to the markup "
                   "they belong to, and get collision-proof class names "
                   "automatically.",
        "date": "2026-09-08",
        "read": "4 min",
        "tag": "Design",
        "accent": "linear-gradient(135deg, #f97316, #f43f5e)",
        "body": [
            ("p", "Every component can carry its own stylesheet. You declare "
                  "the rules where the markup lives, and the framework hands "
                  "back a content-hashed class name, so two components can "
                  "both own a \u201chero\u201d without ever colliding."),
            ("code", "hero = self.styles.scoped_class(\n"
                     "    \"hero\", display=\"grid\", gap=\"18px\",\n"
                     ")"),
            ("h", "One palette, many pages"),
            ("p", "Shared colours, spacing and type live in the theme, so a "
                  "single change ripples across the whole site. Light and "
                  "dark modes come from the same tokens, which is why the "
                  "toggle in the header needs no code of its own."),
            ("list", [
                "Scoped rules for anything local to one page",
                "Theme tokens for anything shared across pages",
                "No global stylesheet to keep in sync by hand",
            ]),
        ],
    },
    {
        "slug": "routing-and-reading",
        "title": "Routes, reading time, and other small comforts",
        "excerpt": "Dynamic routes turn a list of posts into a set of pages, "
                   "and a missing address lands somewhere friendly instead "
                   "of a stack trace.",
        "date": "2026-08-27",
        "read": "3 min",
        "tag": "Craft",
        "accent": "linear-gradient(135deg, #10b981, #3b82f6)",
        "body": [
            ("p", "A blog is mostly two screens: a list and an article. One "
                  "route pattern with a slug parameter covers every article "
                  "you will ever publish, so adding a post means adding data "
                  "and nothing else."),
            ("code", "router.add(\"/posts/:slug\", PostPage)"),
            ("h", "Fail gently"),
            ("p", "Mistyped links happen. A dedicated not-found page keeps "
                  "the visitor inside the site with a way back to the "
                  "archive, which is worth far more than a precise error."),
            ("quote", "Small comforts are what make a site feel finished."),
        ],
    },
    {
        "slug": "writing-for-the-long-form",
        "title": "Designing a page people finish reading",
        "excerpt": "Measure, rhythm and contrast do more for readability "
                   "than any amount of clever layout.",
        "date": "2026-08-12",
        "read": "6 min",
        "tag": "Writing",
        "accent": "linear-gradient(135deg, #a855f7, #ec4899)",
        "body": [
            ("p", "Long-form reading is a physical act. The eye needs a line "
                  "short enough to return from, space between paragraphs to "
                  "rest in, and headings that promise where the piece is "
                  "going next."),
            ("h", "Three settings that matter most"),
            ("list", [
                "A measure of roughly 65 to 75 characters per line",
                "Generous leading, so paragraphs breathe",
                "Strong contrast for body text, softer for asides",
            ]),
            ("p", "Everything else \u2014 the decorative gradients, the tag "
                  "chips, the hover states \u2014 is seasoning. Get the "
                  "reading surface right first and the rest is free to be "
                  "playful."),
        ],
    },
]

POSTS_BY_SLUG = {p["slug"]: p for p in POSTS}


def all_tags():
    return sorted({p["tag"] for p in POSTS})


def posts_for_tag(tag):
    if not tag or tag == "All":
        return POSTS
    return [p for p in POSTS if p["tag"] == tag]
