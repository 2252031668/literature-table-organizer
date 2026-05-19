# CLI Reference

Use one entry only:

- `python scripts/cli.py <subcommand>`

## Main commands

### `init-project`

Create the workspace project structure and starter files.

Example:

```bash
python scripts/cli.py init-project --topic "..." --workbook "C:\path\to\table.xlsx"
```

### `build-framework`

Marks `project/framework.md` as the active editable protocol file for discussion.

Example:

```bash
python scripts/cli.py build-framework --workbook "C:\path\to\table.xlsx"
```

### `normalize-workbook-headers`

Rewrite supported workbook headers into English canonical keys when Chinese-header handling is unstable.

Example:

```bash
python scripts/cli.py normalize-workbook-headers --workbook "C:\path\to\table.xlsx"
```

### `row-analyze`

Generate a paper-report template and row-analysis JSON contract for one row and one local PDF.

Example:

```bash
python scripts/cli.py row-analyze --workbook "C:\path\to\table.xlsx" --row 49 --pdf "C:\path\to\paper.pdf"
```

### `writeback-xlsx`

Write curated values from `row-analysis/*.json` back into the workbook.

Example:

```bash
python scripts/cli.py writeback-xlsx --workbook "C:\path\to\table.xlsx" --preserve-headers
```

## Additional commands

### `find-paper-link`

Search paper links from a title and return ranked candidates plus one recommended URL.

### `pdf-download`

Try static PDF resolution and download `paper.pdf` into a target directory.

### `pilot-run`

Build a pilot task list from selected workbook rows.

### `batch-analyze`

Build a batch task queue for a row range. With `--prepare-shells`, also create report and JSON shells for ready rows.

### `append-papers`

Append confirmed paper rows from a JSON list into the workbook and log the addition.

Behavior:

- detect duplicates by normalized title or normalized link
- skip duplicates instead of failing the whole batch
- return both `added_rows` and `skipped_rows`
- record added versus skipped items in `project/expansion-log.md`

### `reset-project`

Clear generated paper reports, row analysis JSON files, and review queue artifacts while preserving PDFs and `framework.md`.
