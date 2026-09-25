// cache.go implements an in-memory, size-bounded cache of the static
// files this process serves directly (the app's static_dir, and
// Nexoria's own runtime assets under /_nexoria/). A cache hit means
// every request after the first is answered straight from memory --
// no disk read, and, when the client's Accept-Encoding allows it,
// from an already-gzipped copy instead of compressing on every
// request.
//
// Correctness over raw speed: every Load still calls os.Stat first.
// A hit requires the file's size *and* modification time on disk to
// still match what's cached -- so editing a static file during
// development is picked up on the very next request, with no server
// restart or manual invalidation needed. Eviction is plain LRU against
// a caller-supplied total byte budget (-cache-max-bytes), so one
// pathologically large app doesn't grow this without bound.
package main

import (
	"bytes"
	"compress/gzip"
	"container/list"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"mime"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// minCompressibleSize is the smallest response worth gzipping -- below
// this, gzip's own header/framing overhead can exceed what it saves,
// and every byte "saved" costs a CPU cycle better spent elsewhere.
const minCompressibleSize = 1024

// maxCacheableFileSize is a per-file ceiling on what this cache will
// hold in memory at all. A file above this is still served correctly
// (read straight off disk on every request, same as before this
// cache existed), just not double-buffered in RAM -- keeps one huge
// asset from blowing the whole cache's byte budget by itself.
const maxCacheableFileSize = 32 << 20 // 32 MiB

type cachedAsset struct {
	path        string
	data        []byte
	gzipData    []byte // nil if not compressible, or compressing wasn't worth it
	etag        string
	modTime     time.Time
	size        int64
	contentType string
}

func (a *cachedAsset) memBytes() int64 {
	return int64(len(a.data) + len(a.gzipData))
}

// AssetCache is an LRU, byte-budgeted cache of file contents keyed by
// absolute path. Safe for concurrent use.
type AssetCache struct {
	mu       sync.Mutex
	maxBytes int64
	curBytes int64
	entries  map[string]*list.Element // path -> element (Value is *cachedAsset)
	lru      *list.List               // front = most recently used

	hits   int64
	misses int64
}

func NewAssetCache(maxBytes int64) *AssetCache {
	return &AssetCache{
		maxBytes: maxBytes,
		entries:  make(map[string]*list.Element),
		lru:      list.New(),
	}
}

// Load returns the cached asset for path, reading (and, if worthwhile,
// gzip-compressing) it from disk on a cache miss or a stale entry. Any
// os.Stat/os.ReadFile error (including a missing file) is returned
// unchanged so callers can 404/fall through appropriately.
func (c *AssetCache) Load(path string) (*cachedAsset, error) {
	info, err := os.Stat(path)
	if err != nil {
		return nil, err
	}
	if info.IsDir() {
		return nil, fmt.Errorf("%s is a directory", path)
	}

	c.mu.Lock()
	if el, ok := c.entries[path]; ok {
		asset := el.Value.(*cachedAsset)
		if asset.modTime.Equal(info.ModTime()) && asset.size == info.Size() {
			c.lru.MoveToFront(el)
			c.mu.Unlock()
			atomic.AddInt64(&c.hits, 1)
			return asset, nil
		}
		// Stale -- the file changed since we cached it. Drop the old
		// entry now; the reload below will re-insert it fresh.
		c.removeLocked(el)
	}
	c.mu.Unlock()
	atomic.AddInt64(&c.misses, 1)

	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	// Re-stat after reading: if the file was mid-write when the first
	// os.Stat ran, caching against that stale size/mtime pair could
	// wedge the staleness check above (content keeps changing, but
	// happens to match a size we already recorded) until the file
	// changes size too. Stat-after-read closes that window.
	info2, err := os.Stat(path)
	if err != nil {
		return nil, err
	}

	ct := contentTypeFor(path)
	asset := &cachedAsset{
		path:        path,
		data:        data,
		etag:        computeETag(data),
		modTime:     info2.ModTime(),
		size:        info2.Size(),
		contentType: ct,
	}
	if info2.Size() <= maxCacheableFileSize && len(data) >= minCompressibleSize && isCompressible(ct) {
		if gz, ok := gzipCompress(data); ok {
			asset.gzipData = gz
		}
	}

	if info2.Size() <= maxCacheableFileSize {
		c.mu.Lock()
		el := c.lru.PushFront(asset)
		c.entries[path] = el
		c.curBytes += asset.memBytes()
		c.evictLocked()
		c.mu.Unlock()
	}
	return asset, nil
}

func (c *AssetCache) removeLocked(el *list.Element) {
	asset := el.Value.(*cachedAsset)
	c.curBytes -= asset.memBytes()
	c.lru.Remove(el)
	delete(c.entries, asset.path)
}

func (c *AssetCache) evictLocked() {
	for c.curBytes > c.maxBytes {
		back := c.lru.Back()
		if back == nil {
			return
		}
		c.removeLocked(back)
	}
}

// CacheStats is a point-in-time snapshot, surfaced on
// /_nexoria/native-health so cache behavior is visible from outside
// the process without attaching a profiler.
type CacheStats struct {
	Entries  int   `json:"entries"`
	Bytes    int64 `json:"bytes"`
	MaxBytes int64 `json:"max_bytes"`
	Hits     int64 `json:"hits"`
	Misses   int64 `json:"misses"`
}

func (c *AssetCache) Stats() CacheStats {
	c.mu.Lock()
	defer c.mu.Unlock()
	return CacheStats{
		Entries:  len(c.entries),
		Bytes:    c.curBytes,
		MaxBytes: c.maxBytes,
		Hits:     atomic.LoadInt64(&c.hits),
		Misses:   atomic.LoadInt64(&c.misses),
	}
}

func computeETag(data []byte) string {
	sum := sha256.Sum256(data)
	// A short, quoted strong validator (RFC 7232) -- full sha256 hex
	// would work too, but 16 hex chars (64 bits) is already far more
	// collision-resistant than this needs and keeps the header small.
	return `"` + hex.EncodeToString(sum[:])[:16] + `"`
}

func gzipCompress(data []byte) ([]byte, bool) {
	var buf bytes.Buffer
	zw, err := gzip.NewWriterLevel(&buf, gzip.BestCompression)
	if err != nil {
		return nil, false
	}
	if _, err := zw.Write(data); err != nil {
		_ = zw.Close()
		return nil, false
	}
	if err := zw.Close(); err != nil {
		return nil, false
	}
	// Only worth keeping the gzip copy around if it actually shrank the
	// asset meaningfully -- some already-dense content barely compresses.
	if buf.Len() >= len(data) {
		return nil, false
	}
	return buf.Bytes(), true
}

func isCompressible(contentType string) bool {
	if contentType == "" {
		return false
	}
	switch {
	case strings.HasPrefix(contentType, "text/"):
		return true
	case strings.Contains(contentType, "javascript"),
		strings.Contains(contentType, "json"),
		strings.Contains(contentType, "svg"),
		strings.Contains(contentType, "xml"):
		return true
	default:
		return false
	}
}

func contentTypeFor(path string) string {
	if ct := contentTypeForExt(filepath.Ext(path)); ct != "" {
		return ct
	}
	if ct := mime.TypeByExtension(filepath.Ext(path)); ct != "" {
		return ct
	}
	return ""
}

// contentTypeForExt covers the handful of extensions Nexoria's own
// runtime ships (plus common static-asset types) explicitly, rather
// than relying only on the host OS's mime database -- which is
// sometimes missing entries (older/minimal Linux images notably don't
// always know .js is application/javascript) and would otherwise fall
// through to Go's application/octet-stream default and break script
// execution in the browser.
func contentTypeForExt(ext string) string {
	switch strings.ToLower(ext) {
	case ".js", ".mjs":
		return "application/javascript; charset=utf-8"
	case ".css":
		return "text/css; charset=utf-8"
	case ".svg":
		return "image/svg+xml"
	case ".ico":
		return "image/x-icon"
	case ".png":
		return "image/png"
	case ".json":
		return "application/json; charset=utf-8"
	case ".html", ".htm":
		return "text/html; charset=utf-8"
	case ".woff2":
		return "font/woff2"
	case ".woff":
		return "font/woff"
	default:
		return ""
	}
}
