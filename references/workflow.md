# Workflow

## Goal

Turn a literature workbook into either:

- a standard evidence-backed review table, or
- a survey-oriented classification and writing-support workspace

## Mode split

### Standard mode

Use when the user wants workbook verification, evidence files, and field backfill, but is not using the table as the front half of a new survey-paper workflow.

### Survey-oriented mode

Use when the user wants to write a new survey or review article from:

- a survey topic
- a literature workbook
- and optionally a draft source such as Feishu wiki, local markdown, or local docx-derived text

Survey-oriented mode should be driven by:

- `scripts/run_survey_workflow.py`

## Standard mode flow

1. Detect the workbook source.
2. Detect workbook structure.
3. Confirm the primary paper sheet and field-guide sheet.
4. Prepare the local editable workbook.
5. Ensure artifact directories exist.
6. Process papers row by row.
7. Write workbook updates.
8. If needed, preview Feishu sync before pushing back.

## Survey-oriented mode flow

1. Detect the workbook source and structure.
2. Collect the survey topic and optional draft source.
3. Create project-level survey files in `<workbook_stem>_artifacts/project/`.
4. Produce related-survey analysis and candidate breakthrough angles.
5. Draft `outline.md`.
6. Compare workbook fields against outline-driven needs and create `field-gap-analysis.md`.
7. Upgrade the field guide into `field-manual.md`.
8. Confirm the field manual.
9. Run pilot calibration on 5-10 representative papers.
10. Confirm the pilot.
11. Only after those gates pass, run batch processing.
12. Support later paper expansion and reprocessing as the survey evolves.

## Mandatory project files in survey-oriented mode

- `project-brief.md`
- `related-survey-analysis.md`
- `outline.md`
- `field-manual.md`
- `field-gap-analysis.md`
- `pilot-calibration.md`
- `paper-expansion-log.md`
- `workflow-state.json`

## Field-guide upgrade rule

The workbook field-guide sheet can be treated as legacy input.

If it only gives shallow hints such as:

- field name
- fill guidance
- recommended values

then the skill must not proceed directly to batch survey-oriented classification.

Instead:

1. generate `field-manual.md`
2. expand each field into a decision-ready manual
3. compare it against the outline-driven needs
4. discuss and confirm it with the user
5. only then continue

## Pilot gate

Survey-oriented mode requires pilot calibration before full-table processing.

Pilot must:

- cover 5-10 representative papers
- include boundary cases
- include strong- and weak-evidence rows
- record user corrections
- record at least one stable rule learned
- feed those corrections back into the field manual and outline

Batch processing must stop if:

- the pilot sample count is below the minimum
- the pilot is still draft/ready but not confirmed
- the pilot lacks rule-learning records

## Browser gate

Prefer sources in this order:

1. PDF or local full paper text
2. official readable fulltext webpage
3. project page / OpenReview / repository documentation with enough detail
4. high-quality secondary review page
5. abstract-only page

If static fetching cannot reach PDF or sufficient fulltext, the result must enter:

- `browser_pending`

At that point the agent using the skill must:

1. open the page with Browser
2. save `paper.pdf`, `source.md`, or `review.md` into the row asset directory
3. finalize the capture with `finalize_browser_capture.py`
4. continue the same evidence pipeline

Rows with unresolved Browser capture are blocked from normal batch output.

## Workbook columns

Always maintain:

- `本地文件路径`
- `证据链路径`
- `核验警告/状态`

In survey-oriented mode also ensure:

- `写作引用章节`
- `引用论据`

## Writing-support rule

`写作引用章节` must point to sections or subsections in `outline.md`.

`引用论据` should be specific and writing-ready:

- include method differences when relevant
- include concrete evidence or numerical comparisons when available
- include why the paper matters for the target section
- avoid vague generic summaries

Weak or pending evidence should not automatically produce strong writing-ready arguments.

## Paper expansion rule

When the user asks for more papers on a missing aspect:

1. search for candidate papers
2. explain why they are relevant
3. ask for confirmation
4. append confirmed rows into the workbook
5. process those rows with the same evidence and writing-support protocol
6. record the addition in `paper-expansion-log.md`

## Pause conditions

Pause and discuss when:

- the survey topic is unclear
- the article goal or differentiation angle is unclear
- the outline has not been confirmed
- the field manual is still weak or unconfirmed
- pilot calibration has not yet been accepted
- a key classification field still lacks a stable decision question
- any row is stuck in `browser_pending`
