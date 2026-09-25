/**
 * Nexoria client runtime.
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 *
 * Responsibilities:
 *   1. Read the SSR hydration payload and attach event delegation to
 *      the already-rendered DOM (no re-render on first paint).
 *   2. Open a WebSocket to /_nexoria/live and apply incoming patches
 *      produced by the server-side differ (Python, optionally
 *      accelerated by the Rust hot path).
 *   3. Provide a tiny DOM patch applier — the actual diffing always
 *      happens server-side, so this file stays intentionally small
 *      and dependency-free (works with zero npm build step for simple
 *      apps; the Node toolchain in tools/node-build is only needed for
 *      bundling/minifying larger apps and the optional ThreeJS adapter).
 */
(function () {
  "use strict";

  const root = document.getElementById("nx-root");
  const dataEl = document.getElementById("nx-hydration-data");
  const hydration = dataEl ? JSON.parse(dataEl.textContent) : null;
  // The session id MUST come from the server (it's how the server knows
  // which rendered component + handler map this socket's clicks belong
  // to) -- a client-invented id would never match anything server-side
  // and every event would silently be dropped. Only fall back to a
  // random one if hydration data is somehow missing (defensive).
  const sessionId = (hydration && hydration.session) || (crypto.randomUUID
    ? crypto.randomUUID()
    : String(Date.now()) + Math.random());

  let socket = null;
  let reconnectDelay = 500;

  function connect() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(`${proto}://${location.host}/_nexoria/live`);
    socket.addEventListener("open", () => { reconnectDelay = 500; });
    socket.addEventListener("message", (evt) => {
      const msg = JSON.parse(evt.data);
      if (msg.type === "patch") applyPatches(msg.patches);
    });
    socket.addEventListener("close", () => {
      setTimeout(connect, reconnectDelay);
      reconnectDelay = Math.min(reconnectDelay * 2, 8000);
    });
  }

  function nodeAtPath(path) {
    let node = root.firstElementChild || root.firstChild;
    for (const idx of path) {
      if (!node) return null;
      node = node.childNodes[idx];
    }
    return node;
  }

  function buildDomFromDict(vnode) {
    if (vnode.t === "text") return document.createTextNode(vnode.v);
    const node = document.createElement(vnode.tag);
    applyProps(node, vnode.props || {}, vnode.events || {});
    for (const child of vnode.children || []) {
      node.appendChild(buildDomFromDict(child));
    }
    return node;
  }

  function applyProps(node, props, events) {
    for (const [k, v] of Object.entries(props)) {
      if (k === "class") node.className = v;
      else if (v === true) node.setAttribute(k, "");
      else if (v === false) node.removeAttribute(k);
      else node.setAttribute(k, v);
    }
    for (const [event, handlerId] of Object.entries(events)) {
      node.setAttribute(`data-nx-on-${event}`, handlerId);
    }
  }

  function applyPatches(patches) {
    for (const p of patches) {
      const target = nodeAtPath(p.path.slice(0, -1)) || root;
      const idx = p.path[p.path.length - 1];
      switch (p.op) {
        case "text":
          if (target.childNodes[idx]) target.childNodes[idx].textContent = p.payload;
          break;
        case "replace":
          if (target.childNodes[idx]) {
            target.replaceChild(buildDomFromDict(p.payload), target.childNodes[idx]);
          }
          break;
        case "insert":
          target.insertBefore(buildDomFromDict(p.payload), target.childNodes[idx] || null);
          break;
        case "remove":
          if (target.childNodes[idx]) target.removeChild(target.childNodes[idx]);
          break;
        case "update_props": {
          const el = nodeAtPath(p.path);
          if (el) applyProps(el, p.payload.props || {}, p.payload.events || {});
          break;
        }
      }
    }
  }

  // Event delegation: every element with data-nx-on-<event> forwards
  // that event to the server over the live socket, tagged with the
  // handler id the differ assigned at render time.
  const DELEGATED_EVENTS = ["click", "input", "change", "submit", "keydown", "keyup"];

  function dispatchToServer(handlerId, event) {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    const payload = {
      value: event.target && "value" in event.target ? event.target.value : null,
      key: event.key,
    };
    if (event.type === "submit") event.preventDefault();
    socket.send(JSON.stringify({
      event: event.type,
      handler_id: handlerId,
      session: sessionId,
      payload,
    }));
  }

  DELEGATED_EVENTS.forEach((eventName) => {
    document.addEventListener(eventName, (evt) => {
      let node = evt.target;
      const attr = `data-nx-on-${eventName}`;
      while (node && node !== document) {
        if (node.hasAttribute && node.hasAttribute(attr)) {
          dispatchToServer(node.getAttribute(attr), evt);
          break;
        }
        node = node.parentNode;
      }
    }, true);
  });

  connect();

  // Theme toggle -- the actual attribute is already set correctly before
  // first paint by the inline blocking script in <head> (see
  // render/html.py's render_document); this just persists explicit
  // user choices from here on. Wire a button to it with:
  //   el("button", "🌓", class_="nx-theme-toggle", onclick="window.__nexoria__.toggleTheme()")
  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-nx-theme") === "light" ? "light" : "dark";
    const next = current === "light" ? "dark" : "light";
    if (next === "light") {
      document.documentElement.setAttribute("data-nx-theme", "light");
    } else {
      document.documentElement.removeAttribute("data-nx-theme");
    }
    try { localStorage.setItem("nx-theme", next); } catch (e) { /* privacy mode etc. */ }
    return next;
  }

  // Merge, don't overwrite: other optional adapters (three-adapter.js,
  // gsap-adapter.js) may set their own namespaces on window.__nexoria__
  // and can execute before or after this script depending on where
  // App(threejs=True)/App(gsap=True) places their <script> tags --
  // clobbering the whole object here would silently wipe those out.
  window.__nexoria__ = Object.assign(window.__nexoria__ || {}, {
    hydration, applyPatches, sessionId, toggleTheme,
  });
})();
