"""
nexoria.style.stylesheet
===========================
Declarative, CSS-in-Python styling. Two ways to use it:

1. Plain selector -> declaration rules, rendered verbatim:

    styles = Stylesheet({
        ".card": {"background": "var(--nx-surface)", "padding": "24px"},
        ".card:hover": {"transform": "translateY(-2px)"},
    })

2. Component-scoped classes with content-hashed names, so styles never
   collide between components even if they pick the same short name:

    class Card(Component):
        styles = Stylesheet()

        def render(self):
            cls = self.styles.scoped_class("card", background="var(--nx-surface)",
                                             padding="24px")
            return el("div", ..., class_=cls)

`App(styles=...)` (global) and a routed `Component.styles` (per-component,
merged in automatically per request) are both rendered into a single
`<style>` block alongside the theme's CSS variables — see
`nexoria.core.app.App._http_endpoint`.
"""

from __future__ import annotations
from typing import Optional
import hashlib

try:
    from .. import _nexoria_rs  # Rust hot path, if built
    _HAS_RUST = True
except ImportError:  # pragma: no cover
    _nexoria_rs = None
    _HAS_RUST = False


def _fingerprint(text: str) -> str:
    data = text.encode("utf-8")
    if _HAS_RUST:
        return _nexoria_rs.hash_asset(data)
    return hashlib.blake2b(data, digest_size=4).hexdigest()


def _normalize_props(props: dict) -> dict:
    """Allow Python-friendly underscored keys (`font_size`) alongside
    literal hyphenated ones passed via dict-unpacking
    (`**{"-webkit-background-clip": "text"}`)."""
    out = {}
    for k, v in props.items():
        if k.startswith("-"):  # vendor-prefixed, e.g. -webkit-*
            out[k] = v
        else:
            out[k.replace("_", "-")] = v
    return out


class Stylesheet:
    def __init__(self, rules: Optional[dict[str, dict[str, str]]] = None):
        self.rules: dict[str, dict[str, str]] = {k: dict(v) for k, v in (rules or {}).items()}

    def add(self, selector: str, **props: str) -> "Stylesheet":
        self.rules.setdefault(selector, {}).update(_normalize_props(props))
        return self

    def merge(self, other: Optional["Stylesheet"]) -> "Stylesheet":
        """Return a new Stylesheet combining `self` and `other` (other wins on conflicts)."""
        merged = Stylesheet(self.rules)
        if other is not None:
            for selector, props in other.rules.items():
                merged.rules.setdefault(selector, {}).update(props)
        return merged

    def scoped_class(self, name: str, **props: str) -> str:
        """
        Register a content-hashed, collision-proof class name for the
        given declarations and return it, e.g. `nx-card-a1b2c3d4`.
        Calling this again with identical `name`+`props` returns the
        same class name (idempotent across re-renders).

        Property names may use Python-friendly underscores
        (`font_size="1rem"`) — they're converted to real CSS
        (`font-size: 1rem;`) automatically.
        """
        props = _normalize_props(props)
        body = " ".join(f"{k}:{v};" for k, v in sorted(props.items()))
        class_name = f"nx-{name}-{_fingerprint(body)}"
        self.rules[f".{class_name}"] = props
        return class_name

    def to_css(self) -> str:
        parts = []
        for selector, props in self.rules.items():
            body = " ".join(f"{k}: {v};" for k, v in props.items())
            parts.append(f"{selector} {{ {body} }}")
        return "\n".join(parts)

    def __bool__(self) -> bool:
        return bool(self.rules)
