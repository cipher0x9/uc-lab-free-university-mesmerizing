# Maintainer tools

The public product is still **one offline HTML file**: `university/v17-UNIVERSITY.html`.
These scripts keep that file countable, offline-valid, and regenerable. They do
not invent curriculum.

## Verify (required after campus edits)

```bash
python3 tools/verify_campus.py
# or
make verify
```

The command fails unless all of the following hold:

- parsed `window.SECTIONS` length is at least **632**
- every section has a unique `id` plus `title` and `body`
- `window.STATS.sections` matches the array length
- no `,,` holes in the SECTIONS array
- no CDN / external font / script / image loads
- no tracking pixels or `fetch` / XHR / WebSocket / `sendBeacon`
- every inline `<script>` parses with `node --check`

Clickable official-doc `<a href>` links inside section bodies and
`window.UC_RESOURCES` are allowed. They do not load at boot.

`tools/verify_614.py` is a compatibility wrapper for the same command.
`tools/chrome_verify_614.py` is an optional Playwright boot check.

## Regenerate (additive only)

Generators are idempotent. They append missing IDs and refuse to thin the
campus below 632 sections.

```bash
# Practice banks (28 topics). Dry-run first.
python3 uc_qbank_gen.py --dry-run
python3 uc_qbank_gen.py

# Wave-1 vendor / migration / SEV / mastery packs.
python3 uc_supernova_gen.py vendor --dry-run
python3 uc_supernova_gen.py vendor
python3 uc_supernova_gen.py migration
python3 uc_supernova_gen.py sev
python3 uc_supernova_gen.py mastery
```

Shared parse / STATS helpers live in `tools/uc_campus.py`.

## Reader orientation chrome (no curriculum rewrite)

First-run nest map, Start-here rail, hub flow SVGs, and compact sidebar live in
`tools/reader_orient_pack.inc.html`. They are spliced into the flagship **after**
`window.SECTIONS` (render-time chrome). Re-apply without touching section bodies:

```bash
python3 tools/inject_reader_orient.py
python3 tools/inject_section_visuals.py
make verify
```

Per-section flows, icons, and honest port/protocol chips are generated at
render time from `tools/uc_section_visuals.py` (shared lexicon) and
`tools/section_visual_pack.inc.html`. Every section gets chrome; no section
body is rewritten.

## Historical / optional

| Script | Role |
|--------|------|
| `apply_614_expansion.py` | Frozen Wave-19.1 expander. Refuses to write on the 632 campus. |
| `build_uc_resources.py` | Rebuild / re-verify the Official Resources drawer. |
| `recheck_urls_playwright.py` | Browser-recheck vendor URLs (needs Playwright). |
| `university/resources-registry.js` | Maintainer source for the inlined `window.UC_RESOURCES` block. |

Do not point these scripts at a laptop-absolute path. They resolve the repo
from `__file__`.
