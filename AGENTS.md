# AGENTS.md — hummbl-canon

## Project
**hummbl-canon** — a provenance-first corpus of quotable lines for the HUMMBL agent fleet, plus a local-first personal resonance layer. Python 3.11+ stdlib only; JSONL canonical format; MIT.

## Scope
- In scope: `corpus/quotes.jsonl` (the substrate), `scripts/` validators, `docs/schema.md`, `resonance/` conventions
- Out of scope: runtime quote delivery services, the resonance log's personal data (local by design), bibliography curation (lives in `hummbl-bibliography`)

## Layout
- `corpus/quotes.jsonl` — canonical entries, one JSON object per line
- `scripts/validate_corpus.py` — schema + provenance validator (stdlib only)
- `docs/schema.md` — field spec
- `resonance/` — personal log convention; `*.jsonl` files are gitignored

## Testing
```bash
python scripts/validate_corpus.py            # validate corpus
python scripts/validate_corpus.py --stats    # stats
python scripts/quote.py --list               # all anchors
python scripts/quote.py <q-id>               # resolve one
python scripts/validate_resonance.py         # validate local resonance logs (files gitignored)
```

## Conventions
- JSONL is canonical; entries are one object per line, sorted append at EOF
- Every entry separates `claimed_attribution` from `verified_attribution`
- `VERIFIED`/`MISATTRIBUTED` provenance requires non-empty `receipts`
- Commit format: Conventional Commits
- Branch naming: `type/agent/short-desc`

## Direct-to-Main Policy
- **Tier 1** — docs, validator fixes, README
- **Tier 2 — PR required** — new corpus entries, schema changes, anything touching `corpus/quotes.jsonl`
- Claim-honesty rule: no invented attributions, no invented receipts. `UNVERIFIED` is a valid provenance; an uncheckable claim is not a defect — an undocumented one is.
