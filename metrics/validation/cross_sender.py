#!/usr/bin/env python3
"""Reproduce the cross-sender disagreement observation from committed data.

journal/2026-07-30-cross-sender-disagreement.md reports that two senders from
different providers disagree on exactly the probes where one of them is wrong,
with no answer key used to produce the disagreement list.

That claim is only worth as much as its reproducibility, so this script
recomputes it from the repository -- including recovering E-001's cache from git
history, since it was deleted from the working tree.

    python3 metrics/validation/cross_sender.py
"""

from __future__ import annotations

import collections
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "metrics"))

from noophorics import load_probe_measure  # noqa: E402

E001_CACHE_REV = "0345350:experiments/E-001-fluency-cost/.sample-cache.json"
E001B_CACHE = "experiments/E-001b-fluency-factorial/sample-cache.json"


def mode(draws):
    return collections.Counter(draws).most_common(1)[0][0]


def main() -> int:
    measure = load_probe_measure(
        os.path.join(REPO, "experiments", "E-001-fluency-cost", "probes.json"))

    # Prefer the in-tree file. It was missing when this script was written --
    # see journal/2026-07-30-two-audit-holes.md -- and the git fallback is kept
    # so the script still reproduces on a checkout predating the restoration.
    in_tree = os.path.join(REPO, "experiments", "E-001-fluency-cost",
                           "sample-cache.json")
    if os.path.exists(in_tree):
        with open(in_tree, "r", encoding="utf-8") as fh:
            recovered = json.load(fh)
    else:
        try:
            blob = subprocess.check_output(["git", "show", E001_CACHE_REV],
                                           cwd=REPO, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("could not recover %s -- history rewritten?" % E001_CACHE_REV,
                  file=sys.stderr)
            return 2
        recovered = json.loads(blob)
    a_key = next(k for k in recovered if k.startswith("sender"))
    a = recovered[a_key]

    with open(os.path.join(REPO, E001B_CACHE), "r", encoding="utf-8") as fh:
        b = json.load(fh)["sender@gpt-oss:120b"]

    common = [p for p in measure if p.id in a and p.id in b]
    disagree = [p.id for p in common if mode(a[p.id]) != mode(b[p.id])]
    errs_a = [p.id for p in common if mode(a[p.id]) != p.key]
    errs_b = [p.id for p in common if mode(b[p.id]) != p.key]
    union = set(errs_a) | set(errs_b)
    hit = set(disagree) & union

    print("probes answered by both senders : %d of %d" % (len(common), len(measure)))
    print("%-32s: %s" % (a_key.split("/")[0], errs_a))
    print("%-32s: %s" % ("gpt-oss:120b errors vs key", errs_b))
    print("%-32s: %s" % ("cross-sender disagreement", disagree))
    print()
    print("recall    : %d/%d errors flagged" % (len(hit), len(union)))
    print("precision : %d/%d flags are real errors" % (len(hit), max(1, len(disagree))))
    print("false pos : %s" % (sorted(set(disagree) - union) or "none"))
    if disagree and len(hit) == len(disagree) == len(union):
        p = 1.0 / math.comb(len(common), len(disagree))
        print("\nunder random placement of %d flags among %d probes: p = %.2e"
              % (len(disagree), len(common), p))

    # The self-consistency half: why the assigned angle died.
    mass = [collections.Counter(a[p.id]).most_common(1)[0][1] / len(a[p.id])
            for p in common]
    print("\nsender modal mass: min %.4f  mean %.4f  -- variance %.2e"
          % (min(mass), sum(mass) / len(mass),
             sum((x - sum(mass) / len(mass)) ** 2 for x in mass) / len(mass)))
    print("A weight with zero variance leaves every fidelity number unchanged.")
    print("\nObservation, not a finding: post-hoc, one domain, one model pair,")
    print("four errors, and the statistic was chosen after seeing the pattern.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
