# `nexoria.translate`

> Server-side Google Translate in pure Python (unofficial endpoint).

| | |
|---|---|
| **Import** | `from nexoria.translate import translate, Translation` |
| **Enabled by** | Nothing — plain Python, no `App` flag, no client adapter |
| **Network** | HTTPS POST to `translate.google.com/translate_a/single` via `urllib` |

```python
from nexoria.translate import translate
r = translate("Hello, how are you?", to="es")
print(r.text, r.source_language)        # translated text, detected source language
```

`translate(text, to="en", source="auto", host="translate.google.com", timeout=10.0)` returns `Translation(text, source_language, raw)`. HTTP/URL errors are re-raised as `RuntimeError`.

**Read this first.** It calls the same **unofficial, undocumented** endpoint Google's own web UI uses, mirroring the request format of the npm package `@vitalets/google-translate-api`. It is not the paid Cloud Translation API, has no uptime or rate-limit guarantees, and may change or block without notice — use the official API for anything production-critical. The request shape was verified against that library's source rather than a live round-trip.

## API reference

### Classes

#### `class Translation(text: str, source_language: str, raw: dict) -> None`

Translation(text: 'str', source_language: 'str', raw: 'dict')

### Functions

#### `translate(text: str, to: str = 'en', source: str = 'auto', host: str = 'translate.google.com', timeout: float = 10.0) -> Translation`

Translate `text` to the `to` language code (e.g. "es", "fr", "ja"). `source` defaults to "auto" (detect). Returns a `Translation` with `.text` (the translated string) and `.raw` (the full parsed response, including detected source language and alternatives, for anything beyond the plain text).
