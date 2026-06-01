# VX

个人微信公众号 AI 日更草稿流水线。

目标是每天生成 1 篇有温度、浅显、务实的 AI 主题文章，自动评分，低于 85 分自动重写，合格后本地归档、上传到微信公众号草稿箱并同步到 GitHub。个人公众号场景下，默认不自动发布，草稿上传能力以账号实际 API 权限为准。

## 当前闭环

```text
主题池
  -> resource 本地知识库 / NotebookLM 导出资料
  -> 本地文章生成
  -> 自动评分
  -> 低于 85 分自动重写
  -> Markdown / HTML / score.json / metadata.json 归档
  -> 生成封面图 imagegen 提示词
  -> 上传封面永久素材
  -> 上传到微信公众号草稿箱
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

## 本地知识库

把论文笔记、项目资料、实验日志和个人判断放到 `resource/`。推荐按项目拆分：

```text
resource/
  inbox/
  projects/<project-name>/
  notebooklm/exports/
  style-guides/
```

流水线会读取 `.md`、`.txt`、`.json` 素材，并把使用到的文件记录到 `metadata.json`。不要把密钥、Cookie、私有 token 或不可公开信息放进仓库。

NotebookLM 接入步骤见 `resource/notebooklm/README.md`。

## 上传到微信公众号草稿箱

个人公众号能否调用草稿接口，以账号实际权限为准。脚本不会自动发布，只上传到草稿箱供人工检查。

先做 dry-run：

```powershell
python scripts\upload_wechat_draft.py `
  --article-dir drafts\2026-06-01\001-2026-06-01-practical_tip-70657647 `
  --dry-run
```

实际上传前，在当前 PowerShell 会话设置 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET` 环境变量，或传入临时 `WECHAT_ACCESS_TOKEN`。不要把凭据写进仓库。

```powershell
python scripts\upload_wechat_draft.py `
  --article-dir drafts\YYYY-MM-DD\001-...
```

脚本会检查评分，上传 `cover.png` 为永久图片素材，取得封面 `media_id`，调用微信 `draft/add` 写入草稿箱，并把微信返回结果写回草稿目录和 `metadata.json`。

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
- 个人公众号优先上传到草稿箱后人工检查/发布；如账号无草稿接口权限，则保留人工复制流程。
- 涉及医疗、金融、法律、时政、投资收益承诺等内容默认降级或拒绝。

## 验证

```powershell
python -m unittest discover -s tests
python -X utf8 C:\Users\18103\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\github\VX\skills\wechat-ai-daily
```
