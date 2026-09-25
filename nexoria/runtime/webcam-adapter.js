/**
 * Nexoria webcam adapter (optional, App(webcam=True)).
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
import Webcam from "webcam-easy";

const instances = {};

function mount(videoEl) {
  if (videoEl.dataset.nxMounted === "1") return;
  videoEl.dataset.nxMounted = "1";

  let spec;
  try {
    spec = JSON.parse(videoEl.getAttribute("data-nx-webcam"));
  } catch (e) {
    console.error("Nexoria webcam: invalid spec (bad JSON)", e);
    return;
  }

  const webcam = new Webcam(videoEl, spec.facingMode || "user");
  webcam.lastSnapshot = null;
  instances[videoEl.id] = webcam;

  if (spec.autostart !== false) {
    webcam.start().catch((e) => {
      console.error("Nexoria webcam: failed to start camera (permission denied, or no camera available)", e);
    });
  }
}

document.querySelectorAll(".nx-webcam-video").forEach(mount);

window.__nexoria__ = window.__nexoria__ || {};
window.__nexoria__.webcam = {
  instances,
  get: (id) => instances[id],
  start: (id) => instances[id] && instances[id].start().catch((e) => console.error("Nexoria webcam:", e)),
  stop: (id) => instances[id] && instances[id].stop(),
  flip: (id) => instances[id] && (instances[id].facingMode = instances[id].facingMode === "user" ? "environment" : "user") && instances[id].start(),
  snap: (id) => {
    const webcam = instances[id];
    if (!webcam) return null;
    const dataUrl = webcam.snap();
    webcam.lastSnapshot = dataUrl;
    document.getElementById(id).dispatchEvent(
      new CustomEvent("nexoria:webcam:snap", { bubbles: true, detail: { dataUrl } })
    );
    return dataUrl;
  },
  mountNew: () => document.querySelectorAll(".nx-webcam-video").forEach(mount),
};
