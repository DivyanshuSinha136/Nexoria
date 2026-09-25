"""
nexoria.std.physics2d.burst
==============================
A "confetti burst": a button that, on click, launches a spray of
small `physics2d_element`s from one point -- built entirely on top
of `physics2d_element(trigger="event")`, no extra runtime code.
"""

from __future__ import annotations
import random
from typing import Sequence

from ...core.element import el, Element
from .elements import physics2d_element

_DEFAULT_COLORS = ("#FF6B6B", "#FFD93D", "#4ECDC4", "#6FA8FF", "#B892FF")


def physics2d_burst(
    trigger_label: str = "Celebrate!",
    *,
    count: int = 20,
    spread: float = 180,
    direction: float = -90,
    min_velocity: float = 200,
    max_velocity: float = 500,
    gravity: float = 900,
    friction: float = 0.02,
    colors: Sequence[str] = _DEFAULT_COLORS,
    size: str = "10px",
    shape: str = "circle",
) -> Element:
    """
    `physics2d_burst("Ship it!", count=30, direction=-90, spread=140)`.

    `direction` is the center angle of the burst cone in degrees
    (-90 = straight up, matching `physics2d_element`'s convention);
    `spread` is the cone's total width around it. Each particle gets
    a randomized angle within the cone and a randomized speed
    between `min_velocity` and `max_velocity` (computed once, in
    Python, at render time -- only the small per-particle stagger
    before launch is randomized in JS, so the burst doesn't fire as
    one perfectly synchronized wall of particles).

    Needs `physics2d_runtime()` rendered once per page.
    """
    particles = []
    for _ in range(count):
        particles.append(physics2d_element(
            trigger="event",
            velocity=random.uniform(min_velocity, max_velocity),
            angle=direction + random.uniform(-spread / 2, spread / 2),
            gravity=gravity,
            friction=friction,
            spin=random.uniform(-360, 360),
            remove_on_settle=True,
            class_="nx-physics-particle",
            style={
                "position": "absolute", "top": "0", "left": "0",
                "width": size, "height": size,
                "background": random.choice(colors),
                "border_radius": "50%" if shape == "circle" else "2px",
                "opacity": "0", "pointer_events": "none",
            },
        ))

    spawn_point = el(
        "div", *particles,
        style={"position": "absolute", "left": "50%", "bottom": "0", "width": "0", "height": "0"},
    )

    fire_js = (
        "var root=this.closest('[data-nx-physics2d-burst]');"
        "root.querySelectorAll('.nx-physics-particle').forEach(function(p){"
        "p.style.opacity='1';"
        "setTimeout(function(){p.dispatchEvent(new Event('nx:physics2d:start'));}, Math.random()*80);"
        "});"
    )
    button = el(
        "button", trigger_label,
        type="button", onclick=fire_js,
        style={
            "padding": "12px 24px", "border_radius": "var(--nx-radius-sm)", "border": "1px solid var(--nx-border)",
            "background": "var(--nx-primary)", "color": "#ffffff", "font_weight": "700", "cursor": "pointer",
            "position": "relative", "z_index": "1",
        },
    )

    return el(
        "div", spawn_point, button,
        data_nx_physics2d_burst="true",
        style={"position": "relative", "display": "inline-block", "overflow": "visible"},
    )
