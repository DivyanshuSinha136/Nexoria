/**
 * Nexoria Bootstrap adapter (optional, loaded only when App(bootstrap=True)).
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 *
 * Most of Bootstrap activates itself from markup alone -- collapses,
 * dropdowns, modals, offcanvases, alerts and carousels all wire
 * themselves up from their `data-bs-*` attributes the moment
 * bootstrap.bundle.min.js (loaded before this file, see
 * nexoria.bootstrap.config.BOOTSTRAP_CORE_SCRIPT_TAG) is on the page --
 * nothing here needed for any of those.
 *
 * Two things this file does handle:
 *
 *  1. Tooltips and popovers are the exception: per Bootstrap's own
 *     docs they require an explicit `new bootstrap.Tooltip(el)` /
 *     `new bootstrap.Popover(el)` call, so this finds every
 *     [data-bs-toggle="tooltip"] / [data-bs-toggle="popover"] element
 *     and initializes it (skipping any already initialized, so it's
 *     always safe to call again).
 *  2. Bootstrap's color mode (`data-bs-theme` on <html>) is kept in
 *     sync with Nexoria's own dark/light toggle (`data-nx-theme`, see
 *     nexoria.style.theme_toggle_button) via a MutationObserver, so
 *     one theme toggle drives both -- a Bootstrap-styled page never
 *     needs a second one.
 */

function initComponents(root) {
  const scope = root || document;
  scope.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
    if (!bootstrap.Tooltip.getInstance(el)) new bootstrap.Tooltip(el);
  });
  scope.querySelectorAll('[data-bs-toggle="popover"]').forEach((el) => {
    if (!bootstrap.Popover.getInstance(el)) new bootstrap.Popover(el);
  });
}

function syncTheme() {
  const light = document.documentElement.getAttribute("data-nx-theme") === "light";
  document.documentElement.setAttribute("data-bs-theme", light ? "light" : "dark");
}

syncTheme();
initComponents();

new MutationObserver(syncTheme).observe(document.documentElement, {
  attributes: true,
  attributeFilter: ["data-nx-theme"],
});

window.__nexoria__ = window.__nexoria__ || {};
window.__nexoria__.bootstrap = {
  // Call after inserting new DOM (e.g. from a server round-trip) that
  // may contain fresh [data-bs-toggle="tooltip"/"popover"] elements --
  // same convention as nexoria.barcode/qrcode/shiki's own `mountNew`.
  mountNew: (root) => initComponents(root),
};
