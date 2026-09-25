# `nexoria.std.scroll`

> Page-scrolling tools: progress bar, back-to-top button, smooth in-page anchors, scrollable container.

| | |
|---|---|
| **Import** | `from nexoria.std.scroll import scroll_runtime, scroll_progress_bar, scroll_to_top_button, anchor_link, smooth_scroll_container` |
| **Needs** | `scroll_runtime()` once per page for the progress bar and back-to-top button |

```python
el("div",
   scroll_runtime(),
   scroll_progress_bar(color="var(--nx-primary)", height="4px"),
   scroll_to_top_button(threshold=300),
   anchor_link("Pricing", "pricing", offset=72),        # smooth-scrolls to id="pricing"; doesn't touch the URL hash
   smooth_scroll_container(*messages, height="400px"))
```

`anchor_link`'s `offset` shifts the stop point up by that many pixels (to clear a sticky header). `anchor_link` and `smooth_scroll_container` are self-contained.

## API reference

### Functions

#### `scroll_runtime() -> Element`

A `<script>` `Element` powering `scroll_progress_bar()` and `scroll_to_top_button()`. Render it once per page.

#### `scroll_progress_bar(*, color: str = 'var(--nx-primary)', height: str = '4px') -> Element`

A fixed bar at the top of the page whose width tracks scroll progress. Needs `scroll_runtime()`.

#### `scroll_to_top_button(*, threshold: int = 300, label: str = '↑') -> Element`

A "back to top" button, hidden until the page is scrolled past `threshold` px. Needs `scroll_runtime()`.

#### `anchor_link(label: str, target_id: str, *, offset: int = 0, class_: Optional[str] = None) -> Element`

`anchor_link("Pricing", "pricing")`. Smoothly scrolls to the element with `id="pricing"` instead of the browser's instant jump, and (unlike a plain `#pricing` href) doesn't touch the URL hash. `offset` shifts the stop point up by that many pixels (e.g. to clear a sticky navbar).

#### `smooth_scroll_container(*children: Any, height: str = '400px', class_: Optional[str] = None) -> Element`

A scrollable panel with native smooth scrolling for its internal content (e.g. a chat log, a long list).

### Constants

| Name | Value |
|---|---|
| `SCROLL_RUNTIME_JS` | `'(function () {\n  if (window.__nxScroll) return;\n  window.__nxScroll = true;\n\n  function update() {\n    var doc = document.documentElement;\n    var scrolled = doc.scrollTop \|\| document.body.scrollTop;\n    var height = (doc.scrollHeight \|\| document.body.scrollHeight) - doc.clientHeight;\n    var pct = height > 0 ? (scrolled / height) * 100 : 0;\n\n    document.querySelectorAll("[data-nx-scroll-progress]").fo…` |
