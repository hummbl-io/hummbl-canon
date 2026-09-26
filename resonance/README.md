# Resonance log

The personal canon: lines that actually landed for *you*, with when and why.

## Format

`resonance/*.jsonl` — one JSON object per line, gitignored by default (see root `.gitignore`). Suggested shape:

```json
{"ts": "2026-09-26T08:15:00Z", "quote_id": "q-otto-octavius-intelligence", "surface": "youtube/@apollomotivationn", "note": "context made it land — the irony attached", "themes": ["irony", "hubris"]}
```

Fields:
- `ts` — when it hit
- `quote_id` — corpus id (or a freeform `text` field if the line isn't in the corpus yet)
- `surface` — where it came from (video, book, conversation, PR review)
- `note` — why it landed *then*
- `themes` — optional; over time this becomes the index of your own canon

This is local-first by design. The corpus is shareable; the resonance log is the reader's.
