#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from pypdf import PdfReader

from common import ensure_dir, parse_json_file, relative_path, slugify


def extract_pdf_text(pdf_path: Path, txt_path: Path) -> None:
    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        parts.append(f"[Page {page_index}]")
        parts.append(text.strip())
        parts.append("")
    txt_path.write_text("\n".join(parts).strip() + "\n", encoding="utf-8")


def collect_segments(source_text: str, max_segments: int = 6) -> list[dict[str, object]]:
    lines = [line.strip() for line in source_text.splitlines() if line.strip()]
    segments: list[dict[str, object]] = []
    current: list[str] = []
    start = 1
    for line_no, line in enumerate(lines, start=1):
        current.append(line)
        if len(" ".join(current)) >= 350 or len(current) >= 5:
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


def build_markdown(
    row: int,
    title: str,
    link: str | None,
    source_type: str,
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
        f"- Row: `{row}`",
        f"- Original link: {link or ''}",
        f"- Source type: `{source_type}`",
        f"- Local source file: `{local_source_rel}`",
        f"- Access date: `{date.today().isoformat()}`",
        f"- Evidence file: `{evidence_rel}`",
    ]
    if local_text_rel:
        lines.append(f"- Local text file: `{local_text_rel}`")
    if warning:
        lines.append(f"- Warning: `{warning}`")

    lines.extend(["", "## Used source segments", ""])
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

    lines.extend(["## Workbook updates", ""])
    for key, value in sheet_updates.items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "## Field evidence mapping", ""])
    if field_notes:
        for key, note in field_notes.items():
            lines.extend(
                [
                    f"### {key}",
                    f"- Value: {note.get('value', '')}",
                    f"- Source segments: {note.get('segments', '')}",
                    f"- Derivation: {note.get('derivation', '')}",
                    "",
                ]
            )
    else:
        lines.append("- Add field-by-field derivations when the classification pass is completed.")
        lines.append("")

    lines.extend(["## Notes", ""])
    lines.append("- Keep reasoning constrained to the cited segments and the field-guide sheet.")
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
    local_source = Path(str(source_payload["local_source"])).resolve()
    local_text_rel: str | None = None

    if source_payload["status"] == "pdf_download":
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
        source_type=str(source_payload["status"]),
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
        "local_source": local_source_rel,
        "local_text": local_text_rel,
        "evidence_path": evidence_rel,
        "warning": source_payload.get("warning"),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
