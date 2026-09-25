# `nexoria.aggrid`

> Declare an AG Grid (Community, MIT) data grid in Python.

| | |
|---|---|
| **Import** | `from nexoria.aggrid import Grid, Column` |
| **Enabled by** | `App(aggrid=True)` |
| **Library** | `ag-grid-community` 36.1.0 and its internal `ag-stack` from unpkg (import map) |
| **Adapter** | `runtime/aggrid-adapter.js` — uses `createGrid()`; exposes `window.__nexoria__.aggrid.{grids,get,setRowData,mountNew}` |

```python
from nexoria.aggrid import Grid, Column

grid = Grid(
    columns=[Column("name", header_name="Name"), Column("revenue", sortable=True, filter="agNumberColumnFilter")],
    row_data=[{"name": "Acme", "revenue": 1200}, {"name": "Globex", "revenue": 950}],
    theme="quartz",
    options={"pagination": True},          # merged into gridOptions
)
el("div", grid.to_element())
```

`Column(field, header_name=None, **extra)` — extras become `colDef` options. `Grid.options` is merged into `gridOptions`; `columnDefs`/`rowData` from the fields above take precedence.

**Theme CSS caveat.** `Grid(theme=…)` adds the class `ag-theme-<theme>`, but `App` only links the **quartz** theme stylesheet when `aggrid=True`. For `alpine`, `balham` or `material`, add the matching CSS link yourself (URLs are in `AGGRID_THEMES`).

## API reference

### Classes

#### `class Grid(columns: list[Column], row_data: list[dict[str, Any]] = ..., theme: str = 'quartz', width: str = '100%', height: str = '480px', options: dict[str, Any] = ...) -> None`

An AG Grid data grid.

`options` is passed through to `gridOptions` verbatim (merged in after every field above) for anything not covered directly -- pagination, row selection, grouping, cell renderers by registered name, etc.

- **`.to_dict() -> dict`**
- **`.to_element()`**

#### `class Column(field: str, header_name: Optional[str] = None, **extra: Any)`

One AG Grid column definition. `field` is the row-data key; extra keyword args become AG Grid `colDef` options verbatim (`sortable`, `filter`, `width`, `valueFormatter` name strings, `pinned`, ...).

- **`.to_dict() -> dict`**

### Constants

| Name | Value |
|---|---|
| `AGGRID_IMPORTS` | `{'ag-grid-community': 'https://unpkg.com/ag-grid-community@36.1.0/dist/package/main.esm.mjs', 'ag-stack': 'https://unpkg.com/ag-stack@36.1.0/dist/package/main.esm.mjs'}` |
| `AGGRID_ADAPTER_TAG` | `'<script src="/_nexoria/aggrid-adapter.js" type="module" defer></script>'` |
| `AGGRID_THEMES` | `{'quartz': 'https://unpkg.com/ag-grid-community@36.1.0/styles/ag-theme-quartz.min.css', 'alpine': 'https://unpkg.com/ag-grid-community@36.1.0/styles/ag-theme-alpine.min.css', 'balham': 'https://unpkg.com/ag-grid-community@36.1.0/styles/ag-theme-balham.min.css', 'material': 'https://unpkg.com/ag-grid-community@36.1.0/styles/ag-theme-material.min.css'}` |
| `AGGRID_CDN` | `'https://unpkg.com/ag-grid-community@36.1.0/dist/package/main.esm.mjs'` |
