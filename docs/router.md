# `nexoria.router`

> A small path router: static segments, `:param` segments, `*` wildcard, guards, and a not-found component.

| | |
|---|---|
| **Import** | `from nexoria import Router, Route` |
| **Source** | `nexoria/router/router.py` |
| **Enabled by** | Always on (every `App` owns a `Router`) |

## Usage

```python
from nexoria import Router

router = Router()
router.add("/", Home)
router.add("/users/:id", UserProfile, name="user")     # UserProfile(id="42")
router.add("/files/*", FileBrowser)                    # FileBrowser(wildcard="a/b/c.txt")
router.add("/admin", Admin, guards=[lambda params: is_logged_in()])
router.set_not_found(NotFound)
```

`add()` and `set_not_found()` return the router, so calls chain: `Router().add("/", Home).add("/about", About)`.

## Matching rules

- Paths are split on `/`; a trailing slash is optional (`/about` matches `/about/`).
- `:name` matches one segment (`[^/]+`) and becomes a keyword prop of that name.
- `*` matches everything remaining and is delivered as the prop **`wildcard`**.
- **First match wins**, in registration order. Register specific routes (`/users/new`) before parameterised ones (`/users/:id`).
- A route whose **guards** return a falsy value is skipped and matching continues with the next route. Guards receive the dict of *path* parameters only (not query parameters, not the request).
- `resolve(path, **extra_props)` instantiates the component with `**params, **extra_props`. `App` passes the URL **query parameters** as `extra_props`, so `/search?q=py` gives the component `props["q"] == "py"`.
- With no match, `resolve` returns an instance of the not-found component if one is set, otherwise `None` (which makes `App` return its built-in 404 page).

## Navigation

The router runs on the server only. Links are ordinary `<a href>` elements and cause normal page loads; the client runtime does not intercept navigation. Each page load creates a fresh component instance and a fresh session.

## API reference

### Classes

#### `class Router()`

- **`.add(path: str, component: type, name: Optional[str] = None, guards: Optional[list[Callable]] = None) -> 'Router'`**
- **`.match(path: str) -> tuple[Optional[Route], dict]`**
- **`.resolve(path: str, **extra_props)`** — Return an instantiated Component for the given path, or None.
- **`.set_not_found(component: type) -> 'Router'`**

#### `class Route(path: str, component: type, name: Optional[str] = None, guards: list[Callable[[dict], bool]] = ...) -> None`

Route(path: 'str', component: 'type', name: 'Optional[str]' = None, guards: 'list[Callable[[dict], bool]]' = <factory>)
