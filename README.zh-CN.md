# literature-table-organizer

一个 Codex 技能，用于把文献工作簿整理成两类工作流之一：

- 普通的“证据驱动文献表整理”
- 面向新综述写作前半程的“分类 + 证据 + 写作支撑工作流”

英文文档见 [README.md](README.md)

## 这一版的重点变化

这一版已经明显朝“可直接服务综述生产前半程”升级，核心增强包括：

- 增加单一的综述导向总编排入口
- 项目级综述分析产物不再只是模板空壳
- field manual 和 pilot 成为 batch 前的硬门禁
- Browser fallback 进入正式抓取状态流
- evidence 默认支持更完整的判定链和写作支撑字段

这版技能仍然**不负责自动写完整篇综述正文**。它负责的是选题语境、分类协议、证据链、写作支撑和后续补论文工作流。

## 两种模式

### 1. 普通整理模式

适合这些场景：

- 核验已有文献表
- 补全文和更强证据
- 回填用户定义字段
- 维护本地证据链
- 在 `.xlsx` 中写入可点击路径

### 2. 综述导向模式

适合这些场景：

- 这张文献表是为了写一篇新的综述或评述文章
- 需要先分析已有综述，再决定自己的突破口
- 需要写作大纲、字段手册、试分类校准
- 需要把论文和写作章节对应起来
- 需要持续补充新论文并重新整理

这个模式的正式输入是：

- 综述主题
- 文献工作簿
- 可选草稿源，例如 Feishu wiki、本地 Markdown、本地 `.docx`

综述导向模式现在统一通过：

- `scripts/run_survey_workflow.py`

主要阶段包括：

1. `bootstrap`
2. `manual`
3. `pilot`
4. `batch`
5. `expansion`

## 这个技能解决什么问题

很多文献表最后只剩“结果值”，缺少：

- 为什么这样分类
- 具体证据在哪
- 这篇论文服务于综述的哪一节
- 某个章节缺论文时怎么补

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
- `field-gap-analysis.md`
- `pilot-calibration.md`
- `paper-expansion-log.md`
- `workflow-state.json`

其中 `outline.md` 是写作主线中枢。

## 工作簿列

技能始终维护：

- `本地文件路径`
- `证据链路径`
- `核验警告/状态`

在综述导向模式下，还会维护：

- `写作引用章节`
- `引用论据`

对于本地 `.xlsx`，路径列会保留相对路径文本，同时写成本地可点击超链接。

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
- `browser_pending`
- `unresolved`
- `mismatch_or_unverifiable`

### 完整回填门槛

默认只有以下状态允许完整回填：

- `pdf_download`
- `pdf_via_browser`
- `fulltext_web`
- `secondary_review`

摘要级证据不再是综述导向模式下的默认完整分类依据。  
如果行还停留在 `browser_pending`、`unresolved` 或 `mismatch_or_unverifiable`，就不应被当作写作就绪条目。

## Browser fallback

Browser fallback 现在进入正式抓取链路。

当静态抓取无法拿到 PDF 或足够的全文时：

1. 抓取脚本返回 `browser_pending`
2. 使用这个技能的智能体必须立刻接手 Browser
3. Browser 产物写回同一行的资产目录
4. 再通过回流脚本继续证据和工作簿流水线

当前的真实边界是：

- Browser 不能被 Python 脚本直接自动调用
- 因此这是“结构化、强制的智能体接力”，不是纯 Python 内部全自动浏览器

## 字段说明 vs 字段手册

工作簿里可以继续保留轻量字段说明 sheet，例如：

- 字段名
- 建议填写方式
- 推荐取值/说明

但在综述导向模式下，这只算 legacy 输入。  
技能会把它升级成 `field-manual.md`，其中应明确：

- 字段作用
- 服务于哪一章或哪类写作问题
- 判定问题
- 正例/触发条件
- 易混淆项
- 所需证据
- 证据不足时如何保守处理
- 邻近类别排除规则
- 写作用途说明

在 field manual 确认前，不应直接进入 batch。

## Pilot 门禁

综述导向模式下，pilot 校准是硬门禁。

在 batch 前，流程期望至少具备：

- 已准备好的 pilot 样本集
- 足够的样本数量
- 至少一条 learned rule
- workflow state 中的 pilot 确认状态

只要这些条件不满足，batch 就应停止。

## 分类协议

这个技能不再把分类理解成“只填一个值”。

对主要字段，evidence Markdown 应记录：

- 判定问题
- 最终取值
- 关键证据片段
- 前因后果式推理链
- 排除性解释
- 证据充分性
- 写作引用章节
- 在证据足够时生成写作论据

这对综述导向模式尤其重要，因为 `引用论据` 应该是可直接服务写作的，而不是泛泛摘要。

## 持续补论文

综述导向模式支持在发现章节空白后继续扩表。

默认流程：

1. 先规划候选论文
2. 解释为什么相关
3. 等用户确认
4. 追加到工作簿新行
5. 用同一套证据与写作支撑流程处理这些新行
6. 在 `paper-expansion-log.md` 中记录这次补充

## 仓库结构

- `SKILL.md`
  面向 Codex 的技能说明
- `scripts/`
  包括结构识别、总编排、抓取、Browser 回流、pilot 准备、扩表规划、证据生成、工作簿写回、重建、重置和校验
- `references/`
  包括 workflow、field guide contract、evidence template、usage demo
- `assets/demo/`
  demo 工作簿和 demo manifest

## 主要脚本

- `scripts/run_survey_workflow.py`
- `scripts/detect_workbook_structure.py`
- `scripts/prepare_local_workspace.py`
- `scripts/survey_mode_bootstrap.py`
- `scripts/upgrade_field_manual.py`
- `scripts/prepare_pilot_set.py`
- `scripts/fetch_paper_sources.py`
- `scripts/finalize_browser_capture.py`
- `scripts/build_evidence_files.py`
- `scripts/update_workbook.py`
- `scripts/append_paper_rows.py`
- `scripts/plan_paper_expansion.py`
- `scripts/reset_survey_outputs.py`
- `scripts/rebuild_local_workbook.py`
- `scripts/quick_validate.py`

## Demo

仓库内置：

- `assets/demo/literature-demo.xlsx`
- `assets/demo/demo-manifest.json`

demo 现在同时展示普通模式和综述导向模式的预期结构，包括写作支撑列和 pilot 门禁。

## 校验技能

```bash
python scripts/quick_validate.py
```

## 当前限制

- 某些 Windows 环境下，系统自带的 skill validator 仍可能因为默认编码不是 UTF-8 而读取 Markdown 失败。
- Browser fallback 已经被结构化并纳入主链路，但仍依赖智能体执行浏览器动作，而不是 Python 内部全自动浏览器层。
- `引用论据` 的自动生成比之前更强，但最高质量的综述使用仍建议结合代表样本做真实校准。
- 这个技能覆盖的是综述生产前半程，不直接负责生成整篇综述正文。
