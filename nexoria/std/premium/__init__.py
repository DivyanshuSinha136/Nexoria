"""
nexoria.std.premium
======================
Polished, business/SaaS-grade web components: buttons, cards, page
sections and site chrome, all themed off `PREMIUM_THEME` (an
extension of `nexoria.style.theme.Theme`).

    from nexoria.std.premium import (
        PREMIUM_THEME, premium_keyframes,
        premium_button, premium_badge, premium_avatar,
        premium_card, glass_panel, stat_card, pricing_card,
        hero_section, feature_grid, testimonial,
        premium_navbar, premium_footer,
    )
"""

from __future__ import annotations

from .theme import PremiumTheme, PREMIUM_THEME, PREMIUM_KEYFRAMES_CSS, premium_keyframes
from .buttons import premium_button
from .badges import premium_badge, premium_avatar
from .cards import premium_card, glass_panel, stat_card, pricing_card
from .sections import hero_section, feature_grid, testimonial
from .navigation import premium_navbar, premium_footer

__all__ = [
    "PremiumTheme", "PREMIUM_THEME", "PREMIUM_KEYFRAMES_CSS", "premium_keyframes",
    "premium_button",
    "premium_badge", "premium_avatar",
    "premium_card", "glass_panel", "stat_card", "pricing_card",
    "hero_section", "feature_grid", "testimonial",
    "premium_navbar", "premium_footer",
]
