from __future__ import annotations
import time
import logging
from .base import Middleware

logger = logging.getLogger("nexoria")


class LoggingMiddleware(Middleware):
    def before_request(self, request):
        logger.info("%s %s", request.method, request.url.path)
        return None
