# Usage Demo

## Demo package

Use the bundled workbook in:

- `assets/demo/literature-demo.xlsx`

## Demo scenario 1: initialize project

1. Run:
   - `python scripts/cli.py init-project --topic ... --workbook ...`
2. Confirm these workspace outputs:
   - `project/framework.md`
   - `project/project-brief.md`
   - `project/survey-gap-analysis.md`
   - `project/pilot-calibration.md`

## Demo scenario 2: normalize workbook headers

1. Use a workbook with Chinese headers.
2. Run:
   - `python scripts/cli.py normalize-workbook-headers --workbook ...`
3. Confirm supported headers become English canonical keys in the normalized copy.

## Demo scenario 3: row analysis

1. Prepare a local PDF at `papers/<row>-<slug>/paper.pdf`.
2. Run:
   - `python scripts/cli.py row-analyze --workbook ... --row ... --pdf ...`
3. Confirm outputs:
   - `paper-reports/<row>-<slug>.md`
   - `row-analysis/<row>-<slug>.json`
4. Confirm the report has:
   - Part A in Chinese
   - Part B in English field decisions

## Demo scenario 4: pilot and batch task organization

1. Run:
   - `python scripts/cli.py pilot-run --workbook ... --rows 2,3,4`
2. Run:
   - `python scripts/cli.py batch-analyze --workbook ... --row-start 2 --row-end 20`
3. Confirm:
   - `project/review-queue.md`
   - `project/pilot-tasks.json`
   - `project/batch-tasks.json`

## Demo scenario 5: workbook writeback

1. Fill row-analysis JSON files after direct PDF reading.
2. Run:
   - `python scripts/cli.py writeback-xlsx --workbook ... --preserve-headers`
3. Confirm values come only from JSON, not fresh inference.

## Demo scenario 6: append papers safely

1. Prepare a JSON list with candidate rows.
2. Run:
   - `python scripts/cli.py append-papers --workbook ... --rows-json ...`
3. Confirm:
   - new papers are appended
   - duplicate titles or links are skipped
   - `project/expansion-log.md` records both added and skipped items
