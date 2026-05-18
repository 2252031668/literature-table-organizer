#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from common import (
    STATUS_ABSTRACT_ONLY,
    STATUS_FULLTEXT_WEB,
    STATUS_MISMATCH,
    STATUS_PDF_DOWNLOAD,
    STATUS_SECONDARY_REVIEW,
    STATUS_UNRESOLVED,
    WARNING_MISSING_LINK,
    build_artifact_root,
    emit_json,
    ensure_dir,
    evidence_level_for_status,
    slugify,
    source_kind_for_status,
    status_allows_full_backfill,
    warning_for_status,
)


USER_AGENT = "Mozilla/5.0 (compatible; literature-table-organizer/2.0)"
REQUEST_TIMEOUT = 30
FULLTEXT_MIN_WORDS = 450
SECONDARY_REVIEW_MIN_WORDS = 300


@dataclass
class CandidateSource:
    url: str
    label: str
    kind: str


def choose_row_dir(base_dir: Path, row: int, title: str) -> Path:
    return ensure_dir(base_dir / f"{row:03d}-{slugify(title)}")


def fetch_url(url: str) -> requests.Response:
    response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT}, allow_redirects=True)
    response.raise_for_status()
    return response


def looks_like_pdf(response: requests.Response, url: str) -> bool:
    content_type = response.headers.get("content-type", "").lower()
    return "pdf" in content_type or url.lower().endswith(".pdf")


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def title_similarity(a: str, b: str) -> float:
    tokens_a = token_set(a)
    tokens_b = token_set(b)
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / max(len(tokens_a), len(tokens_b))


def soup_title(soup: BeautifulSoup, fallback: str) -> str:
    meta_title = soup.select_one("meta[name='citation_title']")
    if meta_title and meta_title.get("content"):
        return normalize_spaces(meta_title.get("content"))
    if soup.title and soup.title.string:
        return normalize_spaces(soup.title.string)
    return fallback


def arxiv_pdf_url(url: str) -> str | None:
    parsed = urlparse(url)
    if "arxiv.org" not in parsed.netloc:
        return None
    match = re.search(r"/abs/([^/?#]+)", parsed.path)
    if not match:
        return None
    return f"https://arxiv.org/pdf/{match.group(1)}.pdf"


def extract_pdf_links(soup: BeautifulSoup, base_url: str) -> list[CandidateSource]:
    links: list[CandidateSource] = []
    selectors = [
        ("meta[name='citation_pdf_url']", "content", "citation_pdf"),
        ("meta[name='eprints.document_url']", "content", "meta_document_url"),
        ("a[href$='.pdf']", "href", "anchor_pdf"),
        ("a[href*='/pdf']", "href", "anchor_pdf_like"),
        ("iframe[src*='.pdf']", "src", "iframe_pdf"),
        ("embed[src*='.pdf']", "src", "embed_pdf"),
        ("source[src*='.pdf']", "src", "source_pdf"),
    ]
    seen: set[str] = set()
    for selector, attr, label in selectors:
        for node in soup.select(selector):
            value = node.get(attr)
            if not value:
                continue
            candidate = urljoin(base_url, value)
            if candidate in seen:
                continue
            if ".pdf" in candidate.lower() or "/pdf" in candidate.lower():
                seen.add(candidate)
                links.append(CandidateSource(candidate, label, "pdf"))
    return links


def html_to_markdown(url: str, html: str, source_label: str, heading: str | None = None) -> str:
    soup = BeautifulSoup(html, "html.parser")
    title = heading or soup_title(soup, url)
    chunks: list[str] = [
        f"# {title}",
        "",
        f"- URL: {url}",
        f"- Access date: {date.today().isoformat()}",
        f"- Source label: {source_label}",
        "",
    ]
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        text = " ".join(tag.get_text(" ", strip=True).split())
        if not text:
            continue
        if tag.name.startswith("h"):
            level = "#" * min(int(tag.name[1]), 3)
            chunks.extend([f"{level} {text}", ""])
        else:
            chunks.append(text)
            chunks.append("")
        if len("\n".join(chunks)) > 24000:
            break
    return "\n".join(chunks).strip() + "\n"


def search_crossref(title: str) -> list[CandidateSource]:
    url = "https://api.crossref.org/works"
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
        params={"query.title": title, "rows": 5},
    )
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])
    results: list[CandidateSource] = []
    for item in items:
        title_list = item.get("title") or []
        link = item.get("URL")
        if not title_list or not link:
            continue
        if title_similarity(title, title_list[0]) >= 0.65:
            results.append(CandidateSource(link, "crossref", "paper_page"))
    return results


def fallback_search_candidates(title: str) -> list[CandidateSource]:
    query = quote_plus(f'{title} pdf OR openreview OR github OR project OR paper')
    return [CandidateSource(f"https://duckduckgo.com/html/?q={query}", "fallback_search", "search_page")]


def text_word_count(soup: BeautifulSoup) -> int:
    body = soup.get_text(" ", strip=True)
    return len(re.findall(r"\w+", body))


def is_secondary_review_url(url: str) -> bool:
    lowered = url.lower()
    return any(
        token in lowered
        for token in (
            "blog",
            "medium.com",
            "substack",
            "towardsdatascience",
            "hackernoon",
            "zenn.dev",
            "note.com",
        )
    )


def source_filename_for_status(status: str) -> str:
    if status == STATUS_SECONDARY_REVIEW:
        return "review.md"
    return "source.md"


def write_source_markdown(path: Path, url: str, html: str, source_label: str, title: str | None = None) -> None:
    path.write_text(html_to_markdown(url, html, source_label, title), encoding="utf-8")


def build_payload_base(row: int, title: str, link: str | None, row_dir: Path) -> dict[str, object]:
    return {
        "row": row,
        "title": title,
        "input_link": link,
        "asset_dir": str(row_dir),
        "resolved_url": None,
        "secondary_urls": [],
        "browser_required": False,
        "browser_instructions": None,
        "title_match_score": None,
        "source_kind": None,
        "evidence_level": None,
        "allow_full_backfill": False,
        "warning": None,
    }


def finalize_payload(payload: dict[str, object], status: str, local_source: Path | None, resolved_url: str | None, title_match_score: float | None) -> dict[str, object]:
    payload["status"] = status
    payload["resolved_url"] = resolved_url
    payload["title_match_score"] = title_match_score
    payload["source_kind"] = source_kind_for_status(status)
    payload["evidence_level"] = evidence_level_for_status(status)
    payload["allow_full_backfill"] = status_allows_full_backfill(status)
    payload["warning"] = payload.get("warning") or warning_for_status(status)
    if local_source is not None:
        payload["local_source"] = str(local_source)
    return payload


def try_pdf_candidate(candidate: CandidateSource, row_dir: Path, payload: dict[str, object]) -> dict[str, object] | None:
    response = fetch_url(candidate.url)
    final_url = response.url
    if not looks_like_pdf(response, final_url):
        return None
    pdf_path = row_dir / "paper.pdf"
    pdf_path.write_bytes(response.content)
    return finalize_payload(payload, STATUS_PDF_DOWNLOAD, pdf_path, final_url, payload.get("title_match_score"))


def inspect_candidate(title: str, candidate: CandidateSource, row_dir: Path, payload: dict[str, object]) -> dict[str, object] | None:
    response = fetch_url(candidate.url)
    final_url = response.url
    if looks_like_pdf(response, final_url):
        pdf_path = row_dir / "paper.pdf"
        pdf_path.write_bytes(response.content)
        return finalize_payload(payload, STATUS_PDF_DOWNLOAD, pdf_path, final_url, payload.get("title_match_score"))

    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    resolved_title = soup_title(soup, final_url)
    score = title_similarity(title, resolved_title)
    payload["title_match_score"] = score
    if score < 0.35 and candidate.kind != "search_page":
        payload["warning"] = warning_for_status(STATUS_MISMATCH)
        return finalize_payload(payload, STATUS_MISMATCH, None, final_url, score)

    pdf_links = extract_pdf_links(soup, final_url)
    for pdf_candidate in pdf_links:
        pdf_payload = try_pdf_candidate(pdf_candidate, row_dir, payload.copy())
        if pdf_payload:
            pdf_payload["secondary_urls"] = [candidate.url]
            pdf_payload["title_match_score"] = score
            return pdf_payload

    word_count = text_word_count(soup)
    if word_count >= FULLTEXT_MIN_WORDS and candidate.kind != "search_page":
        source_path = row_dir / source_filename_for_status(STATUS_FULLTEXT_WEB)
        write_source_markdown(source_path, final_url, html, candidate.label, resolved_title)
        return finalize_payload(payload, STATUS_FULLTEXT_WEB, source_path, final_url, score)

    if word_count >= SECONDARY_REVIEW_MIN_WORDS and is_secondary_review_url(final_url):
        review_path = row_dir / source_filename_for_status(STATUS_SECONDARY_REVIEW)
        write_source_markdown(review_path, final_url, html, candidate.label, resolved_title)
        return finalize_payload(payload, STATUS_SECONDARY_REVIEW, review_path, final_url, score)

    if candidate.kind == "search_page":
        search_path = row_dir / source_filename_for_status(STATUS_ABSTRACT_ONLY)
        write_source_markdown(search_path, final_url, html, candidate.label, resolved_title)
        payload["warning"] = warning_for_status(STATUS_ABSTRACT_ONLY)
        return finalize_payload(payload, STATUS_ABSTRACT_ONLY, search_path, final_url, score)

    payload["browser_required"] = True
    payload["browser_instructions"] = {
        "resolved_url": final_url,
        "reason": "Static fetching did not reach a PDF or sufficient fulltext page. Use Browser to try dynamic PDF/fulltext retrieval.",
        "suggested_actions": [
            "Open the resolved page in Browser.",
            "Look for PDF, Download, View PDF, OpenReview PDF, or publisher download controls.",
            "If a PDF opens or downloads, save it as paper.pdf in the row asset directory.",
            "If only a readable fulltext webpage is available, save an auditable source.md capture instead.",
        ],
    }
    return None


def resolve_candidates(title: str, link: str | None) -> tuple[list[CandidateSource], str | None]:
    candidates: list[CandidateSource] = []
    warning = None
    if link:
        candidates.append(CandidateSource(link, "input_link", "paper_page"))
        arxiv_pdf = arxiv_pdf_url(link)
        if arxiv_pdf:
            candidates.insert(0, CandidateSource(arxiv_pdf, "arxiv_pdf", "pdf"))
        return candidates, None

    warning = WARNING_MISSING_LINK
    candidates.extend(search_crossref(title))
    candidates.extend(fallback_search_candidates(title))
    return candidates, warning


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="Paper title")
    parser.add_argument("--row", type=int, required=True, help="Workbook row number")
    parser.add_argument("--artifacts-dir", required=True, help="Directory for per-paper assets")
    parser.add_argument("--link", help="Existing paper link")
    args = parser.parse_args()

    base_dir = Path(args.artifacts_dir).resolve()
    row_dir = choose_row_dir(base_dir, args.row, args.title)
    payload = build_payload_base(args.row, args.title, args.link, row_dir)

    candidates, link_warning = resolve_candidates(args.title, args.link)
    payload["search_candidates"] = [{"url": item.url, "label": item.label, "kind": item.kind} for item in candidates]
    if link_warning:
        payload["warning"] = link_warning

    if not candidates:
        emit_json(finalize_payload(payload, STATUS_UNRESOLVED, None, None, None))
        return

    for candidate in candidates:
        try:
            result = inspect_candidate(args.title, candidate, row_dir, payload.copy())
        except Exception as exc:
            payload.setdefault("errors", []).append({"url": candidate.url, "message": str(exc)})
            continue
        if result:
            emit_json(result)
            return

    if payload.get("browser_required"):
        unresolved = finalize_payload(payload, STATUS_UNRESOLVED, None, payload.get("resolved_url"), payload.get("title_match_score"))
        emit_json(unresolved)
        return

    emit_json(finalize_payload(payload, STATUS_UNRESOLVED, None, None, payload.get("title_match_score")))


if __name__ == "__main__":
    main()
