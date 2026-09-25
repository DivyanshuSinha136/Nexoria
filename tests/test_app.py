import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from starlette.testclient import TestClient
from nexoria import App, Component, el, State, Router


class Home(Component):
    def setup(self):
        self.state = State({"count": 0})

    def render(self):
        return el("div", el("h1", "Home"), el("p", str(self.state["count"])))


class About(Component):
    def render(self):
        return el("div", el("h1", "About"))


def make_app():
    router = Router()
    router.add("/", Home)
    router.add("/about", About)
    return App(name="Test App", router=router, debug=True)


def test_home_route_renders():
    client = TestClient(make_app())
    r = client.get("/")
    assert r.status_code == 200
    assert "<h1>Home</h1>" in r.text
    assert "nx-root" in r.text


def test_about_route_renders():
    client = TestClient(make_app())
    r = client.get("/about")
    assert r.status_code == 200
    assert "<h1>About</h1>" in r.text


def test_unknown_route_is_404():
    client = TestClient(make_app())
    r = client.get("/nope")
    assert r.status_code == 404


def test_runtime_js_served():
    client = TestClient(make_app())
    r = client.get("/_nexoria/runtime.js")
    assert r.status_code == 200
    assert "nexoria" in r.text.lower() or "WebSocket" in r.text


def test_health_endpoint():
    client = TestClient(make_app())
    r = client.get("/_nexoria/health")
    assert r.status_code == 200
    assert r.json()["framework"] == "nexoria"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
