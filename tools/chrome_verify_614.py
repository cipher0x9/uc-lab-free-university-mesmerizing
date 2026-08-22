#!/usr/bin/env python3
"""Optional headless Chromium boot check for the flagship campus.

Not part of the default verify command (Playwright is optional).
Expects at least 632 unique sections and a matching STATS count.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "university" / "v17-UNIVERSITY.html"
MIN_SECTIONS = 632


def main() -> int:
    if not HTML.is_file():
        print(f"CHROME EXIT 1\nERROR: flagship not found: {HTML}")
        return 1
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("CHROME SKIP — Playwright is not installed (optional boot check)")
        return 0

    errors: list[str] = []
    page_errors: list[str] = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.on(
                "console",
                lambda msg: errors.append(f"{msg.type}: {msg.text}")
                if msg.type == "error"
                else None,
            )
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            page.goto(f"file://{HTML.resolve()}", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
            count = page.evaluate("window.SECTIONS ? window.SECTIONS.length : -1")
            stats = page.evaluate("window.STATS ? window.STATS.sections : -1")
            browser.close()
    except Exception as exc:
        print(f"CHROME EXIT 1\nERROR: {exc}")
        return 1

    all_errors = errors + page_errors
    print("CHROME EXIT 0")
    print(f"PAGE CONSOLE ERRORS {len(all_errors)}")
    print(f"WINDOW.SECTIONS LENGTH {count}")
    print(f"WINDOW.STATS.SECTIONS {stats}")
    for item in all_errors[:20]:
        print(f"  {item}")
    if all_errors or count < MIN_SECTIONS or stats != count:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
