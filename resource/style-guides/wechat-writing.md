# 微信公众号 AI 技术文章写作规范

## 目标

写给普通读者和技术从业者：有真实问题、有具体细节、有边界、有行动建议。不要写成模板化的“AI 生成文章”，也不要为了迎合检测工具而故意制造低质量文本。

## 标题

- 标题控制在 32 个字以内，优先包含一个明确问题或可验证收益。
- 常用结构：
  - `为什么 X 会 Y？`
  - `把 X 讲清楚：先抓住这 3 个问题`
  - `我用 X 做了一次实验，真正有用的是这一步`
  - `面试里怎么讲清楚 X？`
- 避免夸张、绝对化、制造焦虑和标题党。

## 内容

- 开头用真实问题，不要用空泛宏大叙事。
- 技术部分按“直觉 -> 机制 -> 小例子 -> 边界 -> 可执行练习”展开。
- 每段尽量只讲一件事，移动端阅读优先。
- 引用优先级：官方文档、论文原文、开源项目 README、作者本人项目资料。
- 明确区分事实、经验判断和推测。

## 去 AI 味

- 人设通过判断、例子和措辞体现，不直接罗列“务实、积极、乐观、善良、真实”等性格标签。
- 删除“首先、其次、最后、综上所述”式机械衔接，除非确实有清晰顺序。
- 少用万能句式，多写具体场景、失败经验、取舍和限制。
- 不追求“绕过 AI 检测”。检测工具并不稳定，正确做法是提高原创性、事实性和个人判断密度。
- 发布前人工朗读一遍：删掉不像自己会说的话。

## 排版

- 小标题短而明确。
- 正文使用 16px 左右字号、1.75 至 1.9 行高、短段落。
- 摘要不超过 128 个字。
- 封面不用文字、Logo、水印或过度赛博朋克元素。
- 正文图片必须先上传到微信素材接口获得微信域名 URL，不能直接引用外链。

## 开源和官方参考

- 微信新增草稿接口：<https://developers.weixin.qq.com/doc/service/api/draftbox/draftmanage/api_draft_add>
- 微信上传图文消息图片：<https://developers.weixin.qq.com/doc/service/api/material/permanent/api_uploadimage>
- 微信上传永久素材：<https://developers.weixin.qq.com/doc/service/api/material/permanent/api_addmaterial>
- 微信发布能力说明：<https://developers.weixin.qq.com/doc/offiaccount/Publish/Publish.html>
- Doocs Markdown 编辑器：<https://github.com/doocs/md>
- Markdown Nice 排版工具：<https://github.com/mdnice/markdown-nice>
