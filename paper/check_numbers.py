#!/usr/bin/env python3
"""Every number in the paper, against the committed file it comes from.

The paper asserts that each of its figures is traceable to a committed results
file. That is a claim, and a claim is worth what its check is worth -- so it is
checked here rather than asserted there.

Each row below names a quantity, reads it from the results JSON, reads what the
paper says, and compares. It fails when EITHER side moves: a results file
regenerated with different numbers, or a figure edited in the LaTeX by hand.
That symmetry is the point. A checker that only reads the paper would pass on a
paper that quietly disagreed with its own data.

    python3 paper/check_numbers.py
"""
import glob
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEX = os.path.join(HERE, "noophorics-2026.tex")
TOL = 0.0006          # the paper rounds to three decimals


def newest(pattern: str) -> dict:
    files = sorted(glob.glob(os.path.join(ROOT, pattern)))
    if not files:
        raise SystemExit("no file matches %s" % pattern)
    with open(files[-1], encoding="utf-8") as fh:
        return json.load(fh)


def load(path: str) -> dict:
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return json.load(fh)


def paper_number(pattern: str) -> float:
    """The figure the paper states, by regex. Missing is a failure, not a skip.

    A pattern that stops matching means the sentence was rewritten, and a
    rewritten sentence is exactly when a number goes stale unnoticed.
    """
    m = re.search(pattern, PAPER)
    if not m or m.group(1) is None:
        raise LookupError(pattern)
    return float(m.group(1).replace("$", "").replace("{,}", "").replace(",", ""))


with open(TEX, encoding="utf-8") as fh:
    PAPER = fh.read()

e2c = newest("experiments/E-002c-calibration-slope/results/*.json")
eff = e2c["effects"]
per = e2c["per_brief"]
observed = [b["agreement_observed"] for b in per.values()]
claim_s = [b["agreement_observed"] + b["phi_sender"] for b in per.values()]
claim_r = [b["agreement_observed"] + b["phi_receiver"] for b in per.values()]

void1 = load("experiments/E-001c-fluency-length-controlled/results/"
             "E-001c-20260803T180306Z.json")
void2 = load("experiments/E-001c-fluency-length-controlled/results/"
             "E-001c-20260804T094831Z.json")
floor = load("experiments/E-001c-fluency-length-controlled/floor-by-register.json")
LOW, HIGH = floor["band"]


def cellA(res: dict) -> list:
    return [r["words"] for r in res["rejected"]["A"]]


def fl(cell: str) -> list:
    return [r["words"] for r in floor["cells"][cell]]


def inband(ws) -> int:
    return sum(1 for w in ws if LOW <= w <= HIGH)


# (what it is, value from the source, regex capturing what the paper says)
ROWS = [
    ("beta pooled", eff["beta_pooled"]["value"],
     r"\$\\beta = \+(0\.\d+)\$, 95"),
    ("beta pooled CI low", eff["beta_pooled"]["ci95"][0],
     r"CI \$\[\+(0\.\d+), \+0\.\d+\]\$ --- about an eighth"),
    ("beta pooled CI high", eff["beta_pooled"]["ci95"][1],
     r"CI \$\[\+0\.\d+, \+(0\.\d+)\]\$ --- about an eighth"),
    ("beta receiver", eff["beta_receiver"]["value"],
     r"receiver tracks at \$\\beta = \+(0\.\d+)\$"),
    ("beta sender", eff["beta_sender"]["value"],
     r"track at all,\s*\n?\s*\$\\beta = (-0\.\d+)\$"),
    ("reliability", e2c["beta_attenuation"]["reliability"],
     r"attenuation \(reliability (0\.\d+)\)"),
    ("beta corrected", eff["beta_pooled"]["beta_reliability_corrected"],
     r"pooled\s*\n?slope is \$\+(0\.\d+)\$"),
    ("H3 value", eff["H3_sender_less_responsive"]["value"],
     r"H3 .*?& \$\+(0\.\d+)\$"),
    ("H3 p_holm", eff["H3_sender_less_responsive"]["p_value_holm"],
     r"supported \(\$p_\{\\text\{Holm\}\} = (0\.\d+)\$\) \\\\\s*\nH4"),
    ("H4 value", eff["H4_resolution_survives_finer_grid"]["value"],
     r"H4 .*?& \$\+(0\.\d+)\$"),
    ("observed mean", statistics.mean(observed),
     r"observed agreement & (0\.\d+)"),
    # Population sd. E-002c's FINDINGS reports 0.1591 and the paper copied it;
    # the sample sd is 0.1625, and the first version of this checker used it and
    # reported the paper as wrong. The estimator has to match the source, not
    # whichever one the checker's author reached for first.
    ("observed sd", statistics.pstdev(observed),
     r"observed agreement & 0\.\d+ & (0\.\d+)"),
    ("claimed sender mean", statistics.mean(claim_s),
     r"claimed, sender\s*& (0\.\d+)"),
    ("claimed receiver mean", statistics.mean(claim_r),
     r"claimed, receiver\s*& (0\.\d+)"),
    ("E-001c run 2, cell A mean words", statistics.mean(cellA(void2)),
     r"the realised word counts were 229--318, mean (\d+\.\d)"),
    ("E-001c run 2, cell A minimum", float(min(cellA(void2))),
     r"\\textbf\{minimum (\d+)\}"),
    # The paper rounds this one to a whole word, so it carries its own tolerance.
    ("E-001c run 1, cell A mean words", statistics.mean(cellA(void1)),
     r"mean (\d+) words against\s+the calibrated", 0.5),
    ("floor A", float(min(fl("A"))), r"A & fluent, declarative\s*& \\textbf\{(\d+)\}"),
    ("floor B", float(min(fl("B"))), r"B & fluent, contrastive\s*& (\d+)"),
    ("floor C", float(min(fl("C"))), r"C & terse, declarative\s*& (\d+)"),
    ("floor D", float(min(fl("D"))), r"D & terse, contrastive\s*& (\d+)"),
    ("fluent in band", float(inband(fl("A") + fl("B"))),
     r"Fluent cells put (\d+) of 24"),
    ("terse in band", float(inband(fl("C") + fl("D"))),
     r"terse cells put (\d+) of 24"),
    ("band ceiling", float(HIGH), r"inside a 182--(\d+) word band"),
]


def main() -> int:
    bad = 0
    print("paper figure                        source     paper")
    for row in ROWS:
        name, src, pattern = row[0], row[1], row[2]
        tol = row[3] if len(row) > 3 else max(TOL, abs(src) * 0.0006)
        try:
            said = paper_number(pattern)
        except LookupError:
            print("  %-33s %-10.4g PATTERN NOT FOUND -- the sentence moved"
                  % (name, src))
            bad += 1
            continue
        ok = abs(said - src) <= tol
        print("  %-33s %-10.4g %-10.4g %s"
              % (name, src, said, "ok" if ok else "MISMATCH"))
        bad += 0 if ok else 1
    if bad:
        print("\n%d figure(s) in the paper disagree with the committed record. "
              "The record is not the thing to edit." % bad)
    else:
        print("\nall %d checked figures agree with their sources." % len(ROWS))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
