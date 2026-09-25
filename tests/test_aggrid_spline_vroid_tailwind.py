import sys, os, json, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from starlette.testclient import TestClient
from html import unescape
from nexoria import App, Component, el, Router
from nexoria.aggrid import Grid, Column, AGGRID_CDN
from nexoria.spline import SplineScene, SPLINE_CDN
from nexoria.vroid import VRMAvatar, VRM_CDN
from nexoria.tailwind import TailwindConfig, tailwind_runtime_tag, tailwind_cdn_url, TAILWIND_CDN
from nexoria.render.html import render_to_html


def _importmap_imports(html: str) -> dict:
    m = re.search(r'<script type="importmap">(.*?)</script>', html)
    return json.loads(m.group(1))["imports"] if m else {}


def _attr(html: str, name: str) -> dict:
    m = re.search(rf'{name}="([^"]*)"', html)
    return json.loads(unescape(m.group(1)))


# ---- AG Grid ------------------------------------------------------------

def test_column_serializes_with_extra_kwargs():
    c = Column("revenue", header_name="Revenue", sortable=True, filter="agNumberColumnFilter")
    assert c.to_dict() == {"field": "revenue", "headerName": "Revenue", "sortable": True, "filter": "agNumberColumnFilter"}


def test_grid_serializes_column_defs_and_row_data():
    grid = Grid(columns=[Column("name"), Column("revenue")], row_data=[{"name": "Acme", "revenue": 1}])
    d = grid.to_dict()
    assert d["columnDefs"] == [{"field": "name"}, {"field": "revenue"}]
    assert d["rowData"] == [{"name": "Acme", "revenue": 1}]


def test_grid_to_element_has_theme_class():
    grid = Grid(columns=[Column("x")], theme="alpine")
    node = grid.to_element()
    assert node.tag == "div"
    assert "ag-theme-alpine" in node.props["class"]
    assert "nx-aggrid-grid" in node.props["class"]


def test_grid_no_theme():
    grid = Grid(columns=[Column("x")], theme=None)
    node = grid.to_element()
    assert node.props["class"] == "nx-aggrid-grid"


def test_app_aggrid_false_by_default():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    r = TestClient(App(name="t", router=router)).get("/")
    assert "ag-grid" not in r.text.lower()


def test_app_aggrid_true_injects_importmap_theme_css_and_adapter():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", Grid(columns=[Column("x")]).to_element())

    router.add("/", Home)
    r = TestClient(App(name="t", router=router, aggrid=True)).get("/")
    imports = _importmap_imports(r.text)
    assert imports["ag-grid-community"] == AGGRID_CDN
    assert "ag-stack" in imports
    assert "ag-theme-quartz.min.css" in r.text
    assert "aggrid-adapter.js" in r.text


# ---- Spline ---------------------------------------------------------------

def test_splinescene_serializes():
    scene = SplineScene("https://prod.spline.design/x/scene.splinecode", background="#111")
    assert scene.to_dict() == {"url": "https://prod.spline.design/x/scene.splinecode", "background": "#111"}


def test_splinescene_to_element_is_canvas_with_id():
    scene = SplineScene("https://prod.spline.design/x/scene.splinecode")
    node = scene.to_element()
    assert node.tag == "canvas"
    assert node.props["id"] == scene.scene_id
    assert node.props["class"] == "nx-spline-canvas"


def test_splinescene_emit_event_attr():
    scene = SplineScene("https://x/scene.splinecode", scene_id="my-scene")
    attr = scene.emit_event_attr("mouseDown", "Cube")
    assert "my-scene" in attr
    assert "emitEvent" in attr
    assert "mouseDown" in attr and "Cube" in attr


def test_app_spline_true_injects_importmap_and_adapter():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", SplineScene("https://x/scene.splinecode").to_element())

    router.add("/", Home)
    r = TestClient(App(name="t", router=router, spline=True)).get("/")
    imports = _importmap_imports(r.text)
    assert imports["@splinetool/runtime"] == SPLINE_CDN
    assert "spline-adapter.js" in r.text


# ---- VRoid/VRM -----------------------------------------------------------

def test_vrmavatar_serializes():
    avatar = VRMAvatar("/static/a.vrm", camera_position=(0, 1, 2), auto_rotate=True)
    d = avatar.to_dict()
    assert d["url"] == "/static/a.vrm"
    assert d["cameraPosition"] == [0, 1, 2]
    assert d["autoRotate"] is True


def test_vrmavatar_to_element():
    avatar = VRMAvatar("/static/a.vrm", avatar_id="my-avatar")
    node = avatar.to_element()
    assert node.tag == "div"
    assert node.props["id"] == "my-avatar"
    assert node.props["class"] == "nx-vroid-avatar"


def test_app_vroid_true_injects_three_and_vrm_imports():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", VRMAvatar("/static/a.vrm").to_element())

    router.add("/", Home)
    r = TestClient(App(name="t", router=router, vroid=True)).get("/")
    imports = _importmap_imports(r.text)
    assert imports["@pixiv/three-vrm"] == VRM_CDN
    assert "three" in imports and "three/" in imports
    assert "vroid-adapter.js" in r.text


def test_app_vroid_and_threejs_together_share_three_entry_no_conflict():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", VRMAvatar("/static/a.vrm").to_element())

    router.add("/", Home)
    app = App(name="t", router=router, vroid=True, threejs=True)
    r = TestClient(app).get("/")
    assert r.text.count('type="importmap"') == 1
    imports = _importmap_imports(r.text)
    assert imports["three"]  # single consistent value, no duplicate key error


# ---- Tailwind ---------------------------------------------------------

def test_tailwind_cdn_url_no_plugins():
    assert tailwind_cdn_url() == TAILWIND_CDN


def test_tailwind_cdn_url_with_plugins():
    assert tailwind_cdn_url(["forms", "typography"]) == f"{TAILWIND_CDN}?plugins=forms,typography"


def test_tailwind_config_to_dict():
    cfg = TailwindConfig(dark_mode="class", theme_extend={"colors": {"brand": "#6366f1"}})
    d = cfg.to_dict()
    assert d["darkMode"] == "class"
    assert d["theme"]["extend"]["colors"]["brand"] == "#6366f1"


def test_tailwind_runtime_tag_no_config():
    tag = tailwind_runtime_tag()
    assert tag == f'<script src="{TAILWIND_CDN}"></script>'


def test_tailwind_runtime_tag_with_config_and_plugins():
    cfg = TailwindConfig(dark_mode="media")
    tag = tailwind_runtime_tag(cfg, plugins=["forms"])
    assert f"{TAILWIND_CDN}?plugins=forms" in tag
    assert "tailwind.config" in tag
    assert '"darkMode": "media"' in tag


def test_app_tailwind_false_by_default():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    r = TestClient(App(name="t", router=router)).get("/")
    assert "tailwindcss.com" not in r.text


def test_app_tailwind_true_injects_cdn_script():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    r = TestClient(App(name="t", router=router, tailwind=True)).get("/")
    assert TAILWIND_CDN in r.text


def test_app_tailwind_with_config_injects_config_script():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    cfg = TailwindConfig(dark_mode="class")
    r = TestClient(App(name="t", router=router, tailwind=True, tailwind_config=cfg)).get("/")
    assert "tailwind.config" in r.text
    assert '"darkMode": "class"' in r.text


# ---- everything together --------------------------------------------------

def test_all_new_integrations_plus_existing_ones_dont_conflict():
    router = Router()

    class Home(Component):
        def render(self):
            return el("div",
                Grid(columns=[Column("x")]).to_element(),
                SplineScene("https://x/scene.splinecode").to_element(),
                VRMAvatar("/static/a.vrm").to_element(),
            )

    router.add("/", Home)
    app = App(
        name="t", router=router,
        aggrid=True, spline=True, vroid=True, threejs=True, gsap=True, chartjs=True,
        tailwind=True,
    )
    r = TestClient(app).get("/")
    assert r.status_code == 200
    assert r.text.count('type="importmap"') == 1
    imports = _importmap_imports(r.text)
    expected = {"ag-grid-community", "ag-stack", "@splinetool/runtime", "three", "three/",
                "@pixiv/three-vrm", "gsap", "chart.js", "@kurkle/color"}
    assert set(imports.keys()) == expected


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
