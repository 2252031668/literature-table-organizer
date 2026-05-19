# Paper Report Template

Each paper report should be written to:

- `paper-reports/<row>-<slug>.md`

## Fixed structure

### Part A - Chinese reading notes

Recommended sections:

- Basic Information
- 这篇论文解决什么问题
- 方法是什么，亮点是什么
- 实验怎么做
- 结果最关键的点是什么
- 局限和展望
- 这篇论文对本综述有什么意义

Goal:

- make it obvious that the paper was actually read
- keep the report readable for direct human inspection
- avoid vague abstract paraphrases

### Part B - English field decisions

Recommended repeated block:

- `field`
- `decision`
- `reasoning`
- `confidence`
- `warning`

This section exists to keep downstream JSON extraction stable.

Use English canonical field keys such as:

- `paradigm_mapping`
- `paradigm_subtype`
- `functional_layer`
- `planning_granularity`
- `bimanual_design_type`
- `verified_core_method`
- `verified_tasks_datasets`
- `verified_key_results`
- `verified_limitations`
- `writing_section`
- `writing_argument`

## Report discipline

- Short reasoning is enough; long hidden chains are unnecessary.
- Every important decision should be grounded in direct PDF reading.
- If a field is unsupported, prefer blank plus warning over forced classification.
- `writing_argument` should sound usable in a real survey draft, not like a generic summary.
