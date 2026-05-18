#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from common import ensure_dir, resolve_feishu_sheet_token, run_command


def build_artifact_root(workbook_path: Path) -> Path:
    return workbook_path.parent / f"{workbook_path.stem}_artifacts"


def ensure_workspace_dirs(workbook_path: Path) -> dict[str, str]:
    artifact_root = ensure_dir(build_artifact_root(workbook_path))
    papers_dir = ensure_dir(artifact_root / "papers")
    evidence_dir = ensure_dir(artifact_root / "evidence")
    snapshots_dir = ensure_dir(artifact_root / "snapshots")
    return {
        "artifact_root": str(artifact_root),
        "papers_dir": str(papers_dir),
        "evidence_dir": str(evidence_dir),
        "snapshots_dir": str(snapshots_dir),
    }


def export_feishu_sheet(url: str, output_dir: Path, file_name: str | None) -> Path:
    info = resolve_feishu_sheet_token(url)
    output_arg = "."
    if output_dir != output_dir.parent:
        output_arg = str(Path(".") / output_dir.name)
    cmd = [
        "lark-cli",
        "drive",
        "+export",
        "--doc-type",
        "sheet",
        "--file-extension",
        "xlsx",
        "--token",
        info["token"],
        "--output-dir",
        output_arg,
        "--overwrite",
    ]
    if file_name:
        cmd.extend(["--file-name", file_name])
    result = run_command(cmd, cwd=output_dir.parent)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Feishu export failed")

    exported = None
    for line in reversed(result.stdout.splitlines()):
        line = line.strip()
        if line.endswith(".xlsx"):
            exported = Path(line)
            break
    if exported is None:
        candidates = sorted(output_dir.glob("*.xlsx"), key=lambda item: item.stat().st_mtime, reverse=True)
        if not candidates:
            raise RuntimeError("Feishu export completed without an xlsx artifact")
        exported = candidates[0]
    return exported.resolve()


def copy_local_workbook(source: Path, destination: Path) -> Path:
    ensure_dir(destination.parent)
    shutil.copy2(source, destination)
    return destination.resolve()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-workbook", help="Path to a local workbook")
    parser.add_argument("--feishu-url", help="Feishu spreadsheet URL")
    parser.add_argument(
        "--mode",
        choices=["copy", "inplace", "download"],
        required=True,
        help="For local workbooks: copy or inplace. For Feishu: download.",
    )
    parser.add_argument("--output-dir", help="Optional output directory for copied/exported workbook")
    parser.add_argument("--output-name", help="Optional output filename")
    args = parser.parse_args()

    if not args.local_workbook and not args.feishu_url:
        raise SystemExit("Provide either --local-workbook or --feishu-url")

    if args.local_workbook and args.feishu_url:
        raise SystemExit("Choose only one source: local workbook or Feishu URL")

    if args.local_workbook:
        source = Path(args.local_workbook).resolve()
        if args.mode == "download":
            raise SystemExit("--mode download is only valid for Feishu URLs")
        if args.mode == "inplace":
            editable = source
            snapshot_created = False
        else:
            output_dir = Path(args.output_dir).resolve() if args.output_dir else source.parent
            output_name = args.output_name or f"{source.stem}_working_copy{source.suffix}"
            editable = copy_local_workbook(source, output_dir / output_name)
            snapshot_created = True
        payload = {
            "source_type": "local_xlsx",
            "source_workbook": str(source),
            "editable_workbook": str(editable),
            "created_copy": snapshot_created,
            **ensure_workspace_dirs(editable),
        }
    else:
        if args.mode != "download":
            raise SystemExit("Feishu URLs must use --mode download")
        output_dir = Path(args.output_dir).resolve() if args.output_dir else Path.cwd()
        ensure_dir(output_dir)
        exported = export_feishu_sheet(args.feishu_url, output_dir, args.output_name)
        payload = {
            "source_type": "feishu_sheet",
            "source_url": args.feishu_url,
            "editable_workbook": str(exported),
            "created_copy": False,
            **ensure_workspace_dirs(exported),
        }

    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
