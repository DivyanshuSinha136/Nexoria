import sys, os, json, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from starlette.testclient import TestClient
from html import unescape
from nexoria import App, Component, el, Router
from nexoria.babylonjs import BabylonScene, BabylonMesh, BABYLONJS_CDN
from nexoria.iconify import Icon, ICONIFY_CDN
from nexoria.shiki import CodeBlock, SHIKI_CDN
from nexoria.qrcode import QRCode, QRCODE_CDN
from nexoria.barcode import Barcode, BWIPJS_CDN
from nexoria.openlayers import Map, OL_JS_CDN
from nexoria.webcam import Webcam, WEBCAM_CDN
from nexoria.translate import translate, Translation
from nexoria.render.html import render_to_html


def _importmap_imports(html: str) -> dict:
    m = re.search(r'<script type="importmap">(.*?)</script>', html)
    return json.loads(m.group(1))["imports"] if m else {}


def _make_app(**kwargs):
    router = Router()

    class Home(Component):
        def render(self):
            return el("div", "hi")

    router.add("/", Home)
    return App(name="t", router=router, **kwargs)


# ---- Babylon.js -----------------------------------------------------------

def test_babylon_mesh_and_scene_serialize():
    scene = BabylonScene(background="#111")
    scene.add(BabylonMesh("sphere", color="#22d3ee", animate="rotate_y"))
    d = scene.to_dict()
    assert d["background"] == "#111"
    assert d["meshes"][0]["type"] == "sphere"
    assert d["meshes"][0]["animate"] == "rotate_y"


def test_babylon_to_element_is_canvas():
    node = BabylonScene().to_element()
    assert node.tag == "canvas"
    assert "nx-babylon-scene" in node.props["class"]


def test_app_babylonjs_injects_importmap():
    r = TestClient(_make_app(babylonjs=True)).get("/")
    imports = _importmap_imports(r.text)
    assert imports["@babylonjs/core"] == BABYLONJS_CDN
    assert "babylon-adapter.js" in r.text


# ---- Iconify ----------------------------------------------------------

def test_icon_to_element():
    node = Icon("mdi:home", size="24px", color="red").to_element()
    assert node.tag == "iconify-icon"
    assert node.props["icon"] == "mdi:home"
    assert "24px" in node.props["style"]


def test_app_iconify_injects_script_not_importmap():
    r = TestClient(_make_app(iconify=True)).get("/")
    assert ICONIFY_CDN in r.text
    # classic script -- must not appear in the shared import map
    imports = _importmap_imports(r.text)
    assert "iconify-icon" not in imports


# ---- Shiki --------------------------------------------------------------

def test_codeblock_renders_pre_code_fallback():
    node = CodeBlock("print(1)", lang="python").to_element()
    html = render_to_html(node)
    assert "<pre><code>print(1)</code></pre>" in html


def test_app_shiki_injects_importmap():
    r = TestClient(_make_app(shiki=True)).get("/")
    imports = _importmap_imports(r.text)
    assert imports["shiki"] == SHIKI_CDN
    assert "shiki-adapter.js" in r.text


# ---- QR code ------------------------------------------------------------

def test_qrcode_to_dict_defaults():
    d = QRCode("https://example.com").to_dict()
    assert d["data"] == "https://example.com"
    assert d["width"] == 200
    assert d["dotsOptions"]["color"] == "#000000"


def test_app_qrcode_injects_classic_script_not_importmap():
    r = TestClient(_make_app(qrcode=True)).get("/")
    assert QRCODE_CDN in r.text
    assert "qrcode-adapter.js" in r.text
    imports = _importmap_imports(r.text)
    assert "qr-code-styling" not in imports


# ---- Barcode ------------------------------------------------------------

def test_barcode_to_dict_defaults():
    d = Barcode("0123456789", symbology="ean13").to_dict()
    assert d["bcid"] == "ean13"
    assert d["text"] == "0123456789"
    assert d["includetext"] is True


def test_app_barcode_injects_importmap():
    r = TestClient(_make_app(barcode=True)).get("/")
    imports = _importmap_imports(r.text)
    assert imports["bwip-js"] == BWIPJS_CDN


# ---- OpenLayers -----------------------------------------------------

def test_map_to_dict():
    m = Map(center=(-0.1, 51.5), zoom=10, markers=[(-0.1, 51.5)])
    d = m.to_dict()
    assert d["center"] == [-0.1, 51.5]
    assert d["markers"] == [[-0.1, 51.5]]


def test_app_openlayers_injects_classic_script_and_css():
    r = TestClient(_make_app(openlayers=True)).get("/")
    assert OL_JS_CDN in r.text
    assert "ol.css" in r.text
    imports = _importmap_imports(r.text)
    assert "ol" not in imports


# ---- Webcam -------------------------------------------------------------

def test_webcam_control_attrs():
    cam = Webcam(camera_id="my-cam")
    assert "my-cam" in cam.snap_attr()
    assert "snap" in cam.snap_attr()
    assert "flip" in cam.flip_attr()


def test_app_webcam_injects_importmap():
    r = TestClient(_make_app(webcam=True)).get("/")
    imports = _importmap_imports(r.text)
    assert imports["webcam-easy"] == WEBCAM_CDN


# ---- Google Translate (pure Python, no client adapter) ------------------

def test_translate_parses_realistic_response(monkeypatch):
    import urllib.request

    mock_payload = {
        "sentences": [{"trans": "Hola, ", "orig": "Hello, "}, {"trans": "como estas?", "orig": "how are you?"}],
        "src": "en",
    }

    class FakeResp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return json.dumps(mock_payload).encode()

    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: FakeResp())
    result = translate("Hello, how are you?", to="es")
    assert isinstance(result, Translation)
    assert result.text == "Hola, como estas?"
    assert result.source_language == "en"


def test_translate_raises_runtime_error_on_http_failure(monkeypatch):
    import urllib.request, urllib.error

    def raise_http_error(*a, **k):
        raise urllib.error.HTTPError("url", 403, "Forbidden", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", raise_http_error)
    import pytest
    with pytest.raises(RuntimeError):
        translate("hi", to="es")


# ---- everything together ------------------------------------------------

def test_all_new_integrations_together_single_importmap():
    app = _make_app(
        threejs=True, gsap=True, chartjs=True, aggrid=True, spline=True, vroid=True,
        babylonjs=True, shiki=True, barcode=True, webcam=True,
        iconify=True, qrcode=True, openlayers=True, videojs=True, tailwind=True,
    )
    r = TestClient(app).get("/")
    assert r.status_code == 200
    assert r.text.count('type="importmap"') == 1
    imports = _importmap_imports(r.text)
    expected = {
        "three", "three/", "gsap", "chart.js", "@kurkle/color",
        "ag-grid-community", "ag-stack", "@splinetool/runtime", "@pixiv/three-vrm",
        "@babylonjs/core", "shiki", "bwip-js", "webcam-easy",
    }
    assert set(imports.keys()) == expected


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
