#!/usr/bin/env python3
"""Verification suite for v17-UNIVERSITY.html after 614-section expansion."""
import json, re, subprocess, sys
from pathlib import Path

HTML = Path('/Users/cypher0x9/Documents/01_🎓_UC_AI_FREE_UNIVERSITY_CAMPUS/_github-publish/university/v17-UNIVERSITY.html')
REPORT = Path('/Users/cypher0x9/Desktop/uc-w5-kimi-content-report.md')

def now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).astimezone().isoformat()

def append_report(line):
    with open(REPORT, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def js_compile_check(text):
    """Extract JS blocks and compile with node."""
    # The script tag contents after window.SECTIONS and inline scripts
    scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
    errors = []
    for i, src in enumerate(scripts):
        # Don't try to compile huge SECTIONS array directly through vm if it has HTML strings?
        # Actually node -c can parse JS. We'll wrap in a file.
        try:
            result = subprocess.run(
                ['node', '-c', '-'],
                input=src,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                errors.append(f'Script {i}: {result.stderr.strip()[:200]}')
        except Exception as e:
            errors.append(f'Script {i}: {e}')
    return errors

def html_balance_check(text):
    """Quick stack-based HTML tag balance check for major structural tags."""
    # Remove script/style content to avoid false positives
    stripped = re.sub(r'<script>.*?</script>', '', text, flags=re.DOTALL)
    stripped = re.sub(r'<style>.*?</style>', '', stripped, flags=re.DOTALL)
    stripped = re.sub(r'<!--.*?-->', '', stripped, flags=re.DOTALL)
    # Self-closing tags
    self_closing = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    tag_re = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)[^>]*?>')
    stack = []
    unclosed = 0
    mismatch = 0
    for close, tag in tag_re.findall(stripped):
        if tag in self_closing:
            continue
        if close:
            if stack and stack[-1] == tag:
                stack.pop()
            else:
                mismatch += 1
        else:
            stack.append(tag)
    unclosed = len(stack)
    return unclosed, mismatch

def cdn_check(text):
    # Count external CDN references
    cdn_patterns = [
        r'https?://[^"\'\s]+\.cloudflare\.com',
        r'https?://[^"\'\s]+\.googleapis\.com',
        r'https?://[^"\'\s]+\.bootstrapcdn\.com',
        r'https?://[^"\'\s]+\.jsdelivr\.net',
        r'https?://[^"\'\s]+\.unpkg\.com',
        r'https?://cdn\.[^"\'\s]+',
    ]
    count = 0
    for pat in cdn_patterns:
        count += len(re.findall(pat, text, re.IGNORECASE))
    return count

def double_comma_check(text):
    # Find ',,' in the SECTIONS array region
    return text.count(',,')

def sections_check(text):
    match = re.search(r'window\.SECTIONS\s*=\s*(\[.*?\]);', text, re.DOTALL)
    if not match:
        return -1, -1
    arr = json.loads(match.group(1))
    expected = 614
    holes = sum(1 for s in arr if not isinstance(s, dict) or not s.get('id'))
    return len(arr), holes

def main():
    text = HTML.read_text(encoding='utf-8')
    results = []
    results.append('=== JS VM compile ===')
    js_errors = js_compile_check(text)
    results.append('ALL JS OK' if not js_errors else '\n'.join(js_errors))

    unclosed, mismatch = html_balance_check(text)
    results.append('=== HTML parser ===')
    results.append(f'UNCLOSED {unclosed} MISMATCH {mismatch}')

    cdn = cdn_check(text)
    dc = double_comma_check(text)
    results.append('=== CDN/double-comma ===')
    results.append(f'CDN {cdn}')
    results.append(f'DOUBLECOMMAS        {dc}')

    count, holes = sections_check(text)
    results.append('=== Sections array ===')
    results.append(f'SECTIONS {count} HOLES {holes}')

    stats_match = re.search(r'window\.STATS\s*=\s*(\{[^}]+\});', text)
    results.append('=== STATS ===')
    results.append(f'STATS {stats_match.group(1) if stats_match else "NOT FOUND"}')

    print('\n'.join(results))

    # Chrome check is handled separately; placeholder
    results.append('=== Chrome headless ===')
    results.append('CHROME EXIT TBD')
    results.append('PAGE CONSOLE ERRORS TBD')

    append_report('\n--- VERIFICATION — {} ---'.format(now()))
    for r in results:
        append_report(r)

    # Return non-zero if any check fails (except TBD)
    if js_errors or unclosed or mismatch or cdn or dc or count != 614 or holes:
        sys.exit(1)

if __name__ == '__main__':
    main()
