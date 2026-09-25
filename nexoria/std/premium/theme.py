"""
nexoria.std.premium.theme
============================
Design tokens for the "premium" component family: a restrained,
SaaS/landing-page look built on deep surfaces, a gold/indigo accent
pairing, generous radius, and soft elevation. Extends
`nexoria.style.theme.Theme` (same `--nx-*` variable convention) with
a few premium-only tokens, so premium components read the base theme
first and fall back to their own tokens only where the base theme has
no opinion (e.g. there's no generic "gold" token in `Theme`).
"""

from __future__ import annotations
from dataclasses import dataclass

from ...style.theme import Theme


@dataclass
class PremiumTheme(Theme):
    name: str = "nexoria-premium"

    # premium-only accents, layered on top of the base Theme tokens
    gold: str = "#d4af37"
    gold_soft: str = "#f1dfa3"
    glass_bg: str = "rgba(20, 20, 31, 0.55)"
    glass_border: str = "rgba(255, 255, 255, 0.10)"
    highlight_ring: str = "rgba(99, 102, 241, 0.45)"

    def to_css_vars(self) -> str:
        base = super().to_css_vars()
        extra = (
            "\n:root {\n"
            f"  --nx-premium-gold: {self.gold};\n"
            f"  --nx-premium-gold-soft: {self.gold_soft};\n"
            f"  --nx-premium-glass-bg: {self.glass_bg};\n"
            f"  --nx-premium-glass-border: {self.glass_border};\n"
            f"  --nx-premium-ring: {self.highlight_ring};\n"
            "}"
        )
        return base + extra


PREMIUM_THEME = PremiumTheme()

# Raw `@keyframes` blocks. Kept as plain CSS strings (not
# `Stylesheet` rules) because `Stylesheet` models flat selector ->
# declaration maps and can't express keyframe sub-blocks -- see
# `nexoria.style.stylesheet.Stylesheet.to_css`. Rendered into the page
# via `premium_keyframes()` below, which wraps this in a real
# `<style>` `Element` (raw-text tag, never HTML-escaped -- see
# `nexoria.render.html._RAW_TEXT_TAGS`).
PREMIUM_KEYFRAMES_CSS = """
@keyframes nx-premium-shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
@keyframes nx-premium-fade-up {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes nx-premium-glow {
  0%, 100% { box-shadow: 0 0 0 rgba(212, 175, 55, 0); }
  50% { box-shadow: 0 0 26px rgba(212, 175, 55, 0.35); }
}
""".strip()


def premium_keyframes():
    """
    A `<style>` `Element` carrying every premium `@keyframes` block.
    Drop it once anywhere in your root layout (e.g. next to
    `nexoria.style.components.theme_toggle_button`) before using
    `premium_card(glow=True)`, `premium_button(shimmer=True)`, or
    `hero_section(..., animate=True)`.
    """
    from ...core.element import el
    return el("style", PREMIUM_KEYFRAMES_CSS)
