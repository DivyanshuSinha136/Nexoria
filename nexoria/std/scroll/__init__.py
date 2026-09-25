"""
nexoria.std.scroll
=====================
Page-scrolling tools: a scroll-triggered "back to top" button, a
top-of-page progress bar, smooth in-page anchor links, and a
scrollable container.

    from nexoria.std.scroll import (
        scroll_runtime, scroll_progress_bar, scroll_to_top_button,
        anchor_link, smooth_scroll_container,
    )

`scroll_progress_bar()` and `scroll_to_top_button()` need
`scroll_runtime()` rendered once per page; `anchor_link()` and
`smooth_scroll_container()` are self-contained.
"""

from __future__ import annotations

from .scrolling import (
    SCROLL_RUNTIME_JS, scroll_runtime,
    scroll_progress_bar, scroll_to_top_button,
    anchor_link, smooth_scroll_container,
)

__all__ = [
    "SCROLL_RUNTIME_JS", "scroll_runtime",
    "scroll_progress_bar", "scroll_to_top_button",
    "anchor_link", "smooth_scroll_container",
]
