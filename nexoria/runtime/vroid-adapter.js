/**
 * Nexoria VRM/VRoid adapter (optional, loaded only when App(vroid=True)
 * is set). Reads the declarative avatar spec produced by
 * `nexoria.vroid.avatar.VRMAvatar.to_dict()` from each container's
 * `data-nx-vroid` attribute and renders it with a real Three.js scene
 * + the official `@pixiv/three-vrm` loader plugin.
 *
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { VRMLoaderPlugin, VRMUtils } from "@pixiv/three-vrm";

const avatars = {};

async function mountAvatar(container) {
  if (container.dataset.nxMounted === "1") return;
  container.dataset.nxMounted = "1";

  let spec;
  try {
    spec = JSON.parse(container.getAttribute("data-nx-vroid"));
  } catch (e) {
    console.error("Nexoria VRM: invalid avatar spec (bad JSON)", e);
    return;
  }
  if (!spec.url) {
    console.error("Nexoria VRM: no avatar url given for", container);
    return;
  }

  const width = container.clientWidth || 480;
  const height = container.clientHeight || 480;

  const scene = new THREE.Scene();
  if (spec.background) scene.background = new THREE.Color(spec.background);

  const camera = new THREE.PerspectiveCamera(30, width / height, 0.1, 20);
  camera.position.set(...spec.cameraPosition);
  camera.lookAt(...spec.lookAt);

  scene.add(new THREE.AmbientLight(0xffffff, 1.2));
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
  dirLight.position.set(1, 1, 1).normalize();
  scene.add(dirLight);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  container.innerHTML = "";
  container.appendChild(renderer.domElement);

  const loader = new GLTFLoader();
  loader.register((parser) => new VRMLoaderPlugin(parser));

  let vrm = null;
  try {
    const gltf = await loader.loadAsync(spec.url);
    vrm = gltf.userData.vrm;
    VRMUtils.removeUnnecessaryVertices(gltf.scene);
    VRMUtils.combineSkeletons(gltf.scene);
    VRMUtils.rotateVRM0(vrm); // VRM0-format models face +Z; rotate to face the camera like VRM1
    scene.add(vrm.scene);
  } catch (e) {
    console.error(`Nexoria VRM: failed to load avatar "${spec.url}"`, e);
    return;
  }

  const clock = new THREE.Clock();
  let disposed = false;
  function animate() {
    if (disposed) return;
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    if (vrm) {
      vrm.update(delta); // drives spring-bone physics + look-at each frame
      if (spec.autoRotate) vrm.scene.rotation.y += delta * 0.5;
    }
    renderer.render(scene, camera);
  }
  animate();

  function onResize() {
    const w = container.clientWidth, h = container.clientHeight;
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  window.addEventListener("resize", onResize);

  avatars[container.id] = {
    scene, camera, renderer, vrm,
    dispose: () => { disposed = true; window.removeEventListener("resize", onResize); renderer.dispose(); },
  };
  container.dispatchEvent(new CustomEvent("nexoria:vroid:ready", { bubbles: true, detail: avatars[container.id] }));
}

document.querySelectorAll(".nx-vroid-avatar").forEach(mountAvatar);

window.__nexoria__ = window.__nexoria__ || {};
window.__nexoria__.vroid = {
  avatars,
  get: (id) => avatars[id],
  mountNew: () => document.querySelectorAll(".nx-vroid-avatar").forEach(mountAvatar),
};
