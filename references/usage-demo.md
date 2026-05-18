# Usage Demo

## Demo package

Use the bundled demo workbook in `assets/demo/literature-demo.xlsx`.

It demonstrates:

- standard literature-table organization
- survey-oriented writing support
- lightweight guide input that can be upgraded into a field manual
- orchestration through a single survey workflow entry

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

1. Start from the same workbook and provide a survey topic.
2. Optionally provide a draft source.
3. Run `run_survey_workflow.py --phase bootstrap`.
4. Inspect:
   - `project-brief.md`
   - `related-survey-analysis.md`
   - `outline.md`
   - `field-gap-analysis.md`
5. Run `run_survey_workflow.py --phase manual`.
6. Confirm the field manual and mark it confirmed.
7. Run `run_survey_workflow.py --phase pilot`.
8. Confirm the pilot after recording rule-learning notes.
9. Only then run `run_survey_workflow.py --phase batch`.

## Demo scenario 3: Browser fallback

1. Pick a row whose static fetch does not reach the real paper asset.
2. Confirm that the row enters `browser_pending`.
3. Use Browser to retrieve `paper.pdf`, `source.md`, or `review.md`.
4. Finalize the capture and resume the batch workflow.
5. Confirm that the row now produces evidence and workbook output instead of staying pending.

## Demo scenario 4: incremental paper expansion

1. Identify a missing aspect from the outline.
2. Run candidate planning for that aspect.
3. Confirm which papers should be added.
4. Append them as new workbook rows.
5. Process those new rows with the same evidence and writing-support workflow.
6. Record the addition in `paper-expansion-log.md`.

## What to show when sharing the skill

- workbook structure detection
- project-level files in survey-oriented mode
- one paper asset folder
- one evidence Markdown file with decision-chain content
- manifest and workflow-state files
- updated workbook cells for:
  - classification fields
  - writing-support fields
  - local-file path
  - evidence-path
  - warning/status

## Suggested talking points

- The skill now supports both standard and survey-oriented workflows.
- Survey-oriented mode uses one orchestration entry instead of ad hoc manual sequencing.
- A weak guide sheet can be upgraded into a stronger field manual.
- Browser fallback is a formal stage in the fetch chain, not a side suggestion.
- Pilot calibration and field-manual confirmation are hard gates before batch processing.
- Evidence Markdown is both a traceability layer and a writing-support layer.
