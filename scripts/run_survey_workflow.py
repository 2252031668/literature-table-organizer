#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from common import (
    FIELD_MANUAL_STATUS_CONFIRMED,
    FIELD_MANUAL_STATUS_NEEDS_CONFIRMATION,
    PILOT_STATUS_CONFIRMED,
    PILOT_STATUS_READY,
    PROJECT_MODE_SURVEY,
    STATUS_BROWSER_PENDING,
    emit_json,
    load_workflow_state,
    markdown_has_unresolved_placeholders,
    normalize_text,
    parse_json_file,
    pilot_summary_path_for_workbook,
    project_file_paths,
    save_workflow_state,
    use_legacy_artifacts,
    workflow_state_path_for_workbook,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def run_script(script_name: str, args: list[str], cwd: Path, extra_env: dict[str, str] | None = None) -> dict[str, object]:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    if extra_env:
        env.update(extra_env)
    cmd = [sys.executable, str(SCRIPT_DIR / script_name), *args]
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"{script_name} failed")
    return json.loads(result.stdout)


def choose_primary_sheet(detect_payload: dict[str, object], explicit_name: str | None) -> str:
    if explicit_name:
        return explicit_name
    primary = detect_payload.get("primary_candidates") or []
    if not primary:
        raise RuntimeError("No primary paper sheet candidate detected.")
    return str(primary[0]["sheet_name"])


def choose_fieldguide_sheet(detect_payload: dict[str, object], explicit_name: str | None) -> str | None:
    if explicit_name:
        return explicit_name
    candidates = detect_payload.get("fieldguide_candidates") or []
    if not candidates:
        return None
    return str(candidates[0]["sheet_name"])


def field_manual_confirmed(workbook_path: Path) -> tuple[bool, bool]:
    state = load_workflow_state(workbook_path)
    status = normalize_text(state.get("field_manual_status"))
    file_paths = project_file_paths(workbook_path)
    text = file_paths["field_manual"].read_text(encoding="utf-8", errors="replace") if file_paths["field_manual"].exists() else ""
    has_placeholders = markdown_has_unresolved_placeholders(text)
    return status == FIELD_MANUAL_STATUS_CONFIRMED, has_placeholders


def pilot_confirmed(workbook_path: Path) -> tuple[bool, int, bool]:
    state = load_workflow_state(workbook_path)
    status = normalize_text(state.get("pilot_status"))
    summary_path = pilot_summary_path_for_workbook(workbook_path)
    if not summary_path.exists():
        return False, 0, False
    summary = parse_json_file(summary_path)
    count = int(summary.get("row_count") or 0) if isinstance(summary, dict) else 0
    pilot_text = project_file_paths(workbook_path)["pilot"].read_text(encoding="utf-8", errors="replace") if project_file_paths(workbook_path)["pilot"].exists() else ""
    has_rule = "Rule learned" in pilot_text or "rule learned" in pilot_text.lower()
    return status == PILOT_STATUS_CONFIRMED, count, has_rule


def browser_pending_rows(workbook_path: Path) -> list[int]:
    manifest_path = project_file_paths(workbook_path)["brief"].parent.parent / "manifest.json"
    if not manifest_path.exists():
        return []
    manifest = parse_json_file(manifest_path)
    if not isinstance(manifest, list):
        return []
    pending = []
    for item in manifest:
        if isinstance(item, dict) and normalize_text(item.get("status")) == STATUS_BROWSER_PENDING:
            pending.append(int(item["row"]))
    return pending


def gate_batch(workbook_path: Path) -> dict[str, object]:
    manual_confirmed, manual_has_placeholders = field_manual_confirmed(workbook_path)
    pilot_is_confirmed, pilot_count, pilot_has_rule = pilot_confirmed(workbook_path)
    pending_rows = browser_pending_rows(workbook_path)
    blockers: list[str] = []
    if not manual_confirmed:
        blockers.append("field_manual_not_confirmed")
    if manual_has_placeholders:
        blockers.append("field_manual_has_placeholders")
    if pilot_count < 5:
        blockers.append("pilot_sample_count_below_minimum")
    if not pilot_has_rule:
        blockers.append("pilot_missing_rule_learned")
    if not pilot_is_confirmed:
        blockers.append("pilot_not_confirmed")
    if pending_rows:
        blockers.append("browser_pending_rows")
    return {
        "ok": not blockers,
        "blockers": blockers,
        "browser_pending_rows": pending_rows,
        "pilot_sample_count": pilot_count,
        "pilot_has_rule": pilot_has_rule,
        "field_manual_confirmed": manual_confirmed,
        "field_manual_has_placeholders": manual_has_placeholders,
        "pilot_status_confirmed": pilot_is_confirmed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--workbook", required=True)
    parser.add_argument("--draft-source")
    parser.add_argument("--sheet-name")
    parser.add_argument("--fieldguide-sheet")
    parser.add_argument("--phase", choices=["bootstrap", "manual", "pilot", "batch", "expansion"], default="bootstrap")
    parser.add_argument("--row-start", type=int, default=2)
    parser.add_argument("--row-end", type=int)
    parser.add_argument("--use-legacy-artifacts", action="store_true")
    parser.add_argument("--confirm-field-manual", action="store_true")
    parser.add_argument("--confirm-pilot", action="store_true")
    args = parser.parse_args()

    workbook_path = Path(args.workbook).resolve()
    workbook_dir = workbook_path.parent
    extra_env = {"LTO_USE_LEGACY_ARTIFACTS": "1"} if args.use_legacy_artifacts else {"LTO_USE_LEGACY_ARTIFACTS": "0"}

    detect_payload = run_script("detect_workbook_structure.py", [str(workbook_path)], workbook_dir, extra_env)
    sheet_name = choose_primary_sheet(detect_payload, args.sheet_name)
    fieldguide_sheet = choose_fieldguide_sheet(detect_payload, args.fieldguide_sheet)
    state = load_workflow_state(workbook_path)
    state.update(
        {
            "mode": PROJECT_MODE_SURVEY,
            "topic": normalize_text(args.topic),
            "workbook": str(workbook_path),
            "sheet_name": sheet_name,
            "fieldguide_sheet": fieldguide_sheet,
            "phase": args.phase,
            "use_legacy_artifacts": bool(args.use_legacy_artifacts),
        }
    )
    save_workflow_state(workbook_path, state)

    phase_outputs: dict[str, object] = {
        "detect": detect_payload,
        "workflow_state_path": str(workflow_state_path_for_workbook(workbook_path)),
    }

    if args.phase == "bootstrap":
        phase_outputs["bootstrap"] = run_script(
            "survey_mode_bootstrap.py",
            [
                "--workbook",
                str(workbook_path),
                "--topic",
                args.topic,
                *(["--draft-source", args.draft_source] if args.draft_source else []),
                *(["--fieldguide-sheet", fieldguide_sheet] if fieldguide_sheet else []),
            ],
            workbook_dir,
            extra_env,
        )
    elif args.phase == "manual":
        if not fieldguide_sheet:
            raise RuntimeError("No field-guide sheet detected for manual phase.")
        phase_outputs["manual"] = run_script(
            "upgrade_field_manual.py",
            ["--workbook", str(workbook_path), "--sheet-name", fieldguide_sheet],
            workbook_dir,
            extra_env,
        )
        if args.confirm_field_manual:
            state = load_workflow_state(workbook_path)
            state["field_manual_status"] = FIELD_MANUAL_STATUS_CONFIRMED
            save_workflow_state(workbook_path, state)
            phase_outputs["field_manual_confirmed"] = True
    elif args.phase == "pilot":
        phase_outputs["pilot"] = run_script(
            "prepare_pilot_set.py",
            [
                "--workbook",
                str(workbook_path),
                "--sheet-name",
                sheet_name,
                "--row-start",
                str(args.row_start),
                *(["--row-end", str(args.row_end)] if args.row_end else []),
            ],
            workbook_dir,
            extra_env,
        )
        if args.confirm_pilot:
            state = load_workflow_state(workbook_path)
            state["pilot_status"] = PILOT_STATUS_CONFIRMED
            save_workflow_state(workbook_path, state)
            phase_outputs["pilot_confirmed"] = True
    elif args.phase == "batch":
        gate = gate_batch(workbook_path)
        phase_outputs["gate"] = gate
        if not gate["ok"]:
            phase_outputs["next_action"] = "Resolve blockers before batch processing."
        else:
            phase_outputs["batch"] = run_script(
                "rebuild_local_workbook.py",
                [
                    "--workbook",
                    str(workbook_path),
                    "--sheet-name",
                    sheet_name,
                    "--row-start",
                    str(args.row_start),
                    *(["--row-end", str(args.row_end)] if args.row_end else []),
                    "--survey-mode",
                ],
                workbook_dir,
                extra_env,
            )
    elif args.phase == "expansion":
        phase_outputs["expansion"] = {
            "status": "ready",
            "message": "Use plan_paper_expansion.py to propose candidates, then append_paper_rows.py to add confirmed papers.",
        }

    emit_json(
        {
            "mode": PROJECT_MODE_SURVEY,
            "phase": args.phase,
            "workbook": str(workbook_path),
            "sheet_name": sheet_name,
            "fieldguide_sheet": fieldguide_sheet,
            "use_legacy_artifacts": bool(args.use_legacy_artifacts or use_legacy_artifacts()),
            "outputs": phase_outputs,
        }
    )


if __name__ == "__main__":
    main()
