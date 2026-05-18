#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    STATUS_FULLTEXT_WEB,
    STATUS_MISMATCH,
    STATUS_PDF_VIA_BROWSER,
    STATUS_SECONDARY_REVIEW,
    emit_json,
    evidence_level_for_status,
    normalize_text,
    parse_json_file,
    source_kind_for_status,
    status_allows_full_backfill,
    warning_for_status,
)


def build_payload(source_payload: dict[str, object], status: str, local_source: Path, resolved_url: str | None) -> dict[str, object]:
    payload = dict(source_payload)
    payload["status"] = status
    payload["resolved_url"] = resolved_url or payload.get("resolved_url")
    payload["local_source"] = str(local_source)
    payload["source_kind"] = source_kind_for_status(status)
    payload["evidence_level"] = evidence_level_for_status(status)
    payload["allow_full_backfill"] = status_allows_full_backfill(status)
    payload["warning"] = warning_for_status(status)
    payload["browser_required"] = False
    payload["browser_instructions"] = None
    payload["browser_completed"] = True
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-json", required=True)
    parser.add_argument("--row-asset-dir", required=True)
    parser.add_argument("--resolved-url")
    parser.add_argument("--force-status")
    args = parser.parse_args()

    source_payload = parse_json_file(Path(args.source_json))
    row_dir = Path(args.row_asset_dir).resolve()
    resolved_url = normalize_text(args.resolved_url) or normalize_text(source_payload.get("resolved_url"))
    force_status = normalize_text(args.force_status)

    pdf_path = row_dir / "paper.pdf"
    review_path = row_dir / "review.md"
    source_path = row_dir / "source.md"

    if force_status:
        forced_map = {
            "pdf_via_browser": (STATUS_PDF_VIA_BROWSER, pdf_path),
            "fulltext_web": (STATUS_FULLTEXT_WEB, source_path),
            "secondary_review": (STATUS_SECONDARY_REVIEW, review_path),
            "mismatch_or_unverifiable": (STATUS_MISMATCH, source_path if source_path.exists() else review_path),
        }
        if force_status not in forced_map:
            raise SystemExit(f"Unsupported --force-status: {force_status}")
        status, local_path = forced_map[force_status]
        if not local_path.exists():
            raise SystemExit(f"Forced status {force_status} requires existing file: {local_path}")
        emit_json(build_payload(source_payload, status, local_path, resolved_url))
        return

    if pdf_path.exists():
        emit_json(build_payload(source_payload, STATUS_PDF_VIA_BROWSER, pdf_path, resolved_url))
        return
    if review_path.exists():
        emit_json(build_payload(source_payload, STATUS_SECONDARY_REVIEW, review_path, resolved_url))
        return
    if source_path.exists():
        emit_json(build_payload(source_payload, STATUS_FULLTEXT_WEB, source_path, resolved_url))
        return

    raise SystemExit("No Browser capture artifact found. Expected paper.pdf, source.md, or review.md.")


if __name__ == "__main__":
    main()
