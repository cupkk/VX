# 研究进展总览

## 项目目标

为个人微信公众号搭建 AI 日更草稿闭环：每天生成 1 篇关于 AI 的文章，内容可以覆盖 AI 实用技巧、AI 技术解析、大模型算法知识、每日一道算法题、算法八股文等。文章要体现作者务实、积极、乐观、善良的性格，表达真实自我，有温度，技术部分浅显易懂。

## 当前方向

- 个人公众号优先本地生成和人工发布，不把微信自动发布作为第一阶段目标。
- 每天 1 篇，低于 85 分直接重写。
- 使用本地仓库 `D:\github\VX` 保存 Markdown、HTML、评分、元数据和封面图提示词，并同步到 GitHub。
- 配图通过 Codex 系统内置 imagegen 生成，不把第三方图像 API 或密钥写入仓库。

## 已完成工作

- 初始化本地 Python 项目结构。
- 建立作者画像、内容政策和选题轮换配置。
- 实现本地单篇文章生成、评分、低于阈值重写、Markdown/HTML/JSON 归档的最小闭环。
- 创建 repo-local `wechat-ai-daily` skill，用于指导后续 Codex 运行本日更流程和调用内置 imagegen。

## 当前 blocker

- 尚未接入真实微信公众号草稿箱接口。个人公众号权限可能不支持完整草稿/发布接口，因此当前默认人工复制发布。
- 尚未生成真实封面图文件，当前先生成 `cover_prompt.txt`，后续由 Codex 内置 imagegen 产出 `cover.png`。

## 下一步

- 运行端到端测试。
- 生成第一篇样例草稿。
- 检查 Git diff 中是否有密钥或敏感信息。
- 提交并尝试推送到 GitHub。

# 2026-06-01 更新

## 初始化闭环

- 用户确认开始做，目标是先打通闭环。
- 当前仓库检查结果：`D:\github\VX` 只有 `.git`，远程为 `https://github.com/cupkk/VX.git`。
- 决策：先实现不依赖外部密钥的本地闭环，确保每天可以生成一篇可审核的 AI 文章草稿；微信接口和真实图片生成作为后续可插拔步骤。
- 初次验证发现：`python -m unittest` 默认未发现 `tests/`，后续改用 `python -m unittest discover -s tests`；skill 校验脚本在 Windows 默认 GBK 下读取中文会失败，后续改用 `python -X utf8 ...quick_validate.py`。

## 第一版闭环验证

- 已生成样例草稿目录：`drafts/2026-06-01/001-2026-06-01-practical_tip-70657647/`。
- 产物包括：`article.md`、`article.html`、`score.json`、`metadata.json`、`cover_prompt.txt`。
- 样例标题：`把复杂任务交给 AI 前，先写清楚验收标准`。
- 样例评分：100/100，超过 85 分门槛，状态为 `ready_for_review`。
- 评分器已补充 `source_discipline` 维度，避免只有形式完整但缺少来源意识的稿件直接满分。
- 测试已覆盖：
  - 正常日更生成会产出可审核草稿。
  - 当阈值高于可达分数时，会按重写次数重试，并最终标记 `rejected_after_rewrite`。
- 验证命令：
  - `python -m unittest discover -s tests`：通过，2 个测试。
  - `python -X utf8 C:\Users\18103\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\github\VX\skills\wechat-ai-daily`：通过。
- 已生成 repo-local skill 元数据：`skills/wechat-ai-daily/agents/openai.yaml`。
- 已使用 Codex 内置 imagegen 生成封面图，原始生成文件保存在 Codex 默认生成目录，并复制到草稿目录。
- 因内置 imagegen 输出为 1024x1024 正方形，不符合公众号封面 16:9 预期，已保留 `cover_raw.png`，并裁剪生成 `cover.png`，尺寸为 1024x576。
- 已更新 `metadata.json` 的 `image_generation.status` 为 `generated`，并在 `article.md` frontmatter 中补充 `cover_file` 与 `cover_raw_file`。

## 保留边界

- 未接入微信 AppSecret，未写入任何密钥。
- 未调用微信草稿箱接口，个人公众号当前默认人工复制/审核/发布。
- 已生成真实 `cover.png`；后续可继续优化封面风格和稳定生成 16:9 输出。

## 提交前闭环复核（2026-06-01 12:32 +08:00）

- 复核仓库状态：`D:\github\VX` 当前是 `main` 分支，远程为 `https://github.com/cupkk/VX.git`，本轮改动均属于公众号日更闭环初始化。
- 修正 `scripts/sync_github.ps1` 中秘密扫描正则，确保 PowerShell `Select-String` 能匹配密钥字段后接冒号或等号的写法；日志不保留完整示例，避免提交前扫描误报。
- 重新验证：
  - `python -m unittest discover -s tests`：通过，2 个测试。
  - `python -X utf8 C:\Users\18103\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\github\VX\skills\wechat-ai-daily`：通过，skill 有效。
  - 文本文件秘密扫描：未发现 `AppSecret`、`OPENAI_API_KEY`、`api_key`、`password`、`secret`、`token` 后接 `:` 或 `=` 的疑似密钥字段。
  - 正则样例检查：包含 `api_key` 加冒号的测试字符串可以被当前扫描正则命中；日志不保留完整样例，避免提交前扫描误报。
- 当前下一步：执行 Git 提交并推送到 GitHub，推送后再记录 commit 和远程状态。
