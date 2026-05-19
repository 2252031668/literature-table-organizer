# Workflow

## Goal

Support the front half of new survey writing from:

- a survey topic
- a local workbook
- local paper PDFs
- and optionally a draft source

This skill now uses a single survey-oriented workflow only.

## Read-only skill rule

Do not edit files inside the skill directory during normal use.

Editable project files belong in the workspace:

- `project/framework.md`
- `paper-reports/*.md`
- `row-analysis/*.json`
- workbook working copy

## Single source of truth

The only formal project protocol is:

- `project/framework.md`

It should contain:

- survey context
- compact outline
- classification rules
- reading-report template
- workbook mapping

## Recommended stages

### 1. Initialize project

Run:

- `python scripts/cli.py init-project --topic ... --workbook ...`

This creates the workspace project structure and a starter `framework.md`.

### 2. Build framework

Run:

- `python scripts/cli.py build-framework --workbook ...`

Then discuss and revise `project/framework.md`.

Do not proceed to large-scale analysis before the framework is stable enough to answer:

- what the survey includes and excludes
- what the main outline is
- how each classification field should be judged
- what counts as minimum evidence

### 3. Normalize workbook headers if needed

If Chinese headers are unstable in the current environment, run:

- `python scripts/cli.py normalize-workbook-headers --workbook ...`

Use the normalized workbook copy for later stages when necessary.

### 4. Prepare PDFs

Each analyzed paper should have a local:

- `papers/<row>-<slug>/paper.pdf`

The workflow prefers direct PDF reading.
`paper.txt` is not a required asset anymore.

### 5. Analyze representative rows first

Run:

- `python scripts/cli.py row-analyze --workbook ... --row ... --pdf ...`

This creates:

- `paper-reports/<row>-<slug>.md`
- `row-analysis/<row>-<slug>.json`

The Markdown report must have two halves:

- Part A: Chinese reading notes
- Part B: English field decisions

### 6. Pilot discussion

Use a small set of representative papers first.

Revise `framework.md` before larger runs if:

- boundaries are still unstable
- the outline is still drifting
- field decisions are still inconsistent
- writing-section mapping is unclear

### 7. Batch analysis

After the framework is stable, analyze more rows using the same row-level contract.

Batch analysis should still be understood as repeated row-level reading, not blind heuristic filling.

### 7.5 Expand the workbook safely

Run:

- `python scripts/cli.py append-papers --workbook ... --rows-json ...`

This step is only for safe row insertion.
It does not classify papers automatically.

The command should:

- add genuinely new rows
- skip duplicate titles or links
- record both added and skipped entries in `project/expansion-log.md`

### 8. Workbook writeback

Run:

- `python scripts/cli.py writeback-xlsx --workbook ...`

This should only write from `row-analysis/*.json`.
It should not invent new field values on its own.

## Pause conditions

Pause and discuss when:

- the survey topic is still vague
- `framework.md` is not stable enough
- the paper PDF is missing
- a field decision cannot be justified from direct PDF reading
- the workbook header mapping looks unstable
- a row is clearly boundary-like and needs explicit scope discussion
