// Nexoria native GPU tier (C++/CUDA), optional acceleration module.
// Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
//
// A wholly separate, opt-in native tier alongside the C++ VDOM
// (native/cpp/vdom/), the PyO3 Rust extension (rust_ext/), and the Go
// edge server (native/go/server/): none of those need this, and this
// needs none of those. It exists for workloads that are
// embarrassingly parallel across many independent items -- batch
// fingerprinting and bulk numeric row diffing -- which suit GPU
// hardware far better than the single-tree VDOM diff itself (that
// stays on nexoria.render.diff's existing CPU tiers; branch-heavy,
// pointer-chasing tree traversal does not parallelize well on a GPU).
//
// This file is pure C++ -- no CUDA types appear here at all, only the
// plain functions declared in gpu_kernels.h (implemented in
// gpu_kernels.cu, compiled separately by nvcc). If this module isn't
// built (no CUDA Toolkit on the build machine -- see
// nexoria/native/build_native.py's build_gpu()), `import
// nexoria._nexoria_gpu_cpp` simply fails with ImportError and
// nexoria.native.gpu falls back to plain Python, exactly like every
// other optional native tier in this tree.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <stdexcept>

#include "gpu_kernels.h"

namespace py = pybind11;

namespace {

// GPUEngine.is_available()/device_count() are cheap CUDA-runtime
// queries (cudaGetDeviceCount), not expensive to repeat -- constructed
// fresh from Python (nexoria.native.gpu module-level `_engine =
// _nexoria_gpu_cpp.GPUEngine()`) once per process, same pattern as
// VDomEngine in the C++ VDOM tier.
class GPUEngine {
public:
    GPUEngine() = default;

    bool is_available() const { return nexoria_gpu::device_count() > 0; }

    int device_count() const { return nexoria_gpu::device_count(); }

    py::dict device_info(int index) const {
        nexoria_gpu::DeviceInfo info = nexoria_gpu::query_device(index);
        py::dict out;
        out["name"] = info.name;
        out["compute_capability"] = py::make_tuple(info.major, info.minor);
        out["multiprocessor_count"] = info.multiprocessor_count;
        out["total_mem_bytes"] = info.total_mem_bytes;
        return out;
    }

    std::vector<uint64_t> batch_hash(const std::vector<std::string> &items) const {
        return nexoria_gpu::batch_fnv1a64(items);
    }

    // `old_rows`/`new_rows` are equal-length lists of equal-length
    // numeric rows (a plain rectangular table -- exactly the shape
    // nexoria.aggrid row_data already is). Returns, per row, the list
    // of column indices whose value differs -- the same shape the
    // pure-Python fallback in nexoria.native.gpu.batch_row_diff
    // returns, so callers never need to know which one actually ran.
    std::vector<std::vector<int>> batch_row_diff(
        const std::vector<std::vector<double>> &old_rows,
        const std::vector<std::vector<double>> &new_rows) const {
        if (old_rows.size() != new_rows.size()) {
            throw std::invalid_argument(
                "nexoria native GPU tier: old_rows and new_rows must have the same length");
        }
        size_t rows = old_rows.size();
        if (rows == 0) return {};
        size_t cols = old_rows[0].size();
        for (size_t r = 0; r < rows; ++r) {
            if (old_rows[r].size() != cols || new_rows[r].size() != cols) {
                throw std::invalid_argument(
                    "nexoria native GPU tier: every row must have the same number of columns "
                    "(ragged tables aren't supported by the GPU tier -- pad or use the "
                    "pure-Python fallback for those)");
            }
        }

        std::vector<double> old_flat;
        std::vector<double> new_flat;
        old_flat.reserve(rows * cols);
        new_flat.reserve(rows * cols);
        for (size_t r = 0; r < rows; ++r) {
            old_flat.insert(old_flat.end(), old_rows[r].begin(), old_rows[r].end());
            new_flat.insert(new_flat.end(), new_rows[r].begin(), new_rows[r].end());
        }

        std::vector<uint8_t> mask = nexoria_gpu::batch_row_diff_f64(old_flat, new_flat, rows, cols);

        std::vector<std::vector<int>> out(rows);
        for (size_t r = 0; r < rows; ++r) {
            for (size_t c = 0; c < cols; ++c) {
                if (mask[r * cols + c]) {
                    out[r].push_back(static_cast<int>(c));
                }
            }
        }
        return out;
    }
};

} // namespace

PYBIND11_MODULE(_nexoria_gpu_cpp, m) {
    m.doc() =
        "Nexoria native GPU (CUDA) acceleration tier -- optional, see "
        "nexoria/native/cpp/gpu/. Only present at all if built with a "
        "CUDA Toolkit available (`nexoria build-native --with-gpu`); "
        "nexoria.native.gpu is the Python-facing wrapper and always "
        "falls back to plain Python if this import fails or no "
        "CUDA-capable device is present at runtime.";

    py::class_<GPUEngine>(m, "GPUEngine")
        .def(py::init<>())
        .def("is_available", &GPUEngine::is_available,
             "True if a CUDA-capable GPU is visible to this process right now "
             "(the extension being importable only means it was *built* with "
             "CUDA -- the machine running it might still have no GPU).")
        .def("device_count", &GPUEngine::device_count)
        .def("device_info", &GPUEngine::device_info, py::arg("index") = 0)
        .def("batch_hash", &GPUEngine::batch_hash, py::arg("items"))
        .def("batch_row_diff", &GPUEngine::batch_row_diff,
             py::arg("old_rows"), py::arg("new_rows"));
}
