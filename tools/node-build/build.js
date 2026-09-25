#!/usr/bin/env node
/**
 * Nexoria production build tool.
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 *
 * Bundles and minifies:
 *   - the app's own static/*.js entry points (if any)
 *   - the Nexoria client runtime (runtime.js) and every adapter that
 *     currently exists in nexoria/runtime/ (ThreeJS, GSAP, Chart.js,
 *     video.js, AG Grid, Spline, VRM, Bootstrap, Webcam, OpenLayers,
 *     Barcode, Babylon, QRCode, Shiki, ... -- discovered on disk, not
 *     hardcoded, so a new adapter is picked up automatically), copied
 *     alongside with content-hashed filenames.
 *   - a real, production-compiled Tailwind CSS stylesheet, IF the
 *     project has a Tailwind input file (see buildTailwind() below)
 *     and `@tailwindcss/cli` installed. This is the production
 *     counterpart to `App(tailwind=True)`'s Play CDN (which is meant
 *     for prototyping only, per Tailwind's own guidance) -- entirely
 *     optional and silently skipped if there's no Tailwind input file.
 *
 * Usage:
 *   node build.js            # one-shot production build -> dist/
 *   node build.js --watch    # incremental rebuild on change (dev mode)
 *   node build.js --no-clean # keep previous dist/ output around (one-shot only)
 *   node build.js --help
 */

const path = require("path");
const fs = require("fs");
const crypto = require("crypto");
const { execFileSync } = require("child_process");

const CWD = process.cwd();
const STATIC_DIR = path.join(CWD, "static");
const DIST_DIR = path.join(CWD, "dist");
const RUNTIME_DIR = path.resolve(__dirname, "..", "..", "nexoria", "runtime");

const args = process.argv.slice(2);
const WATCH = args.includes("--watch");
const NO_CLEAN = args.includes("--no-clean");

if (args.includes("--help") || args.includes("-h")) {
  console.log(
    "Nexoria production build tool\n\n" +
    "Usage:\n" +
    "  node build.js             one-shot production build -> dist/\n" +
    "  node build.js --watch     incremental rebuild on change (dev mode)\n" +
    "  node build.js --no-clean  don't wipe dist/ before a one-shot build\n" +
    "  node build.js --help      show this message\n"
  );
  process.exit(0);
}

// ---------------------------------------------------------------------
// Resolve a dependency the way the *app project* would resolve it, not
// the way build.js's own location would. build.js lives inside the
// framework's tools/node-build/ directory; Node's require() resolution
// walks up from the file doing the requiring, so a plain
// `require("esbuild")` here would only ever find an esbuild installed
// somewhere above tools/node-build/ -- never the one the app's own
// `npm install` puts in <app>/node_modules, which is what the CLI
// actually tells people to run. Searching from CWD (and falling back
// to build.js's own directory, in case someone installs a tool
// alongside build.js itself instead) fixes that.
// ---------------------------------------------------------------------
function resolveFrom(pkg, searchDirs) {
  for (const dir of searchDirs) {
    try {
      return require(require.resolve(pkg, { paths: [dir] }));
    } catch {
      // try the next search directory
    }
  }
  return null;
}

const esbuild = resolveFrom("esbuild", [CWD, __dirname]);
if (!esbuild) {
  console.error(
    "esbuild is not installed. Run `npm install` inside your project " +
    "(or `npm install esbuild`) before running `nexoria build`."
  );
  process.exit(1);
}

const ADAPTER_NAME_RE = /^(runtime|.+-adapter)\.js$/;

function hashOf(filePath) {
  const buf = fs.readFileSync(filePath);
  return crypto.createHash("sha1").update(buf).digest("hex").slice(0, 10);
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function cleanDist() {
  fs.rmSync(DIST_DIR, { recursive: true, force: true });
  ensureDir(DIST_DIR);
}

function collectEntryPoints(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".js") && !f.endsWith(".min.js"))
    .map((f) => path.join(dir, f));
}

// Discover every runtime file + adapter that actually exists on disk,
// instead of a hardcoded list that silently drifts out of sync as new
// adapters (Bootstrap, Webcam, OpenLayers, Barcode, Babylon, QRCode,
// Shiki, ...) get added to nexoria/runtime/.
function collectRuntimeFiles() {
  if (!fs.existsSync(RUNTIME_DIR)) return [];
  return fs.readdirSync(RUNTIME_DIR).filter((f) => ADAPTER_NAME_RE.test(f));
}

function findTailwindInput() {
  // Convention over configuration: look for a CSS file that itself
  // does `@import "tailwindcss";` (Tailwind v4's CSS-first config --
  // no tailwind.config.js required). Checked in order; first match wins.
  const candidates = [
    path.join(STATIC_DIR, "tailwind.css"),
    path.join(CWD, "tailwind.css"),
    path.join(CWD, "src", "input.css"),
  ];
  return candidates.find((p) => fs.existsSync(p));
}

function buildTailwind(manifest) {
  const input = findTailwindInput();
  if (!input) return; // nothing to do -- most apps use App(tailwind=True)'s Play CDN, or no Tailwind at all

  let cliEntry;
  try {
    // @tailwindcss/cli's package.json "exports" field only whitelists
    // "./package.json" itself -- require.resolve() of the actual bin
    // script path (dist/index.mjs) is blocked by that exports map even
    // though the file exists on disk. Resolve the whitelisted
    // package.json instead and join the bin path onto its directory.
    // Per the docs, it's installed inside tools/node-build/, but also
    // accept it being installed in the app project itself.
    const pkgJsonPath = require.resolve("@tailwindcss/cli/package.json", {
      paths: [__dirname, CWD],
    });
    const pkg = require(pkgJsonPath);
    const binRelative = typeof pkg.bin === "string" ? pkg.bin : pkg.bin.tailwindcss;
    cliEntry = path.join(path.dirname(pkgJsonPath), binRelative);
    if (!fs.existsSync(cliEntry)) throw new Error(`resolved path does not exist: ${cliEntry}`);
  } catch {
    console.warn(
      `Found a Tailwind input file (${path.relative(CWD, input)}) but ` +
      "@tailwindcss/cli isn't installed -- run `npm install @tailwindcss/cli` " +
      "(inside tools/node-build/, or in your project) to compile a real " +
      "production stylesheet. Skipping for now " +
      "(App(tailwind=True)'s Play CDN still works without this)."
    );
    return;
  }

  const outputPath = path.join(DIST_DIR, "tailwind.css");
  console.log(`Compiling Tailwind CSS: ${path.relative(CWD, input)} -> dist/tailwind.css`);
  execFileSync(process.execPath, [cliEntry, "-i", input, "-o", outputPath, "--minify"], {
    stdio: "inherit",
    cwd: CWD,
  });
  manifest["tailwind.css"] = "/dist/tailwind.css";
}

function writeManifest(manifest) {
  manifest["generatedAt"] = new Date().toISOString();
  ensureDir(DIST_DIR);
  fs.writeFileSync(path.join(DIST_DIR, "manifest.json"), JSON.stringify(manifest, null, 2));
}

// Turn esbuild's metafile.outputs into { "logicalName.js": "/dist/hashed.js" }
// entries. esbuild's [hash] token is base-32-ish (digits + A-Z, e.g.
// "BDEDZC27") -- NOT lowercase hex -- so guessing it back out with a
// regex is fragile and silently produces wrong/duplicate keys the
// moment esbuild's hash format doesn't match the guess. The metafile
// already tells us exactly which entry point produced each output
// (`entryPoint`), so use that instead of guessing.
function mergeEsbuildOutputs(manifest, metafileOutputs) {
  for (const [outFile, info] of Object.entries(metafileOutputs)) {
    if (outFile.endsWith(".map")) continue; // sourcemaps aren't manifest entries
    if (!info.entryPoint) continue; // skip chunks/assets with no direct entry point
    const logicalName = path.basename(info.entryPoint);
    manifest[logicalName] = "/" + path.relative(CWD, path.join(CWD, outFile)).split(path.sep).join("/");
  }
}

async function build() {
  ensureDir(DIST_DIR);
  if (!WATCH && !NO_CLEAN) {
    // One-shot production builds start from a clean dist/ so stale
    // content-hashed files from previous builds don't accumulate
    // forever. Watch mode never cleans -- esbuild's own incremental
    // rebuilds own dist/ once the context is created.
    cleanDist();
  }

  const manifest = {};

  // 1. Copy + hash the framework runtime + every adapter present
  //    (they're already hand-written to be small; no transpile step
  //    needed for these).
  const runtimeFiles = collectRuntimeFiles();
  for (const name of runtimeFiles) {
    const src = path.join(RUNTIME_DIR, name);
    const hash = hashOf(src);
    const outName = name.replace(/\.js$/, `.${hash}.js`);
    fs.copyFileSync(src, path.join(DIST_DIR, outName));
    manifest[name] = `/dist/${outName}`;
  }
  if (runtimeFiles.length > 0) {
    console.log(`Copied ${runtimeFiles.length} runtime file(s): ${runtimeFiles.join(", ")}`);
  }

  // 2. Real production Tailwind build, if applicable (see above).
  buildTailwind(manifest);

  // 3. Bundle the app's own static JS (if any) with esbuild.
  const entryPoints = collectEntryPoints(STATIC_DIR);
  if (entryPoints.length > 0) {
    const ctx = await esbuild.context({
      entryPoints,
      bundle: true,
      minify: !WATCH,
      sourcemap: WATCH,
      outdir: DIST_DIR,
      entryNames: "[name].[hash]",
      target: ["es2020"],
      metafile: true,
      logLevel: "info",
      plugins: WATCH
        ? [
            {
              name: "nexoria-manifest-refresh",
              setup(build) {
                build.onEnd((result) => {
                  if (!result.metafile) return;
                  mergeEsbuildOutputs(manifest, result.metafile.outputs);
                  writeManifest(manifest);
                });
              },
            },
          ]
        : [],
    });

    if (WATCH) {
      await ctx.watch();
      console.log("Nexoria build tool watching for changes... (Ctrl+C to stop)");
      return; // keep process alive for watch mode; onEnd plugin above keeps manifest fresh
    } else {
      const result = await ctx.rebuild();
      mergeEsbuildOutputs(manifest, result.metafile.outputs);
      await ctx.dispose();
    }
  } else if (WATCH) {
    console.log("No static/*.js entry points found -- nothing to watch, but runtime/Tailwind steps ran once.");
  }

  writeManifest(manifest);
  console.log(`Nexoria build complete -> ${path.relative(CWD, DIST_DIR)}/`);
  console.log(JSON.stringify(manifest, null, 2));
}

build().catch((err) => {
  console.error(err);
  process.exit(1);
});
