// firewall.go adds a native request firewall in front of everything
// else this server does -- routing, static serving, and the reverse
// proxy to the Python backend all sit *behind* it. It exists because
// this process is meant to be the actual internet-facing edge (see
// the doc comment in main.go): unlike the Python ASGI backend, which
// nexoria.core.app.App always keeps on loopback only, this binary is
// the one thing in the stack that might reasonably be handed a public
// listen address, so it's also the one thing in the stack that needs
// its own first line of defense rather than assuming an external
// reverse proxy or cloud load balancer is always doing that job.
//
// Four independent checks run, cheapest-and-most-decisive first, so a
// request that's going to be blocked is blocked before any of the
// more expensive routing/proxying/compression work downstream ever
// runs:
//
//  1. deny list        -- IP/CIDR always blocked, no exceptions
//  2. allow list        -- if non-empty, ONLY these IP/CIDRs may pass
//  3. per-IP rate limit -- token bucket, one bucket per client IP
//  4. request sanity     -- disallowed HTTP methods, oversized request
//                           lines, and raw path-traversal/NUL-byte
//                           probes that have no legitimate reason to
//                           appear in a URL this server would ever
//                           generate itself
//
// A request body size cap (MaxBodyBytes, via http.MaxBytesReader) is
// applied last, wrapping the body for every request that got this far
// -- it can't reject before reading, only bound how much any single
// handler downstream is allowed to read.
//
// None of this is wrapped around http.ResponseWriter the way the
// gzip/logging middleware in middleware.go is: withFirewall only ever
// calls next.ServeHTTP(w, r) unchanged for an allowed request, or
// writes a short error response itself and returns for a blocked one
// -- so it can sit safely in front of the reverse proxy's WebSocket
// upgrade handling (see the file-level comment in middleware.go)
// without needing its own Hijack/Flush passthrough at all.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// -- configuration --------------------------------------------------

// FirewallConfig is built once from CLI flags at startup (see
// registerFirewallFlags/newFirewallFromFlags below) and never mutated
// afterward -- Firewall itself only carries the mutable runtime state
// (rate-limiter buckets, counters) that config doesn't cover.
type FirewallConfig struct {
	Enabled bool

	AllowCIDRs []*net.IPNet // if non-empty, only these may pass (checked after DenyCIDRs)
	DenyCIDRs  []*net.IPNet // always blocked, regardless of AllowCIDRs

	// TrustXForwardedFor: when true, the left-most address in a
	// request's X-Forwarded-For header is used as the client IP
	// instead of RemoteAddr, for allow/deny/rate-limit decisions.
	// Default false: RemoteAddr is the only address a client can't
	// forge by simply sending a header, so it's the only one safe to
	// trust by default. Only enable this when nexoria-server sits
	// behind a reverse proxy/load balancer you control that
	// overwrites (never appends blindly to) that header itself.
	TrustXForwardedFor bool

	RateLimitPerSecond float64 // 0 disables rate limiting entirely
	RateLimitBurst     int     // token bucket capacity; must be >= 1 if RateLimitPerSecond > 0

	MaxBodyBytes int64 // 0 disables the body-size cap

	// BlockedMethods are rejected outright with 405 before any
	// routing happens. TRACE/CONNECT/TRACK have no legitimate use for
	// an app server like this and are historically associated with
	// cross-protocol/XST-style probing, so they're blocked by default;
	// callers who genuinely need one can pass an empty list to allow
	// everything through to the mux's own method handling instead.
	BlockedMethods map[string]bool
}

func defaultBlockedMethods() map[string]bool {
	return map[string]bool{
		http.MethodTrace:   true,
		http.MethodConnect: true,
		"TRACK":            true, // non-standard, IIS-era method with the same history as TRACE
	}
}

// registerFirewallFlags wires the firewall's own CLI flags into the
// same flag.FlagSet main() already uses, following the exact naming/
// help-text conventions of the flags already registered there. Called
// from main() before flag.Parse(), so these show up in -h/--help
// alongside everything else rather than needing a separate flag set.
func registerFirewallFlags() *firewallFlagValues {
	v := &firewallFlagValues{}
	flag.BoolVar(&v.enabled, "firewall", true,
		"enable the built-in request firewall (IP allow/deny lists, per-IP rate limiting, request sanity checks)")
	flag.StringVar(&v.allow, "firewall-allow", "",
		"comma-separated IPs/CIDRs; if non-empty, ONLY these may reach the server (e.g. \"10.0.0.0/8,192.168.1.50\")")
	flag.StringVar(&v.deny, "firewall-deny", "",
		"comma-separated IPs/CIDRs to always block, regardless of -firewall-allow")
	flag.Float64Var(&v.rateLimit, "firewall-rate-limit", 20,
		"max sustained requests per second, per client IP; 0 disables rate limiting")
	flag.IntVar(&v.rateBurst, "firewall-rate-burst", 40,
		"token-bucket burst capacity, per client IP (allows short spikes above -firewall-rate-limit)")
	flag.Int64Var(&v.maxBodyBytes, "firewall-max-body-bytes", 10<<20,
		"reject request bodies larger than this many bytes (0 disables the cap)")
	flag.BoolVar(&v.trustXFF, "firewall-trust-x-forwarded-for", false,
		"use the left-most X-Forwarded-For address as the client IP instead of the TCP peer address -- ONLY enable this behind a reverse proxy you control that overwrites the header itself")
	return v
}

// firewallFlagValues holds the raw flag destinations; parseFirewallConfig
// turns them into a validated FirewallConfig after flag.Parse() runs.
type firewallFlagValues struct {
	enabled      bool
	allow        string
	deny         string
	rateLimit    float64
	rateBurst    int
	maxBodyBytes int64
	trustXFF     bool
}

func parseFirewallConfig(v *firewallFlagValues) (*FirewallConfig, error) {
	allowCIDRs, err := parseCIDRList(v.allow)
	if err != nil {
		return nil, fmt.Errorf("-firewall-allow: %w", err)
	}
	denyCIDRs, err := parseCIDRList(v.deny)
	if err != nil {
		return nil, fmt.Errorf("-firewall-deny: %w", err)
	}
	if v.rateLimit > 0 && v.rateBurst < 1 {
		return nil, fmt.Errorf("-firewall-rate-burst must be >= 1 when -firewall-rate-limit > 0 (got %d)", v.rateBurst)
	}
	return &FirewallConfig{
		Enabled:            v.enabled,
		AllowCIDRs:         allowCIDRs,
		DenyCIDRs:          denyCIDRs,
		TrustXForwardedFor: v.trustXFF,
		RateLimitPerSecond: v.rateLimit,
		RateLimitBurst:     v.rateBurst,
		MaxBodyBytes:       v.maxBodyBytes,
		BlockedMethods:     defaultBlockedMethods(),
	}, nil
}

// parseCIDRList accepts a comma-separated list of bare IPs (treated as
// a /32 or /128) and CIDR ranges, e.g. "10.0.0.0/8, 192.168.1.50,
// ::1/128". Empty/whitespace-only entries are skipped so a trailing
// comma or extra spaces from a config file don't turn into an error.
func parseCIDRList(raw string) ([]*net.IPNet, error) {
	var nets []*net.IPNet
	for _, part := range strings.Split(raw, ",") {
		part = strings.TrimSpace(part)
		if part == "" {
			continue
		}
		if !strings.Contains(part, "/") {
			ip := net.ParseIP(part)
			if ip == nil {
				return nil, fmt.Errorf("invalid IP or CIDR: %q", part)
			}
			bits := 32
			if ip.To4() == nil {
				bits = 128
			}
			part = fmt.Sprintf("%s/%d", part, bits)
		}
		_, ipNet, err := net.ParseCIDR(part)
		if err != nil {
			return nil, fmt.Errorf("invalid IP or CIDR: %q: %w", part, err)
		}
		nets = append(nets, ipNet)
	}
	return nets, nil
}

// -- token-bucket rate limiter ---------------------------------------

// tokenBucket is a minimal, mutex-protected token bucket -- no
// external dependency needed for something this small. Tokens refill
// continuously at ratePerSecond (fractional refill computed from
// elapsed wall-clock time on each Allow() call, not a background
// ticker), capped at burst.
type tokenBucket struct {
	mu         sync.Mutex
	tokens     float64
	ratePerSec float64
	burst      float64
	lastRefill time.Time
	lastSeen   time.Time // for cleanupStaleBuckets; separate from lastRefill for clarity even though they're updated together
}

func newTokenBucket(ratePerSec float64, burst int) *tokenBucket {
	now := time.Now()
	return &tokenBucket{
		tokens:     float64(burst), // start full: a client's first requests shouldn't be penalized for the server having just started
		ratePerSec: ratePerSec,
		burst:      float64(burst),
		lastRefill: now,
		lastSeen:   now,
	}
}

// allow reports whether one request may proceed right now, consuming
// one token if so.
func (b *tokenBucket) allow() bool {
	b.mu.Lock()
	defer b.mu.Unlock()
	now := time.Now()
	elapsed := now.Sub(b.lastRefill).Seconds()
	b.lastRefill = now
	b.lastSeen = now
	b.tokens += elapsed * b.ratePerSec
	if b.tokens > b.burst {
		b.tokens = b.burst
	}
	if b.tokens < 1 {
		return false
	}
	b.tokens--
	return true
}

func (b *tokenBucket) idleSince() time.Duration {
	b.mu.Lock()
	defer b.mu.Unlock()
	return time.Since(b.lastSeen)
}

// -- firewall ---------------------------------------------------------

// FirewallStats is a point-in-time snapshot, surfaced on
// /_nexoria/native-health alongside AssetCache's own stats (see
// health.go) so the firewall's behavior is visible from outside the
// process without attaching a profiler -- the same reasoning
// CacheStats already documents for the asset cache.
type FirewallStats struct {
	Enabled           bool  `json:"enabled"`
	AllowedRequests   int64 `json:"allowed_requests"`
	DeniedByList      int64 `json:"denied_by_ip_list"`
	DeniedByRateLimit int64 `json:"denied_by_rate_limit"`
	DeniedByMethod    int64 `json:"denied_by_method"`
	DeniedBySanity    int64 `json:"denied_by_request_sanity"`
	TrackedClientIPs  int   `json:"tracked_client_ips"`
}

type Firewall struct {
	cfg *FirewallConfig

	bucketsMu sync.Mutex
	buckets   map[string]*tokenBucket

	allowed           int64
	deniedByList      int64
	deniedByRateLimit int64
	deniedByMethod    int64
	deniedBySanity    int64
}

func NewFirewall(cfg *FirewallConfig) *Firewall {
	fw := &Firewall{
		cfg:     cfg,
		buckets: make(map[string]*tokenBucket),
	}
	if cfg.Enabled && cfg.RateLimitPerSecond > 0 {
		go fw.cleanupStaleBucketsLoop()
	}
	return fw
}

// cleanupStaleBucketsLoop periodically evicts buckets for client IPs
// that haven't made a request in a while, so a long-running server
// facing many distinct/spoofed source IPs doesn't grow this map
// without bound -- the same unbounded-growth concern AssetCache's own
// byte-budgeted eviction addresses for cached files, just on a timer
// instead of LRU-on-access, since "haven't seen this IP in 10
// minutes" is a more natural staleness signal than "least recently
// used" for a per-client rate-limit bucket.
func (f *Firewall) cleanupStaleBucketsLoop() {
	const interval = 5 * time.Minute
	const staleAfter = 10 * time.Minute
	ticker := time.NewTicker(interval)
	defer ticker.Stop()
	for range ticker.C {
		f.bucketsMu.Lock()
		for ip, b := range f.buckets {
			if b.idleSince() > staleAfter {
				delete(f.buckets, ip)
			}
		}
		f.bucketsMu.Unlock()
	}
}

func (f *Firewall) Stats() FirewallStats {
	f.bucketsMu.Lock()
	tracked := len(f.buckets)
	f.bucketsMu.Unlock()
	return FirewallStats{
		Enabled:           f.cfg.Enabled,
		AllowedRequests:   atomic.LoadInt64(&f.allowed),
		DeniedByList:      atomic.LoadInt64(&f.deniedByList),
		DeniedByRateLimit: atomic.LoadInt64(&f.deniedByRateLimit),
		DeniedByMethod:    atomic.LoadInt64(&f.deniedByMethod),
		DeniedBySanity:    atomic.LoadInt64(&f.deniedBySanity),
		TrackedClientIPs:  tracked,
	}
}

// clientIP extracts the address the firewall should judge this
// request by: RemoteAddr's IP by default, or (only when explicitly
// opted into via -firewall-trust-x-forwarded-for) the left-most
// address in X-Forwarded-For, which is the conventional "original
// client" position in that header when it's only ever appended to by
// trusted intermediaries -- never trust it against an unknown/direct
// internet, since any client can set that header to anything.
func (f *Firewall) clientIP(r *http.Request) string {
	if f.cfg.TrustXForwardedFor {
		if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
			first := strings.TrimSpace(strings.Split(xff, ",")[0])
			if first != "" {
				return first
			}
		}
	}
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr // RemoteAddr had no port for some reason; use it verbatim rather than dropping the request's identity entirely
	}
	return host
}

func ipInAny(ip net.IP, nets []*net.IPNet) bool {
	for _, n := range nets {
		if n.Contains(ip) {
			return true
		}
	}
	return false
}

// checkIPLists applies the deny-then-allow decision described in the
// file-level doc comment. Returns ("", true) if the request may
// proceed, or (reason, false) if it must be blocked.
func (f *Firewall) checkIPLists(ipStr string) (reason string, ok bool) {
	ip := net.ParseIP(ipStr)
	if ip == nil {
		// An unparseable client address (shouldn't normally happen --
		// clientIP() only strips a port off a real RemoteAddr) is
		// treated as untrusted rather than silently exempted from
		// both lists.
		return "unrecognized client address", false
	}
	if ipInAny(ip, f.cfg.DenyCIDRs) {
		return "denied by IP block list", false
	}
	if len(f.cfg.AllowCIDRs) > 0 && !ipInAny(ip, f.cfg.AllowCIDRs) {
		return "not on IP allow list", false
	}
	return "", true
}

// checkRateLimit reports whether ipStr may make one more request right
// now, lazily creating that IP's token bucket on first sight.
func (f *Firewall) checkRateLimit(ipStr string) bool {
	if f.cfg.RateLimitPerSecond <= 0 {
		return true
	}
	f.bucketsMu.Lock()
	b, ok := f.buckets[ipStr]
	if !ok {
		b = newTokenBucket(f.cfg.RateLimitPerSecond, f.cfg.RateLimitBurst)
		f.buckets[ipStr] = b
	}
	f.bucketsMu.Unlock()
	return b.allow()
}

// checkRequestSanity rejects a small set of request shapes that have
// no legitimate reason to reach this server and are commonly seen in
// automated scanning/exploit probing: raw ".." path-traversal
// segments or NUL bytes in the request URI (net/http's own routing
// and Go's path/filepath handling already neutralize these for
// Nexoria's own handlers -- see the filepath.Clean/filepath.Base use
// in main.go -- but rejecting them outright here means they never
// even reach those code paths, or get proxied through to the Python
// backend, in the first place), and unreasonably long request lines
// (a cheap, early defense against some classes of buffer/parsing
// abuse in code further down the stack, well below what any real
// Nexoria route/asset path would ever need).
func (f *Firewall) checkRequestSanity(r *http.Request) (reason string, ok bool) {
	const maxURILength = 8192
	if len(r.RequestURI) > maxURILength {
		return "request URI too long", false
	}
	if strings.Contains(r.URL.Path, "\x00") {
		return "NUL byte in request path", false
	}
	if strings.Contains(r.URL.Path, "..") {
		return "path traversal sequence in request path", false
	}
	return "", true
}

// withFirewall wraps next with every check described in the file-level
// doc comment, in order, short-circuiting on the first one that fails.
// If cfg.Enabled is false, this returns next completely unwrapped --
// running a firewall that unconditionally does nothing on every
// request would just be wasted work.
func withFirewall(next http.Handler, f *Firewall) http.Handler {
	if !f.cfg.Enabled {
		return next
	}
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ip := f.clientIP(r)

		if reason, ok := f.checkIPLists(ip); !ok {
			atomic.AddInt64(&f.deniedByList, 1)
			log.Printf("nexoria-server: firewall: blocked %s %s from %s (%s)", r.Method, r.URL.Path, ip, reason)
			http.Error(w, "403 Forbidden", http.StatusForbidden)
			return
		}

		if f.cfg.BlockedMethods[r.Method] {
			atomic.AddInt64(&f.deniedByMethod, 1)
			log.Printf("nexoria-server: firewall: blocked %s %s from %s (method not allowed)", r.Method, r.URL.Path, ip)
			http.Error(w, "405 Method Not Allowed", http.StatusMethodNotAllowed)
			return
		}

		if reason, ok := f.checkRequestSanity(r); !ok {
			atomic.AddInt64(&f.deniedBySanity, 1)
			log.Printf("nexoria-server: firewall: blocked %s %s from %s (%s)", r.Method, r.URL.Path, ip, reason)
			http.Error(w, "400 Bad Request", http.StatusBadRequest)
			return
		}

		if !f.checkRateLimit(ip) {
			atomic.AddInt64(&f.deniedByRateLimit, 1)
			w.Header().Set("Retry-After", "1")
			log.Printf("nexoria-server: firewall: rate-limited %s %s from %s", r.Method, r.URL.Path, ip)
			http.Error(w, "429 Too Many Requests", http.StatusTooManyRequests)
			return
		}

		if f.cfg.MaxBodyBytes > 0 && r.Body != nil {
			r.Body = http.MaxBytesReader(w, r.Body, f.cfg.MaxBodyBytes)
		}

		atomic.AddInt64(&f.allowed, 1)
		next.ServeHTTP(w, r)
	})
}

// firewallStatusHandler answers GET /_nexoria/firewall-status with the
// current FirewallStats as JSON -- a separate, purely-local endpoint
// (same reasoning as /_nexoria/native-health in health.go) so infra
// can watch the firewall's own counters without them being folded
// into, and potentially cluttering, the general health payload.
func firewallStatusHandler(f *Firewall) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		w.Header().Set("Cache-Control", "no-store")
		_ = json.NewEncoder(w).Encode(f.Stats())
	}
}

// formatBool mirrors the human-readable on/off strings used in
// startup log lines elsewhere in this package (see the "ready,
// listening on" line in main.go), kept here since it's only ever used
// to describe the firewall's own enabled state at startup.
func formatBool(b bool) string {
	if b {
		return "on"
	}
	return "off"
}

// startupSummary is logged once at startup so an operator can see the
// effective firewall configuration (after CIDR parsing/validation)
// without having to re-derive it from raw flag strings.
func (f *Firewall) startupSummary() string {
	if !f.cfg.Enabled {
		return "firewall: disabled"
	}
	rate := "unlimited"
	if f.cfg.RateLimitPerSecond > 0 {
		rate = strconv.FormatFloat(f.cfg.RateLimitPerSecond, 'g', -1, 64) + " req/s/IP (burst " + strconv.Itoa(f.cfg.RateLimitBurst) + ")"
	}
	return fmt.Sprintf(
		"firewall: enabled (allow-list %s, deny-list %d entries, rate-limit %s, trust-x-forwarded-for %s, max-body-bytes %d)",
		func() string {
			if len(f.cfg.AllowCIDRs) == 0 {
				return "disabled (all IPs permitted unless denied)"
			}
			return strconv.Itoa(len(f.cfg.AllowCIDRs)) + " entries"
		}(),
		len(f.cfg.DenyCIDRs),
		rate,
		formatBool(f.cfg.TrustXForwardedFor),
		f.cfg.MaxBodyBytes,
	)
}
