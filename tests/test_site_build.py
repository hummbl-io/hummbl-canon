"""
Tests for hummbl-canon static site compilation and JSON CDN schema integrity.
"""

import json
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = REPO_ROOT / "public"

class TestCanonSiteBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import subprocess
        import sys
        res = subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "build_site.py")], capture_output=True, text=True)
        assert res.returncode == 0, f"Build script failed: {res.stderr}"

    def test_public_artifacts_exist(self):
        self.assertTrue((PUBLIC_DIR / "index.html").is_file())
        self.assertTrue((PUBLIC_DIR / "_headers").is_file())
        self.assertTrue((PUBLIC_DIR / "manifest.json").is_file())
        self.assertTrue((PUBLIC_DIR / "api" / "data.json").is_file())
        self.assertTrue((PUBLIC_DIR / "api" / "quotes.json").is_file())
        self.assertTrue((PUBLIC_DIR / "api" / "stats.json").is_file())

    def test_html_structure(self):
        content = (PUBLIC_DIR / "index.html").read_text(encoding="utf-8")
        self.assertGreater(len(content), 10000)
        self.assertIn("<!DOCTYPE html>", content)
        self.assertIn("HUMMBL CANON", content)
        self.assertIn("canon.hummbl.dev", content)
        self.assertIn("Citation Generator", content)

    def test_api_schema(self):
        data = json.loads((PUBLIC_DIR / "api" / "data.json").read_text(encoding="utf-8"))
        self.assertEqual(data["subdomain"], "canon.hummbl.dev")
        self.assertGreaterEqual(data["stats"]["total_quotes"], 20)
        self.assertIn("VERIFIED", data["stats"]["provenance"])
        self.assertIn("MISATTRIBUTED", data["stats"]["provenance"])

if __name__ == "__main__":
    unittest.main()
