#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from pypdf import PdfReader

from common import SUMMARY_HEADERS, emit_json, ensure_dir, parse_json_file, relative_path, slugify


def extract_pdf_text(pdf_path: Path, txt_path: Path) -> None:
    try:
        reader = PdfReader(str(pdf_path))
        parts: list[str] = []
        for page_index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.encode("utf-8", "replace").decode("utf-8", "replace")
            parts.append(f"[Page {page_index}]")
            parts.append(text.strip())
            parts.append("")
        txt_path.write_text("\n".join(parts).strip() + "\n", encoding="utf-8")
    except Exception as exc:
        fallback = "\n".join(
            [
                "[PDF text extraction failed]",
                str(exc),
                "",
                "The source PDF was preserved, but text extraction failed during this pass.",
                "",
            ]
        )
        txt_path.write_text(fallback, encoding="utf-8")


def collect_segments(source_text: str, max_segments: int = 8) -> list[dict[str, object]]:
    lines = [line.strip() for line in source_text.splitlines() if line.strip()]
    segments: list[dict[str, object]] = []
    current: list[str] = []
    start = 1
    for line_no, line in enumerate(lines, start=1):
        current.append(line)
        if len(" ".join(current)) >= 450 or len(current) >= 6:
            segments.append(
                {
                    "label": f"S{len(segments) + 1}",
                    "line_start": start,
                    "line_end": line_no,
                    "text": " ".join(current),
                }
            )
            current = []
            start = line_no + 1
            if len(segments) >= max_segments:
                break
    if current and len(segments) < max_segments:
        segments.append(
            {
                "label": f"S{len(segments) + 1}",
                "line_start": start,
                "line_end": start + len(current) - 1,
                "text": " ".join(current),
            }
        )
    return segments


def source_inventory_lines(source_payload: dict[str, object], local_source_rel: str, local_text_rel: str | None) -> list[str]:
    lines = [
        "## Source inventory",
        "",
        f"- Final resolved URL: {source_payload.get('resolved_url') or ''}",
        f"- Source kind: `{source_payload.get('source_kind') or ''}`",
        f"- Evidence level: `{source_payload.get('evidence_level') or ''}`",
        f"- Allow full backfill: `{bool(source_payload.get('allow_full_backfill'))}`",
        f"- Local source file: `{local_source_rel}`",
    ]
    if local_text_rel:
        lines.append(f"- Local text file: `{local_text_rel}`")
    secondary_urls = source_payload.get("secondary_urls") or []
    if isinstance(secondary_urls, list) and secondary_urls:
        lines.append("- Secondary URLs used:")
        for url in secondary_urls:
            lines.append(f"  - {url}")
    return lines


def build_markdown(
    row: int,
    title: str,
    link: str | None,
    source_payload: dict[str, object],
    local_source_rel: str,
    local_text_rel: str | None,
    evidence_rel: str,
    sheet_updates: dict[str, str],
    field_notes: dict[str, dict[str, str]] | None,
    warning: str | None,
    segments: list[dict[str, object]],
) -> str:
    lines: list[str] = [
        f"# {title}",
        "",
        "## Row metadata",
        "",
        f"- Row: `{row}`",
        f"- Original link: {link or ''}",
        f"- Source type: `{source_payload.get('status') or ''}`",
        f"- Source kind: `{source_payload.get('source_kind') or ''}`",
        f"- Evidence level: `{source_payload.get('evidence_level') or ''}`",
        f"- Allow full backfill: `{bool(source_payload.get('allow_full_backfill'))}`",
        f"- Access date: `{date.today().isoformat()}`",
        f"- Evidence file: `{evidence_rel}`",
    ]
    if warning:
        lines.append(f"- Warning: `{warning}`")

    lines.extend(["", *source_inventory_lines(source_payload, local_source_rel, local_text_rel), ""])
    lines.extend(["## Used source segments", ""])
    for segment in segments:
        locator_base = local_text_rel or local_source_rel
        lines.extend(
            [
                f"### {segment['label']}",
                f"- Location: `{locator_base}:L{segment['line_start']}-L{segment['line_end']}`",
                "",
                f"> {segment['text']}",
                "",
            ]
        )

    if field_notes:
        lines.extend(["## Classification conclusions", ""])
        for key, note in field_notes.items():
            if key in sheet_updates:
                lines.append(f"- `{key}`: {sheet_updates[key]}")
        lines.append("")

    lines.extend(["## Workbook updates", ""])
    for key, value in sheet_updates.items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "## Field-by-field evidence mapping", ""])
    if field_notes:
        for key, note in field_notes.items():
            lines.extend(
                [
                    f"### {key}",
                    f"- Decision question: {note.get('decision_question', 'Not explicitly recorded in this pass.')}",
                    f"- Value: {note.get('value', '')}",
                    f"- Source segments: {note.get('segments', '')}",
                    f"- Derivation: {note.get('derivation', '')}",
                    f"- Why not nearby categories: {note.get('exclusion_reason', 'Not explicitly recorded in this pass.')}",
                    f"- Evidence sufficiency: {note.get('evidence_sufficiency', 'Needs review')}",
                    "",
                ]
            )
    else:
        lines.append("- This row does not meet the current full-backfill threshold.")
        lines.append("")

    lines.extend(["## Decision chain", ""])
    if field_notes:
        for key, note in field_notes.items():
            lines.extend(
                [
                    f"### {key}",
                    f"- Decision question: {note.get('decision_question', 'Not explicitly recorded in this pass.')}",
                    f"- Final value: {note.get('value', '')}",
                    f"- Causal reasoning: {note.get('causal_reasoning', note.get('derivation', 'Not explicitly recorded in this pass.'))}",
                    f"- Exclusion reasoning: {note.get('exclusion_reason', 'Not explicitly recorded in this pass.')}",
                    f"- Evidence sufficiency: {note.get('evidence_sufficiency', 'Needs review')}",
                    "",
                ]
            )
    else:
        lines.append("- No full decision chain was generated in this pass.")
        lines.append("")

    lines.extend(["## Verified summary fields", ""])
    for key in SUMMARY_HEADERS:
        if key in sheet_updates:
            lines.append(f"- `{key}`: {sheet_updates[key]}")
    if not any(key in sheet_updates for key in SUMMARY_HEADERS):
        lines.append("- No verified summary fields were written in this pass.")

    lines.extend(["", "## Writing support", ""])
    if "写作引用章节" in sheet_updates:
        lines.append(f"- `写作引用章节`: {sheet_updates['写作引用章节']}")
    if "引用论据" in sheet_updates:
        lines.append(f"- `引用论据`: {sheet_updates['引用论据']}")
    if "写作引用章节" not in sheet_updates and "引用论据" not in sheet_updates:
        lines.append("- No writing-support fields were written in this pass.")

    lines.extend(["", "## Notes", ""])
    lines.append("- Keep reasoning constrained to the cited segments and the field-guide sheet.")
    if source_payload.get("source_kind") == "secondary_review":
        lines.append("- This row relies on a secondary review page rather than the original paper text.")
    if source_payload.get("status") == "abstract_only":
        lines.append("- This row is abstract-only and should not be treated as a high-confidence full verification.")
    if warning:
        lines.append("- This row currently carries a warning and should be treated conservatively.")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row", type=int, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--link")
    parser.add_argument("--source-json", required=True, help="JSON output from fetch_paper_sources.py")
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--sheet-updates-json", help="JSON file containing sheet updates for this row")
    parser.add_argument("--field-notes-json", help="Optional JSON file containing field derivation notes")
    args = parser.parse_args()

    source_payload = parse_json_file(Path(args.source_json))
    workspace_root = Path(args.workspace_root).resolve()
    evidence_dir = ensure_dir(Path(args.evidence_dir).resolve())

    row_stem = f"{args.row:03d}-{slugify(args.title)}"
    evidence_path = evidence_dir / f"{row_stem}.md"

    local_source_value = source_payload.get("local_source")
    if not local_source_value:
        raise SystemExit("source-json must contain local_source for evidence generation")
    local_source = Path(str(local_source_value)).resolve()
    local_text_rel: str | None = None

    if source_payload["status"] in {"pdf_download", "pdf_via_browser"}:
        txt_path = local_source.with_name("paper.txt")
        extract_pdf_text(local_source, txt_path)
        source_text = txt_path.read_text(encoding="utf-8", errors="replace")
        local_text_rel = relative_path(txt_path, workspace_root)
    else:
        source_text = local_source.read_text(encoding="utf-8", errors="replace")

    segments = collect_segments(source_text)
    sheet_updates = parse_json_file(Path(args.sheet_updates_json)) if args.sheet_updates_json else {}
    field_notes = parse_json_file(Path(args.field_notes_json)) if args.field_notes_json else None
    evidence_rel = relative_path(evidence_path, workspace_root)
    local_source_rel = relative_path(local_source, workspace_root)

    markdown = build_markdown(
        row=args.row,
        title=args.title,
        link=args.link,
        source_payload=source_payload,
        local_source_rel=local_source_rel,
        local_text_rel=local_text_rel,
        evidence_rel=evidence_rel,
        sheet_updates=sheet_updates,
        field_notes=field_notes,
        warning=source_payload.get("warning"),
        segments=segments,
    )
    evidence_path.write_text(markdown, encoding="utf-8")

    payload = {
        "row": args.row,
        "title": args.title,
        "source_type": source_payload["status"],
        "source_kind": source_payload.get("source_kind"),
        "evidence_level": source_payload.get("evidence_level"),
        "allow_full_backfill": bool(source_payload.get("allow_full_backfill")),
        "local_source": local_source_rel,
        "local_text": local_text_rel,
        "evidence_path": evidence_rel,
        "warning": source_payload.get("warning"),
    }
    emit_json(payload)


if __name__ == "__main__":
    main()
