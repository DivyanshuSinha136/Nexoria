"""
Regression test for the "buttons don't work" bug: the WebSocket handler
looked up sessions in a dict that was never populated (server never
registered one), and the client invented its own random session id that
the server could never match to anything, so every click was silently
dropped. This test drives the *actual* WS protocol end to end -- parse
the SSR'd handler id out of real HTML, open a real WebSocket, send a
real click message, and assert the counter actually changes -- rather
than only exercising the pieces in isolation.
"""
import sys, os, re, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from starlette.testclient import TestClient
from nexoria import App, Component, el, State, Router


class Counter(Component):
    def setup(self):
        self.state = State({"count": 0})

    def render(self):
        return el("div",
            el("p", f"count: {self.state['count']}", key="label"),
            el("button", "Increment", on_click=lambda e: self.state.update(
                count=self.state["count"] + 1)),
        )


def make_client():
    router = Router()
    router.add("/", Counter)
    app = App(name="t", router=router, debug=True)
    return TestClient(app)


def test_full_click_roundtrip_updates_counter():
    client = make_client()
    r = client.get("/")
    assert r.status_code == 200

    # Pull the real session id and the real handler id for the button's
    # on_click out of the actual rendered HTML -- exactly what the
    # browser's runtime.js does.
    hydration_match = re.search(
        r'<script id="nx-hydration-data"[^>]*>(.*?)</script>', r.text, re.S)
    assert hydration_match, "hydration payload script tag not found"
    hydration = json.loads(hydration_match.group(1))
    session_id = hydration["session"]
    assert session_id, "server did not issue a session id"

    handler_match = re.search(r'data-nx-on-click="([^"]+)"', r.text)
    assert handler_match, "no data-nx-on-click attribute found in rendered HTML"
    handler_id = handler_match.group(1)

    with client.websocket_connect("/_nexoria/live") as ws:
        ws.send_json({
            "event": "click",
            "handler_id": handler_id,
            "session": session_id,
            "payload": {},
        })
        response = ws.receive_json()
        assert response["type"] == "patch"
        patches = response["patches"]
        assert any(p["op"] == "text" and "count: 1" in str(p["payload"]) for p in patches), patches


def test_unknown_session_is_ignored_not_crashed():
    """An expired/unknown session (e.g. server restarted) should be a
    silent no-op, not an exception."""
    client = make_client()
    with client.websocket_connect("/_nexoria/live") as ws:
        ws.send_json({"event": "click", "handler_id": "h1", "session": "nonexistent", "payload": {}})
        # Should not crash the socket; send a second, real interaction to
        # prove the connection is still alive and functional afterward.
        r = client.get("/")
        hydration = json.loads(re.search(
            r'<script id="nx-hydration-data"[^>]*>(.*?)</script>', r.text, re.S).group(1))
        handler_id = re.search(r'data-nx-on-click="([^"]+)"', r.text).group(1)
        ws.send_json({
            "event": "click", "handler_id": handler_id,
            "session": hydration["session"], "payload": {},
        })
        response = ws.receive_json()
        assert response["type"] == "patch"


def test_session_cleaned_up_on_disconnect():
    client = make_client()
    r = client.get("/")
    hydration = json.loads(re.search(
        r'<script id="nx-hydration-data"[^>]*>(.*?)</script>', r.text, re.S).group(1))
    session_id = hydration["session"]

    # Find the underlying app instance to inspect its session store.
    app = client.app
    assert session_id in app._sessions

    handler_id = re.search(r'data-nx-on-click="([^"]+)"', r.text).group(1)
    with client.websocket_connect("/_nexoria/live") as ws:
        ws.send_json({"event": "click", "handler_id": handler_id, "session": session_id, "payload": {}})
        ws.receive_json()
    # After the `with` block closes the socket, the session should be
    # cleaned up rather than leaking forever.
    assert session_id not in app._sessions


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
