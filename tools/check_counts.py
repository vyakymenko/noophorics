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


def _count_voids() -> int:
    """Experiments carrying a VOID.md. Zero, not a crash, when there are none.

    A counter that raises instead of reporting has turned an audit into an
    outage -- the same failure the link checker had when a path straddled a
    symlink. os.listdir on a missing directory is the easy way to get there.
    """
    base = os.path.join(ROOT, "experiments")
    if not os.path.isdir(base):
        return 0
    return len([d for d in os.listdir(base)
                if os.path.exists(os.path.join(base, d, "VOID.md"))])


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
        # A void is an experiment with a VOID.md, not a run that was thrown
        # away. The site said "three experiments are void" while two directories
        # carried the file -- the third was E-001's first live run, which was
        # voided and then re-run to completion. A voided run is not a voided
        # experiment and the sentence conflated them.
        "voids": _count_voids(),
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
    ("README.md", r"(fifteen|fourteen|thirteen|twelve|eleven|ten|nine) open problems", "open problems"),
    ("CITATION.cff", r"(fifteen|fourteen|thirteen|twelve|eleven|ten|nine) open problems", "open problems"),
    # The site says the count twice: once in the stat card above, once in prose
    # in the standing section. Only the card was checked, and the prose sat at
    # "ten open problems" against twelve in the file for as long as anyone had
    # been reading it. A number is a claim wherever it appears.
    ("docs/index.html", r"(fifteen|fourteen|thirteen|twelve|eleven|ten|nine) open problems", "open problems"),
    ("docs/index.html", r"(two|three|four|five) experiments are void", "voids"),
    # RETRACTIONS.md opens by saying "a count nobody can audit is worse than no
    # count" and then carried an unaudited one: its standing tally still said
    # three experiments void after E-001c's VOID.md landed, and still said zero
    # findings established months after E-002c. The void half is checkable and
    # is checked here. The findings half is not -- an experiment with a
    # FINDINGS.md and no VOID.md is not the same thing as an established
    # result, and a counter that got that wrong would be worse than none.
    ("RETRACTIONS.md", r"(two|three|four|five) experiments void", "voids"),
    # The retraction count is on the front page twice: as a stat card, which was
    # checked, and in the status sentence, which was not. The void count had the
    # same shape and the same fix. A number is a claim wherever it appears, and
    # this sentence is the one carried into nineteen translations -- so an
    # unchecked numeral here goes wrong in twenty places at once.
    ("docs/index.html", r"(Seventeen|Sixteen|Fifteen|Fourteen|Thirteen|Twelve|Eleven|Ten|Nine) of our own claims are withdrawn",
     "retractions"),
]

# The alternation in CLAIMS above must list every word in here, or a
# correct new count reads as PATTERN NOT FOUND. That is the check
# behaving properly -- a claim it can no longer find is a claim it can no
# longer guard -- but the two lists have to be extended together.
WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "nine": 9, "ten": 10,
         "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
         "fifteen": 15, "sixteen": 16,
         "seventeen": 17}


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
        # Lowercased before lookup: a prose numeral that opens a sentence is
        # capitalised, and "Eleven" against a lowercase table read as an
        # unrecognised numeral rather than as the count it plainly is.
        stated = WORDS.get(raw.lower(), None) if not raw.isdigit() else int(raw)
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
