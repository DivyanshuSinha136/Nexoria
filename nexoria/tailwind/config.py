"""
nexoria.tailwind.config
==========================
Optional Tailwind CSS integration, as an alternative (or complement)
to Nexoria's own `nexoria.style` (Theme/Stylesheet) system, for anyone
who wants Tailwind's utility classes instead.

Two deployment paths, matching Tailwind's own official guidance:

  1. **Play CDN** (`App(tailwind=True)`) -- zero build step, JIT-compiles
     used classes in the browser. This is genuinely how Tailwind
     recommends trying it out or prototyping with no Node.js/bundler
     involved at all, consistent with Nexoria's own "no build step
     required" philosophy. Tailwind's own docs are explicit that this
     is **not recommended for production** (it ships the whole Tailwind
     engine to the browser and recompiles on every load, with no
     purging) -- use it for prototyping, demos, and internal tools; for
     a real production site, use path 2.
  2. **Real compiled CSS** via the Node build pipeline
     (`tools/node-build/build.js`) -- if a `tailwind.config.js` and
     input CSS file are present in the project, `nexoria build` runs
     the actual `tailwindcss` CLI to produce a real, purged production
     stylesheet, no different from any other Tailwind project. This
     needs Node + the `tailwindcss` package at build time only, same as
     the existing esbuild step -- never at runtime.

Both paths can be combined with Nexoria's own `nx-*` base classes
(`nexoria.style`) -- they don't conflict at the DOM level, though
Tailwind's "preflight" reset may visually interact with them; disable
`preflight` in your `TailwindConfig` if you want Nexoria's own reset to
be the only one in effect.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import json

TAILWIND_CDN = "https://cdn.tailwindcss.com"


@dataclass
class TailwindConfig:
    """
    Maps onto the Play CDN's runtime `tailwind.config = {...}` object
    (https://tailwindcss.com/docs/installation/play-cdn#using-a-plugin).

        TailwindConfig(
            dark_mode="class",
            theme_extend={"colors": {"brand": "#6366f1"}},
        )

    `extra` passes any other top-level Tailwind config key through
    verbatim (e.g. `{"corePlugins": {"preflight": False}}` to disable
    Tailwind's own CSS reset if it's fighting with Nexoria's `base.css`).
    """
    theme_extend: dict[str, Any] = field(default_factory=dict)
    dark_mode: Optional[str] = None  # "media" | "class"
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        config: dict[str, Any] = dict(self.extra)
        if self.dark_mode:
            config["darkMode"] = self.dark_mode
        if self.theme_extend:
            theme = dict(config.get("theme", {}))
            theme["extend"] = self.theme_extend
            config["theme"] = theme
        return config


def tailwind_cdn_url(plugins: Optional[list[str]] = None) -> str:
    """
    The Play CDN supports official plugins (forms, typography, container
    queries, aspect-ratio) via a query string:
    https://tailwindcss.com/docs/installation/play-cdn#using-a-plugin
    """
    if not plugins:
        return TAILWIND_CDN
    return f"{TAILWIND_CDN}?plugins={','.join(plugins)}"


def tailwind_runtime_tag(config: Optional[TailwindConfig] = None, plugins: Optional[list[str]] = None) -> str:
    tag = f'<script src="{tailwind_cdn_url(plugins)}"></script>'
    if config is not None:
        config_dict = config.to_dict()
        if config_dict:
            tag += f"\n<script>tailwind.config = {json.dumps(config_dict)};</script>"
    return tag
