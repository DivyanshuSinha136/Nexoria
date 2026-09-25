"""
nexoria.std.physics2d.elements
=================================
A single element driven by `nexoria.std.physics2d.runtime`.
"""

from __future__ import annotations
from typing import Any, Optional

from ...core.element import el, Element


def physics2d_element(
    *children: Any,
    velocity: float = 300,
    angle: float = -60,
    gravity: float = 980,
    friction: float = 0.02,
    spin: float = 0,
    bounce: float = 0,
    floor: str = "none",
    trigger: str = "auto",
    remove_on_settle: bool = False,
    class_: Optional[str] = None,
    style: Optional[dict] = None,
) -> Element:
    """
    `physics2d_element(el("span", "\U0001F680"), velocity=400, angle=-70, spin=180)`.

    Gives its children an initial `velocity` (px/s) launched at
    `angle` degrees (0 = right, 90 = down, so -90 is straight up,
    matching screen-space y-down coordinates), then simulates
    `gravity` (px/s^2, always downward), `friction` (0-1, velocity
    decay per frame), and optional constant `spin` (deg/s) --
    exactly the knobs GSAP's Physics2DPlugin exposes, just applied
    by `nexoria.std.physics2d.runtime`'s own `requestAnimationFrame`
    loop rather than a licensed plugin.

    `floor`: "none" (flies forever/off-screen) | "parent" (bounces
    off the bottom of the nearest positioned ancestor -- this
    element needs to sit inside a `position: relative`/`absolute`
    container for that to work) | "viewport" (bounces off the
    bottom of the browser window, measured once at launch).
    `bounce`: 0 settles the instant it touches the floor; 0 < bounce
    < 1 loses that fraction of energy each bounce.

    `trigger`: "auto" (starts the moment the page loads) | "click" |
    "hover" | "event" (starts only when a `"nx:physics2d:start"` DOM
    event is dispatched on this element -- see `physics2d_burst()`,
    which uses this to fire many particles from one click).

    Moves via `transform: translate() rotate()`, so it never
    disturbs layout -- but that also means, unless you set
    `style={"position": "absolute", ...}` yourself (or `floor`
    isn't "none"), it'll fly right over whatever's laid out after
    it. Needs `physics2d_runtime()` rendered once per page.
    """
    base_style: dict[str, Any] = {"display": "inline-block", "will_change": "transform"}
    if style:
        base_style.update(style)

    return el(
        "div", *children,
        class_=class_,
        style=base_style,
        data_nx_physics2d="true",
        data_nx_physics2d_velocity=str(velocity),
        data_nx_physics2d_angle=str(angle),
        data_nx_physics2d_gravity=str(gravity),
        data_nx_physics2d_friction=str(friction),
        data_nx_physics2d_spin=str(spin),
        data_nx_physics2d_bounce=str(bounce),
        data_nx_physics2d_floor=floor,
        data_nx_physics2d_trigger=trigger,
        data_nx_physics2d_remove_on_settle="true" if remove_on_settle else "false",
    )
