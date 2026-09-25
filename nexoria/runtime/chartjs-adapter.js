/**
 * Nexoria Chart.js adapter (optional, loaded only when App(chartjs=True)
 * is set). Reads the declarative chart config produced by
 * `nexoria.chartjs.chart.Chart.to_dict()` from each canvas's
 * `data-nx-chart` attribute and instantiates a real Chart.js chart.
 *
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

const charts = [];

function mountChart(canvas) {
  let spec;
  try {
    spec = JSON.parse(canvas.getAttribute("data-nx-chart"));
  } catch (e) {
    console.error("Nexoria Chart.js: invalid chart spec", e);
    return;
  }
  const chart = new Chart(canvas, {
    type: spec.type,
    data: spec.data,
    options: spec.options || {},
  });
  charts.push(chart);
}

document.querySelectorAll(".nx-chartjs-canvas").forEach(mountChart);

window.__nexoria__ = window.__nexoria__ || {};
window.__nexoria__.chartjs = { charts };
