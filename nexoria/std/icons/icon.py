"""
nexoria.std.icons.icon
=========================
Offline icon layer for `nexoria.std`. Unlike `nexoria.iconify` (which
fetches icon data from Iconify's public API at request time) or
`nexoria.bootstrap`'s `BOOTSTRAP_ICONS_TAG` (a CDN `<link>` to the
Bootstrap Icons *font* build), everything here ships as part of the
package: 2,078 Bootstrap Icons 1.13.1 SVGs, vendored verbatim into
`nexoria/std/icons/data/` (MIT-licensed, see `LICENSE` next to the
SVGs). No network round-trip, no icon-font `<link>` tag, no
`App(bootstrap=True)`/`App(iconify=True)` opt-in required -- same
"pure Python, plain import" contract the rest of `nexoria.std`
follows (see `nexoria/std/__init__.py`).

Each icon is parsed from its on-disk SVG once, converted into a real
`Element` subtree (not injected as raw/unescaped markup -- there is no
such escape hatch in `nexoria.core.element`, by design), and cached, so
repeated use of the same icon across a render is effectively free.

    from nexoria.std.icons import Icon

    Icon("house-door-fill")
    Icon("alarm", size="1.5rem", color="var(--nx-primary)")
    Icon("github", title="GitHub")   # adds an accessible <title>
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

_DATA_DIR = Path(__file__).parent / "data"
_SVG_NS = "{http://www.w3.org/2000/svg}"


class IconNotFoundError(KeyError):
    """Raised when a requested icon name has no matching bundled SVG."""


@lru_cache(maxsize=1)
def _index() -> dict[str, Path]:
    """name -> svg path, built once from the files actually on disk."""
    return {p.stem: p for p in _DATA_DIR.glob("*.svg")}


def list_icons() -> list[str]:
    """All bundled icon names, sorted (e.g. 'house', 'alarm-fill', ...)."""
    return sorted(_index().keys())


def has_icon(name: str) -> bool:
    return name in _index()


def icon_count() -> int:
    return len(_index())


def _strip_ns(tag: str) -> str:
    return tag[len(_SVG_NS):] if tag.startswith(_SVG_NS) else tag


@lru_cache(maxsize=None)
def _parse_svg(name: str) -> ET.Element:
    """Parse a bundled icon's SVG file once; cached for the process lifetime."""
    path = _index().get(name)
    if path is None:
        raise IconNotFoundError(
            f"no bundled icon named {name!r} -- see nexoria.std.icons.list_icons() "
            f"for the {icon_count()} available names"
        )
    return ET.fromstring(path.read_text(encoding="utf-8"))


def _xml_to_element(node: ET.Element):
    """Recursively turn a parsed SVG XML node into a real `nexoria.core.element.Element`."""
    from ...core.element import el
    tag = _strip_ns(node.tag)
    props = dict(node.attrib)
    children = [_xml_to_element(child) for child in node]
    return el(tag, *children, **props)


@dataclass
class Icon:
    """
    A single Bootstrap Icon, rendered as a real inline `<svg>` element
    tree built from the bundled, offline SVG data (no CDN, no icon
    font, no `iconify-icon` web component).

        Icon("house-door-fill")
        Icon("alarm", size="1.5rem", color="var(--nx-danger)")
        Icon("arrow-repeat", class_="spin")     # bring your own @keyframes
        Icon("github", title="GitHub profile")  # accessible, non-decorative use

    `size` sets both width and height (defaults to the SVG's own
    16x16 viewBox-driven size, i.e. "1em"-ish at the surrounding font
    size if left as None -- pass an explicit size for predictable
    layout). `color` overrides `fill` (Bootstrap Icons ship with
    `fill="currentColor"`, so the default already inherits from CSS
    `color` with no override needed -- `color=` is a convenience for
    setting it independently of text color).
    """

    name: str
    size: Optional[str] = None
    color: Optional[str] = None
    class_: Optional[str] = None
    title: Optional[str] = None

    def to_element(self):
        from ...core.element import el

        root = _parse_svg(self.name)
        element = _xml_to_element(root)

        props = dict(element.props)
        if self.size:
            props["width"] = self.size
            props["height"] = self.size
        if self.color:
            props["fill"] = self.color
        if self.class_:
            existing = props.get("class", "")
            props["class"] = f"{existing} {self.class_}".strip()
        if self.title:
            # Non-decorative use: expose an accessible name and drop the
            # `aria-hidden` a bare icon would otherwise need, per the
            # Bootstrap Icons accessibility guidance.
            props["role"] = "img"
            props.pop("aria-hidden", None)
            title_el = el("title", self.title)
            return el(element.tag, title_el, *element.children, **props)

        props.setdefault("aria-hidden", "true")
        return el(element.tag, *element.children, **props)
