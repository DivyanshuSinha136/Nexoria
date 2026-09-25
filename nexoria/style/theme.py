"""
nexoria.style.theme
======================
Design tokens shared across the framework's default look. A `Theme` is
rendered as CSS custom properties (`--nx-*`) at `:root`, so overriding
one value (say, `primary`) re-colors every component that was built
using the framework's base classes (`nx-btn`, `nx-card`, ...) — no
per-component restyling required.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Theme:
    name: str = "nexoria-default"

    # brand
    primary: str = "#6366f1"
    primary_hover: str = "#4f46e5"
    accent: str = "#22d3ee"

    # surfaces
    background: str = "#0b0b12"
    surface: str = "#14141f"
    surface_alt: str = "#1b1b29"
    border: str = "#26263a"

    # text
    text: str = "#f3f3f7"
    text_muted: str = "#9797ad"

    # feedback
    success: str = "#22c55e"
    danger: str = "#ef4444"
    warning: str = "#f59e0b"

    # shape / type
    radius: str = "14px"
    radius_sm: str = "8px"
    font: str = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, "
                 "Roboto, Helvetica, Arial, sans-serif")
    font_mono: str = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
    space: str = "8px"
    shadow: str = "0 10px 30px rgba(0,0,0,0.35)"

    def to_css_vars(self) -> str:
        tokens = {
            "--nx-primary": self.primary,
            "--nx-primary-hover": self.primary_hover,
            "--nx-accent": self.accent,
            "--nx-bg": self.background,
            "--nx-surface": self.surface,
            "--nx-surface-alt": self.surface_alt,
            "--nx-border": self.border,
            "--nx-text": self.text,
            "--nx-text-muted": self.text_muted,
            "--nx-success": self.success,
            "--nx-danger": self.danger,
            "--nx-warning": self.warning,
            "--nx-radius": self.radius,
            "--nx-radius-sm": self.radius_sm,
            "--nx-font": self.font,
            "--nx-font-mono": self.font_mono,
            "--nx-space": self.space,
            "--nx-shadow": self.shadow,
        }
        body = "\n".join(f"  {k}: {v};" for k, v in tokens.items())
        return f":root {{\n{body}\n}}"


DEFAULT_THEME = Theme()

LIGHT_THEME = Theme(
    name="nexoria-light",
    background="#f7f7fb",
    surface="#ffffff",
    surface_alt="#f0f0f6",
    border="#e4e4ee",
    text="#16161f",
    text_muted="#68687d",
    shadow="0 8px 24px rgba(20,20,40,0.08)",
)
