"""
nexoria.core.element
=====================
The virtual-DOM node primitive. Every Nexoria UI is a tree of `Element`
objects built with the `el()` helper. Elements are immutable, hashable
descriptions of DOM structure — diffing them (see `nexoria.rust_ext`)
produces the minimal patch set applied in the browser.
"""

from __future__ import annotations
from typing import Any, Callable, Optional, Union

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

_EVENT_ID_COUNTER = {"n": 0}


def _next_handler_id() -> str:
    _EVENT_ID_COUNTER["n"] += 1
    return f"h{_EVENT_ID_COUNTER['n']}"


class Element:
    """A single virtual DOM node (tag, text, or component placeholder)."""

    __slots__ = (
        "tag", "props", "children", "key", "text",
        "_handlers", "_handler_ids",
    )

    def __init__(
        self,
        tag: Optional[str] = None,
        props: Optional[dict] = None,
        children: Optional[list] = None,
        text: Optional[str] = None,
        key: Optional[Union[str, int]] = None,
    ):
        self.tag = tag
        self.props = props or {}
        self.children = children or []
        self.text = text
        self.key = key
        self._handlers: dict[str, Callable] = {}
        self._handler_ids: dict[str, str] = {}

        # Extract on_* callables into a handler registry so they never
        # leak into the serialized HTML/JSON patch.
        for k in list(self.props.keys()):
            if k.startswith("on_") and callable(self.props[k]):
                event = k[3:]
                handler_id = _next_handler_id()
                self._handlers[event] = self.props.pop(k)
                self._handler_ids[event] = handler_id

    def is_text(self) -> bool:
        return self.text is not None and self.tag is None

    def is_void(self) -> bool:
        return self.tag in VOID_TAGS

    def to_dict(self) -> dict:
        """Serialize to a plain dict (used for the JSON patch protocol)."""
        if self.is_text():
            return {"t": "text", "v": self.text}
        return {
            "t": "el",
            "tag": self.tag,
            "props": dict(self.props),
            "events": dict(self._handler_ids),
            "key": self.key,
            "children": [c.to_dict() for c in self.children],
        }

    def __repr__(self) -> str:  # pragma: no cover
        if self.is_text():
            return f"Text({self.text!r})"
        return f"<{self.tag} props={self.props} children={len(self.children)}>"


def text(value: Any) -> Element:
    return Element(text=str(value))


def el(tag: str, *children: Union[Element, str, int, float], **props: Any) -> Element:
    """
    Build an Element.

        el("div", el("h1", "Hello"), class_="title")

    - `class_` is remapped to `class`, `for_` to `for` (Python keyword clashes).
    - Bare strings/numbers passed as children become text nodes automatically.
    - Keys go through `key=` and are used by the differ to track identity
      across re-renders (important for lists).
    """
    key = props.pop("key", None)
    remapped = {}
    for k, v in props.items():
        if k.endswith("_") and k[:-1] in {"class", "for", "id", "type"}:
            k = k[:-1]
        k = k.replace("_", "-") if k.startswith("data_") or k.startswith("aria_") else k
        if k == "style" and isinstance(v, dict):
            # Convenience: `style={"color": "red", "font_size": "1rem"}` ->
            # "color: red; font-size: 1rem;" so callers don't hand-format
            # inline style strings themselves. Prefer Stylesheet-based
            # classes (nexoria.style) over inline styles for anything
            # reused across renders or elements.
            v = "; ".join(f"{prop.replace('_', '-')}: {val}" for prop, val in v.items())
        remapped[k] = v

    kids = []
    for c in children:
        coerced = _coerce_child(c)
        if isinstance(coerced, (list, tuple)):
            for cc in coerced:
                sub = _coerce_child(cc)
                if sub is not None:
                    kids.append(sub)
        elif coerced is not None:
            kids.append(coerced)

    return Element(tag=tag, props=remapped, children=kids, key=key)


def _coerce_child(c):
    """
    Turn a child argument into an `Element` (or `None`/list to be
    flattened by the caller). Recognizes the `.to_element()` protocol
    every declarative wrapper in the framework follows (`Icon`,
    `QRCode`, `Barcode`, `Chart`, `Grid`, `Map`, `Webcam`, `Animation`,
    `VideoPlayer`, `BabylonScene`, `SplineScene`, `VRMAvatar`, ...) so
    `el("div", Icon("mdi:home"))` works directly -- without this, a
    bare wrapper object (not itself an `Element`) would silently fall
    through to `text(c)` and render as a stringified Python repr
    instead of the actual widget, since it's easy to forget the
    explicit `.to_element()` call every single one of these needs.
    """
    if isinstance(c, Element) or c is None or isinstance(c, (list, tuple)):
        return c
    to_element = getattr(c, "to_element", None)
    if callable(to_element):
        return to_element()
    return text(c)
