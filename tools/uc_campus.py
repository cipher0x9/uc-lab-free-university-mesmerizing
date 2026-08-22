#!/usr/bin/env python3
"""Shared flagship-campus helpers for UC Lab Free University.

The public product is one offline HTML file. Generators and verify must
agree on how to find ``window.SECTIONS``, how to count it, and how to
update ``window.STATS.sections`` without rewriting curriculum bodies.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
FLAGSHIP = REPO_ROOT / "university" / "v17-UNIVERSITY.html"

# Public ship floor. Generators may add recovered holes; they must never
# thin the campus below this count.
MIN_SECTIONS = 632

STATS_SECTIONS_RE = re.compile(
    r'(window\.STATS\s*=\s*\{[^;]*?"sections"\s*:\s*)\d+',
    re.S,
)
STATS_OBJECT_RE = re.compile(r"window\.STATS\s*=\s*(\{.*?\})\s*;", re.S)
SECTIONS_ASSIGN_RE = re.compile(r"window\.SECTIONS\s*=\s*")

# Tags that would fetch bytes at parse/boot time (not clickable <a href>).
LOAD_TAG_RE = re.compile(
    r"<(?:link|script|img|iframe|source|video|audio|embed|object|track)\b[^>]*>",
    re.I,
)
LOAD_ATTR_RE = re.compile(
    r"""\b(?:href|src|data|poster|srcset)\s*=\s*["']([^"']+)["']""",
    re.I,
)
CSS_HTTP_URL_RE = re.compile(r"""url\(\s*["']?(https?:[^"')\s]+)""", re.I)
CSS_IMPORT_RE = re.compile(r"""@import\s+(?:url\()?["']?(https?:[^"')\s]+)""", re.I)
CDN_HINT_RE = re.compile(
    r"fonts\.googleapis|fonts\.gstatic|typekit\.net|use\.typekit|"
    r"cdn\.jsdelivr|unpkg\.com|cdnjs\.cloudflare|bootstrapcdn|"
    r"ajax\.googleapis|code\.jquery|polyfill\.io",
    re.I,
)
TRACK_HINT_RE = re.compile(
    r"google-analytics|googletagmanager|gtag\(|facebook\.net|"
    r"connect\.facebook|hotjar|mixpanel|segment\.com|plausible\.io|"
    r"pixel\.gif|doubleclick\.net|adservice",
    re.I,
)
NETWORK_API_RE = re.compile(
    r"\bfetch\s*\(|XMLHttpRequest|new\s+WebSocket|navigator\.sendBeacon|"
    r"importScripts\s*\(",
)

SHELL_HREF_ALLOW = (
    "https://github.com/cipher0x9",
    "https://github.com/cipher0x9/",
    "https://linktr.ee/cyphermonkey",
)


def locate_sections(text: str) -> tuple[int, int, list[dict[str, Any]]]:
    """Return ``(start, end, parsed)`` for the SECTIONS array.

    ``start`` is the index of ``[``. ``end`` is the index of the newline
    in the closing ``\\n];`` marker the generators rewrite against.
    """
    match = SECTIONS_ASSIGN_RE.search(text)
    if not match:
        raise RuntimeError("window.SECTIONS assignment not found")
    start = text.find("[", match.end())
    end = text.find("\n];", start)
    if start < 0 or end < 0:
        raise RuntimeError("SECTIONS array boundary not found")
    parsed = json.loads(text[start : end + 2])
    if not isinstance(parsed, list) or any(not isinstance(item, dict) for item in parsed):
        raise RuntimeError("SECTIONS must be a dense object list")
    return start, end, parsed


def section_spans(text: str, start: int, end: int) -> list[tuple[int, int, dict[str, Any]]]:
    """Return exact raw object spans without reserializing the full array."""
    decoder = json.JSONDecoder()
    spans: list[tuple[int, int, dict[str, Any]]] = []
    cursor = start + 1
    while cursor < end:
        while cursor < end and text[cursor] in " \t\r\n,":
            cursor += 1
        if cursor >= end:
            break
        value, finish = decoder.raw_decode(text, cursor)
        if not isinstance(value, dict):
            raise RuntimeError("non-object found in SECTIONS")
        spans.append((cursor, finish, value))
        cursor = finish
    return spans


def update_stats(text: str, section_count: int) -> str:
    updated, count = STATS_SECTIONS_RE.subn(
        rf"\g<1>{section_count}", text, count=1
    )
    if count != 1:
        raise RuntimeError("window.STATS.sections was not updated exactly once")
    return updated


def parse_stats(text: str) -> dict[str, Any]:
    match = STATS_OBJECT_RE.search(text)
    if not match:
        raise RuntimeError("window.STATS object not found")
    parsed = json.loads(match.group(1))
    if not isinstance(parsed, dict):
        raise RuntimeError("window.STATS is not an object")
    return parsed


def assert_not_thinned(before: int, after: int) -> None:
    if after < MIN_SECTIONS:
        raise RuntimeError(
            f"refusing to write a campus with {after} sections "
            f"(floor is {MIN_SECTIONS})"
        )
    if after < before:
        raise RuntimeError(
            f"refusing to shrink the campus from {before} to {after} sections"
        )


def _is_external_url(url: str) -> bool:
    value = url.strip()
    return value.startswith(("http://", "https://", "//"))


def asset_load_leaks(text: str) -> list[str]:
    """External URLs that would load at parse/boot — not clickable links."""
    leaks: list[str] = []
    for tag in LOAD_TAG_RE.findall(text):
        for url in LOAD_ATTR_RE.findall(tag):
            if _is_external_url(url):
                leaks.append(url)
    leaks.extend(CSS_HTTP_URL_RE.findall(text))
    leaks.extend(CSS_IMPORT_RE.findall(text))
    return leaks


def shell_http_hrefs(text: str) -> list[str]:
    """``<a href=http>`` in the HTML shell (before SECTIONS / after array)."""
    start, end, _ = locate_sections(text)
    shell = text[:start] + text[end + 2 :]
    return re.findall(r"""<a\b[^>]+href=["'](https?://[^"']+)["']""", shell, re.I)


def shell_href_allowed(url: str) -> bool:
    if url == SHELL_HREF_ALLOW[0] or url == SHELL_HREF_ALLOW[2]:
        return True
    return url.startswith(SHELL_HREF_ALLOW[1])


def extract_scripts(text: str) -> list[str]:
    return re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", text, re.DOTALL | re.I)
