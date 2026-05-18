# v1.0.0

Initial public release of `literature-table-organizer`.

## Summary

This release packages a reusable Codex skill for organizing literature spreadsheets with local evidence chains and optional Feishu sync.

It is designed for workflows where a spreadsheet is not just a destination, but a review surface that should remain inspectable after the classification work is done.

## Highlights

- Supports both local `xlsx` workbooks and Feishu spreadsheet links
- Detects a paper sheet plus a field-guide sheet in the same workbook
- Uses the field-guide sheet to interpret user-defined classification columns
- Builds local evidence assets for each paper
- Generates one evidence Markdown file per paper row
- Adds or reuses workbook traceability columns
- Supports local-first editing and Feishu sync preview
- Bundles a small demo workbook for onboarding and sharing

## Included capabilities

- workbook structure detection
- local workspace preparation
- PDF or web-preview source capture
- PDF text extraction
- evidence Markdown generation
- workbook updates by header name
- Feishu export to local workbook
- Feishu sync preview and execution entry point

## Bundled demo

This release includes:

- `assets/demo/literature-demo.xlsx`
- `references/usage-demo.md`

The demo is intended to help new users understand the two-sheet contract and the evidence-chain workflow quickly.

## Notes

- The skill is intentionally conservative when evidence is weak.
- Feishu sync is not automatic; it is designed to happen only after explicit user confirmation.
- `SKILL.md` is written for Codex, while `README.md` is written for human readers browsing the repository.
