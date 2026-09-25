"""
nexoria.gsap.animation
=========================
Optional animation layer. Describe GSAP tweens/timelines declaratively
in Python; Nexoria serializes them to a small JSON spec that the client
runtime's GSAP adapter (`runtime/gsap-adapter.js`, loaded only when
`App(gsap=True)` or an Animation is used) turns into real `gsap.to()` /
`gsap.timeline()` calls against the actual rendered DOM.

GSAP animates real elements already on the page (CSS selectors), so
unlike the ThreeJS scene (which owns a `<canvas>` it draws into), an
Animation here targets ordinary `el(...)` nodes elsewhere in your
render() output -- give them a `class_`/`id` to target and reference
that selector in the Tween. GSAP itself is pulled from CDN (never a
Python dependency), same approach as `nexoria.threejs`.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Union
import json

GSAP_VERSION = "3.15.0"
GSAP_CDN = f"https://unpkg.com/gsap@{GSAP_VERSION}/index.js"
# Split for the same reason as THREEJS_IMPORTS/THREEJS_ADAPTER_TAG (see
# nexoria/threejs/scene.py) -- App._build_head() merges these into one
# shared import map across every enabled ESM-based integration.
GSAP_IMPORTS = {"gsap": GSAP_CDN}
GSAP_ADAPTER_TAG = '<script src="/_nexoria/gsap-adapter.js" type="module" defer></script>'
GSAP_RUNTIME_TAG = (
    f'<script type="importmap">{{"imports": {{"gsap": "{GSAP_CDN}"}}}}</script>\n'
    f'{GSAP_ADAPTER_TAG}'
)

# --------------------------------------------------------------------------
# GSAP plugins
# --------------------------------------------------------------------------
# Every plugin GSAP ships (all free to use since GSAP's 2025 relicense --
# there's no more "Club GSAP" split, so this is the complete set, not just
# the historically-free ones). Each is published as its own ESM entry point
# under the same `gsap` package on unpkg, e.g.
# https://unpkg.com/gsap@3.15.0/ScrollTrigger.js -- enabling a plugin adds a
# `"gsap/<Name>": "<that URL>"` entry to the shared import map (see
# App._build_head()) so `import { ScrollTrigger } from "gsap/ScrollTrigger"`
# resolves in the browser, and tells the client adapter (via an inert JSON
# marker, GSAP_PLUGIN_CONFIG_ID) which plugins to dynamically import and
# hand to `gsap.registerPlugin()` before it mounts any Tween/Timeline --
# so a Tween's `vars` can freely use plugin-specific properties
# (`scrollTrigger={...}`, `motionPath={...}`, `drawSVG=...`, etc.) the
# moment that plugin's name is turned on.
GSAP_PLUGIN_CDN_BASE = f"https://unpkg.com/gsap@{GSAP_VERSION}"

GSAP_ALL_PLUGINS = (
    "ScrollTrigger",
    "ScrollToPlugin",
    "ScrollSmoother",
    "Draggable",
    "Flip",
    "Observer",
    "MotionPathPlugin",
    "MotionPathHelper",
    "DrawSVGPlugin",
    "MorphSVGPlugin",
    "Physics2DPlugin",
    "PhysicsPropsPlugin",
    "InertiaPlugin",
    "PixiPlugin",
    "EaselPlugin",
    "TextPlugin",
    "SplitText",
    "ScrambleTextPlugin",
    "CustomEase",
    "CustomBounce",
    "CustomWiggle",
    "GSDevTools",
)

GSAP_PLUGIN_CONFIG_ID = "nx-gsap-plugins"


def _validate_plugins(plugins) -> list[str]:
    names = sorted(set(plugins))
    unknown = [p for p in names if p not in GSAP_ALL_PLUGINS]
    if unknown:
        raise ValueError(
            f"Unknown GSAP plugin(s): {', '.join(unknown)}. "
            f"Available: {', '.join(GSAP_ALL_PLUGINS)}"
        )
    return names


def gsap_plugin_imports(plugins) -> dict[str, str]:
    """
    Import-map entries for the given plugin names, e.g. ``["ScrollTrigger"]``
    -> ``{"gsap/ScrollTrigger": "https://unpkg.com/gsap@.../ScrollTrigger.js"}``.
    Merged into the app-wide import map alongside the core ``"gsap"`` entry.
    Raises ``ValueError`` on an unrecognized plugin name (see
    ``GSAP_ALL_PLUGINS``).
    """
    names = _validate_plugins(plugins)
    return {f"gsap/{name}": f"{GSAP_PLUGIN_CDN_BASE}/{name}.js" for name in names}


def gsap_plugin_config_tag(plugins) -> str:
    """
    Inert ``<script type="application/json">`` marker listing the enabled
    plugin names, read by the client adapter on load so it knows which
    modules to dynamically `import()` and `gsap.registerPlugin()` before
    mounting any animation. Empty string (no tag) if there are no plugins.
    """
    names = _validate_plugins(plugins)
    if not names:
        return ""
    return (
        f'<script type="application/json" id="{GSAP_PLUGIN_CONFIG_ID}">'
        f'{json.dumps(names)}</script>'
    )


@dataclass
class Tween:
    """
    One GSAP tween. `target` is a CSS selector matching element(s)
    already rendered elsewhere on the page (give them a `class_`/`id`
    in `el(...)` to target them). Extra keyword args become GSAP "vars"
    verbatim (`opacity`, `x`, `y`, `scale`, `rotation`, `duration`,
    `ease`, `stagger`, ... -- anything GSAP's `.to()`/`.from()` accepts).

        Tween(".card", opacity=0, y=20, from_vars=True, duration=0.6, ease="power2.out")

    `position` only matters inside a `Timeline` -- it's GSAP's timeline
    position parameter (e.g. `"-=0.3"` to overlap with the previous tween).
    """
    target: str
    from_vars: bool = False
    position: Optional[Union[str, float]] = None
    vars: dict[str, Any] = field(default_factory=dict)

    def __init__(self, target: str, from_vars: bool = False,
                 position: Optional[Union[str, float]] = None, **vars: Any):
        self.target = target
        self.from_vars = from_vars
        self.position = position
        self.vars = vars

    def to_dict(self) -> dict:
        return {
            "type": "tween",
            "target": self.target,
            "from_vars": self.from_vars,
            "position": self.position,
            "vars": self.vars,
        }


@dataclass
class Timeline:
    """
    An ordered sequence of Tweens (or nested Timelines), played as a
    single GSAP timeline:

        Timeline(
            Tween(".hero-title", opacity=0, y=20, from_vars=True, duration=0.6),
            Tween(".hero-sub", opacity=0, y=20, from_vars=True, duration=0.6, position="-=0.3"),
            repeat=0,
        )
    """
    children: list[Union["Tween", "Timeline"]]
    repeat: int = 0
    yoyo: bool = False
    paused: bool = False

    def __init__(self, *children: Union["Tween", "Timeline"],
                 repeat: int = 0, yoyo: bool = False, paused: bool = False):
        self.children = list(children)
        self.repeat = repeat
        self.yoyo = yoyo
        self.paused = paused

    def to_dict(self) -> dict:
        return {
            "type": "timeline",
            "repeat": self.repeat,
            "yoyo": self.yoyo,
            "paused": self.paused,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class Animation:
    """
    Top-level wrapper attaching a Tween/Timeline to the page. Call
    `.to_element()` and include the result anywhere in a `render()`
    return value (it emits an inert `<script type="application/json">`
    marker, not visible UI) -- the client adapter finds it, builds the
    real GSAP timeline, names it, and autoplays it unless
    `autoplay=False` or the timeline itself is `paused=True`.

        anim = Animation(Tween(".box", x=200, duration=1), name="slide-box")
        el("div", ..., anim.to_element())

    Trigger it later (e.g. from a button, purely client-side, no server
    round-trip) with the onclick helpers:

        el("button", "Replay", onclick=anim.restart_attr())
    """
    root: Union[Tween, Timeline]
    name: str
    autoplay: bool = True

    def to_dict(self) -> dict:
        return {"name": self.name, "autoplay": self.autoplay, "root": self.root.to_dict()}

    def to_element(self):
        from ..core.element import el
        return el(
            "script",
            json.dumps(self.to_dict()),
            type="application/json",
            class_="nx-gsap-anim",
        )

    def play_attr(self) -> str:
        return f"window.__nexoria__.gsap.play('{self.name}')"

    def pause_attr(self) -> str:
        return f"window.__nexoria__.gsap.pause('{self.name}')"

    def restart_attr(self) -> str:
        return f"window.__nexoria__.gsap.restart('{self.name}')"

    def reverse_attr(self) -> str:
        return f"window.__nexoria__.gsap.reverse('{self.name}')"
