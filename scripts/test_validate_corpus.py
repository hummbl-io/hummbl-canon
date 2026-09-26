#!/usr/bin/env python3
"""test_validate_corpus.py — Unit tests for validate_corpus.py and HOG-1 opinion schema.

Stdlib-only (Python 3.11+).
"""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.validate_corpus import (
    CORPUS,
    OPINION_CLASSES,
    load_entries,
    validate_entry,
)


class ValidateCorpusTests(unittest.TestCase):
    def setUp(self):
        self.base_entry = {
            "id": "q-test-slug",
            "text": "This is a sufficiently long sample quote for testing.",
            "claimed_attribution": "Speaker A",
            "verified_attribution": "Speaker A, 2026",
            "source": {
                "type": "film",
                "work": "Test Film (2026)",
                "locator": "Scene 1",
            },
            "provenance": "VERIFIED",
            "receipts": [{"type": "primary", "ref": "Test film script"}],
            "context": "Context explaining why this line lands.",
        }

    def test_base_entry_valid(self):
        errs, warns = validate_entry(1, self.base_entry)
        self.assertEqual(errs, [])
        self.assertEqual(warns, [])

    def test_valid_opinion_block(self):
        entry = dict(self.base_entry)
        entry["opinion"] = {
            "class": "AESTHETIC",
            "holder": "agy",
            "loss_function": "Harmonic resonance * syntactic brevity",
            "intensity": 0.95,
            "update_triggers": ["Alternative wording verified with higher historical impact."],
        }
        errs, warns = validate_entry(1, entry)
        self.assertEqual(errs, [])

    def test_valid_opinion_short_tag(self):
        entry = dict(self.base_entry)
        entry["opinion"] = {
            "class": "AXIO",
            "holder": {"identity": "reuben"},
            "loss_function": "Human agency protection",
            "update_triggers": ["Empirical disproof of operator autonomy."],
        }
        errs, warns = validate_entry(1, entry)
        self.assertEqual(errs, [])

    def test_opinion_invalid_class(self):
        entry = dict(self.base_entry)
        entry["opinion"] = {
            "class": "INVALID_CLASS",
            "holder": "agy",
            "loss_function": "Something",
            "update_triggers": ["Trigger"],
        }
        errs, warns = validate_entry(1, entry)
        self.assertTrue(any("opinion.class 'INVALID_CLASS' invalid" in e for e in errs))

    def test_opinion_missing_holder(self):
        entry = dict(self.base_entry)
        entry["opinion"] = {
            "class": "HEURISTIC",
            "holder": "",
            "loss_function": "Complexity reduction",
            "update_triggers": ["Trigger"],
        }
        errs, warns = validate_entry(1, entry)
        self.assertTrue(any("opinion missing valid 'holder' identity" in e for e in errs))

    def test_opinion_missing_loss_function(self):
        entry = dict(self.base_entry)
        entry["opinion"] = {
            "class": "HERMENEUTIC",
            "holder": "agy",
            "loss_function": "",
            "update_triggers": ["Trigger"],
        }
        errs, warns = validate_entry(1, entry)
        self.assertTrue(any("missing 'loss_function' or 'evaluative_basis'" in e for e in errs))

    def test_opinion_missing_update_triggers(self):
        entry = dict(self.base_entry)
        entry["opinion"] = {
            "class": "CONJECTURAL",
            "holder": "agy",
            "loss_function": "Forward model accuracy",
            "update_triggers": [],
        }
        errs, warns = validate_entry(1, entry)
        self.assertTrue(any("requires non-empty 'update_triggers'" in e for e in errs))

    def test_opinion_invalid_intensity(self):
        entry = dict(self.base_entry)
        entry["opinion"] = {
            "class": "AESTHETIC",
            "holder": "agy",
            "loss_function": "Resonance",
            "update_triggers": ["Trigger"],
            "intensity": 1.5,
        }
        errs, warns = validate_entry(1, entry)
        self.assertTrue(any("opinion.intensity must be a float between 0.0 and 1.0" in e for e in errs))

    def test_live_corpus_passes_all_validations(self):
        entries, load_errs = load_entries(CORPUS)
        self.assertEqual(load_errs, [])
        self.assertGreaterEqual(len(entries), 22)
        total_errs = []
        for lineno, e in entries:
            errs, _ = validate_entry(lineno, e)
            total_errs.extend(errs)
        self.assertEqual(total_errs, [])


if __name__ == "__main__":
    unittest.main()
