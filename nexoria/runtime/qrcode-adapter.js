/**
 * Nexoria QR code adapter (optional, App(qrcode=True)).
 * Classic script -- relies on the global `QRCodeStyling` from
 * qr-code-styling's own UMD bundle, loaded just before this file.
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
(function () {
  "use strict";

  function mount(el) {
    if (el.dataset.nxMounted === "1") return;
    el.dataset.nxMounted = "1";

    let spec;
    try {
      spec = JSON.parse(el.getAttribute("data-nx-qrcode"));
    } catch (e) {
      console.error("Nexoria QR code: invalid spec (bad JSON)", e);
      return;
    }
    if (typeof QRCodeStyling !== "function") {
      console.error("Nexoria QR code: the `QRCodeStyling` global wasn't found -- check its <script> tag loaded first.");
      return;
    }

    const qr = new QRCodeStyling(spec);
    el.innerHTML = "";
    qr.append(el);

    window.__nexoria__ = window.__nexoria__ || {};
    window.__nexoria__.qrcode = window.__nexoria__.qrcode || { instances: {} };
    if (!el.id) el.id = `nx-qrcode-${Object.keys(window.__nexoria__.qrcode.instances).length}`;
    window.__nexoria__.qrcode.instances[el.id] = qr;
  }

  document.querySelectorAll(".nx-qrcode").forEach(mount);

  window.__nexoria__ = window.__nexoria__ || {};
  window.__nexoria__.qrcode = window.__nexoria__.qrcode || { instances: {} };
  window.__nexoria__.qrcode.mountNew = () => document.querySelectorAll(".nx-qrcode").forEach(mount);
})();
