"""
nexoria.std.svg.canvas
=========================
Small convenience wrappers around plain `el("svg", ...)` /
`el("path", ...)` for use alongside `PathBuilder` -- optional, since
`el("svg", ..., view_box="0 0 100 100")` already works with no
special-casing (see `nexoria.std.icons.icon.Icon` for the same raw
`el()` approach), but these save the couple of attributes you'd
otherwise repeat on every canvas/path.
"""

from __future__ import annotations
from typing import Any, Optional, Union

from ...core.element import el, Element
from .path import PathBuilder


def svg_canvas(
    *children: Any,
    view_box: str = "0 0 100 100",
    width: Optional[Union[str, int]] = None,
    height: Optional[Union[str, int]] = None,
    class_: Optional[str] = None,
) -> Element:
    """
    `svg_canvas(PathBuilder().circle(50, 50, 40).to_element(fill="var(--nx-primary)"), view_box="0 0 100 100")`.
    A bare `<svg>` with `xmlns`/`viewBox` filled in so you don't have
    to repeat them at every call site.
    """
    props: dict[str, Any] = {"xmlns": "http://www.w3.org/2000/svg", "viewBox": view_box}
    if width is not None:
        props["width"] = width
    if height is not None:
        props["height"] = height
    if class_:
        props["class_"] = class_
    return el("svg", *children, **props)


def svg_path(path: Union[PathBuilder, str], **props: Any) -> Element:
    """
    `svg_path(PathBuilder().move_to(0, 0).line_to(10, 10), stroke="black", fill="none")`
    or `svg_path("M0,0 L10,10", stroke="black")`. Accepts either a
    `PathBuilder` (its `.build()` is used) or an already-built `d`
    string -- a thin convenience over `el("path", d=..., **props)`
    for the string case; `PathBuilder.to_element()` does the same
    thing when you already have a builder in hand.
    """
    d = path.build() if isinstance(path, PathBuilder) else path
    return el("path", d=d, **props)
