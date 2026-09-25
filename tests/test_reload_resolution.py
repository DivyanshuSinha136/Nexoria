import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nexoria import App, Router, Component, el


class Dummy(Component):
    def render(self):
        return el("div", "hi")


def test_resolve_import_string_finds_module_var_and_dir(tmp_path):
    """
    Regression test for the bug where App.run(reload=True) crashed with
    uvicorn's "You must pass the application as an import string" warning
    and exited immediately, because uvicorn.run() was given a live App
    object instead of a "module:var" string. App._resolve_import_string
    must find the top-level variable name this App is bound to and the
    directory of the file it's defined in, regardless of cwd.
    """
    app_file = tmp_path / "app.py"
    app_file.write_text(
        "import sys, os\n"
        f"sys.path.insert(0, {str(os.path.join(os.path.dirname(__file__), '..'))!r})\n"
        "from nexoria import App, Router, Component, el\n"
        "class Home(Component):\n"
        "    def render(self):\n"
        "        return el('div', 'hi')\n"
        "router = Router()\n"
        "router.add('/', Home)\n"
        "app = App(name='t', router=router)\n"
        "target, app_dir = app._resolve_import_string()\n"
        "assert target == 'app:app', target\n"
        "assert app_dir == os.path.dirname(os.path.abspath(__file__)), app_dir\n"
        "print('OK')\n"
    )
    import subprocess
    result = subprocess.run([sys.executable, str(app_file)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_resolve_import_string_raises_without_toplevel_binding():
    router = Router()
    router.add("/", Dummy)
    app = App(name="t", router=router)
    # Called directly (not bound to a module-level variable that `is app`
    # from the perspective of some *other* calling frame) -> should raise
    # a clear error rather than silently misbehaving.
    def caller():
        return app._resolve_import_string()

    import pytest
    with pytest.raises(RuntimeError):
        caller()


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
