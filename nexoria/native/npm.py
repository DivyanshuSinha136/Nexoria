"""
nexoria.native.npm
====================
A minimal, pure-Python npm registry client. Talks directly to the
public npm registry's HTTP API (`registry.npmjs.org`) — which is just
JSON + tarballs over HTTPS — to resolve, download, and extract real
npm packages into a local cache, with **no Node.js or npm CLI required
on the machine**.

This intentionally does *not* replicate npm's full behavior: no
lockfiles, no devDependency graphs, no npm scripts/lifecycle hooks
(`postinstall`, native addon builds via node-gyp, etc.), and no
transitive-dependency install by default (see `install(..., deps=True)`
for a best-effort shallow attempt). Packages that require compiled
native addons or Node built-ins (`fs`, `http`, `child_process`, ...)
will download fine but will not *run* under the embedded JS engine
(`nexoria.native.js`) — that engine only provides a small Node-like
shim, not real Node. Pure-JS packages (lodash, dayjs, animejs, and
most utility/animation/data libraries) work end to end.
"""

from __future__ import annotations
import json
import os
import io
import tarfile
import urllib.request
from dataclasses import dataclass
from typing import Optional

REGISTRY = "https://registry.npmjs.org"
DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".nexoria", "npm_cache")


@dataclass
class PackageInfo:
    name: str
    version: str
    tarball_url: str
    main: Optional[str]          # the package.json "main" entry, relative path
    module: Optional[str]        # "module" field (ESM entry), if present


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def resolve(name: str, version: str = "latest") -> PackageInfo:
    """Look up a package's metadata on the public npm registry."""
    meta = _fetch_json(f"{REGISTRY}/{name}")
    resolved_version = meta["dist-tags"].get(version, version)
    if resolved_version not in meta["versions"]:
        raise ValueError(f"{name}@{version} not found (resolved to {resolved_version!r})")
    v = meta["versions"][resolved_version]
    return PackageInfo(
        name=name,
        version=resolved_version,
        tarball_url=v["dist"]["tarball"],
        main=v.get("main"),
        module=v.get("module"),
    )


def _package_dir(cache_dir: str, name: str, version: str) -> str:
    safe_name = name.replace("/", "__")
    return os.path.join(cache_dir, f"{safe_name}@{version}")


def install(
    name: str,
    version: str = "latest",
    cache_dir: str = DEFAULT_CACHE_DIR,
    force: bool = False,
) -> str:
    """
    Download + extract a single package (no transitive deps) into the
    local cache. Returns the local directory containing its files
    (package.json, dist/, etc.) — mirroring npm's `node_modules/<pkg>/`
    layout for that one package.
    """
    info = resolve(name, version)
    dest = _package_dir(cache_dir, info.name, info.version)
    marker = os.path.join(dest, ".nexoria-installed")
    if os.path.isdir(dest) and os.path.exists(marker) and not force:
        return dest

    os.makedirs(dest, exist_ok=True)
    req = urllib.request.Request(info.tarball_url)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()

    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for member in tar.getmembers():
            # npm tarballs wrap everything in a top-level "package/" dir
            parts = member.name.split("/", 1)
            if len(parts) < 2:
                continue
            member.name = parts[1]
            if not member.name:
                continue
            tar.extract(member, path=dest, filter="data")

    with open(marker, "w") as f:
        f.write(info.version)
    return dest


def entry_point(pkg_dir: str, prefer_module: bool = False) -> str:
    """Resolve the file a `require()`/`import` of this package should load."""
    pkg_json_path = os.path.join(pkg_dir, "package.json")
    with open(pkg_json_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)

    candidates = []
    if prefer_module and pkg.get("module"):
        candidates.append(pkg["module"])
    if pkg.get("main"):
        candidates.append(pkg["main"])
    candidates.append("index.js")

    for rel in candidates:
        path = os.path.join(pkg_dir, rel)
        if os.path.isfile(path):
            return path
        # npm "main" sometimes omits the .js extension
        if os.path.isfile(path + ".js"):
            return path + ".js"
    raise FileNotFoundError(f"Could not resolve an entry point for package at {pkg_dir}")
