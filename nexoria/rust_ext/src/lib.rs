//! Nexoria native hot path.
//!
//! Exposes `_nexoria_rs.diff(old, new)` to Python: takes two JSON-able
//! dicts (or None) shaped like `Element.to_dict()` and returns a list
//! of patch dicts. This module is optional -- `nexoria.render.diff`
//! falls back to a pure-Python implementation automatically if this
//! extension isn't built for the target platform, so Nexoria apps
//! remain fully cross-platform even without a Rust toolchain at
//! deploy time.
//!
//! Written against the pyo3 0.22 `Bound<'py, T>` API (pyo3 0.22 removed
//! the old bare-reference `&PyAny` / `&PyModule` argument style used in
//! earlier pyo3 releases).

mod vnode;
mod differ;
mod asset_hash;

use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyList, PyModule};
use vnode::VNode;

#[pyfunction]
#[pyo3(signature = (old=None, new=None))]
fn diff<'py>(
    py: Python<'py>,
    old: Option<Bound<'py, PyAny>>,
    new: Option<Bound<'py, PyAny>>,
) -> PyResult<PyObject> {
    let old_json: Option<serde_json::Value> = match &old {
        Some(o) => Some(pythonize::depythonize(o)?),
        None => None,
    };
    let new_json: Option<serde_json::Value> = match &new {
        Some(n) => Some(pythonize::depythonize(n)?),
        None => None,
    };

    let old_node: Option<VNode> = old_json
        .map(serde_json::from_value)
        .transpose()
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    let new_node: Option<VNode> = new_json
        .map(serde_json::from_value)
        .transpose()
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;

    let patches = differ::diff(old_node.as_ref(), new_node.as_ref());

    let list = PyList::empty_bound(py);
    for p in patches {
        let d = PyDict::new_bound(py);
        d.set_item("op", p.op)?;
        d.set_item("path", p.path)?;
        d.set_item("payload", pythonize::pythonize(py, &p.payload)?)?;
        list.append(d)?;
    }
    Ok(list.into())
}

#[pyfunction]
fn hash_asset(data: &[u8]) -> String {
    asset_hash::hash_bytes(data)
}

#[pymodule]
fn _nexoria_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(diff, m)?)?;
    m.add_function(wrap_pyfunction!(hash_asset, m)?)?;
    Ok(())
}
