from __future__ import annotations

import hashlib
from datetime import date as date_type
from typing import Any

from .models import ArticleDraft, Section, Topic


def select_topic(topics: dict, target_date: date_type) -> Topic:
    rotation = topics["rotation"]
    index = target_date.toordinal() % len(rotation)
    raw = rotation[index]
    return Topic(
        category=raw["category"],
        category_label=raw["category_label"],
        title_seed=raw["title_seed"],
        core_question=raw["core_question"],
        technical_terms=list(raw["technical_terms"]),
    )


def _slug_for(target_date: str, topic: Topic) -> str:
    digest = hashlib.sha1(f"{target_date}:{topic.title_seed}".encode("utf-8")).hexdigest()[:8]
    return f"{target_date}-{topic.category}-{digest}"


def _resource_section(resource_context: dict[str, Any]) -> Section | None:
    files = resource_context.get("files", [])
    if not files:
        return None

    first = files[0]
    raw_lines = str(first.get("excerpt", "")).splitlines()
    useful_lines = [
        line.strip(" -")
        for line in raw_lines
        if line.strip()
        and not line.startswith("#")
        and "notebooklm.google.com" not in line
        and not line.startswith("导出时间")
        and not line.startswith("来源 notebook")
    ]
    excerpt = " ".join(useful_lines[:2])
    if len(excerpt) > 180:
        excerpt = excerpt[:180].rstrip() + "..."

    return Section(
        heading="从资料里拎出一个线索",
        paragraphs=[
            f"今天这篇会优先参考本地资料库里的内容，尤其是《{first.get('path')}》这份材料。",
            f"我先抓一个最适合展开的线索：{excerpt}",
            "如果资料里有很细的实现、实验或项目背景，我会尽量把它翻译成普通读者也能跟上的问题，而不是照搬术语。",
        ],
    )


def generate_draft(
    profile: dict,
    topics: dict,
    target_date: date_type,
    attempt: int = 1,
    resource_context: dict[str, Any] | None = None,
) -> ArticleDraft:
    topic = select_topic(topics, target_date)
    target_date_text = target_date.isoformat()
    resource_context = resource_context or {}
    rewrite_note = "" if attempt == 1 else "（改写版）"
    title = f"{topic.title_seed}{rewrite_note}"
    if len(title) > 32:
        title = title.replace("为什么", "为何").replace("怎么", "如何")[:32]

    intro = (
        f"今天想聊一个很实际的问题：{topic.core_question}"
        "我希望这篇文章不只是把概念讲清楚，也能给你一个明天就能试的小动作。"
    )
    if attempt > 1:
        intro += "上一版如果显得太硬，这一版我会多放一点例子，少一点术语堆叠。"

    terms = "、".join(topic.technical_terms)
    sections = [
        Section(
            heading="先说一句人话",
            paragraphs=[
                intro,
                f"我的理解是：好技术最后都应该回到人的问题上。{topic.category_label}不是为了显得厉害，而是为了帮我们少走一点弯路。",
            ],
        ),
        Section(
            heading="把概念拆开看",
            paragraphs=[
                f"这件事可以先抓住四个关键词：{terms}。如果这些词一开始看着有点陌生，没关系，我们先把它们当成工具箱里的几个抽屉。",
                "真正重要的是知道什么时候打开哪个抽屉，而不是一上来背定义。",
            ],
            bullets=[
                "先问：我要解决的具体问题是什么？",
                "再问：AI 需要哪些上下文才不会乱猜？",
                "最后问：我怎样判断答案算不算合格？",
            ],
        ),
    ]

    resource_section = _resource_section(resource_context)
    if resource_section is not None:
        sections.append(resource_section)

    sections.extend(
        [
            Section(
                heading="一个小例子",
                paragraphs=[
                    "比如你想让 AI 帮你解释一段论文，直接说“帮我总结”通常会得到一段看似完整但不一定可用的回答。",
                    "更好的问法是：先让它列出核心问题，再让它用生活例子解释，最后要求它标出哪些地方需要查原文确认。",
                ],
            ),
            Section(
                heading="技术背后的直觉",
                paragraphs=[
                    "很多大模型能力看起来像魔法，本质上仍然是模式学习、概率选择和上下文对齐的组合。",
                    "我们不需要把每个公式都背下来，但要知道：模型越缺少边界，越容易把“听起来合理”误当成“真的可靠”。",
                ],
            ),
            Section(
                heading="今天可以练一下",
                paragraphs=[
                    "给自己找一个正在拖延的小任务，写下三句话：目标是什么、材料有哪些、怎样算完成。",
                    "然后把这三句话交给 AI，让它先反问你缺失的信息。这个动作很小，但会明显提高回答质量。",
                ],
            ),
            Section(
                heading="最后",
                paragraphs=[
                    "我一直相信，技术文章可以严谨，也可以有温度。复杂问题不必写得吓人，先把边界讲清楚，再给一个能动手的小练习。",
                    "如果这篇文章能帮你少一点焦虑，多一点可执行的方向，它就有价值。",
                ],
            ),
        ]
    )

    summary = f"{topic.category_label}：用一个真实问题讲清楚 {topic.technical_terms[0]}，并给出一个可立即练习的小方法。"
    cover_prompt = (
        "Use case: scientific-educational\n"
        "Asset type: WeChat article cover image\n"
        f"Primary request: A warm, clean editorial illustration for an AI article about {topic.title_seed}.\n"
        "Style/medium: modern hand-drawn digital illustration, light technology notebook style\n"
        "Composition/framing: 16:9 landscape, centered desk scene with laptop, notes, simple AI concept diagram, generous whitespace\n"
        "Lighting/mood: soft daylight, optimistic, practical, human-centered\n"
        "Color palette: warm white, graphite, calm green, small blue accents\n"
        "Text: no text, no logo\n"
        "Avoid: hype, cyberpunk, dark mood, excessive robots, watermark\n"
    )

    return ArticleDraft(
        title=title,
        slug=_slug_for(target_date_text, topic),
        date=target_date_text,
        topic=topic,
        summary=summary,
        cover_prompt=cover_prompt,
        sections=sections,
        attempt=attempt,
        tags=["AI", topic.category_label, "技术科普", "个人思考"],
        resource_context=resource_context,
    )
