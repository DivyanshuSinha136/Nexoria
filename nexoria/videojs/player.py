"""
nexoria.videojs.player
=========================
Optional video player layer. Describe a video.js player declaratively
in Python; the client adapter (`runtime/videojs-adapter.js`, loaded
only when `App(videojs=True)` is set) instantiates a real video.js
player against a `<video>` element.

Unlike ThreeJS/GSAP/Chart.js, video.js's own ES module build has a
long chain of real external dependencies (HLS/DASH streaming support,
its own XHR/font/VTT packages, ...) -- a clean single-URL import map
isn't realistic for it the way it is for the others. video.js instead
ships an official, fully self-contained UMD bundle (everything inlined)
for exactly this "just drop in a script tag" use case, so that's what
Nexoria uses here: a classic `<script>` (not an ES module) attaching a
global `videojs` function, plus its companion CSS file. Both are still
pulled from CDN -- never a Python dependency.

Customization is three separate, composable pieces:
  * `VideoTheme`  -- re-skin the player's default black UI (big play
    button, control bar, progress/volume fill) to match your app.
  * `ControlBar`  -- choose which controls appear, and in what order.
  * `VideoPlugin` -- load a real video.js plugin script site-wide
    (`App(videojs_plugins=[...])`) and activate it on a specific
    player (`VideoPlayer(active_plugins={...})`).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Union
import json
import uuid

VIDEOJS_JS_CDN = "https://unpkg.com/video.js@8.24.0/dist/video.min.js"
VIDEOJS_CSS_CDN = "https://unpkg.com/video.js@8.24.0/dist/video-js.min.css"

# Split into named pieces (rather than one fixed string) so App can
# insert plugin <script> tags between the core bundle and the adapter
# -- plugins must load after video.js itself but before our adapter
# tries to activate them on a player.
VIDEOJS_CSS_TAG = f'<link rel="stylesheet" href="{VIDEOJS_CSS_CDN}">'
VIDEOJS_CORE_SCRIPT_TAG = f'<script src="{VIDEOJS_JS_CDN}"></script>'
VIDEOJS_ADAPTER_TAG = '<script src="/_nexoria/videojs-adapter.js" defer></script>'
# Kept for anyone importing this directly with no plugins.
VIDEOJS_RUNTIME_TAG = f"{VIDEOJS_CSS_TAG}\n{VIDEOJS_CORE_SCRIPT_TAG}\n{VIDEOJS_ADAPTER_TAG}"

_MIME_BY_EXTENSION = {
    ".mp4": "video/mp4",
    ".m4v": "video/mp4",
    ".webm": "video/webm",
    ".ogg": "video/ogg",
    ".ogv": "video/ogg",
    ".mov": "video/quicktime",
    ".m3u8": "application/x-mpegURL",   # HLS
    ".mpd": "application/dash+xml",     # MPEG-DASH
}


def _guess_mime_type(src: str) -> Optional[str]:
    lowered = src.lower().split("?")[0]
    for ext, mime in _MIME_BY_EXTENSION.items():
        if lowered.endswith(ext):
            return mime
    return None


@dataclass
class Track:
    """
    A subtitle/caption/description track (video.js/HTML5 `<track>`).

        Track("/static/en.vtt", kind="captions", srclang="en", label="English", default=True)
    """
    src: str
    kind: str = "captions"  # "captions" | "subtitles" | "descriptions" | "chapters" | "metadata"
    srclang: str = "en"
    label: Optional[str] = None
    default: bool = False

    def to_dict(self) -> dict:
        return {
            "src": self.src, "kind": self.kind, "srclang": self.srclang,
            "label": self.label or self.srclang, "default": self.default,
        }


@dataclass
class VideoTheme:
    """
    Re-skins video.js's default black UI to match your app, expressed
    as a handful of intent-based colors rather than raw CSS selectors.
    Scoped to one player (via its id), so different players on the
    same page can have different themes.

        player = VideoPlayer("/static/demo.mp4", theme=VideoTheme(accent="#ff6b35"))
        el("div", player.to_element(), player.theme_element())  # both required

    `VideoTheme.from_theme(app_theme)` derives one from a
    `nexoria.style.Theme` (the same tokens your app's own dark/light
    theme uses), so the player's controls automatically match:

        VideoTheme.from_theme(DEFAULT_THEME)
    """
    accent: str = "#6366f1"                       # progress bar, volume fill
    control_bar_bg: str = "rgba(20, 20, 31, 0.75)"
    text: str = "#ffffff"
    big_play_button_bg: Optional[str] = None       # defaults to `accent`
    border_radius: str = "8px"

    @classmethod
    def from_theme(cls, theme: Any) -> "VideoTheme":
        """Derive a player skin from a `nexoria.style.Theme` instance."""
        return cls(
            accent=theme.primary,
            control_bar_bg=theme.surface_alt,
            text=theme.text,
            big_play_button_bg=theme.primary,
            border_radius=theme.radius_sm,
        )

    def to_css(self, scope_id: str) -> str:
        scope = f"#{scope_id}"
        big_play_bg = self.big_play_button_bg or self.accent
        return (
            f"{scope}.video-js .vjs-big-play-button {{ "
            f"background-color: {big_play_bg}; border-radius: {self.border_radius}; border: none; }}\n"
            f"{scope}.video-js .vjs-control-bar {{ background-color: {self.control_bar_bg}; }}\n"
            f"{scope}.video-js .vjs-play-progress, {scope}.video-js .vjs-volume-level {{ "
            f"background-color: {self.accent}; }}\n"
            f"{scope}.video-js .vjs-control, {scope}.video-js .vjs-menu-button .vjs-menu-content {{ "
            f"color: {self.text}; }}\n"
        )


@dataclass
class ControlBar:
    """
    Chooses which control-bar buttons appear, and in what order (maps
    directly onto video.js's own `controlBar.children` option).

        ControlBar(children=["playToggle", "progressControl", "volumePanel", "fullscreenToggle"])

    `extra` passes any other `controlBar` sub-option through verbatim
    (e.g. `{"volumePanel": {"inline": False}}`).
    """
    children: Optional[list[str]] = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = dict(self.extra)
        if self.children is not None:
            d["children"] = self.children
        return d


@dataclass
class VideoPlugin:
    """
    A real video.js plugin, loaded once site-wide via
    `App(videojs_plugins=[VideoPlugin(...)])` and activated per-player
    via `VideoPlayer(active_plugins={name: {...options...}})`.

        # loaded once, app-level:
        app = App(..., videojs=True, videojs_plugins=[
            VideoPlugin("videoJsResolutionSwitcher", "https://cdn.example.com/resolution-switcher.js"),
        ])
        # activated per-player, with this player's own options:
        player = VideoPlayer(..., active_plugins={"videoJsResolutionSwitcher": {"default": "720p"}})

    `name` must match the property the plugin registers on the player
    (check the plugin's own docs) -- that's what
    `VideoPlayer.active_plugins` keys reference.
    """
    name: str
    src: str


@dataclass
class VideoPlayer:
    """
    A video.js player.

        VideoPlayer("/static/demo.mp4", poster="/static/poster.jpg")

    Multiple quality/format sources (video.js/the browser picks the
    first playable one) and captions are both first-class:

        VideoPlayer(
            sources=["/static/demo.webm", "/static/demo.mp4"],
            tracks=[Track("/static/en.vtt", label="English", default=True)],
            fluid=True,
            playback_rates=[0.5, 1, 1.5, 2],
        )

    Each source may be a plain URL string (MIME type is guessed from
    the file extension -- .mp4/.webm/.ogg/.mov/.m3u8/.mpd all
    recognized) or a `{"src": ..., "type": ...}` dict if you need to
    specify the type explicitly (e.g. a URL with no extension).

    Customization:

        VideoPlayer(
            "/static/demo.mp4",
            theme=VideoTheme(accent="#ff6b35"),           # re-skin controls
            control_bar=ControlBar(children=["playToggle", "progressControl"]),
            active_plugins={"myPlugin": {"opt": 1}},        # see VideoPlugin
        )

    If `theme` (or `custom_css`) is set, include `.theme_element()`
    alongside `.to_element()` -- it emits the actual `<style>` tag:

        el("div", player.to_element(), player.theme_element())

    `options` is passed through to `videojs(el, options)` verbatim,
    merged in after every field above, for anything not covered
    directly.
    """
    src: Optional[str] = None
    sources: Optional[list[Union[str, dict]]] = None
    tracks: list[Track] = field(default_factory=list)
    poster: Optional[str] = None
    controls: bool = True
    autoplay: bool = False
    loop: bool = False
    muted: bool = False
    fluid: bool = True
    aspect_ratio: Optional[str] = None          # e.g. "16:9"
    playback_rates: Optional[list[float]] = None  # e.g. [0.5, 1, 1.5, 2]
    width: Optional[int] = None
    height: Optional[int] = None
    preload: str = "auto"  # "auto" | "metadata" | "none"
    control_bar: Optional[ControlBar] = None
    active_plugins: dict[str, dict] = field(default_factory=dict)
    theme: Optional[VideoTheme] = None
    custom_css: Optional[str] = None
    player_id: Optional[str] = None
    options: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.src and not self.sources:
            raise ValueError("VideoPlayer needs either `src=` or `sources=`")
        if self.player_id is None:
            self.player_id = f"nx-video-{uuid.uuid4().hex[:8]}"

    def _resolved_sources(self) -> list[dict]:
        raw = self.sources if self.sources is not None else [self.src]
        resolved = []
        for item in raw:
            if isinstance(item, dict):
                resolved.append({"src": item["src"], "type": item.get("type") or _guess_mime_type(item["src"])})
            else:
                resolved.append({"src": item, "type": _guess_mime_type(item)})
        return resolved

    def to_dict(self) -> dict:
        merged_options = dict(self.options)
        if self.control_bar is not None:
            merged_options["controlBar"] = self.control_bar.to_dict()
        return {
            "sources": self._resolved_sources(),
            "tracks": [t.to_dict() for t in self.tracks],
            "poster": self.poster,
            "controls": self.controls,
            "autoplay": self.autoplay,
            "loop": self.loop,
            "muted": self.muted,
            "fluid": self.fluid,
            "aspectRatio": self.aspect_ratio,
            "playbackRates": self.playback_rates,
            "width": self.width,
            "height": self.height,
            "preload": self.preload,
            "options": merged_options,
            "activePlugins": self.active_plugins,
        }

    def to_element(self, player_id: Optional[str] = None):
        from ..core.element import el
        if player_id is not None:
            self.player_id = player_id
        return el(
            "video",
            id=self.player_id,
            **{
                "class": "video-js nx-videojs-player",
                "data-nx-videojs": json.dumps(self.to_dict()),
            },
            controls=self.controls,
            preload=self.preload,
        )

    def theme_element(self):
        """
        Emits the `<style>` tag for `theme=`/`custom_css=`. Returns
        `None` if neither is set (nothing to render) -- safe to include
        unconditionally: `el("div", player.to_element(), player.theme_element())`
        works whether or not there's a theme, since `el()` skips `None`
        children.
        """
        if self.theme is None and self.custom_css is None:
            return None
        from ..core.element import el
        parts = []
        if self.theme is not None:
            parts.append(self.theme.to_css(self.player_id))
        if self.custom_css:
            parts.append(self.custom_css)
        return el("style", "\n".join(parts))
