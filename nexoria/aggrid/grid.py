"""
nexoria.aggrid.grid
======================
Optional data-grid layer. Describe an AG Grid (Community edition, MIT)
grid declaratively in Python; the client adapter
(`runtime/aggrid-adapter.js`, loaded only when `App(aggrid=True)` is
set) instantiates a real grid via AG Grid's modern `createGrid(el,
gridOptions)` API. AG Grid itself is pulled from CDN as an ES module
-- never a Python dependency.

Verified dependency chain: `ag-grid-community`'s ESM entry has exactly
one genuine external import, `ag-stack` (its own internal utility
package) -- everything else that superficially looks like an import in
that file is either a string literal (used for optional enterprise-
feature error messages) or a relative import within the same package.
Both are included in the import map.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import json

AGGRID_VERSION = "36.1.0"
AGGRID_CDN = f"https://unpkg.com/ag-grid-community@{AGGRID_VERSION}/dist/package/main.esm.mjs"
AG_STACK_CDN = f"https://unpkg.com/ag-stack@{AGGRID_VERSION}/dist/package/main.esm.mjs"
AGGRID_IMPORTS = {"ag-grid-community": AGGRID_CDN, "ag-stack": AG_STACK_CDN}
AGGRID_ADAPTER_TAG = '<script src="/_nexoria/aggrid-adapter.js" type="module" defer></script>'

_THEME_CSS_BASE = f"https://unpkg.com/ag-grid-community@{AGGRID_VERSION}/styles"
AGGRID_THEMES = {
    "quartz": f"{_THEME_CSS_BASE}/ag-theme-quartz.min.css",
    "alpine": f"{_THEME_CSS_BASE}/ag-theme-alpine.min.css",
    "balham": f"{_THEME_CSS_BASE}/ag-theme-balham.min.css",
    "material": f"{_THEME_CSS_BASE}/ag-theme-material.min.css",
}


@dataclass
class Column:
    """
    One AG Grid column definition. `field` is the row-data key; extra
    keyword args become AG Grid `colDef` options verbatim
    (`sortable`, `filter`, `width`, `valueFormatter` name strings,
    `pinned`, ...).

        Column("revenue", header_name="Revenue", sortable=True, filter="agNumberColumnFilter")
    """
    field: str
    header_name: Optional[str] = None
    extra: dict[str, Any] = field(default_factory=dict)

    def __init__(self, field: str, header_name: Optional[str] = None, **extra: Any):
        self.field = field
        self.header_name = header_name
        self.extra = extra

    def to_dict(self) -> dict:
        d = {"field": self.field, **self.extra}
        if self.header_name is not None:
            d["headerName"] = self.header_name
        return d


@dataclass
class Grid:
    """
    An AG Grid data grid.

        Grid(
            columns=[Column("name", header_name="Name"), Column("revenue", sortable=True)],
            row_data=[{"name": "Acme", "revenue": 1200}, {"name": "Globex", "revenue": 950}],
            theme="quartz",
        )

    `options` is passed through to `gridOptions` verbatim (merged in
    after every field above) for anything not covered directly --
    pagination, row selection, grouping, cell renderers by registered
    name, etc.
    """
    columns: list[Column]
    row_data: list[dict[str, Any]] = field(default_factory=list)
    theme: str = "quartz"  # "quartz" | "alpine" | "balham" | "material" | None (no bundled theme CSS)
    width: str = "100%"
    height: str = "480px"
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        merged = dict(self.options)
        merged["columnDefs"] = [c.to_dict() for c in self.columns]
        merged["rowData"] = self.row_data
        return merged

    def to_element(self):
        from ..core.element import el
        theme_class = f"ag-theme-{self.theme}" if self.theme else ""
        return el(
            "div",
            **{
                "class": f"nx-aggrid-grid {theme_class}".strip(),
                "data-nx-aggrid": json.dumps(self.to_dict()),
                "style": f"width:{self.width};height:{self.height};",
            },
        )
