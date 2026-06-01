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
from vx_daily.models import ArticleDraft, Section, Topic  # noqa: E402
from vx_daily.rendering import render_html, render_markdown  # noqa: E402
from vx_daily.scoring import score_draft  # noqa: E402
from vx_daily.wechat_api import build_article_payload  # noqa: E402


class PipelineTests(unittest.TestCase):
    def _draft(self, *, title: str = "为什么大模型越聊越卡？", body: str = "KV Cache 会随着上下文变长持续占用显存。") -> ArticleDraft:
        topic = Topic(
            category="tech_explainer",
            category_label="AI 技术解析",
            title_seed=title,
            core_question="KV Cache 为什么会成为长上下文推理瓶颈？",
            technical_terms=["KV Cache", "PagedAttention", "显存", "上下文"],
        )
        return ArticleDraft(
            title=title,
            slug="test",
            date="2026-06-03",
            topic=topic,
            summary="用一个桌面笔记的例子，解释 KV Cache 为什么会让长对话越来越占显存。",
            cover_prompt="warm editorial cover, no text",
            sections=[
                Section(
                    heading="先从一个真实卡顿说起",
                    paragraphs=[
                        body,
                        "比如同一个客服机器人，一边服务几十个长对话，一边还要保留每轮生成需要用到的 Key 和 Value。",
                    ],
                ),
                Section(
                    heading="直觉：笔记越多，桌面越挤",
                    paragraphs=[
                        "KV Cache 像读长文时摊开的笔记。它减少重复计算，但也会占用越来越多的显存。",
                        "这里的边界是：这不是某个厂商写错代码，而是 Transformer 自回归推理的通用压力。",
                    ],
                ),
                Section(
                    heading="机制：缓存省计算，也吃带宽",
                    paragraphs=[
                        "PagedAttention 把缓存拆成小块管理，类似操作系统的虚拟内存分页，可以缓解多并发下的碎片。",
                        "它主要提高显存利用率，不等于任何单请求都会更快。",
                    ],
                    bullets=["看上下文长度", "看并发量", "看延迟目标"],
                ),
                Section(
                    heading="今天可以练一下",
                    paragraphs=[
                        "下次看到一个推理优化方案，先写三句话：它省了什么、代价是什么、在哪些场景不适合。",
                        "这个检查能帮你避免把论文结论直接外推成商业承诺。",
                    ],
                ),
                Section(
                    heading="来源与边界",
                    paragraphs=[
                        "本文参考 NotebookLM 中关于 KV Cache、PagedAttention、Attention Sinks 和量化边界的资料整理。",
                        "涉及具体数值时应回到论文、官方文档或开源项目 README 确认。",
                    ],
                ),
            ],
            attempt=1,
            tags=["AI", "KV Cache"],
            resource_context={
                "files": [
                    {
                        "path": "resource/notebooklm/exports/kv-cache-optimization-20260601.md",
                        "excerpt": "KV Cache 压缩、PagedAttention、Attention Sinks、KVQuant、KIVI、MLA。",
                    }
                ],
                "combined_excerpt": "KV Cache 压缩、PagedAttention、Attention Sinks、KVQuant、KIVI、MLA。",
            },
        )

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
            self.assertNotIn("自动评分摘要", article)
            self.assertNotIn("封面图提示词", article)
            self.assertNotIn("wechat_media_id", article)
            self.assertNotIn("务实、积极、乐观、善良、真实", article)
            self.assertEqual(metadata["image_generation"]["mode"], "codex_builtin_imagegen")
            self.assertTrue((article_dir / "review.json").exists())

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
            self.assertIn("检索增强生成技术", article)

    def test_scoring_blocks_resource_topic_mismatch(self) -> None:
        draft = self._draft(
            title="大模型为什么会一本正经地胡说？",
            body="幻觉来自语言模型的概率分布和训练目标。比如让 AI 总结论文时，它可能把听起来合理的话当成事实。",
        )

        score = score_draft(draft, {"blacklist_terms": [], "wechat_layout": {"max_title_chars": 32}}, 85)

        self.assertFalse(score.passed)
        self.assertTrue(score.rewrite_required)
        self.assertIn("resource_topic_mismatch", score.hard_blockers)

    def test_scoring_blocks_publish_leaks_and_ai_tells(self) -> None:
        draft = self._draft(
            body=(
                "今天这篇参考 D:\\github\\VX\\resource\\notebooklm\\exports\\kv-cache-optimization-20260601.md。"
                "首先，KV Cache 是关键技术。其次，它非常重要。最后，未来可期。"
            )
        )

        score = score_draft(draft, {"blacklist_terms": [], "wechat_layout": {"max_title_chars": 32}}, 85)

        self.assertFalse(score.passed)
        self.assertIn("publish_leak", score.hard_blockers)
        self.assertIn("ai_tell", score.hard_blockers)

    def test_render_markdown_is_clean_publication_manuscript(self) -> None:
        draft = self._draft()

        article = render_markdown(draft, "ready_for_review")

        self.assertIn("# 为什么大模型越聊越卡？", article)
        self.assertIn("## 来源与边界", article)
        self.assertNotIn("自动评分摘要", article)
        self.assertNotIn("cover_prompt", article)
        self.assertNotIn("wechat_media_id", article)

    def test_render_html_uses_wechat_mobile_theme(self) -> None:
        html = render_html(self._draft())

        self.assertIn('data-vx-theme="wechat-ai-daily"', html)
        self.assertIn("font-size:16px", html)
        self.assertIn("line-height:1.85", html)
        self.assertIn("border-left", html)
        self.assertIn("来源与边界", html)

    def test_notebooklm_resource_drives_generated_angle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            shutil.copytree(ROOT / "config", tmp_root / "config")
            resource_dir = tmp_root / "resource" / "notebooklm" / "exports"
            resource_dir.mkdir(parents=True)
            shutil.copyfile(
                ROOT / "resource" / "notebooklm" / "exports" / "kv-cache-optimization-20260601.md",
                resource_dir / "kv-cache-optimization-20260601.md",
            )

            article_dir = run_daily(tmp_root, date(2026, 6, 3), min_score=85)

            article = (article_dir / "article.md").read_text(encoding="utf-8")
            review = json.loads((article_dir / "review.json").read_text(encoding="utf-8"))

            self.assertIn("KV Cache", article)
            self.assertIn("PagedAttention", article)
            self.assertNotIn("一本正经地胡说", article)
            self.assertTrue(review["passed"])
            self.assertEqual(review["hard_blockers"], [])


if __name__ == "__main__":
    unittest.main()
