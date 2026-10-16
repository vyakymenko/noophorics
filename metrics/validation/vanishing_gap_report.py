#!/usr/bin/env python3
"""Render the vanishing-gap tables from the saved record, or check them.

The results note quotes its numbers from ``research/vanishing-gap.json``. The
tables between the note's ``<!-- tables:start -->`` and ``<!-- tables:end -->``
markers are generated here, so a number in them cannot drift from the record:

    python3 metrics/validation/vanishing_gap_report.py --write
    python3 metrics/validation/vanishing_gap_report.py --check

Prose outside the markers is written by hand and must cite these tables.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RECORD = os.path.join(ROOT, "research", "vanishing-gap.json")
NOTE = os.path.join(ROOT, "research", "2026-10-16-vanishing-gap-results.md")
START, END = "<!-- tables:start -->", "<!-- tables:end -->"
Z = 1.959963984540054


def _f(x, fmt="%.4f"):
    """Shares and coverages are multiples of 1/400: four places show them exactly.

    The first version printed two, and 0.925 -- a cell below the 0.93 line the
    predictions are scored on -- rendered as 0.93.
    """
    return "–" if x is None else fmt % x


def _phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bias_model_rows(cells):
    """Coverage a set of the right width centred on the biased point would have.

    For each variant separately, only cells where every trial is reported and
    every set of that variant is bounded, so the median bounded width stands for
    the set. The centre is the *uncapped* ratio m/g, around which the Fieller set
    is built; the first version used the capped point and mis-centred every cell
    where the cap binds. se = width / (2z); predicted = P(|N(bias/se, 1)| <= z).
    """
    rows = []
    for c in cells:
        if c["kind"] != "grid":
            continue
        for v in ("V0", "V2"):
            x = c["variants"][v]
            if x["gate_pass"] < 0.999 or x["fieller_bounded"] < 0.999:
                continue
            se = x["fieller_bounded_median_width"] / (2 * Z)
            b = x["uncapped_bias_given_reported"]
            pred = _phi(Z - b / se) - _phi(-Z - b / se)
            rows.append((c["n"], c["g"], c["lam"], v, b, se, pred, x["cover_fieller"]))
    return rows


def _held_per_variant(cells):
    """P1-P3 re-read for each variant from the record. score() reads V0 only."""
    grid = [c for c in cells if c["kind"] == "grid"]
    out = {}
    for v in ("V0", "V1", "V2"):
        x = lambda c: c["variants"][v]
        p1 = sum(1 for c in grid if x(c)["cover_fieller"] < 0.93)
        hi = [c for c in grid if c["g"] >= 0.9]
        p2 = (any(x(c)["cover_pct_capped"] < 0.93 for c in hi)
              and any(x(c)["cover_pct_uncapped"] < 0.93 for c in hi)
              and all(x(c)["cover_present"] < 0.93 for c in grid if c["g"] >= 0.95))
        p3 = all(
            x(next(c for c in grid if c["n"] == n and c["lam"] == lam and c["g"] == 0.98))["fieller_bounded"]
            < min(0.5, x(next(c for c in grid if c["n"] == n and c["lam"] == lam
                               and c["g"] == 0.0))["fieller_bounded"])
            for n in (10, 16) for lam in (0.25, 0.5, 0.75, 1.0))
        out[v] = (p1, p2, p3)
    return out


def render(record):
    cells = record["cells"]
    p = record["predictions"]
    per = _held_per_variant(cells)
    yn = lambda b: "holds" if b else "fails"
    out = []
    out.append("**Table 1 — the predictions, scored as registered.** `score()` reads P2 and "
               "P3 from V0; the last column re-reads every prediction for each variant from "
               "the same record.\n")
    out.append("| prediction | held? | the numbers it turned on | per variant |")
    out.append("|---|---|---|---|")
    p1 = p["P1"]["cells_below_0.93"]
    out.append("| P1: V0 Fieller set covers ≥ 0.93 wherever `F*` is defined | **%s** | "
               "below 0.93 in %d of 48 grid cells, lowest %.4f | below 0.93 in V0 %d, V1 %d, "
               "V2 %d cells |"
               % ("yes" if p["P1"]["holds"] else "no", len(p1),
                  min(x[3] for x in p1) if p1 else float("nan"),
                  per["V0"][0], per["V1"][0], per["V2"][0]))
    pr = [x[3] for x in p["P2"]["present_report_cover_at_g_ge_0.95"]]
    out.append("| P2: percentile intervals fall below 0.93 at some `g ≥ 0.9`, capped and uncapped; "
               "the present report below 0.93 at every `g ≥ 0.95` | **%s** | capped below in %d cells, "
               "uncapped in %d; present report covers %.4f–%.4f at `g ≥ 0.95` | V0 %s, V1 %s, V2 %s |"
               % ("yes" if p["P2"]["holds"] else "no",
                  len(p["P2"]["capped_percentile_below_0.93_at_g_ge_0.9"]),
                  len(p["P2"]["uncapped_percentile_below_0.93_at_g_ge_0.9"]), min(pr), max(pr),
                  yn(per["V0"][1]), yn(per["V1"][1]), yn(per["V2"][1])))
    p3 = p["P3"]["bounded_share_g0_vs_g098"]
    out.append("| P3: bounded share of Fieller sets lower at `g = 0.98` than at `g = 0`, and below "
               "one half | **%s** | %.4f–%.4f at `g = 0`; %.4f–%.4f at `g = 0.98` | V0 %s, V1 %s, "
               "V2 %s |"
               % ("yes" if p["P3"]["holds"] else "no", min(x[2] for x in p3), max(x[2] for x in p3),
                  min(x[3] for x in p3), max(x[3] for x in p3),
                  yn(per["V0"][2]), yn(per["V1"][2]), yn(per["V2"][2])))
    nulls = [x[1] for x in p["P4"]["null_excludes_zero"]]
    out.append("| P4: zero-gap antinoophor detected ≥ 0.8 at `n = 16`; null cells exclude zero ≤ 0.08 "
               "| **%s** | %.4f; nulls %.4f and %.4f | does not depend on the variant |"
               % ("yes" if p["P4"]["holds"] else "no",
                  p["P4"]["antinoophor_n16_excludes_zero_away"], nulls[0], nulls[1]))
    out.append("")
    out.append("**Table 2 — every grid cell.** Coverage of the true `F*` at nominal 0.95; "
               "`present` is the gated, capped percentile interval with a refusal counted as a "
               "miss. Bias is of the gated, capped V0 point, among trials it reports.\n")
    out.append("| `n` | `g` | `λ` | true gap | V0 gate pass | V0 bounded | Fieller V0 | Fieller V1 | "
               "Fieller V2 | percentile, capped | present | V0 point bias | movement cover |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        if c["kind"] != "grid":
            continue
        v0, v1, v2 = (c["variants"][k] for k in ("V0", "V1", "V2"))
        out.append("| %d | %s | %s | %.4f | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            c["n"], c["g"], c["lam"], c["true_gap_mean"], _f(v0["gate_pass"]),
            _f(v0["fieller_bounded"]), _f(v0["cover_fieller"]), _f(v1["cover_fieller"]),
            _f(v2["cover_fieller"]), _f(v0["cover_pct_capped"]), _f(v0["cover_present"]),
            _f(v0["point_bias_given_reported"], "%+.3f"), _f(c["move"]["cover"])))
    out.append("")
    out.append("**Table 3 — the zero-gap cells.** The true gap is 0 and `F*` is undefined; "
               "what can be reported is the movement.\n")
    out.append("| `n` | cell | true movement | movement interval excludes 0 | …on the side of moving "
               "away | movement cover | Fieller bounded, V0 / V1 / V2 | gate pass, V0 / V1 |")
    out.append("|---|---|---|---|---|---|---|---|")
    for c in cells:
        if c["kind"] == "grid":
            continue
        v0, v1, v2 = (c["variants"][k] for k in ("V0", "V1", "V2"))
        out.append("| %d | %s | %+.4f | %s | %s | %s | %s / %s / %s | %s / %s |" % (
            c["n"], c["kind"], c["move"]["true_move_mean"], _f(c["move"]["excludes_zero"]),
            _f(c["move"]["excludes_zero_away"]), _f(c["move"]["cover"]),
            _f(v0["fieller_bounded"]), _f(v1["fieller_bounded"]), _f(v2["fieller_bounded"]),
            _f(v0["gate_pass"]), _f(v1["gate_pass"])))
    out.append("")
    out.append("**Table 4 — the simplest model of the Fieller sets' coverage loss.** A set of the "
               "observed median width, centred on the uncapped ratio with its observed bias, would "
               "cover with the probability shown. For each variant, the cells where every trial "
               "is reported and every set of that variant is bounded.\n")
    out.append("| `n` | `g` | `λ` | variant | bias of `M̂/Ĝ` | SE from width | predicted cover | "
               "observed cover |")
    out.append("|---|---|---|---|---|---|---|---|")
    for n, g, lam, v, b, se, pred, obs in bias_model_rows(cells):
        out.append("| %d | %s | %s | %s | %+.4f | %.4f | %.4f | %.4f |" % (n, g, lam, v, b, se, pred, obs))
    out.append("")
    out.append("**Table 5 — the gap each floor convention estimates**, where the true gap is "
               "small. *Added after the first registered run* (see Limits). V1 and V2 share a "
               "denominator. A gap estimate that moves with `λ` at fixed `g` is one the receiver "
               "is changing.\n")
    out.append("| `n` | cell | `g` | `λ` | true gap | mean `Ĝ`, V0 | share `Ĝ < 0`, V0 | "
               "mean `Ĝ`, V1 = V2 | share `Ĝ < 0`, V1 = V2 |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        if c["kind"] == "grid" and c["g"] < 0.9:
            continue
        v0, v1 = c["variants"]["V0"], c["variants"]["V1"]
        out.append("| %d | %s | %s | %s | %.4f | %+.4f | %s | %+.4f | %s |" % (
            c["n"], c["kind"], c["g"], c["lam"] if c["lam"] is not None else "–",
            c["true_gap_mean"], v0["g_hat_mean"], _f(v0["g_hat_negative"]),
            v1["g_hat_mean"], _f(v1["g_hat_negative"])))
    out.append("")
    out.append("**Table 6 — the gap's own interval**, which the plan's report for want 2 puts "
               "beside the movement but whose coverage the plan did not register. *Computed after "
               "the registered run* (see Limits). `percentile` is the 2.5th–97.5th percentile of "
               "`G*`; `basic` reflects it about `Ĝ`. Coverage is of the true gap; `above 0` is the "
               "share of trials whose whole interval lies above zero.\n")
    out.append("| `n` | cell | `g` | `λ` | true gap | V0 percentile | V0 basic | V1 percentile | "
               "V1 basic | V0 percentile above 0 | V1 percentile above 0 |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        v0, v1 = c["variants"]["V0"], c["variants"]["V1"]
        out.append("| %d | %s | %s | %s | %.4f | %s | %s | %s | %s | %s | %s |" % (
            c["n"], c["kind"], c["g"], c["lam"] if c["lam"] is not None else "–",
            c["true_gap_mean"], _f(v0["gap_cover_pct"]), _f(v0["gap_cover_basic"]),
            _f(v1["gap_cover_pct"]), _f(v1["gap_cover_basic"]),
            _f(v0["gap_pct_above_zero"]), _f(v1["gap_pct_above_zero"])))
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = ap.parse_args()
    with open(RECORD, encoding="utf-8") as fh:
        tables = render(json.load(fh))
    with open(NOTE, encoding="utf-8") as fh:
        note = fh.read()
    i, j = note.index(START) + len(START), note.index(END)
    fresh = note[:i] + "\n" + tables + note[j:]
    if args.write:
        with open(NOTE, "w", encoding="utf-8") as fh:
            fh.write(fresh)
        print("wrote tables into %s" % os.path.relpath(NOTE, ROOT))
        return 0
    if fresh != note:
        print("vanishing_gap_report: the note's tables differ from the record; "
              "regenerate with --write and review")
        return 1
    print("vanishing_gap_report: tables current against the record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
