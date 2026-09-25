# `nexoria.js` — client-side JavaScript from Python

> Write the JavaScript that runs **in the browser** without injection risk: `js()`, `Script`, `JSFunction`.

| | |
|---|---|
| **Import** | `from nexoria.js import js, Script, JSFunction` |
| **Enabled by** | Nothing |
| **Not to be confused with** | [`nexoria.native.js`](native.md#3-embedded-js-engine), which runs JS **on the server** |

## `js(template, **values)`

Replaces each `{name}` with `json.dumps(value)`, so strings become correctly quoted JS literals and lists/dicts/bools/`None` become their JS equivalents. A value containing quotes or `</script>` cannot break out of the expression. A missing value raises `KeyError`.

```python
js("alert({msg})", msg='it\'s a "test"')     # alert("it's a \"test\"")
js("plot({data})", data=[1, 2, 3])            # plot([1, 2, 3])
```

`{name}` only matches `\w+` placeholders; other braces (object literals, blocks) are left alone.

## `Script(code, module=False, defer=False, async_=False, on_ready=False)`

A `<script>` element usable as a child anywhere. `on_ready=True` wraps the code so it runs after the DOM is parsed whether the tag executes before or after `DOMContentLoaded`. Content is raw text (see [`render`](render.md#1-html-serialization-htmlpy)) — no escaping needed.

## `JSFunction(name, *params, body="")`

```python
greet = JSFunction("nxGreet", "name", body="alert('Hello, ' + name);")

el("div",
   greet.script_element(),                                  # defines window.nxGreet (once per page)
   el("button", "Say hi", onclick=greet.call_attr(js("{n}", n="World"))))
```

`call_attr(*args)` takes **already-JS-encoded** argument strings — build each with `js(...)` or pass an expression like `"event"` or `"this"`.

Remember: a *string* `onclick=` runs in the browser; a *callable* `on_click=` runs on the server.

## API reference

### Classes

#### `class Script(code: str, module: bool = False, defer: bool = False, async_: bool = False, on_ready: bool = False) -> None`

A raw `<script>` block, safe to embed directly as a child anywhere.

`module=True` renders `type="module"` (for `import`/`export` syntax). `on_ready=True` wraps the code so it runs after the DOM is parsed regardless of where the script tag ends up in the page (handles both the "script runs before DOMContentLoaded" and "script runs after, DOMContentLoaded already fired" cases).

- **`.to_element()`**

#### `class JSFunction(name: str, *params: str, body: str = '')`

Define a reusable, named client-side function directly from Python, then reference it safely from `onclick=`/etc. without hand-writing call syntax yourself.

`body` is the function's raw JS statements; `params` are its parameter names (plain identifiers). `.call_attr(*args)` builds the call expression from already-JS-encoded argument strings -- use `js(...)` to build each argument safely from a Python value, or pass a literal expression (e.g. `"event"` for the DOM event object, `"this"` for the calling element).

- **`.call_attr(*args: str) -> str`**
- **`.script_element()`** — Defines `window.<name>` once. Including this more than once on the same page is harmless (redefining a function is a no-op concern, not an error) -- but only needs to appear once.

### Functions

#### `js(template: str, **values: Any) -> str`

Safely interpolate Python values into a JS template string. Each `{name}` placeholder is replaced with `json.dumps(value)` -- strings become properly quoted/escaped JS string literals, and numbers/lists/dicts/booleans/None all convert to their real JS equivalents -- never raw string substitution, so a value containing `"`, `</script>`, or anything else JS-syntax-breaking can't escape the expression it's placed into.
