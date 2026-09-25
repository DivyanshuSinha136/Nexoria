"""
nexoria.std.animation.presets
================================
A small, dependency-free library of ready-made `Keyframes` -- the
common animate.css-style moves (fades, slides, zooms, attention
seekers) as plain CSS `@keyframes`, so most components never need to
hand-write one. Pre-registered on `nexoria.std.animation.engine.ANIMATION_ENGINE`
under the names in `PRESET_NAMES`.
"""

from __future__ import annotations

from .keyframes import Keyframes

PRESETS: dict[str, Keyframes] = {
    "fade-in": Keyframes("nx-anim-fade-in", {
        "from": {"opacity": 0},
        "to": {"opacity": 1},
    }),
    "fade-out": Keyframes("nx-anim-fade-out", {
        "from": {"opacity": 1},
        "to": {"opacity": 0},
    }),
    "fade-in-up": Keyframes("nx-anim-fade-in-up", {
        "from": {"opacity": 0, "transform": "translateY(24px)"},
        "to": {"opacity": 1, "transform": "translateY(0)"},
    }),
    "fade-in-down": Keyframes("nx-anim-fade-in-down", {
        "from": {"opacity": 0, "transform": "translateY(-24px)"},
        "to": {"opacity": 1, "transform": "translateY(0)"},
    }),
    "fade-in-left": Keyframes("nx-anim-fade-in-left", {
        "from": {"opacity": 0, "transform": "translateX(-24px)"},
        "to": {"opacity": 1, "transform": "translateX(0)"},
    }),
    "fade-in-right": Keyframes("nx-anim-fade-in-right", {
        "from": {"opacity": 0, "transform": "translateX(24px)"},
        "to": {"opacity": 1, "transform": "translateX(0)"},
    }),
    "slide-in-up": Keyframes("nx-anim-slide-in-up", {
        "from": {"transform": "translateY(100%)"},
        "to": {"transform": "translateY(0)"},
    }),
    "slide-in-down": Keyframes("nx-anim-slide-in-down", {
        "from": {"transform": "translateY(-100%)"},
        "to": {"transform": "translateY(0)"},
    }),
    "slide-in-left": Keyframes("nx-anim-slide-in-left", {
        "from": {"transform": "translateX(-100%)"},
        "to": {"transform": "translateX(0)"},
    }),
    "slide-in-right": Keyframes("nx-anim-slide-in-right", {
        "from": {"transform": "translateX(100%)"},
        "to": {"transform": "translateX(0)"},
    }),
    "zoom-in": Keyframes("nx-anim-zoom-in", {
        "from": {"opacity": 0, "transform": "scale(0.85)"},
        "to": {"opacity": 1, "transform": "scale(1)"},
    }),
    "zoom-out": Keyframes("nx-anim-zoom-out", {
        "from": {"opacity": 1, "transform": "scale(1)"},
        "to": {"opacity": 0, "transform": "scale(0.85)"},
    }),
    "flip-in": Keyframes("nx-anim-flip-in", {
        "from": {"opacity": 0, "transform": "perspective(400px) rotateY(90deg)"},
        "to": {"opacity": 1, "transform": "perspective(400px) rotateY(0deg)"},
    }),
    "spin": Keyframes("nx-anim-spin", {
        "from": {"transform": "rotate(0deg)"},
        "to": {"transform": "rotate(360deg)"},
    }),
    "pulse": Keyframes("nx-anim-pulse").at("0%, 100%", transform="scale(1)").at("50%", transform="scale(1.06)"),
    "ping": Keyframes("nx-anim-ping")
        .at(0, transform="scale(1)", opacity=1)
        .at(75, transform="scale(1.8)", opacity=0)
        .at(100, transform="scale(1.8)", opacity=0),
    "bounce": Keyframes("nx-anim-bounce")
        .at("0%, 100%", transform="translateY(0)")
        .at("50%", transform="translateY(-14px)"),
    "shake": Keyframes("nx-anim-shake")
        .at("0%, 100%", transform="translateX(0)")
        .at("20%, 60%", transform="translateX(-8px)")
        .at("40%, 80%", transform="translateX(8px)"),
    "wobble": Keyframes("nx-anim-wobble")
        .at("0%, 100%", transform="translateX(0) rotate(0deg)")
        .at("15%", transform="translateX(-14px) rotate(-5deg)")
        .at("30%", transform="translateX(10px) rotate(3deg)")
        .at("45%", transform="translateX(-8px) rotate(-3deg)")
        .at("60%", transform="translateX(6px) rotate(2deg)")
        .at("75%", transform="translateX(-4px) rotate(-1deg)"),
    "heartbeat": Keyframes("nx-anim-heartbeat")
        .at("0%, 100%", transform="scale(1)")
        .at("14%", transform="scale(1.15)")
        .at("28%", transform="scale(1)")
        .at("42%", transform="scale(1.15)")
        .at("70%", transform="scale(1)"),
    "rubber-band": Keyframes("nx-anim-rubber-band")
        .at(0, transform="scale3d(1, 1, 1)")
        .at(30, transform="scale3d(1.25, 0.75, 1)")
        .at(40, transform="scale3d(0.75, 1.25, 1)")
        .at(50, transform="scale3d(1.15, 0.85, 1)")
        .at(65, transform="scale3d(0.95, 1.05, 1)")
        .at(75, transform="scale3d(1.05, 0.95, 1)")
        .at(100, transform="scale3d(1, 1, 1)"),
}

PRESET_NAMES = tuple(PRESETS.keys())
