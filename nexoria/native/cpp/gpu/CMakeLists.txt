cmake_minimum_required(VERSION 3.18)
project(nexoria_gpu LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# CUDA is enabled as its own CMake *language* (distinct from just
# linking a CUDA runtime library) so that CMake's built-in .cu ->
# nvcc compilation rules kick in for src/gpu_kernels.cu below, the
# same way CMAKE_CXX_STANDARD above drives .cpp compilation. This is
# a hard requirement for this module specifically (unlike the
# optional/soft finds elsewhere in the tree): build_native.py's
# build_gpu() already checks `nvcc` is on PATH *before* ever invoking
# cmake on this directory at all (mirroring build_go_server()'s own
# `go` check), so by the time this file runs, a working CUDA compiler
# is expected to exist -- a hard `enable_language(CUDA)` failure here
# would only happen if PATH changed between that check and this
# configure step, which is a real (if rare) environment error worth
# surfacing clearly rather than papering over.
include(CheckLanguage)
check_language(CUDA)
if(NOT CMAKE_CUDA_COMPILER)
    message(FATAL_ERROR
        "No working CUDA compiler (nvcc) found by CMake, even though "
        "build_gpu() found one on PATH. Do you have multiple CUDA "
        "installs, or a PATH that changed since that check? Install the "
        "CUDA Toolkit (https://developer.nvidia.com/cuda-downloads) and "
        "make sure `nvcc --version` works in this exact shell.")
endif()
enable_language(CUDA)
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)
# Compile for a broad spread of still-current NVIDIA architectures
# (Pascal through Ada/Hopper) rather than only "native", so a wheel
# built on one machine's GPU still runs on another's -- matching the
# cross-machine portability goal every other native tier here already
# has (a compiled extension that only works on the exact box it was
# built on would be a regression, not a feature). PTX is also
# embedded for the newest listed architecture so even newer GPUs than
# these can JIT-compile against it at load time instead of failing
# outright.
if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
    set(CMAKE_CUDA_ARCHITECTURES "61;70;75;80;86;89")
endif()

find_package(pybind11 CONFIG REQUIRED)
find_package(CUDAToolkit REQUIRED)

pybind11_add_module(_nexoria_gpu_cpp
    src/gpu_module.cpp
    src/gpu_kernels.cu
)
target_include_directories(_nexoria_gpu_cpp PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
set_target_properties(_nexoria_gpu_cpp PROPERTIES
    CUDA_SEPARABLE_COMPILATION ON
    CUDA_RESOLVE_DEVICE_SYMBOLS ON
)
target_link_libraries(_nexoria_gpu_cpp PRIVATE CUDA::cudart)
