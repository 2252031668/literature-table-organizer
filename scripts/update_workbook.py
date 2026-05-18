#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from openpyxl import load_workbook

from common import SYSTEM_HEADERS, normalize_text, parse_json_file


def header_map(ws) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for col_idx in range(1, ws.max_column + 1):
        value = normalize_text(ws.cell(1, col_idx).value)
        if value:
            mapping[value] = col_idx
    return mapping


def ensure_headers(ws) -> dict[str, int]:
    mapping = header_map(ws)
    next_col = ws.max_column + 1
    for header in SYSTEM_HEADERS:
        if header not in mapping:
            ws.cell(1, next_col).value = header
            mapping[header] = next_col
            next_col += 1
    return mapping


def apply_updates(ws, updates: list[dict[str, object]]) -> None:
    mapping = ensure_headers(ws)
    for item in updates:
        row = int(item["row"])
        values: dict[str, object] = dict(item.get("values", {}))
        for header in values:
            if header not in mapping:
                mapping[header] = ws.max_column + 1
                ws.cell(1, mapping[header]).value = header
        for header, value in values.items():
            ws.cell(row=row, column=mapping[header]).value = value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", help="Workbook path")
    parser.add_argument("sheet_name", help="Primary worksheet name")
    parser.add_argument("--updates-json", help="JSON list of row updates")
    args = parser.parse_args()

    workbook_path = Path(args.workbook).resolve()
    wb = load_workbook(workbook_path)
    ws = wb[args.sheet_name]
    ensure_headers(ws)

    updates = parse_json_file(Path(args.updates_json)) if args.updates_json else []
    if updates:
        apply_updates(ws, updates)

    wb.save(workbook_path)
    payload = {
        "workbook": str(workbook_path),
        "sheet_name": args.sheet_name,
        "headers": header_map(ws),
        "updated_rows": [item["row"] for item in updates],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
