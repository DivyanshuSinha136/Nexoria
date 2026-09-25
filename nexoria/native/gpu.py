"""
nexoria.native.gpu
======================
Optional native GPU acceleration tier (CUDA), see
nexoria/native/cpp/gpu/. This is a wholly separate, opt-in tier from
the other three (C++ VDOM, PyO3 Rust, Go edge server): it accelerates
batch/bulk workloads that are embarrassingly parallel across many
independent items (fingerprinting many strings at once, diffing many
numeric table rows at once) -- NOT the single-tree VDOM diff itself,
which stays on nexoria.render.diff's existing CPU tiers, since
branch-heavy pointer-chasing tree traversal doesn't suit GPU hardware.

Every function in this module does real work in the compiled
_nexoria_gpu_cpp CUDA/C++ extension when it's available, and an
equivalent pure-Python fallback otherwise -- never a hard dependency,
never required to run a Nexoria app. Build it with:

    nexoria build-native --with-gpu      # alongside the other tiers
    nexoria build-native --gpu-only      # just this one

which needs the CUDA Toolkit (https://developer.nvidia.com/cuda-downloads)
on the *build* machine; end users of an already-built wheel need
nothing beyond having an NVIDIA GPU + driver to actually exercise the
fast path -- is_available() reports False (and every function above
just quietly uses its Python fallback) on any machine without one,
exactly like the Go server tier falls back to plain uvicorn when its
binary isn't present.
"""

from __future__ import annotations
from typing import Optional

try:
    from .. import _nexoria_gpu_cpp  # native CUDA/C++ extension (see native/cpp/gpu/)
    _engine = _nexoria_gpu_cpp.GPUEngine()
    _HAS_GPU_MODULE = True
except ImportError:  # pragma: no cover - not built for this platform, or no CUDA Toolkit at build time
    _nexoria_gpu_cpp = None
    _engine = None
    _HAS_GPU_MODULE = False


def is_available() -> bool:
    """
    True only if BOTH the GPU tier was built (a CUDA Toolkit was
    present when `build-native --with-gpu` ran) AND at least one
    CUDA-capable GPU is actually visible on this machine right now.
    Every other function in this module checks this itself, so calling
    it first is only needed if you want to know which path will run.
    """
    if not _HAS_GPU_MODULE:
        return False
    return _engine.is_available()


def device_count() -> int:
    """Number of CUDA-capable devices visible to this process (0 if the
    tier isn't built, or no GPU/driver is present)."""
    return _engine.device_count() if _HAS_GPU_MODULE else 0


def device_info(index: int = 0) -> Optional[dict]:
    """Static properties (name, compute capability, SM count, total
    VRAM) of device `index`, or None if no GPU is available at all."""
    if not is_available():
        return None
    return _engine.device_info(index)


def batch_hash(items: list[str]) -> list[int]:
    """
    Fingerprint every string in `items` (one 64-bit hash each, order
    preserved). Useful for cheaply detecting "did anything in this
    batch of independent VDOM subtrees / grid rows change at all"
    across thousands of items in parallel, before falling through to
    nexoria.render.diff's detailed CPU-side diff only on the ones that
    did. Falls back to Python's own hash() per item (still correct,
    just not GPU-parallel) when the GPU tier isn't available.
    """
    if is_available():
        return _engine.batch_hash(items)
    return [hash(s) & 0xFFFFFFFFFFFFFFFF for s in items]


def batch_row_diff(old_rows: list[list[float]], new_rows: list[list[float]]) -> list[list[int]]:
    """
    For two equal-length lists of equal-length numeric rows (a plain
    rectangular table -- the shape nexoria.aggrid row_data already
    is), return, per row, the list of column indices whose value
    differs. Intended for bulk table/grid updates where hundreds or
    thousands of rows change independently in a single state update --
    exactly the embarrassingly-parallel shape GPU hardware suits.
    Falls back to a plain per-cell Python comparison (same result
    shape) when the GPU tier isn't available.
    """
    if is_available():
        return _engine.batch_row_diff(old_rows, new_rows)
    out: list[list[int]] = []
    for old_row, new_row in zip(old_rows, new_rows):
        out.append([i for i, (a, b) in enumerate(zip(old_row, new_row)) if a != b])
    return out
