import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from starlette.testclient import TestClient
from nexoria import App, Component, el, Router
from nexoria.bootstrap import (
    BootstrapTheme, BOOTSTRAP_CSS_CDN, BOOTSTRAP_JS_CDN, BOOTSTRAP_ICONS_CSS_CDN,
)


class Home(Component):
    def render(self):
        return el("div", "hi")


def make_app(**kwargs):
    router = Router()
    router.add("/", Home)
    return App(name="Test App", router=router, **kwargs)


def test_bootstrap_theme_to_css_vars_only_includes_set_fields():
    theme = BootstrapTheme(primary="#6366f1", border_radius="0.75rem")
    css_vars = theme.to_css_vars()
    assert css_vars == {"--bs-primary": "#6366f1", "--bs-border-radius": "0.75rem"}


def test_bootstrap_theme_variables_pass_through_verbatim():
    theme = BootstrapTheme(variables={"font-sans-serif": "'Inter', sans-serif"})
    assert theme.to_css_vars() == {"--bs-font-sans-serif": "'Inter', sans-serif"}


def test_bootstrap_theme_empty_produces_no_style_tag():
    assert BootstrapTheme().to_style_tag() == ""


def test_bootstrap_theme_to_style_tag_renders_css_vars():
    tag = BootstrapTheme(primary="#ff0000").to_style_tag()
    assert tag.startswith("<style>:root {")
    assert "--bs-primary: #ff0000;" in tag


def test_app_bootstrap_false_by_default_no_tags_injected():
    r = TestClient(make_app()).get("/")
    assert "bootstrap" not in r.text.lower()


def test_app_bootstrap_true_injects_css_js_and_adapter():
    r = TestClient(make_app(bootstrap=True)).get("/")
    assert BOOTSTRAP_CSS_CDN in r.text
    assert BOOTSTRAP_JS_CDN in r.text
    assert "bootstrap-adapter.js" in r.text


def test_app_bootstrap_icons_off_by_default():
    r = TestClient(make_app(bootstrap=True)).get("/")
    assert BOOTSTRAP_ICONS_CSS_CDN not in r.text


def test_app_bootstrap_icons_injects_icon_stylesheet():
    r = TestClient(make_app(bootstrap=True, bootstrap_icons=True)).get("/")
    assert BOOTSTRAP_ICONS_CSS_CDN in r.text


def test_app_bootstrap_icons_ignored_when_bootstrap_disabled():
    r = TestClient(make_app(bootstrap_icons=True)).get("/")
    assert BOOTSTRAP_ICONS_CSS_CDN not in r.text
    assert "bootstrap-adapter.js" not in r.text


def test_app_bootstrap_theme_injects_style_tag_after_core_css():
    r = TestClient(make_app(bootstrap=True, bootstrap_theme=BootstrapTheme(primary="#00ff00"))).get("/")
    assert "--bs-primary: #00ff00;" in r.text
    css_pos = r.text.index(BOOTSTRAP_CSS_CDN)
    theme_pos = r.text.index("--bs-primary")
    assert css_pos < theme_pos


def test_app_bootstrap_no_theme_style_tag_when_theme_not_given():
    r = TestClient(make_app(bootstrap=True)).get("/")
    assert "--bs-primary" not in r.text


def test_bootstrap_adapter_served_with_js_mimetype():
    r = TestClient(make_app(bootstrap=True)).get("/_nexoria/bootstrap-adapter.js")
    assert r.status_code == 200
    assert "javascript" in r.headers["content-type"]
    assert "bootstrap" in r.text.lower()


def test_bootstrap_adapter_syncs_theme_and_initializes_tooltips_popovers():
    r = TestClient(make_app(bootstrap=True)).get("/_nexoria/bootstrap-adapter.js")
    assert "data-bs-theme" in r.text
    assert "data-nx-theme" in r.text
    assert "bootstrap.Tooltip" in r.text
    assert "bootstrap.Popover" in r.text
    assert "mountNew" in r.text


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
