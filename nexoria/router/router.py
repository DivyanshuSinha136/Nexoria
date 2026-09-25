"""
nexoria.router.router
========================
A single Router implementation shared by SSR (first paint) and the
client-side hydrated app (subsequent navigation), so route-matching
logic never has to be written twice.

Supports static segments, `:param` dynamic segments, and `*` wildcards.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class Route:
    path: str
    component: type          # a Component subclass
    name: Optional[str] = None
    guards: list[Callable[[dict], bool]] = field(default_factory=list)

    def _pattern(self) -> re.Pattern:
        parts = self.path.strip("/").split("/")
        regex_parts = []
        for part in parts:
            if part.startswith(":"):
                regex_parts.append(f"(?P<{part[1:]}>[^/]+)")
            elif part == "*":
                regex_parts.append("(?P<wildcard>.*)")
            else:
                regex_parts.append(re.escape(part))
        pattern = "^/" + "/".join(regex_parts) + "/?$"
        return re.compile(pattern)


class Router:
    def __init__(self):
        self.routes: list[Route] = []
        self.not_found: Optional[type] = None

    def add(self, path: str, component: type, name: Optional[str] = None,
            guards: Optional[list[Callable]] = None) -> "Router":
        self.routes.append(Route(path=path, component=component,
                                  name=name, guards=guards or []))
        return self

    def set_not_found(self, component: type) -> "Router":
        self.not_found = component
        return self

    def match(self, path: str) -> tuple[Optional[Route], dict]:
        for route in self.routes:
            m = route._pattern().match(path)
            if m:
                params = m.groupdict()
                if all(g(params) for g in route.guards):
                    return route, params
        return None, {}

    def resolve(self, path: str, **extra_props):
        """Return an instantiated Component for the given path, or None."""
        route, params = self.match(path)
        if route is None:
            if self.not_found:
                return self.not_found(**extra_props)
            return None
        return route.component(**params, **extra_props)
