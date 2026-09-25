import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from starlette.testclient import TestClient
from nexoria import App, Component, el, Router
from nexoria.gsap import (
    Tween, Timeline, Animation, GSAP_CDN, GSAP_ALL_PLUGINS,
    GSAP_PLUGIN_CDN_BASE, gsap_plugin_imports, gsap_plugin_config_tag,
)


def test_tween_serializes_correctly():
    t = Tween(".box", opacity=0, y=20, from_vars=True, duration=0.5, ease="power2.out")
    d = t.to_dict()
    assert d["type"] == "tween"
    assert d["target"] == ".box"
    assert d["from_vars"] is True
    assert d["vars"] == {"opacity": 0, "y": 20, "duration": 0.5, "ease": "power2.out"}


def test_timeline_serializes_children_in_order():
    tl = Timeline(
        Tween(".a", x=10),
        Tween(".b", x=20, position="-=0.2"),
        repeat=-1, yoyo=True,
    )
    d = tl.to_dict()
    assert d["type"] == "timeline"
    assert d["repeat"] == -1
    assert d["yoyo"] is True
    assert [c["target"] for c in d["children"]] == [".a", ".b"]
    assert d["children"][1]["position"] == "-=0.2"


def test_animation_to_element_produces_valid_json_script_tag():
    from nexoria.render.html import render_to_html
    anim = Animation(Tween(".box", x=100), name="my-anim", autoplay=False)
    node = anim.to_element()
    html = render_to_html(node)
    assert 'class="nx-gsap-anim"' in html
    assert 'type="application/json"' in html
    start = html.index(">") + 1
    end = html.rindex("</")
    recovered = json.loads(html[start:end].replace("<\\/script>", "</script>"))
    assert recovered["name"] == "my-anim"
    assert recovered["autoplay"] is False


def test_animation_control_attrs():
    anim = Animation(Tween(".box", x=1), name="foo")
    assert anim.play_attr() == "window.__nexoria__.gsap.play('foo')"
    assert anim.pause_attr() == "window.__nexoria__.gsap.pause('foo')"
    assert anim.restart_attr() == "window.__nexoria__.gsap.restart('foo')"
    assert anim.reverse_attr() == "window.__nexoria__.gsap.reverse('foo')"


def test_app_gsap_false_by_default_no_tags_injected():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    app = App(name="t", router=router)
    r = TestClient(app).get("/")
    assert "gsap" not in r.text.lower()


def test_app_gsap_true_injects_importmap_and_adapter():
    router = Router()

    class Home(Component):
        def render(self):
            anim = Animation(Tween(".box", x=1), name="a")
            return el("div", el("div", class_="box"), anim.to_element())

    router.add("/", Home)
    app = App(name="t", router=router, gsap=True)
    r = TestClient(app).get("/")
    assert "importmap" in r.text
    assert GSAP_CDN in r.text
    assert "gsap-adapter.js" in r.text
    assert "nx-gsap-anim" in r.text


def test_gsap_adapter_served_with_js_mimetype():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    app = App(name="t", router=router, gsap=True)
    r = TestClient(app).get("/_nexoria/gsap-adapter.js")
    assert r.status_code == 200
    assert "javascript" in r.headers["content-type"]
    assert "gsap" in r.text


def test_gsap_all_plugins_contains_the_major_ones():
    for name in ("ScrollTrigger", "Draggable", "Flip", "MotionPathPlugin",
                 "SplitText", "MorphSVGPlugin", "DrawSVGPlugin", "TextPlugin",
                 "Observer", "CustomEase"):
        assert name in GSAP_ALL_PLUGINS


def test_gsap_plugin_imports_builds_correct_urls():
    imports = gsap_plugin_imports(["ScrollTrigger", "Draggable"])
    assert imports == {
        "gsap/ScrollTrigger": f"{GSAP_PLUGIN_CDN_BASE}/ScrollTrigger.js",
        "gsap/Draggable": f"{GSAP_PLUGIN_CDN_BASE}/Draggable.js",
    }


def test_gsap_plugin_imports_rejects_unknown_plugin():
    with pytest.raises(ValueError):
        gsap_plugin_imports(["NotARealPlugin"])


def test_gsap_plugin_config_tag_empty_when_no_plugins():
    assert gsap_plugin_config_tag([]) == ""


def test_gsap_plugin_config_tag_lists_names_as_json():
    import json as _json
    tag = gsap_plugin_config_tag(["Flip", "ScrollTrigger"])
    assert 'id="nx-gsap-plugins"' in tag
    start = tag.index(">") + 1
    end = tag.rindex("</")
    assert _json.loads(tag[start:end]) == ["Flip", "ScrollTrigger"]


def test_app_rejects_unknown_gsap_plugin_at_construction():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    with pytest.raises(ValueError):
        App(name="t", router=router, gsap=True, gsap_plugins=["NotARealPlugin"])


def test_app_gsap_plugins_injects_plugin_imports_and_config():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    app = App(name="t", router=router, gsap=True, gsap_plugins=["ScrollTrigger", "Draggable"])
    r = TestClient(app).get("/")
    assert "gsap/ScrollTrigger" in r.text
    assert "gsap/Draggable" in r.text
    assert f"{GSAP_PLUGIN_CDN_BASE}/ScrollTrigger.js" in r.text
    assert 'id="nx-gsap-plugins"' in r.text
    assert "gsap-adapter.js" in r.text


def test_app_gsap_plugins_empty_by_default_no_plugin_config_tag():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    app = App(name="t", router=router, gsap=True)
    r = TestClient(app).get("/")
    assert "nx-gsap-plugins" not in r.text


def test_gsap_adapter_registers_plugins_before_mounting_when_served():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    app = App(name="t", router=router, gsap=True, gsap_plugins=["ScrollTrigger"])
    r = TestClient(app).get("/_nexoria/gsap-adapter.js")
    assert r.status_code == 200
    assert "registerConfiguredPlugins" in r.text
    assert "gsap.registerPlugin" in r.text


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
