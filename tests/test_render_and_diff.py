import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nexoria.core.element import el, text
from nexoria.render.html import render_to_html
from nexoria.render.diff import diff


def test_el_builds_tree_and_text_children():
    tree = el("div", el("h1", "Hi"), "raw text", key="root")
    assert tree.tag == "div"
    assert tree.key == "root"
    assert tree.children[0].tag == "h1"
    assert tree.children[1].is_text()
    assert tree.children[1].text == "raw text"


def test_class_underscore_remap():
    node = el("div", class_="box", key="k")
    assert node.props["class"] == "box"
    assert "class_" not in node.props


def test_event_handlers_extracted_not_serialized():
    called = {"n": 0}
    node = el("button", "Click", on_click=lambda e: called.__setitem__("n", called["n"] + 1))
    assert "on_click" not in node.props
    assert "click" in node._handler_ids
    d = node.to_dict()
    assert "on_click" not in d["props"]
    assert "click" in d["events"]


def test_render_to_html_basic():
    tree = el("div", el("p", "hello"), class_="app")
    html = render_to_html(tree)
    assert html == '<div class="app"><p>hello</p></div>'


def test_render_to_html_void_tag():
    tree = el("img", src="a.png")
    html = render_to_html(tree)
    assert html == '<img src="a.png"/>'


def test_script_tag_content_is_not_html_escaped():
    """
    Regression test: <script>/<style> content is raw text per the HTML
    spec and must never be HTML-entity-escaped, or embedded JSON/JS
    breaks (quotes/ampersands become &quot;/&amp;). A literal "</" in
    the content must still be guarded against prematurely closing the
    tag, without corrupting otherwise-valid JSON.
    """
    import json
    payload = json.dumps({"msg": 'a & b "quoted" </script> <tag>'})
    node = el("script", payload, type="application/json")
    html = render_to_html(node)
    assert "&amp;" not in html and "&quot;" not in html
    start = html.index(">") + 1
    end = html.rindex("</")
    inner_text = html[start:end]
    recovered = json.loads(inner_text.replace("<\\/script>", "</script>"))
    assert recovered == {"msg": 'a & b "quoted" </script> <tag>'}


def test_ordinary_text_still_html_escaped():
    node = el("p", "a & b <script>alert(1)</script>")
    html = render_to_html(node)
    assert "&amp;" in html
    assert "&lt;script&gt;" in html
    assert "<script>alert(1)</script>" not in html


def test_boolean_attrs_false_omits_attribute_not_string_false():
    """
    Regression test: HTML boolean attributes (controls, autoplay, loop,
    muted, ...) are true if PRESENT regardless of their string value --
    rendering `controls="False"` would still mean controls are ON in a
    real browser. False must omit the attribute entirely.
    """
    assert render_to_html(el("video", controls=True)) == "<video controls></video>"
    assert render_to_html(el("video", controls=False)) == "<video></video>"
    assert render_to_html(el("audio", autoplay=True, loop=False)) == '<audio autoplay></audio>'


def test_el_calls_to_element_on_declarative_wrapper_objects():
    """
    Regression test: every declarative wrapper across the framework
    (Icon, QRCode, Barcode, Chart, Grid, Map, Webcam, Animation,
    VideoPlayer, BabylonScene, SplineScene, VRMAvatar, ...) exposes a
    `.to_element()` method rather than being an Element itself. Passing
    one directly as a child (forgetting the explicit `.to_element()`
    call -- an easy, recurring mistake since EVERY one of these follows
    the same pattern) used to silently fall through to `text(c)` and
    render as a stringified Python repr instead of the actual widget.
    `el()` now recognizes the `.to_element()` protocol automatically.
    """
    class FakeWidget:
        def to_element(self):
            return el("span", "real element", class_="widget")

    node = el("div", FakeWidget())
    assert len(node.children) == 1
    assert node.children[0].tag == "span"
    assert node.children[0].props["class"] == "widget"
    html = render_to_html(node)
    assert html == '<div><span class="widget">real element</span></div>'


def test_el_to_element_protocol_works_inside_starred_list():
    class FakeWidget:
        def __init__(self, n):
            self.n = n
        def to_element(self):
            return el("i", str(self.n))

    widgets = [FakeWidget(i) for i in range(3)]
    node = el("div", *widgets)
    assert len(node.children) == 3
    assert [c.tag for c in node.children] == ["i", "i", "i"]
    assert [c.children[0].text for c in node.children] == ["0", "1", "2"]


def test_el_to_element_returning_none_is_skipped():
    """Some wrappers' to_element()-adjacent helpers return None when
    there's nothing to render (e.g. VideoPlayer.theme_element() with no
    theme set) -- that must still be safely skippable as a child."""
    class OptionalWidget:
        def to_element(self):
            return None

    node = el("div", OptionalWidget(), "text stays")
    assert len(node.children) == 1
    assert node.children[0].text == "text stays"


def test_diff_text_change():
    old = el("p", "count: 0")
    new = el("p", "count: 1")
    patches = diff(old, new)
    assert any(p.kind == "text" for p in patches)


def test_diff_no_change_no_patches():
    old = el("div", el("p", "same"))
    new = el("div", el("p", "same"))
    patches = diff(old, new)
    assert patches == []

def test_diff_prop_change():
    old = el("div", class_="a")
    new = el("div", class_="b")
    patches = diff(old, new)
    assert len(patches) == 1
    assert patches[0].kind == "update_props"
    assert patches[0].payload["props"]["class"] == "b"


def test_diff_keyed_list_reorder_detects_no_spurious_replace():
    old = el("ul", el("li", "a", key="a"), el("li", "b", key="b"))
    new = el("ul", el("li", "b", key="b"), el("li", "a", key="a"))
    patches = diff(old, new)
    # keyed diff should not blow the whole subtree away
    assert all(p.kind != "replace" for p in patches)


def test_diff_keyed_list_item_removed_uses_remove_not_positional_diff():
    """
    Regression test: a keyed list whose length changes must still use
    identity-based (keyed) diffing, not fall back to comparing children
    positionally. The old buggy condition required old and new child
    counts to match before treating a list as "fully keyed" at all,
    which defeated the entire purpose of keyed diffing (handling
    insertions/removals) -- a 3-item keyed list shrinking to 2 items
    produced a spurious "text" patch (comparing the wrong two nodes by
    position) instead of a single clean "remove".
    """
    old = el("ul", el("li", "a", key="a"), el("li", "b", key="b"), el("li", "c", key="c"))
    new = el("ul", el("li", "a", key="a"), el("li", "c", key="c"))
    patches = diff(old, new)
    kinds = [p.kind for p in patches]
    assert kinds == ["remove"], kinds
    assert patches[0].path == [1]


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
