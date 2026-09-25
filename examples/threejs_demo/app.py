"""
Nexoria example: optional ThreeJS integration. Declare a 3D scene in
pure Python; the client adapter (three-adapter.js) instantiates real
THREE.js objects from the JSON scene graph. Styled with the framework's
default dark theme -- the 3D canvas sits inside an nx-card just like
any other content.
"""

from nexoria import App, Component, el, Router, Stylesheet
from nexoria.threejs import Scene, Mesh, Light, Camera


class SpinningCube(Component):
    styles = Stylesheet()

    def render(self):
        scene = Scene(
            camera=Camera(position=(0, 1, 4)),
            lights=[Light(kind="ambient", intensity=0.6),
                    Light(kind="directional", position=(3, 5, 2))],
            background="#14141f",
        )
        scene.add(Mesh(geometry="box", color="#6366f1", animate="rotate_y"))

        stage = self.styles.scoped_class(
            "stage",
            border_radius="var(--nx-radius)",
            overflow="hidden",
            border="1px solid var(--nx-border)",
        )

        return el("div",
            el("nav",
                el("span", "\u2b21 Nexoria", class_="nx-brand"),
                el("span", "ThreeJS Demo", class_="nx-badge"),
                class_="nx-nav",
            ),
            el("div",
                el("span", "Optional 3D \u00b7 THREE.js", class_="nx-badge"),
                el("h1", "Nexoria + ThreeJS"),
                el("p", "A declarative Python Scene compiles to a real "
                        "THREE.js render, mounted client-side.",
                   style={"color": "var(--nx-text-muted)", "margin_bottom": "20px"}),
                el("div", scene.to_element(), class_=stage),
                class_="nx-card",
            ),
            class_="nx-container",
        )


router = Router()
router.add("/", SpinningCube)

app = App(name="Nexoria ThreeJS Demo", router=router, threejs=True, debug=True)

if __name__ == "__main__":
    app.run(reload=True)
