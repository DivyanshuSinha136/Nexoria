/**
 * Nexoria Babylon.js adapter (optional, App(babylonjs=True)).
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
import * as BABYLON from "@babylonjs/core";

const MESH_BUILDERS = {
  box: (name, size, scene) => BABYLON.MeshBuilder.CreateBox(name, { size }, scene),
  sphere: (name, size, scene) => BABYLON.MeshBuilder.CreateSphere(name, { diameter: size }, scene),
  ground: (name, size, scene) => BABYLON.MeshBuilder.CreateGround(name, { width: size, height: size }, scene),
  cylinder: (name, size, scene) => BABYLON.MeshBuilder.CreateCylinder(name, { height: size, diameter: size * 0.6 }, scene),
  torus: (name, size, scene) => BABYLON.MeshBuilder.CreateTorus(name, { diameter: size, thickness: size * 0.3 }, scene),
};

function mountScene(canvas) {
  if (canvas.dataset.nxMounted === "1") return;
  canvas.dataset.nxMounted = "1";

  let spec;
  try {
    spec = JSON.parse(canvas.getAttribute("data-nx-babylon"));
  } catch (e) {
    console.error("Nexoria Babylon.js: invalid scene spec (bad JSON)", e);
    return;
  }

  const engine = new BABYLON.Engine(canvas, true);
  const scene = new BABYLON.Scene(engine);
  scene.clearColor = BABYLON.Color4.FromHexString(spec.background + "ff");

  const cam = spec.camera || {};
  const camera = new BABYLON.ArcRotateCamera(
    "camera", cam.alpha ?? -1.57, cam.beta ?? 1.2, cam.radius ?? 6, BABYLON.Vector3.Zero(), scene
  );
  camera.attachControl(canvas, true);
  new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0, 1, 0), scene);

  const meshes = (spec.meshes || []).map((m, i) => {
    const builder = MESH_BUILDERS[m.type] || MESH_BUILDERS.box;
    const mesh = builder(`mesh-${i}`, m.size || 1, scene);
    mesh.position = new BABYLON.Vector3(...(m.position || [0, 0, 0]));
    mesh.rotation = new BABYLON.Vector3(...(m.rotation || [0, 0, 0]));
    const mat = new BABYLON.StandardMaterial(`mat-${i}`, scene);
    mat.diffuseColor = BABYLON.Color3.FromHexString(m.color || "#4477ff");
    mesh.material = mat;
    mesh.userData = { animate: m.animate };
    return mesh;
  });

  scene.registerBeforeRender(() => {
    for (const mesh of meshes) {
      if (mesh.userData.animate === "rotate_y") mesh.rotation.y += 0.01;
      if (mesh.userData.animate === "rotate_x") mesh.rotation.x += 0.01;
    }
  });

  engine.runRenderLoop(() => scene.render());
  window.addEventListener("resize", () => engine.resize());

  window.__nexoria__ = window.__nexoria__ || {};
  window.__nexoria__.babylon = window.__nexoria__.babylon || { scenes: {} };
  window.__nexoria__.babylon.scenes[canvas.id || `nx-babylon-${Object.keys(window.__nexoria__.babylon.scenes).length}`] = { engine, scene, camera };
  canvas.dispatchEvent(new CustomEvent("nexoria:babylon:ready", { bubbles: true, detail: { engine, scene } }));
}

document.querySelectorAll(".nx-babylon-scene").forEach(mountScene);

window.__nexoria__ = window.__nexoria__ || {};
window.__nexoria__.babylon = window.__nexoria__.babylon || { scenes: {} };
window.__nexoria__.babylon.mountNew = () => document.querySelectorAll(".nx-babylon-scene").forEach(mountScene);
