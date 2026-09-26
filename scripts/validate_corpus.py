#!/usr/bin/env python3
"""Validate corpus/quotes.jsonl against the canon schema.

Rules enforced:
- one JSON object per line, no blank-line JSON junk
- required fields present (id, text, claimed_attribution, verified_attribution,
  source{type,work,locator}, provenance)
- provenance in {VERIFIED, COMMON-ATTRIB, MISATTRIBUTED, UNVERIFIED}
- unique ids matching q-<slug>
- receipts non-empty for VERIFIED and MISATTRIBUTED (the claim-honesty rule)

Usage:
  python scripts/validate_corpus.py            # validate, exit 0/1
  python scripts/validate_corpus.py --stats    # stats only
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus" / "quotes.jsonl"

PROVENANCE = {"VERIFIED", "COMMON-ATTRIB", "MISATTRIBUTED", "UNVERIFIED"}
REQUIRES_RECEIPTS = {"VERIFIED", "MISATTRIBUTED"}
ID_RE = re.compile(r"^q-[a-z0-9][a-z0-9-]*[a-z0-9]$")
SOURCE_TYPES = {"film", "book", "speech", "paper", "article", "letter", "interview", "other"}
HUMMBL_TAGS = {"P", "IN", "CO", "DE", "RE", "SY"}
OPINION_CLASSES = {
    "AXIOLOGICAL", "AESTHETIC", "CONJECTURAL", "HEURISTIC", "HERMENEUTIC",
    "AXIO", "AESTH", "CONJ", "HEUR", "HERM",
}


def load_entries(path):
    entries, errors = [], []
    if not path.exists():
        return entries, [f"corpus file missing: {path}"]
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"line {i}: invalid JSON ({e.msg})")
            continue
        if not isinstance(obj, dict):
            errors.append(f"line {i}: entry is not a JSON object")
            continue
        entries.append((i, obj))
    return entries, errors


def validate_entry(lineno, e):
    errs, warns = [], []

    for f in ("id", "text", "claimed_attribution", "verified_attribution", "source", "provenance"):
        if f not in e:
            errs.append(f"line {lineno}: missing required field '{f}'")
    if errs:
        return errs, warns

    eid = e["id"]
    if not isinstance(eid, str) or not ID_RE.match(eid):
        errs.append(f"line {lineno}: bad id format '{eid}' (want q-<slug>)")

    if not isinstance(e["text"], str) or len(e["text"].strip()) < 10:
        errs.append(f"line {lineno} ({eid}): text missing or trivially short")

    prov = e["provenance"]
    if prov not in PROVENANCE:
        errs.append(f"line {lineno} ({eid}): bad provenance '{prov}'")

    src = e["source"]
    if not isinstance(src, dict):
        errs.append(f"line {lineno} ({eid}): source must be an object")
    else:
        for f in ("type", "work", "locator"):
            if f not in src:
                errs.append(f"line {lineno} ({eid}): source missing '{f}'")
        if src.get("type") not in SOURCE_TYPES:
            errs.append(f"line {lineno} ({eid}): bad source.type '{src.get('type')}'")

    receipts = e.get("receipts", [])
    if prov in REQUIRES_RECEIPTS:
        if not isinstance(receipts, list) or not receipts:
            errs.append(f"line {lineno} ({eid}): {prov} requires non-empty receipts")
        else:
            for j, r in enumerate(receipts):
                if not isinstance(r, dict) or not r.get("type") or not r.get("ref"):
                    errs.append(f"line {lineno} ({eid}): receipt[{j}] needs type+ref")

    for f in ("claimed_attribution", "verified_attribution"):
        if not isinstance(e[f], str) or not e[f].strip():
            errs.append(f"line {lineno} ({eid}): {f} must be non-empty string")

    if prov == "MISATTRIBUTED" and e["claimed_attribution"] == e["verified_attribution"]:
        errs.append(f"line {lineno} ({eid}): MISATTRIBUTED but claimed == verified")

    for t in e.get("hummbl", []):
        if t not in HUMMBL_TAGS:
            warns.append(f"line {lineno} ({eid}): unknown hummbl tag '{t}'")
    if prov == "UNVERIFIED" and receipts:
        warns.append(f"line {lineno} ({eid}): has receipts but still UNVERIFIED — promote?")
    if not e.get("context"):
        warns.append(f"line {lineno} ({eid}): no context — canon entries should say why the line lands")

    if "opinion" in e:
        op = e["opinion"]
        if not isinstance(op, dict):
            errs.append(f"line {lineno} ({eid}): opinion must be an object")
        else:
            cls = op.get("class")
            if not isinstance(cls, str) or cls.strip().upper() not in OPINION_CLASSES:
                errs.append(f"line {lineno} ({eid}): opinion.class '{cls}' invalid (want one of {sorted(OPINION_CLASSES)})")

            holder = op.get("holder")
            if isinstance(holder, dict):
                holder_name = holder.get("identity") or holder.get("name")
            else:
                holder_name = holder
            if not isinstance(holder_name, str) or not holder_name.strip():
                errs.append(f"line {lineno} ({eid}): opinion missing valid 'holder' identity")

            loss = op.get("loss_function") or op.get("evaluative_basis")
            if not isinstance(loss, str) or not loss.strip():
                errs.append(f"line {lineno} ({eid}): opinion missing 'loss_function' or 'evaluative_basis'")

            triggers = op.get("update_triggers") or op.get("falsification_conditions")
            if not isinstance(triggers, list) or not triggers or not any(isinstance(t, str) and t.strip() for t in triggers):
                errs.append(f"line {lineno} ({eid}): opinion requires non-empty 'update_triggers'")

            if "intensity" in op:
                intensity = op["intensity"]
                if not isinstance(intensity, (int, float)) or not (0.0 <= intensity <= 1.0):
                    errs.append(f"line {lineno} ({eid}): opinion.intensity must be a float between 0.0 and 1.0")

    return errs, warns


def main():
    stats_only = "--stats" in sys.argv
    entries, errors = load_entries(CORPUS)

    seen = {}
    warnings = []
    for lineno, e in entries:
        errs, warns = validate_entry(lineno, e)
        errors.extend(errs)
        warnings.extend(warns)
        eid = e.get("id")
        if isinstance(eid, str):
            if eid in seen:
                errors.append(f"line {lineno}: duplicate id '{eid}' (first on line {seen[eid]})")
            else:
                seen[eid] = lineno

    prov_counts = Counter(e.get("provenance", "?") for _, e in entries)
    theme_counts = Counter(t for _, e in entries for t in e.get("themes", []))
    opinion_count = sum(1 for _, e in entries if "opinion" in e)

    print(f"entries: {len(entries)}")
    print("provenance: " + ", ".join(f"{k}={v}" for k, v in sorted(prov_counts.items())))
    if opinion_count:
        print(f"opinions: {opinion_count} ({opinion_count / len(entries) * 100:.1f}% of corpus)")
    if theme_counts:
        top = ", ".join(f"{k}({v})" for k, v in theme_counts.most_common(8))
        print(f"top themes: {top}")

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
