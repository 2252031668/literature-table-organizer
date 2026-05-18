#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import (
    PROJECT_MODE_SURVEY,
    build_artifact_root,
    emit_json,
    ensure_dir,
    normalize_text,
    project_file_paths,
    write_json,
)


def build_brief_markdown(
    topic: str,
    workbook_path: Path,
    audience: str,
    article_goal: str,
    differentiation: str,
) -> str:
    lines = [
        f"# Project Brief: {topic}",
        "",
        "## Project positioning",
        "",
        f"- Topic: {topic}",
        f"- Workbook: {workbook_path.name}",
        f"- Mode: {PROJECT_MODE_SURVEY}",
        f"- Target audience: {audience}",
        f"- Article goal: {article_goal}",
        "",
        "## Intended contribution",
        "",
        differentiation,
        "",
        "## Taxonomy anchors to refine with the user",
        "",
        "- Main paradigm split",
        "- Sub-paradigm boundaries",
        "- Function-layer mapping",
        "- Collaboration granularity",
        "- Writing-useful evidence requirements",
        "",
        "## Discussion prompts",
        "",
        "- What gap in existing surveys should this article emphasize?",
        "- Which comparisons or exclusions matter most for the final narrative?",
        "- Which claims must be backed by PDF-level evidence rather than abstract-level evidence?",
        "",
    ]
    return "\n".join(lines)


def build_outline_markdown(topic: str) -> str:
    lines = [
        f"# Outline: {topic}",
        "",
        "## 1. Introduction and motivation",
        "- Problem setting",
        "- Why this survey is needed now",
        "- Scope and exclusions",
        "",
        "## 2. Positioning against prior surveys",
        "- Existing survey coverage",
        "- Remaining blind spots",
        "- This survey's distinguishing angle",
        "",
        "## 3. Taxonomy",
        "- Paradigm split",
        "- Subcategory definitions",
        "- Layer mapping",
        "- Collaboration granularity",
        "",
        "## 4. Representative methods by taxonomy branch",
        "- Method summaries",
        "- System mechanisms",
        "- Comparative evidence",
        "",
        "## 5. Benchmarks, tasks, and evaluation signals",
        "- Datasets",
        "- Real-world tasks",
        "- Generalization and safety evidence",
        "",
        "## 6. Limitations and open problems",
        "- Data bottlenecks",
        "- Coordination bottlenecks",
        "- Model design tradeoffs",
        "",
        "## 7. Outlook",
        "- Emerging trends",
        "- Research opportunities",
        "",
    ]
    return "\n".join(lines)


def build_analysis_markdown(topic: str) -> str:
    lines = [
        f"# Related Survey Analysis: {topic}",
        "",
        "## Purpose",
        "",
        "Capture how existing surveys and representative papers frame the space, and identify where the new survey should differentiate itself.",
        "",
        "## To fill",
        "",
        "- Existing surveys read",
        "- Their taxonomy choices",
        "- Their missing coverage",
        "- Candidate breakthrough angles for the new survey",
        "",
    ]
    return "\n".join(lines)


def build_pilot_markdown(topic: str) -> str:
    lines = [
        f"# Pilot Calibration: {topic}",
        "",
        "## Goal",
        "",
        "Calibrate taxonomy interpretation on 5-10 representative papers before full-table processing.",
        "",
        "## Required record per paper",
        "",
        "- Candidate classification",
        "- Why this classification was chosen",
        "- Neighbor category rejected and why",
        "- Evidence sufficiency",
        "- User correction",
        "- Rule learned for later batch processing",
        "",
    ]
    return "\n".join(lines)


def build_expansion_log_markdown(topic: str) -> str:
    return "\n".join(
        [
            f"# Paper Expansion Log: {topic}",
            "",
            "Record candidate paper searches, user confirmations, and row insertions for survey-oriented expansion.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--audience", default="Researchers preparing a survey manuscript")
    parser.add_argument("--article-goal", default="Build a survey-oriented literature workspace and writing scaffold")
    parser.add_argument(
        "--differentiation",
        default="Draft and refine how this survey differs from existing reviews, then drive workbook fields and evidence collection from that outline.",
    )
    args = parser.parse_args()

    workbook_path = Path(args.workbook).resolve()
    artifact_root = ensure_dir(build_artifact_root(workbook_path))
    project_dir = ensure_dir(artifact_root / "project")
    file_paths = project_file_paths(workbook_path)

    topic = normalize_text(args.topic)
    brief = build_brief_markdown(
        topic=topic,
        workbook_path=workbook_path,
        audience=normalize_text(args.audience),
        article_goal=normalize_text(args.article_goal),
        differentiation=normalize_text(args.differentiation),
    )
    outline = build_outline_markdown(topic)
    analysis = build_analysis_markdown(topic)
    pilot = build_pilot_markdown(topic)
    expansion = build_expansion_log_markdown(topic)

    file_paths["brief"].write_text(brief + "\n", encoding="utf-8")
    file_paths["outline"].write_text(outline + "\n", encoding="utf-8")
    file_paths["survey_analysis"].write_text(analysis + "\n", encoding="utf-8")
    file_paths["pilot"].write_text(pilot + "\n", encoding="utf-8")
    file_paths["expansion_log"].write_text(expansion + "\n", encoding="utf-8")
    if not file_paths["field_manual"].exists():
        file_paths["field_manual"].write_text("# Field Manual Draft\n\n", encoding="utf-8")

    summary = {
        "mode": PROJECT_MODE_SURVEY,
        "workbook": str(workbook_path),
        "artifact_root": str(artifact_root),
        "project_dir": str(project_dir),
        "files": {key: str(path) for key, path in file_paths.items()},
    }
    write_json(project_dir / "project-bootstrap.json", summary)
    emit_json(summary)


if __name__ == "__main__":
    main()
