import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nexoria.style import Stylesheet, Theme, DEFAULT_THEME
from nexoria import App, Component, el, Router
from starlette.testclient import TestClient


def test_theme_renders_css_vars():
    css = DEFAULT_THEME.to_css_vars()
    assert ":root" in css
    assert "--nx-primary:" in css
    assert DEFAULT_THEME.primary in css


def test_custom_theme_overrides_tokens():
    t = Theme(primary="#ff0000")
    css = t.to_css_vars()
    assert "--nx-primary: #ff0000;" in css


def test_stylesheet_add_and_to_css():
    s = Stylesheet()
    s.add(".box", background="red", font_size="1rem")
    css = s.to_css()
    assert ".box {" in css
    assert "background: red;" in css
    assert "font-size: 1rem;" in css  # underscore -> hyphen


def test_scoped_class_is_deterministic_and_collision_free():
    s = Stylesheet()
    c1 = s.scoped_class("card", padding="10px")
    c2 = s.scoped_class("card", padding="10px")
    c3 = s.scoped_class("card", padding="20px")
    assert c1 == c2  # same props -> same class name
    assert c1 != c3  # different props -> different class name
    assert c1.startswith("nx-card-")


def test_scoped_class_vendor_prefixed_prop_passthrough():
    s = Stylesheet()
    cls = s.scoped_class("grad", **{"-webkit-background-clip": "text"})
    css = s.to_css()
    assert "-webkit-background-clip: text;" in css


def test_stylesheet_merge_combines_rules():
    a = Stylesheet({".a": {"color": "red"}})
    b = Stylesheet({".b": {"color": "blue"}})
    merged = a.merge(b)
    assert ".a" in merged.rules and ".b" in merged.rules


def test_el_style_dict_converts_to_inline_css_string():
    node = el("div", style={"background_color": "red", "font-size": "1rem"})
    assert node.props["style"] == "background-color: red; font-size: 1rem"


def test_app_injects_theme_and_base_css():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    app = App(name="t", router=router, theme=Theme(primary="#123456"))
    client = TestClient(app)
    r = client.get("/")
    assert "/_nexoria/base.css" in r.text
    assert "--nx-primary: #123456;" in r.text


def test_app_merges_component_scoped_styles():
    router = Router()

    class Home(Component):
        styles = Stylesheet()

        def render(self):
            cls = self.styles.scoped_class("hi", color="green")
            return el("div", "hi", class_=cls)

    router.add("/", Home)
    app = App(name="t", router=router)
    client = TestClient(app)
    r = client.get("/")
    assert "color: green;" in r.text


def test_base_css_served_with_correct_mimetype():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    app = App(name="t", router=router)
    client = TestClient(app)
    r = client.get("/_nexoria/base.css")
    assert r.status_code == 200
    assert "css" in r.headers["content-type"]
    assert ".nx-btn" in r.text


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
