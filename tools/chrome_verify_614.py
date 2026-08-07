#!/usr/bin/env python3
"""Headless Chrome boot check for v17-UNIVERSITY.html."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path('/Users/cypher0x9/Documents/01_🎓_UC_AI_FREE_UNIVERSITY_CAMPUS/_github-publish/university/v17-UNIVERSITY.html').resolve()
REPORT = Path('/Users/cypher0x9/Desktop/uc-w5-kimi-content-report.md')

def now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).astimezone().isoformat()

def append_report(line):
    with open(REPORT, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def main():
    errors = []
    page_errors = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on('console', lambda msg: errors.append(f'{msg.type}: {msg.text}') if msg.type == 'error' else None)
            page.on('pageerror', lambda exc: page_errors.append(str(exc)))
            page.goto(f'file://{HTML}', wait_until='networkidle', timeout=30000)
            # Wait a bit for any deferred JS
            page.wait_for_timeout(2000)
            # Verify SECTIONS loaded
            count = page.evaluate('window.SECTIONS ? window.SECTIONS.length : -1')
            stats = page.evaluate('window.STATS ? window.STATS.sections : -1')
            browser.close()
    except Exception as e:
        print(f'CHROME EXIT 1\nERROR: {e}')
        append_report(f'CHROME EXIT 1\nERROR: {e}')
        sys.exit(1)

    all_errors = errors + page_errors
    print(f'CHROME EXIT 0')
    print(f'PAGE CONSOLE ERRORS {len(all_errors)}')
    print(f'WINDOW.SECTIONS LENGTH {count}')
    print(f'WINDOW.STATS.SECTIONS {stats}')
    if all_errors:
        for e in all_errors[:20]:
            print(f'  {e}')

    append_report(f'CHROME EXIT 0')
    append_report(f'PAGE CONSOLE ERRORS {len(all_errors)}')
    append_report(f'WINDOW.SECTIONS LENGTH {count}')
    append_report(f'WINDOW.STATS.SECTIONS {stats}')

    if all_errors or count != 614 or stats != 614:
        sys.exit(1)

if __name__ == '__main__':
    main()
