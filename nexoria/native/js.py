"""
nexoria.native.js
====================
Python-facing wrapper around the embedded C++ JS engine
(`nexoria._nexoria_js`, built from `nexoria/native/cpp/jsengine/`, which
vendors QuickJS-ng). Combined with `nexoria.native.npm`, this lets you
run real npm packages with **no Node.js or system JS runtime installed
anywhere** — the engine and the package fetcher are both pure
Python+C++, no shelling out to `node`/`npm`.

    from nexoria.native.js import Runtime

    rt = Runtime()
    lodash = rt.require("lodash")          # fetches from the real npm
                                            # registry on first use, then
                                            # caches locally
    print(lodash["chunk"])                 # dict/list results convert
                                            # straight to Python

Honest scope (read this before reaching for a package):

- **Works well**: pure computation/data/utility libraries with no DOM or
  Node-builtin dependency -- lodash, dayjs, most math/animation *logic*
  (e.g. animejs's `utils`/`easings`), and the DOM-independent parts of
  bigger libraries (React's `createElement`/element-tree APIs; Three.js's
  math and scene-graph classes like `Vector3`/`Matrix4`/`BufferGeometry`).
- **Does not work**: anything needing a real DOM (`document`, rendering
  React to actual elements), a GPU/WebGL context (Three.js's
  `WebGLRenderer` — that still runs client-side in the browser via
  `nexoria.threejs`, which already works), Node builtins beyond the tiny
  shim here (`fs`, `http`, `child_process`, worker threads), native addons
  (anything needing node-gyp/prebuilt `.node` binaries), or a
  bundler/dev-server framework like Next.js (which is a full build
  toolchain, not a library you `require()`).
- This is **not** a Node.js replacement. It is a real, working, minimal
  CommonJS-capable JS engine for the pure-JS subset of the npm ecosystem.
"""

from __future__ import annotations
from typing import Any, Optional

from . import npm

try:
    from .. import _nexoria_js
    _HAS_ENGINE = True
except ImportError:  # pragma: no cover - native engine not built
    _nexoria_js = None
    _HAS_ENGINE = False


class NativeEngineUnavailable(RuntimeError):
    pass


class Runtime:
    """
    A single embedded JS execution context. Create one per logical
    "process" you want isolated (module caches, globals, etc. are not
    shared across Runtime instances).
    """

    def __init__(self):
        if not _HAS_ENGINE:
            raise NativeEngineUnavailable(
                "The native JS engine (nexoria._nexoria_js) isn't built for "
                "this platform. Build it with CMake from "
                "nexoria/native/cpp/jsengine/ (see docs/native.md), or run "
                "`nexoria doctor` for guidance."
            )
        self._engine = _nexoria_js.Engine()
        self._installed_roots: set[str] = set()

    def eval(self, code: str, filename: str = "<eval>") -> Any:
        """Evaluate a JS source string; returns the result as a Python value."""
        return self._engine.eval(code, filename)

    def require(self, name: str, version: str = "latest", prefer_module: bool = False) -> Any:
        """
        Fetch (if needed) and load an npm package by name, purely via the
        public npm registry API + this engine — no Node/npm CLI. Returns
        the package's `module.exports`, converted to a Python value.

        For packages you'll call functions on repeatedly, prefer
        `require_raw_js` + your own `eval()` glue, since function values
        currently marshal back to Python only as the string
        `"[Function]"` (see module docstring) — object/array/string/
        number results convert fully, which covers most utility-library
        usage (`lodash`, `dayjs`, math helpers, etc.).
        """
        if name not in self._installed_roots:
            pkg_dir = npm.install(name, version)
            self._engine.register_package_root(name, pkg_dir)
            self._installed_roots.add(name)
        return self._engine.require(name)

    def install_local(self, name: str, directory: str) -> None:
        """Point `require(name)` at an already-local package directory
        (e.g. one you vendor yourself) instead of fetching from npm."""
        self._engine.register_package_root(name, directory)
        self._installed_roots.add(name)


def is_available() -> bool:
    """Whether the native engine was built for this platform/install."""
    return _HAS_ENGINE
