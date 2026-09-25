"""
nexoria.native.build_native
==============================
Builds every optional native acceleration tier from source, in the right
order, and copies the resulting extension modules into the `nexoria`
package directory:

  1. nexoria/native/rust_safety/   (cargo)      -> libnexoria_safety_core.a
  2. nexoria/native/cpp/vdom/      (cmake+ninja) -> _nexoria_vdom_cpp*.so
     (links against the Rust staticlib from step 1)
  3. nexoria/native/cpp/jsengine/  (cmake+ninja) -> _nexoria_js*.so
     (vendors QuickJS-ng under jsengine/vendor/quickjs/)

Plus one wholly separate, opt-in tier:

  4. nexoria/native/go/server/     (go build)    -> nexoria/_bin/nexoria-server[.exe]
     A native edge server (static/runtime asset serving + reverse proxy
     to the same Python ASGI backend) that nexoria.core.app.App.run()
     uses automatically when present. Pass --with-go-server to build it
     alongside steps 1-3, or --go-server-only to build just this (no
     cmake/cargo/rustc required at all in that case).

  5. nexoria/native/cpp/gpu/       (cmake+ninja, needs nvcc) -> _nexoria_gpu_cpp*.so
     Optional CUDA-accelerated tier for embarrassingly-parallel batch
     workloads (fingerprinting many strings at once, diffing many
     numeric table rows at once -- see nexoria.native.gpu) -- NOT the
     single-tree VDOM diff itself, which stays on the CPU tiers above.
     Pass --with-gpu to build it alongside steps 1-3, or --gpu-only to
     build just this (needs the CUDA Toolkit, but nothing else here).

None of this is required to use Nexoria — every tier has a working
fallback (see nexoria/render/diff.py's three-tier chain, the JS engine
raising a clear error if it wasn't built, App.run() falling back to
plain uvicorn if the Go server binary isn't present, and
nexoria.native.gpu falling back to plain Python if the GPU tier isn't
built or no CUDA-capable device is present at runtime). This script
exists purely to make the *native* tiers reproducible from a clean
checkout, since they involve real compiled extensions rather than pure
Python.

Requires: a C++17 compiler, CMake >= 3.18, Ninja, Rust/Cargo, and Python
headers (all standard on any dev machine with a C/C++ toolchain
installed; none of this is required on end users' machines once you've
built and shipped the compiled wheel). The Go server tier additionally
needs a Go toolchain (https://go.dev/dl/), and the GPU tier needs the
CUDA Toolkit (https://developer.nvidia.com/cuda-downloads) -- only if
you build it; it has its own opt-in flags and no dependency on
anything else here.

CMake-free VDOM build: pass --vdom-with-mingw to build the C++ VDOM tier
(step 2) with `mingw32-make` against cpp/vdom/Makefile.mingw instead of
CMake+Ninja/MSVC -- useful on a bare MinGW-w64 install with no CMake.
Combine with --vdom-only to skip the JS engine tier too (it has no
mingw32-make Makefile yet, so it still needs CMake either way):

    python build_native.py --vdom-with-mingw --vdom-only

Go native server: pass --with-go-server (alongside steps 1-3) or
--go-server-only (nothing else):

    python build_native.py --go-server-only

Native GPU (CUDA) tier: pass --with-gpu (alongside steps 1-3) or
--gpu-only (nothing else); needs `nvcc` (the CUDA Toolkit compiler) on
PATH:

    python build_native.py --gpu-only
"""

from __future__ import annotations
import os
import platform
import shutil
import subprocess
import sys

NATIVE_DIR = os.path.dirname(os.path.abspath(__file__))
CPP_DIR = os.path.join(NATIVE_DIR, "cpp")
RUST_SAFETY_DIR = os.path.join(NATIVE_DIR, "rust_safety")
GO_SERVER_DIR = os.path.join(NATIVE_DIR, "go", "server")
GPU_DIR = os.path.join(CPP_DIR, "gpu")
PACKAGE_DIR = os.path.dirname(NATIVE_DIR)  # nexoria/
BIN_DIR = os.path.join(PACKAGE_DIR, "_bin")

IS_WINDOWS = platform.system() == "Windows"
GO_BINARY_NAME = "nexoria-server.exe" if IS_WINDOWS else "nexoria-server"


def _run(cmd: list[str], cwd: str) -> None:
    print(f"$ {' '.join(cmd)}   (in {cwd})")
    subprocess.run(cmd, cwd=cwd, check=True)


def _find_pybind11_cmake_dir() -> str:
    import pybind11
    return pybind11.get_cmake_dir()


def _find_mingw_compilers() -> tuple[str, str] | None:
    """
    Find the gcc/g++ that live in the *same bin directory* as
    mingw32-make itself, rather than trusting a bare compiler *name* to
    resolve correctly on PATH.

    Why this matters: a machine can have an LLVM/clang install earlier
    on PATH than the real MinGW-w64 one. LLVM's clang can masquerade
    under a "gcc"/"cc" name and accept GNU-style flags (CMake then
    reports something like "Clang ... with GNU-like command-line") --
    but it still defaults to the MSVC ABI/target unless told otherwise,
    so it goes looking for kernel32.lib/msvcrtd.lib through lld-link
    instead of MinGW's own libs, and the build fails. This is a
    different resolution path than a plain shell invocation of
    `g++`/`c++`/`mingw32-make` (those can all correctly resolve to the
    real MinGW-w64 copies while CMake's own auto-detection still finds
    the ambiguous one). Anchoring off mingw32-make's own directory
    sidesteps the ambiguity entirely: whatever provides mingw32-make.exe
    also provides the matching gcc.exe/g++.exe right next to it.
    """
    make_path = shutil.which("mingw32-make")
    if make_path is None:
        return None
    bin_dir = os.path.dirname(make_path)
    gcc = os.path.join(bin_dir, "gcc.exe")
    gxx = os.path.join(bin_dir, "g++.exe")
    if os.path.isfile(gcc) and os.path.isfile(gxx):
        return gcc, gxx
    return None


def _windows_cmake_generator() -> tuple[list[str], bool]:
    """
    Decide which CMake generator/build-tool combo to use on Windows, based
    on which toolchain's environment is actually set up in this shell --
    since a machine can easily have both MSVC and a MinGW-w64 install
    present, but only one of them usable without extra setup in any given
    terminal:

      - LIB/INCLUDE set (a VS developer command prompt / vcvarsall.bat
        was run) -> let CMake pick its default Visual Studio generator,
        which drives MSVC directly.
      - LIB/INCLUDE NOT set, but mingw32-make is on PATH -> use the
        "MinGW Makefiles" generator, and pin CMAKE_C_COMPILER/
        CMAKE_CXX_COMPILER to the gcc/g++ living right next to that
        mingw32-make.exe (see _find_mingw_compilers()) instead of
        letting CMake auto-detect a compiler by name -- auto-detection
        is exactly what can land on an unrelated LLVM clang.exe/gcc.exe
        pair earlier on PATH.
      - Neither -> ([], False); the caller's own environment check raises
        a clear error before we'd hit CMake's much less clear one.

    Returns (extra `cmake -G...`/`-D...` args, using_mingw).
    """
    if os.environ.get("LIB") and os.environ.get("INCLUDE"):
        return [], False
    if shutil.which("mingw32-make") is not None:
        args = ["-GMinGW Makefiles"]
        compilers = _find_mingw_compilers()
        if compilers is not None:
            gcc, gxx = compilers
            args += [f"-DCMAKE_C_COMPILER={gcc}", f"-DCMAKE_CXX_COMPILER={gxx}"]
        else:
            print(
                "warning: mingw32-make found, but no gcc.exe/g++.exe sitting next "
                "to it -- letting CMake auto-detect a compiler by name instead, "
                "which can pick up an unrelated clang.exe/gcc.exe from elsewhere "
                "on PATH (e.g. an LLVM install) and fail with confusing "
                "'could not open kernel32.lib'-style linker errors.",
                file=sys.stderr,
            )
        return args, True
    return [], False


def _check_windows_cxx_environment(using_mingw: bool) -> None:
    """
    On Windows, a C++ compiler existing on PATH is not enough for an MSVC
    build: both MSVC's cl.exe and a standalone LLVM/clang++ install need
    the Windows SDK's import libraries (kernel32.lib, user32.lib, ...) on
    LIB, and INCLUDE set for the headers -- both only get set by
    running inside a "Developer Command Prompt for VS" (or after
    calling vcvarsall.bat yourself). Without them, configuration
    proceeds (a bare compiler smoke-test can still pass) but linking
    every real target fails with "could not open 'kernel32.lib'"-style
    errors -- confusing wall-of-text failures deep inside CMake's own
    output. Catch the actual missing ingredient up front instead, with
    one clear fix.

    None of this applies to a MinGW-w64 build (using_mingw=True,
    determined by _windows_cmake_generator() -- it already found
    mingw32-make on PATH and chose the "MinGW Makefiles" generator
    instead): MinGW ships its own bundled headers/import libs and never
    touches VS's Windows SDK setup, so there's nothing to check.
    """
    if not IS_WINDOWS or using_mingw:
        return
    if os.environ.get("LIB") and os.environ.get("INCLUDE"):
        return  # already inside a properly-initialized dev environment

    raise RuntimeError(
        "Windows: no usable C++ build environment detected (neither "
        "MSVC's LIB/INCLUDE env vars nor mingw32-make on PATH). A C++ "
        "compiler merely being on PATH isn't enough for an MSVC build -- "
        "linking needs the Windows SDK's import libraries, which only "
        "get set up inside a Visual Studio developer command prompt.\n\n"
        "Fix -- either:\n"
        "  1. Install \"Visual Studio Build Tools\" if you haven't "
        "already (https://visualstudio.microsoft.com/visual-cpp-build-tools/), "
        "with the \"Desktop development with C++\" workload selected "
        "(this installs MSVC + the Windows SDK together, correctly wired up), "
        "then run `nexoria build-native` from a \"Developer Command "
        "Prompt for VS\" or \"x64 Native Tools Command Prompt for VS\" "
        "(search for it in the Start menu) instead of a plain PowerShell/cmd "
        "window -- that's what sets LIB/INCLUDE for this session.\n"
        "  2. Or install a MinGW-w64 toolchain (e.g. via MSYS2) and make "
        "sure mingw32-make is on PATH -- this step then builds with the "
        "\"MinGW Makefiles\" CMake generator automatically instead, no VS "
        "environment needed.\n\n"
        "If you have a standalone LLVM/clang install (not the one bundled "
        "with Visual Studio) and see \"lld-link: error: could not open "
        "...\", that's this exact issue: clang++ still needs Visual "
        "Studio's Windows SDK libraries, which only your standalone LLVM "
        "install doesn't provide on its own."
    )


def build_rust_safety_core() -> None:
    if shutil.which("cargo") is None:
        raise RuntimeError("cargo not found -- install Rust (https://rustup.rs) to build the native tiers.")
    _run(["cargo", "build", "--release"], cwd=RUST_SAFETY_DIR)


def build_go_server() -> None:
    """
    Build the optional Go native server (native/go/server) and drop the
    binary at nexoria/_bin/nexoria-server[.exe]. This is a *separate*
    optional tier from the Rust/C++ ones above -- it accelerates request
    serving (App.run()), not diffing -- so it's never built by default;
    pass --with-go-server or --go-server-only. App.run() always falls
    back to plain uvicorn if this binary isn't present, so skipping it
    entirely is completely fine.
    """
    if shutil.which("go") is None:
        raise RuntimeError(
            "go not found -- install Go (https://go.dev/dl/) to build the "
            "optional native server tier. This tier is entirely optional: "
            "App.run() always falls back to plain uvicorn if this binary "
            "isn't built."
        )
    os.makedirs(BIN_DIR, exist_ok=True)
    output_path = os.path.join(BIN_DIR, GO_BINARY_NAME)
    # Go's own build cache (under $GOCACHE, outside this repo) already
    # makes repeat builds fast, so -- unlike the CMake tiers above --
    # there's no stale-toolchain-cache class of bug here worth guarding
    # against by wiping anything first.
    _run(["go", "build", "-o", output_path, "."], cwd=GO_SERVER_DIR)
    print(f"  -> built {output_path}")


def build_gpu() -> None:
    """
    Build the optional native GPU (CUDA) tier (native/cpp/gpu/) and
    copy the resulting _nexoria_gpu_cpp*.so/.pyd into the package
    directory, same convention as _copy_built_module() for the VDOM/JS
    tiers. This is a *third* separate optional tier alongside the Go
    server -- it accelerates embarrassingly-parallel batch workloads
    (see nexoria.native.gpu), not request serving or diffing -- so
    it's never built by default; pass --with-gpu or --gpu-only.
    nexoria.native.gpu always falls back to plain Python if this
    extension isn't built, or is built but no CUDA-capable GPU is
    present on the machine actually running the app.
    """
    if shutil.which("nvcc") is None:
        raise RuntimeError(
            "nvcc not found -- install the CUDA Toolkit "
            "(https://developer.nvidia.com/cuda-downloads) to build the "
            "optional native GPU tier. This tier is entirely optional: "
            "nexoria.native.gpu always falls back to plain Python if this "
            "extension isn't built."
        )
    build_dir = _cmake_build(GPU_DIR)
    _copy_built_module(build_dir, "_nexoria_gpu_cpp")


def _cmake_build(module_dir: str, extra_args: list[str] | None = None) -> str:
    build_dir = os.path.join(module_dir, "build")
    # Always start from a clean build directory rather than reusing one
    # from a previous run (exist_ok=True used to do this). CMake caches
    # companion-tool paths (CMAKE_STRIP/CMAKE_AR/CMAKE_RANLIB, ...) the
    # first time it configures a build directory, keyed off whatever
    # compiler was active then -- passing a *different*
    # -DCMAKE_C_COMPILER=... on a later run (e.g. retrying with MinGW
    # after an earlier attempt picked up an unrelated MSVC/Clang
    # install) still re-detects the compiler itself, but does NOT
    # invalidate those already-cached tool paths. The result is a build
    # directory that silently mixes tools from two different toolchains
    # (e.g. real MinGW-w64 gcc/g++ producing the object files, but a
    # leftover CMAKE_STRIP still pointing at LLVM's llvm-strip.exe,
    # which then fails on GNU ld's output with "invalid
    # SymbolTableIndex") -- a confusing failure deep inside the build,
    # long after configure claimed success. A fresh build directory
    # every run costs a slower reconfigure but is the only way to avoid
    # this class of stale-cache bug.
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    cmake_args = ["cmake"]
    using_mingw = False
    if IS_WINDOWS:
        gen_args, using_mingw = _windows_cmake_generator()
        cmake_args += gen_args
    else:
        cmake_args.append("-GNinja")
    cmake_args += [
        f"-Dpybind11_DIR={_find_pybind11_cmake_dir()}",
        "-DCMAKE_BUILD_TYPE=Release",
    ] + (extra_args or []) + [".."]
    _run(cmake_args, cwd=build_dir)

    if IS_WINDOWS:
        if using_mingw:
            # The "MinGW Makefiles" generator produces an ordinary
            # Makefile meant to be driven by mingw32-make (NOT plain
            # `make`, and not `cmake --build`'s own MSVC-flavored
            # invocation) -- same single-config layout as Ninja, so
            # output lands directly in build_dir, no Release/ subdir.
            _run(["mingw32-make"], cwd=build_dir)
        else:
            _run(["cmake", "--build", ".", "--config", "Release"], cwd=build_dir)
    else:
        _run(["ninja"], cwd=build_dir)
    return build_dir


def _copy_built_module(build_dir: str, module_name: str) -> None:
    # On Windows with a Visual Studio generator, build output lands in
    # a config subdirectory (e.g. build/Release/) rather than directly
    # in build/ the way Ninja's single-config output does.
    search_dirs = [build_dir, os.path.join(build_dir, "Release")]
    for search_dir in search_dirs:
        if not os.path.isdir(search_dir):
            continue
        for fname in os.listdir(search_dir):
            if fname.startswith(module_name) and (fname.endswith(".so") or fname.endswith(".pyd")):
                shutil.copy(os.path.join(search_dir, fname), os.path.join(PACKAGE_DIR, fname))
                print(f"  -> copied {fname} into {PACKAGE_DIR}")
                return
    raise RuntimeError(f"Build succeeded but no {module_name}*.so/.pyd found in {build_dir} (or its Release/ subdir)")


def _mingw_make_build(module_dir: str, makefile: str = "Makefile.mingw") -> str:
    """
    Build a module using mingw32-make directly, bypassing CMake entirely.
    Only implemented where the module ships a hand-written mingw32-make
    Makefile (currently just cpp/vdom/Makefile.mingw) -- unlike CMake's
    generic generator-driven build, this drives g++ against a Makefile
    written specifically for the MinGW-w64/GNU toolchain, so it also
    sidesteps the MSVC-vs-GNU staticlib-naming pitfall entirely (the
    Makefile only ever looks for the GNU-named libnexoria_safety_core.a).
    """
    makefile_path = os.path.join(module_dir, makefile)
    if not os.path.isfile(makefile_path):
        raise RuntimeError(f"no {makefile} found in {module_dir} -- mingw32-make build isn't set up for this module yet.")
    build_dir = os.path.join(module_dir, "build")
    _run(["mingw32-make", "-f", makefile], cwd=module_dir)
    return build_dir


def build_vdom_cpp(use_mingw_make: bool = False) -> None:
    vdom_dir = os.path.join(CPP_DIR, "vdom")
    if use_mingw_make:
        build_dir = _mingw_make_build(vdom_dir)
    else:
        build_dir = _cmake_build(vdom_dir)
    _copy_built_module(build_dir, "_nexoria_vdom_cpp")


def build_js_engine() -> None:
    jsengine_dir = os.path.join(CPP_DIR, "jsengine")
    vendor_quickjs = os.path.join(jsengine_dir, "vendor", "quickjs")
    if not os.path.isdir(vendor_quickjs):
        raise RuntimeError(
            f"QuickJS-ng source not found at {vendor_quickjs}. "
            "Vendor it with:\n"
            "  curl -sL https://codeload.github.com/quickjs-ng/quickjs/tar.gz/refs/tags/v0.10.1 -o quickjs.tar.gz\n"
            f"  tar xzf quickjs.tar.gz -C {os.path.join(jsengine_dir, 'vendor')}\n"
            "  mv vendor/quickjs-0.10.1 vendor/quickjs"
        )
    build_dir = _cmake_build(jsengine_dir)
    _copy_built_module(build_dir, "_nexoria_js")


def main() -> None:
    # --vdom-with-mingw: build just the VDOM tier with mingw32-make
    # (cpp/vdom/Makefile.mingw) instead of CMake+Ninja/MSVC. The JS
    # engine tier still needs CMake either way -- there's no mingw32-make
    # Makefile for it (it vendors a much larger QuickJS-ng CMake build
    # that isn't practical to hand-port). Only skips the cmake/ninja
    # PATH check when that's *all* you're building.
    #
    # --with-go-server / --go-server-only and --with-gpu / --gpu-only:
    # the Go native server (build_go_server()) and the native GPU tier
    # (build_gpu()) are each a wholly separate tier on their own
    # toolchain (Go and the CUDA Toolkit respectively), so both are
    # opt-in rather than part of the default 3-step flow. Any "-only"
    # flag builds nothing else at all (no cmake/cargo checks even run
    # for tiers 1-3), while any "--with-*" flag adds that tier alongside
    # the usual steps. Any combination of "-only" flags can be passed
    # together to build just those opt-in tiers and skip 1-3 entirely.
    use_mingw_vdom = "--vdom-with-mingw" in sys.argv
    vdom_only = "--vdom-only" in sys.argv
    go_server_only = "--go-server-only" in sys.argv
    gpu_only = "--gpu-only" in sys.argv
    build_go = go_server_only or "--with-go-server" in sys.argv
    build_gpu_tier = gpu_only or "--with-gpu" in sys.argv

    if go_server_only or gpu_only:
        if go_server_only:
            try:
                print("== Go native server ==")
                build_go_server()
            except RuntimeError as e:
                print(f"error: {e}", file=sys.stderr)
                sys.exit(1)
        if gpu_only:
            try:
                print("== Native GPU (CUDA) tier ==")
                build_gpu()
            except RuntimeError as e:
                print(f"error: {e}", file=sys.stderr)
                sys.exit(1)
        print("\nDone. Run `nexoria doctor` to confirm the requested tier(s) are available.")
        return

    if use_mingw_vdom and shutil.which("mingw32-make") is None:
        print("error: --vdom-with-mingw needs mingw32-make on PATH (part of a MinGW-w64 install).", file=sys.stderr)
        sys.exit(1)

    needs_cmake = not (use_mingw_vdom and vdom_only)
    if needs_cmake and shutil.which("cmake") is None:
        print("error: this needs cmake on PATH (native VDOM/JS engine tiers).", file=sys.stderr)
        sys.exit(1)
    if needs_cmake and not IS_WINDOWS and shutil.which("ninja") is None:
        print("error: this needs ninja on PATH (native VDOM/JS engine tiers).", file=sys.stderr)
        sys.exit(1)

    try:
        # This check is specifically about MSVC/clang-cl needing Visual
        # Studio's LIB/INCLUDE env vars -- skip it entirely when nothing
        # cmake-driven is going to run (e.g. --vdom-with-mingw
        # --vdom-only, which never touches cmake at all), and otherwise
        # let _windows_cmake_generator()'s own detection decide whether
        # the upcoming cmake step(s) will use MSVC or "MinGW Makefiles"
        # -- only the former needs LIB/INCLUDE.
        if needs_cmake and IS_WINDOWS:
            _, using_mingw_cmake = _windows_cmake_generator()
            _check_windows_cxx_environment(using_mingw_cmake)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    print("== 1/3: Rust safety core ==")
    build_rust_safety_core()
    print(f"== 2/3: native C++ VDOM {'(mingw32-make)' if use_mingw_vdom else '(cmake)'} ==")
    build_vdom_cpp(use_mingw_make=use_mingw_vdom)
    if vdom_only:
        print("\n--vdom-only: skipping the JS engine tier.")
    else:
        print("== 3/3: embedded JS engine ==")
        build_js_engine()
    if build_go:
        try:
            print("== Go native server ==")
            build_go_server()
        except RuntimeError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)
    if build_gpu_tier:
        try:
            print("== Native GPU (CUDA) tier ==")
            build_gpu()
        except RuntimeError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)
    print("\nDone. Run `nexoria doctor` to confirm all tiers report ACTIVE/available.")


if __name__ == "__main__":
    main()
