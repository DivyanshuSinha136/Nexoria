# `nexoria.mobile` — Capacitor scaffolding

> `scaffold_capacitor()` wraps a **deployed** Nexoria server in a native iOS/Android WebView shell.

| | |
|---|---|
| **Import** | `from nexoria.mobile import scaffold_capacitor` |
| **CLI** | `nexoria build-mobile --name "My App" --server-url https://your-app.example.com` |
| **Source** | `nexoria/mobile/capacitor.py` |

## The constraint

Capacitor embeds a WebView, not a Python runtime. Nexoria's state lives in a Python server, so the generated app points Capacitor's `server.url` at your **already-deployed** backend. It does not deploy anything, and it is not an offline app. If you need offline-first native behaviour, this architecture is the wrong fit.

## What it generates

`<project>/mobile/`:

- `capacitor.config.json` — `appId`, `appName`, `webDir: "www"`, `server: {url, cleartext}` (`cleartext` is true only for `http://` URLs).
- `www/index.html` — an empty placeholder Capacitor's schema requires.
- `package.json` — `@capacitor/core`, `@capacitor/cli`, `@capacitor/android`, `@capacitor/ios` (^7) with scripts `add:android`, `add:ios`, `sync`, `open:android`, `open:ios`.

`scaffold_capacitor(project_dir, app_name="Nexoria App", app_id="com.pythonaibrain.nexoriaapp", server_url="https://your-deployed-app.example.com") -> str`. The CLI warns if you leave the placeholder URL.

```bash
nexoria build-mobile --name "Inkwell" --server-url https://inkwell.example.com
cd mobile && npm install && npx cap add android && npx cap open android
```

Use HTTPS in production; the WebSocket then runs as `wss://`.

## API reference

### Functions

#### `scaffold_capacitor(project_dir: str, app_name: str = 'Nexoria App', app_id: str = 'com.pythonaibrain.nexoriaapp', server_url: str = 'https://your-deployed-app.example.com') -> str`

Write a Capacitor project config into `<project_dir>/mobile/`. Returns the path to that directory.

`server_url` MUST be your actual deployed backend's URL before this is useful on a real device -- the placeholder default will load nothing. Update it, or pass the real one in directly.
