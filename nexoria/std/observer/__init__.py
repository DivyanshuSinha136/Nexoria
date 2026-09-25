"""
nexoria.std.observer
=======================
A dependency-free engine in the spirit of GSAP's commercial Observer
plugin (https://gsap.com/docs/v3/Plugins/Observer/): normalizes
wheel scrolling and pointer drag (mouse/touch/pen, unified via
Pointer Events) into directional up/down/left/right callbacks, a raw
delta stream, hover, press/release, and click.

    from nexoria.std.observer import observer_runtime, observer_region

Render `observer_runtime()` once anywhere in your root layout, then
wrap whatever should respond to swipes/scroll/drag in
`observer_region(...)` with whichever `on_*_js` callbacks you need.
"""

from __future__ import annotations

from .runtime import OBSERVER_RUNTIME_JS, observer_runtime
from .region import observer_region

__all__ = ["OBSERVER_RUNTIME_JS", "observer_runtime", "observer_region"]
