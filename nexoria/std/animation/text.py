"""
nexoria.std.animation.text
=============================
Two small text animations, both driven by
`nexoria.std.animation.runtime.animation_runtime()`: a number that
counts up when it scrolls into view, and text that types itself out
character by character.
"""

from __future__ import annotations
from typing import Any, Optional

from ...core.element import el, Element


def animated_counter(
    target: float,
    *,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 0,
    duration: int = 1500,
    class_: Optional[str] = None,
) -> Element:
    """
    `animated_counter(48200, prefix="$", suffix=" users")`. Counts up
    from 0 to `target` (ease-out) the moment it scrolls into view.
    Needs `animation_runtime()` rendered once per page. Renders the
    final value as static text if JS never runs (e.g. no-JS clients),
    so nothing is left blank.
    """
    return el(
        "span", f"{prefix}{target:.{decimals}f}{suffix}",
        class_=class_,
        data_nx_counter=str(target),
        data_nx_counter_prefix=prefix,
        data_nx_counter_suffix=suffix,
        data_nx_counter_decimals=str(decimals),
        data_nx_counter_duration=str(duration),
    )


def typewriter_text(text: str, *, speed: int = 40, tag: str = "span", class_: Optional[str] = None) -> Element:
    """
    `typewriter_text("Write your whole stack in Python.", speed=35)`.
    Types `text` out one character at a time once it scrolls into
    view. Needs `animation_runtime()` rendered once per page. Renders
    the full text as a fallback (overwritten once JS types it out),
    so nothing is left blank without JS.
    """
    return el(
        tag, text,
        class_=class_,
        data_nx_typewriter=text,
        data_nx_typewriter_speed=str(speed),
    )
