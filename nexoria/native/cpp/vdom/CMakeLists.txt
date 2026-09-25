cmake_minimum_required(VERSION 3.18)
project(nexoria_vdom LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

find_package(pybind11 CONFIG REQUIRED)

# The Rust safety core (nexoria/native/rust_safety/) is built separately
# with `cargo build --release` (see nexoria/cli/main.py's `nexoria
# build-native`, which drives both this and that in the right order).
# We link its staticlib directly rather than dlopen-ing a shared lib, so
# the resulting Python extension has no extra runtime search-path to get
# wrong.
set(NEXORIA_SAFETY_CORE_DIR
    "${CMAKE_CURRENT_SOURCE_DIR}/../../rust_safety/target/release"
    CACHE PATH "Directory containing the built Rust safety-core staticlib")

# Cargo's staticlib output filename depends on which Rust *target*
# you're building, not just the OS: the x86_64-pc-windows-msvc target
# (the default `rustup` install on Windows) produces "X.lib" -- no
# "lib" prefix, ".lib" extension, matching MSVC's own convention.
# x86_64-pc-windows-gnu (MinGW-w64/GNU toolchain -- what you get when
# building with mingw32-make/g++ instead of MSVC's cl.exe) uses the
# same GNU `ar` archive convention as Unix: "libX.a". CMake sets the
# MINGW variable (distinct from WIN32) when the active compiler is a
# MinGW GCC, so use that to pick the right name instead of assuming
# every Windows build is MSVC.
if(WIN32 AND NOT MINGW)
    set(NEXORIA_SAFETY_CORE_LIB "${NEXORIA_SAFETY_CORE_DIR}/nexoria_safety_core.lib")
else()
    set(NEXORIA_SAFETY_CORE_LIB "${NEXORIA_SAFETY_CORE_DIR}/libnexoria_safety_core.a")
endif()

pybind11_add_module(_nexoria_vdom_cpp src/vdom.cpp)
target_include_directories(_nexoria_vdom_cpp PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(_nexoria_vdom_cpp PRIVATE "${NEXORIA_SAFETY_CORE_LIB}")
if(UNIX)
    # pthread/dl are POSIX-only -- the Rust staticlib pulls in libc's
    # threading/dynamic-loading symbols on Linux/macOS; there's no such
    # library by these names on Windows (MSVC/clang-cl), where the
    # equivalent functionality is already part of the standard runtime.
    target_link_libraries(_nexoria_vdom_cpp PRIVATE pthread dl)
elseif(MINGW)
    # rustc normally emits these Windows system-lib references itself
    # when *it* drives the final link (building a .exe/.dll directly).
    # Here CMake/g++ links the raw .a, so std's own Windows dependencies
    # (threading, crypto RNG seeding, env/user info, synchronization
    # primitives) have to be listed explicitly or the link fails with
    # undefined references to things like BCryptGenRandom / GetUserProfileDirectoryW.
    target_link_libraries(_nexoria_vdom_cpp PRIVATE ws2_32 userenv bcrypt ntdll advapi32)
endif()
