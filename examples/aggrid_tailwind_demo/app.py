"""
Nexoria example: AG Grid + Tailwind CSS, both declared in pure Python.
AG Grid renders real, sortable/filterable tabular data; Tailwind is
used here via the Play CDN for quick styling of the surrounding page
(prototyping-only per Tailwind's own guidance -- see the Tailwind CSS
section of the README for the production build path).
"""

from nexoria import App, Component, el, Router
from nexoria.aggrid import Grid, Column
from nexoria.tailwind import TailwindConfig

ROWS = [
    {"company": "Acme Corp", "revenue": 128000, "growth": "+12%"},
    {"company": "Globex", "revenue": 95000, "growth": "+4%"},
    {"company": "Initech", "revenue": 210000, "growth": "-2%"},
    {"company": "Umbrella", "revenue": 67000, "growth": "+31%"},
]


class Dashboard(Component):
    def render(self):
        grid = Grid(
            columns=[
                Column("company", header_name="Company", sortable=True, filter=True),
                Column("revenue", header_name="Revenue ($)", sortable=True),
                Column("growth", header_name="Growth"),
            ],
            row_data=ROWS,
            theme="quartz",
            height="300px",
        )

        return el("div",
            el("div",
                el("nav",
                    el("span", "\u2b21 Nexoria", **{"class": "font-bold text-lg"}),
                    **{"class": "flex items-center justify-between border-b border-slate-800 pb-4 mb-6"},
                ),
                el("h1", "Company Revenue", **{"class": "text-2xl font-bold mb-1"}),
                el("p", "AG Grid rendering real tabular data, styled with Tailwind.",
                   **{"class": "text-slate-400 mb-6"}),
                el("div", grid.to_element(),
                   **{"class": "rounded-xl overflow-hidden border border-slate-800"}),
                **{"class": "max-w-3xl mx-auto p-8"},
            ),
            **{"class": "min-h-screen bg-slate-950 text-slate-100"},
        )


router = Router()
router.add("/", Dashboard)

app = App(
    name="Nexoria AG Grid + Tailwind Demo",
    router=router,
    aggrid=True,
    tailwind=True,
    tailwind_config=TailwindConfig(dark_mode="class"),
    debug=True,
)

if __name__ == "__main__":
    app.run(reload=True)
