---
name: literature-table-organizer
description: "Organize a literature workbook into either a standard evidence-backed review table or a survey-oriented classification and writing-support workspace. Use when a user provides a local xlsx file or Feishu spreadsheet and wants paper verification, field backfill, survey taxonomy alignment, writing-outline support, evidence files, workbook path columns, or incremental paper expansion."
---

# Literature Table Organizer

Use this skill in one of two modes:

1. Standard mode
   For normal literature-table verification, evidence collection, and workbook backfill.
2. Survey-oriented mode
   For preparing a new survey paper from a topic plus a literature workbook, including related-survey analysis, outline drafting, field-manual upgrade, pilot calibration, writing-support columns, and iterative paper expansion.

Start with `references/workflow.md` before doing substantial work.

## Mode selection

Use survey-oriented mode when any of the following is true:

- the user says the workbook is for writing a survey or review article
- the user provides a survey topic
- the user asks for breakthrough-point analysis, writing outline, writing-section mapping, or writing-ready evidence

Otherwise use standard mode.

## Standard mode

Standard mode keeps the existing behavior:

1. Detect workbook structure.
2. Prepare the local editable workspace.
3. Fetch paper evidence with PDF/fulltext-first policy.
4. Build evidence files.
5. Write workbook updates and local hyperlinks.
6. Preview Feishu sync only when needed.

## Survey-oriented mode

Survey-oriented mode adds mandatory front-loaded stages before batch classification:

1. Topic and project alignment
2. Related-survey and representative-paper reading
3. Breakthrough-point analysis
4. Outline drafting and discussion
5. Field-manual upgrade
6. Pilot calibration on 5-10 representative papers
7. Batch processing
8. Ongoing paper expansion and reprocessing

Do not skip directly to full-table processing in survey-oriented mode.

## Required survey-oriented outputs

Create these project files under `<workbook_stem>_artifacts/project/`:

- `project-brief.md`
- `related-survey-analysis.md`
- `outline.md`
- `field-manual.md`
- `pilot-calibration.md`
- `paper-expansion-log.md`

`outline.md` is the central writing scaffold.

## Workbook behavior

Always maintain:

- `本地文件路径`
- `证据链路径`
- `核验警告/状态`

In survey-oriented mode also maintain:

- `写作引用章节`
- `引用论据`

For local `.xlsx` workbooks, keep relative path text while also writing clickable local hyperlinks.

## Field-guide policy

Treat the workbook field-guide sheet as a lightweight input, not necessarily the final classification protocol.

In survey-oriented mode:

- a simple three-column guide is considered legacy input
- the skill must upgrade it into `field-manual.md`
- the user must confirm the upgraded field manual before batch classification

Do not treat a weak field-guide sheet as sufficient for high-confidence survey classification.

## Classification protocol

Survey-oriented outputs must go beyond “value filling”.

For major classification fields, the evidence output should record:

- decision question
- final value
- key evidence segments
- causal reasoning chain
- exclusion reasoning
- evidence sufficiency

Detailed reasoning belongs primarily in evidence Markdown and project files, not only in workbook cells.

## Paper expansion

Survey-oriented mode must support incremental paper expansion:

1. search for additional papers on a requested aspect
2. present candidate papers and rationale
3. wait for user confirmation
4. append confirmed papers as new workbook rows
5. run the same evidence and writing-support workflow on those rows

## Evidence order

Evidence priority is mandatory:

1. `paper.pdf` or other local full paper text
2. official readable fulltext webpage
3. project page / OpenReview / repository documentation with enough detail
4. high-quality secondary review or interpretation page
5. abstract-only page

Abstract-only pages are never the default basis for complete survey-oriented backfill.

## Files to use

- `references/workflow.md`
- `references/fieldguide-contract.md`
- `references/evidence-template.md`
- `references/usage-demo.md`
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

## Notes

- In survey-oriented mode, do not guess the survey taxonomy before reading related surveys and discussing the outline.
- Do not enter batch processing until pilot calibration is completed.
- Writing-support fields should be concrete enough to support drafting, not generic summaries.
