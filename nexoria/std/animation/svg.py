"""
nexoria.std.animation.svg
============================
Two SVG animations in the spirit of GSAP's commercial DrawSVG and
MorphSVG plugins, built on plain `SVGGeometryElement` APIs -- no
CDN, no license.

`draw_svg()` reveals any `<path>`/`<circle>`/`<rect>`/... as if it
were being drawn, via the standard `stroke-dasharray` trick
(`getTotalLength()` + an animated `stroke-dashoffset`).

`morph_svg()` animates one path's `d` attribute toward another's.
This is a **lightweight coordinate-lerp**, not a true
arbitrary-topology morph: it only interpolates smoothly when both
paths have the same number of numeric coordinates (the same command
structure) -- e.g. two paths both authored as an 8-point star. When
the counts differ, it snaps straight to the target shape instead of
guessing a correspondence between mismatched point sets. For truly
different topologies you'd need a resampling/point-matching
algorithm (which is exactly what GSAP charges for) -- author both
shapes with matching point counts to get a real morph here.
"""

from __future__ import annotations
from typing import Any, Optional

from ...core.element import el, Element


def draw_svg(
    svg: Element,
    *,
    duration: int = 1500,
    delay: int = 0,
    stagger: int = 100,
) -> Element:
    """
    `draw_svg(el("svg", el("path", d="M10 10 L90 90", fill="none", stroke="var(--nx-primary)", style={"stroke_width": "3"}), viewBox="0 0 100 100"))`.
    (`stroke-width` -- like any hyphenated SVG attribute -- needs to
    go through `style=` rather than as a direct keyword, since
    Python identifiers can't contain hyphens; `el()`'s `style=` dict
    is the one place underscores get auto-converted to hyphens.)

    Wraps an existing `<svg>` `Element` (built the normal way with
    `el()`) and tags it to animate every drawable shape inside
    (`path`, `circle`, `ellipse`, `line`, `polyline`, `polygon`,
    `rect`) as if hand-drawn, in document order, `stagger` ms apart,
    once it scrolls into view. Shapes need `fill="none"` and a
    visible `stroke` for the effect to read -- a filled shape will
    still "draw" its outline, but the fill will already be visible
    underneath it. Needs `animation_runtime()` rendered once per
    page.
    """
    svg.props["data-nx-drawsvg"] = "true"
    svg.props["data-nx-drawsvg-duration"] = str(duration)
    svg.props["data-nx-drawsvg-delay"] = str(delay)
    svg.props["data-nx-drawsvg-stagger"] = str(stagger)
    return svg


def morph_svg(
    path_a: str,
    path_b: str,
    *,
    viewBox: str = "0 0 100 100",
    fill: str = "none",
    stroke: str = "var(--nx-primary)",
    stroke_width: str = "3",
    duration: int = 800,
    trigger: str = "hover",
    width: str = "120px",
    height: str = "120px",
) -> Element:
    """
    `morph_svg("M10 80 L50 10 L90 80 Z", "M10 50 L50 90 L90 50 Z", trigger="hover")`.

    Renders `path_a` and morphs it toward `path_b` on `trigger`:
    "hover" | "click" | "scroll" (into view) | "auto" (immediately
    on load). See the module docstring for when this can and can't
    smoothly interpolate. Needs `animation_runtime()` rendered once
    per page.
    """
    path = el(
        "path", d=path_a, fill=fill, stroke=stroke,
        style={"stroke_width": stroke_width},
        data_nx_morph_to=path_b,
        data_nx_morph_duration=str(duration),
        data_nx_morph_trigger=trigger,
    )
    return el("svg", path, viewBox=viewBox, style={"width": width, "height": height, "cursor": "pointer" if trigger in ("hover", "click") else "default"})
