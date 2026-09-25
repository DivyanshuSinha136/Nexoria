//! nexoria-safety-core
//! =====================
//! The memory-safety-critical part of Nexoria's native VDOM stack.
//!
//! The C++ VDOM diff engine (`nexoria/native/cpp/vdom/`) needs to compare
//! child "keys" (the `key=` a component author attaches to list items, see
//! `nexoria.core.element.el`) on every diff. Doing that as raw C-string
//! comparisons/lifetime management in C++ is exactly the class of bug
//! (dangling pointers, missing null terminators, double frees) this crate
//! exists to remove: it owns every interned string for the lifetime of the
//! `Interner`, hands the C++ side back a stable `u32` id instead of a raw
//! pointer to carry around, and turns key *comparison* in the diff hot loop
//! into an integer equality check instead of a string compare.
//!
//! Every exported function is wrapped in `catch_unwind` so a Rust panic
//! can never unwind across the FFI boundary into C++ (which is undefined
//! behavior) -- it becomes a well-defined error sentinel instead.

use std::collections::HashMap;
use std::os::raw::c_int;
use std::panic::{self, AssertUnwindSafe};
use std::sync::Arc;

const INVALID_ID: u32 = 0;

pub struct Interner {
    strings: Vec<Arc<[u8]>>,       // index 0 is a dummy slot; real ids start at 1
    lookup: HashMap<Arc<[u8]>, u32>,
}

impl Interner {
    fn new() -> Self {
        Interner { strings: vec![Arc::from(&b""[..])], lookup: HashMap::new() }
    }

    fn intern(&mut self, bytes: &[u8]) -> u32 {
        if let Some(&id) = self.lookup.get(bytes) {
            return id;
        }
        let arc: Arc<[u8]> = Arc::from(bytes);
        let id = self.strings.len() as u32;
        self.strings.push(arc.clone());
        self.lookup.insert(arc, id);
        id
    }

    fn get(&self, id: u32) -> Option<&[u8]> {
        self.strings.get(id as usize).map(|a| a.as_ref())
    }
}

/// Create a new interner. Returns a heap-allocated opaque pointer the
/// caller must eventually pass to `nx_interner_free`. Never null.
#[no_mangle]
pub extern "C" fn nx_interner_new() -> *mut Interner {
    Box::into_raw(Box::new(Interner::new()))
}

/// Free an interner created by `nx_interner_new`. Passing the same
/// pointer twice, or a pointer not returned by `nx_interner_new`, is
/// undefined behavior on the C++ side (as with any C ABI) -- but a Rust
/// panic during drop still cannot escape as UB, thanks to catch_unwind.
#[no_mangle]
pub extern "C" fn nx_interner_free(ptr: *mut Interner) {
    if ptr.is_null() {
        return;
    }
    let _ = panic::catch_unwind(AssertUnwindSafe(|| unsafe {
        drop(Box::from_raw(ptr));
    }));
}

/// Intern `len` bytes at `data` and return a stable id (>= 1). Returns 0
/// (an id no real key ever has) on any error: null interner, null data
/// with nonzero len, or an internal panic.
#[no_mangle]
pub extern "C" fn nx_interner_intern(ptr: *mut Interner, data: *const u8, len: usize) -> u32 {
    if ptr.is_null() || (data.is_null() && len != 0) {
        return INVALID_ID;
    }
    let result = panic::catch_unwind(AssertUnwindSafe(|| unsafe {
        let interner = &mut *ptr;
        let slice = if len == 0 { &[][..] } else { std::slice::from_raw_parts(data, len) };
        interner.intern(slice)
    }));
    result.unwrap_or(INVALID_ID)
}

/// Number of bytes in the string for `id`, or -1 if `id`/`ptr` is invalid.
#[no_mangle]
pub extern "C" fn nx_interner_get_len(ptr: *const Interner, id: u32) -> i64 {
    if ptr.is_null() {
        return -1;
    }
    let result = panic::catch_unwind(AssertUnwindSafe(|| unsafe {
        (&*ptr).get(id).map(|s| s.len() as i64).unwrap_or(-1)
    }));
    result.unwrap_or(-1)
}

/// Pointer to the interned bytes for `id` (valid only as long as the
/// `Interner` itself is alive, and until the id's slot could ever be
/// removed -- which never happens: interners are append-only). Returns
/// null if `id`/`ptr` is invalid.
#[no_mangle]
pub extern "C" fn nx_interner_get_ptr(ptr: *const Interner, id: u32) -> *const u8 {
    if ptr.is_null() {
        return std::ptr::null();
    }
    let result = panic::catch_unwind(AssertUnwindSafe(|| unsafe {
        (&*ptr).get(id).map(|s| s.as_ptr()).unwrap_or(std::ptr::null())
    }));
    result.unwrap_or(std::ptr::null())
}

/// Equality check as a plain integer compare -- this is the whole point:
/// the C++ diff hot loop never touches raw string memory to compare two
/// keys, just this. Returns 1 if equal, 0 if not (also 0, not an error
/// sentinel, if either id is invalid -- two invalid keys are never
/// considered a match).
#[no_mangle]
pub extern "C" fn nx_interner_ids_equal(a: u32, b: u32) -> c_int {
    if a == INVALID_ID || b == INVALID_ID {
        return 0;
    }
    (a == b) as c_int
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn intern_is_idempotent_and_comparable() {
        let mut i = Interner::new();
        let a = i.intern(b"count-label");
        let b = i.intern(b"count-label");
        let c = i.intern(b"other-label");
        assert_eq!(a, b);
        assert_ne!(a, c);
        assert_eq!(i.get(a).unwrap(), b"count-label");
    }

    #[test]
    fn ffi_roundtrip() {
        let ptr = nx_interner_new();
        let s = b"hello-key";
        let id = nx_interner_intern(ptr, s.as_ptr(), s.len());
        assert_ne!(id, INVALID_ID);
        let len = nx_interner_get_len(ptr, id);
        assert_eq!(len as usize, s.len());
        let data_ptr = nx_interner_get_ptr(ptr, id);
        let recovered = unsafe { std::slice::from_raw_parts(data_ptr, len as usize) };
        assert_eq!(recovered, s);
        assert_eq!(nx_interner_ids_equal(id, id), 1);
        nx_interner_free(ptr);
    }
}
