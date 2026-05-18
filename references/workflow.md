# Workflow

## Goal

Turn a literature workbook into a verifiable review package:

- fill or verify user-defined literature fields in the primary paper sheet
- preserve one local source asset per paper when possible
- generate one evidence Markdown file per paper row
- write relative paths back into the workbook
- make local path cells in xlsx workbooks clickable

## Input contract

The workbook must have:

- one primary paper sheet with the required paper-title header
- an optional paper-link header
- an optional abstract header
- zero or more user-defined fields to fill or verify
- one field-guide worksheet that explains those fields

## Fixed order

1. Identify whether the source is a local workbook or a Feishu sheet URL.
2. Detect the workbook structure.
3. Confirm the target paper sheet when more than one candidate exists.
4. Confirm the field-guide sheet or pause if it is incomplete.
5. Prepare the local editable workbook.
6. Ensure artifact directories exist beside that workbook.
7. Ensure system columns exist.
8. Process papers row by row.
9. Write results to the local workbook.
10. If the source was Feishu, ask whether to sync the local result back to the cloud.

## Evidence order

Prefer sources in this order:

1. PDF or full paper text
2. official readable fulltext webpage
3. project page
4. repository documentation
5. high-quality secondary review or interpretation page
6. abstract-only page

Treat this ordering as a hard gate for automation:

- first try deterministic PDF resolution
- then try static fulltext-page capture
- then try Browser-based dynamic fetching
- only after those fail should the workflow consider a secondary review page
- abstract-only pages are a last-resort record, not a default full-backfill source

## Missing-link policy

When the paper-link cell is empty:

1. search by title
2. fill the link only if the match is reliable
3. if the match remains weak, continue using title-based evidence search
4. if evidence is still weak, keep old values and record a warning

## Warning policy

Do not clear old values by default.

Instead:

- preserve existing values when new evidence is not strong enough to overturn them
- write the reason into the warning/status column
- repeat the same conservative note inside the evidence Markdown

Useful warning strings include:

- `链接缺失，按标题检索`
- `标题-链接疑似错配`
- `未获全文PDF，基于全文网页证据`
- `基于二手解读证据`
- `仅获摘要，不建议完整回填`
- `证据不足，结论待确认`
- `本地路径目标缺失`

Recommended normalized source statuses:

- `pdf_download`
- `pdf_via_browser`
- `fulltext_web`
- `secondary_review`
- `abstract_only`
- `unresolved`
- `mismatch_or_unverifiable`

Backfill policy by status:

- `pdf_download`, `pdf_via_browser`, `fulltext_web`: full backfill allowed
- `secondary_review`: full backfill allowed, but mark it as secondary evidence in the evidence Markdown
- `abstract_only`: do not fully backfill by default; preserve old values or only write paths and warning
- `unresolved`, `mismatch_or_unverifiable`: warning-only unless the user explicitly overrides

## Pause conditions

Pause and discuss with the user when:

- the field-guide sheet is missing
- the field-guide headers are incomplete
- a target column has no usable guide entry
- more than one paper-sheet candidate looks equally valid
- a user-defined field remains semantically unclear after reading the guide

## Artifact layout

Place artifacts beside the editable workbook:

- `<workbook_stem>_artifacts/papers/`
- `<workbook_stem>_artifacts/evidence/`
- `<workbook_stem>_artifacts/snapshots/`
- `<workbook_stem>_artifacts/manifest.json`

Use relative paths when writing the local-file and evidence-path columns back into the workbook.
For local xlsx workbooks, also write Excel hyperlinks so the path cells can be clicked to open the target file.
