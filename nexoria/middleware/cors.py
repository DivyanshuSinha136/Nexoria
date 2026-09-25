from __future__ import annotations
from typing import Optional
from .base import Middleware


class CORSMiddleware(Middleware):
    def __init__(self, allow_origins: Optional[list[str]] = None):
        self.allow_origins = allow_origins or ["*"]

    def before_request(self, request):
        # Full preflight handling is done at the ASGI layer in production
        # builds; this hook exists for app-level origin allow-listing.
        return None
