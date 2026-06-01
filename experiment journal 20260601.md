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

## 首次 GitHub 同步结果（2026-06-01 12:36 +08:00）

- 已通过 `scripts/sync_github.ps1` 完成首次闭环同步。
- 提交信息：`feat: add daily AI WeChat draft pipeline`。
- 本地提交：`03bf0e4 feat: add daily AI WeChat draft pipeline`。
- GitHub 远程核验：
  - `git ls-remote origin refs/heads/main` 返回 `03bf0e4db521bb2245b9d620c1fbd1b5170062cd`。
  - `gh repo view cupkk/VX --json nameWithOwner,defaultBranchRef,url` 返回仓库 `cupkk/VX`、默认分支 `main`、地址 `https://github.com/cupkk/VX`。
- 本地状态：`git status -sb` 显示 `main...origin/main`，推送后工作区干净。
- 注意：本节日志是在首次推送后追加，因此需要再做一次小提交同步日志本身。

## 闭环目标修正与草稿箱上传实现（2026-06-01 12:59 +08:00）

- 用户指出：完整闭环不是到 GitHub 结束，而是要把合格文章上传到微信公众号草稿箱；GitHub 只是归档和同步。
- 用户指出：正文中不应出现“作为一个务实、积极、乐观、善良、真实的人”这种显式人设标签。决策：人设只通过例子、判断、措辞和边界感体现，不直接罗列性格词。
- 已修改生成器和评分器：
  - `src/vx_daily/generator.py` 不再拼接 persona 标签。
  - `src/vx_daily/scoring.py` 会把显式罗列性格标签视为扣分原因。
  - 已同步修正首篇样例草稿的 `article.md`、`article.html`、`metadata.json`。
- 已新增 `resource/` 知识库入口：
  - `resource/inbox/`
  - `resource/projects/`
  - `resource/notebooklm/exports/`
  - `resource/style-guides/wechat-writing.md`
- 已新增 `src/vx_daily/resources.py`，流水线会读取 `resource/` 下的 `.md`、`.txt`、`.json` 文件，并把使用到的素材文件写入 `metadata.json`。
- 已检查 NotebookLM 插件状态：MCP 插件可用，但当前 Google/NotebookLM 未登录，`authenticated=false`。后续需要用户登录或提供 NotebookLM share link 后才能读取项目知识库。
- 已新增微信公众号草稿箱上传脚本：
  - `src/vx_daily/wechat_api.py`
  - `scripts/upload_wechat_draft.py`
- 微信接口实现边界：
  - 通过 `cover.png` 上传永久图片素材，获取封面 `media_id`。
  - 调用微信 `draft/add` 将文章写入草稿箱。
  - 不调用发布接口，发布仍由用户人工检查后执行。
  - 实际上传需要本机环境变量提供公众号 AppID/AppSecret，不能把凭据写入仓库。
- 已执行 dry-run：
  - `python scripts\upload_wechat_draft.py --article-dir drafts\2026-06-01\001-2026-06-01-practical_tip-70657647 --dry-run`
  - 产物：`drafts/2026-06-01/001-2026-06-01-practical_tip-70657647/wechat_draft_payload.dry_run.json`
  - 说明：微信草稿请求体可生成；真实上传尚未执行，因为当前没有公众号 API 凭据。
- 当前下一步：
  - 运行完整测试、skill 校验和秘密扫描。
  - 提交并推送本轮改动。
  - 用户后续在本机设置公众号凭据后，执行无 `--dry-run` 的上传命令测试真实草稿箱写入。

## 草稿箱上传 dry-run 验证（2026-06-01 13:03 +08:00）

- 运行 `python -m unittest discover -s tests`：通过，4 个测试。
- 运行 `python -X utf8 C:\Users\18103\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\github\VX\skills\wechat-ai-daily`：通过。
- 运行微信上传 dry-run：通过，生成 `wechat_draft_payload.dry_run.json`。
- 复查首篇文章和生成器：未再出现显式人设标签句。
- 秘密扫描初次误报 `access_token`、`app_secret` 等正常变量名，以及微信请求体中的固定字段名。已修正 `scripts/sync_github.ps1` 的扫描规则，只拦截字段后跟疑似密钥值的情况。
- 重新运行秘密扫描：未发现疑似密钥字段。
- 当前状态：草稿箱上传代码已可生成请求体；真实调用仍待公众号凭据和账号接口权限验证。

## NotebookLM 与微信真实上传推进（2026-06-01 13:36 +08:00）

- 用户提供 NotebookLM 链接，要求走通 NotebookLM 知识库路径和微信公众号草稿箱上传路径。
- NotebookLM 状态：
  - 已通过 NotebookLM MCP 完成 Google 登录，`authenticated=true`。
  - 对 notebook 提问成功，确认主题为“大语言模型推理阶段中 KV Cache 压缩评估与全面优化技术”。
  - 已抽取 6 个公众号连载选题和关键事实边界。
  - 已保存导出资料：`resource/notebooklm/exports/kv-cache-optimization-20260601.md`。
  - 已基于该资源重新运行日更流水线，生成草稿：`drafts/2026-06-02/002-2026-06-02-tech_explainer-1bb99ad7/`。
  - 该草稿 `metadata.json` 已记录 `resource_context.status=loaded`，使用来源为 `resource/notebooklm/exports/kv-cache-optimization-20260601.md`。
  - 已对该草稿执行微信上传 dry-run，生成 `wechat_draft_payload.dry_run.json`。
- 微信公众号真实上传状态：
  - 用户提供了公众号 AppID 和 AppSecret；本轮只在当前命令进程环境中使用，未写入文件、日志或仓库。
  - 调用真实微信接口失败，错误码 `40164`，微信返回调用 IP `39.174.145.41` 不在白名单。
  - 普通公网 IP 查询得到 `160.16.119.69`，但微信接口实际识别的出口 IP 是 `39.174.145.41`。后续白名单应以微信错误返回的 IP 为准。
  - 已提示用户在微信公众号后台“设置 API IP 白名单”中填写 `39.174.145.41` 并确认。
- 当前 blocker：
  - 未完成真实上传到微信公众号草稿箱，因为必须先由用户在微信公众平台后台设置 API IP 白名单。
- 下一步：
  - 用户确认白名单已保存后，重新运行真实上传命令。
  - 上传成功后检查草稿箱，并把 `wechat_cover_response.json`、`wechat_draft_response.json` 和更新后的 `metadata.json` 同步到 GitHub。

## 两条路径真实闭环完成（2026-06-01 13:49 +08:00）

- 用户已在微信公众号后台设置 API IP 白名单。
- 微信公众号真实上传已成功：
  - `drafts/2026-06-01/001-2026-06-01-practical_tip-70657647/` 已上传到微信公众号草稿箱，用于验证基础生成链路。
  - `drafts/2026-06-02/002-2026-06-02-tech_explainer-1bb99ad7/` 已上传到微信公众号草稿箱，用于验证 NotebookLM 知识库组合链路。
- NotebookLM 组合闭环已经实际跑通：
  - NotebookLM notebook 读取。
  - 导出 KV Cache 优化知识库到 `resource/notebooklm/exports/kv-cache-optimization-20260601.md`。
  - 流水线读取本地 `resource/` 资料。
  - 生成文章草稿、自动评分、封面提示词。
  - 使用 Codex 内置 imagegen 生成第二篇封面图。
  - 保留 `cover_raw.png`，裁剪生成 `cover.png`，尺寸 `1024x576`。
  - 上传封面永久素材。
  - 调用微信 `draft/add` 写入公众号草稿箱。
- 安全调整：
  - 公众号凭据只在当前命令进程中临时使用，运行后已清除环境变量。
  - 微信返回的素材标识不推送到 GitHub。
  - 已新增 `.gitignore` 规则 `wechat_private/`。
  - `scripts/upload_wechat_draft.py` 现在将微信原始响应保存在草稿目录下的 `wechat_private/`，仅本地保留。
  - GitHub 中的 `metadata.json` 只保留 `wechat_draft.status=uploaded`、上传时间和本地私有响应目录名。
- 当前下一步：
  - 跑测试、skill 校验、秘密扫描和 Git 状态核验。
  - 提交并推送本轮真实闭环结果。

## 文章质量与排版升级（2026-06-01 14:35 +08:00）

- 用户确认按方案 A 实施：规则门禁 + 编辑协议 + 公众号移动端预览主题。
- 已把评分器从关键词计数升级为发布质量门禁，新增硬阻断项：资源主题错配、本地路径或 NotebookLM 链接泄露、模板化 AI 写作痕迹、缺少来源注记、缺少具体例子、缺少边界或取舍、缺少可执行动作、黑名单词命中。
- 已拆分产物边界：
  - `article.md` 只保留干净发布稿。
  - `article.html` 保留微信上传用 HTML。
  - `review.json` 保存评分、硬阻断项、警告和原因。
  - `metadata.json` 保存运行状态和资源来源。
  - `cover_prompt.txt` 保存封面提示词。
- 已升级 HTML 渲染为 `data-vx-theme="wechat-ai-daily"` 主题，正文采用移动端友好的 16px、1.85 行高、短段落、克制引用块、来源/边界提示块。
- 已升级 NotebookLM/KV Cache 资源生成逻辑：当本地知识库包含 KV Cache、PagedAttention、长上下文等线索时，选题会直接切到《为什么大模型越聊越卡？》，而不是继续套用通用轮换题。
- 已更新 repo-local skill 和 references：
  - `skills/wechat-ai-daily/SKILL.md`
  - `skills/wechat-ai-daily/references/editorial-quality-gate.md`
  - `skills/wechat-ai-daily/references/wechat-layout.md`
  - `skills/wechat-ai-daily/references/humanizer-checklist.md`
  - `skills/wechat-ai-daily/references/content-standards.md`
- 已新增和更新测试，覆盖质量阻断、稿件/审计拆分、HTML 主题、NotebookLM 资源主导选题。
- 已生成新的本地预览稿：`drafts/2026-06-03/001-2026-06-03-tech_explainer-8400406a/`，标题为《为什么大模型越聊越卡？》。
- 新预览稿 `review.json`：总分 100，通过，`hard_blockers=[]`，`warnings=[]`。
- 已执行微信上传 dry-run，生成 `wechat_draft_payload.dry_run.json`；本次未执行真实上传，避免在质量升级阶段直接写入公众号草稿箱。
- 已用临时本地 HTTP 服务和 Playwright 打开 `article.html` 检查预览；页面加载成功，仅有浏览器自动请求 `favicon.ico` 导致的 404，不影响文章。
- 已通过验证：
  - `python -m unittest discover -s tests`
  - `python -X utf8 C:\Users\18103\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\github\VX\skills\wechat-ai-daily`
  - `git diff --check`，仅有 Windows 换行提示，无空白错误。
- 下一步建议：人工读一遍新预览稿，再决定是否生成封面图并执行真实微信草稿箱上传。

## 质量升级同步结果（2026-06-01 14:40 +08:00）

- 已通过仓库同步脚本完成提交和推送，提交信息为 `feat: add publication quality gate for daily drafts`。
- 远程 `origin/main` 已从 `67a3e52` 推进到 `f0d3362`。
- 本轮同步脚本在提交前执行了暂存区密钥扫描，未中断提交。
- 推送后 `git status --short --branch` 显示 `main...origin/main`，代码工作区已干净。
- 注意：本节为提交后的交接补记；最终提交哈希以 Git 历史为准，避免日志反复追写造成无限提交。
