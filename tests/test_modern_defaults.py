import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from starlette.testclient import TestClient
from nexoria import App, Component, el, Router
from nexoria.style import theme_toggle_button, Theme


class Home(Component):
    def render(self):
        return el("div", el("nav", theme_toggle_button(), class_="nx-nav"), el("h1", "Hi"))


def make_app(**kwargs):
    router = Router()
    router.add("/", Home)
    return App(name="Test App", router=router, **kwargs)


def test_theme_init_script_present_and_runs_before_stylesheets():
    client = TestClient(make_app())
    r = client.get("/")
    # the blocking inline theme-init script must appear before the
    # stylesheet links, so it can set data-nx-theme before first paint
    init_pos = r.text.index("nx-theme")
    css_pos = r.text.index("base.css")
    assert init_pos < css_pos


def test_light_theme_override_included_by_default():
    client = TestClient(make_app())
    r = client.get("/")
    assert 'data-nx-theme="light"' in r.text


def test_light_theme_can_be_disabled():
    client = TestClient(make_app(light_theme=None))
    r = client.get("/")
    assert 'data-nx-theme="light"' not in r.text


def test_custom_light_theme_tokens_used():
    client = TestClient(make_app(light_theme=Theme(primary="#00ff00")))
    r = client.get("/")
    assert '--nx-primary: #00ff00;' in r.text


def test_theme_toggle_button_helper_renders_and_wires_js():
    client = TestClient(make_app())
    r = client.get("/")
    assert "nx-theme-toggle" in r.text
    assert "window.__nexoria__.toggleTheme()" in r.text


def test_runtime_js_exposes_toggle_theme_function():
    client = TestClient(make_app())
    r = client.get("/_nexoria/runtime.js")
    assert "toggleTheme" in r.text
    assert "nx-theme" in r.text


def test_seo_meta_tags_rendered_when_provided():
    client = TestClient(make_app(
        description="A great app.",
        favicon="/fav.ico",
        og_image="https://example.com/og.png",
    ))
    r = client.get("/")
    assert '<meta name="description" content="A great app.">' in r.text
    assert 'property="og:description" content="A great app."' in r.text
    assert 'property="og:image" content="https://example.com/og.png"' in r.text
    assert '<link rel="icon" href="/fav.ico">' in r.text


def test_seo_meta_tags_absent_when_not_provided():
    client = TestClient(make_app())
    r = client.get("/")
    assert '<meta name="description"' not in r.text


def test_default_favicon_is_the_framework_falcon_mark():
    client = TestClient(make_app())
    r = client.get("/")
    assert '<link rel="icon" type="image/svg+xml" href="/_nexoria/falcon-nexoria.svg">' in r.text
    assert '<link rel="icon" type="image/x-icon" href="/_nexoria/falcon-nexoria.ico">' in r.text


def test_favicon_can_be_disabled():
    client = TestClient(make_app(favicon=None))
    r = client.get("/")
    assert '<link rel="icon"' not in r.text


def test_default_404_page_is_styled_not_bare():
    client = TestClient(make_app())
    r = client.get("/does-not-exist")
    assert r.status_code == 404
    assert "nx-card" in r.text
    assert "base.css" in r.text
    assert "Page not found" in r.text


def test_default_404_page_respects_theme_and_seo_settings():
    client = TestClient(make_app(theme=Theme(primary="#ff00ff"), description="Desc"))
    r = client.get("/does-not-exist")
    assert "--nx-primary: #ff00ff;" in r.text
    assert '<meta name="description" content="Desc">' in r.text


def test_custom_not_found_component_overrides_default():
    class Custom404(Component):
        def render(self):
            return el("div", "my custom 404")

    router = Router()
    router.add("/", Home)
    router.set_not_found(Custom404)
    app = App(name="t", router=router)
    r = TestClient(app).get("/nope")
    assert r.status_code == 200  # resolve() returns a component -> normal 200 render path
    assert "my custom 404" in r.text


def test_favicon_redirects_to_framework_icon_when_not_configured():
    """
    Regression test: browsers unconditionally request /favicon.ico
    regardless of any <link rel="icon"> tag. Not configured now means
    "use the framework's default falcon mark", so this should redirect
    to that icon's .ico asset rather than 404 or come back empty.
    """
    client = TestClient(make_app())
    r = client.get("/favicon.ico", follow_redirects=False)
    assert r.status_code in (301, 302, 307, 308)
    assert r.headers["location"] == "/_nexoria/falcon-nexoria.ico"


def test_favicon_returns_204_when_explicitly_disabled():
    client = TestClient(make_app(favicon=None))
    r = client.get("/favicon.ico")
    assert r.status_code == 204


def test_favicon_redirects_when_configured():
    client = TestClient(make_app(favicon="/static/icon.png"))
    r = client.get("/favicon.ico", follow_redirects=False)
    assert r.status_code in (301, 302, 307, 308)
    assert r.headers["location"] == "/static/icon.png"


def test_falcon_icon_assets_served_with_correct_mime_types():
    client = TestClient(make_app())
    svg = client.get("/_nexoria/falcon-nexoria.svg")
    assert svg.status_code == 200
    assert svg.headers["content-type"].startswith("image/svg+xml")

    ico = client.get("/_nexoria/falcon-nexoria.ico")
    assert ico.status_code == 200
    assert ico.headers["content-type"].startswith("image/x-icon")


def test_spinner_class_defined_in_base_css():
    client = TestClient(make_app())
    r = client.get("/_nexoria/base.css")
    assert ".nx-spinner" in r.text


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
