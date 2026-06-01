# resource

这里存放公众号日更的知识库资料。流水线会读取 `resource/` 下的 `.md`、`.txt`、`.json` 文件，并把可用摘要写入新文章的 `metadata.json`。

建议目录：

- `resource/inbox/`：临时丢进来的材料。
- `resource/projects/`：一个项目一个子文件夹，适合放论文笔记、项目 README、实验日志、产品分析。
- `resource/notebooklm/exports/`：从 NotebookLM 问答或来源摘要导出的文本。
- `resource/style-guides/`：写作、标题、排版、去 AI 味规范。这里是规则资料，不作为单篇文章主题素材。

注意：

- 不要放 AppSecret、Cookie、私有 token、账号密码。
- 如果资料来自未公开项目，文章里只能写可公开表达的结论，不泄露代码、客户、隐私或商业机密。
- 资料越具体越好：项目背景、关键问题、失败案例、验证结果、你自己的判断，都会比泛泛摘要更适合写公众号。
