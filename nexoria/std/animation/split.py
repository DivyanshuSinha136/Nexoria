"""
nexoria.std.animation.split
==============================
Per-character/per-word staggered entrance, in the spirit of GSAP's
SplitText -- but needs no extra runtime code at all. The split
happens server-side, in Python: each character or word becomes its
own `<span data-nx-reveal="...">` with an increasing
`--nx-reveal-delay`, then `animation_runtime()`'s existing reveal
`IntersectionObserver` (the same one `animate_in()` uses) triggers
them all at once -- the stagger is pure CSS `transition-delay`, no
JS choreography required.
"""

from __future__ import annotations
from typing import Optional

from ...core.element import el, Element


def split_text(
    text: str,
    *,
    by: str = "chars",
    effect: str = "fade-up",
    stagger: int = 30,
    duration: int = 500,
    tag: str = "span",
    class_: Optional[str] = None,
) -> Element:
    """
    `split_text("Ship a real website", by="words", effect="fade-up", stagger=80)`.

    `by`: "chars" | "words". `effect`: any `animate_in()` effect
    ("fade", "fade-up", "fade-down", "slide-left", "slide-right",
    "zoom-in"). `stagger` is the ms delay added per character/word.
    Needs `reveal_styles()` and `animation_runtime()` (from
    `nexoria.std.animation`) rendered once per page -- same as
    `animate_in()`, which this is built on top of.
    """
    pieces = list(text) if by == "chars" else text.split(" ")

    spans = []
    for i, piece in enumerate(pieces):
        display = "\u00A0" if piece == "" else piece
        spans.append(el(
            tag, display,
            style={
                "display": "inline-block",
                "--nx-reveal-duration": f"{duration}ms",
                "--nx-reveal-delay": f"{i * stagger}ms",
                "white_space": "pre" if piece == " " else "normal",
            },
            data_nx_reveal=effect,
        ))
        if by == "words" and i < len(pieces) - 1:
            spans.append(el("span", "\u00A0"))

    return el(tag, *spans, class_=class_)
