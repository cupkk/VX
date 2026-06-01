# VX

个人微信公众号 AI 日更草稿流水线。

目标是每天生成 1 篇有温度、浅显、务实的 AI 主题文章，自动评分，低于 85 分自动重写，合格后本地归档并同步到 GitHub。个人公众号场景下，第一阶段默认不自动发布、不依赖微信草稿接口。

## 当前闭环

```text
主题池
  -> 本地文章生成
  -> 自动评分
  -> 低于 85 分自动重写
  -> Markdown / HTML / score.json / metadata.json 归档
  -> 生成封面图 imagegen 提示词
  -> GitHub 同步
```

## 快速运行

```powershell
cd D:\github\VX
python scripts\run_daily.py
```

运行后会在 `drafts/YYYY-MM-DD/001-.../` 下生成：

- `article.md`
- `article.html`
- `score.json`
- `metadata.json`
- `cover_prompt.txt`

## GitHub 同步

确认生成内容后运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\sync_github.ps1
```

脚本会检查暂存 diff 中是否包含明显密钥字段，然后执行 `git add`、`git commit`、`git push`。

## 图片生成

脚本只生成 `cover_prompt.txt` 和目标路径。用 Codex 内置 imagegen 生成封面图后，把图片保存为同目录的 `cover.png`。不要把 OpenAI API Key 写进仓库。

## 安全边界

- 不提交 `.env` 或任何 AppSecret。
- 默认不自动发布公众号文章。
- 个人公众号优先人工复制/检查/发布。
- 涉及医疗、金融、法律、时政、投资收益承诺等内容默认降级或拒绝。

## 验证

```powershell
python -m unittest discover -s tests
python -X utf8 C:\Users\18103\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\github\VX\skills\wechat-ai-daily
```
