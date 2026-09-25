/**
 * Nexoria OpenLayers adapter (optional, App(openlayers=True)).
 * Classic script -- relies on the global `ol` from OpenLayers' own
 * pre-bundled dist/ol.js, loaded just before this file.
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
(function () {
  "use strict";

  const maps = {};

  function buildTileLayer(tileSource) {
    if (tileSource === "osm" || !tileSource) {
      return new ol.layer.Tile({ source: new ol.source.OSM() });
    }
    return new ol.layer.Tile({
      source: new ol.source.XYZ({ url: tileSource.url, attributions: tileSource.attributions || "" }),
    });
  }

  function addMarkers(map, markers) {
    if (!markers || !markers.length) return;
    const features = markers.map(([lon, lat]) => new ol.Feature({
      geometry: new ol.geom.Point(ol.proj.fromLonLat([lon, lat])),
    }));
    const source = new ol.source.Vector({ features });
    const layer = new ol.layer.Vector({
      source,
      style: new ol.style.Style({
        image: new ol.style.Circle({
          radius: 7,
          fill: new ol.style.Fill({ color: "#6366f1" }),
          stroke: new ol.style.Stroke({ color: "#fff", width: 2 }),
        }),
      }),
    });
    map.addLayer(layer);
  }

  function mount(container) {
    if (container.dataset.nxMounted === "1") return;
    container.dataset.nxMounted = "1";

    let spec;
    try {
      spec = JSON.parse(container.getAttribute("data-nx-ol"));
    } catch (e) {
      console.error("Nexoria OpenLayers: invalid map spec (bad JSON)", e);
      return;
    }
    if (typeof ol === "undefined") {
      console.error("Nexoria OpenLayers: the `ol` global wasn't found -- check its <script> tag loaded first.");
      return;
    }

    const map = new ol.Map({
      target: container,
      layers: [buildTileLayer(spec.tileSource)],
      view: new ol.View({ center: ol.proj.fromLonLat(spec.center || [0, 0]), zoom: spec.zoom ?? 2 }),
    });
    addMarkers(map, spec.markers);

    maps[container.id] = map;
    container.dispatchEvent(new CustomEvent("nexoria:openlayers:ready", { bubbles: true, detail: { map } }));
  }

  document.querySelectorAll(".nx-ol-map").forEach(mount);

  window.__nexoria__ = window.__nexoria__ || {};
  window.__nexoria__.openlayers = {
    maps,
    get: (id) => maps[id],
    mountNew: () => document.querySelectorAll(".nx-ol-map").forEach(mount),
  };
})();
