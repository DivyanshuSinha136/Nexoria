// Command nexoria-server is Nexoria's optional native edge server.
//
// It is NOT a reimplementation of Nexoria's rendering engine -- routing,
// component rendering, state, and the live-reload WebSocket protocol all
// stay exactly where they already live: in the Python ASGI app
// (nexoria.core.app.App), served by uvicorn exactly as before. What this
// process adds in front of that is a fast, native front door:
//
//   - static assets (the app's own static_dir, and Nexoria's own
//     /_nexoria/<file> runtime assets: runtime.js, base.css, the JS
//     adapters, the favicon) are served directly from disk -- backed by
//     an in-memory, stat-validated cache (cache.go/static.go) so a warm
//     asset costs no disk I/O, and pre-gzipped for clients that accept
//     it
//   - the browser's unconditional GET /favicon.ico is answered natively
//     from that same cache (favicon.go) instead of round-tripping
//     through the Python backend's redirect on every single page load
//   - everything else (SSR HTML routes, the /_nexoria/live WebSocket
//     channel, /_nexoria/health) is reverse-proxied straight through to
//     the Python backend (proxy.go), including WebSocket upgrades --
//     Go's stdlib httputil.ReverseProxy has handled `Connection: Upgrade`
//     requests by hijacking the connection and copying bytes both ways
//     since Go 1.12, so no bespoke WebSocket plumbing is needed here
//   - a second, purely-local /_nexoria/native-health endpoint
//     (health.go) reports this process's own uptime and cache stats,
//     for infra that wants to probe the edge tier without that probe
//     depending on the Python backend also being healthy
//   - gzip compression, basic security headers, panic recovery, and
//     real request/connection timeouts sit in front of all of the above
//     (middleware.go)
//   - a built-in firewall (firewall.go) sits in front of EVERYTHING
//     else, including the middleware above: IP allow/deny lists,
//     per-client-IP rate limiting, a request body size cap, and basic
//     request sanity checks (disallowed methods, oversized request
//     lines, raw path-traversal/NUL-byte probes). Enabled by default
//     (-firewall=false to disable); see firewall.go's file-level
//     comment for the full check order and -firewall-* flags for
//     configuration. Its live counters are at
//     /_nexoria/firewall-status.
//
// nexoria.core.app.App spawns this as a subprocess (see run() in
// nexoria/core/app.py) only when a compiled binary is available AND the
// caller isn't in reload/dev mode; the plain-Python uvicorn path is
// always the fallback if this binary is missing, fails to start, or
// isn't wanted (App.run(native=False)).
package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"
	"time"
)

func main() {
	listenAddr := flag.String("listen", "127.0.0.1:8000", "address to listen on")
	backendAddr := flag.String("backend", "127.0.0.1:8001", "address of the Python ASGI backend (uvicorn) to proxy to")
	staticDir := flag.String("static-dir", "", "optional directory served under /static/ (matches App(static_dir=...)); empty disables it")
	runtimeDir := flag.String("runtime-dir", "", "directory containing Nexoria's runtime assets (runtime.js, base.css, adapters, favicon), served under /_nexoria/<file>")
	name := flag.String("name", "Nexoria App", "app name, used only in log lines and the native-health response")
	gzipEnabled := flag.Bool("gzip", true, "gzip-compress compressible responses for clients that accept it")
	cacheMaxBytes := flag.Int64("cache-max-bytes", 64<<20, "max total bytes of static/runtime asset content kept in the in-memory cache")
	readTimeout := flag.Duration("read-timeout", 15*time.Second, "max duration for reading an entire request, including its body")
	writeTimeout := flag.Duration("write-timeout", 60*time.Second, "max duration before timing out writes of the response; 0 disables it (needed only if you serve very large/slow responses -- the live-reload WebSocket is unaffected, see note in proxy.go)")
	idleTimeout := flag.Duration("idle-timeout", 120*time.Second, "max duration to keep idle keep-alive connections open")
	firewallFlags := registerFirewallFlags()
	flag.Parse()

	firewallCfg, err := parseFirewallConfig(firewallFlags)
	if err != nil {
		log.Fatalf("nexoria-server: %v", err)
	}
	firewall := NewFirewall(firewallCfg)

	backendURL, err := url.Parse("http://" + *backendAddr)
	if err != nil {
		log.Fatalf("nexoria-server: invalid -backend address %q: %v", *backendAddr, err)
	}
	proxy := newBackendProxy(backendURL)
	cache := NewAssetCache(*cacheMaxBytes)

	mux := http.NewServeMux()

	if *staticDir != "" {
		abs, err := filepath.Abs(*staticDir)
		if err != nil {
			log.Fatalf("nexoria-server: invalid -static-dir %q: %v", *staticDir, err)
		}
		mux.HandleFunc("/static/", staticDirHandler(cache, abs))
	}

	if *runtimeDir != "" {
		mux.HandleFunc("/_nexoria/", runtimeAssetHandler(cache, *runtimeDir, proxy))
	}
	// Registered whether or not runtimeDir is set: with no runtimeDir,
	// faviconHandler simply always falls through to the proxy, same as
	// before this route existed.
	mux.HandleFunc("/favicon.ico", faviconHandler(cache, *runtimeDir, proxy))
	mux.HandleFunc("/_nexoria/native-health", nativeHealthHandler(cache, *name, firewall))
	mux.HandleFunc("/_nexoria/firewall-status", firewallStatusHandler(firewall))

	mux.Handle("/", proxy)

	var handler http.Handler = mux
	if *gzipEnabled {
		handler = withGzip(handler)
	}
	handler = withSecurityHeaders(handler)
	handler = logRequests(handler)
	// The firewall sits outside logRequests/securityHeaders/gzip so a
	// blocked or rate-limited request is rejected before any of that
	// downstream work runs -- see firewall.go's file-level comment for
	// the full rationale and check order.
	handler = withFirewall(handler, firewall)
	handler = withRecover(handler)

	server := &http.Server{
		Addr:              *listenAddr,
		Handler:           handler,
		ReadHeaderTimeout: 15 * time.Second,
		ReadTimeout:       *readTimeout,
		WriteTimeout:      *writeTimeout,
		IdleTimeout:       *idleTimeout,
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	go func() {
		<-ctx.Done()
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		_ = server.Shutdown(shutdownCtx)
	}()

	// Printed just before blocking on ListenAndServe, purely as a
	// visible startup confirmation in the console/log output --
	// nexoria.core.app.App's subprocess launcher does NOT parse this
	// line for synchronization; it just gives the process a short fixed
	// window to still be running (see _try_run_native() in
	// core/app.py) before treating startup as successful. Keep this
	// line human-readable, not machine-parsed.
	fmt.Printf("nexoria-server: %s ready, listening on http://%s (backend %s)\n", *name, *listenAddr, *backendAddr)
	fmt.Printf("nexoria-server: %s\n", firewall.startupSummary())

	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("nexoria-server: %v", err)
	}
}

// staticDirHandler serves the app's own static_dir under /static/,
// backed by the shared cache. Unlike the stdlib's http.FileServer
// (the previous implementation here), a directory with no index.html
// 404s instead of rendering a browsable listing -- an app's static_dir
// is for named assets (CSS/JS/images), not something meant to be
// crawled, matching the nginx/Apache "Options -Indexes" convention.
func staticDirHandler(cache *AssetCache, staticDirAbs string) http.HandlerFunc {
	prefix := staticDirAbs + string(filepath.Separator)
	return func(w http.ResponseWriter, r *http.Request) {
		rel := strings.TrimPrefix(r.URL.Path, "/static/")
		// filepath.Clean collapses any ".."/".": joining a cleaned,
		// rooted relative path can't walk outside staticDirAbs, unlike
		// naively filepath.Join-ing the raw request path.
		cleanRel := filepath.Clean("/" + rel)[1:]
		fullPath := filepath.Join(staticDirAbs, cleanRel)
		if fullPath != staticDirAbs && !strings.HasPrefix(fullPath, prefix) {
			http.NotFound(w, r)
			return
		}

		if info, err := os.Stat(fullPath); err == nil && info.IsDir() {
			indexPath := filepath.Join(fullPath, "index.html")
			if _, err := os.Stat(indexPath); err != nil {
				http.NotFound(w, r)
				return
			}
			fullPath = indexPath
		}

		if !serveAsset(cache, w, r, fullPath, "public, max-age=60, must-revalidate") {
			http.NotFound(w, r)
		}
	}
}

// runtimeAssetHandler serves a file directly out of runtimeDir, via
// the shared cache, when the requested /_nexoria/<name> maps to a real
// file there (runtime.js, base.css, an adapter script, the favicon,
// ...), and falls through to the backend proxy for anything else --
// notably /_nexoria/live (the WebSocket channel) and /_nexoria/health,
// neither of which is a file on disk, plus any unknown filename (the
// Python fallback's _serve_runtime_asset() 404s on those too, so
// proxying through gets the same answer, just via one extra hop).
func runtimeAssetHandler(cache *AssetCache, runtimeDir string, proxy http.Handler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		name := strings.TrimPrefix(r.URL.Path, "/_nexoria/")
		// filepath.Base strips any directory components a malformed or
		// malicious request path might smuggle in (e.g. "../../secrets"),
		// mirroring the same os.path.basename() guard the Python
		// fallback (_serve_runtime_asset in core/app.py) already applies.
		safeName := filepath.Base(name)
		if safeName == "." || safeName == string(filepath.Separator) || safeName == "" {
			proxy.ServeHTTP(w, r)
			return
		}
		fullPath := filepath.Join(runtimeDir, safeName)
		if info, err := os.Stat(fullPath); err != nil || info.IsDir() {
			proxy.ServeHTTP(w, r)
			return
		}
		// Runtime assets are versioned with the installed Nexoria
		// package, not by request -- a new Nexoria version means a new
		// file on disk (and a restarted server), never a mutated one at
		// the same path, so a long, immutable cache lifetime is safe.
		if !serveAsset(cache, w, r, fullPath, "public, max-age=3600, immutable") {
			proxy.ServeHTTP(w, r)
		}
	}
}
