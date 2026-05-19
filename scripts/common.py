#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
import zipfile
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


PAPER_TITLE_HEADER = "论文全名"
PAPER_LINK_HEADER = "论文链接"
ABSTRACT_HEADER = "摘要"
FIELD_HEADER = "字段"
FIELD_GUIDANCE_HEADER = "建议填写方式"
FIELD_VALUE_HEADER = "推荐取值/说明"
LOCAL_FILE_HEADER = "本地文件路径"
EVIDENCE_PATH_HEADER = "证据链路径"
WARNING_HEADER = "核验警告/状态"
WRITING_SECTION_HEADER = "写作引用章节"
WRITING_ARGUMENT_HEADER = "引用论据"

PROJECT_MODE_SURVEY = "survey"

FRAMEWORK_STATUS_DRAFT = "draft"
FRAMEWORK_STATUS_CONFIRMED = "confirmed"
PILOT_STATUS_DRAFT = "draft"
PILOT_STATUS_READY = "ready"
PILOT_STATUS_CONFIRMED = "confirmed"

STATUS_PDF_READY = "pdf_ready"
STATUS_PDF_DOWNLOADED = "pdf_downloaded"
STATUS_DOWNLOAD_FAILED = "download_failed"
STATUS_NEEDS_LINK = "needs_link"
STATUS_REVIEW_REQUIRED = "review_required"
STATUS_COMPLETE = "complete"

FRAMEWORK_FILENAME = "framework.md"
FRAMEWORK_SCHEMA_FILENAME = "framework.schema.json"
PROJECT_BRIEF_FILENAME = "project-brief.md"
SURVEY_GAP_ANALYSIS_FILENAME = "survey-gap-analysis.md"
PILOT_CALIBRATION_FILENAME = "pilot-calibration.md"
REVIEW_QUEUE_FILENAME = "review-queue.md"
EXPANSION_LOG_FILENAME = "expansion-log.md"
WORKFLOW_STATE_FILENAME = "workflow-state.json"
PILOT_TASKS_FILENAME = "pilot-tasks.json"
BATCH_TASKS_FILENAME = "batch-tasks.json"
HEADER_MAPPING_FILENAME = "header-mapping.json"

PAPERS_DIRNAME = "papers"
PAPER_REPORTS_DIRNAME = "paper-reports"
ROW_ANALYSIS_DIRNAME = "row-analysis"
PROJECT_DIRNAME = "project"

CANONICAL_HEADER_ORDER = [
    "paper_title",
    "paper_link",
    "abstract",
    "paradigm_mapping",
    "paradigm_subtype",
    "functional_layer",
    "planning_granularity",
    "bimanual_design_type",
    "verified_core_method",
    "verified_tasks_datasets",
    "verified_key_results",
    "verified_limitations",
    "local_file_path",
    "evidence_path",
    "verification_status",
    "writing_section",
    "writing_argument",
]

CANONICAL_TO_ZH = {
    "paper_title": PAPER_TITLE_HEADER,
    "paper_link": PAPER_LINK_HEADER,
    "abstract": ABSTRACT_HEADER,
    "paradigm_mapping": "范式映射",
    "paradigm_subtype": "范式小类",
    "functional_layer": "功能映射层",
    "planning_granularity": "规划粒度",
    "bimanual_design_type": "是否为双臂针对设计",
    "verified_core_method": "核验后核心方法",
    "verified_tasks_datasets": "核验后任务/数据集",
    "verified_key_results": "核验后关键结果",
    "verified_limitations": "核验后主要局限",
    "local_file_path": LOCAL_FILE_HEADER,
    "evidence_path": EVIDENCE_PATH_HEADER,
    "verification_status": WARNING_HEADER,
    "writing_section": WRITING_SECTION_HEADER,
    "writing_argument": WRITING_ARGUMENT_HEADER,
}

CANONICAL_TO_EN = {key: key for key in CANONICAL_HEADER_ORDER}

CANONICAL_HEADER_ALIASES = {
    "paper_title": [PAPER_TITLE_HEADER, "paper title", "title", "paper_title"],
    "paper_link": [PAPER_LINK_HEADER, "paper link", "link", "url", "paper_link"],
    "abstract": [ABSTRACT_HEADER, "abstract", "summary"],
    "paradigm_mapping": ["范式映射", "paradigm mapping", "paradigm_mapping"],
    "paradigm_subtype": ["范式小类", "paradigm subtype", "paradigm_subtype"],
    "functional_layer": ["功能映射层", "paradigm layer", "functional layer", "functional_layer"],
    "planning_granularity": [
        "规划粒度",
        "协同粒度",
        "planning granularity",
        "planning_granularity",
        "coordination granularity",
    ],
    "bimanual_design_type": [
        "是否为双臂针对设计",
        "bimanual design type",
        "bimanual_design_type",
    ],
    "verified_core_method": ["核验后核心方法", "verified core method", "verified_core_method"],
    "verified_tasks_datasets": [
        "核验后任务/数据集",
        "verified tasks/datasets",
        "verified_tasks_datasets",
    ],
    "verified_key_results": ["核验后关键结果", "verified key results", "verified_key_results"],
    "verified_limitations": ["核验后主要局限", "verified limitations", "verified_limitations"],
    "local_file_path": [LOCAL_FILE_HEADER, "local file path", "local_file_path"],
    "evidence_path": [EVIDENCE_PATH_HEADER, "evidence path", "evidence_path"],
    "verification_status": [WARNING_HEADER, "verification status", "warning/status", "verification_status"],
    "writing_section": [WRITING_SECTION_HEADER, "writing section", "writing_section"],
    "writing_argument": [WRITING_ARGUMENT_HEADER, "writing argument", "writing_argument"],
}

FIELD_GUIDE_HEADER_ALIASES = {
    "field_name": [FIELD_HEADER, "字段名", "field", "field name", "field_name"],
    "fill_guidance": [FIELD_GUIDANCE_HEADER, "填写方式", "建议", "guidance", "fill guidance", "fill_guidance"],
    "recommended_values": [FIELD_VALUE_HEADER, "说明", "推荐取值", "recommended values", "recommended_values"],
}

WRITEBACK_GUARDED_KEYS = {
    "paradigm_mapping",
    "paradigm_subtype",
    "functional_layer",
    "planning_granularity",
    "bimanual_design_type",
    "verified_core_method",
    "verified_tasks_datasets",
    "verified_key_results",
    "verified_limitations",
    "writing_section",
    "writing_argument",
}


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_key(value: object) -> str:
    return normalize_text(value).lower()


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


def build_artifact_root(workbook_path: Path) -> Path:
    return workbook_path.parent / f"{workbook_path.stem}_artifacts"


def project_dir_for_workbook(workbook_path: Path) -> Path:
    return build_artifact_root(workbook_path) / PROJECT_DIRNAME


def papers_dir_for_workbook(workbook_path: Path) -> Path:
    return build_artifact_root(workbook_path) / PAPERS_DIRNAME


def paper_reports_dir_for_workbook(workbook_path: Path) -> Path:
    return build_artifact_root(workbook_path) / PAPER_REPORTS_DIRNAME


def row_analysis_dir_for_workbook(workbook_path: Path) -> Path:
    return build_artifact_root(workbook_path) / ROW_ANALYSIS_DIRNAME


def project_file_paths(workbook_path: Path) -> dict[str, Path]:
    project_dir = project_dir_for_workbook(workbook_path)
    return {
        "framework": project_dir / FRAMEWORK_FILENAME,
        "framework_schema": project_dir / FRAMEWORK_SCHEMA_FILENAME,
        "project_brief": project_dir / PROJECT_BRIEF_FILENAME,
        "survey_gap_analysis": project_dir / SURVEY_GAP_ANALYSIS_FILENAME,
        "pilot_calibration": project_dir / PILOT_CALIBRATION_FILENAME,
        "review_queue": project_dir / REVIEW_QUEUE_FILENAME,
        "expansion_log": project_dir / EXPANSION_LOG_FILENAME,
        "workflow_state": project_dir / WORKFLOW_STATE_FILENAME,
        "pilot_tasks": project_dir / PILOT_TASKS_FILENAME,
        "batch_tasks": project_dir / BATCH_TASKS_FILENAME,
        "header_mapping": project_dir / HEADER_MAPPING_FILENAME,
    }


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
    sys.stdout.write(json.dumps(payload, ensure_ascii=True, indent=2))


def read_json_if_exists(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return parse_json_file(path)


def workflow_state_path_for_workbook(workbook_path: Path) -> Path:
    return project_file_paths(workbook_path)["workflow_state"]


def load_workflow_state(workbook_path: Path) -> dict[str, Any]:
    state = read_json_if_exists(workflow_state_path_for_workbook(workbook_path), {})
    return state if isinstance(state, dict) else {}


def save_workflow_state(workbook_path: Path, state: dict[str, Any]) -> Path:
    path = workflow_state_path_for_workbook(workbook_path)
    write_json(path, state)
    return path


def canonical_key_for_header(value: object) -> str | None:
    normalized = normalize_key(value)
    for key, aliases in CANONICAL_HEADER_ALIASES.items():
        if normalized in {normalize_key(alias) for alias in aliases}:
            return key
    return None


def canonical_fieldguide_key(value: object) -> str | None:
    normalized = normalize_key(value)
    for key, aliases in FIELD_GUIDE_HEADER_ALIASES.items():
        if normalized in {normalize_key(alias) for alias in aliases}:
            return key
    return None


def preferred_header_for_key(key: str, language: str = "english") -> str:
    if language == "chinese":
        return CANONICAL_TO_ZH.get(key, key)
    return CANONICAL_TO_EN.get(key, key)


def detect_header_language(headers: list[str]) -> str:
    zh_hits = 0
    en_hits = 0
    for header in headers:
        key = canonical_key_for_header(header)
        if not key:
            continue
        if normalize_text(header) == CANONICAL_TO_ZH.get(key, ""):
            zh_hits += 1
        if normalize_key(header) == CANONICAL_TO_EN.get(key, "").lower():
            en_hits += 1
    return "english" if en_hits > zh_hits else "chinese"


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
        elif re.match(r"^\d+(\.\d+)*\s+\S+", line):
            headings.append(line)
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
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def run_command(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
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
        return {
            "source": value,
            "kind": "url",
            "title": None,
            "text": "",
            "headings": [],
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


def parse_row_spec(spec: str) -> list[int]:
    rows: set[int] = set()
    for part in spec.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            for value in range(min(start, end), max(start, end) + 1):
                rows.add(value)
        else:
            rows.add(int(token))
    return sorted(rows)


def markdown_has_unresolved_placeholders(text: str) -> bool:
    lowered = text.lower()
    return "todo" in lowered or "待填写" in lowered or "[confirm]" in lowered
