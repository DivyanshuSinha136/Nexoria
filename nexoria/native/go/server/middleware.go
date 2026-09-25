// middleware.go wraps the mux with, from outermost to innermost:
// panic recovery -> request logging -> security headers -> gzip
// compression -> the actual routes.
//
// Wrapping http.ResponseWriter is where it's easy to accidentally
// break the live-reload WebSocket channel: httputil.ReverseProxy
// upgrades a WS connection by type-asserting the ResponseWriter it
// was given to http.Hijacker and hijacking the raw connection.
// Embedding a bare http.ResponseWriter field only promotes that
// interface's own three methods (Header/Write/WriteHeader) -- it does
// NOT make the wrapper satisfy http.Hijacker even though the
// underlying concrete value does, so any wrapper sitting in front of
// the proxy needs its own explicit Hijack (and Flush, for streamed
// responses) method that delegates to the real ResponseWriter
// underneath. statusCapturingWriter below does this; the gzip wrapper
// sidesteps the question entirely by never wrapping Upgrade requests
// in the first place (see withGzip).
package main

import (
	"bufio"
	"compress/gzip"
	"fmt"
	"log"
	"net"
	"net/http"
	"strings"
	"time"
)

// -- request logging ---------------------------------------------------

func logRequests(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		lw := &statusCapturingWriter{ResponseWriter: w, status: http.StatusOK}
		next.ServeHTTP(lw, r)
		log.Printf("%s %s %d %s", r.Method, r.URL.Path, lw.status, time.Since(start))
	})
}

// statusCapturingWriter wraps http.ResponseWriter purely to remember
// which status code a handler wrote, since http.ResponseWriter itself
// has no getter for it -- needed so logRequests can log the real
// response status instead of always assuming 200.
type statusCapturingWriter struct {
	http.ResponseWriter
	status int
}

func (w *statusCapturingWriter) WriteHeader(code int) {
	w.status = code
	w.ResponseWriter.WriteHeader(code)
}

// Hijack delegates to the underlying ResponseWriter's own Hijack, so a
// WebSocket upgrade proxied straight through this wrapper still works
// (see the file-level doc comment on why this can't be inherited for
// free from embedding).
func (w *statusCapturingWriter) Hijack() (net.Conn, *bufio.ReadWriter, error) {
	hj, ok := w.ResponseWriter.(http.Hijacker)
	if !ok {
		return nil, nil, fmt.Errorf("nexoria-server: underlying ResponseWriter does not support hijacking")
	}
	return hj.Hijack()
}

// Flush delegates to the underlying ResponseWriter's own Flush, so
// streamed/chunked responses proxied through this wrapper still flush
// incrementally instead of buffering until the handler returns.
func (w *statusCapturingWriter) Flush() {
	if f, ok := w.ResponseWriter.(http.Flusher); ok {
		f.Flush()
	}
}

// -- security headers ---------------------------------------------------

// withSecurityHeaders sets a small, conservative set of headers safe
// for every response regardless of what the app does: neither header
// changes existing behavior for a normal page, they only remove a
// footgun (a browser guessing a different content type than the one
// this server declared) and reduce what's leaked on cross-origin
// navigations. Anything more opinionated (CSP, X-Frame-Options) is
// genuinely app-specific and left to the app itself, not imposed here.
func withSecurityHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		h := w.Header()
		h.Set("X-Content-Type-Options", "nosniff")
		h.Set("Referrer-Policy", "strict-origin-when-cross-origin")
		next.ServeHTTP(w, r)
	})
}

// -- gzip compression ---------------------------------------------------

// withGzip transparently gzip-compresses compressible responses (as
// judged by isCompressible on whatever Content-Type the handler sets)
// for clients that advertise gzip support, most importantly the
// proxied SSR HTML from the Python backend -- static/runtime assets
// already carry their own pre-compressed copy from AssetCache and are
// written directly, so this mainly picks up everything else.
//
// Upgrade requests (the live-reload WebSocket) are passed through
// completely unwrapped: they're not compressible responses in the
// first place, and wrapping would put an extra non-Hijacker layer
// between the proxy and the real connection for no benefit.
func withGzip(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if isUpgradeRequest(r) || !acceptsGzip(r) {
			next.ServeHTTP(w, r)
			return
		}
		gzw := &gzipResponseWriter{ResponseWriter: w}
		defer gzw.Close()
		next.ServeHTTP(gzw, r)
	})
}

func isUpgradeRequest(r *http.Request) bool {
	return strings.Contains(strings.ToLower(r.Header.Get("Connection")), "upgrade")
}

type gzipResponseWriter struct {
	http.ResponseWriter
	gz          *gzip.Writer
	wroteHeader bool
	skip        bool // true once we've decided not to compress this response
}

func (g *gzipResponseWriter) WriteHeader(status int) {
	if g.wroteHeader {
		return
	}
	g.wroteHeader = true
	h := g.ResponseWriter.Header()
	// Respect a handler that already picked its own encoding (the
	// static-asset path serving a pre-gzipped cache entry sets
	// Content-Encoding itself) or whose content type isn't worth
	// compressing (images, already-compressed formats, or nothing set
	// at all).
	if h.Get("Content-Encoding") != "" || !isCompressible(h.Get("Content-Type")) {
		g.skip = true
		g.ResponseWriter.WriteHeader(status)
		return
	}
	h.Del("Content-Length") // the compressed body's length differs
	h.Set("Content-Encoding", "gzip")
	h.Add("Vary", "Accept-Encoding")
	g.ResponseWriter.WriteHeader(status)
	g.gz = gzip.NewWriter(g.ResponseWriter)
}

func (g *gzipResponseWriter) Write(b []byte) (int, error) {
	if !g.wroteHeader {
		g.WriteHeader(http.StatusOK)
	}
	if g.skip || g.gz == nil {
		return g.ResponseWriter.Write(b)
	}
	return g.gz.Write(b)
}

// Flush lets a streamed backend response keep flushing incrementally
// through the gzip writer instead of buffering until Close().
func (g *gzipResponseWriter) Flush() {
	if g.gz != nil {
		g.gz.Flush()
	}
	if f, ok := g.ResponseWriter.(http.Flusher); ok {
		f.Flush()
	}
}

func (g *gzipResponseWriter) Close() error {
	if g.gz != nil {
		return g.gz.Close()
	}
	return nil
}

// -- panic recovery ---------------------------------------------------

// withRecover turns a panic in any handler into a 500 instead of
// killing the whole process -- one bad request (or a bug triggered by
// one) should never take down every other in-flight connection.
func withRecover(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if rec := recover(); rec != nil {
				log.Printf("nexoria-server: panic handling %s %s: %v", r.Method, r.URL.Path, rec)
				http.Error(w, "500 internal server error", http.StatusInternalServerError)
			}
		}()
		next.ServeHTTP(w, r)
	})
}
