"""
nexoria.cache.assets
=======================
Cache-busting filename fingerprinting for the production build pipeline
(`nexoria build`). Uses the Rust `hash_asset` hot path when available
for large bundles; falls back to Python's hashlib otherwise.
"""

from __future__ import annotations
import hashlib

try:
    from .. import _nexoria_rs
    _HAS_RUST = True
except ImportError:  # pragma: no cover
    _nexoria_rs = None
    _HAS_RUST = False


def fingerprint(data: bytes) -> str:
    if _HAS_RUST:
        return _nexoria_rs.hash_asset(data)
    return hashlib.blake2b(data, digest_size=5).hexdigest()
