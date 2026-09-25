"""
nexoria.translate.google
===========================
Translation via Google's public (unofficial) translate endpoint --
the SAME endpoint and request format used by the npm package
`@vitalets/google-translate-api`, reimplemented directly in pure
Python rather than run through a JS engine.

This is a deliberate departure from Nexoria's other integrations: the
npm package this is based on is fundamentally a *server-side* Node.js
library (it depends on `node-fetch` and makes HTTP calls -- it has no
browser build, no DOM interaction, nothing a client-side adapter could
run). Since Nexoria's backend is already Python, routing this through
our embedded JS engine (which has no networking capability by design --
see nexoria.native.js's docstring) would add complexity for no benefit
over calling the same endpoint directly from Python. The request
format below (URL, query params, POST body, response shape) was copied
directly from the real, current version of
`@vitalets/google-translate-api`'s own source, not guessed or
independently reverse-engineered.

Honest caveat: this hits an unofficial, undocumented Google endpoint
(the same one Google Translate's own web UI uses) -- it is not the
official, paid Google Cloud Translation API, has no uptime/rate-limit
guarantees, and could change or start blocking traffic without notice.
For anything production-critical, use the official Cloud Translation
API instead. Also: this sandbox's own network egress allowlist blocks
translate.google.com, so this could not be tested against the live
endpoint during development -- the implementation is verified against
the real library's source code, not a live round-trip.
"""

from __future__ import annotations
import json
import urllib.request
import urllib.parse
import urllib.error
from dataclasses import dataclass


@dataclass
class Translation:
    text: str
    source_language: str
    raw: dict


def translate(text: str, to: str = "en", source: str = "auto", host: str = "translate.google.com", timeout: float = 10.0) -> Translation:
    """
    Translate `text` to the `to` language code (e.g. "es", "fr", "ja").
    `source` defaults to "auto" (detect). Returns a `Translation` with
    `.text` (the translated string) and `.raw` (the full parsed
    response, including detected source language and alternatives, for
    anything beyond the plain text).

        result = translate("Hello, how are you?", to="es")
        print(result.text)  # "Hola, ¿cómo estás?"
    """
    url = f"https://{host}/translate_a/single?client=at&dt=t&dt=rm&dj=1"
    body = urllib.parse.urlencode({"sl": source, "tl": to, "q": text}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = json.load(resp)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Google Translate request failed: HTTP {e.code} {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Google Translate request failed: {e.reason}") from e

    sentences = raw.get("sentences", [])
    translated = "".join(s["trans"] for s in sentences if "trans" in s)
    detected_source = raw.get("src", source)
    return Translation(text=translated, source_language=detected_source, raw=raw)
