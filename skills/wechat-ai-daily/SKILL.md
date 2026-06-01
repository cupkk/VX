---
name: wechat-ai-daily
description: Use when producing, reviewing, improving, previewing, or uploading daily AI-themed WeChat public-account drafts in D:\github\VX, especially when local resource notes or NotebookLM exports should ground the article.
---

# WeChat AI Daily

## Overview

Generate one publication-ready AI article draft per day for a personal WeChat public account. The draft must be grounded in `resource/`, pass the editorial gate, render cleanly for mobile WeChat reading, then stop in the WeChat draft box for human review.

## Workflow

1. Work in `D:\github\VX`.
2. Inspect `resource/`, prioritizing project notes and `resource/notebooklm/exports/`.
3. Choose one article angle from the material. Do not append resource notes as a generic extra section.
4. Run `python scripts\run_daily.py`.
5. Inspect `article.md`, `article.html`, `review.json`, `metadata.json`, and `cover_prompt.txt`.
6. If `review.json.passed=false` or `hard_blockers` is non-empty, rewrite before any upload.
7. Use built-in imagegen with `cover_prompt.txt`, save `cover_raw.png`, crop or resize to `cover.png` at 16:9.
8. Preview `article.html`; check mobile readability, paragraph length, headings, source note, and no local path leaks.
9. Run `python scripts\upload_wechat_draft.py --article-dir <draft_dir> --dry-run`.
10. Upload without `--dry-run` only after the preview is publication-ready and credentials are available.
11. Commit and push with `powershell -ExecutionPolicy Bypass -File scripts\sync_github.ps1`.

## Hard Rules

- Daily count is exactly 1.
- Minimum score is 85. Below 85 must rewrite.
- Any hard blocker means no WeChat upload.
- `article.md` is the clean publication manuscript. Audit data belongs in `review.json`; cover prompt belongs in `cover_prompt.txt`.
- Never publish local paths, NotebookLM URLs, material IDs, tokens, credentials, or private response JSON.
- Never call the publish API. The user manually reviews and publishes from the WeChat draft box.

## Content Protocol

- Start from a real reader problem, not a broad trend opening.
- Use this structure when possible: scene -> intuition -> mechanism -> example -> boundary -> small exercise -> source note.
- Express the author's practical, positive, kind voice through judgment and examples. Do not list persona labels.
- Prefer clear tradeoffs over hype. Avoid absolute claims such as "完全无损", "所有场景最优", "彻底淘汰".
- Before upload, do a humanizer pass: remove mechanical transitions, generic conclusions, vague authority, over-bolded list headers, and template rhythm.

## References

- `references/content-standards.md`
- `references/editorial-quality-gate.md`
- `references/wechat-layout.md`
- `references/humanizer-checklist.md`

Useful external inspiration: `geekjourneyx/md2wechat-skill`, Doocs Markdown, Markdown Nice, and public AI-writing cleanup checklists. Treat them as inspiration; the VX gate and local resource grounding rules take priority.
