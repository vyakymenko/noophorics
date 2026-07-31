#!/usr/bin/env python3
"""Every count this repository states about itself, checked against the source.

A programme whose pitch is that its numbers are auditable cannot afford a stated
count that disagrees with the file behind it -- and it had one for days: README
advertised 46 tests while the suite defined 86. Nobody noticed by reading,
because a number in prose reads as true.

    python3 tools/check_counts.py        # exits non-zero on any mismatch
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as fh:
        return fh.read()


def truth() -> dict:
    docs = os.path.join(ROOT, "docs")
    journal = os.path.join(docs, "journal")
    return {
        "tests": len(re.findall(r"def test_", _read("metrics/tests/test_metrics.py"))),
        "laws": len(re.findall(r"^## L\d", _read("theory/laws.md"), re.M)),
        "open problems": len(re.findall(r"^## \d+\.", _read("theory/open-problems.md"), re.M)),
        "languages": len([d for d in os.listdir(docs)
                          if len(d) == 2 and os.path.isdir(os.path.join(docs, d))]),
        "axioms": len(re.findall(r"^\*\*A\d", _read("PRINCIPIA.md"), re.M)),
        "retractions": len(re.findall(r"^\| \d+ \|", _read("RETRACTIONS.md"), re.M)),
        "journal entries": len([d for d in os.listdir(journal)
                                if os.path.isdir(os.path.join(journal, d))]),
    }


# (file, regex capturing the number, which truth key it must equal)
CLAIMS = [
    ("README.md", r"test_metrics\.py\s+#\s+(\d+) tests", "tests"),
    ("docs/index.html", r"<dt>Conjectural laws</dt><dd>(\d+)", "laws"),
    ("docs/index.html", r"<dt>Open problems</dt><dd>(\d+)", "open problems"),
    ("docs/index.html", r"<dt>Own claims refuted</dt><dd><a[^>]*>(\d+)", "retractions"),
    # Added after the launch audit found README and CITATION advertising ten
    # open problems against twelve in the file. Prose numerals count: "ten" is a
    # claim exactly as much as "10" is, and greps for digits miss them.
    ("README.md", r"(twelve|eleven|ten|nine) open problems", "open problems"),
    ("CITATION.cff", r"(twelve|eleven|ten|nine) open problems", "open problems"),
]

WORDS = {"nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13}


def main() -> int:
    t = truth()
    print("ground truth")
    for k, v in sorted(t.items()):
        print("  %-16s %d" % (k, v))
    print("\nstated counts")
    bad = 0
    for rel, pattern, key in CLAIMS:
        text = _read(rel)
        m = re.search(pattern, text)
        if not m:
            print("  %-22s %-16s PATTERN NOT FOUND -- the claim moved or went" % (rel, key))
            bad += 1
            continue
        raw = m.group(1)
        stated = WORDS.get(raw, None) if not raw.isdigit() else int(raw)
        if stated is None:
            print("  %-22s %-16s unrecognised numeral %r" % (rel, key, raw))
            bad += 1
            continue
        ok = stated == t[key]
        print("  %-22s %-16s states %-4d actual %-4d %s"
              % (rel, key, stated, t[key], "ok" if ok else "MISMATCH"))
        bad += 0 if ok else 1
    if bad:
        print("\n%d mismatch(es). A stated count that disagrees with its source is "
              "the first thing a hostile reader finds." % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
