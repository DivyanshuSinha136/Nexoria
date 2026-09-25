"""
nexoria.render.diff
======================
Computes the minimal patch set between two Element trees.

This is the single hottest loop in the framework — it runs on every
state change, on potentially large trees. Nexoria tries three backends,
in order, and application code never needs to know which one ran:

  1. the native C++ VDOM (`nexoria._nexoria_vdom_cpp`, see
     nexoria/native/cpp/vdom/) — fastest; diff-key identity is handled
     by a small Rust "safety core" (nexoria/native/rust_safety/) so key
     comparisons in the hot loop are integer equality checks against a
     Rust-owned interner, not hand-rolled C++ string lifetime code.
  2. the PyO3 Rust extension (`nexoria._nexoria_rs`, see
     nexoria/rust_ext/) — used if the C++ tier wasn't built.
  3. a pure-Python implementation, functionally identical to the other
     two (all three are covered by the same test vectors in
     tests/test_render_and_diff.py) — always available, no build step.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from ..core.element import Element

try:
    from .. import _nexoria_vdom_cpp  # native C++ VDOM (see native/cpp/vdom/)
    _vdom_engine = _nexoria_vdom_cpp.VDomEngine()
    _HAS_CPP = True
except ImportError:  # pragma: no cover - not built for this platform
    _nexoria_vdom_cpp = None
    _vdom_engine = None
    _HAS_CPP = False

try:
    from .. import _nexoria_rs  # compiled Rust extension (see rust_ext/)
    _HAS_RUST = True
except ImportError:  # pragma: no cover - pure-python environments
    _nexoria_rs = None
    _HAS_RUST = False


@dataclass
class Patch:
    """A single DOM mutation instruction, addressed by child-index path."""
    kind: str                     # "replace" | "update_props" | "insert" | "remove" | "text"
    path: list[int]
    payload: Any = field(default=None)

    def to_dict(self) -> dict:
        return {"op": self.kind, "path": self.path, "payload": self.payload}


def diff(old: Optional[Element], new: Optional[Element]) -> list[Patch]:
    """Public entry point. Returns an ordered list of Patch objects."""
    if _HAS_CPP:
        raw = _vdom_engine.diff(
            old.to_dict() if old else None,
            new.to_dict() if new else None,
        )
        return [Patch(kind=p["op"], path=p["path"], payload=p.get("payload")) for p in raw]
    if _HAS_RUST:
        raw = _nexoria_rs.diff(
            old.to_dict() if old else None,
            new.to_dict() if new else None,
        )
        return [Patch(kind=p["op"], path=p["path"], payload=p.get("payload")) for p in raw]
    return _diff_py(old, new, [])


def _diff_py(old: Optional[Element], new: Optional[Element], path: list[int]) -> list[Patch]:
    patches: list[Patch] = []

    if old is None and new is None:
        return patches
    if old is None:
        return [Patch("insert", path, new.to_dict())]
    if new is None:
        return [Patch("remove", path, None)]

    # text vs text
    if old.is_text() and new.is_text():
        if old.text != new.text:
            patches.append(Patch("text", path, new.text))
        return patches

    # differing node types -> full replace
    if old.is_text() != new.is_text() or old.tag != new.tag:
        return [Patch("replace", path, new.to_dict())]

    # same tag: diff props
    if old.props != new.props or old._handler_ids != new._handler_ids:
        merged_events = dict(new._handler_ids)
        patches.append(Patch("update_props", path, {
            "props": new.props,
            "events": merged_events,
        }))

    # diff children with key-aware matching
    old_children = old.children
    new_children = new.children
    old_keys = {c.key: c for c in old_children if c.key is not None}
    new_keys = {c.key: c for c in new_children if c.key is not None}

    if old_keys and new_keys and len(old_keys) == len(old_children) and len(new_keys) == len(new_children):
        # fully keyed lists: diff by identity, ignore positional churn.
        # (Each side just needs to be *independently* fully keyed here --
        # requiring old_children and new_children to be the same length
        # would defeat the entire point of keyed diffing, which exists
        # precisely to handle insertions/removals cleanly. See
        # tests/test_render_and_diff.py::test_diff_keyed_list_item_removed_uses_remove_not_positional_diff
        # for the regression this used to produce.)
        for key, new_child in new_keys.items():
            old_child = old_keys.get(key)
            patches.extend(_diff_py(old_child, new_child, path + [_index_of(new_children, new_child)]))
        for key in old_keys:
            if key not in new_keys:
                idx = _index_of(old_children, old_keys[key])
                patches.append(Patch("remove", path + [idx], None))
    else:
        max_len = max(len(old_children), len(new_children))
        for i in range(max_len):
            oc = old_children[i] if i < len(old_children) else None
            nc = new_children[i] if i < len(new_children) else None
            patches.extend(_diff_py(oc, nc, path + [i]))

    return patches


def _index_of(seq, item) -> int:
    for i, x in enumerate(seq):
        if x is item:
            return i
    return -1


def hot_path_active() -> str:
    """Report which diff backend is in use (for diagnostics/CLI)."""
    if _HAS_CPP:
        return "cpp"
    if _HAS_RUST:
        return "rust"
    return "python"
