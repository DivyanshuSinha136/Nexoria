"""
nexoria.js.script
====================
"JS-in-Python": write client-side JavaScript directly in your Python
files, safely.

This is the *client-side authoring* story -- for running real JS/npm
packages *server-side* from Python, see `nexoria.native.js` (the
embedded QuickJS engine) instead. Different problem, different module:
this one is about writing the JS that ends up in the browser, cleanly,
from Python source, with no injection risk when Python values flow
into it.

Three pieces:
  * `js(template, **values)` -- safely interpolate Python values into a
    JS template string (each value is JSON-encoded, never pasted in
    raw), so untrusted/dynamic values can't break out of the
    surrounding JS syntax.
  * `Script(code)` -- wraps raw JS as a real `<script>` element via the
    `.to_element()` protocol every declarative wrapper in Nexoria
    follows, so `el("div", Script("..."))` just works. Content is
    emitted as genuine raw text (see render/html.py's script/style
    handling) -- ordinary JS syntax needs no escaping.
  * `JSFunction(name, *params, body=...)` -- define a reusable, named
    client-side function from Python once, then reference it safely
    from `onclick=`/etc. without hand-writing call syntax yourself.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import json
import re

_PLACEHOLDER = re.compile(r"\{(\w+)\}")


def js(template: str, **values: Any) -> str:
    """
    Safely interpolate Python values into a JS template string. Each
    `{name}` placeholder is replaced with `json.dumps(value)` --
    strings become properly quoted/escaped JS string literals, and
    numbers/lists/dicts/booleans/None all convert to their real JS
    equivalents -- never raw string substitution, so a value
    containing `"`, `</script>`, or anything else JS-syntax-breaking
    can't escape the expression it's placed into.

        js("alert({msg})", msg="it's a \\"test\\"")
        # -> 'alert("it\\'s a \\\\"test\\\\"")'   (a single, safe JS string literal)

        js("plot({data})", data=[1, 2, 3])
        # -> "plot([1, 2, 3])"
    """
    def replace(match: re.Match) -> str:
        name = match.group(1)
        if name not in values:
            raise KeyError(f"js(): no value given for placeholder {{{name}}} in template {template!r}")
        return json.dumps(values[name])
    return _PLACEHOLDER.sub(replace, template)


@dataclass
class Script:
    """
    A raw `<script>` block, safe to embed directly as a child anywhere:

        el("div", ..., Script("console.log('hydrated')"))

    `module=True` renders `type="module"` (for `import`/`export`
    syntax). `on_ready=True` wraps the code so it runs after the DOM
    is parsed regardless of where the script tag ends up in the page
    (handles both the "script runs before DOMContentLoaded" and
    "script runs after, DOMContentLoaded already fired" cases).
    """
    code: str
    module: bool = False
    defer: bool = False
    async_: bool = False
    on_ready: bool = False

    def _final_code(self) -> str:
        if not self.on_ready:
            return self.code
        return (
            "(function(){function __nxRun(){\n" + self.code + "\n}"
            'if(document.readyState==="loading"){'
            'document.addEventListener("DOMContentLoaded",__nxRun);'
            "}else{__nxRun();}})();"
        )

    def to_element(self):
        from ..core.element import el
        props: dict[str, Any] = {}
        if self.module:
            props["type"] = "module"
        if self.defer:
            props["defer"] = True
        if self.async_:
            props["async"] = True
        return el("script", self._final_code(), **props)


@dataclass
class JSFunction:
    """
    Define a reusable, named client-side function directly from
    Python, then reference it safely from `onclick=`/etc. without
    hand-writing call syntax yourself:

        greet = JSFunction("nxGreet", "name", body="alert('Hello, ' + name);")

        el("div",
           greet.script_element(),   # defines window.nxGreet -- include once per page
           el("button", "Say hi",
              onclick=greet.call_attr(js("{n}", n="World"))))

    `body` is the function's raw JS statements; `params` are its
    parameter names (plain identifiers). `.call_attr(*args)` builds the
    call expression from already-JS-encoded argument strings -- use
    `js(...)` to build each argument safely from a Python value, or
    pass a literal expression (e.g. `"event"` for the DOM event object,
    `"this"` for the calling element).
    """
    name: str
    params: list[str] = field(default_factory=list)
    body: str = ""

    def __init__(self, name: str, *params: str, body: str = ""):
        self.name = name
        self.params = list(params)
        self.body = body

    def script_element(self):
        """
        Defines `window.<name>` once. Including this more than once on
        the same page is harmless (redefining a function is a no-op
        concern, not an error) -- but only needs to appear once.
        """
        params_str = ", ".join(self.params)
        code = f"window.{self.name} = function({params_str}) {{\n{self.body}\n}};"
        return Script(code).to_element()

    def call_attr(self, *args: str) -> str:
        return f"window.{self.name}({', '.join(args)})"
