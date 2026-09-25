"""
nexoria.std.cartoon.theme
============================
Design tokens for the "cartoon" component family: bold flat colors,
thick dark outlines, chunky rounded corners, and a comic-style
hard-drop shadow (offset solid shadow, no blur) instead of premium's
soft elevation. Extends `nexoria.style.theme.Theme`.
"""

from __future__ import annotations
from dataclasses import dataclass

from ...style.theme import Theme


@dataclass
class CartoonTheme(Theme):
    name: str = "nexoria-cartoon"

    # bright, saturated palette + a heavy ink outline
    coral: str = "#FF6B6B"
    sunshine: str = "#FFD93D"
    mint: str = "#4ECDC4"
    sky: str = "#6FA8FF"
    grape: str = "#B892FF"
    ink: str = "#1F1B24"
    paper: str = "#FFFDF6"

    def to_css_vars(self) -> str:
        base = super().to_css_vars()
        extra = (
            "\n:root {\n"
            f"  --nx-cartoon-coral: {self.coral};\n"
            f"  --nx-cartoon-sunshine: {self.sunshine};\n"
            f"  --nx-cartoon-mint: {self.mint};\n"
            f"  --nx-cartoon-sky: {self.sky};\n"
            f"  --nx-cartoon-grape: {self.grape};\n"
            f"  --nx-cartoon-ink: {self.ink};\n"
            f"  --nx-cartoon-paper: {self.paper};\n"
            "}"
        )
        return base + extra


CARTOON_THEME = CartoonTheme()

# See `nexoria.std.premium.theme` for why these are raw CSS strings
# rather than `Stylesheet` rules.
CARTOON_KEYFRAMES_CSS = """
@keyframes nx-cartoon-wiggle {
  0%, 100% { transform: rotate(-2deg); }
  50% { transform: rotate(2deg); }
}
@keyframes nx-cartoon-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
@keyframes nx-cartoon-pop {
  0% { transform: scale(0.85); opacity: 0; }
  60% { transform: scale(1.08); opacity: 1; }
  100% { transform: scale(1); }
}
@keyframes nx-cartoon-float {
  0%, 100% { transform: translateY(0) rotate(-1deg); }
  50% { transform: translateY(-5px) rotate(1deg); }
}
""".strip()


def cartoon_keyframes():
    """
    A `<style>` `Element` carrying every cartoon `@keyframes` block.
    Drop it once anywhere in your root layout before using
    `cartoon_button(wiggle=True)`, `cartoon_card(tilt=True)`,
    `sticker_badge(pop=True)`, or `cartoon_avatar(bounce=True)`.
    """
    from ...core.element import el
    return el("style", CARTOON_KEYFRAMES_CSS)
