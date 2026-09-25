// Nexoria native VDOM (C++), advanced/high-performance tier.
// Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
//
// A third diff backend alongside the pure-Python one (nexoria.render.diff)
// and the PyO3 Rust one (nexoria/rust_ext/). Structurally the same
// algorithm (text/prop/insert/remove/replace + a keyed-children fast path),
// implemented as an arena-style tree of nodes in C++ for raw diff-loop
// speed, but with diff-key identity handled by nexoria-safety-core (a
// small Rust crate, see ../nexoria_safety_core.h) rather than hand-rolled
// C++ string-lifetime code -- key comparisons in the hot loop become
// integer equality checks against a Rust-owned interner instead of
// C-string comparisons/lifetime bookkeeping.
//
// nexoria.render.diff picks whichever backend is actually built, in order
// native-C++ > PyO3-Rust > pure-Python -- this module is purely optional
// acceleration, never a hard dependency.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <memory>
#include <string>
#include <vector>
#include <unordered_map>

#include "nexoria_safety_core.h"

namespace py = pybind11;

struct VNode {
    bool is_text = false;
    std::string text;
    std::string tag;
    py::dict props;
    py::dict events;
    py::object key_value = py::none(); // preserved for round-trip fidelity in insert/replace payloads
    uint32_t key_id = 0; // 0 == no key, guaranteed by nexoria_safety_core
    std::vector<std::unique_ptr<VNode>> children;
};

struct Patch {
    const char *op;
    std::vector<int64_t> path;
    py::object payload;
};

class VDomEngine {
public:
    VDomEngine() { interner_ = nx_interner_new(); }
    ~VDomEngine() { nx_interner_free(interner_); }
    VDomEngine(const VDomEngine &) = delete;
    VDomEngine &operator=(const VDomEngine &) = delete;

    std::unique_ptr<VNode> parse(const py::object &obj) {
        auto node = std::make_unique<VNode>();
        if (obj.is_none()) return node; // caller checks is_text tag emptiness only via null unique_ptr normally
        py::dict d = obj.cast<py::dict>();
        std::string t = d["t"].cast<std::string>();
        if (t == "text") {
            node->is_text = true;
            node->text = d["v"].cast<std::string>();
            return node;
        }
        node->tag = d["tag"].cast<std::string>();
        node->props = d.contains("props") ? d["props"].cast<py::dict>() : py::dict();
        node->events = d.contains("events") ? d["events"].cast<py::dict>() : py::dict();
        if (d.contains("key") && !d["key"].is_none()) {
            node->key_value = d["key"];
            std::string key_str = py::str(d["key"]).cast<std::string>();
            node->key_id = nx_interner_intern(interner_,
                reinterpret_cast<const uint8_t *>(key_str.data()), key_str.size());
        }
        if (d.contains("children")) {
            for (auto child : d["children"]) {
                node->children.push_back(parse(py::reinterpret_borrow<py::object>(child)));
            }
        }
        return node;
    }

    py::object node_to_dict(const VNode *n) {
        py::dict out;
        if (n->is_text) {
            out["t"] = "text";
            out["v"] = n->text;
            return out;
        }
        out["t"] = "el";
        out["tag"] = n->tag;
        out["props"] = n->props;
        out["events"] = n->events;
        out["key"] = n->key_value;
        py::list kids;
        for (auto &c : n->children) kids.append(node_to_dict(c.get()));
        out["children"] = kids;
        return out;
    }

    py::list diff(py::object old_obj, py::object new_obj) {
        auto old_node = old_obj.is_none() ? nullptr : parse(old_obj);
        auto new_node = new_obj.is_none() ? nullptr : parse(new_obj);
        std::vector<Patch> patches;
        std::vector<int64_t> path;
        diff_into(old_node.get(), new_node.get(), path, patches);

        py::list out;
        for (auto &p : patches) {
            py::dict d;
            d["op"] = p.op;
            py::list path_list;
            for (auto seg : p.path) path_list.append(seg);
            d["path"] = path_list;
            d["payload"] = p.payload;
            out.append(d);
        }
        return out;
    }

private:
    Interner *interner_;

    bool props_equal(const py::dict &a, const py::dict &b) {
        return a.equal(b);
    }

    void diff_into(const VNode *old_n, const VNode *new_n,
                   std::vector<int64_t> &path, std::vector<Patch> &out) {
        if (!old_n && !new_n) return;
        if (!old_n) { out.push_back({"insert", path, node_to_dict(new_n)}); return; }
        if (!new_n) { out.push_back({"remove", path, py::none()}); return; }

        if (old_n->is_text && new_n->is_text) {
            if (old_n->text != new_n->text) {
                out.push_back({"text", path, py::cast(new_n->text)});
            }
            return;
        }
        if (old_n->is_text != new_n->is_text || old_n->tag != new_n->tag) {
            out.push_back({"replace", path, node_to_dict(new_n)});
            return;
        }

        if (!props_equal(old_n->props, new_n->props) || !props_equal(old_n->events, new_n->events)) {
            py::dict payload;
            payload["props"] = new_n->props;
            payload["events"] = new_n->events;
            out.push_back({"update_props", path, payload});
        }

        diff_children(old_n->children, new_n->children, path, out);
    }

    void diff_children(const std::vector<std::unique_ptr<VNode>> &old_children,
                        const std::vector<std::unique_ptr<VNode>> &new_children,
                        std::vector<int64_t> &path, std::vector<Patch> &out) {
        bool old_all_keyed = !old_children.empty();
        bool new_all_keyed = !new_children.empty();
        for (auto &c : old_children) if (c->key_id == 0) { old_all_keyed = false; break; }
        for (auto &c : new_children) if (c->key_id == 0) { new_all_keyed = false; break; }

        if (old_all_keyed && new_all_keyed) {
            std::unordered_map<uint32_t, const VNode *> old_by_key;
            std::unordered_map<uint32_t, size_t> old_index_by_key;
            for (size_t i = 0; i < old_children.size(); ++i) {
                old_by_key[old_children[i]->key_id] = old_children[i].get();
                old_index_by_key[old_children[i]->key_id] = i;
            }
            for (size_t i = 0; i < new_children.size(); ++i) {
                const VNode *new_child = new_children[i].get();
                auto it = old_by_key.find(new_child->key_id);
                const VNode *old_child = it == old_by_key.end() ? nullptr : it->second;
                path.push_back((int64_t)i);
                diff_into(old_child, new_child, path, out);
                path.pop_back();
            }
            for (auto &kv : old_index_by_key) {
                bool still_present = false;
                for (auto &nc : new_children) {
                    if (nx_interner_ids_equal(nc->key_id, kv.first)) { still_present = true; break; }
                }
                if (!still_present) {
                    path.push_back((int64_t)kv.second);
                    out.push_back({"remove", path, py::none()});
                    path.pop_back();
                }
            }
            return;
        }

        size_t max_len = std::max(old_children.size(), new_children.size());
        for (size_t i = 0; i < max_len; ++i) {
            const VNode *oc = i < old_children.size() ? old_children[i].get() : nullptr;
            const VNode *nc = i < new_children.size() ? new_children[i].get() : nullptr;
            path.push_back((int64_t)i);
            diff_into(oc, nc, path, out);
            path.pop_back();
        }
    }
};

PYBIND11_MODULE(_nexoria_vdom_cpp, m) {
    m.doc() = "Nexoria native VDOM (C++ diff engine + Rust-backed key safety). "
              "Part of the Pythonaibrain ecosystem.";

    py::class_<VDomEngine>(m, "VDomEngine")
        .def(py::init<>())
        .def("diff", &VDomEngine::diff, py::arg("old"), py::arg("new"),
             "Diff two Element.to_dict()-shaped trees (or None) and return "
             "a list of patch dicts, identical in shape to the pure-Python "
             "and PyO3-Rust backends.");
}
