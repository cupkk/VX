# WeChat Layout

WeChat readers mostly scan on mobile. The layout should help the article breathe without looking like a marketing poster.

## HTML Theme

- Body text: 16px, line-height around 1.85, no negative letter spacing.
- Paragraphs: short, one idea per paragraph, usually below 120 Chinese characters.
- Headings: 18px, clear and specific. Avoid decorative symbols.
- Summary: one blockquote at the top, below 128 Chinese characters.
- Lists: use only when scanability improves. Avoid bold inline-header lists.
- Source and boundary note: use a restrained callout with a left border.
- Cards: avoid nested cards and decorative floating sections.

## Upload Preview

Before calling the real WeChat upload:

1. Open or inspect `article.html`.
2. Check no text is cramped in long paragraphs.
3. Check headings form a readable outline.
4. Check source note and boundary note are present.
5. Check no local paths, NotebookLM links, material IDs, or secrets are visible.
6. Run upload script with `--dry-run`.

## External References

- Doocs Markdown: https://github.com/doocs/md
- Markdown Nice: https://github.com/mdnice/markdown-nice
- WeChat draft API docs: https://developers.weixin.qq.com/doc/service/api/draftbox/draftmanage/api_draft_add
