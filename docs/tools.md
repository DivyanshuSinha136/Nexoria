# `tools/` — the Node.js build tool

> `tools/node-build/build.js` — the production asset build behind `nexoria build`. Node is a **build-time** dependency only.

| | |
|---|---|
| **Source** | `tools/node-build/build.js`, `package.json` (`@nexoria/node-build` 0.1.0, Node ≥ 18) |
| **Dependencies** | `esbuild ^0.23.0`; optional `@tailwindcss/cli ^4.3.3` |
| **Invoked by** | `nexoria build` (or directly: `node tools/node-build/build.js [--watch] [--no-clean] [--help]`) |

## What one run does

Run from your **project directory** (the current working directory is what matters):

1. **Clean** `dist/` (skipped with `--no-clean` or in `--watch`).
2. **Runtime files.** Every `runtime.js` and `*-adapter.js` found in `nexoria/runtime/` — discovered on disk, not from a hard-coded list — is copied to `dist/<name>.<sha1-10>.js`.
3. **Tailwind (optional).** If an input file exists — checked in order: `static/tailwind.css`, `./tailwind.css`, `src/input.css` — containing `@import "tailwindcss";` (Tailwind v4 CSS-first config), and `@tailwindcss/cli` is installed (in `tools/node-build/` or your project), it compiles a minified, purged `dist/tailwind.css`. Missing CLI → a warning and a skip.
4. **App JS.** Every `static/*.js` (excluding `*.min.js`) is bundled and minified with esbuild (`es2020`, output `[name].[hash].js`). In `--watch` it uses sourcemaps, no minification, and refreshes the manifest on every rebuild.
5. **Manifest.** Writes `dist/manifest.json` mapping logical names to hashed URLs, plus `generatedAt`.

esbuild is resolved from your **project** (`node_modules` under the CWD) first and from `tools/node-build/` second, so `npm install` in the app is enough. If it is missing the tool exits 1 with instructions.

## Important: `dist/` is not auto-served

`App` does not read `manifest.json` and serves the un-hashed runtime from `/_nexoria/`. The build produces immutable, cache-friendly artifacts for you to publish (CDN, reverse proxy, your own static route). Pair it with the Go edge server or a proxy for long-lived caching.

## Example

```bash
cd myapp
npm install            # installs esbuild (from the generated package.json)
nexoria build
cat dist/manifest.json
```
