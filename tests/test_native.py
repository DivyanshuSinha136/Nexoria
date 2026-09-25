"""
Tests for nexoria.native (the npm registry client + embedded JS engine).

Some tests here hit the real public npm registry over the network (there
is no realistic way to test "fetch a real npm package with no Node
installed" without actually fetching one). They're marked so they can be
skipped in fully offline environments.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from nexoria.native import npm, js_available

pytestmark = pytest.mark.network


def _network_available() -> bool:
    import urllib.request
    try:
        urllib.request.urlopen("https://registry.npmjs.org/lodash", timeout=5)
        return True
    except Exception:
        return False


requires_network = pytest.mark.skipif(not _network_available(), reason="no network access")
requires_native_engine = pytest.mark.skipif(not js_available(), reason="native JS engine not built")


@requires_network
def test_npm_resolve_real_package():
    info = npm.resolve("lodash")
    assert info.name == "lodash"
    assert info.tarball_url.startswith("https://registry.npmjs.org/")


@requires_network
def test_npm_install_extracts_real_tarball(tmp_path):
    d = npm.install("lodash", cache_dir=str(tmp_path))
    assert os.path.isdir(d)
    assert os.path.isfile(os.path.join(d, "package.json"))
    entry = npm.entry_point(d)
    assert os.path.isfile(entry)


@requires_network
@requires_native_engine
def test_runtime_require_runs_real_lodash():
    from nexoria.native import Runtime
    rt = Runtime()
    rt.require("lodash")  # fetches from the real registry + registers the package root
    result = rt.eval('''
        var _ = require("lodash");
        JSON.stringify({
            chunk: _.chunk([1,2,3,4,5], 2),
            uniq: _.uniq([1,2,2,3]),
            sum: _.sum([1,2,3]),
        });
    ''')
    import json
    parsed = json.loads(result)
    assert parsed["chunk"] == [[1, 2], [3, 4], [5]]
    assert parsed["uniq"] == [1, 2, 3]
    assert parsed["sum"] == 6


@requires_native_engine
def test_engine_eval_basic_values_without_network():
    from nexoria import _nexoria_js
    eng = _nexoria_js.Engine()
    assert eng.eval("1 + 2") == 3
    assert eng.eval("[1,2,3].map(x => x * 2)") == [2, 4, 6]
    assert eng.eval("({a: 1, b: null})") == {"a": 1, "b": None}
    assert eng.eval("'hello'") == "hello"


@requires_native_engine
def test_engine_require_relative_module(tmp_path):
    from nexoria import _nexoria_js
    (tmp_path / "helper.js").write_text("module.exports = { square: x => x * x };")
    (tmp_path / "main.js").write_text(
        "var h = require('./helper'); module.exports = h.square(6);"
    )
    eng = _nexoria_js.Engine()
    result = eng.eval(f'require("{tmp_path / "main.js"}")'.replace("\\", "/"))
    assert result == 36


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
