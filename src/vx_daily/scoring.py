from __future__ import annotations

import re

from .models import ArticleDraft, ScoreResult

AI_TELL_PATTERNS = [
    "首先",
    "其次",
    "最后",
    "综上所述",
    "总而言之",
    "未来可期",
    "重要的是",
    "值得注意的是",
]

EXPLICIT_PERSONA_TERMS = ["作为一个务实", "务实、积极", "善良、真实的人", "我是一个"]

PUBLISH_LEAK_PATTERNS = [
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"\bresource/"),
    re.compile(r"notebooklm\.google\.com", re.IGNORECASE),
    re.compile(r"wechat_private", re.IGNORECASE),
    re.compile(r"(APP_SECRET|WECHAT_APP_SECRET|OPENAI_API_KEY|access_token)", re.IGNORECASE),
]

RESOURCE_KEYWORDS = [
    "KV Cache",
    "PagedAttention",
    "Attention Sinks",
    "Heavy Hitters",
    "KVQuant",
    "KIVI",
    "MLA",
    "vLLM",
    "显存",
    "长上下文",
    "推理",
]


def _article_text(draft: ArticleDraft) -> str:
    parts: list[str] = [draft.title, draft.summary]
    for section in draft.sections:
        parts.append(section.heading)
        parts.extend(section.paragraphs)
        parts.extend(section.bullets)
    return "\n".join(parts)


def _leading_text(draft: ArticleDraft) -> str:
    parts = [draft.title, draft.summary]
    if draft.sections:
        parts.append(draft.sections[0].heading)
        parts.extend(draft.sections[0].paragraphs)
    return "\n".join(parts)


def _resource_excerpt(draft: ArticleDraft) -> str:
    files = draft.resource_context.get("files", [])
    excerpts = [str(item.get("excerpt", "")) for item in files]
    combined = str(draft.resource_context.get("combined_excerpt", ""))
    return "\n".join([combined, *excerpts])


def _resource_hits(text: str, resource_excerpt: str) -> list[str]:
    if not resource_excerpt:
        return []
    candidates = [keyword for keyword in RESOURCE_KEYWORDS if keyword in resource_excerpt]
    return [keyword for keyword in candidates if keyword in text]


def _has_publish_leak(text: str) -> bool:
    return any(pattern.search(text) for pattern in PUBLISH_LEAK_PATTERNS)


def _has_ai_tell(text: str) -> bool:
    transition_count = sum(1 for pattern in AI_TELL_PATTERNS if pattern in text)
    has_ordered_template = all(pattern in text for pattern in ("首先", "其次", "最后"))
    return has_ordered_template or transition_count >= 4 or any(term in text for term in EXPLICIT_PERSONA_TERMS)


def _paragraphs(draft: ArticleDraft) -> list[str]:
    result: list[str] = []
    for section in draft.sections:
        result.extend(section.paragraphs)
        result.extend(section.bullets)
    return result


def score_draft(draft: ArticleDraft, policy: dict, threshold: int) -> ScoreResult:
    text = _article_text(draft)
    leading_text = _leading_text(draft)
    resource_excerpt = _resource_excerpt(draft)
    paragraphs = _paragraphs(draft)
    details: dict[str, int] = {}
    reasons: list[str] = []
    hard_blockers: list[str] = []
    warnings: list[str] = []

    title_len = len(draft.title)
    max_title = int(policy.get("wechat_layout", {}).get("max_title_chars", 32))
    details["title"] = 10 if 8 <= title_len <= max_title else 5
    if details["title"] < 10:
        reasons.append("标题长度不适合公众号草稿箱。")

    section_count = len(draft.sections)
    details["structure"] = 12 if section_count >= 5 else 6
    if section_count < 5:
        reasons.append("小标题层次不足，读者在手机端不容易扫读。")

    max_paragraph_chars = int(policy.get("wechat_layout", {}).get("paragraph_chars", 120))
    too_long_paragraphs = [p for p in paragraphs if len(p) > max_paragraph_chars + 45]
    has_example = any(marker in text for marker in ("比如", "像", "举个例子", "小例子"))
    paragraph_count = sum(len(section.paragraphs) for section in draft.sections)
    details["readability"] = 14 if paragraph_count >= 8 and has_example and not too_long_paragraphs else 8
    if details["readability"] < 14:
        if too_long_paragraphs:
            reasons.append("存在过长段落，需要拆短以适配移动端阅读。")
            warnings.append("long_paragraph")
        if not has_example:
            reasons.append("缺少具体例子，技术解释容易显得抽象。")
            hard_blockers.append("missing_concrete_example")

    warmth_terms = ["我", "我们", "你", "希望", "相信", "焦虑", "方向", "练一下"]
    warmth_hits = sum(1 for term in warmth_terms if term in text)
    details["warmth"] = 10 if warmth_hits >= 4 and not any(term in text for term in EXPLICIT_PERSONA_TERMS) else 5
    if details["warmth"] < 10:
        reasons.append("个人真实感应通过判断、例子和措辞体现，不能直接罗列人设标签。")

    tech_hits = sum(1 for term in draft.topic.technical_terms if term in text)
    details["technical_grounding"] = 14 if tech_hits >= min(3, len(draft.topic.technical_terms)) else 7
    if details["technical_grounding"] < 14:
        reasons.append("技术关键词没有真正进入正文解释。")

    has_boundary = any(marker in text for marker in ("边界", "不等于", "不能", "不是", "代价", "取舍", "不适合"))
    details["boundary"] = 10 if has_boundary else 4
    if not has_boundary:
        reasons.append("缺少边界或取舍提醒，容易把技术讲成单向宣传。")
        hard_blockers.append("missing_boundary")

    action_terms = ["练一下", "三句话", "目标", "材料", "完成", "判断", "先写"]
    action_hits = sum(1 for term in action_terms if term in text)
    details["actionability"] = 10 if action_hits >= 4 else 5
    if details["actionability"] < 10:
        reasons.append("可执行建议不够具体。")
        hard_blockers.append("missing_actionable_takeaway")

    blacklist_hits = [term for term in policy.get("blacklist_terms", []) if term in text]
    details["safety"] = 12 if not blacklist_hits else 0
    if blacklist_hits:
        reasons.append("命中黑名单词：" + "、".join(blacklist_hits))
        hard_blockers.append("blacklist_term")

    if _has_publish_leak(text):
        reasons.append("正文泄露了本地路径、NotebookLM 链接或接口字段，不能上传到公众号。")
        hard_blockers.append("publish_leak")

    if _has_ai_tell(text):
        reasons.append("正文存在明显模板化 AI 写作痕迹，需要重写衔接和结尾。")
        hard_blockers.append("ai_tell")

    details["image_fit"] = 6 if draft.cover_prompt.strip() else 0
    if details["image_fit"] == 0:
        reasons.append("缺少封面图提示词。")

    source_terms = ["官方", "论文", "开源", "README", "来源", "参考", "确认", "NotebookLM"]
    source_hits = sum(1 for term in source_terms if term in text)
    details["source_discipline"] = 8 if source_hits >= 2 else 3
    if details["source_discipline"] < 8:
        reasons.append("缺少明确来源注记。")
        hard_blockers.append("missing_source_note")

    if resource_excerpt:
        resource_hits = _resource_hits(text, resource_excerpt)
        leading_hits = _resource_hits(leading_text, resource_excerpt)
        conflict_terms = ["幻觉", "胡说", "概率分布", "训练目标"]
        has_kv_resource = "KV Cache" in resource_excerpt
        conflict_in_title = any(term in draft.title or term in leading_text for term in conflict_terms)
        if has_kv_resource and (len(resource_hits) < 3 or len(leading_hits) < 1 or conflict_in_title):
            reasons.append("本地资料主题没有主导文章角度，存在资源主题错配。")
            hard_blockers.append("resource_topic_mismatch")
        details["source_grounding"] = 8 if len(resource_hits) >= 3 else 3
    else:
        details["source_grounding"] = 6

    hard_blockers = sorted(set(hard_blockers))
    warnings = sorted(set(warnings))
    total = min(100, sum(details.values()))
    passed = total >= threshold and not hard_blockers
    if passed:
        reasons.append("达到发布预览标准，可进入本地待审。")

    return ScoreResult(
        total=total,
        passed=passed,
        threshold=threshold,
        details=details,
        reasons=reasons,
        rewrite_required=not passed,
        hard_blockers=hard_blockers,
        warnings=warnings,
    )
