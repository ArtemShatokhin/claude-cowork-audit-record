#!/usr/bin/env python3
"""Re-check the Cowork audit and approval record against Anthropic's own page.

Kortix is open source. This script keeps one page honest: the Claude Help
Center article on Cowork for Team and Enterprise plans. Every sentence in
sources.json is a quote the record in README.md depends on. The script
fetches the page, normalises whitespace and typographic quotes, and reports
each quote as found or missing.

    python3 check.py                # fetch the live page
    python3 check.py --file cw.html # check a saved copy (offline)
    python3 check.py --json         # machine-readable output

Exit code is 0 when every quote is present, 1 when any is missing. A missing
quote is the signal: the record below it needs a new date and a new reading.
Standard library only.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAG = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
TAGS = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")
TYPO = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u00a0": " "}


def normalise(text: str) -> str:
    for bad, good in TYPO.items():
        text = text.replace(bad, good)
    return WS.sub(" ", text).strip()


def page_text(raw: str) -> str:
    if "<" in raw and ">" in raw:
        raw = TAG.sub(" ", raw)
        raw = TAGS.sub(" ", raw)
        raw = html.unescape(raw)
    return normalise(raw)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "audit-record-check/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", help="check a saved HTML/text copy instead of fetching")
    ap.add_argument("--sources", default=str(HERE / "sources.json"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    spec = json.loads(Path(a.sources).read_text(encoding="utf-8"))
    raw = Path(a.file).read_text(encoding="utf-8", errors="replace") if a.file else fetch(spec["page"])
    haystack = page_text(raw)

    rows, missing = [], 0
    for q in spec["quotes"]:
        ok = normalise(q["quote"]) in haystack
        missing += 0 if ok else 1
        rows.append({"id": q["id"], "found": ok, "quote": q["quote"]})

    if a.json:
        print(json.dumps({"page": spec["page"], "checked": spec["checked"],
                          "missing": missing, "quotes": rows}, indent=2))
    else:
        print(f"page: {spec['page']}")
        print(f"record dated: {spec['checked']}")
        print(f"quotes checked: {len(rows)}  missing: {missing}\n")
        for r in rows:
            print(f"  [{'ok' if r['found'] else 'MISSING'}] {r['id']}")
            if not r["found"]:
                print(f"      {r['quote']}")
        if missing:
            print("\nA missing quote means the record is stale: re-read the page, "
                  "update README.md and bump `checked` in sources.json.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
