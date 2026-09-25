// favicon.go answers the browser's unconditional GET /favicon.ico
// natively, straight from the asset cache, instead of proxying it to
// the Python backend and following that backend's redirect to
// /_nexoria/falcon-nexoria.ico (see App._favicon in core/app.py) --
// one cached read beats a proxied request plus a 302 plus a second
// request, on literally every page load.
package main

import (
	"net/http"
	"os"
	"path/filepath"
)

// faviconHandler serves Nexoria's own default favicon
// (falcon-nexoria.ico, shipped as a runtime asset -- see
// DEFAULT_FAVICON_ICO in core/app.py) directly out of runtimeDir when
// it's present on disk. Anything this can't resolve locally --
// runtimeDir not configured, the file missing, or an App(favicon=...)
// override the Go tier has no way to know about -- falls through to
// the proxy, so Python's own /favicon.ico route (redirect, a custom
// icon, or a deliberate 204 for App(favicon=None)) still gets the
// final say.
func faviconHandler(cache *AssetCache, runtimeDir string, proxy http.Handler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if runtimeDir != "" {
			path := filepath.Join(runtimeDir, "falcon-nexoria.ico")
			if info, err := os.Stat(path); err == nil && !info.IsDir() {
				if serveAsset(cache, w, r, path, "public, max-age=3600, immutable") {
					return
				}
			}
		}
		proxy.ServeHTTP(w, r)
	}
}
