# `nexoria.shiki`

> Real syntax highlighting (VS Code's TextMate grammars) via Shiki.

| | |
|---|---|
| **Import** | `from nexoria.shiki import CodeBlock` |
| **Enabled by** | `App(shiki=True)` |
| **Library** | Shiki 1.24.0 through **esm.sh** (`https://esm.sh/shiki@1.24.0/bundle/web`) in the import map |
| **Adapter** | `runtime/shiki-adapter.js`; `window.__nexoria__.shiki.mountNew()` |

```python
from nexoria.shiki import CodeBlock
CodeBlock("def hello():\n    print('hi')", lang="python", theme="github-dark")
```

Highlighting runs client-side; the raw code is present in the initial HTML inside a `<pre><code>` so it is readable and indexable before JS runs. Shiki is the one integration that uses a bundling CDN (esm.sh) rather than files verified directly from the package: its dependency tree is too deep to assemble by hand. That is a different trust posture from the others; pin or self-host it if that matters to you.

Want highlighting without JS or a CDN? [`std.lib.code_window`](std/lib.md) has a small built-in Python highlighter.

## API reference

### Classes

#### `class CodeBlock(code: str, lang: str = 'python', theme: str = 'github-dark', block_id: Optional[str] = None) -> None`

A syntax-highlighted code block.

Highlighting happens client-side (Shiki loads the requested language grammar + theme on demand); the raw code is still present in the initial HTML (in a hidden `<pre>`) so it's readable/indexable before JS runs.

- **`.to_element()`**

### Constants

| Name | Value |
|---|---|
| `SHIKI_IMPORTS` | `{'shiki': 'https://esm.sh/shiki@1.24.0/bundle/web'}` |
| `SHIKI_ADAPTER_TAG` | `'<script src="/_nexoria/shiki-adapter.js" type="module" defer></script>'` |
| `SHIKI_CDN` | `'https://esm.sh/shiki@1.24.0/bundle/web'` |
