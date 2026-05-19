# literature-table-organizer v3.0

`literature-table-organizer` 是一个面向**综述写作前半程**的 Codex 技能。

v3.0 现在固定为**单一 survey workflow**，围绕以下输入展开：

- 综述主题
- 本地 workbook
- 本地论文 PDF
- 可选草稿上下文

English documentation: [README.md](README.md)

## v3.0 的定位

v3.0 不再保留旧的混合工作流，而是收口为一条清晰主线：

- 初始化 survey 项目
- 建立并讨论 `project/framework.md`
- 基于本地 PDF 逐篇阅读论文
- 产出 paper report 和 row-analysis JSON
- 将整理后的结果写回 workbook

这版技能主要服务于：

- 综述导向的文献分析
- 分类规则校准
- 证据支撑的阅读记录
- 面向后续写作的工作表回填

它不是一个“自动写完整篇综述”的系统。

## 核心架构

整条流程只由一个正式协议文件驱动：

- `project/framework.md`

这个文件是唯一规则源，负责承载：

- survey context
- compact outline
- classification rules
- reading report structure
- workbook mapping

正式主产物固定为：

- `paper-reports/<row>-<slug>.md`
- `row-analysis/<row>-<slug>.json`

workbook 写回只消费 JSON，不再在写回阶段重新推断。

## 主流程

1. 运行 `init-project` 初始化 workspace 项目结构。
2. 使用 `build-framework` 并讨论、修改 `project/framework.md`。
3. 如有需要，先做 workbook 表头归一化。
4. 准备本地 `paper.pdf`。
5. 先对代表性论文运行 `row-analyze`。
6. 用 `pilot-run` 组织试分类校准。
7. 用 `batch-analyze` 生成更大范围的阅读队列。
8. 用 `writeback-xlsx` 把确认后的字段写回 workbook。

## CLI

统一只使用一个入口：

```bash
python scripts/cli.py <subcommand>
```

主要命令包括：

- `init-project`
- `build-framework`
- `normalize-workbook-headers`
- `find-paper-link`
- `pdf-download`
- `row-analyze`
- `pilot-run`
- `batch-analyze`
- `append-papers`
- `writeback-xlsx`
- `reset-project`

## Paper Report 与 JSON

`row-analyze` 是整套技能里最核心的单篇动作。

输入：

- `project/framework.md`
- workbook 某一行的元数据
- 本地 `paper.pdf`

输出：

- 一份 Markdown 格式的 paper report
- 一份 row-analysis JSON

报告结构固定为两半：

- Part A：中文阅读报告
- Part B：英文字段判断

这样既方便人工直接阅读，也方便后续稳定抽取结构化字段。

## Workbook 表头策略

技能内部只使用英文 canonical keys。

面向 workbook 时：

- 默认尽量保留原有中文表头
- 必要时可将支持的表头归一化为英文

命令：

```bash
python scripts/cli.py normalize-workbook-headers --workbook ...
```

如果当前环境对中文表头处理不稳定，建议先生成英文表头副本再继续。

## v3.0 中的 `append-papers`

`append-papers` 现在被定义为一个**安全扩表命令**。

行为固定为：

- 用规范化标题或规范化链接检测重复
- 遇到重复时跳过，而不是整批失败
- CLI 返回同时包含 `added_rows` 和 `skipped_rows`
- `project/expansion-log.md` 同时记录新增和跳过结果

它只负责追加基础论文元数据和可选写作字段。
它不会自动完成论文理解或自动分类。

## PDF 与下载策略

正式阅读输入只认本地 PDF：

- `papers/<row>-<slug>/paper.pdf`

`pdf-download` 只做静态 PDF 解析和下载。

它可以处理：

- arXiv
- 直接 PDF 链接
- 常见论文页中的静态 PDF 提取

如果静态下载失败，仍然需要人工继续处理。
v3.0 不再把旧的 Browser fallback 主链路作为正式公开口径。

## Demo 与校验

仓库内置 demo 资源：

- `assets/demo/literature-demo.xlsx`
- `assets/demo/demo-manifest.json`

校验命令：

```bash
python scripts/quick_validate.py
```

## 当前边界

- CLI 不会自动“读懂 PDF 正文”；`row-analyze` 仍然是代理主判读工作流。
- 想获得高质量结果，依然需要认真讨论 `framework.md`，并在 pilot 阶段做代表性校准。
- 这个技能服务的是综述生产前半程，不负责直接生成完整综述初稿。
