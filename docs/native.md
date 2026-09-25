# `nexoria.native` — optional native tiers

> Five independent, optional native layers. None is required; each has a working fallback. Build them with `nexoria native build`.

| | |
|---|---|
| **Python API** | `from nexoria.native import npm, gpu, Runtime, js_available` · `from nexoria.native import goserver` |
| **Source** | `nexoria/native/` — `build_native.py`, `goserver.py`, `gpu.py`, `js.py`, `npm.py`, `rust_safety/`, `cpp/{vdom,jsengine,gpu}/`, `go/server/` |
| **Build with** | `nexoria native build [--vdom-only] [--with-go-server] [--with-gpu] …` (see [`cli`](cli.md)) |
| **Check with** | `nexoria doctor` / `nexoria native status` |

## The tiers at a glance

| # | Tier | Language | Output | Fallback when absent |
|---|---|---|---|---|
| 1 | **Safety core** — generational string interner | Rust | `libnexoria_safety_core.a` (linked into #2) | n/a (build dependency of #2) |
| 2 | **C++ VDOM** — arena tree differ | C++17 + pybind11 | `nexoria/_nexoria_vdom_cpp*.so/.pyd` | PyO3 Rust differ → pure-Python differ |
| 3 | **Embedded JS engine** — QuickJS-ng + CommonJS loader | C++17 + pybind11 | `nexoria/_nexoria_js*.so/.pyd` | `Runtime()` raises `NativeEngineUnavailable` |
| 4 | **Go edge server** — static cache, firewall, reverse proxy | Go | `nexoria/_bin/nexoria-server[.exe]` | plain uvicorn |
| 5 | **GPU tier** — batch hashing / row-diff | CUDA C++ | `nexoria/_nexoria_gpu_cpp*.so/.pyd` | pure-Python implementations |

(The PyO3 Rust extension is a separate, `maturin`-built component — see [`rust_ext`](rust_ext.md).)

Build prerequisites, on the **build machine only**: a C++17 compiler, CMake ≥ 3.18, Ninja (non-Windows), Rust/Cargo, and `pybind11` for Python. Go needs the Go toolchain; the GPU tier needs `nvcc` (CUDA Toolkit).

---

## 1. Rust safety core

A `cdylib`/`staticlib` crate (`nexoria-safety-core`) exporting a C ABI:

`nx_interner_new`, `nx_interner_free`, `nx_interner_intern(ptr, data, len) -> u32`, `nx_interner_get_len`, `nx_interner_get_ptr`, `nx_interner_ids_equal(a, b) -> int`.

Purpose: the C++ differ compares list **keys** on every diff. The interner owns every key string for its lifetime and hands back a stable `u32` id (0 means "no key"), turning key comparison into an integer equality check and removing manual string-lifetime code from C++. Every exported function is wrapped in `catch_unwind` so a Rust panic can never unwind into C++. Header: `cpp/vdom/nexoria_safety_core.h`.

## 2. C++ VDOM

`nexoria._nexoria_vdom_cpp.VDomEngine().diff(old, new)` — same algorithm and test vectors as the Python and Rust differs, with an arena of `VNode`s and key ids from the safety core. Builds via CMake (`CMakeLists.txt`) or, on bare MinGW-w64 Windows, `Makefile.mingw` (`--vdom-with-mingw`). Because it is the same algorithm, it has the same [keyed-list limitations](render.md#known-limitations-of-keyed-lists).

## 3. Embedded JS engine

Vendors [QuickJS-ng](https://github.com/quickjs-ng/quickjs) (v0.10.1 recommended by the build script; **not V8**) and wraps it with a minimal CommonJS loader (`require`, `module.exports`, `__dirname`, `__filename`; relative, absolute and package resolution) and a small Node-like shim (`console`, `process`, synchronous `setTimeout`/`setImmediate`). Exposed as `nexoria._nexoria_js.Engine`.

```python
from nexoria.native import Runtime, js_available

if js_available():
    rt = Runtime()                     # isolated globals + module cache
    print(rt.eval("1 + 2"))            # 3
    _ = rt.require("lodash")           # fetched from the npm registry on first use
    print(rt.eval('JSON.stringify(require("lodash").chunk([1,2,3,4,5], 2))'))
```

`Runtime` methods: `eval(code, filename="<eval>")`, `require(name, version="latest", prefer_module=False)`, `install_local(name, directory)`. Objects, arrays, strings and numbers marshal back to Python; **function values come back only as the string `"[Function]"`**, so for functions write JS glue with `eval()`.

`nexoria.native.npm` is a pure-Python npm registry client (`resolve`, `install`, `entry_point`, `PackageInfo`): it downloads a package's tarball from `registry.npmjs.org` into `~/.nexoria/npm_cache/<name>@<version>/` (with a `.nexoria-installed` marker) using `tarfile`'s `data` extraction filter. It fetches **one package, no transitive dependencies**, runs no lifecycle scripts, and has no lockfile.

**What works:** pure computation libraries (lodash, dayjs, animejs' math/easing helpers, React's `createElement` tree API, Three.js math and scene-graph classes). **What does not:** DOM, WebGL, Node built-ins beyond the shim (`fs`, `http`, `child_process`, workers), native add-ons, and full toolchains such as Next.js. It is a small JS engine for the pure-JS subset of npm, not a Node replacement. This is unrelated to the client-side [`nexoria.js`](js.md) helpers.

## 4. Go edge server

`nexoria-server` sits in front of the Python app. `App.run()` spawns it automatically when the binary exists (never with `reload=True`).

```
Browser ──► nexoria-server (firewall → gzip/security headers → routing)
              ├─ /static/*, /_nexoria/<file>, /favicon.ico  → in-memory, stat-validated cache
              ├─ /_nexoria/native-health, /_nexoria/firewall-status → local JSON
              └─ everything else (SSR, WebSocket, /_nexoria/health) → reverse proxy → uvicorn on 127.0.0.1:<free port>
```

Source files: `main.go` (flags, wiring, graceful shutdown), `firewall.go`, `middleware.go` (gzip, security headers, panic recovery, timeouts), `cache.go`, `static.go`, `favicon.go`, `proxy.go` (`httputil.ReverseProxy`, WebSocket upgrades pass through), `health.go`. Standard library only.

**Flags** (all also settable indirectly through `App.run(firewall={...})` for the firewall group):

| Flag | Default | Notes |
|---|---|---|
| `-listen` | `127.0.0.1:8000` | Public address |
| `-backend` | `127.0.0.1:8001` | Python ASGI backend (set by `App.run`) |
| `-static-dir`, `-runtime-dir`, `-name` | — | Set by `App.run` |
| `-gzip` | `true` | |
| `-cache-max-bytes` | 64 MiB | In-memory asset cache |
| `-read-timeout`, `-write-timeout`, `-idle-timeout` | 15 s, 60 s, 120 s | `-write-timeout 0` disables |
| `-firewall` | `true` | Master switch |
| `-firewall-allow` / `-firewall-deny` | empty | Comma-separated IPs/CIDRs |
| `-firewall-rate-limit` / `-firewall-rate-burst` | 20 req/s, 40 | Per client IP, token bucket |
| `-firewall-max-body-bytes` | 10 MiB | Caps how much a handler may read |
| `-firewall-trust-x-forwarded-for` | `false` | Enable only behind a proxy you control |

**Firewall check order:** deny list → allow list (if non-empty, only these pass) → per-IP rate limit → request sanity (disallowed methods, oversized request lines, raw path-traversal/NUL probes) → body-size cap. It runs before every other handler. Counters: `/_nexoria/firewall-status`.

```python
app.run(host="0.0.0.0", port=8000, firewall={"deny": "203.0.113.0/24", "rate_limit": 5, "rate_burst": 10})
```

Falling back: with no binary, `App.run()` uses plain uvicorn, which has **no firewall of its own**.

## 5. GPU tier

A CUDA extension for embarrassingly parallel **batch** work — deliberately *not* the single-tree VDOM diff (branchy, pointer-chasing traversal suits CPUs, not GPUs).

| Function | Behaviour |
|---|---|
| `gpu.is_available()` | `True` only if the module is built **and** a CUDA device is visible right now |
| `gpu.device_count()`, `gpu.device_info(index=0)` | Device details (`name`, compute capability, SM count, VRAM) or `0`/`None` |
| `gpu.batch_hash(items: list[str]) -> list[int]` | One 64-bit hash per string, order preserved |
| `gpu.batch_row_diff(old_rows, new_rows) -> list[list[int]]` | Per row, the column indices whose value changed |

Fallbacks are pure Python and produce correct results. Note that the `batch_hash` fallback uses Python's built-in `hash()` masked to 64 bits: those values are salted per process and are **not comparable** with the GPU's hashes. Only compare hashes produced by the same backend within one process.

Kernels are compiled for a spread of NVIDIA architectures (Pascal through Hopper) so a wheel built on one machine runs on another; every CUDA call is checked and raises a descriptive `RuntimeError` on failure.

---

## `build_native.py`

Orchestrates all of the above (`main()` reads flags from `sys.argv`; `nexoria native build` sets them for you). Notable behaviour:

- On Windows it picks the toolchain from the environment: MSVC if `LIB`/`INCLUDE` are set, otherwise MinGW Makefiles pinned to the `gcc`/`g++` next to `mingw32-make` (avoiding an unrelated LLVM/clang earlier on `PATH`); otherwise a clear error explaining how to get a working environment.
- Built modules are copied into the package directory; the Go binary goes to `nexoria/_bin/`.
- The JS engine needs QuickJS-ng under `cpp/jsengine/vendor/quickjs/` (already vendored in the source tree).

## API reference

### `nexoria.native.gpu`

### Functions

#### `batch_hash(items: list[str]) -> list[int]`

Fingerprint every string in `items` (one 64-bit hash each, order preserved). Useful for cheaply detecting "did anything in this batch of independent VDOM subtrees / grid rows change at all" across thousands of items in parallel, before falling through to nexoria.render.diff's detailed CPU-side diff only on the ones that did. Falls back to Python's own hash() per item (still correct, just not GPU-parallel) when the GPU tier isn't available.

#### `batch_row_diff(old_rows: list[list[float]], new_rows: list[list[float]]) -> list[list[int]]`

For two equal-length lists of equal-length numeric rows (a plain rectangular table -- the shape nexoria.aggrid row_data already is), return, per row, the list of column indices whose value differs. Intended for bulk table/grid updates where hundreds or thousands of rows change independently in a single state update -- exactly the embarrassingly-parallel shape GPU hardware suits. Falls back to a plain per-cell Python comparison (same result shape) when the GPU tier isn't available.

#### `device_count() -> int`

Number of CUDA-capable devices visible to this process (0 if the tier isn't built, or no GPU/driver is present).

#### `device_info(index: int = 0) -> Optional[dict]`

Static properties (name, compute capability, SM count, total VRAM) of device `index`, or None if no GPU is available at all.

#### `is_available() -> bool`

True only if BOTH the GPU tier was built (a CUDA Toolkit was present when `build-native --with-gpu` ran) AND at least one CUDA-capable GPU is actually visible on this machine right now. Every other function in this module checks this itself, so calling it first is only needed if you want to know which path will run.

### `nexoria.native.npm`

### Classes

#### `class PackageInfo(name: str, version: str, tarball_url: str, main: Optional[str], module: Optional[str]) -> None`

PackageInfo(name: 'str', version: 'str', tarball_url: 'str', main: 'Optional[str]', module: 'Optional[str]')

### Functions

#### `entry_point(pkg_dir: str, prefer_module: bool = False) -> str`

Resolve the file a `require()`/`import` of this package should load.

#### `install(name: str, version: str = 'latest', cache_dir: str = '/root/.nexoria/npm_cache', force: bool = False) -> str`

Download + extract a single package (no transitive deps) into the local cache. Returns the local directory containing its files (package.json, dist/, etc.) — mirroring npm's `node_modules/<pkg>/` layout for that one package.

#### `resolve(name: str, version: str = 'latest') -> PackageInfo`

Look up a package's metadata on the public npm registry.

### Constants

| Name | Value |
|---|---|
| `DEFAULT_CACHE_DIR` | `'/root/.nexoria/npm_cache'` |
| `REGISTRY` | `'https://registry.npmjs.org'` |

### `nexoria.native.js`

### Classes

#### `class NativeEngineUnavailable()`

#### `class Runtime()`

A single embedded JS execution context. Create one per logical "process" you want isolated (module caches, globals, etc. are not shared across Runtime instances).

- **`.eval(code: str, filename: str = '<eval>') -> Any`** — Evaluate a JS source string; returns the result as a Python value.
- **`.install_local(name: str, directory: str) -> None`** — Point `require(name)` at an already-local package directory (e.g. one you vendor yourself) instead of fetching from npm.
- **`.require(name: str, version: str = 'latest', prefer_module: bool = False) -> Any`** — Fetch (if needed) and load an npm package by name, purely via the public npm registry API + this engine — no Node/npm CLI. Returns the package's `module.exports`, converted to a Python value.

### Functions

#### `is_available() -> bool`

Whether the native engine was built for this platform/install.
