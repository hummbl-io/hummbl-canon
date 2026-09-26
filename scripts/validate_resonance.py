#!/usr/bin/env python3
"""Validate resonance/*.jsonl entries against the resonance schema.

Resonance logs are personal and gitignored — this validator runs locally,
never in CI. It enforces the anchor rule: a `quote_id` must resolve to a
corpus id (dangling anchors are defects; use `text` for uncaptured lines).

Rules enforced:
- one JSON object per line across resonance/*.jsonl
- `ts` parses as ISO-8601 (Z or offset)
- exactly one of `quote_id` (must resolve to corpus/quotes.jsonl) or `text`
- `surface` non-empty when present
- warn when `note` is missing (the point is *why it landed*)

Usage:
  python scripts/validate_resonance.py            # validate, exit 0/1
  python scripts/validate_resonance.py --stats    # stats only
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus" / "quotes.jsonl"
RESONANCE_DIR = ROOT / "resonance"


def corpus_ids():
    ids = set()
    if not CORPUS.exists():
        return ids
    for raw in CORPUS.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if raw:
            try:
                ids.add(json.loads(raw)["id"])
            except (json.JSONDecodeError, KeyError):
                pass
    return ids


def parse_ts(ts):
    if not isinstance(ts, str):
        return False
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def main():
    stats_only = "--stats" in sys.argv
    errors, warnings = [], []
    known = corpus_ids()

    files = sorted(RESONANCE_DIR.glob("*.jsonl")) if RESONANCE_DIR.exists() else []
    entries = []
    for path in files:
        for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.strip()
            if not line:
                continue
            loc = f"{path.name}:{i}"
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"{loc}: invalid JSON ({e.msg})")
                continue
            if not isinstance(obj, dict):
                errors.append(f"{loc}: entry is not a JSON object")
                continue
            entries.append((loc, obj))

    for loc, e in entries:
        if not parse_ts(e.get("ts")):
            errors.append(f"{loc}: missing or malformed 'ts' (want ISO-8601)")

        qid, text = e.get("quote_id"), e.get("text")
        if qid and text:
            errors.append(f"{loc}: both 'quote_id' and 'text' — pick one anchor form")
        elif not qid and not text:
            errors.append(f"{loc}: needs 'quote_id' (corpus anchor) or 'text' (uncaptured line)")
        elif qid:
            if known and qid not in known:
                errors.append(f"{loc}: quote_id '{qid}' not in corpus — dangling anchor")
        elif isinstance(text, str) and len(text.strip()) < 10:
            errors.append(f"{loc}: 'text' missing or trivially short")

        if "surface" in e and (not isinstance(e["surface"], str) or not e["surface"].strip()):
            errors.append(f"{loc}: 'surface' present but empty")
        if not e.get("note"):
            warnings.append(f"{loc}: no 'note' — the point is why it landed")
        if "themes" in e and not isinstance(e["themes"], list):
            errors.append(f"{loc}: 'themes' must be a list")

    anchored = sum(1 for _, e in entries if e.get("quote_id"))
    theme_counts = Counter(t for _, e in entries for t in e.get("themes", []) if isinstance(t, str))
    surfaces = Counter(e.get("surface") for _, e in entries if isinstance(e.get("surface"), str))

    print(f"files: {len(files)}, entries: {len(entries)} (anchored: {anchored}, freeform: {len(entries) - anchored})")
    if surfaces:
        print("surfaces: " + ", ".join(f"{k}({v})" for k, v in surfaces.most_common(5)))
    if theme_counts:
        print("top themes: " + ", ".join(f"{k}({v})" for k, v in theme_counts.most_common(8)))

    if stats_only:
        return 0 if not errors else 1
    for w in warnings:
        print(f"warn: {w}")
    for x in errors:
        print(f"error: {x}")
    print("OK" if not errors else f"FAIL ({len(errors)} errors, {len(warnings)} warnings)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
