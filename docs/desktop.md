# `nexoria.desktop` — Electron scaffolding

> `scaffold_electron()` writes a small Electron project that runs your Python server as a child process and shows it in a native window.

| | |
|---|---|
| **Import** | `from nexoria.desktop import scaffold_electron` |
| **CLI** | `nexoria build-desktop --name "My App" --entry app.py --port 8000 --app-id com.you.app` |
| **Source** | `nexoria/desktop/electron.py` |
| **Needs (build machine)** | Node, Electron, electron-builder |

## What it generates

`<project>/electron/` containing:

- **`main.js`** — spawns `python3 <entry>` (override with `NEXORIA_PYTHON`), sets `NEXORIA_DESKTOP=1`, polls `http://127.0.0.1:<port>/_nexoria/health` for up to 15 s, then opens a 1200×800 `BrowserWindow`. It kills the child on `before-quit` and quits when all windows close (except on macOS).
- **`preload.js`** — `contextIsolation` on, `nodeIntegration` off; exposes only `window.nexoriaDesktop.platform`.
- **`package.json`** — scripts `start` (`electron .`) and `dist` (`electron-builder`); dev-dependencies `electron ^33`, `electron-builder ^25`.

`scaffold_electron(project_dir, app_name="Nexoria App", entry_file="app.py", port=8000, app_id="com.pythonaibrain.nexoria-app") -> str` returns the directory path. It is idempotent: it overwrites generated files and never touches your own `app.py`.

```bash
nexoria build-desktop --name "Inkwell"
cd electron && npm install && npm start      # run
npm run dist                                  # installer
```

## Things to know

- Your `app.py` must listen on the same `--port` the scaffold polls; `app.run(port=8000)` matches the default.
- The packaged app still needs a Python interpreter (and your dependencies) on the end user's machine, or you must bundle one yourself — the scaffold does not.
- Nothing here is loaded at runtime by web apps; it is build-time scaffolding.

## API reference

### Functions

#### `scaffold_electron(project_dir: str, app_name: str = 'Nexoria App', entry_file: str = 'app.py', port: int = 8000, app_id: str = 'com.pythonaibrain.nexoria-app') -> str`

Write a complete Electron project into `<project_dir>/electron/`. Returns the path to that directory. Idempotent: safe to re-run after editing your app -- overwrites the generated files, never touches your own `app.py`.
