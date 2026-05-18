# literature-table-organizer

一个用于整理文献工作簿的 Codex 技能。它会把“论文表”变成一套可追溯的证据工作流：保留本地全文或网页证据、生成逐篇证据文件、按保守规则回填字段，并在本地 `.xlsx` 中写入可点击打开的路径。

英文文档见 [README.md](README.md)

## 适用场景

这个技能适合这样的工作簿：

- 一张论文主表
- 一张字段说明表，用来解释用户自定义列应该怎么填

它不把文献整理当成一次性填表，而是走一条可复用流水线：

1. 识别工作簿结构
2. 按“PDF/全文优先”抓取证据
3. 生成本地证据产物
4. 把结果和追溯路径写回工作簿

## v2 更新重点

- 从“摘要优先”升级为“PDF/全文优先”的证据策略
- 明确证据状态分级与完整回填门槛
- 本地 `.xlsx` 中的路径列既保留相对路径文本，也支持点击打开
- 证据 Markdown 会记录证据等级、是否允许完整回填、字段级依据
- 增加 manifest 与工作簿重建/清理辅助能力

## 仓库结构

- `SKILL.md`
  面向 Codex 的技能说明
- `agents/openai.yaml`
  技能元数据
- `scripts/`
  结构识别、抓取、证据生成、工作簿写回、校验与重建脚本
- `references/`
  工作流、证据模板、字段说明约定、同步说明、使用示例
- `assets/demo/`
  内置 demo 工作簿和 demo manifest

## 核心流程

1. 识别输入来源。
   本地 `xlsx` 或飞书电子表格。
2. 检测工作簿结构。
   识别论文主表和字段说明表。
3. 准备本地可编辑工作区。
   创建 papers、evidence、snapshots 等兄弟目录。
4. 抓取证据。
   优先拿 `paper.pdf`，其次是可读全文网页，再其次是合格的二手解读页。
5. 生成证据文件。
   保留 `paper.pdf`、`paper.txt`、`source.md` 或 `review.md`，并为每一行生成一份证据 Markdown。
6. 写回工作簿。
   复用或追加 `本地文件路径`、`证据链路径`、`核验警告/状态`，并给本地 `.xlsx` 写入可点击超链接。
7. 按需预览飞书同步。
   默认不会自动回传飞书。

## 证据策略

### 优先级

1. 本地可保存的论文全文，例如 `paper.pdf`
2. 官方可读的全文网页
3. 信息足够支撑结论的项目页、OpenReview 页或仓库文档
4. 高质量二手论文解读页
5. 仅摘要页

### 状态枚举

- `pdf_download`
- `pdf_via_browser`
- `fulltext_web`
- `secondary_review`
- `abstract_only`
- `unresolved`
- `mismatch_or_unverifiable`

### 完整回填门槛

只有以下状态默认允许完整回填工作簿：

- `pdf_download`
- `pdf_via_browser`
- `fulltext_web`
- `secondary_review`

以下状态默认只允许保守处理，不应驱动完整分类：

- `abstract_only`
- `unresolved`
- `mismatch_or_unverifiable`

在 v2 中，摘要页不再被当作默认完整核验依据。

## Browser fallback 现状

这个技能的抓取链路把 Browser fallback 视为静态抓取失败后的标准下一步。

但 v2 会如实说明当前能力边界：

- 先执行静态 HTTP 抓取
- 抓取脚本会输出 Browser fallback 指引，并标记需要动态抓取
- Python 抓取脚本目前还不会在脚本内部全自动完成 Browser 动态下载

也就是说，Browser fallback 在 v2 中是“半自动兜底链路”，而不是“脚本内全自动下载器”。

## 本地工作簿行为

对于本地 `.xlsx`，技能会在保留相对路径文本的同时，把以下列写成本地可点击超链接：

- `本地文件路径`
- `证据链路径`

这样就可以直接从工作簿打开对应的 PDF 或证据 Markdown。

## 已知限制

- 摘要页不能作为默认完整回填依据。
- 某些站点仍需要人工处理或 Browser 辅助抓取。
- 标题与来源疑似错配的行会被主动降级，禁止自动分类。
- 飞书同步走保守流程，先本地后回传。
- 内置 demo 只用于展示流程，不代表真实论文抓取覆盖能力。

## 快速开始

### 环境要求

- Python 3.9 及以上
- 脚本依赖的 Python 包，包括工作簿和 PDF 处理相关依赖
- 可使用 Codex 技能的运行环境

### 校验技能

```bash
python scripts/quick_validate.py
```

### 本地使用方式

把技能用于一个包含以下内容的本地工作簿：

- 一张带 `论文全名` 的论文主表
- 可选的 `论文链接`、`摘要`
- 一张语义上对应 `字段`、`建议填写方式`、`推荐取值/说明` 的字段说明表

之后技能脚本会准备 artifact 目录、抓取证据、生成证据文件，并把结果写回工作簿。

### Demo

仓库内置：

- `assets/demo/literature-demo.xlsx`
- `assets/demo/demo-manifest.json`

如果需要重建 demo 工作簿，可以运行：

```bash
python scripts/create_demo_workbook.py
```

## 主要脚本

- `scripts/detect_workbook_structure.py`
  识别论文主表和字段说明表候选项。
- `scripts/prepare_local_workspace.py`
  准备本地副本和 artifact 目录。
- `scripts/fetch_paper_sources.py`
  解析 PDF/全文来源，并在需要时输出 Browser fallback 指引。
- `scripts/build_evidence_files.py`
  生成证据 Markdown 和 PDF 文本抽取文件。
- `scripts/update_workbook.py`
  按列名写回单元格和本地超链接。
- `scripts/rebuild_local_workbook.py`
  基于已有本地证据和 manifest 重建工作簿状态。
- `scripts/quick_validate.py`
  校验技能结构并编译脚本。

## 输出目录

默认情况下，本地 artifact 会放在工作簿旁边：

- `<workbook_stem>_artifacts/papers/`
- `<workbook_stem>_artifacts/evidence/`
- `<workbook_stem>_artifacts/snapshots/`

如果旁边已经存在旧的 `artifacts/` 目录，脚本会优先复用它。

manifest 会记录每一行的核心状态，例如：

- row
- title
- local source path
- evidence path
- status
- warning
- backfill eligibility
- resolved URL

## 发布说明

这个仓库既可以作为技能源码仓库分发，也可以作为打包压缩包的来源，例如 `literature-table-organizer-v2.zip`。

对外发布时建议排除以下临时内容：

- `__pycache__/`
- `.pyc`
- 本地运行生成的工作簿产物
- 与内置 demo 无关的论文下载缓存和证据缓存
