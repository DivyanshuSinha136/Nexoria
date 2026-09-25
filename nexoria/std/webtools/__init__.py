"""
nexoria.std.webtools
=======================
General-purpose UI utilities that don't belong to either the
premium or cartoon look: a hover tooltip, a copy-to-clipboard
button, a modal dialog, an accordion, and a tabbed panel switcher.
Each is fully self-contained (no shared runtime, no manual ids).

    from nexoria.std.webtools import (
        tooltip, copy_button, modal_dialog, accordion, tabs,
    )
"""

from __future__ import annotations

from .tooltip import tooltip, copy_button
from .modal import modal_dialog
from .accordion import accordion
from .tabs import tabs

__all__ = ["tooltip", "copy_button", "modal_dialog", "accordion", "tabs"]
