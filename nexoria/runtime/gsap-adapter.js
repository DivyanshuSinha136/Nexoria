/**
 * Nexoria GSAP adapter (optional, loaded only when App(gsap=True) or an
 * Animation is used). Reads the declarative tween/timeline specs
 * produced by `nexoria.gsap.animation.Animation.to_dict()` from each
 * `<script type="application/json" class="nx-gsap-anim">` marker and
 * builds real GSAP timelines against the actual rendered DOM.
 *
 * Plugins: when `App(gsap_plugins=[...])` names one or more official GSAP
 * plugins (ScrollTrigger, Draggable, Flip, MotionPathPlugin, SplitText,
 * ...), Python emits their ESM entry points into the shared import map
 * plus an inert `<script id="nx-gsap-plugins">` JSON marker (see
 * `nexoria.gsap.animation.gsap_plugin_config_tag`) listing the enabled
 * names. Before mounting any animation, this adapter dynamically
 * `import()`s each one (resolved through that same import map, e.g.
 * `"gsap/ScrollTrigger"`) and hands it to `gsap.registerPlugin()` --
 * after that, a Tween's `vars` can freely use plugin-specific properties
 * (`scrollTrigger={...}`, `motionPath={...}`, `drawSVG=...`, etc.).
 *
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
import { gsap } from "gsap";

const timelines = {};

async function registerConfiguredPlugins() {
  const configEl = document.getElementById("nx-gsap-plugins");
  if (!configEl) return [];
  let names;
  try {
    names = JSON.parse(configEl.textContent);
  } catch (e) {
    console.error("Nexoria GSAP: invalid plugin config", e);
    return [];
  }
  const registered = [];
  await Promise.all(
    names.map(async (name) => {
      try {
        const mod = await import(/* @vite-ignore */ `gsap/${name}`);
        const plugin = mod[name] || mod.default;
        if (!plugin) {
          console.error(`Nexoria GSAP: plugin module "${name}" has no "${name}" export`);
          return;
        }
        gsap.registerPlugin(plugin);
        registered.push(name);
      } catch (e) {
        console.error(`Nexoria GSAP: failed to load plugin "${name}"`, e);
      }
    })
  );
  return registered;
}

function buildTween(tl, spec) {
  const vars = { ...spec.vars };
  const method = spec.from_vars ? "from" : "to";
  const position = spec.position === null || spec.position === undefined ? undefined : spec.position;
  if (tl) {
    tl[method](spec.target, vars, position);
    return null;
  }
  return gsap[method](spec.target, vars);
}

function buildTimeline(spec, parentTl) {
  if (spec.type === "tween") {
    return buildTween(parentTl, spec);
  }
  // spec.type === "timeline"
  if (parentTl) {
    const nested = gsap.timeline({ repeat: spec.repeat || 0, yoyo: !!spec.yoyo });
    for (const child of spec.children) buildTimeline(child, nested);
    const position = spec.position === null || spec.position === undefined ? undefined : spec.position;
    parentTl.add(nested, position);
    return nested;
  }
  const tl = gsap.timeline({
    repeat: spec.repeat || 0,
    yoyo: !!spec.yoyo,
    paused: !!spec.paused,
  });
  for (const child of spec.children) buildTimeline(child, tl);
  return tl;
}

function mountAnimation(scriptEl) {
  let payload;
  try {
    payload = JSON.parse(scriptEl.textContent);
  } catch (e) {
    console.error("Nexoria GSAP: invalid animation payload", e);
    return;
  }
  const built = buildTimeline(payload.root, null);
  timelines[payload.name] = built;
  if (payload.autoplay === false && built && built.pause) {
    built.pause();
  }
}

window.__nexoria__ = window.__nexoria__ || {};
window.__nexoria__.gsap = {
  timelines,
  plugins: [],
  ready: (async () => {
    // Plugins must be registered *before* any Tween/Timeline using their
    // vars (scrollTrigger, motionPath, drawSVG, ...) is built, so mounting
    // waits on this even though it means animations attach a tick later
    // than a plugin-free page would.
    const registered = await registerConfiguredPlugins();
    window.__nexoria__.gsap.plugins = registered;
    document.querySelectorAll(".nx-gsap-anim").forEach(mountAnimation);
  })(),
  play: (name) => timelines[name] && timelines[name].play(),
  pause: (name) => timelines[name] && timelines[name].pause(),
  restart: (name) => timelines[name] && timelines[name].restart(),
  reverse: (name) => timelines[name] && timelines[name].reverse(),
};
