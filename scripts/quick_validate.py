#!/usr/bin/env python3
from __future__ import annotations

import argparse
import py_compile
from pathlib import Path


def ensure_contains(path: Path, patterns: list[str]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = [pattern for pattern in patterns if pattern not in text]
    if missing:
        raise RuntimeError(f"{path.name} is missing required markers: {', '.join(missing)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "skill_root",
        nargs="?",
        default=str(Path(__file__).resolve().parents[1]),
        help="Path to the skill root",
    )
    args = parser.parse_args()

    skill_root = Path(args.skill_root).resolve()
    scripts_dir = skill_root / "scripts"
    references_dir = skill_root / "references"

    for script in sorted(scripts_dir.rglob("*.py")):
        py_compile.compile(str(script), doraise=True)

    required_scripts = [
        scripts_dir / "cli.py",
        scripts_dir / "common.py",
        scripts_dir / "lib" / "project.py",
        scripts_dir / "lib" / "workbook.py",
        scripts_dir / "lib" / "pdf_fetcher.py",
        scripts_dir / "lib" / "link_search.py",
        scripts_dir / "lib" / "row_contracts.py",
    ]
    missing = [str(path.relative_to(skill_root)) for path in required_scripts if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required scripts: {', '.join(missing)}")

    ensure_contains(
        skill_root / "SKILL.md",
        ["framework.md", "row-analyze", "read-only", "paper-reports", "writeback-xlsx"],
    )
    ensure_contains(
        references_dir / "workflow.md",
        ["framework.md", "row-analyze", "normalize-workbook-headers", "writeback-xlsx"],
    )
    ensure_contains(
        references_dir / "cli.md",
        ["init-project", "pdf-download", "pilot-run", "batch-analyze", "append-papers", "reset-project"],
    )
    ensure_contains(
        references_dir / "report-template.md",
        ["Part A", "Part B", "writing_argument"],
    )
    ensure_contains(
        references_dir / "usage-demo.md",
        ["row-analyze", "paper-reports", "pilot-run", "batch-analyze", "append-papers", "writeback-xlsx"],
    )

    print("Script compilation succeeded.")
    print("Single-workflow survey skill checks succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
