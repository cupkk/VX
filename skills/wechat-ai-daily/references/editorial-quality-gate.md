# Editorial Quality Gate

Use this checklist before any WeChat draft upload.

## Artifact Boundary

- `article.md`: clean publication manuscript only.
- `article.html`: WeChat-ready HTML only.
- `review.json`: score, blockers, warnings, reasons.
- `metadata.json`: operational state and resource provenance.
- `cover_prompt.txt`: imagegen prompt.
- `wechat_private/`: local-only WeChat API responses.

## Hard Blockers

Any blocker means rewrite before preview or upload:

- Resource topic mismatch: local material does not drive the title, opening, and mechanism sections.
- Publish leak: local filesystem path, `resource/` path, NotebookLM URL, token name, or private response path appears in the article.
- AI tell: mechanical `首先/其次/最后`, generic positive conclusion, explicit persona labels, or reusable filler paragraphs.
- Missing source note.
- Missing concrete example.
- Missing boundary or tradeoff.
- Missing actionable takeaway.
- Blacklist or sensitive-boundary hit.

## Editorial Review

Ask these questions:

1. Can a reader explain the core idea after reading the first two sections?
2. Does the article contain one specific scene, not just definitions?
3. Does the mechanism section explain why, not only what?
4. Is the limitation stated plainly?
5. Can the reader do one small exercise today?
6. Does each factual claim have a reasonable path back to official docs, a paper, an open-source README, or a clearly labeled experience judgment?

## Source Grounding

When local resources exist, choose one angle and rewrite the whole article around it. Do not paste excerpts or local file paths into the manuscript. Keep provenance in `metadata.json`.
