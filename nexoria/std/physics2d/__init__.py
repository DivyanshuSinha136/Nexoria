"""
nexoria.std.physics2d
========================
A dependency-free engine in the spirit of GSAP's commercial
Physics2DPlugin: velocity, angle, gravity, friction, spin, and an
optional floor bounce, all driven by one small
`requestAnimationFrame` loop.

    from nexoria.std.physics2d import (
        physics2d_runtime, physics2d_element, physics2d_burst,
    )

Render `physics2d_runtime()` once anywhere in your root layout, then
use `physics2d_element()` for a single projectile (a launched icon,
a bouncing ball) or `physics2d_burst()` for a one-click confetti
spray built on top of it.
"""

from __future__ import annotations

from .runtime import PHYSICS2D_RUNTIME_JS, physics2d_runtime
from .elements import physics2d_element
from .burst import physics2d_burst

__all__ = [
    "PHYSICS2D_RUNTIME_JS", "physics2d_runtime",
    "physics2d_element",
    "physics2d_burst",
]
