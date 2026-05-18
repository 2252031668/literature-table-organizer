# Literature Table Organizer

A Codex skill for turning a literature workbook into either:

- a standard evidence-backed review table
- a survey-oriented classification and writing-support workspace

Chinese documentation: [README.zh-CN.md](README.zh-CN.md)

## What Changed in This Version

The skill is now designed to support the **front half of survey production** more directly:

- one orchestration entry for survey-oriented workflow
- stronger project-level survey analysis outputs
- field-manual and pilot gating before batch processing
- Browser fallback as a formal fetch-stage state instead of an informal suggestion
- richer evidence decision chains and writing-support fields

This version still does **not** auto-write a full survey paper draft. It focuses on topic alignment, classification, evidence, writing support, and ongoing literature expansion.

## Two Modes

### 1. Standard mode

Use this when you want to:

- verify papers in an existing workbook
- collect stronger evidence
- fill user-defined fields
- maintain local traceability files
- write clickable local paths back into `.xlsx`

### 2. Survey-oriented mode

Use this when the workbook is part of preparing a new survey or review paper.

This mode takes:

- a survey topic
- a literature workbook
- and optionally a draft source such as a Feishu wiki, local Markdown file, or local `.docx`

Survey-oriented mode is now driven through:

- `scripts/run_survey_workflow.py`

Its main phases are:

1. bootstrap
2. manual
3. pilot
4. batch
5. expansion

## What the Skill Solves

Many literature tables stop at filled values and do not preserve:

- why a paper was classified that way
- what evidence actually supports the classification
- which survey section the paper contributes to
- how to extend the table when a new writing gap appears

This skill turns the workbook into a reusable workspace with:

- local source artifacts
- per-paper evidence Markdown
- manifest state
- project-level survey files
- workbook hyperlinks and writing-support columns

## Survey-Oriented Project Files

In survey-oriented mode, the skill creates:

- `<workbook_stem>_artifacts/project/project-brief.md`
- `<workbook_stem>_artifacts/project/related-survey-analysis.md`
- `<workbook_stem>_artifacts/project/outline.md`
- `<workbook_stem>_artifacts/project/field-manual.md`
- `<workbook_stem>_artifacts/project/field-gap-analysis.md`
- `<workbook_stem>_artifacts/project/pilot-calibration.md`
- `<workbook_stem>_artifacts/project/paper-expansion-log.md`
- `<workbook_stem>_artifacts/project/workflow-state.json`

`outline.md` is the central writing scaffold.

## Workbook Columns

The skill always maintains:

- `本地文件路径`
- `证据链路径`
- `核验警告/状态`

In survey-oriented mode it also maintains:

- `写作引用章节`
- `引用论据`

For local `.xlsx`, path cells remain human-readable relative paths and are also written as clickable hyperlinks.

## Evidence Policy

### Priority Order

1. local full paper text such as `paper.pdf`
2. official readable fulltext webpage
3. project page, OpenReview page, or repository documentation with enough detail
4. high-quality secondary review page
5. abstract-only page

### Status Values

- `pdf_download`
- `pdf_via_browser`
- `fulltext_web`
- `secondary_review`
- `abstract_only`
- `browser_pending`
- `unresolved`
- `mismatch_or_unverifiable`

### Full Backfill Rule

Full backfill is allowed only for:

- `pdf_download`
- `pdf_via_browser`
- `fulltext_web`
- `secondary_review`

Abstract-only evidence is not the default basis for complete survey-oriented classification.

Rows that remain `browser_pending`, `unresolved`, or `mismatch_or_unverifiable` should not be treated as writing-ready.

## Browser Fallback

Browser fallback is now part of the formal fetch chain.

When static fetching cannot reach the real paper asset:

1. the fetch script returns `browser_pending`
2. the agent using the skill is expected to complete Browser capture immediately
3. the capture is finalized back into the same row asset directory
4. the evidence and workbook pipeline resumes

Important limitation:

- Browser is not directly called from Python
- the skill relies on the agent using Browser and then returning the result through the provided finalization step

So Browser fallback is **agent-enforced and structured**, not a fully autonomous browser subprocess inside Python.

## Field Guide vs Field Manual

The workbook may still contain a lightweight guide sheet with:

- field name
- fill guidance
- recommended values

That is treated as a legacy input.

In survey-oriented mode, the skill upgrades it into `field-manual.md`, which should express:

- field purpose
- writing section served
- decision question
- positive triggers
- confusing neighbors
- required evidence
- conservative fallback rule
- neighboring-category exclusion rule
- writing-use note

Batch survey-oriented processing should not proceed until the upgraded field manual is discussed and confirmed.

## Pilot Gating

Survey-oriented mode uses pilot calibration as a hard gate.

Before batch processing, the workflow expects:

- a prepared pilot set
- a sufficient sample count
- at least one learned rule recorded
- pilot confirmation reflected in workflow state

If those checks fail, batch processing should stop.

## Classification Protocol

The skill no longer treats classification as only fill a value.

For major fields, evidence Markdown should capture:

- decision question
- final value
- key evidence segments
- causal reasoning chain
- exclusion reasoning
- evidence sufficiency
- writing section
- writing argument when evidence is strong enough

This is especially important in survey-oriented mode, where `引用论据` should be writing-ready rather than generic.

## Incremental Paper Expansion

Survey-oriented mode supports expanding the workbook when a section or topic is under-covered.

Default flow:

1. search for candidate papers
2. explain why they are relevant
3. wait for user confirmation
4. append them as new workbook rows
5. process the new rows with the same evidence and writing-support workflow
6. record the addition in `paper-expansion-log.md`

## Repository Layout

- `SKILL.md`
  Codex-facing skill instructions
- `scripts/`
  detection, orchestration, fetch, Browser finalization, pilot prep, expansion planning, evidence, workbook updates, rebuild, reset, and validation
- `references/`
  workflow, field-guide contract, evidence template, and usage examples
- `assets/demo/`
  demo workbook and demo manifest

## Main Scripts

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

The repository includes:

- `assets/demo/literature-demo.xlsx`
- `assets/demo/demo-manifest.json`

The demo now shows both standard and survey-oriented workflow expectations, including writing-support columns and pilot gating.

## Validate the Skill

```bash
python scripts/quick_validate.py
```

## Known Limits

- The bundled system-level skill validator on some Windows setups may still hit local encoding issues when reading UTF-8 Markdown through a non-UTF-8 default code page.
- Browser fallback is structured and required, but still depends on the agent performing browser actions rather than a Python-only automation layer.
- Writing-ready arguments are stronger than before, but the highest-quality survey use still benefits from real per-paper calibration on representative samples.
- The skill supports the front half of survey production, not full article drafting.
