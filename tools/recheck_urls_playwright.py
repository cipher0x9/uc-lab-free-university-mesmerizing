#!/usr/bin/env python3
"""Re-check bot-blocked seed URLs with a real headless Chromium (Wave E).

curl gets TLS-fingerprint 403s from Akamai-fronted doc portals (cisco.com,
fcc.gov, ...). A real browser answers the honest question: does the page load?
Updates tools/.uc_resources_urlcache.json in place.
"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / 'tools/.uc_resources_urlcache.json'

def main():
    cache = json.loads(CACHE.read_text())
    todo = [u for u, c in cache.items() if not (c[:1] in '23' or c.endswith('*'))]
    print(f'rechecking {len(todo)} URLs with Chromium')
    ok = fail = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for url in todo:
            try:
                resp = page.goto(url, wait_until='domcontentloaded', timeout=20000)
                code = str(resp.status) if resp else '000'
                # let redirects settle; final URL noted for the audit
                final = page.url
                if code[:1] in '23':
                    cache[url] = code + 'B'  # B = browser-verified
                    ok += 1
                    note = '' if final == url else f' -> {final}'
                    print(f'  OK  [{code}] {url}{note}')
                else:
                    cache[url] = code
                    fail += 1
                    print(f'  BAD [{code}] {url}')
            except Exception as e:
                cache[url] = '000'
                fail += 1
                print(f'  BAD [ERR] {url} :: {str(e)[:80]}')
        browser.close()
    CACHE.write_text(json.dumps(cache, indent=0))
    print(f'browser recheck: {ok} ok, {fail} still failing')

if __name__ == '__main__':
    main()
