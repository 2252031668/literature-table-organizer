#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from common import ensure_dir, slugify


USER_AGENT = "Mozilla/5.0 (compatible; literature-table-organizer/1.0)"
WARNING_MISSING_LINK = "\u94fe\u63a5\u7f3a\u5931\uff0c\u6309\u6807\u9898\u68c0\u7d22"
WARNING_INSUFFICIENT = "\u8bc1\u636e\u4e0d\u8db3\uff0c\u7ed3\u8bba\u5f85\u786e\u8ba4"


def choose_row_dir(base_dir: Path, row: int, title: str) -> Path:
    return ensure_dir(base_dir / f"{row:03d}-{slugify(title)}")


def fetch_url(url: str) -> requests.Response:
    response = requests.get(url, timeout=30, headers={"User-Agent": USER_AGENT}, allow_redirects=True)
    response.raise_for_status()
    return response


def looks_like_pdf(response: requests.Response, url: str) -> bool:
    content_type = response.headers.get("content-type", "").lower()
    return "pdf" in content_type or url.lower().endswith(".pdf")


def extract_pdf_link(html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    selectors = [
        ('a[href$=".pdf"]', "href"),
        ('meta[name="citation_pdf_url"]', "content"),
        ('meta[property="og:url"]', "content"),
    ]
    for selector, attr in selectors:
        node = soup.select_one(selector)
        if node and node.get(attr):
            value = node.get(attr)
            candidate = urljoin(base_url, value)
            if candidate.lower().endswith(".pdf") or "/pdf" in candidate.lower():
                return candidate
    return None


def html_to_markdown(url: str, html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    chunks: list[str] = [f"# {title}", "", f"- URL: {url}", f"- Access date: {date.today().isoformat()}", ""]
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
        if len("\n".join(chunks)) > 12000:
            break
    return "\n".join(chunks).strip() + "\n"


def search_crossref(title: str) -> list[dict[str, str]]:
    url = "https://api.crossref.org/works"
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": USER_AGENT},
        params={"query.title": title, "rows": 5},
    )
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])
    results: list[dict[str, str]] = []
    for item in items:
        title_list = item.get("title") or []
        if not title_list:
            continue
        link = item.get("URL")
        if not link:
            continue
        results.append({"title": title_list[0], "url": link})
    return results


def title_similarity(a: str, b: str) -> float:
    tokens_a = set(re.findall(r"[a-z0-9]+", a.lower()))
    tokens_b = set(re.findall(r"[a-z0-9]+", b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / max(len(tokens_a), len(tokens_b))


def resolve_best_url(title: str, link: str | None) -> tuple[str | None, list[dict[str, str]], str | None]:
    if link:
        return link, [], None
    candidates = search_crossref(title)
    for candidate in candidates:
        if title_similarity(title, candidate["title"]) >= 0.65:
            return candidate["url"], candidates, WARNING_MISSING_LINK
    return None, candidates, WARNING_INSUFFICIENT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="Paper title")
    parser.add_argument("--row", type=int, required=True, help="Workbook row number")
    parser.add_argument("--artifacts-dir", required=True, help="Directory for per-paper assets")
    parser.add_argument("--link", help="Existing paper link")
    args = parser.parse_args()

    base_dir = Path(args.artifacts_dir).resolve()
    row_dir = choose_row_dir(base_dir, args.row, args.title)
    resolved_url, search_candidates, warning = resolve_best_url(args.title, args.link)

    payload: dict[str, object] = {
        "row": args.row,
        "title": args.title,
        "input_link": args.link,
        "resolved_url": resolved_url,
        "search_candidates": search_candidates,
        "warning": warning,
        "asset_dir": str(row_dir),
    }

    if not resolved_url:
        payload["status"] = "unresolved"
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    response = fetch_url(resolved_url)
    if looks_like_pdf(response, response.url):
        pdf_path = row_dir / "paper.pdf"
        pdf_path.write_bytes(response.content)
        payload.update(
            {
                "status": "pdf_download",
                "resolved_url": response.url,
                "local_source": str(pdf_path),
            }
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    pdf_url = extract_pdf_link(response.text, response.url)
    if pdf_url:
        pdf_response = fetch_url(pdf_url)
        pdf_path = row_dir / "paper.pdf"
        pdf_path.write_bytes(pdf_response.content)
        payload.update(
            {
                "status": "pdf_download",
                "resolved_url": response.url,
                "pdf_url": pdf_response.url,
                "local_source": str(pdf_path),
            }
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    source_path = row_dir / "source.md"
    source_path.write_text(html_to_markdown(response.url, response.text), encoding="utf-8")
    payload.update(
        {
            "status": "web_preview",
            "resolved_url": response.url,
            "local_source": str(source_path),
        }
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
