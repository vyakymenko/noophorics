#!/usr/bin/env python3
"""Claims this repository makes about its own experiments, checked against them.

On 2026-09-08 an audit found three false published claims. Two were false
against machine-readable facts that were already in the repository:

  retraction 20  "No `claude-*` model has ever read `RIVERSIDE-30`" -- while
                 E-004's own result artifact recorded `claude-opus-4-8` at
                 0.733 against `RIVERSIDE-30@2e6afe2f3c92`.
  retraction 21  "it fails E-004's 0.90 subject gate" -- while E-004's
                 pre-registration registers `> 0.60` and no 0.90 anywhere.

Both stood for days, and both were read by several people, because a number in
prose reads as true and nobody reopened the file behind it. `check_counts.py`
guards ten counts the repository states *about itself*; these are claims it
states *about its own experiments*, and nothing read them.

    python3 tools/check_provenance.py     # exits non-zero on any mismatch

WHAT THIS DELIBERATELY DOES NOT COVER. Retraction 19 -- "`gpt-oss`'s fluent
floor sits above the ceiling", against a table four lines up reporting 223 and
a ceiling of 231 -- is a contradiction between prose and a table cell the prose
does not name. Catching it means resolving "gpt-oss's fluent floor" to a cell,
which is not a regex. It is left uncovered and named here rather than
approximated: a check that fires on prose it half-understands teaches its reader
to ignore it, which is worse than no check.

A SECOND GAP, MEASURED RATHER THAN GUESSED. Run against the tree of 2026-09-06
this tool reports 4 claims and exits 1, finding retraction 20 in
`PREDICTION-crossover.md` and retraction 21 in `RESULTS-llama-crossover.md` and
`THIRD-MODEL.md`. It does **not** find retraction 21's instance in
`theory/laws.md`, where the identical miscitation sits about thirty words after
an unrelated "withdrawn as tautological" and is therefore read as a quotation.
That is the cost of the shared 40-word convention: an acknowledgement near a
claim cannot be told from an acknowledgement *of* it. `check_retracted` carries
the same exposure. Naming it beats narrowing the window, which would break the
quotation case this tool needs more.

Struck text is skipped, and so is a claim quoted next to its own withdrawal --
a retraction has to be able to state what it withdrew. That test is not
reimplemented here: `WITHDRAWAL_VOCAB`, `CONDITIONAL` and `CONTEXT_WORDS` are
imported from `check_retracted`, which learned the hard part (the vocabulary
must be *perfective*, or "Refuted if:" on every law card suppresses the real
findings). Two writers of one list is a race the later writer wins.
"""

from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check_retracted import (                                   # noqa: E402
    CONDITIONAL, CONTEXT_WORDS, WITHDRAWAL_VOCAB, normalise,
)

# Comparison operators a registered threshold is written with. A gate row is a
# table row carrying one; prose mentioning the same number is not a gate, which
# is why the scope is table rows and not the file.
_OPS = r"[><≥≤]"


def _read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as fh:
        return fh.read()


def strip_struck(text: str) -> str:
    """What remains is asserted as true. Same convention as check_retracted."""
    text = re.sub(r"<s>.*?</s>", " ", text, flags=re.S | re.I)
    return re.sub(r"~~.+?~~", " ", text, flags=re.S)


def registered_gates() -> dict:
    """experiment id -> every number registered as a threshold in its gates.

    Read from table rows carrying a comparison operator, because that is the
    shape every gate table in `experiments/` uses. Deliberately permissive: a
    number found anywhere in such a row counts, so the check errs towards
    passing a real citation rather than towards crying wolf on one.
    """
    out = {}
    base = os.path.join(ROOT, "experiments")
    if not os.path.isdir(base):
        return out
    for d in sorted(os.listdir(base)):
        path = os.path.join(base, d, "PREREGISTRATION.md")
        if not os.path.exists(path):
            continue
        eid = d.split("-fluency")[0].split("-phantom")[0].split("-")[0:2]
        eid = "-".join(eid) if len(eid) > 1 else d
        nums = set()
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if not line.lstrip().startswith("|"):
                    continue
                if not re.search(_OPS, line):
                    continue
                for tok in re.findall(r"\d+(?:\.\d+)?", line):
                    nums.add(_canon(tok))
        out[eid] = nums
    return out


def _canon(tok: str) -> str:
    """0.9 and 0.90 are the same threshold; 0.90 and 0.900 are too."""
    try:
        return "%g" % float(tok)
    except ValueError:
        return tok


def measured_pairs() -> set:
    """(model, measure name) for every pair any artifact in the repo records."""
    pairs = set()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if ".git" in dirpath or "/docs" in dirpath or "node_modules" in dirpath:
            continue
        for name in filenames:
            if not name.endswith(".json"):
                continue
            try:
                with open(os.path.join(dirpath, name), "r", encoding="utf-8") as fh:
                    d = json.load(fh)
            except Exception:
                continue          # a malformed artifact is not this tool's outage
            if not isinstance(d, dict):
                continue
            # shape 1: one model, one measure
            m, pm = d.get("model"), d.get("probe_measure")
            if isinstance(m, str) and isinstance(pm, str):
                pairs.add((m, pm.split("@")[0]))
            # shape 2: accuracy[measure][model], as E-004 writes it
            acc = d.get("accuracy")
            if isinstance(acc, dict):
                for meas, per in acc.items():
                    if isinstance(per, dict):
                        for model in per:
                            pairs.add((model, meas.split("@")[0]))
    return pairs


# Claims of the form "E-004's 0.90 subject gate". The three phrasings here are
# the three the repository actually used; a phrasing not listed is not checked,
# which is a gap and is better than a pattern loose enough to match arithmetic.
GATE_CLAIMS = [
    re.compile(r"E-(\d\w*)['’]s\s+(?:[a-z\-]+\s+){0,3}?(\d+(?:\.\d+)?)\s+(?:[a-z\-]+\s+){0,3}?(?:gate|bar|threshold|floor)"),
    re.compile(r"E-(\d\w*)['’]s\s+(?:[a-z\-]+\s+){0,3}?(?:gate|bar|threshold|floor)\s+(?:of|at|is)\s+(\d+(?:\.\d+)?)"),
    re.compile(r"E-(\d\w*)\s+set\s+the\s+bar\s+at\s+(\d+(?:\.\d+)?)"),
]

# Claims that a measurement was never made.
NEVER_CLAIMS = [
    re.compile(r"[Nn]o\s+`?([A-Za-z0-9.:*\-]+)`?\s+model\s+has\s+ever\s+read\s+`?([A-Z][A-Z0-9\-]{3,})`?"),
    re.compile(r"has\s+never\s+been\s+run\s+on\s+`?([A-Z][A-Z0-9\-]{3,})`?"),
    re.compile(r"has\s+never\s+read\s+`?([A-Z][A-Z0-9\-]{3,})`?"),
]


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


_LEDGER_ROW = re.compile(r"^\| \d+ \|", re.M)


def in_ledger_claim_column(rel: str, text: str, start: int) -> bool:
    """Is this inside RETRACTIONS.md's "Claim" cell -- i.e. withdrawn by structure?

    `check_retracted` meets the same problem and answers it by excluding the
    whole file, naming the cost: a claim asserted as *live* inside
    RETRACTIONS.md then goes unchecked. The cost is avoidable. The ledger's
    second column is the withdrawn claim by construction, so only that cell is
    exempt here, and a "Killed by" cell citing the wrong experiment's gate is
    still caught.
    """
    if rel != "RETRACTIONS.md":
        return False
    bol = text.rfind("\n", 0, start) + 1
    line = text[bol:text.find("\n", start) if text.find("\n", start) > 0 else len(text)]
    if not _LEDGER_ROW.match(line):
        return False
    bars = [i for i, ch in enumerate(line) if ch == "|"]
    if len(bars) < 3:
        return False
    return bars[1] < (start - bol) < bars[2]


def acknowledged(text: str, start: int, end: int) -> bool:
    """Is this occurrence quoted next to its own withdrawal?

    The same window and the same vocabulary `check_retracted` uses, so a
    correction written to satisfy one checker satisfies both. Without this the
    tool fires on every retraction that states what it retracted -- which is
    every retraction, since the ledger's second column is nothing else.
    """
    before = normalise(text[max(0, start - 900):start])[-CONTEXT_WORDS:]
    after = normalise(text[end:end + 900])[:CONTEXT_WORDS]
    ctx = list(before) + list(after)
    for j, w in enumerate(ctx):
        nxt = ctx[j + 1] if j + 1 < len(ctx) else ""
        if (w, nxt) in CONDITIONAL:
            continue
        if w in WITHDRAWAL_VOCAB:
            return True
    return False


def _targets() -> list:
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if ".git" in dirpath or "node_modules" in dirpath:
            continue
        rel_dir = os.path.relpath(dirpath, ROOT)
        # Generated pages restate their sources; checking both doubles every
        # report. docs/index.html is hand-written and is checked.
        if rel_dir.startswith("docs") and rel_dir != "docs":
            continue
        for name in sorted(filenames):
            if name.endswith(".md") or name == "index.html":
                out.append(os.path.relpath(os.path.join(dirpath, name), ROOT))
    return sorted(out)


def _family_matches(claimed: str, model: str) -> bool:
    """`claude-*` matches claude-opus-4-8; an exact name matches itself."""
    c = claimed.strip("`").lower().rstrip("*").rstrip("-")
    return model.lower().startswith(c) if c else False


def main() -> int:
    gates = registered_gates()
    pairs = measured_pairs()
    measures = {meas for _, meas in pairs}
    models = {m for m, _ in pairs}

    print("registered gate thresholds")
    for eid in sorted(gates):
        if gates[eid]:
            print("  %-8s %s" % (eid, " ".join(sorted(gates[eid], key=_sortkey))))
    print("\nmeasured pairs: %d model×measure, %d models, %d measures"
          % (len(pairs), len(models), len(measures)))

    bad = quoted = 0
    for rel in _targets():
        try:
            text = strip_struck(_read(rel))
        except (OSError, UnicodeDecodeError):
            continue

        for pat in GATE_CLAIMS:
            for m in pat.finditer(text):
                eid, num = "E-" + m.group(1), _canon(m.group(2))
                if eid not in gates:
                    continue                 # not an experiment with a prereg
                if num in gates[eid]:
                    continue
                if (acknowledged(text, m.start(), m.end())
                        or in_ledger_claim_column(rel, text, m.start())):
                    quoted += 1
                    continue
                bad += 1
                if True:
                    print("\n  %s:%d" % (rel, _line_of(text, m.start())))
                    print("    claims: %s" % " ".join(m.group(0).split()))
                    print("    %s registers: %s"
                          % (eid, " ".join(sorted(gates[eid], key=_sortkey)) or "(no gate table)"))
                    print("    fix: cite the experiment that registered this threshold")

        for pat in NEVER_CLAIMS:
            for m in pat.finditer(text):
                groups = m.groups()
                meas = groups[-1]
                claimed_model = groups[0] if len(groups) > 1 else None
                if meas not in measures:
                    continue                 # nothing measured it; the claim holds
                if claimed_model is None:
                    # "It has never been run on X" has no subject to match on.
                    # An earlier version guessed the nearest model name and got
                    # it wrong on the sentence this check exists for: the
                    # crossover prediction names gpt-oss last and means claude.
                    # So it does not guess. Every model named nearby that WAS
                    # measured on the named measure is reported, and a human
                    # decides which one the sentence meant -- which is the whole
                    # job of a checker that cannot read.
                    back = text[max(0, m.start() - 600):m.start()]
                    hits = sorted({mm for mm in models
                                   if mm in back and (mm, meas) in pairs})
                    claimed_model = "the subject of this sentence"
                else:
                    hits = sorted({mm for mm in models
                                   if (mm, meas) in pairs
                                   and _family_matches(claimed_model, mm)})
                if hits:
                    if (acknowledged(text, m.start(), m.end())
                            or in_ledger_claim_column(rel, text, m.start())):
                        quoted += 1
                        continue
                    bad += 1
                    print("\n  %s:%d" % (rel, _line_of(text, m.start())))
                    print("    claims: %s" % " ".join(m.group(0).split())[:110])
                    print("    but %s on %s: %s"
                          % ("these were measured" if len(hits) > 1 or
                             claimed_model.startswith("the subject")
                             else "%s was measured" % claimed_model,
                             meas, ", ".join(hits)))
                    print("    fix: read the artifact, or strike the claim in place")

    if bad:
        print("\n%d claim(s) contradicted by this repository's own files. "
              "That is the shape of retractions 20 and 21." % bad)
        return 1
    print("\ncheck_provenance: every attributed gate and every never-measured claim "
          "agrees with the experiments behind it (%d quoted with the withdrawal "
          "acknowledged)" % quoted)
    return 0


def _sortkey(s: str):
    try:
        return (0, float(s))
    except ValueError:
        return (1, s)


if __name__ == "__main__":
    raise SystemExit(main())
