# Canon entry schema

One JSON object per line in `corpus/quotes.jsonl`.

## Required fields

| Field | Type | Notes |
|---|---|---|
| `id` | string | `q-<slug>`, unique, lowercase |
| `text` | string | The line itself, verbatim where possible |
| `claimed_attribution` | string | What the popular attribution says (may equal verified) |
| `verified_attribution` | string | What the evidence supports, with entity/work/date |
| `source` | object | `{type, work, locator}` — see below |
| `provenance` | enum | `VERIFIED` \| `COMMON-ATTRIB` \| `MISATTRIBUTED` \| `UNVERIFIED` |

## Optional fields

| Field | Type | Notes |
|---|---|---|
| `context` | string | Why the line lands; the scene/passage that gives it weight |
| `themes` | string[] | Freeform tags (e.g. `hubris`, `systems`, `responsibility`) |
| `hummbl` | string[] | Base120 transformation tags (`P`,`IN`,`CO`,`DE`,`RE`,`SY`) |
| `receipts` | object[] | `{type, ref}` — evidence links/citations. **Required non-empty for `VERIFIED` and `MISATTRIBUTED`** |
| `notes` | string | Anything else load-bearing |

## `source` object

- `type`: `film` \| `book` \| `speech` \| `paper` \| `article` \| `letter` \| `interview` \| `other`
- `work`: the containing work (title, year)
- `locator`: where in the work (scene, chapter, page, timestamp, citation)

## Provenance ladder

- `VERIFIED` — primary or strong secondary evidence the named party said/wrote the line
- `COMMON-ATTRIB` — plausible traditional attribution without conclusive evidence (e.g., ancient quotes relayed by later authors)
- `MISATTRIBUTED` — the popular attribution is demonstrably wrong; `verified_attribution` names the actual origin
- `UNVERIFIED` — claimed but not yet checked (valid state; an entry may live here until receipts arrive)

---

# Resonance entry schema

One JSON object per line in `resonance/*.jsonl` (gitignored — local-first by design).

The resonance log answers a different question than the corpus: not "who really said this" but "when did this line land for the reader, and why." Entries are never published to the shared corpus.

## Required fields

| Field | Type | Notes |
|---|---|---|
| `ts` | string | ISO-8601 timestamp of the capture moment (`2026-09-26T08:15:00Z`) |
| anchor | — | exactly one of `quote_id` (corpus id; must resolve) **or** `text` (uncaptured line) |

## Optional fields

| Field | Type | Notes |
|---|---|---|
| `surface` | string | Where it came from — video, book, conversation, PR review |
| `note` | string | Why it landed *then* — the point of the record |
| `themes` | string[] | Freeform tags; over time this indexes the reader's own canon |

## Anchor rule

- `quote_id` **must** resolve to an id in `corpus/quotes.jsonl` — a dangling anchor is a validation error, not a soft reference
- `text` is the escape hatch for lines that hit before they're captured in the corpus; those entries are candidates for later corpus ingestion
- Never both fields on one entry — pick one anchor form

Validated by `scripts/validate_resonance.py` (local only; the files are gitignored).
