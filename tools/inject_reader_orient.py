#!/usr/bin/env python3
"""Idempotently splice the reader-orientation pack into the flagship HTML.

Does not rewrite window.SECTIONS bodies. Inserts chrome (CSS+JS) before </body>.
"""

from __future__ import annotations

from pathlib import Path

from uc_campus import FLAGSHIP

BEGIN = "<!-- ===== UC READER ORIENTATION PACK ===== -->"
END = "<!-- ===== /UC READER ORIENTATION PACK ===== -->"
PACK = Path(__file__).resolve().parent / "reader_orient_pack.inc.html"


def splice(html: str, pack: str) -> str:
    if BEGIN in html:
        start = html.find(BEGIN)
        stop = html.find(END)
        if start < 0 or stop < 0 or stop < start:
            raise RuntimeError("orientation pack markers are unbalanced")
        stop += len(END)
        return html[:start] + pack.strip() + html[stop:]
    idx = html.rfind("</body>")
    if idx < 0:
        raise RuntimeError("flagship has no closing body tag")
    return html[:idx] + pack.strip() + "\n" + html[idx:]


def main() -> None:
    pack = PACK.read_text(encoding="utf-8").strip()
    if not pack.startswith(BEGIN) or not pack.endswith(END):
        raise RuntimeError("pack file must start/end with the orientation markers")
    if "</script>" in pack.split("<script>", 1)[-1].rsplit("</script>", 1)[0]:
        # inner script must not contain a raw closing tag
        inner = pack.split("<script>", 1)[1].rsplit("</script>", 1)[0]
        if "</script>" in inner:
            raise RuntimeError("pack JS contains a raw </script> that would truncate the campus")
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
