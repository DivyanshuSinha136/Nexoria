"""
nexoria.core.component
========================
Base class for stateful, reusable UI components. Components are pure
Python classes; `render()` returns an `Element` tree. State changes
(via `self.state`) automatically schedule a re-render + diff/patch.
"""

from __future__ import annotations
from typing import Any, ClassVar, Optional
from ..state.store import State
from ..style.stylesheet import Stylesheet
from .element import Element


class Component:
    """
    Subclass and implement `render()`:

        class Counter(Component):
            def setup(self):
                self.state = State({"count": 0})

            def render(self):
                return el("button",
                           f"Clicked {self.state['count']} times",
                           on_click=lambda e: self.state.update(
                               count=self.state["count"] + 1))

    Optionally declare component-scoped CSS via `styles`:

        class Counter(Component):
            styles = Stylesheet()

            def render(self):
                cls = self.styles.scoped_class("counter", padding="24px")
                return el("div", ..., class_=cls)

    `App` automatically merges a routed component's `styles` into the
    page's `<style>` block alongside the app-level theme — no manual
    wiring required.
    """

    name: str = ""
    styles: ClassVar[Optional[Stylesheet]] = None

    def __init__(self, **props: Any):
        self.props = props
        self.state: Optional[State] = None
        self._mounted = False
        self._app = None  # bound by App/Router at mount time
        self.setup()

    # --- lifecycle hooks (override as needed) ---------------------------
    def setup(self) -> None:
        """Called once at construction. Initialize `self.state` here."""
        pass

    def on_mount(self) -> None:
        """Called once the component's DOM has been attached (client-side)."""
        pass

    def on_unmount(self) -> None:
        """Called just before the component is removed from the tree."""
        pass

    def render(self) -> Element:  # pragma: no cover - abstract
        raise NotImplementedError(f"{self.__class__.__name__} must implement render()")

    # --- internal ---------------------------------------------------------
    def _bind(self, app) -> None:
        self._app = app
        if self.state is not None:
            self.state._on_change(lambda: app._schedule_rerender(self))

    def _mount(self) -> None:
        if not self._mounted:
            self._mounted = True
            self.on_mount()

    def _unmount(self) -> None:
        if self._mounted:
            self._mounted = False
            self.on_unmount()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} props={self.props}>"
