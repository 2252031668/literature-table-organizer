#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from openpyxl import load_workbook

from common import (
    ABSTRACT_HEADER,
    CLASSIFICATION_HEADERS,
    EVIDENCE_PATH_HEADER,
    LOCAL_FILE_HEADER,
    PAPER_LINK_HEADER,
    PAPER_TITLE_HEADER,
    SUMMARY_HEADERS,
    WARNING_HEADER,
    WRITING_EVIDENCE_HEADER,
    WRITING_SECTION_HEADER,
    build_artifact_root,
    emit_json,
    ensure_dir,
    manifest_path_for_workbook,
    normalize_text,
    read_json_if_exists,
    relative_path,
    slugify,
    status_allows_full_backfill,
    write_json,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def run_script(script_name: str, args: list[str], cwd: Path) -> dict[str, object]:
    cmd = [sys.executable, str(SCRIPT_DIR / script_name), *args]
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"{script_name} failed")
    return json.loads(result.stdout)


def header_map(ws) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for col_idx in range(1, ws.max_column + 1):
        value = normalize_text(ws.cell(1, col_idx).value)
        if value:
            mapping[value] = col_idx
    return mapping


def cell_value(ws, headers: dict[str, int], row: int, header: str) -> str:
    col = headers.get(header)
    if not col:
        return ""
    return normalize_text(ws.cell(row, col).value)


def infer_field_notes(values: dict[str, str]) -> dict[str, dict[str, str]] | None:
    notes: dict[str, dict[str, str]] = {}
    for key in CLASSIFICATION_HEADERS:
        value = normalize_text(values.get(key))
        if value:
            notes[key] = {
                "value": value,
                "segments": "S1, S2",
                "decision_question": f"How should `{key}` be assigned under the current survey taxonomy?",
                "derivation": "Preserved or updated from the available evidence under the current source policy.",
                "causal_reasoning": "Trace the paper's input, core modules, outputs, and coordination mechanism before assigning the label.",
                "exclusion_reason": "Check neighboring categories and record why they were not selected.",
                "evidence_sufficiency": "Needs reviewer confirmation unless supported by full paper evidence.",
            }
    return notes or None


def write_temp_json(path: Path, payload: object) -> Path:
    write_json(path, payload)
    return path


def placeholder_source_payload(row: int, title: str, row_dir: Path, warning: str) -> dict[str, object]:
    source_path = row_dir / "source.md"
    if not source_path.exists():
        source_path.write_text(
            "\n".join(
                [
                    f"# {title}",
                    "",
                    "- Source label: placeholder",
                    f"- Warning: {warning}",
                    "",
                    "## Abstract",
                    "",
                    "No source artifact was available during this rebuild pass.",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    return {
        "row": row,
        "title": title,
        "status": "unresolved",
        "resolved_url": None,
        "secondary_urls": [],
        "source_kind": "unresolved",
        "evidence_level": "unresolved",
        "allow_full_backfill": False,
        "warning": warning,
        "local_source": str(source_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", required=True)
    parser.add_argument("--sheet-name", required=True)
    parser.add_argument("--row-start", type=int, default=2)
    parser.add_argument("--row-end", type=int)
    parser.add_argument("--overwrite-existing-evidence", action="store_true")
    parser.add_argument("--survey-mode", action="store_true")
    args = parser.parse_args()

    workbook_path = Path(args.workbook).resolve()
    workbook_dir = workbook_path.parent
    artifact_root = ensure_dir(build_artifact_root(workbook_path))
    papers_dir = ensure_dir(artifact_root / "papers")
    evidence_dir = ensure_dir(artifact_root / "evidence")
    tmp_dir = ensure_dir(artifact_root / "snapshots" / "tmp")
    manifest_path = manifest_path_for_workbook(workbook_path)

    wb = load_workbook(workbook_path)
    ws = wb[args.sheet_name]
    headers = header_map(ws)

    manifest = read_json_if_exists(manifest_path, [])
    if not isinstance(manifest, list):
        manifest = []
    manifest_by_row = {int(item["row"]): item for item in manifest if isinstance(item, dict) and "row" in item}

    updates: list[dict[str, object]] = []
    processed_manifest: list[dict[str, object]] = []
    row_end = args.row_end or ws.max_row

    for row in range(args.row_start, row_end + 1):
        title = cell_value(ws, headers, row, PAPER_TITLE_HEADER)
        if not title:
            continue

        existing_evidence = cell_value(ws, headers, row, EVIDENCE_PATH_HEADER)
        if existing_evidence and not args.overwrite_existing_evidence:
            continue

        link = cell_value(ws, headers, row, PAPER_LINK_HEADER) or None
        abstract = cell_value(ws, headers, row, ABSTRACT_HEADER)
        row_dir = ensure_dir(papers_dir / f"{row:03d}-{slugify(title)}")

        try:
            source_payload = run_script(
                "fetch_paper_sources.py",
                ["--title", title, "--row", str(row), "--artifacts-dir", str(papers_dir), *(["--link", link] if link else [])],
                workbook_dir,
            )
        except Exception as exc:
            source_payload = placeholder_source_payload(row, title, row_dir, str(exc))

        if not source_payload.get("local_source"):
            source_payload = placeholder_source_payload(
                row,
                title,
                row_dir,
                normalize_text(source_payload.get("warning")) or "No local source artifact was produced.",
            )

        source_json_path = write_temp_json(tmp_dir / f"{row:03d}-{slugify(title)}-source.json", source_payload)
        source_rel = relative_path(Path(str(source_payload["local_source"])).resolve(), workbook_dir)

        values: dict[str, str] = {LOCAL_FILE_HEADER: source_rel}
        links: dict[str, str] = {LOCAL_FILE_HEADER: source_rel}

        warning_value = normalize_text(source_payload.get("warning"))
        if warning_value:
            values[WARNING_HEADER] = warning_value

        for header in CLASSIFICATION_HEADERS:
            existing_value = cell_value(ws, headers, row, header)
            if existing_value:
                values[header] = existing_value

        for header in SUMMARY_HEADERS:
            existing_value = cell_value(ws, headers, row, header)
            if existing_value:
                values[header] = existing_value

        if args.survey_mode:
            writing_section = cell_value(ws, headers, row, WRITING_SECTION_HEADER)
            writing_argument = cell_value(ws, headers, row, WRITING_EVIDENCE_HEADER)
            if writing_section:
                values[WRITING_SECTION_HEADER] = writing_section
            if writing_argument:
                values[WRITING_EVIDENCE_HEADER] = writing_argument

        if status_allows_full_backfill(str(source_payload["status"])) and abstract:
            values.setdefault("核验后核心方法", abstract[:300].strip())
        elif abstract and not values.get(ABSTRACT_HEADER):
            values[ABSTRACT_HEADER] = abstract

        row_updates_path = write_temp_json(tmp_dir / f"{row:03d}-{slugify(title)}-updates.json", values)
        field_notes = infer_field_notes(values)
        field_notes_path = None
        if field_notes:
            field_notes_path = write_temp_json(tmp_dir / f"{row:03d}-{slugify(title)}-field-notes.json", field_notes)

        evidence_payload = run_script(
            "build_evidence_files.py",
            [
                "--row",
                str(row),
                "--title",
                title,
                *(["--link", link] if link else []),
                "--source-json",
                str(source_json_path),
                "--evidence-dir",
                str(evidence_dir),
                "--workspace-root",
                str(workbook_dir),
                "--sheet-updates-json",
                str(row_updates_path),
                *(["--field-notes-json", str(field_notes_path)] if field_notes_path else []),
            ],
            workbook_dir,
        )

        evidence_rel = normalize_text(evidence_payload.get("evidence_path"))
        if evidence_rel:
            values[EVIDENCE_PATH_HEADER] = evidence_rel
            links[EVIDENCE_PATH_HEADER] = evidence_rel

        updates.append({"row": row, "values": values, "links": links})
        processed_manifest.append(
            {
                "row": row,
                "title": title,
                "local_source": source_rel,
                "evidence_path": evidence_rel,
                "status": source_payload.get("status"),
                "warning": source_payload.get("warning"),
                "allow_full_backfill": bool(source_payload.get("allow_full_backfill")),
                "resolved_url": source_payload.get("resolved_url"),
            }
        )

    updates_json_path = write_temp_json(tmp_dir / "workbook-updates.json", updates)
    workbook_update_args = [str(workbook_path), args.sheet_name, "--updates-json", str(updates_json_path)]
    if args.survey_mode:
        workbook_update_args.append("--survey-mode")
    workbook_update_payload = run_script("update_workbook.py", workbook_update_args, workbook_dir)

    for item in processed_manifest:
        manifest_by_row[int(item["row"])] = item
    final_manifest = [manifest_by_row[key] for key in sorted(manifest_by_row)]
    write_json(manifest_path, final_manifest)

    payload = {
        "workbook": str(workbook_path),
        "sheet_name": args.sheet_name,
        "processed_rows": [item["row"] for item in processed_manifest],
        "manifest_path": str(manifest_path),
        "workbook_update": workbook_update_payload,
        "survey_mode": args.survey_mode,
    }
    emit_json(payload)


if __name__ == "__main__":
    main()
