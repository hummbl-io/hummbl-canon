#!/usr/bin/env python3
"""Resolve and browse corpus anchors — makes `q-*` ids citable in docs.

  python scripts/quote.py q-otto-octavius-intelligence   # resolve one anchor
  python scripts/quote.py --list                         # every id
  python scripts/quote.py --theme hubris                 # filter by theme
  python scripts/quote.py --search "slave of the passions"  # substring search
  python scripts/quote.py --cite q-gall-simple-system    # one-line citation form
"""

import json
import sys
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent / "corpus" / "quotes.jsonl"


def load():
    entries = {}
    if not CORPUS.exists():
        return entries
    for raw in CORPUS.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            e = json.loads(raw)
            entries[e["id"]] = e
        except (json.JSONDecodeError, KeyError):
            continue
    return entries


def fmt(e, cite=False):
    if cite:
        return f'{e["id"]} — "{e["text"]}" — {e["verified_attribution"]} [{e["provenance"]}]'
    parts = [f'{e["id"]}  [{e["provenance"]}]', f'  "{e["text"]}"', f'  verified: {e["verified_attribution"]}']
    if e.get("claimed_attribution") != e["verified_attribution"]:
        parts.append(f'  claimed:  {e["claimed_attribution"]}')
    src = e.get("source", {})
    parts.append(f'  source:   {src.get("work", "?")} — {src.get("locator", "?")}')
    if e.get("context"):
        parts.append(f'  context:  {e["context"]}')
    return "\n".join(parts)


def main():
    args = sys.argv[1:]
    entries = load()
    if not entries:
        print("corpus empty or missing", file=sys.stderr)
        return 1

    cite = "--cite" in args
    args = [a for a in args if a != "--cite"]

    if not args or "--list" in args:
        for qid in entries:
            print(qid)
        return 0

    if "--theme" in args:
        i = args.index("--theme")
        tag = args[i + 1]
        hits = [qid for qid, e in entries.items() if tag in e.get("themes", [])]
        for qid in hits:
            print(fmt(entries[qid], cite=cite))
        print(f"— {len(hits)} entries tagged '{tag}'")
        return 0

    if "--search" in args:
        i = args.index("--search")
        needle = " ".join(args[i + 1:]).lower()
        hits = [qid for qid, e in entries.items()
                if needle in e["text"].lower()
                or needle in e["verified_attribution"].lower()
                or needle in e.get("context", "").lower()]
        for qid in hits:
            print(fmt(entries[qid], cite=cite))
        if not hits:
            print(f"no entries match '{needle}'")
            return 1
        return 0

    qid = args[0]
    if qid not in entries:
        print(f"unknown id '{qid}' — {len(entries)} in corpus; try --list or --search", file=sys.stderr)
        return 1
    print(fmt(entries[qid], cite=cite))
    return 0


if __name__ == "__main__":
    sys.exit(main())
