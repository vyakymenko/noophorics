#!/usr/bin/env python3
"""Every experiment's status on the site agrees with the directory behind it.

The front page carried, for weeks, `E-002 - Ablation ladder - Planned` and
`E-004 - Chain decay - Planned`, while `experiments/E-002-phantom-agreement/`
and `experiments/E-004-disagreement-detector/` both held a VOID.md and were
different experiments entirely. The founding roadmap had assigned those two
identifiers to the ladder and the chain; the repository later reused them.

Nothing could see it. The ids in `theory/laws.md` are prose, not links, so
`check_links` never resolved them. And `check_counts.py` compares the site's
"four experiments are void" against the number of VOID.md files -- which was
right the whole time. The count was correct while the list a reader actually
reads was wrong, which is the same shape RETRACTIONS.md records about its own
void table, on a different surface.

    python3 tools/check_experiments.py      # exits non-zero on any mismatch
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A site tag that means "no directory should exist yet".
UNBUILT = {"Planned", "Unscheduled"}

# Experiments whose site status is deliberately not the mechanical one, with the
# reason. Kept explicit and short: an exception list that grows without reasons
# is how a check stops checking.
OVERRIDE = {
    # E-001's first live run was voided and the experiment was then reopened as
    # a construct critique, so it carries FINDINGS.md and is still described as
    # void. RETRACTIONS.md lists it in the void table for the same reason.
    "E-001": "Void",
}


def status_of(d: str) -> str:
    if os.path.exists(os.path.join(d, "VOID.md")):
        return "Void"
    if os.path.exists(os.path.join(d, "FINDINGS.md")):
        return "Findings"
    return "Live"


def repo_experiments(root: str = None) -> dict:
    base = os.path.join(root or ROOT, "experiments")
    if not os.path.isdir(base):
        return {}
    out = {}
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        if not os.path.isdir(d):
            continue
        m = re.match(r"(E-\d+[a-z]?)", name)
        if m:
            out[m.group(1)] = status_of(d)
    return out


# `class="tag"` is not enough: E-001 carries `class="tag tag-alert"`, and a
# checker that silently fails to find a row reports the row as ABSENT, which is
# a different and more alarming defect than the one it has.
ROW = re.compile(
    r'<span class="id">(E-[\w+]+)</span>.*?'
    r'<span class="tag[^"]*">([^<]+)</span>', re.S)


def normalise(tag: str) -> str:
    """"Void &middot; informative" is a Void with a gloss, not a fifth status."""
    return re.split(r"&\w+;|\u00b7", tag)[0].strip()


def site_experiments(root: str = None) -> dict:
    path = os.path.join(root or ROOT, "docs", "index.html")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    # Non-greedy across the whole file would let one row's id pair with a later
    # row's tag, so each row is matched inside its own container.
    out = {}
    for block in re.split(r'<div class="exp">', html)[1:]:
        m = ROW.search(block.split("</div>")[0] + "</div>")
        if m:
            out[m.group(1)] = normalise(m.group(2))
    return out


def check(root: str = None) -> list:
    repo, site = repo_experiments(root), site_experiments(root)
    bad = []
    for eid, actual in sorted(repo.items()):
        expected = OVERRIDE.get(eid, actual)
        if eid not in site:
            bad.append((eid, "runs in the repository, absent from the site"))
        elif site[eid] in UNBUILT:
            bad.append((eid, "site says %r but experiments/%s* exists (status %r)"
                        % (site[eid], eid, actual)))
        elif site[eid] != expected:
            bad.append((eid, "site says %r, directory says %r"
                        % (site[eid], expected)))
    for eid, tag in sorted(site.items()):
        if eid.endswith("+"):
            continue
        if eid not in repo and tag not in UNBUILT:
            bad.append((eid, "site says %r but no experiments/%s* directory exists"
                        % (tag, eid)))
    return bad


def main() -> int:
    repo, site = repo_experiments(), site_experiments()
    bad = check()
    print("experiments: %d in the repository, %d rows on the site"
          % (len(repo), len(site)))
    for eid in sorted(set(repo) | set(site)):
        print("  %-8s repo %-9s site %s"
              % (eid, repo.get(eid, "-"), site.get(eid, "-")))
    if bad:
        print("\n%d mismatch(es):" % len(bad))
        for eid, why in bad:
            print("  %-8s %s" % (eid, why))
        print("\nAn identifier that names one thing in experiments/ and another "
              "on the site is worse than a wrong status: it makes every pointer "
              "to it resolve to the wrong experiment.")
    else:
        print("\ncheck_experiments: every status agrees with its directory")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
