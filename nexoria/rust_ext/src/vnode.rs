//! Mirrors nexoria.core.element.Element's `to_dict()` shape so the Rust
//! side can deserialize a tree straight from the Python JSON-able dict
//! without any bespoke FFI marshalling code on the Python side.

use serde::Deserialize;
use std::collections::HashMap;

#[derive(Debug, Deserialize, Clone)]
#[serde(tag = "t")]
pub enum VNode {
    #[serde(rename = "text")]
    Text { v: String },
    #[serde(rename = "el")]
    El {
        tag: String,
        props: HashMap<String, serde_json::Value>,
        events: HashMap<String, String>,
        key: Option<serde_json::Value>,
        children: Vec<VNode>,
    },
}

impl VNode {
    pub fn is_text(&self) -> bool {
        matches!(self, VNode::Text { .. })
    }

    pub fn tag(&self) -> Option<&str> {
        match self {
            VNode::El { tag, .. } => Some(tag.as_str()),
            _ => None,
        }
    }

    pub fn children(&self) -> &[VNode] {
        match self {
            VNode::El { children, .. } => children.as_slice(),
            VNode::Text { .. } => &[],
        }
    }

    pub fn key(&self) -> Option<&serde_json::Value> {
        match self {
            VNode::El { key, .. } => key.as_ref(),
            VNode::Text { .. } => None,
        }
    }
}
