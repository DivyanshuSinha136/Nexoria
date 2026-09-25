"""
nexoria.native.goserver
==========================
Locates the optional compiled Go native server binary (built by
nexoria/native/build_native.py's build_go_server(), or shipped
pre-built in a wheel) so nexoria.core.app.App.run() can find and spawn
it without duplicating path logic.

This module never builds or spawns anything itself -- it only answers
"is a binary there, and where". Spawning it (and always falling back to
plain uvicorn if it's missing or fails) is App.run()'s job.
"""

from __future__ import annotations
import os
import platform

_PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # nexoria/
_BIN_DIR = os.path.join(_PACKAGE_DIR, "_bin")

BINARY_NAME = "nexoria-server.exe" if platform.system() == "Windows" else "nexoria-server"


def binary_path() -> str | None:
    """Return the path to the compiled native server binary, or None if
    it hasn't been built (see `nexoria build-native --with-go-server`,
    or `--go-server-only`)."""
    path = os.path.join(_BIN_DIR, BINARY_NAME)
    return path if os.path.isfile(path) else None


def is_available() -> bool:
    return binary_path() is not None
