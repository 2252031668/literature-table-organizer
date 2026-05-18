# Feishu Sync

## Default rule

Do not sync automatically after local editing.

Finish the local workbook first, summarize the local result, and then ask the user whether to sync back to Feishu.

## Sync mode

Use `scripts/feishu_sync.py` in preview mode first.

Preview mode should:

- inspect the remote spreadsheet
- match local worksheet titles to remote worksheets
- show which sheets will be written
- show whether any worksheets are missing remotely

Execute mode should only run after explicit user confirmation.

## Limitations

- The sync script writes rectangular used ranges back to matching worksheets.
- It is designed for controlled workbook updates, not for arbitrary spreadsheet reshaping.
- Extra remote content outside the written ranges may remain unless the user asks for deeper cleanup.
