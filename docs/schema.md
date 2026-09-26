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
