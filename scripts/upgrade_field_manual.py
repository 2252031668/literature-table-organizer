#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from openpyxl import load_workbook

from common import (
    FIELD_GUIDANCE_HEADER,
    FIELD_HEADER,
    FIELD_VALUE_HEADER,
    emit_json,
    normalize_text,
    project_file_paths,
)


ENHANCED_HEADERS = [
    "字段",
    "服务章节/写作问题",
    "字段作用",
    "判定问题",
    "建议填写方式",
    "推荐取值/说明",
    "正例/触发条件",
    "反例/易混淆项",
    "关键证据要求",
    "不足证据时如何处理",
]


def header_map(ws) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for col_idx in range(1, ws.max_column + 1):
        value = normalize_text(ws.cell(1, col_idx).value)
        if value:
            mapping[value] = col_idx
    return mapping


def detect_legacy_rows(ws) -> list[dict[str, str]]:
    headers = header_map(ws)
    field_col = headers.get(FIELD_HEADER)
    guide_col = headers.get(FIELD_GUIDANCE_HEADER)
    value_col = headers.get(FIELD_VALUE_HEADER)
    rows: list[dict[str, str]] = []
    if not field_col:
        return rows
    for row_idx in range(2, ws.max_row + 1):
        field_name = normalize_text(ws.cell(row_idx, field_col).value)
        if not field_name:
            continue
        rows.append(
            {
                "字段": field_name,
                "建议填写方式": normalize_text(ws.cell(row_idx, guide_col).value) if guide_col else "",
                "推荐取值/说明": normalize_text(ws.cell(row_idx, value_col).value) if value_col else "",
            }
        )
    return rows


def build_manual(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Field Manual Draft",
        "",
        "The original workbook field guide is too lightweight for survey-oriented batch classification.",
        "Use this draft to discuss and confirm decision rules before pilot calibration and full-table processing.",
        "",
        "## Required columns in the upgraded manual",
        "",
    ]
    for header in ENHANCED_HEADERS:
        lines.append(f"- {header}")
    lines.extend(["", "## Draft entries", ""])

    for row in rows:
        field_name = row["字段"]
        lines.extend(
            [
                f"### {field_name}",
                f"- 字段: {field_name}",
                "- 服务章节/写作问题: TODO",
                "- 字段作用: TODO",
                "- 判定问题: TODO",
                f"- 建议填写方式: {row['建议填写方式'] or 'TODO'}",
                f"- 推荐取值/说明: {row['推荐取值/说明'] or 'TODO'}",
                "- 正例/触发条件: TODO",
                "- 反例/易混淆项: TODO",
                "- 关键证据要求: TODO",
                "- 不足证据时如何处理: TODO",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", required=True)
    parser.add_argument("--sheet-name", required=True)
    args = parser.parse_args()

    workbook_path = Path(args.workbook).resolve()
    wb = load_workbook(workbook_path, read_only=True)
    ws = wb[args.sheet_name]
    rows = detect_legacy_rows(ws)
    file_paths = project_file_paths(workbook_path)
    draft = build_manual(rows)
    file_paths["field_manual"].parent.mkdir(parents=True, exist_ok=True)
    file_paths["field_manual"].write_text(draft + "\n", encoding="utf-8")

    payload = {
        "workbook": str(workbook_path),
        "sheet_name": args.sheet_name,
        "legacy_entry_count": len(rows),
        "field_manual_path": str(file_paths["field_manual"]),
        "requires_user_confirmation": True,
    }
    emit_json(payload)


if __name__ == "__main__":
    main()
