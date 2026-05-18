# Usage Demo

## Demo package

Use the bundled demo workbook in `assets/demo/literature-demo.xlsx`.

It contains:

- a primary paper sheet with the required paper-title column
- optional link and abstract columns
- several user-defined literature fields
- a field-guide worksheet with semantic headers

## Demo scenario 1: local workbook

1. Start from the demo workbook.
2. Detect the workbook structure.
3. Choose copy mode so the original demo file stays untouched.
4. Prepare the local artifact folders beside the working copy.
5. Pick one or two paper rows and run the evidence workflow.
6. Write back:
   - user-defined fields
   - local-file path
   - evidence-path
   - warning/status
7. Open the evidence Markdown files and confirm each conclusion points to a source segment.
8. Click the `本地文件路径` and `证据链路径` cells in Excel and confirm they open the target file.

## Demo scenario 2: Feishu workbook

1. Use any Feishu sheet that follows the same two-sheet pattern.
2. Export it locally with `prepare_local_workspace.py`.
3. Run the same evidence workflow on the local export.
4. Preview sync with `feishu_sync.py --mode preview`.
5. Only execute sync after explicit user confirmation.

## What to show when sharing the skill

- the workbook structure detection result
- the generated `<workbook_stem>_artifacts/` folders
- one paper asset folder
- one evidence Markdown file
- the manifest file
- the updated workbook cells for:
  - user-defined classifications
  - local-file path
  - evidence-path
  - warning/status
- clickable path cells in the local xlsx workbook

## Suggested talking points

- The skill does not hardcode one research taxonomy.
- The field-guide worksheet tells the agent how to interpret user-defined columns.
- The evidence Markdown is the traceability layer.
- Browser fallback is part of the standard workflow when static fetching cannot reach the real paper asset.
- Feishu editing is intentionally staged through a local workbook first.
