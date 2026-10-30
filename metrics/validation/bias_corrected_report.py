#!/usr/bin/env python3
"""Render the bias-corrected tables from the saved record, or check them.

    python3 metrics/validation/bias_corrected_report.py --write
    python3 metrics/validation/bias_corrected_report.py --check

The tables between the note's markers are generated here from
``research/bias-corrected.json``; prose outside them cites these tables.
Columns marked with † come from fields added after the registered run.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RECORD = os.path.join(ROOT, "research", "bias-corrected.json")
NOTE = os.path.join(ROOT, "research", "2026-10-22-bias-corrected-results.md")
START, END = "<!-- tables:start -->", "<!-- tables:end -->"


def _f(x, fmt="%.4f"):
    return "–" if x is None else fmt % x


def _range(xs, fmt="%.4f"):
    xs = [x for x in xs if x is not None]
    return (fmt + "–" + fmt) % (min(xs), max(xs))


def render(record):
    cells = record["cells"]
    grid = [c for c in cells if c["kind"] == "grid"]
    p = record["predictions"]
    rep = record["reproduction"]
    R = lambda c, k: c["reports"][k]
    out = []
    out.append("**Table 1 — the predictions, scored as registered, and the built-in check.**\n")
    out.append("| item | held? | the numbers it turned on |")
    out.append("|---|---|---|")
    out.append("| check: V0 and V2 reproduce `vanishing-gap.json` exactly | **%s** | %d mismatching fields |"
               % ("yes" if rep["matches_previous_record"] else "no",
                  rep.get("mismatch_count", len(rep["mismatches"]))))
    out.append("| B1: jackknife `Ĝ` closer to the true gap than V2's in ≥ 40 of 48 cells | **%s** | "
               "%d of 48 |" % ("yes" if p["B1"]["holds"] else "no",
                               p["B1"]["cells_where_jk_gap_error_is_smaller"]))
    out.append("| B2: jackknife Fieller set covers ≥ 0.93 in every grid cell | **%s** | %s across "
               "the grid; below 0.93 in %d cells |"
               % ("yes" if p["B2"]["holds"] else "no",
                  _range(R(c, "JK")["cover_fieller"] for c in grid), len(p["B2"]["cells_below_0.93"])))
    nulls = p["B3"]["null_gap_interval_above_zero"]
    out.append("| B3: jackknife gap percentile interval covers ≥ 0.90 everywhere, and lies above "
               "zero in ≤ 0.10 of null trials | **%s** | covers %s; below 0.90 in %d of 48 "
               "cells; above zero in %s of null trials |"
               % ("yes" if p["B3"]["holds"] else "no",
                  _range(R(c, "JK")["gap_cover_pct"] for c in grid),
                  len(p["B3"]["cells_below_0.90"]), _range(x for _, x in nulls)))
    out.append("| B4: jackknife bounded share below one half at `g = 0.98` | **%s** | %s |"
               % ("yes" if p["B4"]["holds"] else "no",
                  _range(x for _, _, x in p["B4"]["bounded_share_at_g_0.98"])))
    out.append("")
    out.append("**Table 2 — the Fieller set for `F*`, every grid cell.** Coverage of the true "
               "`F*`; the median width of the bounded sets, which the plan committed to report "
               "beside any coverage gained; and the bias of the uncapped ratio over trials with "
               "`Ĝ > 0.02`.\n")
    out.append("| `n` | `g` | `λ` | true gap | cover V0 | cover V2 | cover MM | cover JK | "
               "bounded JK | width V2 | width JK | ratio bias V2 | ratio bias MM | ratio bias JK |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in grid:
        v0, v2, mm, jk = (R(c, k) for k in ("V0", "V2", "MM", "JK"))
        out.append("| %d | %s | %s | %.4f | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            c["n"], c["g"], c["lam"], c["true_gap_mean"], _f(v0["cover_fieller"]),
            _f(v2["cover_fieller"]), _f(mm["cover_fieller"]), _f(jk["cover_fieller"]),
            _f(jk["fieller_bounded"]), _f(v2["fieller_bounded_median_width"]),
            _f(jk["fieller_bounded_median_width"]),
            _f(v2["ratio_bias_given_reported"], "%+.4f"),
            _f(mm["ratio_bias_given_reported"], "%+.4f"),
            _f(jk["ratio_bias_given_reported"], "%+.4f")))
    out.append("")
    out.append("**Table 3 — the gap, every grid cell.** The mean error of `Ĝ` against the true "
               "gap, and coverage of the true gap by the two registered intervals (percentile and "
               "basic) and by a Wald interval †, for Miller–Madow and the jackknife.\n")
    out.append("| `n` | `g` | `λ` | error V2 | error MM | error JK | MM percentile | MM basic | "
               "MM Wald † | JK percentile | JK basic | JK Wald † |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in grid:
        v2, mm, jk = (R(c, k) for k in ("V2", "MM", "JK"))
        out.append("| %d | %s | %s | %+.4f | %+.4f | %+.4f | %s | %s | %s | %s | %s | %s |" % (
            c["n"], c["g"], c["lam"], v2["g_error_mean"], mm["g_error_mean"], jk["g_error_mean"],
            _f(mm["gap_cover_pct"]), _f(mm["gap_cover_basic"]), _f(mm["gap_cover_wald"]),
            _f(jk["gap_cover_pct"]), _f(jk["gap_cover_basic"]), _f(jk["gap_cover_wald"])))
    out.append("")
    out.append("**Table 4 — the movement, every grid cell.** Coverage of the true movement by the "
               "registered percentile interval and by a Wald interval †. V0's movement is the "
               "plug-in `D̂_prior − D̂_post`.\n")
    out.append("| `n` | `g` | `λ` | V0 percentile | MM percentile | JK percentile | V0 Wald † | "
               "MM Wald † | JK Wald † |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for c in grid:
        v0, mm, jk = (R(c, k) for k in ("V0", "MM", "JK"))
        out.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            c["n"], c["g"], c["lam"], _f(v0["move_cover"]), _f(mm["move_cover"]),
            _f(jk["move_cover"]), _f(v0["move_cover_wald"]), _f(mm["move_cover_wald"]),
            _f(jk["move_cover_wald"])))
    out.append("")
    out.append("**Table 5 — the zero-gap cells, every estimator.** The share of trials whose gap "
               "interval lies wholly above zero (a gap reported where there is none), and whose "
               "movement interval excludes zero on the side of moving away. † added after the "
               "registered run.\n")
    out.append("| `n` | cell | estimator | gap above 0, percentile | gap above 0, Wald † | "
               "movement away, percentile | movement away, Wald † | Fieller bounded |")
    out.append("|---|---|---|---|---|---|---|---|")
    for c in cells:
        if c["kind"] == "grid":
            continue
        for k in ("V0", "V2", "MM", "JK"):
            r = R(c, k)
            out.append("| %d | %s | %s | %s | %s | %s | %s | %s |" % (
                c["n"], c["kind"], k, _f(r["gap_pct_above_zero"]), _f(r["gap_wald_above_zero"]),
                _f(r["move_excludes_zero_away"]), _f(r["move_wald_excludes_zero_away"]),
                _f(r["fieller_bounded"])))
    out.append("")
    out.append("**Table 6 — where the bootstrap centres the gap †.** Across all 52 cells, the mean "
               "of the bootstrap `G*` minus the point estimate, and minus the plug-in `D̂_prior` "
               "computed from the same answers; the second column is meaningful for the estimators "
               "without a floor (MM, JK).\n")
    out.append("| estimator | `mean(G*) − Ĝ` | `mean(G*) − D̂_prior, plug-in` | gap Wald cover, grid † | "
               "movement Wald cover, grid † |")
    out.append("|---|---|---|---|---|")
    for k in ("V0", "V2", "MM", "JK"):
        out.append("| %s | %s | %s | %s | %s |" % (
            k, _range((R(c, k)["boot_shift_from_point_mean"] for c in cells), "%+.4f"),
            _range((R(c, k)["boot_shift_from_plugin_mean"] for c in cells), "%+.4f"),
            _range(R(c, k)["gap_cover_wald"] for c in grid),
            _range(R(c, k)["move_cover_wald"] for c in grid)))
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
        print("bias_corrected_report: the note's tables differ from the record; "
              "regenerate with --write and review")
        return 1
    print("bias_corrected_report: tables current against the record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
