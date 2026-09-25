/**
 * Nexoria Spline adapter (optional, loaded only when App(spline=True)
 * is set). Reads the declarative scene reference produced by
 * `nexoria.spline.scene.SplineScene.to_dict()` from each canvas's
 * `data-nx-spline` attribute and loads it via Spline's own runtime.
 *
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
import { Application } from "@splinetool/runtime";

const apps = {};

async function mountScene(canvas) {
  if (canvas.dataset.nxMounted === "1") return;
  canvas.dataset.nxMounted = "1";

  let spec;
  try {
    spec = JSON.parse(canvas.getAttribute("data-nx-spline"));
  } catch (e) {
    console.error("Nexoria Spline: invalid scene spec (bad JSON)", e);
    return;
  }
  if (!spec.url) {
    console.error("Nexoria Spline: no scene url given for", canvas);
    return;
  }

  if (spec.background) {
    canvas.style.background = spec.background;
  }

  const app = new Application(canvas);
  try {
    await app.load(spec.url);
  } catch (e) {
    console.error(`Nexoria Spline: failed to load scene "${spec.url}"`, e);
    return;
  }

  apps[canvas.id] = app;
  canvas.dispatchEvent(new CustomEvent("nexoria:spline:ready", { bubbles: true, detail: { app } }));
}

document.querySelectorAll(".nx-spline-canvas").forEach(mountScene);

window.__nexoria__ = window.__nexoria__ || {};
window.__nexoria__.spline = {
  apps,
  get: (id) => apps[id],
  mountNew: () => document.querySelectorAll(".nx-spline-canvas").forEach(mountScene),
};
