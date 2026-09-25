"""
Nexoria example: Chart.js + video.js, both declared in pure Python.
Chart.js renders into a <canvas>; video.js wraps a real <video> element,
customized with a theme matching the app's own dark theme, a trimmed
control bar, and a demo plugin. Both load from CDN as needed -- neither
is a Python dependency.
"""

from nexoria import App, Component, el, Router
from nexoria.chartjs import Chart, Dataset
from nexoria.videojs import VideoPlayer, VideoTheme, ControlBar, VideoPlugin
from nexoria.style import DEFAULT_THEME


class Dashboard(Component):
    def render(self):
        chart = Chart(
            type="bar",
            labels=["Jan", "Feb", "Mar", "Apr"],
            datasets=[
                Dataset("Revenue", [12, 19, 14, 22], backgroundColor="#6366f1"),
                Dataset("Costs", [8, 11, 9, 13], backgroundColor="#22d3ee"),
            ],
            options={"responsive": True, "plugins": {"legend": {"position": "bottom"}}},
        )
        video = VideoPlayer(
            "https://vjs.zencdn.net/v/oceans.mp4",
            poster="https://vjs.zencdn.net/v/oceans.png",
            controls=True,
            # Customization: re-skin to match the app's own dark theme,
            # and show only a minimal control bar.
            theme=VideoTheme.from_theme(DEFAULT_THEME),
            control_bar=ControlBar(children=[
                "playToggle", "progressControl", "volumePanel", "fullscreenToggle",
            ]),
        )

        return el("div",
            el("nav", el("span", "\u2b21 Nexoria", class_="nx-brand"), class_="nx-nav"),
            el("div",
                el("h1", "Quarterly Report"),
                el("div", chart.to_element(), style={"margin_bottom": "32px"}),
                el("h2", "Product Demo"),
                video.to_element(),
                video.theme_element(),
                class_="nx-card",
            ),
            class_="nx-container",
        )


router = Router()
router.add("/", Dashboard)

app = App(name="Nexoria Dashboard Demo", router=router, chartjs=True, videojs=True, debug=True)

if __name__ == "__main__":
    app.run(reload=True)
