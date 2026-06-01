from __future__ import annotations

import html
import json
from pathlib import Path

from .models import ArticleDraft, ScoreResult


def render_markdown(draft: ArticleDraft, score: ScoreResult, status: str) -> str:
    tags = ", ".join(draft.tags)
    lines = [
        "---",
        f"title: {draft.title}",
        f"date: {draft.date}",
        f"status: {status}",
        f"score: {score.total}",
        f"threshold: {score.threshold}",
        f"attempt: {draft.attempt}",
        f"tags: {tags}",
        "wechat_media_id: ",
        "cover_media_id: ",
        "---",
        "",
        f"# {draft.title}",
        "",
        f"> {draft.summary}",
        "",
    ]

    for section in draft.sections:
        lines.append(f"## {section.heading}")
        lines.append("")
        for paragraph in section.paragraphs:
            lines.append(paragraph)
            lines.append("")
        for bullet in section.bullets:
            lines.append(f"- {bullet}")
        if section.bullets:
            lines.append("")

    lines.extend(
        [
            "## 自动评分摘要",
            "",
            f"- 总分：{score.total}/{100}",
            f"- 门槛：{score.threshold}",
            f"- 是否通过：{'是' if score.passed else '否'}",
            f"- 是否需要重写：{'是' if score.rewrite_required else '否'}",
            "",
        ]
    )
    for reason in score.reasons:
        lines.append(f"- {reason}")
    lines.extend(["", "## 封面图提示词", "", "```text", draft.cover_prompt.rstrip(), "```", ""])
    return "\n".join(lines)


def render_html(draft: ArticleDraft) -> str:
    blocks = [
        '<section style="font-size:16px;line-height:1.85;color:#222;">',
        f'<h1 style="font-size:22px;line-height:1.4;">{html.escape(draft.title)}</h1>',
        f'<blockquote style="margin:16px 0;padding:12px 16px;background:#f7f7f7;border-left:4px solid #7aa874;">{html.escape(draft.summary)}</blockquote>',
    ]
    for section in draft.sections:
        blocks.append(f'<h2 style="font-size:19px;margin-top:28px;">{html.escape(section.heading)}</h2>')
        for paragraph in section.paragraphs:
            blocks.append(f"<p>{html.escape(paragraph)}</p>")
        if section.bullets:
            blocks.append("<ul>")
            for bullet in section.bullets:
                blocks.append(f"<li>{html.escape(bullet)}</li>")
            blocks.append("</ul>")
    blocks.append("</section>")
    return "\n".join(blocks)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

