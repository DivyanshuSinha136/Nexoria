"""
nexoria.std.animation.scramble
=================================
Scramble-reveal text: random characters shuffle in place, then lock
in to the real text left-to-right, one at a time -- the classic
"decrypting" text effect. Scroll-triggered, same as the other
`nexoria.std.animation` components.
"""

from __future__ import annotations
from typing import Optional

from ...core.element import el, Element


def scramble_text(
    text: str,
    *,
    chars: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    speed: int = 40,
    reveal_delay: int = 35,
    tag: str = "span",
    class_: Optional[str] = None,
) -> Element:
    """
    `scramble_text("DECRYPTING...", speed=30, reveal_delay=40)`.

    `speed` is the ms between scramble frames; `reveal_delay` is the
    ms between locking in each successive real character (so a
    higher `reveal_delay` relative to `speed` locks characters in
    more slowly). Spaces are never scrambled. Needs
    `animation_runtime()` rendered once per page. Renders the final
    text as a static fallback if JS never runs.
    """
    return el(
        tag, text,
        class_=class_,
        data_nx_scramble=text,
        data_nx_scramble_chars=chars,
        data_nx_scramble_speed=str(speed),
        data_nx_scramble_reveal_delay=str(reveal_delay),
    )
