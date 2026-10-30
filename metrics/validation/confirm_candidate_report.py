#!/usr/bin/env python3
"""Render the candidate confirmation's tables from the saved record, or check them.

    python3 metrics/validation/confirm_candidate_report.py --write
    python3 metrics/validation/confirm_candidate_report.py --check

The tables between the note's markers are generated here from
``research/candidate-confirmation.json``; prose outside them cites these tables.
Columns and tables marked with † rest on fields added after the registered run.
``--check`` also rescores the record with the committed ``score()`` and checks its
settings against the module's, so a record edited by hand does not pass.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from statistics import NormalDist

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import confirm_candidate as cc  # noqa: E402

RECORD = os.path.join(ROOT, "research", "candidate-confirmation.json")
NOTE = os.path.join(ROOT, "research", "2026-10-30-candidate-confirmation-results.md")
START, END = "<!-- tables:start -->", "<!-- tables:end -->"
Z = 1.959963984540054


def normal_cover(bias_sd, ratio):
    """Coverage of a Wald interval whose error is normal with this centre and spread.

    ``bias_sd`` is the mean error in units of its actual spread, ``ratio`` the
    interval's spread as a share of the actual one.
    """
    n = NormalDist()
    return n.cdf(Z * ratio - bias_sd) - n.cdf(-Z * ratio - bias_sd)


def _model(c, which):
    cover, em, esd, bsd = {"gap": ("gap_cover", "g_error_mean", "g_error_sd", "g_boot_sd_mean"),
                           "move": ("move_cover", "m_error_mean", "m_error_sd",
                                    "m_boot_sd_mean")}[which]
    b, r = c[em] / c[esd], c[bsd] / c[esd]
    return c[cover], normal_cover(b, r), normal_cover(b, 1.0), normal_cover(0.0, r)


def _f(x, fmt="%.4f"):
    return "–" if x is None else fmt % x


def _range(xs, fmt="%.4f"):
    xs = [x for x in xs if x is not None]
    return (fmt + "–" + fmt) % (min(xs), max(xs)) if xs else "–"


def _held(p):
    return "yes" if p["holds"] else "no"


def _grid_table(rows):
    out = ["| `K` | `n` | `g` | `λ` | true gap | Fieller cover | bounded | median width | "
           "movement Wald cover | gap Wald cover | mean error of `Ĝ` |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in rows:
        out.append("| %d | %d | %s | %s | %.4f | %s | %s | %s | %s | %s | %+.4f |" % (
            c["k"], c["n"], c["g"], c["lam"], c["true_gap_mean"], _f(c["cover_fieller"]),
            _f(c["fieller_bounded"]), _f(c["fieller_bounded_median_width"]),
            _f(c["move_cover"]), _f(c["gap_cover"]), c["g_error_mean"]))
    return out


def render(record):
    cells = record["cells"]
    grid = [c for c in cells if c["kind"] == "grid"]
    g0 = [c for c in grid if c["rho"] == 0.0]
    g3 = [c for c in grid if c["rho"] == 0.3]
    p = record["predictions"]
    out = []
    out.append("**Table 1 — the predictions, scored as registered.** C1–C3 are scored on the 24 "
               "grid cells with independent answers, C2 and C3 also on the zero-gap cells with "
               "independent answers, C5 on the 8 grid cells at `g = 0.95` with independent answers, "
               "and C4 on the 24 grid cells with correlated ones.\n")
    out.append("| prediction | held? | the numbers it turned on |")
    out.append("|---|---|---|")
    out.append("| C1: Fieller set covers ≥ 0.93 in every grid cell, `ρ = 0` | **%s** | %s; below "
               "0.93 in %d of 24 cells |" % (_held(p["C1"]), _range(c["cover_fieller"] for c in g0),
                                            len(p["C1"]["cells_below_0.93"])))
    out.append("| C2: movement Wald covers ≥ 0.93 in every grid cell; antinoophor at `n = 16` "
               "excludes zero away in ≥ 0.80; nulls exclude zero in ≤ 0.08 | **%s** | covers %s, "
               "below 0.93 in %d of 24 cells; antinoophor %s; nulls %s |"
               % (_held(p["C2"]), _range(c["move_cover"] for c in g0),
                  len(p["C2"]["grid_cells_below_0.93"]),
                  _range(x for _, x in p["C2"]["antinoophor_n16_excludes_zero_away"]),
                  _range(x for *_, x in p["C2"]["null_excludes_zero"])))
    out.append("| C3: gap Wald covers ≥ 0.90 in every grid cell; above zero in ≤ 0.10 of null "
               "trials | **%s** | covers %s, below 0.90 in %d of 24 cells; nulls above zero %s |"
               % (_held(p["C3"]), _range(c["gap_cover"] for c in g0),
                  len(p["C3"]["grid_cells_below_0.90"]),
                  _range(x for *_, x in p["C3"]["null_gap_above_zero"])))
    out.append("| C4: at `ρ = 0.3`, Fieller covers < 0.93 in at least half the grid cells | "
               "**%s** | %d of %d cells; coverage %s |"
               % (_held(p["C4"]), p["C4"]["dependent_cells_below_0.93"], p["C4"]["of"],
                  _range(c["cover_fieller"] for c in g3)))
    out.append("| C5: bounded share < 0.5 at `g = 0.95` in every grid cell, `ρ = 0` | **%s** | %s |"
               % (_held(p["C5"]), _range(x for *_, x in p["C5"]["bounded_share_at_g_0.95"])))
    out.append("")
    out.append("**Table 2 — independent answers (`ρ = 0`), every grid cell.** Coverage of the "
               "true `F*` by the Fieller set, the share of bounded sets and their median width, "
               "coverage of the true movement and gap by their Wald intervals, and the mean error "
               "of the jackknife gap.\n")
    out.extend(_grid_table(g0))
    out.append("")
    out.append("**Table 3 — correlated answers (`ρ = 0.3`), every grid cell.** The same columns.\n")
    out.extend(_grid_table(g3))
    out.append("")
    out.append("**Table 4 — the zero-gap cells.** The share of trials whose movement interval "
               "excludes zero, excludes it on the side of moving away, and whose gap interval "
               "lies wholly above zero; and the share of bounded Fieller sets.\n")
    out.append("| `K` | `ρ` | `n` | cell | movement excludes 0 | movement away | gap above 0 | "
               "Fieller bounded | mean error of `Ĝ` |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        if c["kind"] == "grid":
            continue
        out.append("| %d | %s | %d | %s | %s | %s | %s | %s | %+.4f |" % (
            c["k"], c["rho"], c["n"], c["kind"], _f(c["move_excludes_zero"]),
            _f(c["move_excludes_zero_away"]), _f(c["gap_above_zero"]),
            _f(c["fieller_bounded"]), c["g_error_mean"]))
    out.append("")
    out.append("**Table 5 — the errors' spread beside the bootstrap's estimate of it †, every "
               "cell.** For the movement and the gap: the true value's mean over trials, the mean "
               "and standard deviation over trials of the estimate's error, the mean bootstrap "
               "standard deviation, the bootstrap's spread as a share of the actual one, and the "
               "mean error in units of the actual spread.\n")
    out.append("| `K` | `ρ` | `n` | cell | true movement † | `M̂` error † | `M̂` error sd † | "
               "`M*` sd † | ratio † | bias/sd † | true gap | `Ĝ` error | `Ĝ` error sd † | `G*` sd † | "
               "ratio † | bias/sd † |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        label = c["kind"] if c["kind"] != "grid" else "g %s, λ %s" % (c["g"], c["lam"])
        out.append("| %d | %s | %d | %s | %+.4f | %+.4f | %.4f | %.4f | %.2f | %+.2f | %.4f | "
                   "%+.4f | %.4f | %.4f | %.2f | %+.2f |" % (
                       c["k"], c["rho"], c["n"], label, c["true_move_mean"], c["m_error_mean"],
                       c["m_error_sd"], c["m_boot_sd_mean"], c["m_boot_sd_mean"] / c["m_error_sd"],
                       c["m_error_mean"] / c["m_error_sd"], c["true_gap_mean"], c["g_error_mean"],
                       c["g_error_sd"], c["g_boot_sd_mean"], c["g_boot_sd_mean"] / c["g_error_sd"],
                       c["g_error_mean"] / c["g_error_sd"]))
    out.append("")
    gaps = [_model(c, "gap") for c in cells]
    moves = [_model(c, "move") for c in cells]
    zs = [abs(o - m) / math.sqrt(m * (1 - m) / c["trials"])
          for c in cells for o, m, _, _ in (_model(c, "gap"), _model(c, "move"))]
    out.append("**Table 6 — the gap's Wald coverage against a normal model built from Table 5 †, "
               "every grid cell.** *model*: an error normal with the measured mean and standard "
               "deviation, against an interval of half-width `z` × the mean bootstrap standard "
               "deviation; *centre only*: the same error against `z` × its own standard deviation; "
               "*spread only*: a centred error against `z` × the mean bootstrap standard deviation. "
               "Over all 64 cells, observed minus model lies between %+.4f and %+.4f for the gap and "
               "between %+.4f and %+.4f for the movement; the largest difference is %.2f Monte Carlo "
               "standard errors of the model's coverage, over %d cell–quantity pairs. The model was "
               "chosen after the failures were seen.\n"
               % (min(o - m for o, m, _, _ in gaps), max(o - m for o, m, _, _ in gaps),
                  min(o - m for o, m, _, _ in moves), max(o - m for o, m, _, _ in moves),
                  max(zs), len(zs)))
    out.append("| `K` | `ρ` | `n` | `g` | `λ` | observed | model | centre only | spread only |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for c in grid:
        o, m, centre, spread = _model(c, "gap")
        out.append("| %d | %s | %d | %s | %s | %.4f | %.4f | %.4f | %.4f |"
                   % (c["k"], c["rho"], c["n"], c["g"], c["lam"], o, m, centre, spread))
    return "\n".join(out) + "\n"


def record_problems(record):
    """What makes the record disagree with the committed module, if anything."""
    problems = []
    if json.loads(json.dumps(cc.score(record["cells"]))) != record["predictions"]:
        problems.append("predictions differ from score(cells)")
    settings = {"trials_per_cell": cc.TRIALS, "bootstrap": cc.BOOT, "probes": cc.N_PROBES,
                "z": cc.Z, "alpha_sender": cc.ALPHA_SENDER, "alpha_diffuse": cc.ALPHA_DIFFUSE,
                "quick": False}
    for key, want in settings.items():
        if record.get(key) != want:
            problems.append("%s is %r, not %r" % (key, record.get(key), want))
    shape = lambda c: (c["index"], c["k"], c["rho"], c["n"], c["kind"], c["g"], c["lam"])
    if [shape(c) for c in record["cells"]] != [shape(c) for c in cc.cells()]:
        problems.append("cells differ from cells()")
    short = [c["index"] for c in record["cells"] if c["trials"] != cc.TRIALS]
    if short:
        problems.append("cells %s do not have %d trials" % (short, cc.TRIALS))
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = ap.parse_args()
    with open(RECORD, encoding="utf-8") as fh:
        record = json.load(fh)
    problems = record_problems(record)
    if problems:
        print("confirm_candidate_report: the record disagrees with the module: " + "; ".join(problems))
        return 1
    tables = render(record)
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
        print("confirm_candidate_report: the note's tables differ from the record; "
              "regenerate with --write and review")
        return 1
    print("confirm_candidate_report: tables current against the record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
