---
name: wechat-ai-daily
description: Generate one daily AI-themed WeChat public-account draft for the VX repo, ground it in local resource or NotebookLM exports, score it, rewrite if below threshold, archive locally, prepare a built-in imagegen cover, upload to the WeChat draft box when credentials are available, and sync to GitHub. Use when the user asks to produce, review, or continue the daily AI公众号 draft workflow in D:\github\VX.
---

# WeChat AI Daily

## Overview

Produce one warm, practical, technically clear AI article draft per day for a personal WeChat public account. Use local resources or NotebookLM exports as the knowledge base. Keep the workflow score-gated and stop at the WeChat draft box for manual review before publishing.

## Workflow

1. Work in `D:\github\VX`.
2. Read useful files under `resource/`; prefer project notes and `resource/notebooklm/exports/`.
3. Run `python scripts\run_daily.py`.
4. Inspect the generated folder under `drafts/YYYY-MM-DD/`.
5. Read `score.json`; if the score is below 85, the pipeline should already have retried up to its max attempts.
6. Use built-in `image_gen` to generate a cover from `cover_prompt.txt`, then save it as `cover.png` in the same draft folder.
7. Review `article.md` and `article.html`.
8. Run `python scripts\upload_wechat_draft.py --article-dir <draft_dir> --dry-run`.
9. When WeChat credentials and account permissions are available, rerun without `--dry-run` to upload to the WeChat draft box.
10. Commit and push with `powershell -ExecutionPolicy Bypass -File scripts\sync_github.ps1`.

## Content Rules

- Daily count is exactly 1.
- Minimum score is 85; drafts below that must be rewritten before becoming review-ready.
- The author persona is practical, positive, optimistic, kind, and authentic. Express it through examples, judgment, and tone. Do not list personality labels in the article.
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

This repo is for a personal public account. Upload review-ready content to the WeChat draft box when API credentials and account permissions are available. Do not call the publish API: the user reviews and publishes manually. If the account does not have draft API access, keep the local archive and manual copy/paste fallback.

## Useful Commands

```powershell
cd D:\github\VX
python scripts\run_daily.py
python scripts\upload_wechat_draft.py --article-dir <draft_dir> --dry-run
python -m unittest discover -s tests
powershell -ExecutionPolicy Bypass -File scripts\sync_github.ps1
```

## References

For detailed style and safety notes, read `references/content-standards.md` when adjusting generation or scoring rules.
