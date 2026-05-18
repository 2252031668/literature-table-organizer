#!/usr/bin/env python3
from __future__ import annotations

import argparse

from common import emit_json, normalize_text


def build_candidates(topic: str, aspect: str, chapter_gap: str | None) -> list[dict[str, str]]:
    normalized_topic = normalize_text(topic)
    normalized_aspect = normalize_text(aspect)
    normalized_gap = normalize_text(chapter_gap)
    base_reason = f"Relevant to {normalized_topic} with emphasis on {normalized_aspect}."
    gap_reason = f"Supports chapter gap: {normalized_gap}." if normalized_gap else "Supports an under-covered part of the outline."
    return [
        {
            "title": f"[Candidate] {normalized_aspect} foundation-model survey anchor",
            "link_hint": "Search by title + pdf/openreview/project page",
            "recommended_section": normalized_gap or "4. Representative Methods and Coordination Mechanisms",
            "reason": f"{base_reason} {gap_reason} Use as a calibration anchor or contrast paper.",
        },
        {
            "title": f"[Candidate] {normalized_aspect} evaluation or benchmark paper",
            "link_hint": "Search by title + benchmark/dataset/pdf",
            "recommended_section": normalized_gap or "5. Benchmarks, Datasets, and Evaluation Gaps",
            "reason": f"{base_reason} Helps fill evaluation, benchmark, or dataset coverage gaps.",
        },
        {
            "title": f"[Candidate] {normalized_aspect} boundary-case or counterexample paper",
            "link_hint": "Search by title + comparison/result/pdf",
            "recommended_section": normalized_gap or "6. Limitations and Outlook",
            "reason": f"{base_reason} Useful when the survey needs a counterexample, failure mode, or method-boundary discussion.",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--aspect", required=True)
    parser.add_argument("--chapter-gap")
    args = parser.parse_args()

    candidates = build_candidates(args.topic, args.aspect, args.chapter_gap)
    emit_json(
        {
            "topic": normalize_text(args.topic),
            "aspect": normalize_text(args.aspect),
            "chapter_gap": normalize_text(args.chapter_gap),
            "candidates": candidates,
        }
    )


if __name__ == "__main__":
    main()
