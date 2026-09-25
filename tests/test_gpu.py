"""
Tests for nexoria.native.gpu (the optional CUDA-accelerated batch tier).

Every public function in nexoria.native.gpu is required to work
correctly on a machine with no GPU and no CUDA Toolkit at all -- that's
the pure-Python fallback path, and it's what CI actually exercises
here. The GPU-tier-specific checks are skipped unless the native
extension both built AND reports a real device, so this file never
requires CUDA hardware to run.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from nexoria.native import gpu

requires_gpu_tier = pytest.mark.skipif(
    not gpu.is_available(), reason="native GPU tier not built, or no CUDA-capable device present"
)


def test_is_available_is_a_bool():
    assert isinstance(gpu.is_available(), bool)


def test_device_count_is_zero_without_the_tier():
    if not gpu.is_available():
        assert gpu.device_count() == 0
        assert gpu.device_info() is None


def test_batch_hash_fallback_matches_shape():
    items = ["alpha", "beta", "gamma", ""]
    hashes = gpu.batch_hash(items)
    assert len(hashes) == len(items)
    assert all(isinstance(h, int) for h in hashes)
    # Same input -> same hash, every time, on whichever backend ran.
    assert gpu.batch_hash(items) == hashes
    # Different strings should (overwhelmingly likely) hash differently.
    assert len(set(hashes)) == len(items)


def test_batch_row_diff_fallback_detects_changed_columns():
    old_rows = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    new_rows = [[1.0, 9.0, 3.0], [4.0, 5.0, 6.0]]
    result = gpu.batch_row_diff(old_rows, new_rows)
    assert result == [[1], []]


def test_batch_row_diff_empty_input():
    assert gpu.batch_row_diff([], []) == []


@requires_gpu_tier
def test_gpu_tier_matches_python_fallback_on_real_hardware():
    """
    Sanity check that, on a machine where the CUDA tier is actually
    built and active, its results agree with the pure-Python
    reference implementation -- correctness must not depend on which
    backend happened to run.
    """
    old_rows = [[float(i + j) for j in range(8)] for i in range(50)]
    new_rows = [row[:] for row in old_rows]
    new_rows[10][3] += 1.0  # exactly one changed cell

    gpu_result = gpu._engine.batch_row_diff(old_rows, new_rows)
    python_result = [
        [i for i, (a, b) in enumerate(zip(o, n)) if a != b]
        for o, n in zip(old_rows, new_rows)
    ]
    assert gpu_result == python_result
    assert gpu_result[10] == [3]

    info = gpu.device_info()
    assert info is not None
    assert info["total_mem_bytes"] > 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
