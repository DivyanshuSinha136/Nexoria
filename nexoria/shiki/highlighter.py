"""
nexoria.shiki.highlighter
============================
Optional syntax highlighting using Shiki (the same highlighter that
powers VS Code and GitHub -- real TextMate grammars, not a toy
regex highlighter).

Unlike every other integration in Nexoria, Shiki's real dependency
tree could not be hand-assembled into an import map: even its
CDN-oriented "bundle/web" entry pulls in the "unified/rehype" markdown-
AST ecosystem transitively (hast-util-to-html alone pulls in 10+
further packages). This is exactly the scenario bundling CDN services
like esm.sh exist for -- they resolve and bundle a package's full
dependency tree server-side into one flat ES module. esm.sh is also
what Shiki's own documentation recommends for browser/CDN usage
without a bundler. This is a deliberately different verification
posture from Nexoria's other integrations (which point directly at a
package's own published, independently-checked files) -- flagged here
explicitly rather than presented as equivalent.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import json

SHIKI_VERSION = "1.24.0"
SHIKI_CDN = f"https://esm.sh/shiki@{SHIKI_VERSION}/bundle/web"
SHIKI_IMPORTS = {"shiki": SHIKI_CDN}
SHIKI_ADAPTER_TAG = '<script src="/_nexoria/shiki-adapter.js" type="module" defer></script>'


@dataclass
class CodeBlock:
    """
    A syntax-highlighted code block.

        CodeBlock("def hello():\\n    print('hi')", lang="python", theme="github-dark")

    Highlighting happens client-side (Shiki loads the requested
    language grammar + theme on demand); the raw code is still present
    in the initial HTML (in a hidden `<pre>`) so it's readable/indexable
    before JS runs.
    """
    code: str
    lang: str = "python"
    theme: str = "github-dark"
    block_id: Optional[str] = None

    def __post_init__(self):
        if self.block_id is None:
            import uuid
            self.block_id = f"nx-shiki-{uuid.uuid4().hex[:8]}"

    def to_element(self):
        from ..core.element import el
        spec = json.dumps({"code": self.code, "lang": self.lang, "theme": self.theme})
        return el(
            "div",
            el("pre", el("code", self.code)),
            id=self.block_id,
            **{"class": "nx-shiki-block", "data-nx-shiki": spec},
        )
