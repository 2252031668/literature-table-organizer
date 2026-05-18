# Literature Table Organizer

A reusable Codex skill for organizing literature spreadsheets with local evidence chains.

This skill is designed for workflows where a user maintains a paper table and wants more than a one-time fill. It helps turn a spreadsheet into a traceable review workspace:

- detect the main paper sheet and the field-guide sheet
- verify papers from full text or reliable web sources
- generate local evidence files for each paper
- write results back into the workbook
- optionally sync a locally edited workbook back to Feishu

## What problem it solves

Many literature tables are hard to reuse because the classification logic only lives in someone's head. This skill makes the review process inspectable by keeping:

- the source asset itself
- a per-paper evidence Markdown file
- workbook columns that point back to those local artifacts

The result is a spreadsheet where the classification fields are not just filled, but traceable.

## Supported inputs

The skill supports two entry points:

1. A local `xlsx` workbook
2. A Feishu spreadsheet link

The expected workbook structure is:

- one primary paper sheet
- one field-guide sheet in the same workbook

The primary paper sheet must contain:

- a paper-title column

It may also contain:

- a paper-link column
- an abstract column

The field-guide sheet must define the user-facing meaning of the fields you want filled. It is detected by semantic headers corresponding to:

- field name
- fill guidance
- recommended values or notes

## Core workflow

1. Detect workbook structure
2. Confirm the correct paper sheet if more than one candidate exists
3. Confirm the field-guide sheet
4. Prepare a local editable workbook
5. Fetch paper sources
6. Generate evidence files
7. Write results back into the workbook
8. Preview Feishu sync
9. Sync to Feishu only after explicit confirmation

## Evidence model

For each paper, the skill tries to keep a local source artifact:

- `paper.pdf` when a downloadable paper is available
- `source.md` when the paper is only available through a reliable web preview

It also generates:

- `paper.txt` for PDFs
- one evidence Markdown file per row

The workbook can automatically include or reuse these system columns:

- local file path
- evidence path
- warning or verification status

## Repository layout

- `SKILL.md`
  - Codex-facing skill instructions
- `agents/openai.yaml`
  - UI metadata for the skill
- `scripts/`
  - reusable helpers for structure detection, source fetching, evidence generation, workbook updates, and Feishu sync
- `references/`
  - workflow and field-guide reference files
- `assets/demo/`
  - bundled example workbook and manifest

## Included demo

This repository includes a small demo workbook:

- `assets/demo/literature-demo.xlsx`

It shows:

- a minimal paper sheet
- a field-guide sheet
- user-defined classification fields
- the traceability columns used by the skill

You can also regenerate it with:

```bash
python scripts/create_demo_workbook.py
```

## Key scripts

- `scripts/detect_workbook_structure.py`
  - identifies candidate paper sheets and the field-guide sheet
- `scripts/prepare_local_workspace.py`
  - prepares local artifact folders and supports Feishu export
- `scripts/fetch_paper_sources.py`
  - resolves or downloads paper sources
- `scripts/build_evidence_files.py`
  - creates evidence Markdown and PDF text extracts
- `scripts/update_workbook.py`
  - writes workbook updates by header name
- `scripts/feishu_sync.py`
  - previews or executes sync back to Feishu
- `scripts/quick_validate.py`
  - validates the skill and compiles the scripts

## Design principles

- The field-guide sheet is the source of truth for user-defined columns.
- The skill does not hardcode one research taxonomy.
- Weak evidence should produce warnings, not overconfident classifications.
- Feishu editing is staged through a local workbook first.
- Traceability is a first-class output, not an afterthought.

## Validation status

This version has been exercised with:

- local workbook structure detection
- local working-copy preparation
- workbook header extension and row updates
- evidence file generation
- Feishu export to local workbook
- Feishu sync preview

## Sharing

If you want to distribute the skill directly, the repository can be shared as source, and the packaged skill archive can also be distributed separately.
