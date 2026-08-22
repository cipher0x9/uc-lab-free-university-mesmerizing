#!/usr/bin/env python3
"""Verify the flagship offline campus.

Checks the real file on disk:

- section count (floor 632) and unique IDs
- STATS.sections matches the parsed array
- no empty / hole objects
- no double-comma holes in the SECTIONS array
- no CDN / external font / script / image loads
- no tracking pixels or browser network APIs
- each inline <script> parses with ``node -c``

Educational ``<a href="https://...">`` links inside section bodies and
``window.UC_RESOURCES`` are allowed — they do not load at boot.

Usage:
    python3 tools/verify_campus.py
    python3 tools/verify_campus.py --html university/v17-UNIVERSITY.html
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from uc_campus import (  # noqa: E402
    CDN_HINT_RE,
    FLAGSHIP,
    MIN_SECTIONS,
    NETWORK_API_RE,
    TRACK_HINT_RE,
    asset_load_leaks,
    extract_scripts,
    locate_sections,
    parse_stats,
    shell_href_allowed,
    shell_http_hrefs,
)


def check_js_syntax(scripts: list[str]) -> list[str]:
    if not scripts:
        return ["no <script> blocks found"]
    errors: list[str] = []
    for index, source in enumerate(scripts):
        try:
            result = subprocess.run(
                ["node", "--check"],
                input=source,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except FileNotFoundError:
            return ["node is not installed — JS syntax check requires Node.js"]
        except subprocess.TimeoutExpired:
            errors.append(f"script[{index}]: node --check timed out")
            continue
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "unknown parse error").strip()
            errors.append(f"script[{index}]: {detail[:400]}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=FLAGSHIP)
    args = parser.parse_args()
    path = args.html.resolve()
    if not path.is_file():
        print(f"FAIL  flagship not found: {path}")
        return 1

    text = path.read_text(encoding="utf-8")
    size = path.stat().st_size
    failed = False
    lines: list[str] = [
        "UC Lab Free University — campus verify",
        f"file     {path}",
        f"bytes    {size}",
    ]

    try:
        start, end, sections = locate_sections(text)
        stats = parse_stats(text)
    except Exception as exc:
        print("\n".join(lines))
        print(f"FAIL  parse: {exc}")
        return 1

    ids = [str(section.get("id", "") or "") for section in sections]
    holes = sum(
        1
        for section, section_id in zip(sections, ids)
        if not section_id or not section.get("title") or not section.get("body")
    )
    dupes = sorted(key for key, count in Counter(ids).items() if count > 1)
    array_region = text[start : end + 2]
    double_commas = array_region.count(",,")
    stats_count = stats.get("sections")
    version = stats.get("version", "")

    lines.append(f"version  {version}")
    lines.append(f"stats    {stats_count}")
    lines.append(f"sections {len(sections)}")
    lines.append(f"unique   {len(set(ids))}")
    lines.append(f"holes    {holes}")
    lines.append(f"dupes    {len(dupes)}")
    lines.append(f"commas   {double_commas}")

    if len(sections) < MIN_SECTIONS:
        failed = True
        lines.append(f"FAIL  section count {len(sections)} is below floor {MIN_SECTIONS}")
    else:
        lines.append(f"PASS  section count {len(sections)} (floor {MIN_SECTIONS})")

    if stats_count != len(sections):
        failed = True
        lines.append(
            f"FAIL  STATS.sections={stats_count} does not match array length {len(sections)}"
        )
    else:
        lines.append("PASS  STATS.sections matches array length")

    if len(set(ids)) != len(sections) or dupes:
        failed = True
        lines.append(f"FAIL  duplicate section ids: {dupes[:12]}")
    else:
        lines.append("PASS  every section id is unique")

    if holes:
        failed = True
        lines.append(f"FAIL  {holes} section hole(s) (missing id/title/body)")
    else:
        lines.append("PASS  no empty section holes")

    if double_commas:
        failed = True
        lines.append(f"FAIL  {double_commas} double-comma hole(s) in SECTIONS")
    else:
        lines.append("PASS  no double-comma holes in SECTIONS")

    leaks = asset_load_leaks(text)
    if leaks:
        failed = True
        lines.append(f"FAIL  external asset loads: {leaks[:8]}")
    else:
        lines.append("PASS  no CDN / external font / script / image loads")

    cdn_hits = CDN_HINT_RE.findall(text)
    if cdn_hits:
        failed = True
        lines.append(f"FAIL  CDN host tokens in flagship: {sorted(set(cdn_hits))[:8]}")
    else:
        lines.append("PASS  no CDN host tokens")

    track_hits = TRACK_HINT_RE.findall(text)
    if track_hits:
        failed = True
        lines.append(f"FAIL  tracking tokens: {sorted(set(track_hits))[:8]}")
    else:
        lines.append("PASS  no tracking pixels / analytics beacons")

    net_hits = NETWORK_API_RE.findall(text)
    if net_hits:
        failed = True
        lines.append(f"FAIL  browser network APIs: {sorted(set(net_hits))[:8]}")
    else:
        lines.append("PASS  no fetch / XHR / WebSocket / sendBeacon")

    shell_hrefs = shell_http_hrefs(text)
    bad_shell = [url for url in shell_hrefs if not shell_href_allowed(url)]
    lines.append(f"shell   {len(shell_hrefs)} outbound <a href> (github/linktr allow-list)")
    if bad_shell:
        failed = True
        lines.append(f"FAIL  unexpected shell hrefs: {bad_shell}")
    else:
        lines.append("PASS  shell outbound hrefs are maintainer/share links only")

    js_errors = check_js_syntax(extract_scripts(text))
    if js_errors:
        failed = True
        lines.append("FAIL  JS syntax")
        lines.extend(f"       {item}" for item in js_errors[:8])
    else:
        lines.append(f"PASS  JS syntax ({len(extract_scripts(text))} inline scripts, node --check)")

    lines.append("RESULT  " + ("FAIL" if failed else "PASS"))
    print("\n".join(lines))
    return 1 if failed else 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    sys.exit(main())
