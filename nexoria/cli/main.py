"""
nexoria.cli.main
===================
The `nexoria` command-line tool:

    nexoria new myapp          # scaffold a new project
    nexoria dev                # run the dev server with hot patch reload
    nexoria build               # production build (invokes Node/esbuild)
    nexoria doctor               # full toolchain + native-tier status report
    nexoria native status       # just the native-tier table
    nexoria native build        # build the optional native tiers from source
    nexoria native clean        # remove built native artifacts
    nexoria build-desktop        # scaffold an Electron desktop shell
    nexoria build-mobile         # scaffold a Capacitor mobile shell

Every command works with zero extra dependencies; installing `rich`
(a regular dependency of this package) upgrades the output to colored
tables, spinners and panels. Pass --no-color, or set NO_COLOR=1, to
force the plain-text rendering either way.
"""

from __future__ import annotations

import argparse
import glob
import importlib
import os
import platform
import shutil
import subprocess
import sys
import textwrap

from . import ui
from ..__version__ import __version__, __framework_name__

TEMPLATE_APP_PY = '''\
from nexoria import App, Component, el, State, Router, Stylesheet

class Home(Component):
    styles = Stylesheet()

    def setup(self):
        self.state = State({{"count": 0}})

    def render(self):
        hero = self.styles.scoped_class(
            "hero", display="flex", flex_direction="column",
            align_items="center", gap="16px", text_align="center",
        )
        return el("div",
            el("nav",
                el("span", "{app_name}", class_="nx-brand"),
                class_="nx-nav",
            ),
            el("div",
                el("h1", "Welcome to {app_name}"),
                el("p", f"Clicked {{self.state['count']}} times",
                   style={{"color": "var(--nx-text-muted)"}}),
                el("button", "Click me", class_="nx-btn",
                   on_click=lambda e: self.state.update(count=self.state["count"] + 1)),
                class_=f"nx-card {{hero}}",
            ),
            class_="nx-container",
        )

router = Router()
router.add("/", Home)

app = App(name="{app_name}", router=router, static_dir="static", debug=True)

if __name__ == "__main__":
    app.run(reload=True)
'''

TEMPLATE_PACKAGE_JSON = '''\
{{
  "name": "{app_name}",
  "version": "0.1.0",
  "private": true,
  "description": "A Nexoria application ({app_name}).",
  "scripts": {{
    "build": "node ../../tools/node-build/build.js",
    "dev": "node ../../tools/node-build/build.js --watch"
  }},
  "devDependencies": {{
    "esbuild": "^0.23.0"
  }}
}}
'''

TEMPLATE_GITIGNORE = "__pycache__/\n*.pyc\n.venv/\nnode_modules/\ndist/\n.nexoria-cache/\n"


# --------------------------------------------------------------------------
# new
# --------------------------------------------------------------------------

def cmd_new(args: argparse.Namespace) -> None:
    name = args.name
    if os.path.exists(name):
        if not args.force and not ui.confirm(
            f"Directory '{name}' already exists. Overwrite its contents?", default=False,
        ):
            ui.error(f"directory '{name}' already exists (pass --force to overwrite without asking)")
            sys.exit(1)

    with ui.spinner(f"Scaffolding '{name}'..."):
        os.makedirs(os.path.join(name, "static"), exist_ok=True)
        with open(os.path.join(name, "app.py"), "w") as f:
            f.write(TEMPLATE_APP_PY.format(app_name=name))
        with open(os.path.join(name, "package.json"), "w") as f:
            f.write(TEMPLATE_PACKAGE_JSON.format(app_name=name))
        with open(os.path.join(name, ".gitignore"), "w") as f:
            f.write(TEMPLATE_GITIGNORE)

    ui.success(f"Created {__framework_name__} project '{name}'.")
    ui.key_values("Next steps", [
        ("1.", f"cd {name}"),
        ("2.", "pip install nexoria"),
        ("3.", "python app.py    (or: nexoria dev)"),
    ])


# --------------------------------------------------------------------------
# dev
# --------------------------------------------------------------------------

def cmd_dev(args: argparse.Namespace) -> None:
    sys.path.insert(0, os.getcwd())
    module_name = args.module.replace(".py", "")
    try:
        mod = importlib.import_module(module_name)
    except ImportError as e:
        ui.error(f"could not import '{module_name}': {e}")
        sys.exit(1)

    app = getattr(mod, "app", None)
    if app is None:
        ui.error(f"module '{module_name}' has no top-level `app` object (expected an `App(...)` instance)")
        sys.exit(1)

    ui.key_values(f"{__framework_name__} dev server", [
        ("Module", module_name),
        ("URL", f"http://{args.host}:{args.port}"),
        ("Hot reload", "on"),
        ("Debug", "on" if getattr(app, "debug", False) else "off"),
    ])
    ui.info()
    app.run(host=args.host, port=args.port, reload=True)


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------

def cmd_build(args: argparse.Namespace) -> None:
    node_build = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "tools", "node-build", "build.js",
    )
    if shutil.which("node") is None:
        ui.warn("Node.js not found on PATH -- skipping asset bundling step.")
        return
    with ui.spinner("Bundling app assets (esbuild via Node)..."):
        try:
            subprocess.run(["node", node_build], check=True)
        except subprocess.CalledProcessError as e:
            ui.error(f"asset build failed (exit code {e.returncode})")
            sys.exit(e.returncode)
    ui.success("Build complete.")


# --------------------------------------------------------------------------
# shared native-tier / toolchain status collection (used by both
# `doctor` and `native status`)
# --------------------------------------------------------------------------

# Extension files that Python's import machinery can actually load,
# whatever platform/interpreter they were built for. Used to find
# candidate builds on disk independently of whether the *current*
# interpreter can load them -- see _probe_native_module() below.
_EXTENSION_EXTS = (".so", ".pyd", ".dylib")


def _package_dir() -> str:
    """The directory Python is actually importing `nexoria` from right
    now -- i.e. exactly where __version__.py and every compiled
    _nexoria_*.pyd/.so needs to sit to be picked up. If this doesn't
    match the folder you're dropping built binaries into (a separate
    editable checkout vs. an installed copy, a second Python on PATH,
    a mismatched venv, ...), that mismatch -- not a missing file -- is
    almost always why a tier that's clearly "right there" still shows
    as not built."""
    import nexoria as _nexoria_pkg
    return os.path.dirname(os.path.abspath(_nexoria_pkg.__file__))


def _interpreter_tag() -> str:
    import sysconfig
    ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or "unknown ABI tag"
    impl = sys.implementation.name
    ver = ".".join(map(str, sys.version_info[:2]))
    return f"{impl} {ver}, {platform.machine()} (expects *{ext_suffix})"


def _find_candidate_builds(base_name: str, pkg_dir: str) -> list[str]:
    """Any file in pkg_dir that looks like a compiled build of
    `base_name` for *any* platform/interpreter -- e.g. both
    _nexoria_vdom_cpp.cp312-win_amd64.pyd and
    _nexoria_vdom_cpp.cpython-312-x86_64-linux-gnu.so match, whether or
    not either one is loadable by the Python running right now."""
    return sorted(
        os.path.basename(p)
        for p in glob.glob(os.path.join(pkg_dir, base_name + "*"))
        if os.path.splitext(p)[1].lower() in _EXTENSION_EXTS
    )


def _probe_native_module(base_name: str, verify=None) -> tuple:
    """
    Tries to actually import+use nexoria.<base_name> for this process,
    while separately scanning disk for any matching build regardless
    of whether it's loadable here. This tells apart three situations
    that a bare `except ImportError: available = False` collapses into
    one indistinguishable "not built":

      1. genuinely not built anywhere       -> no file found on disk
      2. built, but for a different         -> file(s) found, but this
         interpreter/OS/architecture           interpreter can't load
                                                any of them
      3. built for this exact interpreter,  -> file found, import
         but broken some other way             raises something other
         (missing runtime DLL, a crash          than "just missing"
         inside the extension's own init)

    Returns (ok, detail) -- ok is True only for a build that actually
    loaded (and passed `verify`, if given) in this process.
    """
    pkg_dir = _package_dir()
    candidates = _find_candidate_builds(base_name, pkg_dir)
    try:
        mod = importlib.import_module(f"nexoria.{base_name}")
        if verify is not None:
            verify(mod)
    except Exception as e:
        if candidates:
            return False, (
                f"found {', '.join(candidates)} in {pkg_dir}, but "
                f"this interpreter -- {_interpreter_tag()} -- couldn't load it "
                f"({type(e).__name__}: {e})"
            )
        return False, f"not found in {pkg_dir} (`nexoria native build`)"
    loaded_from = os.path.basename(getattr(mod, "__file__", "") or "") or base_name
    return True, f"loaded {loaded_from}"


def _which_detail(tool: str, note: str) -> ui.StatusRow:
    found = shutil.which(tool) is not None
    return (tool, True if found else None, "found on PATH" if found else note)


def _native_tier_rows() -> list:
    from ..render.diff import hot_path_active
    from ..native import goserver, gpu

    tier = hot_path_active()
    cpp_ok, cpp_detail = _probe_native_module("_nexoria_vdom_cpp", verify=lambda m: m.VDomEngine())
    rust_ok, rust_detail = _probe_native_module("_nexoria_rs")
    js_ok, js_detail = _probe_native_module("_nexoria_js")

    rows: list = [
        ("C++ VDOM diff engine",
         True if tier == "cpp" else (None if cpp_ok else False),
         "active -- fastest diff path" if tier == "cpp" else cpp_detail),
        ("PyO3 Rust extension (_nexoria_rs)",
         True if tier == "rust" else (None if rust_ok else False),
         "active" if tier == "rust" else (
             "loaded, but a faster tier is active" if rust_ok else rust_detail)),
        ("Pure-Python diff fallback", True,
         "active -- always available" if tier == "python" else "available as fallback"),
        ("Embedded JS engine (QuickJS)", js_ok,
         "available -- no Node.js required" if js_ok else js_detail),
    ]
    go_ok = goserver.is_available()
    rows.append((
        "Native edge server (Go)", go_ok if go_ok else None,
        f"available ({goserver.binary_path()})" if go_ok
        else f"not found in {goserver._BIN_DIR} -- App.run() falls back to uvicorn (`nexoria native build --with-go-server`)",
    ))
    gpu_module_ok, gpu_module_detail = _probe_native_module("_nexoria_gpu_cpp", verify=lambda m: m.GPUEngine())
    if gpu.is_available():
        dinfo = gpu.device_info() or {}
        gpu_detail = f"active ({dinfo.get('name', 'unknown GPU')}, {gpu.device_count()} device(s))"
        gpu_ok = True
    elif gpu_module_ok:
        gpu_detail = "built, but no CUDA-capable GPU visible on this machine"
        gpu_ok = None
    else:
        gpu_detail = gpu_module_detail
        gpu_ok = None if "not found" in gpu_detail else False
    rows.append(("Native GPU tier (CUDA)", gpu_ok, gpu_detail))
    return rows


def _toolchain_rows() -> list:
    return [
        _which_detail("node", "optional, only used by `nexoria build` to bundle app JS"),
        _which_detail("rustc", "optional, only needed to build the native tiers"),
        _which_detail("cargo", "optional, only needed to build the native tiers"),
        _which_detail("cmake", "optional, only needed to build the C++ tiers"),
        _which_detail("ninja", "optional, alternative build driver for the C++ tiers"),
        _which_detail("mingw32-make", "optional Windows-only alternative to cmake for the VDOM tier"),
        _which_detail("go", "optional, only needed for the native edge-server tier"),
        _which_detail("nvcc", "optional, only needed for the native GPU (CUDA) tier"),
    ]


def _collect_status() -> dict:
    return {
        "version": __version__,
        "python": sys.version.split()[0],
        "package_dir": _package_dir(),
        "interpreter": _interpreter_tag(),
        "native_tiers": [
            {"component": n, "ready": ok, "detail": d} for n, ok, d in _native_tier_rows()
        ],
        "toolchains": [
            {"tool": n, "found": bool(ok), "detail": d} for n, ok, d in _toolchain_rows()
        ],
    }


# --------------------------------------------------------------------------
# doctor
# --------------------------------------------------------------------------

def cmd_doctor(args: argparse.Namespace) -> None:
    if getattr(args, "json", False):
        import json
        print(json.dumps(_collect_status(), indent=2))
        return

    ui.banner(__version__)
    ui.info(f"Package dir : {_package_dir()}   (drop compiled *_nexoria_*.pyd/.so files here)")
    ui.info(f"Interpreter : {_interpreter_tag()}")
    ui.status_table(
        f"{__framework_name__} v{__version__} -- system report",
        [
            ("Native tiers (what's actually running)", _native_tier_rows()),
            ("Build toolchains (only needed for `nexoria native build`)", _toolchain_rows()),
        ],
    )
    ui.info(f"\nPython {sys.version.split()[0]} on {sys.platform}")
    ui.info("Run `nexoria native build --help` to build any missing native tier from source.")


# --------------------------------------------------------------------------
# native  (status / build / clean)
# --------------------------------------------------------------------------

def cmd_native_status(args: argparse.Namespace) -> None:
    ui.info(f"Package dir : {_package_dir()}   (drop compiled *_nexoria_*.pyd/.so files here)")
    ui.info(f"Interpreter : {_interpreter_tag()}")
    ui.status_table(
        "Native tiers", [("Status", _native_tier_rows())],
    )


def _run_build_native(args: argparse.Namespace) -> None:
    from ..native import build_native

    flags = []
    if args.vdom_with_mingw:
        flags.append("--vdom-with-mingw")
    if args.vdom_only:
        flags.append("--vdom-only")
    if args.with_go_server:
        flags.append("--with-go-server")
    if args.go_server_only:
        flags.append("--go-server-only")
    if args.with_gpu:
        flags.append("--with-gpu")
    if args.gpu_only:
        flags.append("--gpu-only")

    # build_native.main() reads its flags straight out of sys.argv (see
    # nexoria/native/build_native.py), so keep it in sync with whatever
    # this subcommand's own argparse flags resolved to, regardless of
    # how the user actually typed them.
    old_argv = sys.argv[:]
    sys.argv = [old_argv[0]] + flags
    try:
        ui.rule("Building native tiers")
        build_native.main()
    except (RuntimeError, subprocess.CalledProcessError) as e:
        ui.error(str(e))
        sys.exit(1)
    except SystemExit as e:
        if e.code not in (0, None):
            raise
    finally:
        sys.argv = old_argv

    ui.success("Native build finished.")
    ui.info("Run `nexoria doctor` (or `nexoria native status`) to confirm which tiers are now active.")


def cmd_native_build(args: argparse.Namespace) -> None:
    _run_build_native(args)


def cmd_build_native_legacy(args: argparse.Namespace) -> None:
    ui.warn("`nexoria build-native` has moved to `nexoria native build` (kept here for compatibility).")
    _run_build_native(args)


_NATIVE_ARTIFACT_GLOBS = [
    "_nexoria_vdom_cpp*.so", "_nexoria_vdom_cpp*.pyd",
    "_nexoria_js*.so", "_nexoria_js*.pyd",
    "_nexoria_gpu_cpp*.so", "_nexoria_gpu_cpp*.pyd",
]


def _native_clean_targets() -> list[tuple[str, str]]:
    """Returns (label, path) pairs for everything `native clean` would
    remove. Deliberately scoped to build_native.py's own artifacts --
    never touches nexoria/_nexoria_rs (that's maturin/pip's job)."""
    from ..native import build_native as bn

    targets = [
        ("C++ VDOM build dir", os.path.join(bn.CPP_DIR, "vdom", "build")),
        ("JS engine build dir", os.path.join(bn.CPP_DIR, "jsengine", "build")),
        ("GPU tier build dir", os.path.join(bn.GPU_DIR, "build")),
        ("Rust safety-core target dir", os.path.join(bn.RUST_SAFETY_DIR, "target")),
        ("Go server binary dir", bn.BIN_DIR),
    ]
    for pattern in _NATIVE_ARTIFACT_GLOBS:
        for match in glob.glob(os.path.join(bn.PACKAGE_DIR, pattern)):
            targets.append((f"compiled module ({os.path.basename(match)})", match))
    return [(label, path) for label, path in targets if os.path.exists(path)]


def cmd_native_clean(args: argparse.Namespace) -> None:
    targets = _native_clean_targets()
    if not targets:
        ui.success("Nothing to clean -- no built native artifacts found.")
        return

    ui.status_table("Native artifacts to remove", [
        ("Will remove", [(label, None, path) for label, path in targets]),
    ])
    if not args.yes and not ui.confirm(f"Remove these {len(targets)} item(s)?", default=False):
        ui.info("Aborted -- nothing removed.")
        return

    with ui.spinner("Removing native build artifacts..."):
        for _label, path in targets:
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                try:
                    os.remove(path)
                except OSError:
                    pass
    ui.success(f"Removed {len(targets)} native artifact(s). Run `nexoria native build` to rebuild.")


def _add_native_build_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--vdom-with-mingw", action="store_true",
        help="build the C++ VDOM tier with mingw32-make (cpp/vdom/Makefile.mingw) instead of CMake+Ninja/MSVC",
    )
    p.add_argument(
        "--vdom-only", action="store_true",
        help="skip the embedded JS engine tier (it has no mingw32-make path yet, so it still needs CMake either way)",
    )
    p.add_argument(
        "--with-go-server", action="store_true",
        help="also build the optional Go native server tier -- needs Go on PATH",
    )
    p.add_argument(
        "--go-server-only", action="store_true",
        help="build ONLY the Go native server tier -- skips the Rust/C++ tiers and their toolchain checks entirely",
    )
    p.add_argument(
        "--with-gpu", action="store_true",
        help="also build the optional native GPU (CUDA) tier -- needs the CUDA Toolkit (nvcc) on PATH",
    )
    p.add_argument(
        "--gpu-only", action="store_true",
        help="build ONLY the native GPU (CUDA) tier -- skips the Rust/C++/Go tiers and their toolchain checks entirely",
    )


# --------------------------------------------------------------------------
# build-desktop / build-mobile
# --------------------------------------------------------------------------

def cmd_build_desktop(args: argparse.Namespace) -> None:
    from ..desktop import scaffold_electron
    with ui.spinner("Scaffolding Electron desktop shell..."):
        d = scaffold_electron(
            os.getcwd(), app_name=args.name, entry_file=args.entry, port=args.port, app_id=args.app_id,
        )
    ui.success(f"Electron project scaffolded at {d}")
    ui.key_values("Next steps", [
        ("1.", f"cd {os.path.relpath(d)}"),
        ("2.", "npm install"),
        ("3.", "npm start          # run it"),
        ("4.", "npm run dist       # package an installer"),
    ])


def cmd_build_mobile(args: argparse.Namespace) -> None:
    from ..mobile import scaffold_capacitor
    with ui.spinner("Scaffolding Capacitor mobile shell..."):
        d = scaffold_capacitor(
            os.getcwd(), app_name=args.name, app_id=args.app_id, server_url=args.server_url,
        )
    ui.success(f"Capacitor project scaffolded at {d}")
    if "example.com" in args.server_url:
        ui.warn("using the placeholder server URL -- pass --server-url pointing at your actual deployed backend before this is useful.")
    ui.key_values("Next steps", [
        ("1.", f"cd {os.path.relpath(d)}"),
        ("2.", "npm install"),
        ("3.", "npx cap add android   # and/or: npx cap add ios"),
        ("4.", "npx cap open android"),
    ])


# --------------------------------------------------------------------------
# argument parser / entry point
# --------------------------------------------------------------------------

class _NexoriaArgumentParser(argparse.ArgumentParser):
    """Routes argparse's own usage errors through the same styled
    error() helper every other failure in this CLI uses, instead of
    argparse's raw stderr dump."""

    def error(self, message: str) -> None:  # noqa: D102 - argparse override
        ui.error(message)
        self.print_usage(sys.stderr)
        sys.exit(2)


def _build_parser() -> argparse.ArgumentParser:
    parser = _NexoriaArgumentParser(prog="nexoria", description=f"{__framework_name__} CLI")
    parser.add_argument("--version", action="version", version=f"{__framework_name__} {__version__}")
    parser.add_argument("--no-color", action="store_true", help="disable colored/rich output")
    sub = parser.add_subparsers(dest="command")

    p_new = sub.add_parser("new", help="scaffold a new Nexoria project")
    p_new.add_argument("name")
    p_new.add_argument("--force", action="store_true", help="overwrite an existing directory without asking")
    p_new.set_defaults(func=cmd_new)

    p_dev = sub.add_parser("dev", help="run the dev server with hot reload")
    p_dev.add_argument("--module", default="app", help="Python module exposing a top-level `app` object (default: app)")
    p_dev.add_argument("--host", default="127.0.0.1")
    p_dev.add_argument("--port", type=int, default=8000)
    p_dev.set_defaults(func=cmd_dev)

    p_build = sub.add_parser("build", help="production build via the Node toolchain")
    p_build.set_defaults(func=cmd_build)

    p_doctor = sub.add_parser("doctor", help="full toolchain + native-tier status report")
    p_doctor.add_argument("--json", action="store_true", help="print machine-readable JSON instead of a table")
    p_doctor.set_defaults(func=cmd_doctor)

    p_native = sub.add_parser("native", help="inspect, build, or clean the optional native acceleration tiers")
    native_sub = p_native.add_subparsers(dest="native_command", required=True)

    p_native_status = native_sub.add_parser("status", help="show which native tiers are built/active")
    p_native_status.set_defaults(func=cmd_native_status)

    p_native_build = native_sub.add_parser("build", help="build the optional native tiers from source")
    _add_native_build_args(p_native_build)
    p_native_build.set_defaults(func=cmd_native_build)

    p_native_clean = native_sub.add_parser("clean", help="remove built native artifacts (compiled modules, build dirs)")
    p_native_clean.add_argument("-y", "--yes", action="store_true", help="remove without asking for confirmation")
    p_native_clean.set_defaults(func=cmd_native_clean)

    # Kept as a top-level alias for `nexoria native build` (this is
    # where the flags used to live before native's own subcommands
    # existed) so existing scripts/muscle-memory keep working.
    p_build_native = sub.add_parser(
        "build-native", help="deprecated alias for `nexoria native build`",
    )
    _add_native_build_args(p_build_native)
    p_build_native.set_defaults(func=cmd_build_native_legacy)

    p_build_desktop = sub.add_parser("build-desktop", help="scaffold an Electron desktop app wrapping this Nexoria app")
    p_build_desktop.add_argument("--name", default="Nexoria App")
    p_build_desktop.add_argument("--entry", default="app.py", help="your app's entry .py file")
    p_build_desktop.add_argument("--port", type=int, default=8000)
    p_build_desktop.add_argument("--app-id", default="com.pythonaibrain.nexoria-app")
    p_build_desktop.set_defaults(func=cmd_build_desktop)

    p_build_mobile = sub.add_parser("build-mobile", help="scaffold a Capacitor mobile app shell pointing at a deployed Nexoria backend")
    p_build_mobile.add_argument("--name", default="Nexoria App")
    p_build_mobile.add_argument("--app-id", default="com.pythonaibrain.nexoriaapp")
    p_build_mobile.add_argument(
        "--server-url", default="https://your-deployed-app.example.com",
        help="your deployed backend's URL -- REQUIRED for a real device to load anything",
    )
    p_build_mobile.set_defaults(func=cmd_build_mobile)

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if getattr(args, "no_color", False):
        ui.force_plain()

    if not args.command:
        ui.banner(__version__)
        parser.print_help()
        return

    try:
        args.func(args)
    except KeyboardInterrupt:
        ui.info()
        ui.warn("interrupted.")
        sys.exit(130)


if __name__ == "__main__":
    main()
