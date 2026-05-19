from __future__ import annotations

import re
from urllib.parse import quote_plus

import requests


USER_AGENT = "Mozilla/5.0 (compatible; literature-table-organizer/3.0)"
REQUEST_TIMEOUT = 30


def token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def title_similarity(a: str, b: str) -> float:
    tokens_a = token_set(a)
    tokens_b = token_set(b)
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / max(len(tokens_a), len(tokens_b))


def search_crossref(title: str) -> list[dict[str, object]]:
    response = requests.get(
        "https://api.crossref.org/works",
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
        params={"query.title": title, "rows": 5},
    )
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])
    candidates: list[dict[str, object]] = []
    for item in items:
        title_list = item.get("title") or []
        link = item.get("URL")
        if not title_list or not link:
            continue
        score = title_similarity(title, title_list[0])
        candidates.append(
            {
                "url": link,
                "label": "crossref",
                "matched_title": title_list[0],
                "title_match_score": score,
            }
        )
    return candidates


def fallback_duckduckgo(title: str) -> list[dict[str, object]]:
    query = quote_plus(f'{title} pdf OR openreview OR github OR project OR paper')
    return [
        {
            "url": f"https://duckduckgo.com/html/?q={query}",
            "label": "duckduckgo_html_search",
            "matched_title": "",
            "title_match_score": 0.0,
        }
    ]


def find_paper_link(title: str) -> dict[str, object]:
    candidates = search_crossref(title)
    candidates.sort(key=lambda item: float(item["title_match_score"]), reverse=True)
    if not candidates:
        candidates = fallback_duckduckgo(title)
    recommended = candidates[0] if candidates else None
    return {
        "title": title,
        "candidates": candidates,
        "recommended_url": recommended["url"] if recommended else None,
        "recommended_reason": recommended["label"] if recommended else "no_candidate",
        "needs_manual_check": not recommended or float(recommended.get("title_match_score", 0.0)) < 0.65,
    }
