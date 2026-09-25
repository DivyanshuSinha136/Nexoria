/**
 * Nexoria barcode adapter (optional, App(barcode=True)).
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
import bwipjs from "bwip-js";

function mount(canvas) {
  if (canvas.dataset.nxMounted === "1") return;
  canvas.dataset.nxMounted = "1";

  let spec;
  try {
    spec = JSON.parse(canvas.getAttribute("data-nx-barcode"));
  } catch (e) {
    console.error("Nexoria barcode: invalid spec (bad JSON)", e);
    return;
  }

  try {
    bwipjs.toCanvas(canvas, spec);
  } catch (e) {
    console.error(`Nexoria barcode: failed to render "${spec.bcid}" barcode`, e);
  }
}

document.querySelectorAll(".nx-barcode").forEach(mount);

window.__nexoria__ = window.__nexoria__ || {};
window.__nexoria__.barcode = { mountNew: () => document.querySelectorAll(".nx-barcode").forEach(mount) };
