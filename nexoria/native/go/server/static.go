// static.go serves files backed by AssetCache over HTTP: correct
// Content-Type/ETag/Cache-Control headers, gzip negotiation against a
// pre-compressed copy when one exists, and conditional-request /
// Range support for the uncompressed path via http.ServeContent.
package main

import (
	"bytes"
	"net/http"
	"strconv"
	"strings"
	"time"
)

// serveAsset serves the file at diskPath from the shared cache,
// applying cacheControl and standard conditional-request handling.
// Returns false, having written nothing, if the file can't be loaded
// (missing, unreadable, a directory) so callers can fall through to
// another handler -- e.g. the reverse proxy -- instead of just
// 404ing on something the backend might still be able to answer.
func serveAsset(cache *AssetCache, w http.ResponseWriter, r *http.Request, diskPath, cacheControl string) bool {
	asset, err := cache.Load(diskPath)
	if err != nil {
		return false
	}

	header := w.Header()
	if asset.contentType != "" {
		header.Set("Content-Type", asset.contentType)
	}
	header.Set("Etag", asset.etag)
	header.Add("Vary", "Accept-Encoding")
	if cacheControl != "" {
		header.Set("Cache-Control", cacheControl)
	}

	if asset.gzipData != nil && acceptsGzip(r) {
		// Range plus Content-Encoding is a can of worms no client here
		// actually needs for these asset sizes, so the gzip path skips
		// http.ServeContent's Range support entirely and is written
		// directly. It still needs to honor conditional requests itself,
		// since ServeContent isn't the one doing that in this branch.
		if notModified(r, asset) {
			w.WriteHeader(http.StatusNotModified)
			return true
		}
		header.Set("Content-Encoding", "gzip")
		header.Set("Content-Length", strconv.Itoa(len(asset.gzipData)))
		w.WriteHeader(http.StatusOK)
		if r.Method != http.MethodHead {
			_, _ = w.Write(asset.gzipData)
		}
		return true
	}

	// http.ServeContent already checks If-None-Match against the Etag
	// header we just set (and If-Modified-Since against modtime), and
	// transparently handles Range requests and HEAD -- all for free.
	http.ServeContent(w, r, diskPath, asset.modTime, bytes.NewReader(asset.data))
	return true
}

func acceptsGzip(r *http.Request) bool {
	for _, enc := range strings.Split(r.Header.Get("Accept-Encoding"), ",") {
		if strings.TrimSpace(enc) == "gzip" {
			return true
		}
	}
	return false
}

func notModified(r *http.Request, asset *cachedAsset) bool {
	if inm := r.Header.Get("If-None-Match"); inm != "" {
		return inm == asset.etag
	}
	if ims := r.Header.Get("If-Modified-Since"); ims != "" {
		if t, err := time.Parse(http.TimeFormat, ims); err == nil {
			return !asset.modTime.After(t.Add(time.Second))
		}
	}
	return false
}
