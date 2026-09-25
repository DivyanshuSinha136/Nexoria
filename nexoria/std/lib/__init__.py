"""
nexoria.std.lib
==================
Dark, dev-tool/terminal-styled web components -- the look of
Nexoria's own landing page: near-black surfaces, a cyan/pink accent
pairing, a faint background grid, code-editor chrome, and mono type
throughout. All themed off `LIB_THEME` (an extension of
`nexoria.style.theme.Theme`).

    from nexoria.std.lib import (
        LIB_THEME, lib_keyframes, lib_grid_background,
        lib_pill, lib_eyebrow, live_badge, lib_tag, lib_tag_row, stat_chip_row,
        lib_button,
        code_window, lib_feature_card, integration_chip,
        lib_hero, pipeline_steps, feature_trio, integrations_row, install_cta,
        lib_navbar, lib_footer,
    )
"""

from __future__ import annotations

from .theme import LibTheme, LIB_THEME, LIB_KEYFRAMES_CSS, lib_keyframes, lib_grid_background
from .badges import lib_pill, lib_eyebrow, live_badge, lib_tag, lib_tag_row, stat_chip_row
from .buttons import lib_button
from .cards import code_window, lib_feature_card, integration_chip
from .sections import lib_hero, pipeline_steps, feature_trio, integrations_row, install_cta
from .navigation import lib_navbar, lib_footer

__all__ = [
    "LibTheme", "LIB_THEME", "LIB_KEYFRAMES_CSS", "lib_keyframes", "lib_grid_background",
    "lib_pill", "lib_eyebrow", "live_badge", "lib_tag", "lib_tag_row", "stat_chip_row",
    "lib_button",
    "code_window", "lib_feature_card", "integration_chip",
    "lib_hero", "pipeline_steps", "feature_trio", "integrations_row", "install_cta",
    "lib_navbar", "lib_footer",
]
