from __future__ import annotations

import html
import json
from pathlib import Path

from .models import ArticleDraft


def render_markdown(draft: ArticleDraft, status: str) -> str:
    tags = ", ".join(draft.tags)
    lines = [
        "---",
        f"title: {draft.title}",
        f"date: {draft.date}",
        f"status: {status}",
        f"tags: {tags}",
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

    return "\n".join(lines).rstrip() + "\n"


def _section_style(section_heading: str) -> str:
    if "来源" in section_heading or "边界" in section_heading:
        return (
            "margin:28px 0 0;padding:14px 16px;"
            "background:#f7f8f5;border-left:4px solid #6f8f72;border-radius:4px;"
        )
    return "margin:30px 0 0;padding:0;"


def render_html(draft: ArticleDraft) -> str:
    blocks = [
        '<section data-vx-theme="wechat-ai-daily" style="font-size:16px;line-height:1.85;'
        'color:#242424;letter-spacing:0;word-break:break-word;">',
        f'<h1 style="font-size:22px;line-height:1.4;margin:0 0 14px;font-weight:700;color:#111;">{html.escape(draft.title)}</h1>',
        '<blockquote style="margin:16px 0 22px;padding:12px 16px;background:#f6f7f8;'
        'border-left:4px solid #4f7f73;color:#3d3d3d;border-radius:4px;">'
        f"{html.escape(draft.summary)}</blockquote>",
    ]
    for section in draft.sections:
        blocks.append(f'<section style="{_section_style(section.heading)}">')
        blocks.append(
            '<h2 style="font-size:18px;line-height:1.45;margin:0 0 12px;'
            'font-weight:700;color:#1f3d36;">'
            f"{html.escape(section.heading)}</h2>"
        )
        for paragraph in section.paragraphs:
            blocks.append(f'<p style="margin:0 0 14px;">{html.escape(paragraph)}</p>')
        if section.bullets:
            blocks.append('<ul style="margin:4px 0 2px;padding-left:1.2em;">')
            for bullet in section.bullets:
                blocks.append(f'<li style="margin:0 0 8px;">{html.escape(bullet)}</li>')
            blocks.append("</ul>")
        blocks.append("</section>")
    blocks.append("</section>")
    return "\n".join(blocks)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
