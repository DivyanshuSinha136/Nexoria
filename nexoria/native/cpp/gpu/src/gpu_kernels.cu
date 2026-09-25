// nexoria native GPU tier -- CUDA kernels and host-side launch code.
// Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
//
// Everything CUDA-specific lives in this one translation unit (nvcc
// compiles .cu, the rest of the module is plain C++ compiled by the
// host compiler -- see CMakeLists.txt). gpu_module.cpp only ever calls
// the plain-C++ functions declared in gpu_kernels.h.

#include "gpu_kernels.h"

#include <cuda_runtime.h>
#include <sstream>
#include <stdexcept>

namespace nexoria_gpu {

namespace {

// Every CUDA runtime call in this file goes through this macro so a
// failure always throws a clear, specific std::runtime_error (which
// pybind11 turns into a Python exception) instead of either crashing
// the process or silently returning garbage -- the same
// "check every call, never assume" discipline the Rust safety core
// and the C++ VDOM tier already apply to their own error paths.
#define NX_CUDA_CHECK(expr)                                                \
    do {                                                                   \
        cudaError_t _nx_err = (expr);                                      \
        if (_nx_err != cudaSuccess) {                                      \
            std::ostringstream _nx_oss;                                   \
            _nx_oss << "nexoria native GPU tier: CUDA error at "           \
                    << __FILE__ << ":" << __LINE__ << ": "                 \
                    << cudaGetErrorString(_nx_err);                        \
            throw std::runtime_error(_nx_oss.str());                       \
        }                                                                  \
    } while (0)

// A GPU kernel launch itself never returns a cudaError_t (the launch
// syntax can't propagate one) -- a bad launch config or an in-kernel
// fault only surfaces on the *next* CUDA call, which would otherwise
// misattribute the error to that unrelated later call. Calling this
// right after every launch, before touching results, keeps failures
// attributed to the kernel that actually caused them.
inline void nx_check_last_launch() {
    NX_CUDA_CHECK(cudaGetLastError());
}

// RAII wrapper so a thrown NX_CUDA_CHECK (or any other exception)
// between an allocation and its intended cudaFree still frees the
// device buffer instead of leaking VRAM -- there's no CUDA-side
// equivalent of a Python/C++ smart pointer built into the runtime
// API, so this is deliberately minimal and single-purpose rather than
// pulling in a template allocator abstraction for two call sites.
class DeviceBuffer {
public:
    explicit DeviceBuffer(size_t bytes) : bytes_(bytes) {
        if (bytes_ > 0) {
            NX_CUDA_CHECK(cudaMalloc(&ptr_, bytes_));
        }
    }
    ~DeviceBuffer() {
        if (ptr_ != nullptr) {
            cudaFree(ptr_); // best-effort in a destructor; nothing meaningful to do with a failure here
        }
    }
    DeviceBuffer(const DeviceBuffer &) = delete;
    DeviceBuffer &operator=(const DeviceBuffer &) = delete;

    void *get() const { return ptr_; }
    template <typename T> T *as() const { return static_cast<T *>(ptr_); }

private:
    void *ptr_ = nullptr;
    size_t bytes_ = 0;
};

} // namespace

bool cuda_runtime_available() {
    int count = 0;
    // A missing driver, a driver/runtime version mismatch, or simply
    // no NVIDIA GPU present all surface as a non-success cudaError_t
    // here rather than a crash -- deliberately swallowed (not
    // NX_CUDA_CHECK'd) because "no GPU on this machine" is the normal,
    // expected outcome on most dev boxes and CI runners, not an error
    // this tier should ever throw for. Callers that want to know
    // *why* there's no GPU can still call device_count()/query_device
    // themselves for a real error message.
    cudaError_t err = cudaGetDeviceCount(&count);
    return err == cudaSuccess && count > 0;
}

int device_count() {
    int count = 0;
    cudaError_t err = cudaGetDeviceCount(&count);
    if (err != cudaSuccess) {
        return 0; // see cuda_runtime_available() -- "no GPU" is not an error here
    }
    return count;
}

DeviceInfo query_device(int index) {
    int count = device_count();
    if (index < 0 || index >= count) {
        std::ostringstream oss;
        oss << "nexoria native GPU tier: device index " << index
            << " out of range (" << count << " device(s) visible)";
        throw std::out_of_range(oss.str());
    }
    cudaDeviceProp props{};
    NX_CUDA_CHECK(cudaGetDeviceProperties(&props, index));
    DeviceInfo info;
    info.name = props.name;
    info.major = props.major;
    info.minor = props.minor;
    info.multiprocessor_count = props.multiProcessorCount;
    info.total_mem_bytes = props.totalGlobalMem;
    return info;
}

// -- batch string fingerprinting ---------------------------------------

namespace {

// One thread per string. `offsets[i]`/`offsets[i+1]` bound string i
// inside the single concatenated `data` buffer (variable-length
// strings can't be indexed as a flat 2D array the way the fixed-width
// row-diff kernel below can, so this uses a CSR-style offsets array
// instead -- the standard GPU pattern for ragged/variable-length
// per-thread inputs).
__global__ void fnv1a64_kernel(const uint8_t *data, const uint32_t *offsets,
                                uint32_t n, uint64_t *out_hashes) {
    uint32_t i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;

    constexpr uint64_t FNV_OFFSET_BASIS = 14695981039346656037ULL;
    constexpr uint64_t FNV_PRIME = 1099511628211ULL;

    uint64_t h = FNV_OFFSET_BASIS;
    uint32_t start = offsets[i];
    uint32_t end = offsets[i + 1];
    for (uint32_t p = start; p < end; ++p) {
        h ^= static_cast<uint64_t>(data[p]);
        h *= FNV_PRIME;
    }
    out_hashes[i] = h;
}

// Threads-per-block for every 1D kernel launch in this file. 256 is a
// conservative, broadly-portable occupancy-friendly choice across the
// whole Pascal-through-Ada/Hopper architecture spread this module is
// compiled for (see CMAKE_CUDA_ARCHITECTURES in CMakeLists.txt) --
// tuning this per-architecture would need per-arch launch-config
// branches for a workload (short-lived batch jobs, not a sustained
// kernel loop) where that tuning effort isn't worth it.
constexpr int kThreadsPerBlock = 256;

} // namespace

std::vector<uint64_t> batch_fnv1a64(const std::vector<std::string> &inputs) {
    uint32_t n = static_cast<uint32_t>(inputs.size());
    if (n == 0) return {};

    // Build the CSR-style offsets + concatenated-bytes layout the
    // kernel expects, on the host, before the single H2D copy below --
    // cheap relative to the copy/launch itself, and keeps the kernel
    // itself branch-free.
    std::vector<uint32_t> offsets(n + 1, 0);
    for (uint32_t i = 0; i < n; ++i) {
        offsets[i + 1] = offsets[i] + static_cast<uint32_t>(inputs[i].size());
    }
    std::vector<uint8_t> data(offsets[n]);
    for (uint32_t i = 0; i < n; ++i) {
        std::copy(inputs[i].begin(), inputs[i].end(), data.begin() + offsets[i]);
    }

    DeviceBuffer d_data(data.empty() ? 1 : data.size()); // cudaMalloc(0) is legal but keep it simple
    DeviceBuffer d_offsets((n + 1) * sizeof(uint32_t));
    DeviceBuffer d_out(n * sizeof(uint64_t));

    if (!data.empty()) {
        NX_CUDA_CHECK(cudaMemcpy(d_data.get(), data.data(), data.size(), cudaMemcpyHostToDevice));
    }
    NX_CUDA_CHECK(cudaMemcpy(d_offsets.get(), offsets.data(), offsets.size() * sizeof(uint32_t), cudaMemcpyHostToDevice));

    int blocks = static_cast<int>((n + kThreadsPerBlock - 1) / kThreadsPerBlock);
    fnv1a64_kernel<<<blocks, kThreadsPerBlock>>>(
        d_data.as<uint8_t>(), d_offsets.as<uint32_t>(), n, d_out.as<uint64_t>());
    nx_check_last_launch();
    NX_CUDA_CHECK(cudaDeviceSynchronize());

    std::vector<uint64_t> out(n);
    NX_CUDA_CHECK(cudaMemcpy(out.data(), d_out.get(), n * sizeof(uint64_t), cudaMemcpyDeviceToHost));
    return out;
}

// -- batch numeric row diff ---------------------------------------------

namespace {

// One thread per cell (row-major, same layout as the flattened input
// arrays) -- `rows * cols` independent equality checks with no
// cross-thread dependency at all, the textbook embarrassingly-parallel
// shape this tier exists for.
__global__ void row_diff_kernel(const double *a, const double *b,
                                 size_t total_cells, uint8_t *out_mask) {
    size_t i = static_cast<size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
    if (i >= total_cells) return;
    out_mask[i] = (a[i] != b[i]) ? 1 : 0;
}

} // namespace

std::vector<uint8_t> batch_row_diff_f64(
    const std::vector<double> &old_flat,
    const std::vector<double> &new_flat,
    size_t rows,
    size_t cols) {
    size_t total = rows * cols;
    if (old_flat.size() != total || new_flat.size() != total) {
        throw std::invalid_argument(
            "nexoria native GPU tier: old_flat/new_flat length must equal rows*cols");
    }
    if (total == 0) return {};

    DeviceBuffer d_old(total * sizeof(double));
    DeviceBuffer d_new(total * sizeof(double));
    DeviceBuffer d_out(total * sizeof(uint8_t));

    NX_CUDA_CHECK(cudaMemcpy(d_old.get(), old_flat.data(), total * sizeof(double), cudaMemcpyHostToDevice));
    NX_CUDA_CHECK(cudaMemcpy(d_new.get(), new_flat.data(), total * sizeof(double), cudaMemcpyHostToDevice));

    int blocks = static_cast<int>((total + kThreadsPerBlock - 1) / kThreadsPerBlock);
    row_diff_kernel<<<blocks, kThreadsPerBlock>>>(
        d_old.as<double>(), d_new.as<double>(), total, d_out.as<uint8_t>());
    nx_check_last_launch();
    NX_CUDA_CHECK(cudaDeviceSynchronize());

    std::vector<uint8_t> out(total);
    NX_CUDA_CHECK(cudaMemcpy(out.data(), d_out.get(), total * sizeof(uint8_t), cudaMemcpyDeviceToHost));
    return out;
}

} // namespace nexoria_gpu
