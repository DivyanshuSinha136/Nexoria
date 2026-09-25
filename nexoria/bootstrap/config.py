"""
nexoria.bootstrap.config
===========================
Optional Bootstrap 5 integration, as an alternative (or complement) to
Nexoria's own `nexoria.style` (Theme/Stylesheet) system and to
`nexoria.tailwind`, for anyone who wants Bootstrap's components and
utility classes instead.

Bootstrap ships an official, fully self-contained UMD bundle (CSS +
a JS bundle with Popper.js already inlined) built for exactly this
"drop in a script tag, no build step" use case -- same reasoning
`nexoria.videojs` documents for why it isn't part of the shared ESM
import map ThreeJS/GSAP/Chart.js share. Both files are still pulled
from CDN, never a Python dependency.

Most of Bootstrap activates itself from markup alone
(`class_="btn btn-primary"`, `data-bs-toggle="collapse"/"dropdown"/
"modal"/...`) once the bundle is loaded, with zero Python-side helpers
needed. Two components don't self-activate that way -- tooltips and
popovers require a real `new bootstrap.Tooltip(el)` / `new
bootstrap.Popover(el)` call per Bootstrap's own docs -- so the client
adapter (`runtime/bootstrap-adapter.js`, loaded only when
`App(bootstrap=True)`) auto-initializes every
`[data-bs-toggle="tooltip"]` / `[data-bs-toggle="popover"]` element it
finds, and exposes `window.__nexoria__.bootstrap.mountNew()` to re-run
that after any DOM change the client runtime doesn't already know to
watch for (same convention as `nexoria.barcode`/`nexoria.qrcode`/
`nexoria.shiki`).

The adapter also keeps Bootstrap's color mode (`data-bs-theme` on
`<html>`) in sync with Nexoria's own dark/light toggle
(`data-nx-theme`, see `nexoria.style.theme_toggle_button`) via a
MutationObserver, so a Bootstrap-styled page gets one theme toggle
button, not two independent ones that can drift apart.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

BOOTSTRAP_VERSION = "5.3.3"
BOOTSTRAP_CSS_CDN = f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css"
# "bundle" build includes Popper.js inlined -- dropdowns/tooltips/popovers
# (which need it for positioning) work with this one script alone, no
# separate Popper CDN entry to manage.
BOOTSTRAP_JS_CDN = f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/bootstrap.bundle.min.js"

BOOTSTRAP_ICONS_VERSION = "1.11.3"
BOOTSTRAP_ICONS_CSS_CDN = (
    f"https://cdn.jsdelivr.net/npm/bootstrap-icons@{BOOTSTRAP_ICONS_VERSION}"
    f"/font/bootstrap-icons.min.css"
)

BOOTSTRAP_CSS_TAG = f'<link rel="stylesheet" href="{BOOTSTRAP_CSS_CDN}">'
BOOTSTRAP_CORE_SCRIPT_TAG = f'<script src="{BOOTSTRAP_JS_CDN}"></script>'
BOOTSTRAP_ADAPTER_TAG = '<script src="/_nexoria/bootstrap-adapter.js" defer></script>'
BOOTSTRAP_ICONS_TAG = f'<link rel="stylesheet" href="{BOOTSTRAP_ICONS_CSS_CDN}">'
# Kept for anyone importing this directly with no theme/icons.
BOOTSTRAP_RUNTIME_TAG = f"{BOOTSTRAP_CSS_TAG}\n{BOOTSTRAP_CORE_SCRIPT_TAG}\n{BOOTSTRAP_ADAPTER_TAG}"


@dataclass
class BootstrapTheme:
    """
    Bootstrap 5.3+ exposes its entire palette as CSS custom properties
    (`--bs-primary`, `--bs-body-bg`, `--bs-border-radius`, ...) -- override
    any of them without touching Sass or a build step:

        BootstrapTheme(primary="#6366f1", border_radius="0.75rem")

    Renders to a single `<style>:root{...}</style>` tag placed after the
    core Bootstrap stylesheet, so these values win via normal CSS cascade
    order. `variables` passes any other `--bs-*` custom property through
    verbatim by its bare name (no `--bs-` prefix needed):

        BootstrapTheme(variables={"font-sans-serif": "'Inter', sans-serif"})
    """
    primary: Optional[str] = None
    secondary: Optional[str] = None
    success: Optional[str] = None
    danger: Optional[str] = None
    warning: Optional[str] = None
    info: Optional[str] = None
    light: Optional[str] = None
    dark: Optional[str] = None
    body_bg: Optional[str] = None
    body_color: Optional[str] = None
    border_radius: Optional[str] = None
    font_family_base: Optional[str] = None
    variables: dict[str, str] = field(default_factory=dict)

    def to_css_vars(self) -> dict[str, str]:
        named = {
            "primary": self.primary,
            "secondary": self.secondary,
            "success": self.success,
            "danger": self.danger,
            "warning": self.warning,
            "info": self.info,
            "light": self.light,
            "dark": self.dark,
            "body-bg": self.body_bg,
            "body-color": self.body_color,
            "border-radius": self.border_radius,
            "font-sans-serif": self.font_family_base,
        }
        css_vars = {f"--bs-{k}": v for k, v in named.items() if v is not None}
        css_vars.update({f"--bs-{k}": v for k, v in self.variables.items()})
        return css_vars

    def to_style_tag(self) -> str:
        css_vars = self.to_css_vars()
        if not css_vars:
            return ""
        body = " ".join(f"{k}: {v};" for k, v in css_vars.items())
        return f"<style>:root {{ {body} }}</style>"
