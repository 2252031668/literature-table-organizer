#!/usr/bin/env python3
from __future__ import annotations

import argparse
import py_compile
import sys
from pathlib import Path


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
            return result.returncode

    for script in sorted((skill_root / "scripts").glob("*.py")):
        py_compile.compile(str(script), doraise=True)

    print("Script compilation succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
