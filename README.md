# Literature Table Organizer

A Codex skill for turning a literature workbook into either:

- a standard evidence-backed review table
- a survey-oriented classification and writing-support workspace

Chinese documentation: [README.zh-CN.md](README.zh-CN.md)

## Two Modes

### 1. Standard mode

Use this when you want to:

- verify papers in an existing workbook
- collect better evidence
- fill user-defined fields
- maintain local traceability files
- write clickable local paths back into `.xlsx`

### 2. Survey-oriented mode

Use this when the workbook is part of preparing a new survey or review paper.

This mode adds a front-half survey workflow:

1. understand the survey topic and article goal
2. read related surveys and representative papers
3. identify differentiation and breakthrough angles
4. draft an outline
5. upgrade the field guide into a field manual
6. calibrate taxonomy decisions on 5-10 papers
7. batch process the workbook
8. keep expanding the paper pool as the outline evolves

## What the Skill Solves

Many literature tables stop at “filled values” and do not preserve:

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
- `<workbook_stem>_artifacts/project/pilot-calibration.md`
- `<workbook_stem>_artifacts/project/paper-expansion-log.md`

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
- `unresolved`
- `mismatch_or_unverifiable`

### Full Backfill Rule

Full backfill is allowed only for:

- `pdf_download`
- `pdf_via_browser`
- `fulltext_web`
- `secondary_review`

Abstract-only evidence is not the default basis for complete survey-oriented classification.

## Classification Protocol

The skill no longer treats classification as only “fill a value”.

For major fields, evidence Markdown should capture:

- decision question
- final value
- key evidence segments
- causal reasoning chain
- exclusion reasoning
- evidence sufficiency

This is especially important in survey-oriented mode, where `引用论据` should be writing-ready rather than generic.

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

Batch survey-oriented processing should not proceed until the upgraded field manual is discussed and confirmed.

## Browser Fallback

The fetch chain treats Browser fallback as the standard next step after static fetching fails.

Current behavior is intentionally described conservatively:

- static HTTP fetching runs first
- the fetch script can emit Browser fallback instructions
- Browser-driven dynamic retrieval is not yet fully automated inside the Python fetch script

So Browser fallback is supported as a semi-automatic recovery path rather than a fully automated in-script downloader.

## Incremental Paper Expansion

Survey-oriented mode supports expanding the workbook when a section or topic is under-covered.

Default flow:

1. search for candidate papers
2. explain why they are relevant
3. wait for user confirmation
4. append them as new workbook rows
5. process the new rows with the same evidence and writing-support workflow

## Repository Layout

- `SKILL.md`
  Codex-facing skill instructions
- `scripts/`
  detection, fetch, evidence, workbook updates, survey bootstrap, field-manual upgrade, row append, rebuild, and validation
- `references/`
  workflow, field-guide contract, evidence template, and usage examples
- `assets/demo/`
  demo workbook and demo manifest

## Main Scripts

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

The repository includes:

- `assets/demo/literature-demo.xlsx`
- `assets/demo/demo-manifest.json`

The demo now shows both standard and survey-oriented workflow expectations, including writing-support columns.

## Validate the Skill

```bash
python scripts/quick_validate.py
```

## Known Limits

- The system-level skill validator on some Windows setups may hit local encoding issues when reading UTF-8 Markdown through a non-UTF-8 default code page.
- Browser fallback is still semi-automatic.
- Weak field guides should be upgraded before serious survey-oriented use.
- The skill supports the front half of survey production, not full article drafting.
