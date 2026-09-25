/**
 * Nexoria ThreeJS adapter (optional, loaded only when App(threejs=True)
 * or a Scene() is used). Reads the declarative scene graph produced by
 * `nexoria.threejs.scene.Scene.to_dict()` from each element's
 * `data-nx-scene` attribute and instantiates real THREE.js objects.
 *
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
import * as THREE from "three";

const GEOMETRY_FACTORY = {
  box: () => new THREE.BoxGeometry(1, 1, 1),
  sphere: () => new THREE.SphereGeometry(0.75, 32, 32),
  plane: () => new THREE.PlaneGeometry(2, 2),
  torus: () => new THREE.TorusGeometry(0.7, 0.25, 16, 64),
};

const MATERIAL_FACTORY = {
  standard: (color) => new THREE.MeshStandardMaterial({ color }),
  basic: (color) => new THREE.MeshBasicMaterial({ color }),
  phong: (color) => new THREE.MeshPhongMaterial({ color }),
};

function buildLight(spec) {
  let light;
  if (spec.kind === "ambient") light = new THREE.AmbientLight(spec.color, spec.intensity);
  else if (spec.kind === "point") light = new THREE.PointLight(spec.color, spec.intensity);
  else light = new THREE.DirectionalLight(spec.color, spec.intensity);
  if (spec.position) light.position.set(...spec.position);
  return light;
}

function buildMesh(spec) {
  const geomFn = GEOMETRY_FACTORY[spec.geometry] || GEOMETRY_FACTORY.box;
  const matFn = MATERIAL_FACTORY[spec.material] || MATERIAL_FACTORY.standard;
  const mesh = new THREE.Mesh(geomFn(), matFn(spec.color));
  mesh.position.set(...spec.position);
  mesh.rotation.set(...spec.rotation);
  mesh.scale.set(...spec.scale);
  mesh.userData.animate = spec.animate;
  return mesh;
}

function mountScene(container) {
  const spec = JSON.parse(container.getAttribute("data-nx-scene"));
  const width = container.clientWidth || 640;
  const height = container.clientHeight || 480;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(spec.background);

  const cam = spec.camera;
  const camera = cam.kind === "orthographic"
    ? new THREE.OrthographicCamera(-width / 100, width / 100, height / 100, -height / 100, 0.1, 1000)
    : new THREE.PerspectiveCamera(cam.fov, width / height, 0.1, 1000);
  camera.position.set(...cam.position);
  camera.lookAt(...cam.lookAt);

  spec.lights.forEach((l) => scene.add(buildLight(l)));
  const meshes = spec.meshes.map(buildMesh);
  meshes.forEach((m) => scene.add(m));

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.innerHTML = "";
  container.appendChild(renderer.domElement);

  function animate() {
    requestAnimationFrame(animate);
    for (const mesh of meshes) {
      if (mesh.userData.animate === "rotate_y") mesh.rotation.y += 0.01;
      if (mesh.userData.animate === "rotate_x") mesh.rotation.x += 0.01;
    }
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", () => {
    const w = container.clientWidth, h = container.clientHeight;
    renderer.setSize(w, h);
    if (camera.isPerspectiveCamera) {
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
  });
}

document.querySelectorAll(".nx-three-scene").forEach(mountScene);
