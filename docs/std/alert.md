# `nexoria.std.alert`

> Feedback surfaces: dismissible banner, auto-dismissing toast, inline alert. Fully self-contained (client-side).

| | |
|---|---|
| **Import** | `from nexoria.std.alert import alert_banner, toast, inline_alert` |
| **Variants** | `info | success | warning | danger` |

```python
alert_banner("Your trial ends in 3 days.", variant="warning", title="Heads up")
toast("Saved!", variant="success", duration=4000, position="bottom-right")
inline_alert("Passwords don't match", variant="danger")
```

- `alert_banner(message, variant, title, dismissible=True, icon)` — has a close button.
- `toast(message, variant, title, duration=4000, position="bottom-right")` — slides in and removes itself after `duration` ms or on click; `duration=0` requires a manual dismiss. Positions: `top-right`, `top-left`, `bottom-right`, `bottom-left`.
- `inline_alert(message, variant)` — compact, not dismissible, for forms.

Dismissal is a literal `onclick` on the element itself: no server round-trip, no shared runtime.

## API reference

### Functions

#### `alert_banner(message: str, *, variant: str = 'info', title: Optional[str] = None, dismissible: bool = True, icon: Optional[Element] = None) -> Element`

`alert_banner("Your trial ends in 3 days.", variant="warning", title="Heads up")`. `variant`: "info" | "success" | "warning" | "danger".

#### `toast(message: str, *, variant: str = 'info', title: Optional[str] = None, duration: int = 4000, position: str = 'bottom-right') -> Element`

`toast("Saved!", variant="success")`. Slides in, then dismisses itself after `duration` ms (or immediately on click). Pass `duration=0` to require a manual dismiss.

Renders as a fixed-position element -- mount it directly in your page tree (e.g. conditionally, from a `Component`'s `render()`) rather than pre-rendering a stack of them; each carries its own unique id so several can coexist.

#### `inline_alert(message: str, *, variant: str = 'info') -> Element`

A compact, non-dismissible alert line for forms/fields: `inline_alert("Passwords don't match", variant="danger")`.
