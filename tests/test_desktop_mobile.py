import sys, os, json, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nexoria.desktop import scaffold_electron
from nexoria.mobile import scaffold_capacitor


def _node_check(path: str) -> None:
    result = subprocess.run(["node", "--check", path], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_scaffold_electron_creates_valid_files(tmp_path):
    d = scaffold_electron(str(tmp_path), app_name="My App", port=9000)
    assert os.path.isdir(d)
    assert os.path.isfile(os.path.join(d, "main.js"))
    assert os.path.isfile(os.path.join(d, "preload.js"))
    assert os.path.isfile(os.path.join(d, "package.json"))

    _node_check(os.path.join(d, "main.js"))
    _node_check(os.path.join(d, "preload.js"))

    with open(os.path.join(d, "package.json")) as f:
        pkg = json.load(f)
    assert pkg["main"] == "main.js"
    assert "electron" in pkg["devDependencies"]
    assert "electron-builder" in pkg["devDependencies"]


def test_scaffold_electron_main_js_has_correct_port_and_entry(tmp_path):
    d = scaffold_electron(str(tmp_path), app_name="My App", entry_file="server.py", port=9000)
    content = open(os.path.join(d, "main.js")).read()
    assert "const PORT = 9000;" in content
    assert '"server.py"' in content
    assert "/_nexoria/health" in content  # health check endpoint every App already serves


def test_scaffold_electron_is_idempotent(tmp_path):
    d1 = scaffold_electron(str(tmp_path), app_name="A")
    d2 = scaffold_electron(str(tmp_path), app_name="B")
    assert d1 == d2
    content = open(os.path.join(d2, "main.js")).read()
    assert "for B" in content  # second call's app_name won, files were overwritten cleanly


def test_scaffold_capacitor_creates_valid_config(tmp_path):
    d = scaffold_capacitor(str(tmp_path), app_name="My App", server_url="https://real.example.org")
    assert os.path.isfile(os.path.join(d, "capacitor.config.json"))
    assert os.path.isfile(os.path.join(d, "package.json"))
    assert os.path.isdir(os.path.join(d, "www"))

    with open(os.path.join(d, "capacitor.config.json")) as f:
        config = json.load(f)
    assert config["server"]["url"] == "https://real.example.org"
    assert config["appName"] == "My App"
    assert config["server"]["cleartext"] is False  # https -> no cleartext needed


def test_scaffold_capacitor_cleartext_true_for_http():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = scaffold_capacitor(td, server_url="http://192.168.1.5:8000")
        config = json.load(open(os.path.join(d, "capacitor.config.json")))
        assert config["server"]["cleartext"] is True


def test_scaffold_capacitor_package_json_valid(tmp_path):
    d = scaffold_capacitor(str(tmp_path))
    with open(os.path.join(d, "package.json")) as f:
        pkg = json.load(f)
    assert "@capacitor/core" in pkg["dependencies"]
    assert "@capacitor/android" in pkg["devDependencies"]
    assert "@capacitor/ios" in pkg["devDependencies"]


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
