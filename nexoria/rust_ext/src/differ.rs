//! The performance-critical tree diff. Functionally mirrors
//! `nexoria/render/diff.py::_diff_py`, but runs at native speed and
//! without allocating a Patch object per call across the FFI boundary
//! (patches are built once and returned as a single serde_json::Value).

use crate::vnode::VNode;
use serde_json::json;
use std::collections::HashMap;

pub struct Patch {
    pub op: &'static str,
    pub path: Vec<usize>,
    pub payload: serde_json::Value,
}

pub fn diff(old: Option<&VNode>, new: Option<&VNode>) -> Vec<Patch> {
    let mut out = Vec::new();
    diff_into(old, new, &mut Vec::new(), &mut out);
    out
}

fn node_to_value(n: &VNode) -> serde_json::Value {
    // Cheap re-serialization for "replace"/"insert" payloads; the tree
    // sizes here are the *changed* subtree only, not the whole app.
    serde_json::to_value(SerHelper(n)).unwrap_or(serde_json::Value::Null)
}

// Thin wrapper so we can hand-roll Serialize without fighting the
// internally-tagged enum shape we used for Deserialize.
struct SerHelper<'a>(&'a VNode);
impl<'a> serde::Serialize for SerHelper<'a> {
    fn serialize<S: serde::Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        use serde::ser::SerializeMap;
        match self.0 {
            VNode::Text { v } => {
                let mut m = s.serialize_map(Some(2))?;
                m.serialize_entry("t", "text")?;
                m.serialize_entry("v", v)?;
                m.end()
            }
            VNode::El { tag, props, events, key, children } => {
                let mut m = s.serialize_map(Some(6))?;
                m.serialize_entry("t", "el")?;
                m.serialize_entry("tag", tag)?;
                m.serialize_entry("props", props)?;
                m.serialize_entry("events", events)?;
                m.serialize_entry("key", key)?;
                let kids: Vec<_> = children.iter().map(SerHelper).collect();
                m.serialize_entry("children", &kids)?;
                m.end()
            }
        }
    }
}

fn diff_into(old: Option<&VNode>, new: Option<&VNode>, path: &mut Vec<usize>, out: &mut Vec<Patch>) {
    match (old, new) {
        (None, None) => {}
        (None, Some(n)) => out.push(Patch { op: "insert", path: path.clone(), payload: node_to_value(n) }),
        (Some(_), None) => out.push(Patch { op: "remove", path: path.clone(), payload: serde_json::Value::Null }),
        (Some(o), Some(n)) => {
            match (o, n) {
                (VNode::Text { v: ov }, VNode::Text { v: nv }) => {
                    if ov != nv {
                        out.push(Patch { op: "text", path: path.clone(), payload: json!(nv) });
                    }
                }
                (VNode::El { .. }, VNode::Text { .. }) | (VNode::Text { .. }, VNode::El { .. }) => {
                    out.push(Patch { op: "replace", path: path.clone(), payload: node_to_value(n) });
                }
                (
                    VNode::El { tag: ot, props: op_, events: oe, children: ochildren, .. },
                    VNode::El { tag: nt, props: np, events: ne, children: nchildren, .. },
                ) => {
                    if ot != nt {
                        out.push(Patch { op: "replace", path: path.clone(), payload: node_to_value(n) });
                        return;
                    }
                    if op_ != np || oe != ne {
                        out.push(Patch {
                            op: "update_props",
                            path: path.clone(),
                            payload: json!({ "props": np, "events": ne }),
                        });
                    }
                    diff_children(ochildren, nchildren, path, out);
                }
            }
        }
    }
}

fn diff_children(old: &[VNode], new: &[VNode], path: &mut Vec<usize>, out: &mut Vec<Patch>) {
    let old_keyed: HashMap<String, (usize, &VNode)> = old.iter().enumerate()
        .filter_map(|(i, c)| c.key().map(|k| (k.to_string(), (i, c))))
        .collect();
    let new_keyed: HashMap<String, (usize, &VNode)> = new.iter().enumerate()
        .filter_map(|(i, c)| c.key().map(|k| (k.to_string(), (i, c))))
        .collect();

    let fully_keyed = !old_keyed.is_empty() && !new_keyed.is_empty()
        && old_keyed.len() == old.len() && new_keyed.len() == new.len();

    if fully_keyed {
        for (k, (ni, nnode)) in new_keyed.iter() {
            let onode = old_keyed.get(k).map(|(_, n)| *n);
            path.push(*ni);
            diff_into(onode, Some(*nnode), path, out);
            path.pop();
        }
        for (k, (oi, _)) in old_keyed.iter() {
            if !new_keyed.contains_key(k) {
                path.push(*oi);
                out.push(Patch { op: "remove", path: path.clone(), payload: serde_json::Value::Null });
                path.pop();
            }
        }
    } else {
        let max_len = old.len().max(new.len());
        for i in 0..max_len {
            path.push(i);
            diff_into(old.get(i), new.get(i), path, out);
            path.pop();
        }
    }
}
