/**
 * Nexoria Shiki adapter (optional, App(shiki=True)).
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
import { codeToHtml } from "shiki";

async function mount(container) {
  if (container.dataset.nxMounted === "1") return;
  container.dataset.nxMounted = "1";

  let spec;
  try {
    spec = JSON.parse(container.getAttribute("data-nx-shiki"));
  } catch (e) {
    console.error("Nexoria Shiki: invalid spec (bad JSON)", e);
    return;
  }

  try {
    const html = await codeToHtml(spec.code, { lang: spec.lang, theme: spec.theme });
    container.innerHTML = html;
  } catch (e) {
    console.error(`Nexoria Shiki: failed to highlight (lang="${spec.lang}")`, e);
    // leave the original <pre><code> in place -- readable plain text fallback
  }
}

document.querySelectorAll(".nx-shiki-block").forEach(mount);

window.__nexoria__ = window.__nexoria__ || {};
window.__nexoria__.shiki = { mountNew: () => document.querySelectorAll(".nx-shiki-block").forEach(mount) };
