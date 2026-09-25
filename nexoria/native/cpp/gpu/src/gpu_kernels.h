// nexoria native GPU tier -- host-side declarations.
// Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
//
// This header is the only thing gpu_module.cpp (the pybind11 binding
// layer) includes -- it never touches CUDA types directly, so the
// pybind11 translation unit stays plain C++ and all `__global__`/
// `<cuda_runtime.h>` usage is confined to gpu_kernels.cu. Every
// function here does its own error handling internally (see .cu) and
// throws std::runtime_error on a CUDA failure, which pybind11
// automatically turns into a Python RuntimeError -- callers on the
// Python side (nexoria.native.gpu) are expected to have already
// checked cuda_runtime_available()/device_count() > 0 before calling
// any of these, exactly like every other optional native tier in this
// tree (checked once, then trusted).
#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace nexoria_gpu {

struct DeviceInfo {
    std::string name;
    int major = 0;
    int minor = 0;
    int multiprocessor_count = 0;
    size_t total_mem_bytes = 0;
};

// True if the CUDA runtime can be initialized and at least one
// CUDA-capable device is visible. Safe to call even on a machine with
// no NVIDIA driver installed at all -- a failed cudaGetDeviceCount()
// is treated as "no GPU", not an error.
bool cuda_runtime_available();

// Number of CUDA-capable devices visible to this process (0 if none /
// no driver). GPUEngine::is_available() in gpu_module.cpp is exactly
// `device_count() > 0`.
int device_count();

// Query static properties of device `index`. Throws std::out_of_range
// if index >= device_count().
DeviceInfo query_device(int index);

// Fingerprints every string in `inputs` in parallel on the GPU with a
// 64-bit FNV-1a hash (one thread per string), returning one hash per
// input in the same order. Used by the Python side
// (nexoria.native.gpu.batch_hash) to cheaply detect "did anything in
// this batch change at all" across many independent VDOM subtrees or
// grid rows before falling through to the detailed CPU-side diff
// (nexoria.render.diff) only on the ones that did -- the embarrassingly
// -parallel shape (thousands of independent, same-op fingerprints)
// suits GPU hardware far better than the branch-heavy single-tree
// diff itself, which stays on the CPU tiers.
std::vector<uint64_t> batch_fnv1a64(const std::vector<std::string> &inputs);

// `old_flat`/`new_flat` are `rows * cols`-length row-major arrays of
// doubles (already flattened by the caller -- see
// GPUEngine::batch_row_diff in gpu_module.cpp). Returns a `rows *
// cols` byte mask (1 = changed, 0 = unchanged), computed with one GPU
// thread per cell. Intended for bulk table/grid updates (see
// nexoria.aggrid) where hundreds or thousands of rows can change
// independently in a single state update.
std::vector<uint8_t> batch_row_diff_f64(
    const std::vector<double> &old_flat,
    const std::vector<double> &new_flat,
    size_t rows,
    size_t cols);

} // namespace nexoria_gpu
