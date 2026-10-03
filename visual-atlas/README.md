# UC Visual Atlas

Offline world map of voice technology. Open it from the repository root:

```
open visual-atlas/index.html
```

Or open `index.html` in any browser. Nothing is fetched at load. Educational links are ordinary anchors.

## What is here

- `index.html` — hub map, search, legend
- `families/` — 19 family pages, 28 step-through flows, 156 flip cards
- `matrices.html` — capability matrices, dated 2026-10-03
- `timeline.html` — 23 dated events with source links
- `glossary.html` — 195 terms
- `drills.html` — response codes, ports, codecs, DSCP, 3 am traps (56 cards)
- `assets/atlas.css`, `assets/atlas.js` — local theme, flow engine, drills
- `SOURCES.md` — fact ledger, including the 2026-10-03 box facts (E1–E5, W1–W6, T1–T6, F1–F6, S1–S8, M1–M3, P1–P8)
- `tools/check_atlas.py` — offline checker
- `tools/build_pages.py` — regenerates HTML from the catalogs

## Verify

```
python3 visual-atlas/tools/check_atlas.py
```

Exit 0 means file size, offline rules, internal links, reduced motion, print CSS, and inline script syntax all passed.

Synthetic addresses are RFC 5737 only (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24). Example domains are example.com and example.net.
