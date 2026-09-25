"""
nexoria.core.app
==================
The `App` object is the entry point of every Nexoria project. It is a
real ASGI application (built on Starlette, served by uvicorn), so it
runs on any standard Python ASGI host — no bespoke server required.

Responsibilities:
  * server-side render the matched route's Component to HTML on first load
  * serve the compiled client runtime + hydration payload
  * keep a live-reload WebSocket channel for state-driven re-renders
  * expose lifecycle hooks and pluggable middleware
"""

from __future__ import annotations
import json
import inspect
import os
import subprocess
import sys
import threading
import time
import uuid
from html import escape
from typing import Callable, Optional

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, Response, RedirectResponse
from starlette.routing import Route as StarletteRoute, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.staticfiles import StaticFiles

_RUNTIME_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "runtime")

# The framework's own mark (a falcon -- Pythonaibrain/Nexoria branding),
# shipped as a runtime asset and used as the favicon on every app unless
# App(favicon=...) is given a different path, or App(favicon=None) turns
# the icon off entirely (same on/off-by-default convention as
# `light_theme`). SVG is the primary <link rel="icon"> (crisp at any
# size, and every browser that still matters supports it); the PNG-as-.ico
# asset exists purely so the browser's unconditional GET /favicon.ico
# has something real to redirect to for chrome that bypasses the <link>
# tags (old OS tab bars, PWA install prompts, etc.).
DEFAULT_FAVICON_SVG = "/_nexoria/falcon-nexoria.svg"
DEFAULT_FAVICON_ICO = "/_nexoria/falcon-nexoria.ico"


def _find_free_port() -> int:
    """Reserve an ephemeral local port for the native server's backend
    uvicorn instance to bind to. Binds and immediately closes rather than
    holding the socket, so there's a (very short, practically-never-hit)
    race with something else grabbing the same port before uvicorn binds
    it moments later -- the standard, good-enough idiom for this."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_until(predicate: Callable[[], bool], timeout: float, interval: float = 0.05) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()

from .component import Component
from .element import Element
from ..render.html import render_to_html, render_document
from ..render.diff import diff
from ..router.router import Router
from ..middleware.base import Middleware
from ..native import goserver as _goserver
from ..threejs.scene import THREEJS_IMPORTS, THREEJS_ADAPTER_TAG
from ..gsap.animation import (
    GSAP_IMPORTS, GSAP_ADAPTER_TAG, gsap_plugin_imports, gsap_plugin_config_tag,
)
from ..chartjs.chart import CHARTJS_IMPORTS, CHARTJS_ADAPTER_TAG
from ..videojs.player import (
    VIDEOJS_CSS_TAG, VIDEOJS_CORE_SCRIPT_TAG, VIDEOJS_ADAPTER_TAG, VideoPlugin,
)
from ..aggrid.grid import AGGRID_IMPORTS, AGGRID_ADAPTER_TAG
from ..spline.scene import SPLINE_IMPORTS, SPLINE_ADAPTER_TAG
from ..vroid.avatar import VROID_IMPORTS, VROID_ADAPTER_TAG
from ..tailwind.config import TailwindConfig, tailwind_runtime_tag
from ..bootstrap.config import (
    BootstrapTheme, BOOTSTRAP_CSS_TAG, BOOTSTRAP_CORE_SCRIPT_TAG,
    BOOTSTRAP_ADAPTER_TAG, BOOTSTRAP_ICONS_TAG,
)
from ..babylonjs.scene import BABYLONJS_IMPORTS, BABYLONJS_ADAPTER_TAG
from ..iconify.icon import ICONIFY_SCRIPT_TAG
from ..shiki.highlighter import SHIKI_IMPORTS, SHIKI_ADAPTER_TAG
from ..qrcode.generator import QRCODE_SCRIPT_TAG, QRCODE_ADAPTER_TAG
from ..barcode.generator import BWIPJS_IMPORTS, BWIPJS_ADAPTER_TAG
from ..openlayers.map import OL_CSS_TAG, OL_CORE_SCRIPT_TAG, OL_ADAPTER_TAG
from ..webcam.capture import WEBCAM_IMPORTS, WEBCAM_ADAPTER_TAG
from ..style.theme import Theme, DEFAULT_THEME, LIGHT_THEME
from ..style.stylesheet import Stylesheet


class App:
    def __init__(
        self,
        name: str = "Nexoria App",
        router: Optional[Router] = None,
        static_dir: Optional[str] = None,
        threejs: bool = False,
        gsap: bool = False,
        gsap_plugins: Optional[list[str]] = None,
        chartjs: bool = False,
        videojs: bool = False,
        videojs_plugins: Optional[list[VideoPlugin]] = None,
        aggrid: bool = False,
        spline: bool = False,
        vroid: bool = False,
        tailwind: bool = False,
        tailwind_config: Optional[TailwindConfig] = None,
        tailwind_plugins: Optional[list[str]] = None,
        bootstrap: bool = False,
        bootstrap_theme: Optional[BootstrapTheme] = None,
        bootstrap_icons: bool = False,
        babylonjs: bool = False,
        iconify: bool = False,
        shiki: bool = False,
        qrcode: bool = False,
        barcode: bool = False,
        openlayers: bool = False,
        webcam: bool = False,
        debug: bool = False,
        theme: Optional[Theme] = None,
        light_theme: Optional[Theme] = LIGHT_THEME,
        styles: Optional[Stylesheet] = None,
        description: Optional[str] = None,
        favicon: Optional[str] = DEFAULT_FAVICON_SVG,
        og_image: Optional[str] = None,
    ):
        self.name = name
        self.router = router or Router()
        self.static_dir = static_dir
        self.threejs_enabled = threejs
        self.gsap_enabled = gsap
        # Validated eagerly (not lazily in _build_head) so a typo'd plugin
        # name fails fast at app construction, same spirit as GSAP itself
        # throwing on an unregistered plugin -- see GSAP_ALL_PLUGINS for
        # the full list (ScrollTrigger, Draggable, Flip, SplitText, ...).
        self.gsap_plugins = sorted(set(gsap_plugins or []))
        if self.gsap_plugins:
            gsap_plugin_imports(self.gsap_plugins)
        self.chartjs_enabled = chartjs
        self.videojs_enabled = videojs
        self.videojs_plugins = videojs_plugins or []
        self.aggrid_enabled = aggrid
        self.spline_enabled = spline
        self.vroid_enabled = vroid
        self.tailwind_enabled = tailwind
        self.tailwind_config = tailwind_config
        self.tailwind_plugins = tailwind_plugins or []
        self.bootstrap_enabled = bootstrap
        self.bootstrap_theme = bootstrap_theme
        self.bootstrap_icons_enabled = bootstrap_icons
        self.babylonjs_enabled = babylonjs
        self.iconify_enabled = iconify
        self.shiki_enabled = shiki
        self.qrcode_enabled = qrcode
        self.barcode_enabled = barcode
        self.openlayers_enabled = openlayers
        self.webcam_enabled = webcam
        self.debug = debug
        self.theme = theme or DEFAULT_THEME
        # A light-mode variant is on by default (nexoria.style.LIGHT_THEME):
        # every app gets a working, persisted dark/light toggle for free
        # (see runtime.js's theme init + `nx-theme-toggle` in base.css).
        # Pass light_theme=None to disable the toggle entirely.
        self.light_theme = light_theme
        self.styles = styles or Stylesheet()
        self.description = description
        self.favicon = favicon
        self.og_image = og_image
        self.middlewares: list[Middleware] = []
        self._sessions: dict[str, dict] = {}  # session_id -> {component, tree, handlers}
        self._asgi = self._build_asgi()

    # -- public API ---------------------------------------------------------
    def use(self, middleware: Middleware) -> "App":
        self.middlewares.append(middleware)
        return self

    def route(self, path: str, name: Optional[str] = None):
        """Decorator form: @app.route("/about")"""
        def wrapper(component_cls: type):
            self.router.add(path, component_cls, name=name)
            return component_cls
        return wrapper

    def run(self, host: str = "127.0.0.1", port: int = 8000, reload: bool = False,
            native: Optional[bool] = None, firewall: Optional[dict] = None) -> None:
        """
        Start the dev/production server.

        `native` controls whether the compiled Go edge server (see
        `nexoria build-native --with-go-server`, native/go/server/) fronts
        this app instead of talking to uvicorn directly. It serves static
        assets (static_dir, and Nexoria's own /_nexoria/* runtime files)
        straight from disk and reverse-proxies everything else -- SSR
        routes, the live WebSocket channel -- to a plain uvicorn instance
        running underneath it, unchanged:
          - None (default): use it automatically if a compiled binary is
            available; otherwise fall back to plain uvicorn.
          - True: try to use it; if it isn't built or fails to start for
            any reason, warn and fall back to plain uvicorn rather than
            raising -- this tier is always optional, never a hard
            requirement.
          - False: always run plain uvicorn (today's behavior,
            unchanged), regardless of whether a native binary exists.

        Never combined with `reload=True`: uvicorn's own autoreloader
        already re-execs a fresh subprocess on every file change, a
        different (and incompatible) process-management story than the
        native server's own long-lived backend thread -- reload always
        uses plain uvicorn, and `native` is ignored in that case.

        `reload=True` runs uvicorn's autoreloader, which needs the app
        passed as an "module:variable" import string rather than a live
        object (so it can re-import your code in a fresh subprocess after
        a file change). Nexoria detects that string for you automatically
        by inspecting the caller, so `app.run(reload=True)` just works
        from a normal `python app.py` — you never have to type
        `uvicorn app:app --reload` yourself.

        `firewall` only applies when the native server is actually in
        use (see `native` above) -- it's ignored for plain uvicorn,
        which has no firewall of its own (put one in front yourself,
        e.g. a reverse proxy or your platform's network rules, if you
        need one there). It configures the native server's built-in
        firewall (native/go/server/firewall.go), on by default with a
        conservative rate limit even if you pass nothing. Recognized
        keys, all optional (see `-firewall-*` in
        `nexoria-server -h` for the exact defaults/semantics each maps
        to): `enabled` (bool), `allow` / `deny` (str, comma-separated
        IPs/CIDRs), `rate_limit` (float, requests/sec/IP), `rate_burst`
        (int), `max_body_bytes` (int), `trust_x_forwarded_for` (bool) --
        only turn that last one on if the native server sits behind a
        reverse proxy you control that overwrites the header itself.

            app.run(firewall={
                "deny": "203.0.113.0/24",
                "rate_limit": 5, "rate_burst": 10,
            })
        """
        import uvicorn
        if reload:
            target, app_dir = self._resolve_import_string()
            uvicorn.run(target, host=host, port=port, reload=True,
                        app_dir=app_dir, reload_dirs=[app_dir])
            return

        use_native = native if native is not None else _goserver.is_available()
        if use_native and self._try_run_native(host, port, firewall or {}):
            return  # ran to normal completion behind the native server
        uvicorn.run(self._asgi, host=host, port=port)

    # Maps App.run(firewall={...}) dict keys to the native server's own
    # -firewall-* flag names, so callers write friendly Python kwarg
    # -style keys without needing to know the Go binary's exact flag
    # spelling. Kept as one small table here rather than duplicated
    # string-formatting logic scattered through _try_run_native.
    _FIREWALL_FLAG_NAMES = {
        "enabled": "-firewall",
        "allow": "-firewall-allow",
        "deny": "-firewall-deny",
        "rate_limit": "-firewall-rate-limit",
        "rate_burst": "-firewall-rate-burst",
        "max_body_bytes": "-firewall-max-body-bytes",
        "trust_x_forwarded_for": "-firewall-trust-x-forwarded-for",
    }

    def _firewall_args(self, firewall: dict) -> list[str]:
        """Translate an App.run(firewall={...}) dict into native server
        CLI args, e.g. {"deny": "1.2.3.0/24", "rate_limit": 5} ->
        ["-firewall-deny", "1.2.3.0/24", "-firewall-rate-limit", "5"].
        Unknown keys raise immediately -- silently ignoring a typo'd
        key (e.g. "rate-limit" instead of "rate_limit") would otherwise
        leave someone thinking a firewall rule is active when it never
        reached the native server at all.
        """
        args: list[str] = []
        for key, value in firewall.items():
            if key not in self._FIREWALL_FLAG_NAMES:
                raise ValueError(
                    f"App.run(firewall=...): unrecognized key {key!r} -- "
                    f"expected one of {sorted(self._FIREWALL_FLAG_NAMES)}"
                )
            flag_name = self._FIREWALL_FLAG_NAMES[key]
            if isinstance(value, bool):
                args += [flag_name, "true" if value else "false"]
            else:
                args += [flag_name, str(value)]
        return args

    def _try_run_native(self, host: str, port: int, firewall: Optional[dict] = None) -> bool:
        """
        Attempt to serve this app behind the compiled Go native server.

        Runs a plain uvicorn instance in a background thread as the
        actual backend (bound to a fresh local port, never exposed
        directly), then spawns the native binary in front of it and
        blocks until that process exits.

        Returns True if the native server actually took over serving
        (the caller must NOT also start plain uvicorn in that case) --
        including the normal case where it ran until Ctrl+C/shutdown.
        Returns False if it never got off the ground for any reason
        (binary missing, failed to spawn, exited immediately) --
        `run()` then falls back to plain uvicorn itself. Every failure
        path here prints why before returning False, since silently
        falling back would look like the app just started slower for
        no visible reason.
        """
        binary = _goserver.binary_path()
        if binary is None:
            print(
                "warning: native server requested but no compiled binary found -- "
                "build it with `nexoria build-native --with-go-server` (or "
                "--go-server-only). Falling back to plain uvicorn.",
                file=sys.stderr,
            )
            return False

        import uvicorn
        backend_port = _find_free_port()
        config = uvicorn.Config(
            self._asgi, host="127.0.0.1", port=backend_port,
            log_level=("info" if self.debug else "warning"),
        )
        backend = uvicorn.Server(config)
        backend_thread = threading.Thread(target=backend.run, daemon=True)
        backend_thread.start()
        if not _wait_until(lambda: backend.started, timeout=10.0):
            print(
                "warning: native server's backend (uvicorn) didn't start in "
                "time -- falling back to plain uvicorn.",
                file=sys.stderr,
            )
            backend.should_exit = True
            return False

        args = [
            binary,
            "-listen", f"{host}:{port}",
            "-backend", f"127.0.0.1:{backend_port}",
            "-name", self.name,
            "-runtime-dir", _RUNTIME_DIR,
        ]
        if self.static_dir:
            args += ["-static-dir", os.path.abspath(self.static_dir)]
        if firewall:
            args += self._firewall_args(firewall)

        try:
            proc = subprocess.Popen(args)
        except OSError as e:
            print(
                f"warning: failed to start the native server binary ({e}) -- "
                "falling back to plain uvicorn.",
                file=sys.stderr,
            )
            backend.should_exit = True
            return False

        # A real server binds its port and starts serving in well under
        # a second; if it's already exited by the time this short window
        # is up, that's a startup failure (bad flags, port already in
        # use, ...) rather than the process just being slow -- treat it
        # as one and fall back, instead of silently limping along with
        # no server actually listening on `port`.
        try:
            proc.wait(timeout=1.5)
        except subprocess.TimeoutExpired:
            pass  # still running -- looks like it started fine
        else:
            print(
                f"warning: native server exited immediately (code {proc.returncode}) "
                "-- falling back to plain uvicorn.",
                file=sys.stderr,
            )
            backend.should_exit = True
            return False

        print(f"Serving {self.name} via the native edge server at "
              f"http://{host}:{port} (backend: uvicorn on 127.0.0.1:{backend_port})")
        try:
            proc.wait()
        except KeyboardInterrupt:
            pass
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
            backend.should_exit = True
            backend_thread.join(timeout=5)
        return True

    def _resolve_import_string(self) -> tuple[str, str]:
        """
        Walk the call stack to find the module-level variable this App
        instance is bound to (conventionally `app = App(...)`), and
        return ("module_name:variable_name", containing_directory) so
        uvicorn's reloader can re-import it regardless of the process's
        current working directory.

        Walks every frame outward (not a fixed depth) so this works
        whether it's invoked from `run()` or called directly.
        """
        frame = inspect.currentframe()
        try:
            candidate = frame.f_back
            var_name = None
            module_file = None
            while candidate is not None:
                match = next(
                    (name for name, val in candidate.f_globals.items() if val is self),
                    None,
                )
                if match is not None:
                    var_name = match
                    module_file = candidate.f_globals.get("__file__")
                    break
                candidate = candidate.f_back

            if var_name is None or not module_file:
                raise RuntimeError(
                    "reload=True needs this App assigned to a top-level variable "
                    "in a real .py file, e.g.:\n\n"
                    "    app = App(...)\n"
                    "    app.run(reload=True)\n\n"
                    "Call .run(reload=False) instead if that isn't possible "
                    "(e.g. when running interactively)."
                )
            module_name = os.path.splitext(os.path.basename(module_file))[0]
            app_dir = os.path.dirname(os.path.abspath(module_file)) or "."
            return f"{module_name}:{var_name}", app_dir
        finally:
            del frame

    def _schedule_rerender(self, component: Component) -> None:
        """Hook called by Component/State on mutation (dev/live mode only)."""
        # In the full implementation this pushes a diff over the live
        # WebSocket channel keyed by session id. See _ws_endpoint below.
        pass

    @staticmethod
    def _collect_handlers(el: Optional[Element], out: dict[str, Callable]) -> None:
        """
        Walk a rendered Element tree and flatten every node's
        `on_click=`/`on_input=`/etc. callables into a single
        handler_id -> callable map. The differ only ever tells the
        client which handler_id fired; without this map the server has
        no way to find the actual Python callable to invoke.

        This must be rebuilt after every render (see _ws_endpoint) since
        handler ids are freshly generated each time an Element tree is
        built (see core/element.py's module-level id counter) -- the ids
        from the *previous* tree are not valid on the new one.
        """
        if el is None or el.is_text():
            return
        for event, callback in el._handlers.items():
            handler_id = el._handler_ids.get(event)
            if handler_id:
                out[handler_id] = callback
        for child in el.children:
            App._collect_handlers(child, out)

    # -- internals ------------------------------------------------------
    def _run_middlewares(self, request) -> Optional[HTMLResponse]:
        for mw in self.middlewares:
            result = mw.before_request(request)
            if result is not None:
                return result
        return None

    def _build_head(self, component_styles: Optional[Stylesheet] = None) -> str:
        """
        Compose everything that goes in <head> beyond <title>: theme
        tokens (dark + the optional light-mode override), base reset CSS,
        app-level + component-level Stylesheets, SEO meta/favicon/OG
        tags, and a single merged import map + adapter scripts for
        whichever of ThreeJS/GSAP/Chart.js/video.js/Bootstrap are
        enabled. Shared
        by the normal render path and the default 404 page so both get
        the same theming/SEO treatment.
        """
        merged_styles = self.styles.merge(component_styles) if isinstance(component_styles, Stylesheet) else self.styles
        head_parts = [
            '<link rel="stylesheet" href="/_nexoria/base.css">',
            f"<style>{self.theme.to_css_vars()}</style>",
        ]
        if self.light_theme is not None:
            # Emitted as an attribute-selector override so it only takes
            # effect once runtime.js (or the user) sets
            # documentElement[data-nx-theme="light"] -- see
            # nx-theme-toggle in base.css and the theme init in
            # runtime.js. Until then the plain :root tokens above apply,
            # so there's no flash-of-wrong-theme on first paint.
            light_css = self.light_theme.to_css_vars().replace(
                ":root", ':root[data-nx-theme="light"]', 1)
            head_parts.append(f"<style>{light_css}</style>")
        if merged_styles:
            head_parts.append(f"<style>{merged_styles.to_css()}</style>")
        if self.description:
            head_parts.append(f'<meta name="description" content="{escape(self.description, quote=True)}">')
            head_parts.append(f'<meta property="og:description" content="{escape(self.description, quote=True)}">')
        head_parts.append(f'<meta property="og:title" content="{escape(self.name, quote=True)}">')
        head_parts.append('<meta property="og:type" content="website">')
        if self.og_image:
            head_parts.append(f'<meta property="og:image" content="{escape(self.og_image, quote=True)}">')
        if self.favicon:
            if self.favicon == DEFAULT_FAVICON_SVG:
                # Framework default: pair the svg with the .ico fallback
                # for the (now rare) chrome that ignores/mishandles an
                # svg favicon.
                head_parts.append(f'<link rel="icon" type="image/svg+xml" href="{DEFAULT_FAVICON_SVG}">')
                head_parts.append(f'<link rel="icon" type="image/x-icon" href="{DEFAULT_FAVICON_ICO}">')
            else:
                head_parts.append(f'<link rel="icon" href="{escape(self.favicon, quote=True)}">')

        # Merge every enabled ESM-based integration's import-map entries
        # into a SINGLE `<script type="importmap">` tag -- browsers only
        # honor one per document, so ThreeJS/GSAP/Chart.js each emitting
        # their own would silently break whichever loaded second.
        import_map_entries: dict[str, str] = {}
        adapter_tags: list[str] = []
        if self.threejs_enabled:
            import_map_entries.update(THREEJS_IMPORTS)
            adapter_tags.append(THREEJS_ADAPTER_TAG)
        if self.gsap_enabled:
            import_map_entries.update(GSAP_IMPORTS)
            if self.gsap_plugins:
                # Plugin ESM entry points (e.g. "gsap/ScrollTrigger") join
                # the same shared import map; the config tag is the inert
                # data the adapter reads to know which of them to
                # dynamically import() and gsap.registerPlugin() before it
                # mounts any Tween/Timeline -- it must be present before
                # GSAP_ADAPTER_TAG executes, so it's appended first.
                import_map_entries.update(gsap_plugin_imports(self.gsap_plugins))
                adapter_tags.append(gsap_plugin_config_tag(self.gsap_plugins))
            adapter_tags.append(GSAP_ADAPTER_TAG)
        if self.chartjs_enabled:
            import_map_entries.update(CHARTJS_IMPORTS)
            adapter_tags.append(CHARTJS_ADAPTER_TAG)
        if self.aggrid_enabled:
            import_map_entries.update(AGGRID_IMPORTS)
            adapter_tags.append(AGGRID_ADAPTER_TAG)
        if self.spline_enabled:
            import_map_entries.update(SPLINE_IMPORTS)
            adapter_tags.append(SPLINE_ADAPTER_TAG)
        if self.vroid_enabled:
            # VROID_IMPORTS includes "three"/"three/" -- if threejs=True
            # is *also* set, dict.update just overwrites "three" with the
            # identical URL (both come from the same THREEJS_CDN
            # constant), so there's no conflict either way.
            import_map_entries.update(VROID_IMPORTS)
            adapter_tags.append(VROID_ADAPTER_TAG)
        if self.babylonjs_enabled:
            import_map_entries.update(BABYLONJS_IMPORTS)
            adapter_tags.append(BABYLONJS_ADAPTER_TAG)
        if self.shiki_enabled:
            import_map_entries.update(SHIKI_IMPORTS)
            adapter_tags.append(SHIKI_ADAPTER_TAG)
        if self.barcode_enabled:
            import_map_entries.update(BWIPJS_IMPORTS)
            adapter_tags.append(BWIPJS_ADAPTER_TAG)
        if self.webcam_enabled:
            import_map_entries.update(WEBCAM_IMPORTS)
            adapter_tags.append(WEBCAM_ADAPTER_TAG)
        if import_map_entries:
            head_parts.append(
                f'<script type="importmap">{json.dumps({"imports": import_map_entries})}</script>'
            )
        head_parts.extend(adapter_tags)

        if self.aggrid_enabled:
            from ..aggrid.grid import AGGRID_THEMES
            head_parts.append(f'<link rel="stylesheet" href="{AGGRID_THEMES.get("quartz")}">')

        # Iconify, QR code (qr-code-styling), and OpenLayers all ship as
        # classic global-attaching scripts (not ES modules with a clean
        # dependency-free entry point) -- see each module's own
        # docstring for why. Loaded independently of the shared import
        # map above, same reasoning as video.js.
        if self.iconify_enabled:
            head_parts.append(ICONIFY_SCRIPT_TAG)
        if self.qrcode_enabled:
            head_parts.append(QRCODE_SCRIPT_TAG)
            head_parts.append(QRCODE_ADAPTER_TAG)
        if self.openlayers_enabled:
            head_parts.append(OL_CSS_TAG)
            head_parts.append(OL_CORE_SCRIPT_TAG)
            head_parts.append(OL_ADAPTER_TAG)

        # video.js doesn't participate in the import map above -- it
        # ships as a classic, fully self-contained UMD bundle instead of
        # an ES module with a clean dependency-free entry point (see
        # nexoria/videojs/player.py's docstring for why), so it brings
        # its own CSS link + <script> tags. Any App(videojs_plugins=[...])
        # scripts load between the core bundle and our adapter -- they
        # must be present before the adapter tries to activate them on
        # a player, but need video.js's own global to exist first.
        if self.videojs_enabled:
            head_parts.append(VIDEOJS_CSS_TAG)
            head_parts.append(VIDEOJS_CORE_SCRIPT_TAG)
            for plugin in self.videojs_plugins:
                head_parts.append(f'<script src="{escape(plugin.src, quote=True)}"></script>')
            head_parts.append(VIDEOJS_ADAPTER_TAG)

        # Bootstrap doesn't participate in the shared import map above
        # either, same reasoning as video.js: it ships as a classic,
        # fully self-contained UMD bundle (Popper.js already inlined in
        # the "bundle" build), not an ES module. CSS first, then the
        # optional CSS-variable theme override (must come after the core
        # stylesheet to win the cascade), then the core script, then
        # Bootstrap Icons (a separate stylesheet, independent of theming),
        # then our adapter -- which needs the `bootstrap` global to
        # already exist.
        if self.bootstrap_enabled:
            head_parts.append(BOOTSTRAP_CSS_TAG)
            if self.bootstrap_theme is not None:
                theme_tag = self.bootstrap_theme.to_style_tag()
                if theme_tag:
                    head_parts.append(theme_tag)
            head_parts.append(BOOTSTRAP_CORE_SCRIPT_TAG)
            if self.bootstrap_icons_enabled:
                head_parts.append(BOOTSTRAP_ICONS_TAG)
            head_parts.append(BOOTSTRAP_ADAPTER_TAG)

        # Tailwind's Play CDN (prototyping-only per Tailwind's own
        # guidance -- see nexoria/tailwind/config.py's module docstring
        # for the production alternative). Independent of the shared
        # import map above: it's a classic script, not an ES module.
        if self.tailwind_enabled:
            head_parts.append(tailwind_runtime_tag(self.tailwind_config, self.tailwind_plugins))

        return "\n".join(head_parts)

    def _default_not_found_html(self) -> str:
        """A themed, styled 404 page -- used unless the app registers its
        own via `router.set_not_found(SomeComponent)`."""
        body = (
            '<div class="nx-container">'
            '<div class="nx-card nx-center" style="flex-direction:column;gap:12px;text-align:center;">'
            '<span class="nx-badge">404</span>'
            '<h1>Page not found</h1>'
            '<p style="color:var(--nx-text-muted)">'
            "The page you're looking for doesn't exist or has moved."
            '</p>'
            '<a href="/" class="nx-btn">Go home</a>'
            '</div></div>'
        )
        return render_document(
            body_html=body,
            hydration_script="null",
            title=f"Not found · {self.name}",
            extra_head=self._build_head(),
        )

    async def _http_endpoint(self, request):
        early = self._run_middlewares(request)
        if early is not None:
            return early

        path = request.url.path
        component = self.router.resolve(path, **dict(request.query_params))
        if component is None:
            return HTMLResponse(self._default_not_found_html(), status_code=404)

        tree = component.render()
        body_html = render_to_html(tree)

        # Register a session server-side so the live WebSocket channel
        # can find this exact rendered component/tree/handler-map again
        # when a click comes in. The session id is handed to the client
        # via the hydration payload below -- it must originate here, not
        # be invented client-side, or the server has no way to look
        # anything up when an event arrives.
        session_id = uuid.uuid4().hex
        handlers: dict[str, Callable] = {}
        self._collect_handlers(tree, handlers)
        self._sessions[session_id] = {"component": component, "tree": tree, "handlers": handlers}

        component_styles = getattr(component, "styles", None)
        extra_head = self._build_head(component_styles)

        hydration_payload = json.dumps({
            "route": path,
            "tree": tree.to_dict(),
            "component": component.__class__.__name__,
            "session": session_id,
        })
        html = render_document(
            body_html=body_html,
            hydration_script=hydration_payload,
            title=self.name,
            extra_head=extra_head,
        )
        return HTMLResponse(html)

    async def _ws_endpoint(self, websocket: WebSocket) -> None:
        """
        Live channel used in dev mode (and optionally production) to push
        diff patches to the client instead of full page reloads whenever
        server-authoritative state changes.
        """
        await websocket.accept()
        current_session_id: Optional[str] = None
        try:
            while True:
                msg = await websocket.receive_json()
                handler_id = msg.get("handler_id")
                session_id = msg.get("session")
                current_session_id = session_id
                session = self._sessions.get(session_id)
                if session is None:
                    # Unknown/expired session (e.g. server restarted since
                    # this page was loaded) -- nothing to do until the
                    # page is reloaded and gets a fresh one.
                    continue
                component: Component = session["component"]
                old_tree: Element = session["tree"]
                handler = session["handlers"].get(handler_id)
                if handler:
                    result = handler(msg.get("payload"))
                    if inspect.isawaitable(result):
                        await result
                new_tree = component.render()
                patches = diff(old_tree, new_tree)
                new_handlers: dict[str, Callable] = {}
                self._collect_handlers(new_tree, new_handlers)
                session["tree"] = new_tree
                session["handlers"] = new_handlers
                await websocket.send_json({
                    "type": "patch",
                    "patches": [p.to_dict() for p in patches],
                })
        except WebSocketDisconnect:
            pass  # normal: page navigated away/refreshed/closed
        except Exception:
            if self.debug:
                raise
        finally:
            if current_session_id is not None:
                self._sessions.pop(current_session_id, None)

    async def _health(self, request):
        return JSONResponse({"status": "ok", "framework": "nexoria"})

    async def _favicon(self, request):
        """
        Browsers request /favicon.ico unconditionally, regardless of any
        <link rel="icon"> tag. Without this, every page load logs a
        noisy 404 even when the app works perfectly. Redirects to
        whatever App(favicon=...) resolves to (the framework's own
        falcon mark by default, DEFAULT_FAVICON_SVG -- redirected to its
        .ico sibling here since this route is specifically answering a
        *.ico* request); App(favicon=None) means no icon at all, so this
        returns an empty 204 (a deliberate no-icon response, not a
        missing-route error).
        """
        if self.favicon:
            target = DEFAULT_FAVICON_ICO if self.favicon == DEFAULT_FAVICON_SVG else self.favicon
            return RedirectResponse(target)
        return Response(status_code=204)

    async def _serve_runtime_asset(self, request):
        filename = request.path_params["filename"]
        safe = os.path.basename(filename)
        path = os.path.join(_RUNTIME_DIR, safe)
        if not os.path.isfile(path):
            return Response(status_code=404)
        with open(path, "rb") as f:
            content = f.read()
        media_type = "application/javascript" if safe.endswith(".js") else (
            "text/css" if safe.endswith(".css") else (
            "image/svg+xml" if safe.endswith(".svg") else (
            "image/x-icon" if safe.endswith(".ico") else "text/plain"
        )))
        return Response(content, media_type=media_type)

    def _build_asgi(self) -> Starlette:
        routes = [
            WebSocketRoute("/_nexoria/live", self._ws_endpoint),
            StarletteRoute("/_nexoria/health", self._health),
            StarletteRoute("/favicon.ico", self._favicon),
            StarletteRoute("/_nexoria/{filename}", self._serve_runtime_asset, methods=["GET"]),
            StarletteRoute("/{path:path}", self._http_endpoint, methods=["GET"]),
        ]
        app = Starlette(debug=self.debug, routes=routes)
        if self.static_dir:
            app.mount("/static", StaticFiles(directory=self.static_dir), name="static")
        return app

    # ASGI protocol passthrough so `App` instances are directly servable
    async def __call__(self, scope, receive, send):
        await self._asgi(scope, receive, send)
