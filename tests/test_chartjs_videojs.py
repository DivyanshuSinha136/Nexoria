import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from starlette.testclient import TestClient
from nexoria import App, Component, el, Router
from nexoria.chartjs import Chart, Dataset, CHARTJS_CDN
from nexoria.videojs import VideoPlayer, Track, VideoTheme, ControlBar, VideoPlugin, VIDEOJS_JS_CDN, VIDEOJS_CSS_CDN
from nexoria.gsap import Tween, Animation
from nexoria.render.html import render_to_html


# ---- Chart.js -------------------------------------------------------

def test_dataset_serializes_with_extra_kwargs():
    d = Dataset("Revenue", [10, 20, 15], backgroundColor="#6366f1", tension=0.4)
    out = d.to_dict()
    assert out == {"label": "Revenue", "data": [10, 20, 15], "backgroundColor": "#6366f1", "tension": 0.4}


def test_chart_serializes_correct_chartjs_shape():
    chart = Chart(
        type="bar",
        labels=["Jan", "Feb", "Mar"],
        datasets=[Dataset("Revenue", [10, 20, 15], backgroundColor="#6366f1")],
        options={"responsive": True},
    )
    d = chart.to_dict()
    assert d["type"] == "bar"
    assert d["data"]["labels"] == ["Jan", "Feb", "Mar"]
    assert d["data"]["datasets"][0]["label"] == "Revenue"
    assert d["options"] == {"responsive": True}


def test_chart_to_element_produces_valid_json_canvas():
    chart = Chart(type="line", labels=["A"], datasets=[Dataset("X", [1])])
    node = chart.to_element()
    assert node.tag == "canvas"
    html = render_to_html(node)
    assert 'class="nx-chartjs-canvas"' in html
    # data-nx-chart is an attribute (not text content), so ordinary
    # attribute HTML-escaping applies here -- confirm it round-trips.
    import re
    from html import unescape
    m = re.search(r'data-nx-chart="([^"]*)"', html)
    recovered = json.loads(unescape(m.group(1)))
    assert recovered["type"] == "line"


def test_app_chartjs_false_by_default():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    r = TestClient(App(name="t", router=router)).get("/")
    assert "chart.js" not in r.text.lower()


def test_app_chartjs_true_injects_importmap_and_adapter():
    router = Router()

    class Home(Component):
        def render(self):
            chart = Chart(type="pie", labels=["A"], datasets=[Dataset("X", [1])])
            return el("div", chart.to_element())

    router.add("/", Home)
    r = TestClient(App(name="t", router=router, chartjs=True)).get("/")
    assert "importmap" in r.text
    assert CHARTJS_CDN in r.text
    assert "chartjs-adapter.js" in r.text
    assert "nx-chartjs-canvas" in r.text


def test_chartjs_importmap_includes_transitive_kurkle_color_dependency():
    """
    Regression test: chart.js's ESM entry imports its color-parsing
    helper (@kurkle/color) as a bare specifier internally. Without an
    import-map entry for it too, the browser throws "Failed to resolve
    module specifier '@kurkle/color'" the moment chart.js's own code
    runs -- the top-level chart.js URL alone isn't enough.
    """
    from nexoria.chartjs.chart import KURKLE_COLOR_CDN
    router = Router()

    class Home(Component):
        def render(self):
            chart = Chart(type="pie", labels=["A"], datasets=[Dataset("X", [1])])
            return el("div", chart.to_element())

    router.add("/", Home)
    r = TestClient(App(name="t", router=router, chartjs=True)).get("/")
    imports = _importmap_imports(r.text)
    assert "@kurkle/color" in imports
    assert imports["@kurkle/color"] == KURKLE_COLOR_CDN


# ---- video.js ---------------------------------------------------------

def test_videoplayer_serializes_fields():
    v = VideoPlayer("/static/demo.mp4", poster="/static/p.jpg", autoplay=True, muted=True)
    d = v.to_dict()
    assert d["sources"] == [{"src": "/static/demo.mp4", "type": "video/mp4"}]
    assert d["poster"] == "/static/p.jpg"
    assert d["autoplay"] is True
    assert d["muted"] is True


def test_videoplayer_requires_src_or_sources():
    import pytest
    with pytest.raises(ValueError):
        VideoPlayer()


def test_videoplayer_multiple_sources_with_mime_guessing():
    v = VideoPlayer(sources=["/static/demo.webm", "/static/demo.mp4", "/static/demo.m3u8"])
    d = v.to_dict()
    assert d["sources"] == [
        {"src": "/static/demo.webm", "type": "video/webm"},
        {"src": "/static/demo.mp4", "type": "video/mp4"},
        {"src": "/static/demo.m3u8", "type": "application/x-mpegURL"},
    ]


def test_videoplayer_source_dict_explicit_type_overrides_guess():
    v = VideoPlayer(sources=[{"src": "/static/stream", "type": "application/dash+xml"}])
    d = v.to_dict()
    assert d["sources"] == [{"src": "/static/stream", "type": "application/dash+xml"}]


def test_videoplayer_tracks_serialize():
    v = VideoPlayer("/static/demo.mp4", tracks=[
        Track("/static/en.vtt", label="English", default=True),
        Track("/static/fr.vtt", srclang="fr"),
    ])
    d = v.to_dict()
    assert d["tracks"] == [
        {"src": "/static/en.vtt", "kind": "captions", "srclang": "en", "label": "English", "default": True},
        {"src": "/static/fr.vtt", "kind": "captions", "srclang": "fr", "label": "fr", "default": False},
    ]


def test_videoplayer_fluid_default_true_and_extra_options():
    v = VideoPlayer("/static/demo.mp4", aspect_ratio="16:9", playback_rates=[0.5, 1, 2])
    d = v.to_dict()
    assert d["fluid"] is True
    assert d["aspectRatio"] == "16:9"
    assert d["playbackRates"] == [0.5, 1, 2]


# ---- video.js customization: theme, control bar, plugins --------------

def test_video_theme_to_css_scoped_by_player_id():
    theme = VideoTheme(accent="#ff6b35")
    css = theme.to_css("my-player")
    assert "#my-player.video-js .vjs-big-play-button" in css
    assert "#ff6b35" in css


def test_video_theme_from_theme_derives_from_app_theme():
    from nexoria.style import Theme
    app_theme = Theme(primary="#00ffcc", surface_alt="#111111", text="#eeeeee", radius_sm="4px")
    vt = VideoTheme.from_theme(app_theme)
    assert vt.accent == "#00ffcc"
    assert vt.control_bar_bg == "#111111"
    assert vt.text == "#eeeeee"
    assert vt.border_radius == "4px"


def test_videoplayer_theme_element_none_when_no_theme():
    v = VideoPlayer("/static/demo.mp4")
    assert v.theme_element() is None


def test_videoplayer_theme_element_renders_scoped_style_tag():
    v = VideoPlayer("/static/demo.mp4", theme=VideoTheme(accent="#123456"), player_id="explicit-id")
    style_node = v.theme_element()
    assert style_node.tag == "style"
    html = render_to_html(style_node)
    assert "#explicit-id.video-js" in html
    assert "#123456" in html


def test_videoplayer_custom_css_included_in_theme_element():
    v = VideoPlayer("/static/demo.mp4", custom_css=".foo { color: red; }", player_id="p1")
    html = render_to_html(v.theme_element())
    assert ".foo { color: red; }" in html


def test_videoplayer_el_none_children_skipped():
    """`el("div", player.to_element(), player.theme_element())` must work
    whether or not a theme is set -- None children are dropped."""
    from nexoria.core.element import el
    v = VideoPlayer("/static/demo.mp4")  # no theme
    node = el("div", v.to_element(), v.theme_element())
    assert len(node.children) == 1


def test_control_bar_serializes_into_options():
    v = VideoPlayer("/static/demo.mp4", control_bar=ControlBar(children=["playToggle", "progressControl"]))
    d = v.to_dict()
    assert d["options"]["controlBar"] == {"children": ["playToggle", "progressControl"]}


def test_control_bar_extra_options_passthrough():
    cb = ControlBar(extra={"volumePanel": {"inline": False}})
    assert cb.to_dict() == {"volumePanel": {"inline": False}}


def test_active_plugins_serialize():
    v = VideoPlayer("/static/demo.mp4", active_plugins={"myPlugin": {"x": 1}})
    d = v.to_dict()
    assert d["activePlugins"] == {"myPlugin": {"x": 1}}


def test_app_videojs_plugins_injects_scripts_in_correct_order():
    router = Router()

    class Home(Component):
        def render(self):
            player = VideoPlayer("/static/demo.mp4", active_plugins={"coolPlugin": {}})
            return el("div", player.to_element())

    router.add("/", Home)
    app = App(
        name="t", router=router, videojs=True,
        videojs_plugins=[VideoPlugin("coolPlugin", "https://cdn.example.com/cool.js")],
    )
    r = TestClient(app).get("/")
    assert "https://cdn.example.com/cool.js" in r.text
    core_pos = r.text.index(VIDEOJS_JS_CDN)
    plugin_pos = r.text.index("cool.js")
    adapter_pos = r.text.index("videojs-adapter.js")
    assert core_pos < plugin_pos < adapter_pos


def test_app_videojs_no_plugins_by_default():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", VideoPlayer("/static/demo.mp4").to_element())

    router.add("/", Home)
    r = TestClient(App(name="t", router=router, videojs=True)).get("/")
    assert "cool.js" not in r.text


def test_videoplayer_to_element_has_video_js_class_and_controls_boolean():
    v = VideoPlayer("/static/demo.mp4", controls=True)
    node = v.to_element(player_id="my-player")
    html = render_to_html(node)
    assert 'id="my-player"' in html
    assert "video-js" in html
    assert "nx-videojs-player" in html
    assert " controls" in html  # real HTML boolean attribute, not controls="True"
    assert 'controls="' not in html


def test_videoplayer_controls_false_omits_attribute():
    v_on = VideoPlayer("/static/demo.mp4", controls=True)
    v_off = VideoPlayer("/static/demo.mp4", controls=False)
    html_on = render_to_html(v_on.to_element())
    html_off = render_to_html(v_off.to_element())
    # The real HTML boolean attribute (bare "controls" token, distinct
    # from the same word appearing inside the JSON spec attribute value)
    # must be present when True and absent when False.
    assert ' controls preload="auto">' in html_on
    assert ' controls preload="auto">' not in html_off
    assert ' preload="auto">' in html_off


def test_app_videojs_true_injects_css_and_umd_script():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", VideoPlayer("/static/demo.mp4").to_element())

    router.add("/", Home)
    r = TestClient(App(name="t", router=router, videojs=True)).get("/")
    assert VIDEOJS_CSS_CDN in r.text
    assert VIDEOJS_JS_CDN in r.text
    assert "videojs-adapter.js" in r.text
    # video.js is classic UMD, not an ES module -- must NOT show up in
    # the shared import map alongside three/gsap/chart.js.
    assert "video.js" not in _importmap_imports(r.text)


def _importmap_imports(html: str) -> dict:
    import re
    m = re.search(r'<script type="importmap">(.*?)</script>', html)
    if not m:
        return {}
    return json.loads(m.group(1))["imports"]


# ---- the multi-integration import-map merge fix ------------------------

def test_multiple_esm_integrations_produce_exactly_one_importmap():
    """
    Regression test: ThreeJS/GSAP/Chart.js each used to emit their own
    `<script type="importmap">` tag. Browsers only honor one import map
    per document, so enabling more than one of these together used to
    silently break whichever loaded second.
    """
    router = Router()

    class Home(Component):
        def render(self):
            chart = Chart(type="bar", labels=["A"], datasets=[Dataset("X", [1])])
            anim = Animation(Tween(".box", x=1), name="a")
            return el("div", chart.to_element(), anim.to_element())

    router.add("/", Home)
    app = App(name="t", router=router, gsap=True, chartjs=True, threejs=True)
    r = TestClient(app).get("/")
    assert r.text.count('type="importmap"') == 1
    imports = _importmap_imports(r.text)
    assert set(imports.keys()) == {"three", "gsap", "chart.js", "@kurkle/color"}


def test_all_four_integrations_together_dont_crash():
    router = Router()

    class Home(Component):
        def render(self):
            chart = Chart(type="bar", labels=["A"], datasets=[Dataset("X", [1])])
            video = VideoPlayer("/static/demo.mp4")
            anim = Animation(Tween(".box", x=1), name="a")
            return el("div", chart.to_element(), video.to_element(), anim.to_element())

    router.add("/", Home)
    app = App(name="t", router=router, gsap=True, chartjs=True, threejs=True, videojs=True)
    r = TestClient(app).get("/")
    assert r.status_code == 200
    assert r.text.count('type="importmap"') == 1


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
