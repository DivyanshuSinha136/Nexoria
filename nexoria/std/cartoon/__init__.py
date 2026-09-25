"""
nexoria.std.cartoon
======================
Playful, comic-styled web components: chunky outlined buttons and
cards, speech/thought bubbles, sticker badges, emoji avatars, and a
blob progress bar -- all themed off `CARTOON_THEME` (an extension of
`nexoria.style.theme.Theme`).

    from nexoria.std.cartoon import (
        CARTOON_THEME, cartoon_keyframes,
        cartoon_button, cartoon_card, comic_panel,
        speech_bubble, thought_bubble,
        sticker_badge, cartoon_avatar, blob_progress,
    )
"""

from __future__ import annotations

from .theme import CartoonTheme, CARTOON_THEME, CARTOON_KEYFRAMES_CSS, cartoon_keyframes
from .buttons import cartoon_button
from .cards import cartoon_card, comic_panel
from .speech import speech_bubble, thought_bubble
from .badges import sticker_badge, cartoon_avatar
from .progress import blob_progress

__all__ = [
    "CartoonTheme", "CARTOON_THEME", "CARTOON_KEYFRAMES_CSS", "cartoon_keyframes",
    "cartoon_button",
    "cartoon_card", "comic_panel",
    "speech_bubble", "thought_bubble",
    "sticker_badge", "cartoon_avatar",
    "blob_progress",
]
