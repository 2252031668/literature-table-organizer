# literature-table-organizer v3.0

`literature-table-organizer` is a Codex skill for the front half of survey writing.

It is now released as a **single-workflow survey tool** built around:

- a survey topic
- a local workbook
- local paper PDFs
- optional draft context

Chinese documentation: [README.zh-CN.md](README.zh-CN.md)

## What v3.0 Is

v3.0 removes the old mixed workflow design and keeps one clear path only:

- initialize a survey project
- build `project/framework.md`
- read papers row by row from local PDFs
- produce paper reports and row-analysis JSON
- write curated results back to the workbook

This version is designed for:

- survey-oriented literature analysis
- classification calibration
- evidence-backed note taking
- workbook writeback for later writing

It is not a full survey-drafting system.

## Core Architecture

The workflow is driven by one single protocol file:

- `project/framework.md`

That file is the sole rule source for:

- survey context
- compact outline
- classification rules
- reading report structure
- workbook mapping

The main output contracts are:

- `paper-reports/<row>-<slug>.md`
- `row-analysis/<row>-<slug>.json`

The workbook is written back only from JSON.

## Main Workflow

1. Run `init-project` to create the workspace project scaffold.
2. Use `build-framework` and revise `project/framework.md`.
3. Normalize workbook headers if needed.
4. Prepare local `paper.pdf` files.
5. Run `row-analyze` on representative papers first.
6. Use `pilot-run` to organize pilot calibration.
7. Use `batch-analyze` to generate a larger review queue.
8. Use `writeback-xlsx` to write curated fields back to the workbook.

## CLI

Use one entry only:

```bash
python scripts/cli.py <subcommand>
```

Main commands:

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

## Paper Reports and JSON

`row-analyze` is the core paper-level action.

Inputs:

- `project/framework.md`
- workbook row metadata
- local `paper.pdf`

Outputs:

- a paper report in Markdown
- a row-analysis JSON file

The report format is fixed:

- Part A: Chinese reading notes
- Part B: English field decisions

This makes the report readable for human review while keeping downstream JSON extraction stable.

## Workbook Header Strategy

Internally, the skill uses English canonical keys only.

Workbook-facing behavior:

- preserve existing Chinese headers when possible
- optionally normalize supported headers into English

Use:

```bash
python scripts/cli.py normalize-workbook-headers --workbook ...
```

when the current environment handles Chinese headers unreliably.

## `append-papers` in v3.0

`append-papers` now acts as a safe row insertion command.

Behavior:

- detect duplicates by normalized title or normalized link
- skip duplicates instead of failing the whole batch
- return both `added_rows` and `skipped_rows`
- record both added and skipped entries in `project/expansion-log.md`

It only appends basic row metadata and optional writing fields.
It does not classify papers automatically.

## PDF and Download Policy

The formal reading input is local PDF only:

- `papers/<row>-<slug>/paper.pdf`

`pdf-download` performs static PDF resolution only.

It can help with:

- arXiv links
- direct PDF links
- common paper-page PDF extraction

If static download fails, manual follow-up is still required.
v3.0 does not advertise the old Browser fallback chain as part of the main workflow anymore.

## Demo and Validation

Bundled demo assets:

- `assets/demo/literature-demo.xlsx`
- `assets/demo/demo-manifest.json`

Validation:

```bash
python scripts/quick_validate.py
```

## Known Limits

- The CLI does not automatically understand PDF content; `row-analyze` is an agent-led reading workflow.
- The best results still depend on careful framework discussion and representative pilot calibration.
- The skill is for the front half of survey production, not for generating a full survey manuscript draft.
