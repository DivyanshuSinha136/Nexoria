# `nexoria.cli` — the `nexoria` command

> Scaffolding, dev server, production build, native-tier management, and a diagnostics report — with optional `rich` output.

| | |
|---|---|
| **Entry point** | `nexoria = "nexoria.cli.main:main"` (from `pyproject.toml`); also `python -m nexoria.cli.main` |
| **Source** | `nexoria/cli/main.py` (commands), `nexoria/cli/ui.py` (terminal helpers) |
| **Depends on** | `rich` (optional — plain-text fallback), `argparse` |

## Commands

| Command | What it does |
|---|---|
| `nexoria new NAME [--force]` | Creates `NAME/` with `app.py` (a styled counter), `package.json` (esbuild dev-dependency, `build`/`dev` scripts), `.gitignore`, and `static/`. Asks before overwriting an existing directory unless `--force`. |
| `nexoria dev [--module app] [--host 127.0.0.1] [--port 8000]` | Imports `<module>` from the current directory, requires a top-level `app` object, prints a status panel, and runs `app.run(reload=True)`. |
| `nexoria build` | If `node` is on `PATH`, runs `tools/node-build/build.js` (esbuild bundling, runtime hashing, optional Tailwind compile); otherwise prints a warning and skips. |
| `nexoria doctor [--json]` | Status of every native tier and every toolchain (`node`, `rustc`, `cargo`, `cmake`, `ninja`, `mingw32-make`, `go`, `nvcc`). `--json` prints machine-readable output. |
| `nexoria native status` | Just the native-tier table. |
| `nexoria native build [flags]` | Builds the optional native tiers from source (see below). |
| `nexoria native clean [-y]` | Removes built native artifacts (build dirs, compiled `_nexoria_*` modules, the Go binary). Asks for confirmation unless `-y`. Never touches `_nexoria_rs` (that is maturin/pip's job). |
| `nexoria build-native [flags]` | Deprecated alias for `native build` (prints a notice). |
| `nexoria build-desktop [--name] [--entry app.py] [--port 8000] [--app-id]` | Scaffolds `./electron/` — see [`desktop`](desktop.md). |
| `nexoria build-mobile [--name] [--app-id] [--server-url URL]` | Scaffolds `./mobile/` — see [`mobile`](mobile.md). |
| `nexoria --version`, `--no-color` | Global flags. `NO_COLOR`/`NEXORIA_NO_COLOR` env vars also force plain output. |

### `native build` flags

| Flag | Effect |
|---|---|
| *(none)* | Rust safety core → C++ VDOM → embedded JS engine |
| `--vdom-only` | Skip the JS engine |
| `--vdom-with-mingw` | Build the VDOM with `mingw32-make` and `Makefile.mingw` instead of CMake (Windows, no CMake) |
| `--with-go-server` / `--go-server-only` | Also / only build the Go edge server |
| `--with-gpu` / `--gpu-only` | Also / only build the CUDA tier |

Exit codes: failures print a styled error and exit `1`; usage errors exit `2`; Ctrl+C exits `130`.

## `doctor` in detail

`doctor` distinguishes three situations that a bare "not built" would blur:

1. **Not built anywhere** — no matching file in the package directory.
2. **Built for a different interpreter/OS/architecture** — a file exists but this interpreter can't load it (the message shows the expected ABI tag).
3. **Built for this interpreter but broken** — e.g. a missing runtime DLL.

It also prints the package directory Python is importing from, which is the folder compiled `*_nexoria_*.so/.pyd` files must sit in.

## `ui.py` helpers

`banner`, `success`, `error`, `warn`, `info`, `rule`, `confirm`, `spinner`, `status_table`, `key_values`, `force_plain`, `using_rich` — used by every command; each degrades to `print()`/`input()` without `rich`.

## Notes

- `nexoria dev` always uses reload mode; the Go edge server is not used in dev.
- `nexoria build` does not fail when Node is missing — it warns and returns.
- The generated `package.json` script paths (`node ../../tools/node-build/build.js`) assume the project sits two levels below the framework checkout; adjust them for an app created elsewhere, or run the build tool from wherever it is installed.

## API reference

### Functions

#### `banner(version: str, tagline: str = 'Python-native. Rust-fast. Batteries included.') -> None`

#### `confirm(question: str, default: bool = False) -> bool`

#### `error(msg: str) -> None`

#### `force_plain() -> None`

Disable rich output for the rest of the process (used by --no-color and by anything piping nexoria's output somewhere non-interactive).

#### `info(msg: str = '') -> None`

#### `key_values(title: str, pairs: Sequence[tuple[str, str]]) -> None`

Small labeled panel, used for things like the dev-server startup banner (host, port, module, reload state).

#### `rule(title: str = '') -> None`

#### `spinner(msg: str)`

Show a spinner while a block of code runs; prints a plain start line (no live spinner) when rich isn't available or output isn't a real terminal.

#### `status_table(title: str, sections: Sequence[tuple[str, Iterable[StatusRow]]]) -> None`

Render one or more named sections of status rows as a single table.

#### `success(msg: str) -> None`

#### `using_rich() -> bool`

#### `warn(msg: str) -> None`

### Constants

| Name | Value |
|---|---|
| `BAD` | `'red'` |
| `BRAND` | `'#7c5cff'` |
| `MUTED` | `'dim'` |
| `OK` | `'green'` |
| `WARN` | `'yellow'` |
