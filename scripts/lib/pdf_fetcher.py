from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from common import STATUS_DOWNLOAD_FAILED, STATUS_PDF_DOWNLOADED, STATUS_PDF_READY, ensure_dir


USER_AGENT = "Mozilla/5.0 (compatible; literature-table-organizer/3.0)"
REQUEST_TIMEOUT = 30


@dataclass
class CandidateSource:
    url: str
    label: str
    kind: str


def token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def title_similarity(a: str, b: str) -> float:
    tokens_a = token_set(a)
    tokens_b = token_set(b)
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / max(len(tokens_a), len(tokens_b))


def fetch_url(url: str) -> requests.Response:
    response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT}, allow_redirects=True)
    response.raise_for_status()
    return response


def looks_like_pdf(response: requests.Response, url: str) -> bool:
    content_type = response.headers.get("content-type", "").lower()
    return "pdf" in content_type or url.lower().endswith(".pdf")


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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


def download_pdf(url: str, out_dir: Path, expected_title: str | None = None) -> dict[str, object]:
    out_dir = ensure_dir(out_dir.resolve())
    candidates: list[CandidateSource] = [CandidateSource(url, "input_link", "paper_page")]
    arxiv_pdf = arxiv_pdf_url(url)
    if arxiv_pdf:
        candidates.insert(0, CandidateSource(arxiv_pdf, "arxiv_pdf", "pdf"))

    last_error = None
    for candidate in candidates:
        try:
            response = fetch_url(candidate.url)
        except Exception as exc:
            last_error = str(exc)
            continue

        final_url = response.url
        if looks_like_pdf(response, final_url):
            pdf_path = out_dir / "paper.pdf"
            pdf_path.write_bytes(response.content)
            return {
                "status": STATUS_PDF_DOWNLOADED,
                "input_url": url,
                "resolved_url": final_url,
                "pdf_path": str(pdf_path),
                "title_match_score": None,
                "warning": None,
                "needs_manual_check": False,
            }

        soup = BeautifulSoup(response.text, "html.parser")
        resolved_title = soup_title(soup, final_url)
        score = title_similarity(expected_title or resolved_title, resolved_title) if expected_title else None
        for pdf_candidate in extract_pdf_links(soup, final_url):
            try:
                pdf_response = fetch_url(pdf_candidate.url)
            except Exception as exc:
                last_error = str(exc)
                continue
            pdf_final_url = pdf_response.url
            if looks_like_pdf(pdf_response, pdf_final_url):
                pdf_path = out_dir / "paper.pdf"
                pdf_path.write_bytes(pdf_response.content)
                return {
                    "status": STATUS_PDF_DOWNLOADED,
                    "input_url": url,
                    "resolved_url": pdf_final_url,
                    "pdf_path": str(pdf_path),
                    "title_match_score": score,
                    "warning": None,
                    "needs_manual_check": bool(score is not None and score < 0.65),
                }

    return {
        "status": STATUS_DOWNLOAD_FAILED,
        "input_url": url,
        "resolved_url": None,
        "pdf_path": None,
        "title_match_score": None,
        "warning": last_error or "Static PDF download failed.",
        "needs_manual_check": True,
    }
