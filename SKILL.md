---
name: literature-table-organizer
description: "Organize a literature workbook that contains a paper sheet plus a field-guide sheet. Use when a user uploads a local xlsx file or shares a Feishu spreadsheet link and asks to verify papers, search full text, fill user-defined classification columns, create local evidence files, or maintain the columns `\u672c\u5730\u6587\u4ef6\u8def\u5f84`, `\u8bc1\u636e\u94fe\u8def\u5f84`, and `\u6838\u9a8c\u8b66\u544a/\u72b6\u6001`. The primary paper sheet must include `\u8bba\u6587\u5168\u540d` and may also include `\u8bba\u6587\u94fe\u63a5` and `\u6458\u8981`; another worksheet must define field semantics with columns matching `\u5b57\u6bb5`, `\u5efa\u8bae\u586b\u5199\u65b9\u5f0f`, and `\u63a8\u8350\u53d6\u503c/\u8bf4\u660e`."
---

# Literature Table Organizer

Use this skill to turn a literature spreadsheet into a traceable review workspace instead of a one-off table fill.

Start with `references/workflow.md` before doing substantial work.

## Core workflow

1. Detect the input source.
   - Local `xlsx`
   - Feishu spreadsheet URL
2. Run `scripts/detect_workbook_structure.py`.
   - Find 1-3 candidate paper sheets
   - Find the field-guide sheet by semantic headers
   - Detect whether the system columns already exist
3. Pause when the structure is ambiguous.
   - More than one plausible primary sheet
   - Missing field-guide sheet
   - Field-guide semantics are incomplete
   - User-defined columns remain unclear after reading the guide
4. Prepare the local workspace with `scripts/prepare_local_workspace.py`.
   - Local workbook: ask whether to edit a copy or the original
   - Feishu workbook: export locally and edit the downloaded file
   - Create sibling artifact folders for papers, evidence, and snapshots
5. Collect paper evidence.
   - Use `scripts/fetch_paper_sources.py` to resolve or download a PDF when possible
   - Fall back to a local Markdown capture for reliable web previews
6. Build evidence artifacts with `scripts/build_evidence_files.py`.
   - Keep `paper.pdf` or `source.md`
   - Generate `paper.txt` from PDFs
   - Generate one evidence Markdown file per row
7. Write workbook updates with `scripts/update_workbook.py`.
   - Reuse existing system columns when present
   - Otherwise append the local-file, evidence-path, and warning/status columns
   - Update user-defined classification fields and traceability columns
8. If the source was Feishu, only sync back after explicit user confirmation.
   - Use `scripts/feishu_sync.py`
   - Default to preview mode first

## Required behavior

- Treat the field-guide worksheet as the source of truth for user-defined columns.
- Do not guess when the guide is missing or semantically unclear.
- For local workbooks, ask whether to edit a copy or the original each time.
- For Feishu workbooks, export locally first and do not auto-sync after editing.
- If a paper link is missing, search by title and fill the link only when the match is reliable.
- If evidence is weak or conflicting, keep the old cell value and write the reason into the warning/status column.
- Always keep local traceability artifacts beside the workbook in `<workbook_stem>_artifacts/`.
- Prefer relative paths inside workbook cells.

## Files to use

- `references/workflow.md`
  - End-to-end workflow, pause conditions, warning policy
- `references/fieldguide-contract.md`
  - How to identify the field-guide worksheet and interpret it
- `references/evidence-template.md`
  - Expected evidence Markdown structure
- `references/feishu-sync.md`
  - Sync contract and limitations
- `references/usage-demo.md`
  - Shareable walkthrough and demo scenarios
- `scripts/detect_workbook_structure.py`
  - Workbook structure detection
- `scripts/prepare_local_workspace.py`
  - Local copy/export and artifact directory preparation
- `scripts/fetch_paper_sources.py`
  - Source resolution and download
- `scripts/build_evidence_files.py`
  - Evidence asset and Markdown generation
- `scripts/update_workbook.py`
  - Workbook writes by header name
- `scripts/feishu_sync.py`
  - Preview or execute Feishu sync
- `scripts/quick_validate.py`
  - Validate the skill and compile scripts
- `scripts/create_demo_workbook.py`
  - Regenerate the bundled demo workbook if needed

## Demo assets

- `assets/demo/literature-demo.xlsx`
  - Minimal local workbook demo with a paper sheet and a field-guide sheet
- `assets/demo/demo-manifest.json`
  - What the demo workbook is intended to show

## Notes

- Keep the reasoning about classification inside the evidence Markdown, not only in the sheet.
- When syncing back to Feishu, preview first unless the user has already confirmed the final push.
