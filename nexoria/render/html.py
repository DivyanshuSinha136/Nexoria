"""
nexoria.render.html
=====================
Serializes an Element tree to real HTML for the first server-rendered
paint (SSR). Event handlers are stripped here and re-attached client
side by the hydration runtime using the `data-nx-ev` markers, so the
initial payload is pure markup with no inline JS.
"""

from __future__ import annotations
from html import escape
from ..core.element import Element, VOID_TAGS

_BOOL_ATTRS = {
    "checked", "disabled", "selected", "readonly", "multiple", "hidden",
    "controls", "autoplay", "loop", "muted", "playsinline", "required",
    "reversed", "async", "defer", "novalidate", "ismap", "itemscope",
}

# Per the HTML spec, the text content of <script>/<style> is raw text, not
# HTML -- browsers never decode entities inside them. Escaping it with
# html.escape() (as ordinary element text needs) would corrupt inline JS
# or JSON (e.g. `"a & b"` becoming `"a &amp; b"`, breaking JSON.parse).
_RAW_TEXT_TAGS = {"script", "style"}


def _attrs_to_str(el: Element) -> str:
    parts = []
    for k, v in el.props.items():
        if k in _BOOL_ATTRS:
            if v:
                parts.append(k)
            continue
        parts.append(f'{k}="{escape(str(v), quote=True)}"')
    for event, handler_id in el._handler_ids.items():
        parts.append(f'data-nx-on-{event}="{handler_id}"')
    return (" " + " ".join(parts)) if parts else ""


def render_to_html(root: Element, indent: int = 0, pretty: bool = False, raw: bool = False) -> str:
    """Recursively render an Element (or Component.render() output) to HTML.

    `raw` is True while inside a <script>/<style> element: text children
    are emitted verbatim (only guarding against a literal "</" that would
    prematurely close the tag) instead of HTML-escaped.
    """
    pad = ("  " * indent) if pretty else ""
    nl = "\n" if pretty else ""

    if root.is_text():
        if raw:
            # Prevent a literal "</" in raw content (e.g. a JSON string
            # containing "</script>") from closing the tag early. "\/" is
            # a no-op, valid escape in both JSON strings and JS source, so
            # this can't corrupt otherwise-valid content.
            text_out = root.text.replace("</", "<\\/")
            return f"{pad}{text_out}{nl}"
        return f"{pad}{escape(root.text)}{nl}"

    attrs = _attrs_to_str(root)
    if root.is_void():
        return f"{pad}<{root.tag}{attrs}/>{nl}"

    child_raw = raw or root.tag in _RAW_TEXT_TAGS
    if not root.children:
        return f"{pad}<{root.tag}{attrs}></{root.tag}>{nl}"

    inner = "".join(render_to_html(c, indent + 1, pretty, raw=child_raw) for c in root.children)
    if pretty:
        return f"{pad}<{root.tag}{attrs}>\n{inner}{pad}</{root.tag}>\n"
    return f"{pad}<{root.tag}{attrs}>{inner}</{root.tag}>"


def render_document(
    body_html: str,
    hydration_script: str,
    title: str = "Nexoria App",
    extra_head: str = "",
    stylesheets: list[str] | None = None,
) -> str:
    """Wrap a rendered component tree in a full HTML document for SSR."""
    styles = "\n".join(f'<link rel="stylesheet" href="{s}">' for s in (stylesheets or []))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<script>
/* Set the theme attribute before any CSS is applied, so a saved
   light/dark preference (or the OS preference, on first visit) takes
   effect on first paint instead of flashing the server-rendered
   default theme and then switching. Deliberately not deferred. */
(function() {{
  try {{
    var saved = localStorage.getItem("nx-theme");
    var theme = saved || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
    if (theme === "light") document.documentElement.setAttribute("data-nx-theme", "light");
  }} catch (e) {{ /* localStorage unavailable (privacy mode, etc.) -- fall back to server default */ }}
}})();
</script>
{styles}
{extra_head}
</head>
<body>
<div id="nx-root">{body_html}</div>
<script src="/_nexoria/runtime.js" defer></script>
<script id="nx-hydration-data" type="application/json">{hydration_script}</script>
</body>
</html>"""
