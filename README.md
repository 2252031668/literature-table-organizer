# Literature Table Organizer

A Codex skill for turning a literature workbook into a traceable review workspace with local evidence files, conservative backfill rules, and clickable local paths in `.xlsx`.

Chinese documentation: [README.zh-CN.md](README.zh-CN.md)

## What It Is For

This skill is designed for workflows where a workbook contains:

- one paper sheet with rows of papers
- one field-guide sheet that explains how user-defined columns should be filled

Instead of treating the workbook as a one-off table fill, the skill builds a repeatable pipeline:

1. detect workbook structure
2. fetch paper evidence with PDF/fulltext-first policy
3. generate local evidence artifacts
4. write results and traceability paths back to the workbook

## V2 Highlights

- PDF/fulltext-first evidence policy instead of abstract-first filling
- explicit evidence status levels and backfill thresholds
- local `.xlsx` path cells stay human-readable and also become clickable hyperlinks
- evidence Markdown now records source level, backfill eligibility, and field-level rationale
- manifest and workbook rebuild helpers for cleanup and consistency repair

## Repository Layout

- `SKILL.md`
  Codex-facing skill instructions
- `agents/openai.yaml`
  skill metadata
- `scripts/`
  structure detection, fetching, evidence generation, workbook update, validation, and rebuild helpers
- `references/`
  workflow, evidence template, field-guide contract, sync notes, and usage examples
- `assets/demo/`
  bundled workbook demo and demo manifest

## Core Workflow

1. Detect the workbook source.
   Local `xlsx` or Feishu spreadsheet.
2. Detect workbook structure.
   Identify the primary paper sheet and the field-guide sheet.
3. Prepare a local editable workspace.
   Create sibling artifact folders for papers, evidence, and snapshots.
4. Fetch evidence.
   Prefer `paper.pdf`, then readable fulltext pages, then qualified secondary review pages.
5. Build evidence files.
   Preserve `paper.pdf`, `paper.txt`, `source.md`, or `review.md` as appropriate and generate one evidence Markdown file per paper.
6. Update the workbook.
   Reuse or append `本地文件路径`, `证据链路径`, and `核验警告/状态`, and write clickable local hyperlinks for local `.xlsx`.
7. Optionally preview Feishu sync.
   Feishu is not auto-synced by default.

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

Full workbook backfill is allowed only for:

- `pdf_download`
- `pdf_via_browser`
- `fulltext_web`
- `secondary_review`

These states are conservative by default and should not drive full classification:

- `abstract_only`
- `unresolved`
- `mismatch_or_unverifiable`

Abstract-only evidence is not treated as a default basis for complete verification in v2.

## Browser Fallback

The fetch pipeline is designed to treat Browser fallback as the standard next step after static fetching fails.

Current v2 behavior is intentionally described conservatively:

- static HTTP fetching runs first
- the fetch script can emit Browser fallback instructions and mark that dynamic retrieval is required
- Browser-based dynamic retrieval is not yet executed fully automatically inside the Python fetch script

In practice, this means Browser fallback is supported as a semi-automatic recovery path rather than a fully automated in-script downloader.

## Local Workbook Behavior

For local `.xlsx` workbooks, the skill preserves relative path text in the workbook while also writing local hyperlinks for:

- `本地文件路径`
- `证据链路径`

This makes it possible to click from the workbook directly into the downloaded paper or evidence Markdown file.

## Known Limits

- Abstract pages are not accepted as the default basis for full backfill.
- Some sites still require manual or Browser-assisted retrieval.
- Title/source mismatch rows are intentionally downgraded and should not be auto-classified.
- Feishu sync is staged and conservative; local editing comes first.
- The bundled demo is only for workflow illustration and does not represent broad real-world fetch coverage.

## Quick Start

### Prerequisites

- Python 3.9+
- Python packages required by the scripts, including workbook and PDF handling dependencies
- Codex environment capable of using the skill

### Validate the Skill

```bash
python scripts/quick_validate.py
```

### Typical Local Workflow

Use the skill against a local workbook that contains:

- a paper sheet with `论文全名`
- optionally `论文链接` and `摘要`
- a field-guide sheet with semantic equivalents of `字段`, `建议填写方式`, and `推荐取值/说明`

The skill scripts then prepare artifacts, fetch evidence, build evidence files, and update the workbook.

### Demo

The repository includes:

- `assets/demo/literature-demo.xlsx`
- `assets/demo/demo-manifest.json`

You can regenerate the demo workbook with:

```bash
python scripts/create_demo_workbook.py
```

## Main Scripts

- `scripts/detect_workbook_structure.py`
  Detect paper-sheet and field-guide-sheet candidates.
- `scripts/prepare_local_workspace.py`
  Prepare local copies and artifact folders.
- `scripts/fetch_paper_sources.py`
  Resolve PDF/fulltext sources and emit Browser fallback instructions when needed.
- `scripts/build_evidence_files.py`
  Generate evidence Markdown and PDF text extracts.
- `scripts/update_workbook.py`
  Update workbook cells and local hyperlinks by header name.
- `scripts/rebuild_local_workbook.py`
  Rebuild workbook rows from existing local evidence and manifest state.
- `scripts/quick_validate.py`
  Validate skill structure and compile scripts.

## Output Structure

By default, local artifacts live beside the workbook in:

- `<workbook_stem>_artifacts/papers/`
- `<workbook_stem>_artifacts/evidence/`
- `<workbook_stem>_artifacts/snapshots/`

If a legacy sibling `artifacts/` directory already exists, the scripts prefer reusing it.

The manifest records per-row state such as:

- row
- title
- local source path
- evidence path
- status
- warning
- backfill eligibility
- resolved URL

## Publishing Notes

This repository is suitable both as:

- source distribution for the skill itself
- the basis of a packaged skill archive such as `literature-table-organizer-v2.zip`

For public releases, exclude caches and transient artifacts such as:

- `__pycache__/`
- `.pyc`
- local workbook outputs
- downloaded paper/evidence caches unrelated to the bundled demo
