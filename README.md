# HUMMBL Canon

A provenance-first corpus of quotable lines — the ones that carry real load — plus a personal resonance layer.

Most quote collections are wrong about who said what. Canon treats attribution as a *claim* that carries receipts or doesn't. Every entry separates `claimed_attribution` (what the internet says) from `verified_attribution` (what the evidence supports), and marks provenance as `VERIFIED`, `COMMON-ATTRIB`, `MISATTRIBUTED`, or `UNVERIFIED`.

## Layers

| Layer | Path | Purpose |
|---|---|---|
| **Corpus** | `corpus/quotes.jsonl` | The substrate. One JSON object per line, diffable, machine-readable. |
| **Fleet** | corpus IDs | Agents cite `q-*` IDs in AARs, briefs, and reviews the way they cite rules and receipts. |
| **Resonance** | `resonance/` | Personal log of lines that actually landed — when, where, why. Local-first; see `resonance/README.md`. |

## Quick start

```bash
python scripts/validate_corpus.py            # validate corpus/quotes.jsonl
python scripts/validate_corpus.py --stats    # corpus statistics
python scripts/quote.py q-gall-simple-system            # resolve an anchor
python scripts/quote.py --cite q-feynman-fool-yourself  # citation form
python scripts/quote.py --theme hubris                  # browse by theme
python scripts/quote.py --search "slave of the passions"
python scripts/validate_resonance.py           # validate local resonance logs
```

No dependencies beyond Python 3.11 stdlib.

## Schema

See `docs/schema.md`. Required fields: `id`, `text`, `claimed_attribution`, `verified_attribution`, `source`, `provenance`. `VERIFIED` and `MISATTRIBUTED` entries must carry `receipts` — the claim-honesty rule enforced structurally.

## Conventions

- Corpus edits go through PRs (same Tier-2 discipline as `hummbl-bibliography`)
- Conventional Commits, `type/agent/short-desc` branches
- Attribution claims need sources; "commonly attributed to" is a finding, not a defect

## License

MIT — see `LICENSE`.
