# literature-table-organizer

一个 Codex 技能，用于把文献工作簿变成两种工作流之一：

- 普通的“证据驱动文献表整理”
- 面向新综述写作前半程的“分类 + 证据 + 写作支撑工作流”

英文文档见 [README.md](README.md)

## 两种模式

### 1. 普通整理模式

适合这些场景：

- 校验已有文献表
- 补全文和更强证据
- 回填用户定义字段
- 维护本地证据链
- 在 `.xlsx` 中写入可点击路径

### 2. 综述导向模式

适合这些场景：

- 这张文献表是为了写一篇新的综述/评论文章
- 需要先分析已有综述，再决定自己的突破口
- 需要写作大纲、字段手册、试分类校准
- 需要把论文和写作章节对应起来
- 需要持续补充新论文并重新整理

这个模式会额外走一条前置流程：

1. 理解综述主题和文章目标
2. 阅读相关综述与代表性论文
3. 分析差异化与突破口
4. 生成并讨论大纲
5. 把字段说明升级成字段手册
6. 抽 5-10 篇论文做校准
7. 再批量跑整表
8. 后续继续补论文和重跑

## 这个技能解决什么问题

很多文献表最后只剩“结果”，缺少：

- 为什么这样分类
- 具体证据在哪里
- 这篇论文服务于综述的哪一章
- 某个章节缺文献时怎么补

这个技能会把工作簿升级成一套可复用工作区，包括：

- 本地原文或网页证据
- 逐篇 evidence Markdown
- manifest 状态文件
- 项目级综述文档
- 工作簿可点击路径和写作支撑列

## 综述导向模式的项目级产物

在 `<workbook_stem>_artifacts/project/` 下会生成：

- `project-brief.md`
- `related-survey-analysis.md`
- `outline.md`
- `field-manual.md`
- `pilot-calibration.md`
- `paper-expansion-log.md`

其中 `outline.md` 是写作主线中枢。

## 工作簿列

技能始终维护：

- `本地文件路径`
- `证据链路径`
- `核验警告/状态`

在综述导向模式下，还会维护：

- `写作引用章节`
- `引用论据`

对本地 `.xlsx`，路径列会保留相对路径文本，同时写成本地可点击超链接。

## 证据策略

### 优先级

1. 本地全文，例如 `paper.pdf`
2. 官方可读全文网页
3. 项目页、OpenReview 页或仓库文档
4. 高质量二手解读页
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

只有以下状态默认允许完整回填：

- `pdf_download`
- `pdf_via_browser`
- `fulltext_web`
- `secondary_review`

摘要级证据不再是综述导向模式下的默认完整分类依据。

## 分类协议

这个技能不再把分类理解成“只填一个值”。

对主要字段，evidence Markdown 应该记录：

- 判定问题
- 最终取值
- 关键证据片段
- 前因后果式推理链
- 排除性解释
- 证据充分性

这对综述导向模式尤其重要，因为 `引用论据` 必须能直接服务写作，而不是泛泛描述。

## 字段说明 vs 字段手册

工作簿里仍然可以保留轻量字段说明表，例如：

- 字段名
- 建议填写方式
- 推荐取值/说明

但在综述导向模式下，这只算 legacy 输入。

技能会把它升级成 `field-manual.md`，其中应该明确：

- 字段作用
- 服务哪一章或哪类写作问题
- 判定问题
- 正例/触发条件
- 易混淆项
- 所需证据
- 证据不足时如何保守处理

在字段手册确认前，不应直接批量跑综述导向分类。

## Browser fallback

抓取链路仍然遵循：

- 先静态 HTTP 抓取
- 如果失败，再进入 Browser fallback

当前能力边界会如实说明：

- 脚本会输出 Browser fallback 指引
- 但 Python 抓取脚本内部还没有完全自动化的 Browser 动态下载

所以 Browser fallback 目前仍是“半自动兜底链路”。

## 持续补论文

综述导向模式支持在发现章节空白后继续扩表。

默认流程：

1. 检索候选论文
2. 解释为什么相关
3. 等用户确认
4. 追加到工作簿新行
5. 用同一套证据和写作支撑流程处理这些新行

## 仓库结构

- `SKILL.md`
  面向 Codex 的技能说明
- `scripts/`
  包括结构识别、抓取、证据生成、survey bootstrap、字段手册升级、追加行、重建和校验
- `references/`
  包括 workflow、field guide contract、evidence template、usage demo
- `assets/demo/`
  demo 工作簿和 demo manifest

## 主要脚本

- `scripts/detect_workbook_structure.py`
- `scripts/prepare_local_workspace.py`
- `scripts/survey_mode_bootstrap.py`
- `scripts/upgrade_field_manual.py`
- `scripts/fetch_paper_sources.py`
- `scripts/build_evidence_files.py`
- `scripts/update_workbook.py`
- `scripts/append_paper_rows.py`
- `scripts/rebuild_local_workbook.py`
- `scripts/quick_validate.py`

## Demo

仓库内置：

- `assets/demo/literature-demo.xlsx`
- `assets/demo/demo-manifest.json`

demo 现在同时展示普通模式和综述导向模式的预期结构，包括写作支撑列。

## 校验技能

```bash
python scripts/quick_validate.py
```

## 当前限制

- 某些 Windows 环境下，系统自带的 skill validator 可能因为默认编码不是 UTF-8 而读取 Markdown 失败。
- Browser fallback 仍是半自动。
- 弱字段说明需要先升级成字段手册再严肃使用。
- 这个技能覆盖的是综述生产前半程，不直接负责生成整篇综述正文。
