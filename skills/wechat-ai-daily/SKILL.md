---
name: wechat-ai-daily
description: Generate one daily AI-themed WeChat public-account draft for the VX repo, score it, rewrite if below threshold, archive Markdown/HTML/JSON locally, prepare a built-in imagegen cover prompt, and sync changes to GitHub. Use when the user asks to produce, review, or continue the daily AI公众号 draft workflow in D:\github\VX.
---

# WeChat AI Daily

## Overview

Produce one warm, practical, technically clear AI article draft per day for a personal WeChat public account. Keep the workflow local-first, score-gated, and safe for manual review before publishing.

## Workflow

1. Work in `D:\github\VX`.
2. Run `python scripts\run_daily.py`.
3. Inspect the generated folder under `drafts/YYYY-MM-DD/`.
4. Read `score.json`; if the score is below 85, the pipeline should already have retried up to its max attempts.
5. Use built-in `image_gen` to generate a cover from `cover_prompt.txt`, then save it as `cover.png` in the same draft folder.
6. Review `article.md` and `article.html`.
7. Commit and push with `powershell -ExecutionPolicy Bypass -File scripts\sync_github.ps1`.

## Content Rules

- Daily count is exactly 1.
- Minimum score is 85; drafts below that must be rewritten before becoming review-ready.
- The author persona is practical, positive, optimistic, kind, and authentic.
- Technical explanations should start from intuition, then mechanism, then one small exercise.
- Keep the text warm and human, not hype-driven.
- Avoid medical, financial, legal, political, privacy, and exaggerated-result claims unless handled as careful disclaimers.
- Never commit AppSecret, `OPENAI_API_KEY`, cookies, tokens, or `.env` files.

## Imagegen Cover Step

Use the built-in image generation tool, not an API key, for covers. Prompt from `cover_prompt.txt` and save the selected bitmap into the draft folder as `cover.png`.

Preferred cover style:
- warm modern hand-drawn digital illustration
- light technology notebook style
- no text, no logo, no watermark
- practical, optimistic, human-centered AI mood

## Publishing Boundary

This repo is for a personal public account. Do not assume automated WeChat publishing or draft API access. Default to local Markdown/HTML archive and manual copy/paste review unless the user explicitly asks to test WeChat API permissions.

## Useful Commands

```powershell
cd D:\github\VX
python scripts\run_daily.py
python -m unittest discover -s tests
powershell -ExecutionPolicy Bypass -File scripts\sync_github.ps1
```

## References

For detailed style and safety notes, read `references/content-standards.md` when adjusting generation or scoring rules.
