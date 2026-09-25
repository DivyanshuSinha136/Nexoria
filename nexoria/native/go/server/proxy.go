// proxy.go builds the reverse proxy to the Python ASGI backend. The
// stdlib default (httputil.NewSingleHostReverseProxy with its default
// Transport) works, but leans on http.DefaultTransport's defaults,
// which were never tuned for "always the same one loopback backend" --
// this gives it its own Transport with real timeouts and a connection
// pool sized for that actual traffic shape, plus a clearer response
// than the stdlib's bare "context deadline exceeded" text when the
// backend is down.
package main

import (
	"io"
	"log"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"time"
)

func newBackendProxy(backendURL *url.URL) *httputil.ReverseProxy {
	proxy := httputil.NewSingleHostReverseProxy(backendURL)
	proxy.ErrorLog = log.New(os.Stderr, "nexoria-server: backend proxy: ", log.LstdFlags)
	proxy.Transport = &http.Transport{
		Proxy: http.ProxyFromEnvironment,
		DialContext: (&net.Dialer{
			Timeout:   5 * time.Second,
			KeepAlive: 30 * time.Second,
		}).DialContext,
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 20,
		IdleConnTimeout:     90 * time.Second,
		// Both endpoints are the loopback backend this same process
		// spawned (see App._try_run_native in core/app.py) -- there's
		// no TLS handshake to time out, this is just a safe stdlib
		// default carried over in case a future backend address isn't
		// always plain http on loopback.
		TLSHandshakeTimeout:   5 * time.Second,
		ExpectContinueTimeout: 1 * time.Second,
		// The live-reload WebSocket channel needs its Upgrade response
		// back promptly (it's a handshake, not a slow poll), and SSR
		// routes are local Python rendering -- neither should ever need
		// more than a few seconds of headroom to produce headers.
		ResponseHeaderTimeout: 30 * time.Second,
	}
	proxy.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
		log.Printf("nexoria-server: backend proxy error for %s %s: %v", r.Method, r.URL.Path, err)
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		w.Header().Set("Cache-Control", "no-store")
		w.WriteHeader(http.StatusBadGateway)
		_, _ = io.WriteString(w, "502 Bad Gateway: the Nexoria backend is not responding.\n")
	}
	return proxy
}
