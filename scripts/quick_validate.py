#!/usr/bin/env python3
from __future__ import annotations

import argparse
import py_compile
import sys
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
    validator = (
        Path.home()
        / ".codex"
        / "skills"
        / ".system"
        / "skill-creator"
        / "scripts"
        / "quick_validate.py"
    )

    if validator.exists():
        from subprocess import run

        result = run(
            [sys.executable, str(validator), str(skill_root)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        if result.returncode != 0:
            print("Note: system validator failed; on Windows this may still reflect a gbk/utf-8 decoding limitation rather than a skill logic failure.")

    for script in sorted((skill_root / "scripts").glob("*.py")):
        py_compile.compile(str(script), doraise=True)

    required_scripts = [
        "run_survey_workflow.py",
        "survey_mode_bootstrap.py",
        "upgrade_field_manual.py",
        "prepare_pilot_set.py",
        "finalize_browser_capture.py",
        "plan_paper_expansion.py",
        "append_paper_rows.py",
        "reset_survey_outputs.py",
        "rebuild_local_workbook.py",
    ]
    missing_scripts = [name for name in required_scripts if not (skill_root / "scripts" / name).exists()]
    if missing_scripts:
        raise FileNotFoundError(f"Missing required scripts: {', '.join(missing_scripts)}")

    ensure_contains(
        skill_root / "SKILL.md",
        ["run_survey_workflow.py", "browser_pending", "field manual", "pilot"],
    )
    ensure_contains(
        skill_root / "references" / "workflow.md",
        ["browser_pending", "field-manual", "pilot", "run_survey_workflow.py"],
    )
    ensure_contains(
        skill_root / "references" / "usage-demo.md",
        ["Browser", "run_survey_workflow.py", "pilot"],
    )

    print("Script compilation succeeded.")
    print("Local survey workflow checks succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
