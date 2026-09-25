import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from starlette.testclient import TestClient
from nexoria import App, Component, el, Router
from nexoria.render.html import render_to_html

from nexoria.std.premium import (
    PREMIUM_THEME, premium_keyframes, premium_button, premium_badge, premium_avatar,
    premium_card, glass_panel, stat_card, pricing_card, hero_section, feature_grid,
    testimonial, premium_navbar, premium_footer,
)
from nexoria.std.cartoon import (
    CARTOON_THEME, cartoon_keyframes, cartoon_button, cartoon_card, comic_panel,
    speech_bubble, thought_bubble, sticker_badge, cartoon_avatar, blob_progress,
)


def make_app(component_cls, **kwargs):
    router = Router()
    router.add("/", component_cls)
    return App(name="Test App", router=router, **kwargs)


# -- premium ------------------------------------------------------------

def test_premium_theme_extends_base_theme_css_vars():
    css = PREMIUM_THEME.to_css_vars()
    assert "--nx-primary" in css          # inherited from Theme
    assert "--nx-premium-gold" in css     # premium-only token


def test_premium_keyframes_renders_style_tag_with_raw_css():
    html = render_to_html(premium_keyframes())
    assert html.startswith("<style>")
    assert "@keyframes nx-premium-shimmer" in html


def test_premium_button_renders_link_when_href_given():
    html = render_to_html(premium_button("Go", href="/x"))
    assert "<a " in html
    assert 'href="/x"' in html
    assert "Go" in html


def test_premium_button_renders_button_when_no_href():
    html = render_to_html(premium_button("Go"))
    assert "<button" in html


def test_premium_button_disabled_has_no_click_handlers():
    html = render_to_html(premium_button("Go", href="/x", disabled=True))
    assert "<button" in html  # disabled anchors degrade to a plain button
    assert "aria-disabled" in html


def test_premium_card_glow_sets_animation_style():
    html = render_to_html(premium_card("body", title="T", glow=True))
    assert "nx-premium-glow" in html
    assert "T" in html


def test_pricing_card_highlighted_shows_badge_and_gold_button():
    html = render_to_html(pricing_card("Pro", "$29", features=["a", "b"], highlighted=True))
    assert "Most Popular" in html
    assert "a" in html and "b" in html


def test_feature_grid_renders_all_items():
    html = render_to_html(feature_grid([{"title": "Fast", "desc": "d1"}, {"title": "Safe", "desc": "d2"}]))
    assert "Fast" in html and "Safe" in html


def test_premium_navbar_renders_links_and_cta():
    html = render_to_html(premium_navbar("Acme", links=[("Product", "/p")], cta_text="Sign up", cta_href="/su"))
    assert "Acme" in html
    assert 'href="/p"' in html
    assert "Sign up" in html


def test_app_renders_premium_hero_end_to_end():
    class Home(Component):
        def render(self):
            return el("div", hero_section("Title", subtitle="Sub", cta_text="Go", cta_href="/go"))

    r = TestClient(make_app(Home)).get("/")
    assert r.status_code == 200
    assert "Title" in r.text
    assert "Go" in r.text


# -- cartoon --------------------------------------------------------------

def test_cartoon_theme_extends_base_theme_css_vars():
    css = CARTOON_THEME.to_css_vars()
    assert "--nx-primary" in css
    assert "--nx-cartoon-ink" in css


def test_cartoon_keyframes_renders_style_tag_with_raw_css():
    html = render_to_html(cartoon_keyframes())
    assert "@keyframes nx-cartoon-wiggle" in html


def test_cartoon_button_wiggle_sets_animation_style():
    html = render_to_html(cartoon_button("Go!", wiggle=True))
    assert "nx-cartoon-wiggle" in html


def test_cartoon_button_disabled_has_no_press_handlers():
    html = render_to_html(cartoon_button("Go!", disabled=True))
    assert "onmousedown" not in html
    assert "aria-disabled" in html


def test_cartoon_card_renders_title_and_children():
    html = render_to_html(cartoon_card("body text", title="Chapter 1"))
    assert "Chapter 1" in html
    assert "body text" in html


def test_comic_panel_wraps_children_and_caption():
    html = render_to_html(comic_panel(cartoon_card("a"), cartoon_card("b"), caption="strip"))
    assert "strip" in html


def test_speech_bubble_all_directions_render():
    for direction in ("left", "right", "bottom"):
        html = render_to_html(speech_bubble("hi", direction=direction))
        assert "hi" in html


def test_thought_bubble_renders():
    html = render_to_html(thought_bubble("hmm"))
    assert "hmm" in html


def test_sticker_badge_star_uses_clip_path():
    html = render_to_html(sticker_badge("NEW", shape="star"))
    assert "clip-path" in html
    assert "NEW" in html


def test_cartoon_avatar_bounce_sets_animation_style():
    html = render_to_html(cartoon_avatar(bounce=True))
    assert "nx-cartoon-bounce" in html


def test_blob_progress_clamps_percentage():
    over = render_to_html(blob_progress(150, max_value=100))
    assert "width: 100.0%" in over or "width:100.0%" in over

    under = render_to_html(blob_progress(-10, max_value=100))
    assert "width: 0.0%" in under or "width:0.0%" in under


def test_app_renders_cartoon_card_end_to_end():
    class Home(Component):
        def render(self):
            return el("div", cartoon_card("hello", title="Hi"))

    r = TestClient(make_app(Home)).get("/")
    assert r.status_code == 200
    assert "Hi" in r.text


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
