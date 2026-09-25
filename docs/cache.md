# `nexoria.cache`

> Content fingerprinting for cache-busting asset names.

| | |
|---|---|
| **Import** | `from nexoria.cache import fingerprint` |
| **Source** | `nexoria/cache/assets.py` |
| **Acceleration** | Rust `hash_asset` (xxHash64, 10 hex chars) when `_nexoria_rs` is built; else `hashlib.blake2b(digest_size=5)` (10 hex chars) |

```python
from nexoria.cache import fingerprint
fingerprint(b"body { color: red }")     # e.g. '3f9a1c02be'
```

`fingerprint(data: bytes) -> str` returns a short hex digest. The two backends both produce 10 characters but **different values** for the same input, so treat the digest as an opaque per-environment token.

Note that the production build in [`tools`](tools.md) computes its own SHA-1-based hashes in Node; this Python function is available for your own tooling.

## API reference

### Functions

#### `fingerprint(data: bytes) -> str`
