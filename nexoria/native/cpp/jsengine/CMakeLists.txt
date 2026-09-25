cmake_minimum_required(VERSION 3.18)
project(nexoria_jsengine LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Vendored QuickJS-ng (see vendor/quickjs/) -- provides the `qjs` static lib
# target we link against. QJS_BUILD_LIBC is off: we don't want quickjs-libc's
# std/os modules (real fs/process exec) available to loaded packages.
set(QJS_BUILD_LIBC OFF CACHE BOOL "" FORCE)
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(QJS_BUILD_CLI OFF CACHE BOOL "" FORCE)
set(QJS_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
add_subdirectory(vendor/quickjs)

find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_nexoria_js src/engine.cpp)
target_include_directories(_nexoria_js PRIVATE vendor/quickjs)
target_link_libraries(_nexoria_js PRIVATE qjs)
