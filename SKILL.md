---
name: literature-table-organizer
description: "Use for survey-oriented literature analysis from topic + local xlsx + local PDFs. This skill supports a single workflow for early-stage survey writing: build a framework, analyze papers one by one from PDF, generate paper reports and row-analysis JSON, normalize workbook headers when needed, and write back curated results to the workbook."
---

# Literature Table Organizer

This skill now supports one workflow only:

- survey-oriented literature analysis for new review or survey writing

It does not target ordinary literature-table cleanup anymore.

## Read-only skill rule

During normal use:

- do not edit project files inside `C:\Users\27216\.codex\skills\literature-table-organizer`
- do not ask the user to edit files inside the skill directory
- treat the skill directory as read-only tooling and instructions

All editable project outputs must live in the workspace next to the workbook:

- `project/framework.md`
- `paper-reports/*.md`
- `row-analysis/*.json`
- workbook working copy

Read [references/workflow.md](references/workflow.md) first.

## Core idea

The workflow is driven by one single source of truth:

- `project/framework.md`

That file should contain:

- survey context
- compact outline
- classification rules
- reading-report template
- workbook writeback mapping

The main paper-level action is:

- `python scripts/cli.py row-analyze --workbook ... --row ... --pdf ...`

That action should produce:

- `paper-reports/<row>-<slug>.md`
- `row-analysis/<row>-<slug>.json`

## Preferred workflow

1. Initialize a survey project.
2. Build or revise `project/framework.md`.
3. Normalize workbook headers if Chinese header handling is unstable.
4. Download or prepare local PDFs.
5. Analyze representative rows first.
6. Run pilot discussion and revise `framework.md`.
7. Analyze more rows.
8. Write back curated results to the workbook.

## CLI entry

Use a single CLI entry:

- `python scripts/cli.py <subcommand>`

Main commands:

- `init-project`
- `build-framework`
- `normalize-workbook-headers`
- `row-analyze`
- `writeback-xlsx`

Additional commands are reserved for the same workflow:

- `find-paper-link`
- `pdf-download`
- `pilot-run`
- `batch-analyze`
- `append-papers`
- `reset-project`

## Row analysis contract

`row-analyze` is the core capability.

Inputs:

- `framework.md`
- workbook row metadata
- local `paper.pdf`

Outputs:

- a Markdown paper report with two fixed halves
- a minimal JSON file for workbook writeback

The report must use:

- Part A: Chinese reading notes
- Part B: English field decisions using stable English field keys

Do not treat abstract-only text as sufficient for high-confidence classification.

## Workbook strategy

Internally, use English canonical keys only.

Externally:

- Chinese headers may be preserved through explicit mapping
- if header handling becomes unstable, use `normalize-workbook-headers` to create an English-header workbook copy

`writeback-xlsx` should only consume existing `row-analysis/*.json`.
It should not re-infer fields on its own.

## Files to read

- `references/workflow.md`
- `references/cli.md`
- `references/report-template.md`

## Notes

- Prefer local `.xlsx` as the main workbook surface.
- Feishu can still be used as an optional draft source, not as the main execution surface.
- File names for new project artifacts should stay in English to avoid Windows and terminal path issues.
- The skill may help generate templates and stable contracts, but actual high-quality classification depends on directly reading the PDF.
