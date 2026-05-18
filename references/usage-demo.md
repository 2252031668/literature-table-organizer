# Usage Demo

## Demo package

Use the bundled demo workbook in `assets/demo/literature-demo.xlsx`.

It demonstrates:

- standard literature-table organization
- survey-oriented writing support
- lightweight guide input that can be upgraded into a field manual

## Demo scenario 1: standard mode

1. Start from the demo workbook.
2. Detect workbook structure.
3. Prepare a local working copy.
4. Pick one or two rows and run the evidence workflow.
5. Write back:
   - classification fields
   - local-file path
   - evidence-path
   - warning/status
6. Open the evidence Markdown file and confirm each conclusion points to source segments.
7. Click the local path cells in Excel and confirm they open the target files.

## Demo scenario 2: survey-oriented mode

1. Start from the same workbook, but also provide a survey topic.
2. Run survey bootstrap and create the project files under `<workbook_stem>_artifacts/project/`.
3. Draft `outline.md` and compare it with the current workbook fields.
4. Upgrade the lightweight guide into `field-manual.md`.
5. Use 5-10 representative rows for pilot calibration.
6. Fill `写作引用章节` and `引用论据` for sample rows.
7. Confirm that evidence Markdown now contains decision-chain sections.

## Demo scenario 3: incremental paper expansion

1. Identify a missing aspect from the outline.
2. Search for candidate papers.
3. Confirm which ones should be added.
4. Append them as new workbook rows.
5. Process those new rows with the same evidence and writing-support workflow.

## What to show when sharing the skill

- workbook structure detection
- project-level files in survey-oriented mode
- one paper asset folder
- one evidence Markdown file with decision-chain content
- manifest and project bootstrap files
- updated workbook cells for:
  - classification fields
  - writing-support fields
  - local-file path
  - evidence-path
  - warning/status

## Suggested talking points

- The skill now supports both standard and survey-oriented workflows.
- Survey-oriented mode does not go straight to batch classification.
- A weak guide sheet can be upgraded into a stronger field manual.
- Evidence Markdown is both a traceability layer and a writing-support layer.
- Browser fallback remains part of the fetch chain when static fetching cannot reach the real paper asset.
