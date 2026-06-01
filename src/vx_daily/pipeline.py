from __future__ import annotations

from datetime import date as date_type
from datetime import datetime
from pathlib import Path

from .config import load_project_config
from .generator import generate_draft
from .rendering import render_html, render_markdown, write_json
from .scoring import score_draft


def _next_article_dir(root: Path, target_date: date_type, slug: str) -> Path:
    day_dir = root / "drafts" / target_date.isoformat()
    day_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(path for path in day_dir.iterdir() if path.is_dir())
    index = len(existing) + 1
    return day_dir / f"{index:03d}-{slug}"


def run_daily(root: Path, target_date: date_type, min_score: int | None = None, max_attempts: int = 3) -> Path:
    config = load_project_config(root)
    threshold = min_score or int(config.profile["publishing"]["min_score"])

    attempts = []
    final_draft = None
    final_score = None

    for attempt in range(1, max_attempts + 1):
        draft = generate_draft(config.profile, config.topics, target_date, attempt=attempt)
        score = score_draft(draft, config.policy, threshold)
        attempts.append({"attempt": attempt, "score": score.to_dict(), "title": draft.title})
        final_draft = draft
        final_score = score
        if score.passed:
            break

    if final_draft is None or final_score is None:
        raise RuntimeError("pipeline did not produce a draft")

    status = "ready_for_review" if final_score.passed else "rejected_after_rewrite"
    article_dir = _next_article_dir(root, target_date, final_draft.slug)
    article_dir.mkdir(parents=True, exist_ok=False)

    (article_dir / "article.md").write_text(
        render_markdown(final_draft, final_score, status), encoding="utf-8"
    )
    (article_dir / "article.html").write_text(render_html(final_draft), encoding="utf-8")
    (article_dir / "cover_prompt.txt").write_text(final_draft.cover_prompt, encoding="utf-8")
    write_json(article_dir / "score.json", final_score.to_dict())
    write_json(
        article_dir / "metadata.json",
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "date": target_date.isoformat(),
            "status": status,
            "daily_count": 1,
            "account_type": config.profile["publishing"]["account_type"],
            "draft": final_draft.to_dict(),
            "attempts": attempts,
            "image_generation": {
                "mode": "codex_builtin_imagegen",
                "status": "prompt_ready",
                "prompt_file": "cover_prompt.txt",
                "target_file": "cover.png",
            },
            "github_sync": {
                "status": "pending",
                "command": "powershell -ExecutionPolicy Bypass -File scripts\\sync_github.ps1",
            },
        },
    )
    return article_dir

