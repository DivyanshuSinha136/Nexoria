// health.go adds /_nexoria/native-health: a health check answered by
// this process alone, with no round trip to the Python backend. The
// existing /_nexoria/health stays exactly as it was (proxied straight
// through, since only the backend can attest to its own health); this
// is a second, separate endpoint -- useful to an infra/load-balancer
// probe that wants to check the edge tier itself is up and serving,
// independently of whatever the backend is doing.
package main

import (
	"encoding/json"
	"net/http"
	"time"
)

var serverStart = time.Now()

type nativeHealthResponse struct {
	Status   string        `json:"status"`
	Server   string        `json:"server"`
	Uptime   string        `json:"uptime"`
	Cache    CacheStats    `json:"cache"`
	Firewall FirewallStats `json:"firewall"`
}

func nativeHealthHandler(cache *AssetCache, name string, firewall *Firewall) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		resp := nativeHealthResponse{
			Status:   "ok",
			Server:   name,
			Uptime:   time.Since(serverStart).Round(time.Second).String(),
			Cache:    cache.Stats(),
			Firewall: firewall.Stats(),
		}
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		w.Header().Set("Cache-Control", "no-store")
		_ = json.NewEncoder(w).Encode(resp)
	}
}
