from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Topic:
    category: str
    category_label: str
    title_seed: str
    core_question: str
    technical_terms: list[str]


@dataclass(frozen=True)
class Section:
    heading: str
    paragraphs: list[str] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ArticleDraft:
    title: str
    slug: str
    date: str
    topic: Topic
    summary: str
    cover_prompt: str
    sections: list[Section]
    attempt: int
    tags: list[str]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return payload


@dataclass(frozen=True)
class ScoreResult:
    total: int
    passed: bool
    threshold: int
    details: dict[str, int]
    reasons: list[str]
    rewrite_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

