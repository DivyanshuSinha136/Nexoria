"""
nexoria.middleware.base
==========================
Minimal middleware protocol. Unlike ASGI middleware (which wraps the
whole call), Nexoria middleware hooks into the request lifecycle at
the level app authors actually think in: before a route resolves.
"""

from __future__ import annotations
from typing import Optional


class Middleware:
    def before_request(self, request) -> Optional[object]:
        """
        Return a Starlette Response to short-circuit the request
        (e.g. redirect, 401), or None to continue normally.
        """
        return None
