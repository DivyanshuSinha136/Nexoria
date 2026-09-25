# `nexoria.videojs`

> Declare a video.js player in Python, with theming, control-bar selection, captions and plugins.

| | |
|---|---|
| **Import** | `from nexoria.videojs import VideoPlayer, Track, VideoTheme, ControlBar, VideoPlugin` |
| **Enabled by** | `App(videojs=True)`; site-wide plugins via `App(videojs_plugins=[VideoPlugin(...)])` |
| **Library** | video.js 8.24.0 — classic UMD script + CSS from unpkg (not the import map: its ES build has a deep dependency chain) |
| **Adapter** | `runtime/videojs-adapter.js` |

```python
from nexoria.videojs import VideoPlayer, Track, VideoTheme, ControlBar

player = VideoPlayer(
    sources=["/static/demo.webm", "/static/demo.mp4"],     # first playable wins
    tracks=[Track("/static/en.vtt", label="English", default=True)],
    poster="/static/poster.jpg",
    playback_rates=[0.5, 1, 1.5, 2],
    theme=VideoTheme(accent="#ff6b35"),
    control_bar=ControlBar(children=["playToggle", "progressControl", "fullscreenToggle"]),
)
el("div", player.to_element(), player.theme_element())     # theme_element() is None when unused – safe to include
```

- Sources are URL strings (MIME guessed from `.mp4 .m4v .webm .ogg .ogv .mov .m3u8 .mpd`) or `{"src":…, "type":…}` dicts.
- `VideoPlayer` needs `src=` or `sources=` (raises `ValueError` otherwise). `player_id` is auto-generated (`nx-video-xxxxxxxx`) unless supplied; `to_element(player_id=…)` overrides it.
- `VideoTheme.from_theme(DEFAULT_THEME)` derives a skin from a Nexoria `Theme`. It is scoped to one player by id.
- `options` merges into `videojs(el, options)`; `active_plugins={"myPlugin": {...}}` activates a loaded plugin on that player (name must match the property the plugin registers).
- Client API: `window.__nexoria__.videojs.get/play/pause/dispose(id)`; DOM event `nexoria:videojs:ready`.

## API reference

### Classes

#### `class VideoPlayer(src: Optional[str] = None, sources: Optional[list[Union[str, dict]]] = None, tracks: list[Track] = ..., poster: Optional[str] = None, controls: bool = True, autoplay: bool = False, loop: bool = False, muted: bool = False, fluid: bool = True, aspect_ratio: Optional[str] = None, playback_rates: Optional[list[float]] = None, width: Optional[int] = None, height: Optional[int] = None, preload: str = 'auto', control_bar: Optional[ControlBar] = None, active_plugins: dict[str, dict] = ..., theme: Optional[VideoTheme] = None, custom_css: Optional[str] = None, player_id: Optional[str] = None, options: dict[str, Any] = ...) -> None`

A video.js player.

Multiple quality/format sources (video.js/the browser picks the first playable one) and captions are both first-class.

Each source may be a plain URL string (MIME type is guessed from the file extension -- .mp4/.webm/.ogg/.mov/.m3u8/.mpd all recognized) or a `{"src": ..., "type": ...}` dict if you need to specify the type explicitly (e.g. a URL with no extension).

Customization.

If `theme` (or `custom_css`) is set, include `.theme_element()` alongside `.to_element()` -- it emits the actual `<style>` tag.

`options` is passed through to `videojs(el, options)` verbatim, merged in after every field above, for anything not covered directly.

- **`.theme_element()`** — Emits the `<style>` tag for `theme=`/`custom_css=`. Returns `None` if neither is set (nothing to render) -- safe to include unconditionally: `el("div", player.to_element(), player.theme_element())` works whether or not there's a theme, since `el()` skips `None` children.
- **`.to_dict() -> dict`**
- **`.to_element(player_id: Optional[str] = None)`**

#### `class Track(src: str, kind: str = 'captions', srclang: str = 'en', label: Optional[str] = None, default: bool = False) -> None`

A subtitle/caption/description track (video.js/HTML5 `<track>`).

Track("/static/en.vtt", kind="captions", srclang="en", label="English", default=True)

- **`.to_dict() -> dict`**

#### `class VideoTheme(accent: str = '#6366f1', control_bar_bg: str = 'rgba(20, 20, 31, 0.75)', text: str = '#ffffff', big_play_button_bg: Optional[str] = None, border_radius: str = '8px') -> None`

Re-skins video.js's default black UI to match your app, expressed as a handful of intent-based colors rather than raw CSS selectors. Scoped to one player (via its id), so different players on the same page can have different themes.

`VideoTheme.from_theme(app_theme)` derives one from a `nexoria.style.Theme` (the same tokens your app's own dark/light theme uses), so the player's controls automatically match.

- **`.from_theme(theme: Any) -> 'VideoTheme'`** — Derive a player skin from a `nexoria.style.Theme` instance.
- **`.to_css(scope_id: str) -> str`**

#### `class ControlBar(children: Optional[list[str]] = None, extra: dict[str, Any] = ...) -> None`

Chooses which control-bar buttons appear, and in what order (maps directly onto video.js's own `controlBar.children` option).

`extra` passes any other `controlBar` sub-option through verbatim (e.g. `{"volumePanel": {"inline": False}}`).

- **`.to_dict() -> dict`**

#### `class VideoPlugin(name: str, src: str) -> None`

A real video.js plugin, loaded once site-wide via `App(videojs_plugins=[VideoPlugin(...)])` and activated per-player via `VideoPlayer(active_plugins={name: {...options...}})`.

`name` must match the property the plugin registers on the player (check the plugin's own docs) -- that's what `VideoPlayer.active_plugins` keys reference.

### Constants

| Name | Value |
|---|---|
| `VIDEOJS_JS_CDN` | `'https://unpkg.com/video.js@8.24.0/dist/video.min.js'` |
| `VIDEOJS_CSS_CDN` | `'https://unpkg.com/video.js@8.24.0/dist/video-js.min.css'` |
| `VIDEOJS_CSS_TAG` | `'<link rel="stylesheet" href="https://unpkg.com/video.js@8.24.0/dist/video-js.min.css">'` |
| `VIDEOJS_CORE_SCRIPT_TAG` | `'<script src="https://unpkg.com/video.js@8.24.0/dist/video.min.js"></script>'` |
| `VIDEOJS_ADAPTER_TAG` | `'<script src="/_nexoria/videojs-adapter.js" defer></script>'` |
| `VIDEOJS_RUNTIME_TAG` | `'<link rel="stylesheet" href="https://unpkg.com/video.js@8.24.0/dist/video-js.min.css">\n<script src="https://unpkg.com/video.js@8.24.0/dist/video.min.js"></script>\n<script src="/_nexoria/videojs-adapter.js" defer></script>'` |
