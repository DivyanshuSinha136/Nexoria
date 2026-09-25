# `nexoria.std.physics2d`

> Projectile motion without a license: velocity, angle, gravity, friction, spin and floor bounce, in the spirit of GSAP's Physics2DPlugin, driven by one `requestAnimationFrame` loop.

| | |
|---|---|
| **Import** | `from nexoria.std.physics2d import physics2d_runtime, physics2d_element, physics2d_burst` |
| **Needs** | `physics2d_runtime()` once per page |

```python
physics2d_runtime()
physics2d_element(el("span", "🚀"), velocity=400, angle=-70, spin=180, trigger="click")
physics2d_burst("Ship it!", count=30, direction=-90, spread=140)      # one-click confetti
```

- **`angle`** is in degrees with 0 = right and 90 = down, so `-90` is straight up.
- **`floor`**: `"none"` (default), `"parent"` or `"viewport"`. `"parent"` needs the element inside a `position: relative/absolute` container; `"viewport"` is measured once at launch. `bounce` = 0 settles the instant it touches the floor; a value between 0 and 1 loses that fraction of energy on each bounce.
- **`trigger`**: `"auto"` (on load), `"click"`, `"hover"`, or `"event"` — start only when a `nx:physics2d:start` DOM event is dispatched on the element (what `physics2d_burst` uses to fire many particles from one click).
- `remove_on_settle` removes the element once it stops.
- `physics2d_burst(trigger_label, count, spread, direction, min_velocity, max_velocity, gravity, friction, colors, size, shape)` renders a button plus particles.

## API reference

### Functions

#### `physics2d_runtime() -> Element`

A `<script>` `Element` carrying the Physics2D engine. Render it once per page.

#### `physics2d_element(*children: Any, velocity: float = 300, angle: float = -60, gravity: float = 980, friction: float = 0.02, spin: float = 0, bounce: float = 0, floor: str = 'none', trigger: str = 'auto', remove_on_settle: bool = False, class_: Optional[str] = None, style: Optional[dict] = None) -> Element`

`physics2d_element(el("span", "🚀"), velocity=400, angle=-70, spin=180)`.

Gives its children an initial `velocity` (px/s) launched at `angle` degrees (0 = right, 90 = down, so -90 is straight up, matching screen-space y-down coordinates), then simulates `gravity` (px/s^2, always downward), `friction` (0-1, velocity decay per frame), and optional constant `spin` (deg/s) -- exactly the knobs GSAP's Physics2DPlugin exposes, just applied by `nexoria.std.physics2d.runtime`'s own `requestAnimationFrame` loop rather than a licensed plugin.

`floor`: "none" (flies forever/off-screen) | "parent" (bounces off the bottom of the nearest positioned ancestor -- this element needs to sit inside a `position: relative`/`absolute` container for that to work) | "viewport" (bounces off the bottom of the browser window, measured once at launch). `bounce`: 0 settles the instant it touches the floor; 0 < bounce < 1 loses that fraction of energy each bounce.

`trigger`: "auto" (starts the moment the page loads) | "click" | "hover" | "event" (starts only when a `"nx:physics2d:start"` DOM event is dispatched on this element -- see `physics2d_burst()`, which uses this to fire many particles from one click).

Moves via `transform: translate() rotate()`, so it never disturbs layout -- but that also means, unless you set `style={"position": "absolute", ...}` yourself (or `floor` isn't "none"), it'll fly right over whatever's laid out after it. Needs `physics2d_runtime()` rendered once per page.

#### `physics2d_burst(trigger_label: str = 'Celebrate!', *, count: int = 20, spread: float = 180, direction: float = -90, min_velocity: float = 200, max_velocity: float = 500, gravity: float = 900, friction: float = 0.02, colors: Sequence[str] = ('#FF6B6B', '#FFD93D', '#4ECDC4', '#6FA8FF', '#B892FF'), size: str = '10px', shape: str = 'circle') -> Element`

`physics2d_burst("Ship it!", count=30, direction=-90, spread=140)`.

`direction` is the center angle of the burst cone in degrees (-90 = straight up, matching `physics2d_element`'s convention); `spread` is the cone's total width around it. Each particle gets a randomized angle within the cone and a randomized speed between `min_velocity` and `max_velocity` (computed once, in Python, at render time -- only the small per-particle stagger before launch is randomized in JS, so the burst doesn't fire as one perfectly synchronized wall of particles).

Needs `physics2d_runtime()` rendered once per page.

### Constants

| Name | Value |
|---|---|
| `PHYSICS2D_RUNTIME_JS` | `'(function () {\n  if (window.__nxPhysics2D) return;\n  window.__nxPhysics2D = true;\n\n  function startOne(elm) {\n    if (elm.getAttribute("data-nx-physics2d-running") === "true") return;\n    elm.setAttribute("data-nx-physics2d-running", "true");\n    elm.removeAttribute("data-nx-physics2d-settled");\n\n    var v = parseFloat(elm.getAttribute("data-nx-physics2d-velocity")) \|\| 0;\n    var angleDeg = parseFloat(e…` |

The element moves with `transform`, so it never disturbs layout — but unless you position it absolutely (or set a floor) it flies over whatever follows it.
