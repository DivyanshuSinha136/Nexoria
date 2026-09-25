# `rust_ext` — the PyO3 Rust hot path

> A compiled extension (`nexoria._nexoria_rs`) providing a fast virtual-DOM differ and asset hashing. Optional: everything falls back to pure Python.

| | |
|---|---|
| **Source** | `nexoria/rust_ext/` (`Cargo.toml`, `src/lib.rs`, `vnode.rs`, `differ.rs`, `asset_hash.rs`) |
| **Built with** | [maturin](https://www.maturin.rs/) (`maturin develop --release`), configured in `pyproject.toml` |
| **Crate** | `nexoria-rs` 0.1.0 — `pyo3 0.22`, `pythonize 0.22`, `serde`, `serde_json`, `twox-hash`; release profile uses LTO, `opt-level = 3`, `panic = "abort"` |
| **Python module** | `nexoria._nexoria_rs` |
| **Used by** | `nexoria.render.diff`, `nexoria.style.stylesheet`, `nexoria.cache.assets` |

## Exposed functions

| Function | Description |
|---|---|
| `diff(old=None, new=None) -> list[dict]` | Takes two `Element.to_dict()` trees (or `None`), returns patch dicts `{"op", "path", "payload"}`. Uses `pythonize` to convert Python objects to `serde_json` values and back. |
| `hash_asset(data: bytes) -> str` | xxHash64 (seed 0), formatted as 16 hex chars, truncated to the first 10. |

## Structure

- `vnode.rs` — a `serde` enum `VNode { Text{v}, El{tag, props, events, key, children} }` tagged by `"t"`, matching `Element.to_dict()`.
- `differ.rs` — the same algorithm as the Python differ (including keyed-children handling and its [limitations](render.md#known-limitations-of-keyed-lists)).
- `asset_hash.rs` — the hashing helper.

## Build and verify

```bash
pip install maturin
maturin develop --release
nexoria doctor          # "PyO3 Rust extension (_nexoria_rs)" should be active/loaded
```

The source distribution ships a Linux CPython 3.12 build (`_nexoria_rs.cpython-312-x86_64-linux-gnu.so`); on other platforms/interpreters the framework silently uses the Python differ. Wheels built by `maturin` include the compiled module and exclude `target/`, tests, docs and examples (see `[tool.maturin] exclude`).

## API reference

Compiled module — no Python source to introspect. See the table above.
