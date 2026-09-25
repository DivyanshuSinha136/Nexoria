/**
 * Nexoria video.js adapter (optional, loaded only when App(videojs=True)
 * is set). Reads the declarative player config produced by
 * `nexoria.videojs.player.VideoPlayer.to_dict()` from each video
 * element's `data-nx-videojs` attribute and instantiates a real
 * video.js player. Classic script (not a module) -- relies on the
 * global `videojs` function from video.js's own UMD bundle, loaded
 * just before this file (see VIDEOJS_RUNTIME_TAG).
 *
 * Ecosystem: Pythonaibrain | Author: Divyanshu Sinha | License: MIT
 */
(function () {
  "use strict";

  const players = {};

  function buildOptions(spec) {
    const options = Object.assign(
      {
        controls: spec.controls !== false,
        autoplay: !!spec.autoplay,
        loop: !!spec.loop,
        muted: !!spec.muted,
        preload: spec.preload || "auto",
        fluid: spec.fluid !== false,
        sources: Array.isArray(spec.sources) ? spec.sources : [],
      },
      spec.options || {}
    );
    if (spec.aspectRatio) options.aspectRatio = spec.aspectRatio;
    if (Array.isArray(spec.playbackRates) && spec.playbackRates.length) {
      options.playbackRates = spec.playbackRates;
    }
    if (spec.width) options.width = spec.width;
    if (spec.height) options.height = spec.height;
    return options;
  }

  function addTracks(player, tracks) {
    if (!Array.isArray(tracks)) return;
    for (const t of tracks) {
      player.addRemoteTextTrack(
        { kind: t.kind, src: t.src, srclang: t.srclang, label: t.label, default: !!t.default },
        false // manualCleanup=false: video.js manages/cleans it up with the player
      );
    }
  }

  function activatePlugins(player, activePlugins, registrationId) {
    if (!activePlugins || typeof activePlugins !== "object") return;
    for (const [name, opts] of Object.entries(activePlugins)) {
      if (typeof player[name] !== "function") {
        console.error(
          `Nexoria video.js: plugin "${name}" isn't registered on the player -- ` +
          `check that its script is listed in App(videojs_plugins=[...]) and that ` +
          `"${name}" matches the property name the plugin actually registers ` +
          `(see the plugin's own docs).`,
          registrationId
        );
        continue;
      }
      try {
        player[name](opts || {});
      } catch (e) {
        console.error(`Nexoria video.js: plugin "${name}" threw during activation`, e);
      }
    }
  }

  function mountPlayer(el) {
    // Guard against double-init -- harmless if this script (or a
    // hand-written call to mountPlayer-equivalent logic) ever runs
    // twice against the same element, which would otherwise throw from
    // inside video.js itself.
    if (el.dataset.nxMounted === "1") return;

    let spec;
    try {
      spec = JSON.parse(el.getAttribute("data-nx-videojs"));
    } catch (e) {
      console.error("Nexoria video.js: invalid player spec (bad JSON)", e);
      return;
    }

    if (typeof videojs !== "function") {
      console.error(
        "Nexoria video.js: the `videojs` global wasn't found -- check that " +
        "video.js's own <script> tag loaded before this adapter (see " +
        "VIDEOJS_RUNTIME_TAG in nexoria/videojs/player.py)."
      );
      return;
    }
    if (!spec.sources || spec.sources.length === 0) {
      console.error("Nexoria video.js: no playable sources given for", el);
      return;
    }

    if (spec.poster) el.setAttribute("poster", spec.poster);

    // Capture the id BEFORE calling videojs() -- video.js internally
    // renames the original <video> element's id (appending
    // "_html5_api") as part of wrapping it in its own player structure,
    // since `el` is a live DOM node reference, `el.id` read *after*
    // construction would silently pick up that renamed id instead of
    // the one the Python author actually assigned via
    // VideoPlayer.to_element(player_id=...) -- breaking
    // window.__nexoria__.videojs.get/play/pause/dispose(id) for every
    // caller relying on the id they gave it.
    const registrationId = el.id;

    let player;
    try {
      player = videojs(el, buildOptions(spec));
    } catch (e) {
      console.error("Nexoria video.js: failed to initialize player", e);
      return;
    }

    player.on("error", () => {
      const err = player.error();
      console.error(
        "Nexoria video.js: playback error" + (err ? ` (code ${err.code}): ${err.message}` : ""),
        registrationId
      );
    });

    player.ready(() => {
      // addRemoteTextTrack needs the player's tech to be ready --
      // calling it immediately after construction (before `ready`)
      // silently drops the track on some tech/environment
      // combinations, so tracks are added here instead.
      addTracks(player, spec.tracks);
      activatePlugins(player, spec.activePlugins, registrationId);
      el.dispatchEvent(new CustomEvent("nexoria:videojs:ready", { bubbles: true, detail: { player } }));
    });

    el.dataset.nxMounted = "1";
    players[registrationId] = player;
  }

  document.querySelectorAll(".nx-videojs-player").forEach(mountPlayer);

  window.__nexoria__ = window.__nexoria__ || {};
  window.__nexoria__.videojs = {
    players,
    get: (id) => players[id],
    play: (id) => players[id] && players[id].play(),
    pause: (id) => players[id] && players[id].pause(),
    dispose: (id) => {
      if (players[id]) {
        players[id].dispose();
        delete players[id];
      }
    },
    /** Mount any .nx-videojs-player elements added to the DOM after
     * initial page load (e.g. by a future dynamic-content feature). */
    mountNew: () => document.querySelectorAll(".nx-videojs-player").forEach(mountPlayer),
  };
})();
