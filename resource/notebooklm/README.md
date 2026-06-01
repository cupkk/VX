# NotebookLM 接入说明

当前 NotebookLM MCP 插件可用，但本机尚未完成 Google 登录。接入方式有两种：

1. 插件方式：用户打开 NotebookLM，进入目标 notebook，点击 Share，设置 Anyone with the link，然后把 share link 发给 Codex。Codex 会把 notebook 注册到本地库，再用 `ask_question` 读取项目材料。
2. 浏览器方式：用户允许 Codex 打开可交互 Chrome 登录 NotebookLM。登录后，Codex 可以通过插件会话读取 notebook，并把问答摘要保存到 `resource/notebooklm/exports/`。

建议每个项目先导出三个文件：

- `project-summary.md`：项目背景、目标、主要贡献。
- `article-angles.md`：可拆成几篇公众号的选题角度。
- `source-notes.md`：必须保留的事实、数据、引用和不能公开的边界。

这些导出文件会被日更流水线作为知识库输入，但不会替代人工审核。
