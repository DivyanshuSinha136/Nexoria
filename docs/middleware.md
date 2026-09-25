# `nexoria.middleware`

> A minimal request hook that runs before a route resolves.

| | |
|---|---|
| **Import** | `from nexoria.middleware import Middleware, CORSMiddleware, LoggingMiddleware` |
| **Source** | `nexoria/middleware/base.py`, `cors.py`, `logging.py` |
| **Registered with** | `app.use(mw)` (chainable) |

## The protocol

```python
from nexoria.middleware import Middleware
from starlette.responses import RedirectResponse

class AuthGuard(Middleware):
    def before_request(self, request):
        if not request.cookies.get("session"):
            return RedirectResponse("/login")     # short-circuit
        return None                               # continue

app.use(AuthGuard())
```

`before_request(request)` receives the Starlette `Request`. Returning a Starlette `Response` stops processing and sends it; returning `None` moves on to the next middleware and then to routing. Middlewares run in registration order.

## Built-ins

| Class | What it does today |
|---|---|
| `LoggingMiddleware` | Logs `METHOD /path` at `INFO` on the `"nexoria"` logger. |
| `CORSMiddleware(allow_origins=None)` | Stores `allow_origins` (default `["*"]`) but `before_request` currently returns `None` — it does **not** add CORS headers or answer preflights. For real CORS, wrap the ASGI app with Starlette's `CORSMiddleware` (`app._asgi`) or use a reverse proxy. |

## Scope

Middleware runs only for **SSR page requests** (the catch-all route). It does not run for the live WebSocket, `/_nexoria/*` assets, `/_nexoria/health`, or `/favicon.ico`. There is no `after_request`/response hook.

## API reference

### Classes

#### `class Middleware()`

- **`.before_request(request) -> Optional[object]`** — Return a Starlette Response to short-circuit the request (e.g. redirect, 401), or None to continue normally.

#### `class CORSMiddleware(allow_origins: Optional[list[str]] = None)`

- **`.before_request(request)`** — Return a Starlette Response to short-circuit the request (e.g. redirect, 401), or None to continue normally.

#### `class LoggingMiddleware()`

- **`.before_request(request)`** — Return a Starlette Response to short-circuit the request (e.g. redirect, 401), or None to continue normally.
