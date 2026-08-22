#!/usr/bin/env python3
"""Splice the per-section visual chrome pack into the flagship HTML.

Does not rewrite window.SECTIONS bodies. Injects a shared generator that
stamps flow + protocol/port chips at render time.
"""

from __future__ import annotations

from pathlib import Path

from uc_campus import FLAGSHIP
from uc_section_visuals import lexicon_json

BEGIN = "<!-- ===== UC SECTION VISUAL PACK ===== -->"
END = "<!-- ===== /UC SECTION VISUAL PACK ===== -->"
PACK = Path(__file__).resolve().parent / "section_visual_pack.inc.html"


def splice(html: str, pack: str) -> str:
    if BEGIN in html:
        start = html.find(BEGIN)
        stop = html.find(END)
        if start < 0 or stop < 0 or stop < start:
            raise RuntimeError("section visual pack markers are unbalanced")
        stop += len(END)
        return html[:start] + pack.strip() + html[stop:]
    idx = html.rfind("</body>")
    if idx < 0:
        raise RuntimeError("flagship has no closing body tag")
    return html[:idx] + pack.strip() + "\n" + html[idx:]


def compose_pack() -> str:
    raw = PACK.read_text(encoding="utf-8").strip()
    if not raw.startswith(BEGIN) or not raw.endswith(END):
        raise RuntimeError("pack file must start/end with section visual markers")
    token = "var LEX = window.__UC_SECTION_VISUAL_LEXICON__;"
    if token not in raw:
        raise RuntimeError("pack is missing the lexicon placeholder")
    lex = lexicon_json()
    if "</script>" in lex:
        raise RuntimeError("lexicon JSON would break the script tag")
    return raw.replace(token, "var LEX = " + lex + ";", 1)


def main() -> None:
    pack = compose_pack()
    original = FLAGSHIP.read_text(encoding="utf-8")
    updated = splice(original, pack + "\n")
    if updated == original:
        print(f"unchanged {FLAGSHIP} ({len(original.encode('utf-8'))} bytes)")
        return
    FLAGSHIP.write_text(updated, encoding="utf-8")
    print(
        f"wrote {FLAGSHIP} "
        f"{len(original.encode('utf-8'))} -> {len(updated.encode('utf-8'))} bytes"
    )


if __name__ == "__main__":
    main()
