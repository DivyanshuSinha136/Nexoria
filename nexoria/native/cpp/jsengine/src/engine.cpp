// nexoria native JS engine.
// Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
//
// Embeds QuickJS-ng (vendored under vendor/quickjs/) to run real JavaScript
// -- including plain-JS npm packages fetched by nexoria.native.npm -- with
// no Node.js or system JS runtime installed. This implements a *minimal*
// CommonJS module loader (require/module.exports/__dirname/__filename) and
// a handful of Node-like globals (console, process, a synchronous
// setTimeout shim). It is NOT Node: there is no real event loop, no fs/
// http/child_process/net builtins, and no native addon (node-gyp) support.
// Packages that only use plain JS/ES features (lodash, dayjs, most
// animation/math/data utility libraries) run correctly; packages that
// need the DOM (React, most UI libs), a bundler/dev-server (Next.js), or
// native addons will not run here -- consider those out of scope for
// this engine and documented as such.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <fstream>
#include <sstream>
#include <sys/stat.h>
#include <unordered_map>
#include <vector>
#include <memory>
#include <stdexcept>

extern "C" {
#include "quickjs.h"
}

namespace py = pybind11;

// ---------------------------------------------------------------------
// Small filesystem helpers (no dependency on Node's `fs` -- just C++ std)
// ---------------------------------------------------------------------
static bool file_exists(const std::string &path) {
    struct stat st;
    return ::stat(path.c_str(), &st) == 0 && S_ISREG(st.st_mode);
}

static std::string dirname_of(const std::string &path) {
    auto pos = path.find_last_of('/');
    return pos == std::string::npos ? std::string(".") : path.substr(0, pos);
}

static std::string read_file(const std::string &path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) throw std::runtime_error("Cannot read file: " + path);
    std::ostringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

static std::string normalize_join(const std::string &base, const std::string &rel) {
    // Very small path joiner/normalizer -- good enough for CommonJS-style
    // "./x" / "../x" resolution without pulling in <filesystem> quirks.
    std::vector<std::string> parts;
    std::string combined = base + "/" + rel;
    std::stringstream ss(combined);
    std::string seg;
    while (std::getline(ss, seg, '/')) {
        if (seg.empty() || seg == ".") continue;
        if (seg == "..") { if (!parts.empty()) parts.pop_back(); continue; }
        parts.push_back(seg);
    }
    std::string out = combined[0] == '/' ? "/" : "";
    for (size_t i = 0; i < parts.size(); ++i) {
        out += parts[i];
        if (i + 1 < parts.size()) out += "/";
    }
    return out;
}

// ---------------------------------------------------------------------
// JS <-> Python value conversion
// ---------------------------------------------------------------------
struct JSFunctionHandle; // fwd decl

class Engine {
public:
    JSRuntime *rt;
    JSContext *ctx;
    std::unordered_map<std::string, JSValue> module_cache;
    std::vector<std::string> dir_stack;                    // for relative require()
    std::unordered_map<std::string, std::string> package_roots; // name -> local dir

    Engine() {
        rt = JS_NewRuntime();
        ctx = JS_NewContext(rt);
        JS_SetContextOpaque(ctx, this);
        dir_stack.push_back(".");
        install_globals();
    }

    ~Engine() {
        for (auto &kv : module_cache) JS_FreeValue(ctx, kv.second);
        JS_FreeContext(ctx);
        JS_FreeRuntime(rt);
    }

    Engine(const Engine &) = delete;
    Engine &operator=(const Engine &) = delete;

    void register_package_root(const std::string &name, const std::string &dir) {
        package_roots[name] = dir;
    }

    py::object eval(const std::string &code, const std::string &filename) {
        JSValue result = JS_Eval(ctx, code.c_str(), code.size(), filename.c_str(), JS_EVAL_TYPE_GLOBAL);
        py::object out = to_python(result);
        check_exception(result);
        JS_FreeValue(ctx, result);
        return out;
    }

    py::object require(const std::string &specifier) {
        std::string resolved = resolve(specifier);
        return to_python(require_resolved(resolved));
    }

    std::string resolve(const std::string &specifier) {
        if (specifier.rfind("./", 0) == 0 || specifier.rfind("../", 0) == 0) {
            std::string base = normalize_join(dir_stack.back(), specifier);
            return resolve_file_candidates(base);
        }
        if (!specifier.empty() && specifier[0] == '/') {
            // absolute path, same as Node: require("/abs/path/to/file")
            return resolve_file_candidates(specifier);
        }
        // top-level / scoped package name, optionally with a subpath:
        // "lodash" or "lodash/fp" or "@scope/pkg/sub"
        std::string name, subpath;
        size_t slash = specifier.find('/');
        bool scoped = !specifier.empty() && specifier[0] == '@';
        if (scoped) {
            size_t second_slash = specifier.find('/', slash + 1);
            name = second_slash == std::string::npos ? specifier : specifier.substr(0, second_slash);
            subpath = second_slash == std::string::npos ? "" : specifier.substr(second_slash + 1);
        } else {
            name = slash == std::string::npos ? specifier : specifier.substr(0, slash);
            subpath = slash == std::string::npos ? "" : specifier.substr(slash + 1);
        }
        auto it = package_roots.find(name);
        if (it == package_roots.end()) {
            throw std::runtime_error("Cannot find module '" + specifier +
                "' -- no package root registered (did you call npm.install() / Runtime.require() first?)");
        }
        std::string pkg_dir = it->second;
        if (!subpath.empty()) {
            return resolve_file_candidates(pkg_dir + "/" + subpath);
        }
        return resolve_file_candidates(pkg_dir + "/" + package_main(pkg_dir));
    }

private:
    std::string package_main(const std::string &pkg_dir) {
        std::string pj = pkg_dir + "/package.json";
        if (!file_exists(pj)) return "index.js";
        std::string content = read_file(pj);
        // Minimal "main" field extraction without a full JSON parser
        // dependency in C++: parse via QuickJS itself (it already has a
        // JSON parser built in), then read the field back out.
        JSValue parsed = JS_ParseJSON(ctx, content.c_str(), content.size(), "package.json");
        std::string result = "index.js";
        if (!JS_IsException(parsed)) {
            JSValue main_val = JS_GetPropertyStr(ctx, parsed, "main");
            if (JS_IsString(main_val)) {
                const char *s = JS_ToCString(ctx, main_val);
                if (s) { result = s; JS_FreeCString(ctx, s); }
            }
            JS_FreeValue(ctx, main_val);
        }
        JS_FreeValue(ctx, parsed);
        return result;
    }

    std::string resolve_file_candidates(const std::string &base) {
        if (file_exists(base)) return base;
        if (file_exists(base + ".js")) return base + ".js";
        if (file_exists(base + "/index.js")) return base + "/index.js";
        throw std::runtime_error("Module not found: " + base);
    }

    JSValue require_resolved(const std::string &resolved_path) {
        auto cached = module_cache.find(resolved_path);
        if (cached != module_cache.end()) return JS_DupValue(ctx, cached->second);

        std::string source = read_file(resolved_path);
        std::string dir = dirname_of(resolved_path);
        std::string wrapped = "(function(module, exports, require, __filename, __dirname) {\n"
                               + source + "\n})";

        JSValue wrapper_fn = JS_Eval(ctx, wrapped.c_str(), wrapped.size(),
                                     resolved_path.c_str(), JS_EVAL_TYPE_GLOBAL);
        check_exception(wrapper_fn);

        JSValue module_obj = JS_NewObject(ctx);
        JSValue exports_obj = JS_NewObject(ctx);
        JS_SetPropertyStr(ctx, module_obj, "exports", JS_DupValue(ctx, exports_obj));

        JSValue require_fn = JS_NewCFunction(ctx, &Engine::require_trampoline, "require", 1);

        JSValue argv[5] = {
            module_obj, exports_obj, require_fn,
            JS_NewString(ctx, resolved_path.c_str()),
            JS_NewString(ctx, dir.c_str()),
        };

        dir_stack.push_back(dir);
        JSValue call_result = JS_Call(ctx, wrapper_fn, JS_UNDEFINED, 5, argv);
        dir_stack.pop_back();

        JS_FreeValue(ctx, wrapper_fn);
        JS_FreeValue(ctx, require_fn);
        JS_FreeValue(ctx, argv[3]);
        JS_FreeValue(ctx, argv[4]);
        check_exception(call_result);
        JS_FreeValue(ctx, call_result);

        JSValue final_exports = JS_GetPropertyStr(ctx, module_obj, "exports");
        JS_FreeValue(ctx, module_obj);
        JS_FreeValue(ctx, exports_obj);

        module_cache[resolved_path] = JS_DupValue(ctx, final_exports);
        return final_exports;
    }

    static JSValue require_trampoline(JSContext *ctx, JSValueConst this_val,
                                       int argc, JSValueConst *argv) {
        Engine *self = static_cast<Engine *>(JS_GetContextOpaque(ctx));
        if (argc < 1 || !JS_IsString(argv[0])) {
            return JS_ThrowTypeError(ctx, "require() expects a string specifier");
        }
        const char *spec_c = JS_ToCString(ctx, argv[0]);
        std::string spec(spec_c);
        JS_FreeCString(ctx, spec_c);
        try {
            std::string resolved = self->resolve(spec);
            return self->require_resolved(resolved);
        } catch (const std::exception &e) {
            return JS_ThrowReferenceError(ctx, "%s", e.what());
        }
    }

    void check_exception(JSValue &v) {
        if (JS_IsException(v)) {
            JSValue exc = JS_GetException(ctx);
            const char *msg = JS_ToCString(ctx, exc);
            std::string message = msg ? msg : "unknown JS exception";
            JS_FreeCString(ctx, msg);
            JS_FreeValue(ctx, exc);
            throw std::runtime_error("JS exception: " + message);
        }
    }

    static JSValue console_log_impl(JSContext *ctx, JSValueConst this_val,
                                     int argc, JSValueConst *argv) {
        for (int i = 0; i < argc; ++i) {
            const char *s = JS_ToCString(ctx, argv[i]);
            if (s) { fputs(s, stdout); if (i + 1 < argc) fputc(' ', stdout); JS_FreeCString(ctx, s); }
        }
        fputc('\n', stdout);
        return JS_UNDEFINED;
    }

    static JSValue set_timeout_impl(JSContext *ctx, JSValueConst this_val,
                                     int argc, JSValueConst *argv) {
        // No real event loop here: this is a synchronous shim that calls
        // the callback immediately. Fine for libraries that use
        // setTimeout(fn, 0) as a "next tick" hint; NOT a substitute for
        // real asynchronous timing.
        if (argc >= 1 && JS_IsFunction(ctx, argv[0])) {
            JSValue r = JS_Call(ctx, argv[0], JS_UNDEFINED, 0, nullptr);
            JS_FreeValue(ctx, r);
        }
        return JS_NewInt32(ctx, 0);
    }

    void install_globals() {
        JSValue global = JS_GetGlobalObject(ctx);

        JSValue console = JS_NewObject(ctx);
        JSValue log_fn = JS_NewCFunction(ctx, &Engine::console_log_impl, "log", 0);
        JS_SetPropertyStr(ctx, console, "log", JS_DupValue(ctx, log_fn));
        JS_SetPropertyStr(ctx, console, "error", JS_DupValue(ctx, log_fn));
        JS_SetPropertyStr(ctx, console, "warn", log_fn);
        JS_SetPropertyStr(ctx, global, "console", console);

        JSValue process = JS_NewObject(ctx);
        JS_SetPropertyStr(ctx, process, "platform", JS_NewString(ctx, "nexoria-embedded"));
        JS_SetPropertyStr(ctx, process, "version", JS_NewString(ctx, "v0-quickjs"));
        JS_SetPropertyStr(ctx, process, "env", JS_NewObject(ctx));
        JS_SetPropertyStr(ctx, global, "process", process);

        JS_SetPropertyStr(ctx, global, "setTimeout",
                           JS_NewCFunction(ctx, &Engine::set_timeout_impl, "setTimeout", 2));
        JS_SetPropertyStr(ctx, global, "clearTimeout",
                           JS_NewCFunction(ctx, [](JSContext *c, JSValueConst, int, JSValueConst *) {
                               return JS_UNDEFINED;
                           }, "clearTimeout", 1));
        JS_SetPropertyStr(ctx, global, "setImmediate",
                           JS_NewCFunction(ctx, &Engine::set_timeout_impl, "setImmediate", 1));
        JS_SetPropertyStr(ctx, global, "clearImmediate",
                           JS_NewCFunction(ctx, [](JSContext *c, JSValueConst, int, JSValueConst *) {
                               return JS_UNDEFINED;
                           }, "clearImmediate", 1));
        JS_SetPropertyStr(ctx, global, "queueMicrotask",
                           JS_NewCFunction(ctx, &Engine::set_timeout_impl, "queueMicrotask", 1));

        // Also expose require() at the top level so plain eval()'d scripts
        // (not just loaded CommonJS modules) can call it directly.
        JS_SetPropertyStr(ctx, global, "require",
                           JS_NewCFunction(ctx, &Engine::require_trampoline, "require", 1));

        JS_FreeValue(ctx, global);
    }

public:
    py::object to_python(JSValueConst v) {
        int tag = JS_VALUE_GET_TAG(v);
        if (JS_IsException(v)) return py::none();
        if (JS_IsUndefined(v) || JS_IsNull(v)) return py::none();
        if (JS_IsBool(v)) return py::bool_(JS_ToBool(ctx, v));
        if (JS_IsNumber(v)) {
            double d;
            JS_ToFloat64(ctx, &d, v);
            if (d == (int64_t)d) return py::int_((int64_t)d);
            return py::float_(d);
        }
        if (JS_IsString(v)) {
            const char *s = JS_ToCString(ctx, v);
            std::string out = s ? s : "";
            JS_FreeCString(ctx, s);
            return py::str(out);
        }
        if (JS_IsArray(v)) {
            py::list out;
            int64_t len = 0;
            JSValue len_val = JS_GetPropertyStr(ctx, v, "length");
            JS_ToInt64(ctx, &len, len_val);
            JS_FreeValue(ctx, len_val);
            for (int64_t i = 0; i < len; ++i) {
                JSValue item = JS_GetPropertyUint32(ctx, v, (uint32_t)i);
                out.append(to_python(item));
                JS_FreeValue(ctx, item);
            }
            return out;
        }
        if (JS_IsFunction(ctx, v)) {
            return py::str("[Function]"); // callables aren't marshalled (see docs)
        }
        if (JS_IsObject(v)) {
            py::dict out;
            JSPropertyEnum *props;
            uint32_t count;
            if (JS_GetOwnPropertyNames(ctx, &props, &count, v,
                                       JS_GPN_STRING_MASK | JS_GPN_ENUM_ONLY) == 0) {
                for (uint32_t i = 0; i < count; ++i) {
                    JSValue key_val = JS_AtomToString(ctx, props[i].atom);
                    const char *key_c = JS_ToCString(ctx, key_val);
                    std::string key = key_c ? key_c : "";
                    JS_FreeCString(ctx, key_c);
                    JS_FreeValue(ctx, key_val);
                    JSValue prop_val = JS_GetProperty(ctx, v, props[i].atom);
                    out[py::str(key)] = to_python(prop_val);
                    JS_FreeValue(ctx, prop_val);
                    JS_FreeAtom(ctx, props[i].atom);
                }
                js_free(ctx, props);
            }
            return out;
        }
        return py::none();
    }
};

PYBIND11_MODULE(_nexoria_js, m) {
    m.doc() = "Nexoria embedded JS engine (QuickJS-ng) -- run real JS/npm "
              "packages with no Node.js installed. Part of the Pythonaibrain ecosystem.";

    py::class_<Engine>(m, "Engine")
        .def(py::init<>())
        .def("register_package_root", &Engine::register_package_root,
             py::arg("name"), py::arg("dir"),
             "Tell the engine where a package's local files live (usually "
             "the directory nexoria.native.npm.install() returned) so "
             "require('that-package') resolves without Node's module algorithm.")
        .def("eval", &Engine::eval, py::arg("code"), py::arg("filename") = "<eval>",
             "Evaluate a JS source string as a script; returns the completion "
             "value converted to a Python object (str/int/float/bool/None/"
             "list/dict). JS functions are not marshalled back to Python.")
        .def("require", &Engine::require, py::arg("specifier"),
             "CommonJS-style require('pkg' | './relative/file'). Runs the "
             "module (with a minimal console/process/setTimeout shim) and "
             "returns its module.exports, converted to a Python object.");
}
