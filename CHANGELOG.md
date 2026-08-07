# Changelog

## [2026-08-06] — Wave E: resources + public polish (local → pending push)

- **Official Resources drawer**: chapter hubs (13 `hub-*` sections) and matching curriculum groups now show a curated card of real, verified official docs (Cisco, Microsoft Learn, AWS, Google Cloud, Twilio, IETF/RFC-Editor, W3C, IANA, FCC)
- New `window.UC_RESOURCES` registry (63 unique verified URLs, deduped, reused across sections — inlined in the flagship HTML so the "one file, offline" promise holds; source also kept at `university/resources-registry.js` for maintainers)
- Every URL was fetched and confirmed live before inclusion — no invented links, no fake `example.com` placeholders
- Static outbound `http(s)` href count in the HTML shell stays at **4** (github/linktr) — resource links render dynamically per-section, so the campus still boots with zero network calls
- Docs synced: DOWNLOADS.md/HOW-TO-GET.md stale 252-section figures corrected to **631 / v20.1-UI / ~15 MB**; README/START-HERE updated to mention the Resources drawer
- Verified: 0 holes, 0 CDN, all 631 sections open cleanly under Playwright with zero JS errors, mobile 390px has zero horizontal scroll, reduced-motion respected

## [2026-08-06] — v20.1-UI (local → pending push)

- **631 sections** campus (public badges were stale at 252/240)
- Wave C content: 13 chapter hubs, 8 inline SVG flows, 4 LICC banks (80 Qs), migration enrichments
- Wave D UI: hash deep-links, scroll-margin, chapter rail, lively CSS + reduced-motion, self-heal boot, a11y menus
- Verified: 0 holes, 0 CDN, Playwright boot clean, `#hub-cucm` deep-link OK
- Docs badges/counts synced; release zip refresh scheduled post-push

All notable public improvements to **UC Lab Free University** are recorded here.

## [2026-08-06] — God-mode public polish

- Fixed curriculum index links (relative paths; removed local file:// URLs)
- Corrected section badge to 240 (aligned with campus HTML)
- Pure MIT LICENSE for GitHub license detection + NOTICE.md
- Expanded curriculum: Teams Phone, Expressway/MRA, recording/WFO, media/codecs, home lab, LICC workbook, multi-vendor interop, presence/IM
- Added FAQ, CHANGELOG, CITATION.cff, Code of Conduct, issue/PR templates
- Sibling matrix includes AI Lab + Ardham Shastra

## [2026-08-05] — Curriculum depth packs

- Added dense technical curriculum markdown packs
- Sibling cross-links and brand consistency

## [2026-08-01] — Mobile-friendly campus release

- Browser-first HTML campus + release zips
- Offline open path documented for phone and desktop
