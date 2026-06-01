from __future__ import annotations

from .models import ArticleDraft, ScoreResult


def _article_text(draft: ArticleDraft) -> str:
    parts: list[str] = [draft.title, draft.summary]
    for section in draft.sections:
        parts.append(section.heading)
        parts.extend(section.paragraphs)
        parts.extend(section.bullets)
    return "\n".join(parts)


def score_draft(draft: ArticleDraft, policy: dict, threshold: int) -> ScoreResult:
    text = _article_text(draft)
    details: dict[str, int] = {}
    reasons: list[str] = []

    title_len = len(draft.title)
    details["title"] = 10 if 8 <= title_len <= policy["wechat_layout"]["max_title_chars"] else 5
    if details["title"] < 10:
        reasons.append("标题长度不够适配公众号。")

    section_count = len(draft.sections)
    details["structure"] = 14 if section_count >= 5 else 7
    if section_count < 5:
        reasons.append("小标题层次不足。")

    paragraph_count = sum(len(section.paragraphs) for section in draft.sections)
    details["readability"] = 14 if paragraph_count >= 8 and "比如" in text else 9
    if details["readability"] < 14:
        reasons.append("例子或解释还不够浅显。")

    explicit_persona_terms = ["作为一个务实", "务实、积极", "善良、真实的人", "我是一个"]
    explicit_persona_hits = [term for term in explicit_persona_terms if term in text]

    warmth_terms = ["我", "我们", "你", "希望", "相信", "温度", "焦虑", "方向"]
    warmth_hits = sum(1 for term in warmth_terms if term in text)
    details["warmth"] = 12 if warmth_hits >= 5 and not explicit_persona_hits else 7
    if details["warmth"] < 12:
        if explicit_persona_hits:
            reasons.append("人设应通过表达体现，不要把性格标签直接写进正文。")
        else:
            reasons.append("个人真实感和温度还不够。")

    tech_hits = sum(1 for term in draft.topic.technical_terms if term in text)
    details["technical_grounding"] = 16 if tech_hits >= min(3, len(draft.topic.technical_terms)) else 9
    if details["technical_grounding"] < 16:
        reasons.append("技术关键词覆盖不足。")

    action_terms = ["练一下", "三句话", "目标", "材料", "完成", "判断"]
    action_hits = sum(1 for term in action_terms if term in text)
    details["actionability"] = 10 if action_hits >= 4 else 6
    if details["actionability"] < 10:
        reasons.append("可执行建议不够具体。")

    blacklist_hits = [term for term in policy["blacklist_terms"] if term in text]
    details["safety"] = 12 if not blacklist_hits else 0
    if blacklist_hits:
        reasons.append("命中黑名单词：" + "、".join(blacklist_hits))

    details["image_fit"] = 6 if draft.cover_prompt.strip() else 0
    if details["image_fit"] == 0:
        reasons.append("缺少封面图提示词。")

    source_terms = ["官方", "论文", "开源", "原文", "引用", "来源", "确认"]
    source_hits = sum(1 for term in source_terms if term in text)
    details["source_discipline"] = 6 if source_hits >= 2 else 3
    if details["source_discipline"] < 6:
        reasons.append("来源意识有体现，但还可以加入更明确的参考来源。")

    total = min(100, sum(details.values()))
    passed = total >= threshold and not blacklist_hits
    if passed:
        reasons.append("达到入库标准，可保存为本地待审稿。")

    return ScoreResult(
        total=total,
        passed=passed,
        threshold=threshold,
        details=details,
        reasons=reasons,
        rewrite_required=not passed,
    )
