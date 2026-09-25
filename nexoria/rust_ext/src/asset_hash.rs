//! Fast non-cryptographic hashing for asset cache-busting filenames
//! (e.g. `app.a1b2c3d4.js`), used by the build pipeline in
//! `tools/node-build` via the Python `nexoria.cache` module.

use twox_hash::XxHash64;
use std::hash::Hasher;

pub fn hash_bytes(data: &[u8]) -> String {
    let mut hasher = XxHash64::with_seed(0);
    hasher.write(data);
    format!("{:016x}", hasher.finish())[..10].to_string()
}
