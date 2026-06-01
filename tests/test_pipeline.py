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
from vx_daily.wechat_api import build_article_payload  # noqa: E402


class PipelineTests(unittest.TestCase):
    def test_build_wechat_payload_uses_news_article_shape(self) -> None:
        payload = build_article_payload(
            title="把复杂任务交给 AI 前",
            html_content="<section><p>hello</p></section>",
            thumb_media_id="MEDIA_ID",
            author="科技互联网博士",
            digest="一篇测试摘要",
        )

        self.assertEqual(payload["article_type"], "news")
        self.assertEqual(payload["thumb_media_id"], "MEDIA_ID")
        self.assertEqual(payload["need_open_comment"], 0)

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
            self.assertNotIn("务实、积极、乐观、善良、真实", article)
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

    def test_run_daily_uses_resource_materials_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            shutil.copytree(ROOT / "config", tmp_root / "config")
            resource_dir = tmp_root / "resource" / "projects" / "demo"
            resource_dir.mkdir(parents=True)
            (resource_dir / "notes.md").write_text(
                "这个项目用检索增强生成技术减少模型幻觉，核心经验是先保存来源，再生成答案。",
                encoding="utf-8",
            )

            article_dir = run_daily(tmp_root, date(2026, 6, 1), min_score=85)

            metadata = json.loads((article_dir / "metadata.json").read_text(encoding="utf-8"))
            article = (article_dir / "article.md").read_text(encoding="utf-8")

            self.assertEqual(metadata["resource_context"]["status"], "loaded")
            self.assertIn("resource/projects/demo/notes.md", metadata["resource_context"]["files"])
            self.assertIn("从资料里拎出一个线索", article)
            self.assertIn("检索增强生成技术", article)


if __name__ == "__main__":
    unittest.main()
