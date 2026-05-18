#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


PAPER_TITLE_HEADER = "\u8bba\u6587\u5168\u540d"
PAPER_LINK_HEADER = "\u8bba\u6587\u94fe\u63a5"
ABSTRACT_HEADER = "\u6458\u8981"
FIELD_HEADER = "\u5b57\u6bb5"
FIELD_GUIDANCE_HEADER = "\u5efa\u8bae\u586b\u5199\u65b9\u5f0f"
FIELD_VALUE_HEADER = "\u63a8\u8350\u53d6\u503c/\u8bf4\u660e"
LOCAL_FILE_HEADER = "\u672c\u5730\u6587\u4ef6\u8def\u5f84"
EVIDENCE_PATH_HEADER = "\u8bc1\u636e\u94fe\u8def\u5f84"
WARNING_HEADER = "\u6838\u9a8c\u8b66\u544a/\u72b6\u6001"
WRITING_SECTION_HEADER = "\u5199\u4f5c\u5f15\u7528\u7ae0\u8282"
WRITING_EVIDENCE_HEADER = "\u5f15\u7528\u8bba\u636e"
PROJECT_MODE_SURVEY = "survey_oriented"
PROJECT_MODE_STANDARD = "standard"
FIELD_MANUAL_STATUS_DRAFT = "draft"
FIELD_MANUAL_STATUS_NEEDS_CONFIRMATION = "needs_user_confirmation"
FIELD_MANUAL_STATUS_CONFIRMED = "confirmed"
PILOT_STATUS_DRAFT = "draft"
PILOT_STATUS_READY = "ready"
PILOT_STATUS_CONFIRMED = "confirmed"
CLASSIFICATION_HEADERS = [
    "\u8303\u5f0f\u6620\u5c04",
    "\u8303\u5f0f\u5c0f\u7c7b",
    "\u529f\u80fd\u6620\u5c04\u5c42",
    "\u534f\u540c\u7c92\u5ea6",
    "\u662f\u5426\u4e3a\u53cc\u81c2\u9488\u5bf9\u8bbe\u8ba1",
]
SUMMARY_HEADERS = [
    "\u6838\u9a8c\u540e\u6838\u5fc3\u65b9\u6cd5",
    "\u6838\u9a8c\u540e\u4efb\u52a1/\u6570\u636e\u96c6",
    "\u6838\u9a8c\u540e\u5173\u952e\u7ed3\u679c",
    "\u6838\u9a8c\u540e\u4e3b\u8981\u5c40\u9650",
]

SYSTEM_HEADERS = [LOCAL_FILE_HEADER, EVIDENCE_PATH_HEADER, WARNING_HEADER]
SURVEY_SYSTEM_HEADERS = SYSTEM_HEADERS + [WRITING_SECTION_HEADER, WRITING_EVIDENCE_HEADER]

PROJECT_ARTIFACT_FILES = {
    "brief": "project-brief.md",
    "survey_analysis": "related-survey-analysis.md",
    "outline": "outline.md",
    "field_manual": "field-manual.md",
    "field_gap_analysis": "field-gap-analysis.md",
    "pilot": "pilot-calibration.md",
    "expansion_log": "paper-expansion-log.md",
}

STATUS_PDF_DOWNLOAD = "pdf_download"
STATUS_PDF_VIA_BROWSER = "pdf_via_browser"
STATUS_FULLTEXT_WEB = "fulltext_web"
STATUS_SECONDARY_REVIEW = "secondary_review"
STATUS_ABSTRACT_ONLY = "abstract_only"
STATUS_BROWSER_PENDING = "browser_pending"
STATUS_UNRESOLVED = "unresolved"
STATUS_MISMATCH = "mismatch_or_unverifiable"

PRIMARY_SOURCE_STATUSES = {
    STATUS_PDF_DOWNLOAD,
    STATUS_PDF_VIA_BROWSER,
    STATUS_FULLTEXT_WEB,
}
SECONDARY_SOURCE_STATUSES = {
    STATUS_SECONDARY_REVIEW,
}
LOW_CONFIDENCE_SOURCE_STATUSES = {
    STATUS_ABSTRACT_ONLY,
    STATUS_BROWSER_PENDING,
    STATUS_UNRESOLVED,
    STATUS_MISMATCH,
}

WARNING_MISSING_LINK = "\u94fe\u63a5\u7f3a\u5931\uff0c\u6309\u6807\u9898\u68c0\u7d22"
WARNING_WEB_ONLY = "\u672a\u83b7\u5168\u6587PDF\uff0c\u57fa\u4e8e\u5168\u6587\u7f51\u9875\u8bc1\u636e"
WARNING_SECONDARY = "\u57fa\u4e8e\u4e8c\u624b\u89e3\u8bfb\u8bc1\u636e"
WARNING_ABSTRACT_ONLY = "\u4ec5\u83b7\u6458\u8981\uff0c\u4e0d\u5efa\u8bae\u5b8c\u6574\u56de\u586b"
WARNING_BROWSER_PENDING = "\u9700\u8981Browser\u52a8\u6001\u6293\u53d6\uff0c\u6682\u4e0d\u8fdb\u5165\u5b8c\u6574\u56de\u586b"
WARNING_INSUFFICIENT = "\u8bc1\u636e\u4e0d\u8db3\uff0c\u7ed3\u8bba\u5f85\u786e\u8ba4"
WARNING_MISMATCH = "\u6807\u9898-\u94fe\u63a5\u7591\u4f3c\u9519\u914d"
WARNING_MISSING_TARGET = "\u672c\u5730\u8def\u5f84\u76ee\u6807\u7f3a\u5931"

WARNING_BY_STATUS = {
    STATUS_PDF_DOWNLOAD: None,
    STATUS_PDF_VIA_BROWSER: None,
    STATUS_FULLTEXT_WEB: WARNING_WEB_ONLY,
    STATUS_SECONDARY_REVIEW: WARNING_SECONDARY,
    STATUS_ABSTRACT_ONLY: WARNING_ABSTRACT_ONLY,
    STATUS_BROWSER_PENDING: WARNING_BROWSER_PENDING,
    STATUS_UNRESOLVED: WARNING_INSUFFICIENT,
    STATUS_MISMATCH: WARNING_MISMATCH,
}

SOURCE_KIND_BY_STATUS = {
    STATUS_PDF_DOWNLOAD: "primary_pdf",
    STATUS_PDF_VIA_BROWSER: "primary_pdf_browser",
    STATUS_FULLTEXT_WEB: "primary_fulltext_web",
    STATUS_SECONDARY_REVIEW: "secondary_review",
    STATUS_ABSTRACT_ONLY: "abstract_only",
    STATUS_BROWSER_PENDING: "browser_pending",
    STATUS_UNRESOLVED: "unresolved",
    STATUS_MISMATCH: "mismatch_or_unverifiable",
}

EVIDENCE_LEVEL_BY_STATUS = {
    STATUS_PDF_DOWNLOAD: "primary_fulltext_pdf",
    STATUS_PDF_VIA_BROWSER: "primary_fulltext_pdf",
    STATUS_FULLTEXT_WEB: "primary_fulltext_web",
    STATUS_SECONDARY_REVIEW: "secondary_review",
    STATUS_ABSTRACT_ONLY: "abstract_only",
    STATUS_BROWSER_PENDING: "browser_pending",
    STATUS_UNRESOLVED: "unresolved",
    STATUS_MISMATCH: "mismatch_or_unverifiable",
}

EVIDENCE_SUFFICIENCY_BY_STATUS = {
    STATUS_PDF_DOWNLOAD: "strong",
    STATUS_PDF_VIA_BROWSER: "strong",
    STATUS_FULLTEXT_WEB: "moderate",
    STATUS_SECONDARY_REVIEW: "moderate",
    STATUS_ABSTRACT_ONLY: "weak",
    STATUS_BROWSER_PENDING: "pending",
    STATUS_UNRESOLVED: "pending",
    STATUS_MISMATCH: "pending",
}


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_key(value: object) -> str:
    return normalize_text(value).lower()


PRIMARY_TITLE_HEADERS = {
    normalize_key(value)
    for value in (
        PAPER_TITLE_HEADER,
        "paper title",
        "title",
    )
}
OPTIONAL_LINK_HEADERS = {
    normalize_key(value)
    for value in (
        PAPER_LINK_HEADER,
        "paper link",
        "link",
        "url",
    )
}
OPTIONAL_ABSTRACT_HEADERS = {
    normalize_key(value)
    for value in (
        ABSTRACT_HEADER,
        "abstract",
        "summary",
    )
}
FIELD_COL_KEYS = {
    normalize_key(value)
    for value in (
        FIELD_HEADER,
        "\u5b57\u6bb5\u540d",
        "field",
        "field name",
    )
}
GUIDANCE_COL_KEYS = {
    normalize_key(value)
    for value in (
        FIELD_GUIDANCE_HEADER,
        "\u586b\u5199\u65b9\u5f0f",
        "\u5efa\u8bae",
        "how to fill",
        "guidance",
    )
}
VALUE_COL_KEYS = {
    normalize_key(value)
    for value in (
        FIELD_VALUE_HEADER,
        "\u8bf4\u660e",
        "\u63a8\u8350\u503c/\u8bf4\u660e",
        "\u63a8\u8350\u53d6\u503c",
        "recommended values",
        "recommended values/notes",
    )
}


def slugify(text: str) -> str:
    value = text.replace("++", " plus plus ")
    value = value.replace("+", " plus ")
    value = value.replace("&", " and ")
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii").lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "item"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def use_legacy_artifacts() -> bool:
    return os.environ.get("LTO_USE_LEGACY_ARTIFACTS", "").strip().lower() in {"1", "true", "yes"}


def build_artifact_root(workbook_path: Path) -> Path:
    preferred = workbook_path.parent / f"{workbook_path.stem}_artifacts"
    legacy = workbook_path.parent / "artifacts"
    if use_legacy_artifacts() and legacy.exists():
        return legacy
    return preferred


def manifest_path_for_workbook(workbook_path: Path) -> Path:
    return build_artifact_root(workbook_path) / "manifest.json"


def project_dir_for_workbook(workbook_path: Path) -> Path:
    return build_artifact_root(workbook_path) / "project"


def project_file_paths(workbook_path: Path) -> dict[str, Path]:
    project_dir = project_dir_for_workbook(workbook_path)
    return {key: project_dir / filename for key, filename in PROJECT_ARTIFACT_FILES.items()}


def workflow_state_path_for_workbook(workbook_path: Path) -> Path:
    return project_dir_for_workbook(workbook_path) / "workflow-state.json"


def pilot_summary_path_for_workbook(workbook_path: Path) -> Path:
    return project_dir_for_workbook(workbook_path) / "pilot-summary.json"


def fieldguide_mapping_path_for_workbook(workbook_path: Path) -> Path:
    return project_dir_for_workbook(workbook_path) / "fieldguide-mapping.json"


def relative_path(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def parse_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def emit_json(payload: Any) -> None:
    data = json.dumps(payload, ensure_ascii=True, indent=2)
    sys.stdout.write(data)


def read_json_if_exists(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return parse_json_file(path)


def load_workflow_state(workbook_path: Path) -> dict[str, Any]:
    state = read_json_if_exists(workflow_state_path_for_workbook(workbook_path), {})
    return state if isinstance(state, dict) else {}


def save_workflow_state(workbook_path: Path, state: dict[str, Any]) -> Path:
    path = workflow_state_path_for_workbook(workbook_path)
    write_json(path, state)
    return path


def run_command(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    executable = cmd[0]
    if executable == "lark-cli":
        resolved = shutil.which("lark-cli.cmd") or shutil.which("lark-cli") or shutil.which("lark-cli.ps1")
        if resolved:
            cmd = [resolved, *cmd[1:]]
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def parse_feishu_url(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        raise ValueError(f"Unsupported Feishu URL: {url}")
    if "sheets" in parts:
        index = parts.index("sheets")
        return {"kind": "sheet", "token": parts[index + 1]}
    if "wiki" in parts:
        index = parts.index("wiki")
        return {"kind": "wiki", "token": parts[index + 1]}
    raise ValueError(f"Unsupported Feishu URL: {url}")


def resolve_feishu_sheet_token(url: str) -> dict[str, str]:
    parsed = parse_feishu_url(url)
    if parsed["kind"] == "sheet":
        return parsed
    result = run_command(
        [
            "lark-cli",
            "wiki",
            "spaces",
            "get_node",
            "--params",
            json.dumps({"token": parsed["token"]}, ensure_ascii=False),
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Failed to resolve wiki node")
    payload = json.loads(result.stdout)
    node = payload.get("data", {}).get("node") or payload.get("node") or {}
    obj_type = node.get("obj_type")
    obj_token = node.get("obj_token")
    if obj_type != "sheet" or not obj_token:
        raise ValueError("The Feishu wiki link does not resolve to a sheet document")
    return {"kind": "sheet", "token": obj_token}


def col_to_letter(index: int) -> str:
    letters: list[str] = []
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters.append(chr(65 + remainder))
    return "".join(reversed(letters))


def warning_for_status(status: str) -> str | None:
    return WARNING_BY_STATUS.get(status)


def source_kind_for_status(status: str) -> str:
    return SOURCE_KIND_BY_STATUS.get(status, status)


def evidence_level_for_status(status: str) -> str:
    return EVIDENCE_LEVEL_BY_STATUS.get(status, status)


def status_allows_full_backfill(status: str) -> bool:
    return status in PRIMARY_SOURCE_STATUSES or status in SECONDARY_SOURCE_STATUSES


def evidence_sufficiency_for_status(status: str) -> str:
    return EVIDENCE_SUFFICIENCY_BY_STATUS.get(status, "pending")


def html_fragment_to_text(fragment: str) -> str:
    if "<" not in fragment or ">" not in fragment:
        return normalize_text(unescape(fragment))
    text = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    text = re.sub(r"</(p|h1|h2|h3|li|tr)>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_markdown_headings(text: str) -> list[str]:
    headings: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            headings.append(re.sub(r"^#+\s*", "", line).strip())
            continue
        if re.match(r"^\d+(\.\d+)*\s+\S+", line):
            headings.append(line)
            continue
        if len(headings) >= 12:
            break
    return headings


def extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml_bytes = archive.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    parts: list[str] = []
    for node in root.iter():
        if node.tag.endswith("}t") and node.text:
            parts.append(node.text)
        elif node.tag.endswith("}p"):
            parts.append("\n")
    text = "".join(parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def read_draft_source(source: str | None) -> dict[str, Any]:
    if not source:
        return {
            "source": None,
            "kind": None,
            "title": None,
            "text": "",
            "headings": [],
        }

    value = source.strip()
    if value.startswith("http://") or value.startswith("https://"):
        result = run_command(
            [
                "lark-cli",
                "docs",
                "+fetch",
                "--api-version",
                "v2",
                "--doc",
                value,
            ]
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Failed to fetch draft source")
        payload = json.loads(result.stdout)
        doc = payload.get("data", {}).get("document", {}) or {}
        content = str(doc.get("content") or "")
        text = html_fragment_to_text(content)
        title_match = re.search(r"<title>(.*?)</title>", content, flags=re.I | re.S)
        return {
            "source": value,
            "kind": "feishu_doc",
            "title": normalize_text(title_match.group(1)) if title_match else None,
            "text": text,
            "headings": extract_markdown_headings(text),
        }

    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Draft source does not exist: {path}")

    suffix = path.suffix.lower()
    if suffix in {".md", ".txt"}:
        text = path.read_text(encoding="utf-8", errors="replace")
    elif suffix == ".docx":
        text = extract_docx_text(path)
    else:
        text = path.read_text(encoding="utf-8", errors="replace")

    return {
        "source": str(path),
        "kind": suffix.lstrip(".") or "text",
        "title": path.stem,
        "text": text.strip(),
        "headings": extract_markdown_headings(text),
    }


def markdown_has_unresolved_placeholders(text: str) -> bool:
    lowered = text.lower()
    return "todo" in lowered or "to fill" in lowered or "[confirm]" in lowered
