"""
Nexoria — a production-grade, modular, cross-platform web framework.

Write your entire frontend and backend in Python. Nexoria compiles your
component tree to real DOM operations, hydrates it in the browser via a
tiny JS runtime, and offloads performance-critical work (diffing, asset
pipeline, dev server) to a Rust hot path and a Node.js toolchain — while
you never leave Python.

Ecosystem : Pythonaibrain
Author    : Divyanshu Sinha
License   : MIT
"""

from .__version__ import __version__, __author__, __ecosystem__, __license__
from .core.app import App
from .core.component import Component
from .core.element import el, Element
from .state.store import State, use_state
from .router.router import Router, Route
from .style import Stylesheet, Theme, DEFAULT_THEME, LIGHT_THEME

__all__ = [
    "App",
    "Component",
    "Element",
    "el",
    "State",
    "use_state",
    "Router",
    "Route",
    "Stylesheet",
    "Theme",
    "DEFAULT_THEME",
    "LIGHT_THEME",
    "__version__",
    "__author__",
    "__ecosystem__",
    "__license__",
]
