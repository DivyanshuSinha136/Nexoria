/**
 * Nexoria AG Grid adapter (optional, loaded only when App(aggrid=True)
 * is set). Reads the declarative grid config produced by
 * `nexoria.aggrid.grid.Grid.to_dict()` from each grid container's
 * `data-nx-aggrid` attribute and instantiates a real AG Grid via the
 * modern `createGrid(el, gridOptions)` API.
 *
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
import { createGrid } from "ag-grid-community";

const grids = {};

function mountGrid(el) {
  if (el.dataset.nxMounted === "1") return;

  let gridOptions;
  try {
    gridOptions = JSON.parse(el.getAttribute("data-nx-aggrid"));
  } catch (e) {
    console.error("Nexoria AG Grid: invalid grid spec (bad JSON)", e);
    return;
  }

  let api;
  try {
    api = createGrid(el, gridOptions);
  } catch (e) {
    console.error("Nexoria AG Grid: failed to create grid", e);
    return;
  }

  el.dataset.nxMounted = "1";
  if (!el.id) el.id = `nx-aggrid-${Object.keys(grids).length}-${Date.now()}`;
  grids[el.id] = api;
  el.dispatchEvent(new CustomEvent("nexoria:aggrid:ready", { bubbles: true, detail: { api } }));
}

document.querySelectorAll(".nx-aggrid-grid").forEach(mountGrid);

window.__nexoria__ = window.__nexoria__ || {};
window.__nexoria__.aggrid = {
  grids,
  get: (id) => grids[id],
  setRowData: (id, rows) => grids[id] && grids[id].setGridOption("rowData", rows),
  mountNew: () => document.querySelectorAll(".nx-aggrid-grid").forEach(mountGrid),
};
