# Nexoria Flowcharts

Diagrams are [Mermaid](https://mermaid.js.org) and render natively on GitHub and in most Markdown viewers. Companion documents: [ARCHITECTURE.md](ARCHITECTURE.md), [TOP-LEVEL-API-REFRANCE.md](TOP-LEVEL-API-REFRANCE.md).

**Contents:** 1. [Page request (SSR)](#1-page-request-ssr) · 2. [Hydration](#2-hydration) · 3. [Event → patch cycle](#3-event--patch-cycle) · 4. [Differ](#4-the-differ) · 5. [Router matching](#5-router-matching) · 6. [`App.run()` mode selection](#6-apprun-mode-selection) · 7. [Go edge request path](#7-go-edge-request-path) · 8. [`<head>` assembly](#8-head-assembly) · 9. [Integration lifecycle](#9-integration-lifecycle) · 10. [Native tier selection](#10-native-tier-selection) · 11. [`nexoria build`](#11-nexoria-build) · 12. [`nexoria native build`](#12-nexoria-native-build) · 13. [Theme toggle](#13-theme-toggle)

---

## 1. Page request (SSR)

```mermaid
flowchart TD
    A["GET /path"] --> B{"Middleware<br/>before_request"}
    B -->|"returns a Response"| Z["Send that response"]
    B -->|"returns None (all)"| C["Router.resolve path plus query params"]
    C --> D{"Match?"}
    D -->|"no, no not-found set"| N["Built-in 404 page<br/>status 404"]
    D -->|"no, not-found set"| E
    D -->|"yes: guards pass"| E["Instantiate component<br/>setup() runs"]
    E --> F["component.render()<br/>returns Element tree"]
    F --> G["render_to_html<br/>handlers become data-nx-on attributes"]
    G --> H["Create session id<br/>store component, tree, handler map"]
    H --> I["_build_head<br/>theme, css, meta, import map, adapters"]
    I --> J["render_document<br/>wrap body, add runtime.js and hydration JSON"]
    J --> K["200 text/html"]
```

Note: the not-found component, when set, is served with status **200**.

## 2. Hydration

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as Server
    B->>S: GET /
    S-->>B: HTML (complete page) + hydration JSON + runtime.js tag
    Note over B: Page is already visible and readable
    B->>B: runtime.js parses #nx-hydration-data
    B->>S: WebSocket connect /_nexoria/live
    B->>B: Install one capture-phase listener per event type
    B->>B: Adapters scan DOM and mount libraries
    Note over B,S: Idle until the user interacts
```

## 3. Event → patch cycle

```mermaid
sequenceDiagram
    participant U as User
    participant R as runtime.js
    participant W as App WebSocket loop
    participant C as Component
    participant D as differ
    U->>R: click on button data-nx-on-click=h1
    R->>W: event, handler_id h1, session, payload
    W->>W: look up session (ignore if unknown)
    W->>C: run handler h1 (await if async)
    C->>C: state.update(count=1)
    W->>C: render() again
    C-->>W: new Element tree
    W->>D: diff(old_tree, new_tree)
    D-->>W: patch list
    W->>W: store new tree, rebuild handler map (new ids)
    W-->>R: type patch, patches
    R->>R: apply each patch to the DOM in order
    R-->>U: updated UI
```

**Worked example** (a real capture from a counter component; the button was clicked once):

```text
→ {"event":"click","handler_id":"h1","session":"dddc02ed…","payload":{"value":null}}
← {"type":"patch","patches":[
     {"op":"text","path":[0,0],"payload":"Clicked 1 times"},
     {"op":"update_props","path":[1],"payload":{"events":{"click":"h2"},"props":{}}}]}
```

The text node inside the first `<p>` changed, and the button's handler id was refreshed (`h1` → `h2`). Paths start at the first element inside `#nx-root`.

## 4. The differ

```mermaid
flowchart TD
    S(["diff old, new"]) --> A{"old and new both None?"}
    A -->|yes| X["no patches"]
    A -->|no| B{"old None?"}
    B -->|yes| I["insert new"]
    B -->|no| C{"new None?"}
    C -->|yes| RM["remove old"]
    C -->|no| D{"both text?"}
    D -->|yes| T{"same string?"}
    T -->|no| TP["text patch"]
    T -->|yes| X
    D -->|no| E{"same tag and both elements?"}
    E -->|no| RP["replace"]
    E -->|yes| F{"props or handler ids differ?"}
    F -->|yes| UP["update_props"]
    F -->|no| G
    UP --> G["diff children"]
    G --> H{"both child lists fully keyed?"}
    H -->|yes| K["match by key<br/>insert new keys, remove missing keys,<br/>recurse on shared keys"]
    H -->|no| P["match by position<br/>recurse, then insert extras or remove extras"]
```

Keyed matching has [documented limits](render.md#known-limitations-of-keyed-lists) (reorders, multiple removals).

## 5. Router matching

```mermaid
flowchart TD
    A["resolve path"] --> B["Iterate routes in registration order"]
    B --> C{"Pattern matches?<br/>static, :param, wildcard"}
    C -->|no| B
    C -->|yes| D{"All guards truthy?"}
    D -->|no| B
    D -->|yes| E["Component with params and extra props"]
    B -->|"routes exhausted"| F{"not-found set?"}
    F -->|yes| G["Not-found component"]
    F -->|no| H["None: App shows built-in 404"]
```

## 6. `App.run()` mode selection

```mermaid
flowchart TD
    A["app.run host, port, reload, native, firewall"] --> B{"reload is True?"}
    B -->|yes| C["Find module:variable from call stack<br/>uvicorn with autoreload<br/>native ignored"]
    B -->|no| D{"native is False?"}
    D -->|yes| U["Plain uvicorn"]
    D -->|no| E{"nexoria-server binary found?"}
    E -->|no| W["warn if native was True"] --> U
    E -->|yes| F["Start uvicorn on a free loopback port in a thread"]
    F --> G{"Backend answers in time?"}
    G -->|no| W2["warn"] --> U
    G -->|yes| H["Spawn nexoria-server with firewall flags"]
    H --> I{"Alive after about 1.5 s?"}
    I -->|no| W3["warn"] --> U
    I -->|yes| J["Serve: Go edge in front of Python<br/>Ctrl+C stops both"]
```

## 7. Go edge request path

```mermaid
flowchart TD
    R["Incoming request"] --> FW1{"Deny list?"}
    FW1 -->|match| X1["Blocked"]
    FW1 -->|no| FW2{"Allow list non-empty<br/>and not listed?"}
    FW2 -->|yes| X1
    FW2 -->|no| FW3{"Rate limit exceeded<br/>for this IP?"}
    FW3 -->|yes| X2["429"]
    FW3 -->|no| FW4{"Sanity check fails?<br/>method, request line, traversal, NUL"}
    FW4 -->|yes| X1
    FW4 -->|no| CAP["Apply body size cap"]
    CAP --> MW["gzip, security headers, panic recovery"]
    MW --> RT{"Path"}
    RT -->|"/static/*"| ST["Static cache (memory)"]
    RT -->|"/_nexoria/ file, /favicon.ico"| RA["Runtime asset cache"]
    RT -->|"/_nexoria/native-health<br/>/_nexoria/firewall-status"| LH["Local JSON"]
    RT -->|"everything else incl. WebSocket"| PX["Reverse proxy to uvicorn"]
```

## 8. `<head>` assembly

```mermaid
flowchart LR
    A["base.css link"] --> B["theme :root variables"]
    B --> C["light theme override<br/>if light_theme set"]
    C --> D["app plus component Stylesheet"]
    D --> E["description and Open Graph tags"]
    E --> F["favicon links"]
    F --> G["ONE merged import map<br/>three, gsap, chart.js, aggrid, spline, ..."]
    G --> H["adapter scripts<br/>only for enabled flags"]
    H --> I["classic tags: iconify, QR, OpenLayers,<br/>video.js, Bootstrap, Tailwind"]
```

## 9. Integration lifecycle

```mermaid
sequenceDiagram
    participant P as Python component
    participant A as App head
    participant J as adapter.js
    participant L as Library
    P->>P: Chart(...).to_element() → canvas with data-nx-chart JSON
    A->>A: App(chartjs=True) adds import map and adapter tag
    Note over J: On page load
    J->>J: querySelectorAll(".nx-chartjs-canvas")
    J->>L: build real object from JSON spec
    J->>J: register window.__nexoria__.chartjs
    Note over P,J: Later patches that add new widgets need mountNew()
```

## 10. Native tier selection

```mermaid
flowchart TD
    subgraph Differ
      A["import nexoria.render.diff"] --> B{"_nexoria_vdom_cpp imports?"}
      B -->|yes| C["C++ VDOM + Rust interner"]
      B -->|no| D{"_nexoria_rs imports?"}
      D -->|yes| E["PyO3 Rust differ"]
      D -->|no| F["Pure Python differ"]
    end
    subgraph Hashing
      G["fingerprint / scoped class"] --> H{"_nexoria_rs.hash_asset?"}
      H -->|yes| I["xxHash64, 10 hex"]
      H -->|no| J["blake2b"]
    end
    subgraph JS_engine
      K["Runtime()"] --> L{"_nexoria_js imports?"}
      L -->|yes| M["QuickJS-ng engine"]
      L -->|no| N["NativeEngineUnavailable"]
    end
    subgraph GPU
      O["gpu.batch_hash / batch_row_diff"] --> P{"module built and CUDA device present?"}
      P -->|yes| Q["CUDA kernels"]
      P -->|no| R["Python fallback"]
    end
```

## 11. `nexoria build`

```mermaid
flowchart TD
    A["nexoria build"] --> B{"node on PATH?"}
    B -->|no| W["warn and skip"]
    B -->|yes| C["node tools/node-build/build.js"]
    C --> D["Clean dist/ unless watch or no-clean"]
    D --> E["Copy runtime.js and adapters<br/>rename with sha1 hash"]
    E --> F{"tailwind input file<br/>and @tailwindcss/cli?"}
    F -->|yes| G["Compile minified dist/tailwind.css"]
    F -->|no| H
    G --> H["esbuild: bundle static/*.js<br/>minify, hash names"]
    H --> I["Write dist/manifest.json"]
```

## 12. `nexoria native build`

```mermaid
flowchart TD
    A["nexoria native build flags"] --> B["Rust safety core: cargo build --release"]
    B --> C["C++ VDOM: CMake + Ninja<br/>or Makefile.mingw"]
    C --> D{"--vdom-only?"}
    D -->|no| E["JS engine: CMake, vendored QuickJS-ng"]
    D -->|yes| F
    E --> F{"--with-go-server or --go-server-only?"}
    F -->|yes| G["go build nexoria-server into nexoria/_bin"]
    F -->|no| H
    G --> H{"--with-gpu or --gpu-only?"}
    H -->|yes| I{"nvcc found?"}
    I -->|yes| J["CMake CUDA build"]
    I -->|no| K["error: install CUDA Toolkit"]
    H -->|no| L["Copy modules into package dir"]
    J --> L
    L --> M["nexoria doctor: verify"]
```

## 13. Theme toggle

```mermaid
sequenceDiagram
    participant H as Inline head script
    participant D as document.documentElement
    participant U as User
    participant R as runtime.js
    H->>H: read localStorage nx-theme, else prefers-color-scheme
    H->>D: set data-nx-theme before CSS is parsed
    Note over D: No flash of the wrong theme
    U->>R: click theme_toggle_button
    R->>D: flip data-nx-theme
    R->>R: persist to localStorage
    Note over D: Bootstrap adapter mirrors it to data-bs-theme
```
