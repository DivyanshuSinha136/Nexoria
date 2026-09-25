"""
nexoria.std.lib.theme
========================
Design tokens for the "lib" component family: the dark,
terminal/dev-tool look used on the Nexoria project's own landing
page -- near-black navy surfaces, a cyan/teal + hot-pink accent
pairing, a faint background grid, monospace-forward type, and
code-editor chrome (traffic-light dots, "LIVE" status pips).
Extends `nexoria.style.theme.Theme` (same `--nx-*` variable
convention) with lib-only tokens.
"""

from __future__ import annotations
from dataclasses import dataclass

from ...style.theme import Theme


@dataclass
class LibTheme(Theme):
    name: str = "nexoria-lib"

    # base surfaces swapped for a near-black terminal feel
    background: str = "#05070d"
    surface: str = "#0a0e17"
    surface_alt: str = "#0f1420"
    border: str = "#1b2333"
    text: str = "#e7ebf5"
    text_muted: str = "#7c8aa8"

    # lib-only accents
    cyan: str = "#22e5e5"
    cyan_soft: str = "#8ff7f0"
    pink: str = "#ff4f81"
    pink_soft: str = "#ff9ab8"
    code_bg: str = "#0a0f1a"
    code_chrome: str = "#141a29"
    grid_line: str = "rgba(94, 234, 212, 0.055)"

    def to_css_vars(self) -> str:
        base = super().to_css_vars()
        extra = (
            "\n:root {\n"
            f"  --nx-lib-cyan: {self.cyan};\n"
            f"  --nx-lib-cyan-soft: {self.cyan_soft};\n"
            f"  --nx-lib-pink: {self.pink};\n"
            f"  --nx-lib-pink-soft: {self.pink_soft};\n"
            f"  --nx-lib-code-bg: {self.code_bg};\n"
            f"  --nx-lib-code-chrome: {self.code_chrome};\n"
            f"  --nx-lib-grid-line: {self.grid_line};\n"
            "}"
        )
        return base + extra


LIB_THEME = LibTheme()

# See `nexoria.std.premium.theme` for why these are raw CSS strings
# rather than `Stylesheet` rules (keyframe sub-blocks aren't
# expressible as flat selector -> declaration maps).
LIB_KEYFRAMES_CSS = """
@keyframes nx-lib-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.35; transform: scale(0.7); }
}
@keyframes nx-lib-gradient-shift {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}
@keyframes nx-lib-rise {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes nx-lib-blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}
""".strip()


def lib_keyframes():
    """
    A `<style>` `Element` carrying every lib `@keyframes` block. Drop
    it once anywhere in your root layout before using
    `live_badge()`'s pulsing dot, `lib_hero(animate=True)`, or a
    gradient-animated `lib_heading(..., animate=True)`.
    """
    from ...core.element import el
    return el("style", LIB_KEYFRAMES_CSS)


def lib_grid_background(*, class_=None):
    """
    A faint, full-bleed graph-paper grid `<div>` (absolutely
    positioned -- give its parent `position: relative`), matching
    the subtle grid behind the Nexoria hero. Layer page content over
    it in a sibling element.
    """
    from ...core.element import el
    return el(
        "div",
        style={
            "position": "absolute",
            "inset": "0",
            "background_image": (
                "linear-gradient(var(--nx-lib-grid-line) 1px, transparent 1px), "
                "linear-gradient(90deg, var(--nx-lib-grid-line) 1px, transparent 1px)"
            ),
            "background_size": "42px 42px",
            "pointer_events": "none",
        },
        class_=class_,
    )
