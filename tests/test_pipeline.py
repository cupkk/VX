from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vx_daily.pipeline import run_daily  # noqa: E402


class PipelineTests(unittest.TestCase):
    def test_run_daily_creates_reviewable_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            shutil.copytree(ROOT / "config", tmp_root / "config")

            article_dir = run_daily(tmp_root, date(2026, 6, 1), min_score=85)

            self.assertTrue((article_dir / "article.md").exists())
            self.assertTrue((article_dir / "article.html").exists())
            self.assertTrue((article_dir / "score.json").exists())
            self.assertTrue((article_dir / "metadata.json").exists())
            self.assertTrue((article_dir / "cover_prompt.txt").exists())

            score = json.loads((article_dir / "score.json").read_text(encoding="utf-8"))
            metadata = json.loads((article_dir / "metadata.json").read_text(encoding="utf-8"))
            article = (article_dir / "article.md").read_text(encoding="utf-8")

            self.assertGreaterEqual(score["total"], 85)
            self.assertTrue(score["passed"])
            self.assertEqual(metadata["daily_count"], 1)
            self.assertIn("有温度", article)
            self.assertEqual(metadata["image_generation"]["mode"], "codex_builtin_imagegen")

    def test_run_daily_retries_when_score_is_below_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            shutil.copytree(ROOT / "config", tmp_root / "config")

            article_dir = run_daily(tmp_root, date(2026, 6, 1), min_score=101, max_attempts=2)

            metadata = json.loads((article_dir / "metadata.json").read_text(encoding="utf-8"))
            score = json.loads((article_dir / "score.json").read_text(encoding="utf-8"))

            self.assertEqual(len(metadata["attempts"]), 2)
            self.assertFalse(score["passed"])
            self.assertEqual(metadata["status"], "rejected_after_rewrite")


if __name__ == "__main__":
    unittest.main()
