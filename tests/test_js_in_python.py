import sys, os, json, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nexoria.js import js, Script, JSFunction
from nexoria.core.element import el
from nexoria.render.html import render_to_html


# ---- js() safe interpolation ---------------------------------------------

def test_js_interpolates_string_as_json_encoded_literal():
    assert js("alert({msg})", msg="hello") == 'alert("hello")'


def test_js_interpolates_numbers_lists_dicts_booleans_none():
    assert js("f({n})", n=42) == "f(42)"
    assert js("f({n})", n=[1, 2, 3]) == "f([1, 2, 3])"
    assert js("f({n})", n={"a": 1}) == 'f({"a": 1})'
    assert js("f({n})", n=True) == "f(true)"
    assert js("f({n})", n=None) == "f(null)"


def test_js_multiple_placeholders():
    assert js("f({a}, {b})", a=1, b="x") == 'f(1, "x")'


def test_js_missing_placeholder_raises_keyerror():
    import pytest
    with pytest.raises(KeyError):
        js("f({missing})")


def test_js_neutralizes_quote_injection_attempt():
    """A value containing quotes/backslashes must stay inside one JSON
    string literal, not break out into raw JS syntax."""
    evil = '"; alert(1); //'
    result = js("f({v})", v=evil)
    # must round-trip through JSON back to the exact original string --
    # proof it was JSON-encoded, not raw-pasted
    inner = result[len("f("):-1]
    assert json.loads(inner) == evil
    # and must not contain an unescaped quote that could close the string early
    assert 'f("";' not in result


def test_js_neutralizes_script_tag_injection_attempt():
    evil = '</script><script>alert(1)</script>'
    result = js("f({v})", v=evil)
    inner = result[len("f("):-1]
    assert json.loads(inner) == evil


# ---- Script -----------------------------------------------------------

def test_script_to_element_is_real_script_tag():
    node = Script("console.log(1)").to_element()
    assert node.tag == "script"
    html = render_to_html(node)
    assert html == "<script>console.log(1)</script>"


def test_script_module_flag_sets_type_module():
    node = Script("import x from 'y';", module=True).to_element()
    html = render_to_html(node)
    assert 'type="module"' in html


def test_script_defer_async_flags():
    node = Script("x()", defer=True, async_=True).to_element()
    html = render_to_html(node)
    assert " defer" in html
    assert " async" in html


def test_script_content_not_html_escaped():
    """Raw JS syntax (quotes, &, <, >) must survive unescaped -- <script>
    content is raw text per the HTML spec, not HTML-escaped ordinary text."""
    node = Script("if (a < b && c > d) { x = 'quoted'; }").to_element()
    html = render_to_html(node)
    assert "&amp;" not in html
    assert "&lt;" not in html
    assert "if (a < b && c > d)" in html


def test_script_embeds_directly_as_el_child_via_to_element_protocol():
    """Dogfoods the el() .to_element() auto-coercion fix: Script must
    work as a bare child, not just via an explicit .to_element() call."""
    node = el("div", Script("console.log(1)"))
    assert len(node.children) == 1
    assert node.children[0].tag == "script"


def test_script_on_ready_wraps_code_for_dom_ready():
    node = Script("doThing();", on_ready=True).to_element()
    html = render_to_html(node)
    assert "DOMContentLoaded" in html
    assert "doThing();" in html
    assert "readyState" in html


def test_script_injection_attempt_defused_end_to_end():
    """
    Full pipeline: a malicious value flows through js() into Script and
    out through render_to_html. What actually matters for HTML/script
    parsing safety is that no literal, unescaped `</script>` sequence
    appears anywhere except the one real closing tag our own template
    adds at the end -- a browser's HTML tokenizer in "script data
    state" only breaks out on that exact literal sequence; a bare
    `<script>` (opening, no slash) appearing inside another script's
    raw text content is inert data, not a security concern, so it's
    NOT what this test should assert against.
    """
    evil = '"); alert(1); //</script><script>alert(2)//'
    node = el("div", Script(js("run({v})", v=evil)))
    html = render_to_html(node)
    # every literal, unescaped "</" in the output must be one of the
    # two genuine closing tags our own template added (</script></div>)
    # at the very end -- never one from inside the injected content.
    real_closing = "</script></div>"
    assert html.endswith(real_closing)
    before_closing = html[: -len(real_closing)]
    assert "</" not in before_closing, before_closing


# ---- JSFunction -----------------------------------------------------

def test_jsfunction_script_element_defines_window_function():
    f = JSFunction("nxGreet", "name", body="return 'Hi ' + name;")
    node = f.script_element()
    html = render_to_html(node)
    assert "window.nxGreet = function(name)" in html
    assert "return 'Hi ' + name;" in html


def test_jsfunction_call_attr_builds_call_expression():
    f = JSFunction("nxGreet", "name")
    assert f.call_attr('"World"') == 'window.nxGreet("World")'


def test_jsfunction_call_attr_with_js_helper():
    f = JSFunction("nxGreet", "name")
    attr = f.call_attr(js("{n}", n="World"))
    assert attr == 'window.nxGreet("World")'


def test_jsfunction_multiple_params():
    f = JSFunction("nxAdd", "a", "b", body="return a + b;")
    html = render_to_html(f.script_element())
    assert "function(a, b)" in html


def test_jsfunction_no_params():
    f = JSFunction("nxNoop", body="return 1;")
    html = render_to_html(f.script_element())
    assert "function()" in html


def test_jsfunction_end_to_end_generates_valid_executable_js():
    """Run the actual generated JS through Node to prove it's real,
    correct, executable JavaScript -- not just syntactically-plausible
    Python string formatting. Node has no `window` global (it isn't a
    browser), so this harness shims one, same as every other
    browser-target verification in this project's test suite."""
    f = JSFunction("nxAdd", "a", "b", body="return a + b;")
    func_def = render_to_html(f.script_element())
    inner = func_def[len("<script>"):-len("</script>")]
    script = "var window = globalThis;\n" + inner + "\nconsole.log(window.nxAdd(2, 3));"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "5"


def test_jsfunction_button_onclick_end_to_end():
    """A button wired via JSFunction.call_attr renders a correct,
    properly-escaped onclick attribute alongside the function definition."""
    greet = JSFunction("nxGreet", "name", body="alert('Hello, ' + name);")
    node = el("div", greet.script_element(), el("button", "Hi", onclick=greet.call_attr(js("{n}", n="World"))))
    html = render_to_html(node)
    assert "window.nxGreet = function(name)" in html
    assert 'onclick="window.nxGreet(&quot;World&quot;)"' in html


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
