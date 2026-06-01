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


def _resource_excerpt(resource_context: dict[str, Any]) -> str:
    files = resource_context.get("files", [])
    excerpts = [str(item.get("excerpt", "")) for item in files]
    combined = str(resource_context.get("combined_excerpt", ""))
    return "\n".join([combined, *excerpts])


def _is_kv_cache_resource(resource_context: dict[str, Any]) -> bool:
    excerpt = _resource_excerpt(resource_context)
    return "KV Cache" in excerpt and ("PagedAttention" in excerpt or "长上下文" in excerpt)


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
    if len(excerpt) > 140:
        excerpt = excerpt[:140].rstrip() + "..."

    return Section(
        heading="把资料变成一个可读问题",
        paragraphs=[
            f"本地资料里最适合展开的一条线索是：{excerpt}",
            "我会把它先转成读者能感到的场景，再回到技术机制。这样写不只是更好读，也能减少把术语照搬成结论的风险。",
        ],
    )


def _kv_cache_topic() -> Topic:
    return Topic(
        category="tech_explainer",
        category_label="AI 技术解析",
        title_seed="为什么大模型越聊越卡？",
        core_question="KV Cache 为什么会在长上下文和高并发推理里成为显存瓶颈？",
        technical_terms=["KV Cache", "PagedAttention", "显存", "长上下文", "推理"],
    )


def _kv_cache_sections(attempt: int) -> list[Section]:
    rewrite_note = "这版我会把抽象术语再压低一点，多留一点生活里的直觉。" if attempt > 1 else ""
    return [
        Section(
            heading="先从一个卡顿说起",
            paragraphs=[
                "你和一个大模型聊得越久，它未必是在“变笨”，更常见的问题是：它要带着越来越长的上下文继续往下写。",
                f"我更愿意把 KV Cache 理解成一本摊在桌上的笔记。它帮模型少做重复计算，但笔记越摊越多，显存这张桌子也会越来越挤。{rewrite_note}",
            ],
        ),
        Section(
            heading="直觉：缓存是在省时间，也是在占空间",
            paragraphs=[
                "Transformer 每生成一个新 token，都要回看前面内容。没有缓存，它会反复重算；有了 KV Cache，它可以把已经算过的 Key 和 Value 留下来复用。",
                "这听起来很划算。代价是，长上下文会让缓存持续增长；高并发时，很多人的对话缓存一起放进显存，压力就会很快出现。我们看到的卡顿，常常就藏在这笔账里。",
            ],
        ),
        Section(
            heading="PagedAttention 解决的不是魔法问题",
            paragraphs=[
                "PagedAttention 的直觉很像操作系统分页：不要给每个请求预留一大块连续显存，而是把缓存拆成小块，需要多少就拼多少。",
                "比如餐厅排座位，整桌预留容易浪费；把座位拆细，翻台率会更高。对应到推理服务里，它主要缓解多并发下的显存碎片和利用率问题。",
            ],
            bullets=[
                "它更关心显存利用率，不等于单个请求一定更快。",
                "它适合服务很多变长请求，但低并发、极低延迟场景要看额外查表开销。",
                "它是工程调度方法，不是让模型理解能力突然变强的算法。",
            ],
        ),
        Section(
            heading="哪些记忆可以瘦身",
            paragraphs=[
                "KV Cache 压缩的难点在于，不是所有 token 都一样重要。很多工作会尝试保留开头、最近内容、注意力很重的 token，再丢掉影响较小的部分。",
                "Attention Sinks、Heavy Hitters、H2O、Scissorhands 这些名字背后，讨论的都是同一个朴素问题：哪些内容必须留下，哪些内容可以用较小代价放手。",
            ],
        ),
        Section(
            heading="量化也要看 Key 和 Value 的脾气",
            paragraphs=[
                "把 KV Cache 压到 4-bit 或 2-bit，直觉上像图片压缩。但 AI 的“记忆”里有离群值，不能简单一刀切。",
                "一些资料会区分 Key 和 Value 的分布：Key 更容易受离群通道影响，Value 相对平滑。KVQuant、KIVI、RotateKV 这类方法，本质上是在更细地处理这种差异。",
            ],
        ),
        Section(
            heading="边界：别把优化写成万能药",
            paragraphs=[
                "这里最容易误解的一点是：缓存优化不是免费午餐。它通常是在吞吐、延迟、精度和成本之间换一个更适合当前业务的平衡点。",
                "MLA 这类架构级优化也不是能直接装到任意已有模型上的插件。数学推理、长链路 CoT 任务对激进缓存驱逐更敏感，不能只看省了多少显存。",
            ],
        ),
        Section(
            heading="今天可以练一下",
            paragraphs=[
                "下次看到一篇推理优化论文或工程博客，先写三句话：它省了什么资源，付出了什么代价，在哪些场景不适合。",
                "这个小检查很务实。我自己读系统论文时也常用它：先把兴奋感放一放，再判断一个方案能不能放进自己的系统。",
            ],
        ),
        Section(
            heading="来源与边界",
            paragraphs=[
                "本文依据本地知识库整理的 KV Cache 主题笔记，并优先采用论文、官方文档和开源项目 README 作为后续核验来源。",
                "文中不宣称任何方法完全无损，也不把单篇论文结论外推成商业承诺；涉及具体数值时，应回到原文确认模型规模、上下文长度和测试设置。",
            ],
        ),
    ]


def _default_sections(topic: Topic, resource_context: dict[str, Any], attempt: int) -> list[Section]:
    intro = (
        f"今天想聊一个很实际的问题：{topic.core_question}"
        "我希望这篇文章不只是把概念讲清楚，也能给你一个明天就能试的小动作。"
    )
    if attempt > 1:
        intro += "这一版会多放一点例子，少一点术语堆叠。"

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
                f"这件事可以先抓住几个关键词：{terms}。如果这些词一开始看着陌生，没关系，我们先把它们当成工具箱里的几个抽屉。",
                "真正重要的是知道什么时候打开哪个抽屉，而不是一上来背定义。",
            ],
            bullets=[
                "先问：我要解决的具体问题是什么？",
                "再问：AI 需要哪些上下文才不会乱猜？",
                "再检查：我怎样判断答案算不算合格？",
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
                    "更好的问法是：先让它列出核心问题，再让它用生活例子解释，然后要求它标出哪些地方需要查原文确认。",
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
                heading="来源与边界",
                paragraphs=[
                    "本文优先参考本地知识库、官方文档、论文原文和开源项目 README；无法核实的内容只作为经验判断，不写成事实。",
                    "技术文章可以严谨，也可以有温度。复杂问题不必写得吓人，先把边界讲清楚，再给一个能动手的小练习。",
                ],
            ),
        ]
    )
    return sections


def generate_draft(
    profile: dict,
    topics: dict,
    target_date: date_type,
    attempt: int = 1,
    resource_context: dict[str, Any] | None = None,
) -> ArticleDraft:
    target_date_text = target_date.isoformat()
    resource_context = resource_context or {}
    topic = _kv_cache_topic() if _is_kv_cache_resource(resource_context) else select_topic(topics, target_date)
    rewrite_note = "" if attempt == 1 else "（改写版）"
    title = f"{topic.title_seed}{rewrite_note}"
    if len(title) > 32:
        title = title.replace("为什么", "为何").replace("怎么", "如何")[:32]

    if _is_kv_cache_resource(resource_context):
        sections = _kv_cache_sections(attempt)
        summary = "用桌面笔记的例子，讲清楚 KV Cache 为什么会让长上下文推理越来越吃显存。"
    else:
        sections = _default_sections(topic, resource_context, attempt)
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
