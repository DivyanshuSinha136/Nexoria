import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from nexoria.core.element import el
from nexoria.render.html import render_to_html
from nexoria.std.icons import Icon, IconNotFoundError, list_icons, has_icon, icon_count


def test_bundled_icon_count_matches_vendored_set():
    # Bootstrap Icons 1.13.1, sprite file excluded (per-icon SVGs only).
    assert icon_count() == 2078


def test_has_icon_true_for_known_name():
    assert has_icon("house-door-fill") is True


def test_has_icon_false_for_unknown_name():
    assert has_icon("this-icon-does-not-exist") is False


def test_list_icons_is_sorted_and_contains_known_names():
    names = list_icons()
    assert names == sorted(names)
    assert "github" in names
    assert "alarm-fill" in names


def test_unknown_icon_raises_icon_not_found_error():
    with pytest.raises(IconNotFoundError):
        Icon("this-icon-does-not-exist").to_element()


def test_icon_renders_as_real_svg_element_not_raw_string():
    element = Icon("house").to_element()
    assert element.tag == "svg"
    assert any(c.tag == "path" for c in element.children)


def test_icon_html_output_is_inline_svg_markup():
    html = render_to_html(Icon("house").to_element())
    assert html.startswith("<svg")
    assert "<path" in html
    assert 'aria-hidden="true"' in html  # decorative by default


def test_icon_size_overrides_width_and_height():
    html = render_to_html(Icon("house", size="2rem").to_element())
    assert 'width="2rem"' in html
    assert 'height="2rem"' in html


def test_icon_color_overrides_fill():
    html = render_to_html(Icon("house", color="var(--nx-primary)").to_element())
    assert 'fill="var(--nx-primary)"' in html


def test_icon_title_adds_accessible_title_and_drops_aria_hidden():
    html = render_to_html(Icon("github", title="GitHub profile").to_element())
    assert "<title>GitHub profile</title>" in html
    assert 'role="img"' in html
    assert "aria-hidden" not in html


def test_icon_class_merges_with_existing_bi_class():
    html = render_to_html(Icon("house", class_="spin").to_element())
    assert "bi-house" in html
    assert "spin" in html


def test_icon_drops_into_el_tree_via_to_element_protocol():
    html = render_to_html(el("button", Icon("cart-fill"), " Add to cart"))
    assert "<button" in html
    assert "<svg" in html
    assert "Add to cart" in html


def test_multi_path_icon_renders_every_path():
    # emoji-smile.svg has two <path> children in the source SVG.
    element = Icon("emoji-smile").to_element()
    assert sum(1 for c in element.children if c.tag == "path") == 2


def test_icon_parsing_is_cached_across_calls():
    from nexoria.std.icons.icon import _parse_svg
    first = _parse_svg("house")
    second = _parse_svg("house")
    assert first is second
