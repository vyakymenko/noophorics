#!/usr/bin/env python3
"""Bias-corrected divergences on the vanishing-gap harness.

Runs the simulation registered in research/2026-10-22-bias-corrected-plan.md,
committed before this file. It reuses ``vanishing_gap`` for the truth, the
draws, the floors and Fieller's set, and spends randomness in exactly the order
``vanishing_gap.run_trial`` does, so the plug-in V0 and V2 reports it carries
must reproduce ``research/vanishing-gap.json`` field for field. ``check_reproduction``
compares them; a mismatch means the comparison is not the one the plan made.

    python3 metrics/validation/bias_corrected.py --out research/bias-corrected.json

Two decisions made while writing this file, before any run, because the plan
left them open:

1. **The ratio's bias** is taken over trials with ``G > EPSILON``, as for the
   plug-in variants, and is of the uncapped ratio ``M/G``.
2. **The jackknife of the plug-in divergence** uses the library's definition of
   JSD for unequal sample sizes when one answer is left out, ``m = (p + q)/2``
   of the two empirical frequency vectors.

Standard library only.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import random
import statistics
import sys
from functools import lru_cache
from typing import Dict, List, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import vanishing_gap as vg  # noqa: E402

LN2 = math.log(2.0)
ESTIMATORS = ("MM", "JK")
PLUGIN = ("V0", "V2")
Counts = Tuple[int, ...]


# --------------------------------------------------------------------------
# corrected divergences


def _h_bits(c: Counts) -> float:
    n = sum(c)
    return -sum((x / n) * math.log2(x / n) for x in c if x > 0)


@lru_cache(maxsize=None)
def jsd_mm(a: Counts, b: Counts) -> float:
    """Miller-Madow on each entropy of the plug-in divergence, equal sizes only.

    H_MM = H_plugin + (k - 1)/(2 N ln 2), k the options seen, N the sample
    size: n for each party and 2n for the pooled answers. Not clamped.
    """
    n = sum(a)
    if sum(b) != n:
        raise ValueError("Miller-Madow JSD here assumes equal answer counts")
    pooled = tuple(x + y for x, y in zip(a, b))

    def h_mm(c: Counts) -> float:
        k = sum(1 for x in c if x > 0)
        return _h_bits(c) + (k - 1) / (2.0 * sum(c) * LN2)
    return h_mm(pooled) - 0.5 * (h_mm(a) + h_mm(b))


@lru_cache(maxsize=None)
def jsd_jk(a: Counts, b: Counts) -> float:
    """Two-sample delete-one jackknife of the plug-in divergence. Not clamped.

    theta - (n_a - 1)(mean over left-out a - theta) - (n_b - 1)(... b ...),
    where leaving out one answer of option k has weight count_k / n.
    """
    theta = vg.jsd_counts(a, b)
    na, nb = sum(a), sum(b)

    def mean_left_out(c: Counts, other: Counts, first: bool) -> float:
        acc = 0.0
        for k, ck in enumerate(c):
            if ck == 0:
                continue
            reduced = tuple(x - (1 if i == k else 0) for i, x in enumerate(c))
            value = vg.jsd_counts(reduced, other) if first else vg.jsd_counts(other, reduced)
            acc += ck * value
        return acc / sum(c)

    ma = mean_left_out(a, b, True)
    mb = mean_left_out(b, a, False)
    return theta - (na - 1) * (ma - theta) - (nb - 1) * (mb - theta)


def corrected(fn, s: Sequence[Counts], p: Sequence[Counts], q: Sequence[Counts]) -> Tuple[float, float]:
    """(M, G) for a corrected divergence, with no floor."""
    n = len(s)
    dp = sum(fn(a, b) for a, b in zip(s, p)) / n
    dq = sum(fn(a, b) for a, b in zip(s, q)) / n
    return dp - dq, dp


FNS = {"MM": jsd_mm, "JK": jsd_jk}


# --------------------------------------------------------------------------
# one trial


def _interval(xs: List[float]) -> Tuple[float, float]:
    xs = sorted(xs)
    return vg._percentile(xs, 0.025), vg._percentile(xs, 0.975)


def _report(m: float, g: float, ms: List[float], gs: List[float], t: Dict,
            d_plug: float = None) -> Dict:
    shape = vg.fieller(m, g, vg._cov(ms, ms), vg._cov(ms, gs), vg._cov(gs, gs))
    g_lo, g_hi = _interval(gs)
    m_lo, m_hi = _interval(ms)
    rec = {
        "g_hat": g, "g_error": g - t["true_gap"],
        "reported": g > vg.EPSILON,
        "fieller": shape[0],
        "fieller_width": (shape[2] - shape[1]) if shape[0] == "bounded" else None,
        "gap_cover_pct": g_lo <= t["true_gap"] <= g_hi,
        "gap_cover_basic": 2 * g - g_hi <= t["true_gap"] <= 2 * g - g_lo,
        "gap_pct_above_zero": g_lo > 0,
        "move_cover": m_lo <= t["true_move"] <= m_hi,
        "move_excludes_zero": m_hi < 0 or m_lo > 0,
        "move_excludes_zero_away": m_hi < 0,
    }
    # Added after the registered run, to test why the percentile gap interval
    # failed: Wald intervals take their centre from the point and only their
    # spread from the bootstrap, and the shifts locate the bootstrap's centre.
    gsd, msd = statistics.stdev(gs), statistics.stdev(ms)
    rec.update({
        "gap_cover_wald": g - vg.Z * gsd <= t["true_gap"] <= g + vg.Z * gsd,
        "gap_wald_above_zero": g - vg.Z * gsd > 0,
        "move_cover_wald": m - vg.Z * msd <= t["true_move"] <= m + vg.Z * msd,
        "move_wald_excludes_zero": m + vg.Z * msd < 0 or m - vg.Z * msd > 0,
        "move_wald_excludes_zero_away": m + vg.Z * msd < 0,
        "boot_shift_from_point": statistics.fmean(gs) - g,
        "boot_shift_from_plugin": (statistics.fmean(gs) - d_plug) if d_plug is not None else None,
    })
    if t["true_f"] is not None:
        rec["cover_fieller"] = vg.in_set(shape, t["true_f"])
        rec["ratio_error"] = (m / g - t["true_f"]) if g > vg.EPSILON else None
    return rec


def run_trial(cell: Dict, trial: int) -> Dict:
    rng = random.Random(1_000_003 * cell["index"] + trial)
    sender, prior, post = vg.truth_for(rng, cell)
    n = cell["n"]
    t_prior = sum(vg.jsd(a, b) for a, b in zip(sender, prior)) / vg.N_PROBES
    t_post = sum(vg.jsd(a, b) for a, b in zip(sender, post)) / vg.N_PROBES
    truth = {"true_gap": t_prior, "true_move": t_prior - t_post,
             "true_f": (t_prior - t_post) / t_prior if t_prior > 0 else None}

    s = [vg.multinomial(rng, n, d) for d in sender]
    p = [vg.multinomial(rng, n, d) for d in prior]
    q = [vg.multinomial(rng, n, d) for d in post]
    plug = vg.ratio_parts(vg.components(s, p, q))
    point = {v: plug[v] for v in PLUGIN}
    point.update({e: corrected(FNS[e], s, p, q) for e in ESTIMATORS})

    boot = {k: ([], []) for k in point}
    for _ in range(vg.BOOT):
        bs = [vg.multinomial(rng, n, [x / n for x in c]) for c in s]
        bp = [vg.multinomial(rng, n, [x / n for x in c]) for c in p]
        bq = [vg.multinomial(rng, n, [x / n for x in c]) for c in q]
        bplug = vg.ratio_parts(vg.components(bs, bp, bq))
        for v in PLUGIN:
            boot[v][0].append(bplug[v][0])
            boot[v][1].append(bplug[v][1])
        for e in ESTIMATORS:
            m, g = corrected(FNS[e], bs, bp, bq)
            boot[e][0].append(m)
            boot[e][1].append(g)

    out = dict(truth)
    d_plug = vg.components(s, p, q)["d_prior"]
    out["reports"] = {k: _report(point[k][0], point[k][1], boot[k][0], boot[k][1], truth, d_plug)
                      for k in point}
    return out


# --------------------------------------------------------------------------
# summaries, the reproduction check and the registered predictions


def _share(xs) -> float:
    xs = list(xs)
    return sum(1 for x in xs if x) / len(xs) if xs else None


def summarise(cell: Dict, trials: List[Dict]) -> Dict:
    out = dict(cell)
    out["trials"] = len(trials)
    out["true_gap_mean"] = statistics.fmean(t["true_gap"] for t in trials)
    defined = [t for t in trials if t["true_f"] is not None]
    out["reports"] = {}
    for k in PLUGIN + ESTIMATORS:
        recs = [t["reports"][k] for t in trials]
        drecs = [t["reports"][k] for t in defined]
        errs = [r["ratio_error"] for r in drecs if r.get("ratio_error") is not None]
        widths = sorted(r["fieller_width"] for r in recs if r["fieller_width"] is not None)
        out["reports"][k] = {
            "g_hat_mean": statistics.fmean(r["g_hat"] for r in recs),
            "g_error_mean": statistics.fmean(r["g_error"] for r in recs),
            "g_rmse": math.sqrt(statistics.fmean(r["g_error"] ** 2 for r in recs)),
            "gate_pass": _share(r["reported"] for r in recs),
            "fieller_bounded": _share(r["fieller"] == "bounded" for r in recs),
            "fieller_bounded_median_width": widths[len(widths) // 2] if widths else None,
            "cover_fieller": _share(r["cover_fieller"] for r in drecs) if drecs else None,
            "ratio_bias_given_reported": statistics.fmean(errs) if errs else None,
            "gap_cover_pct": _share(r["gap_cover_pct"] for r in recs),
            "gap_cover_basic": _share(r["gap_cover_basic"] for r in recs),
            "gap_pct_above_zero": _share(r["gap_pct_above_zero"] for r in recs),
            "move_cover": _share(r["move_cover"] for r in recs),
            "move_excludes_zero": _share(r["move_excludes_zero"] for r in recs),
            "move_excludes_zero_away": _share(r["move_excludes_zero_away"] for r in recs),
            # Added after the registered run (see _report).
            "gap_cover_wald": _share(r["gap_cover_wald"] for r in recs),
            "gap_wald_above_zero": _share(r["gap_wald_above_zero"] for r in recs),
            "move_cover_wald": _share(r["move_cover_wald"] for r in recs),
            "move_wald_excludes_zero": _share(r["move_wald_excludes_zero"] for r in recs),
            "move_wald_excludes_zero_away": _share(r["move_wald_excludes_zero_away"] for r in recs),
            "boot_shift_from_point_mean": statistics.fmean(r["boot_shift_from_point"] for r in recs),
            "boot_shift_from_plugin_mean": statistics.fmean(r["boot_shift_from_plugin"] for r in recs),
        }
    return out


def run_cell(cell: Dict, trials: int = vg.TRIALS) -> Dict:
    return summarise(cell, [run_trial(cell, i) for i in range(trials)])


# Fields this run computes for V0 and V2 that vanishing-gap.json also holds.
REPRODUCED = {"gate_pass": "gate_pass", "fieller_bounded": "fieller_bounded",
              "cover_fieller": "cover_fieller", "g_hat_mean": "g_hat_mean",
              "gap_cover_pct": "gap_cover_pct", "gap_cover_basic": "gap_cover_basic",
              "gap_pct_above_zero": "gap_pct_above_zero",
              "fieller_bounded_median_width": "fieller_bounded_median_width"}


def check_reproduction(summary: List[Dict], previous: Dict) -> List[str]:
    """Every V0/V2 field shared with the previous record, compared exactly."""
    old = {c["index"]: c for c in previous["cells"]}
    bad = []
    for c in summary:
        o = old[c["index"]]
        for v in PLUGIN:
            for mine, theirs in REPRODUCED.items():
                if c["reports"][v][mine] != o["variants"][v][theirs]:
                    bad.append("cell %d %s %s: %r != %r" % (
                        c["index"], v, mine, c["reports"][v][mine], o["variants"][v][theirs]))
        if c["reports"]["V0"]["move_cover"] != o["move"]["cover"]:
            bad.append("cell %d movement cover differs" % c["index"])
    return bad


def score(summary: List[Dict]) -> Dict:
    grid = [c for c in summary if c["kind"] == "grid"]
    jk = lambda c: c["reports"]["JK"]
    v2 = lambda c: c["reports"]["V2"]
    b1 = [(c["n"], c["g"], c["lam"]) for c in grid
          if abs(jk(c)["g_error_mean"]) < abs(v2(c)["g_error_mean"])]
    b2 = [(c["n"], c["g"], c["lam"], jk(c)["cover_fieller"]) for c in grid
          if jk(c)["cover_fieller"] < 0.93]
    b3_cover = [(c["n"], c["g"], c["lam"], jk(c)["gap_cover_pct"]) for c in grid
                if jk(c)["gap_cover_pct"] < 0.90]
    nulls = [(c["n"], jk(c)["gap_pct_above_zero"]) for c in summary if c["kind"] == "null"]
    b4 = [(c["n"], c["lam"], jk(c)["fieller_bounded"]) for c in grid if c["g"] == 0.98]
    return {
        "B1": {"holds": len(b1) >= 40, "cells_where_jk_gap_error_is_smaller": len(b1)},
        "B2": {"holds": not b2, "cells_below_0.93": b2},
        "B3": {"holds": not b3_cover and all(x <= 0.10 for _, x in nulls),
               "cells_below_0.90": b3_cover, "null_gap_interval_above_zero": nulls},
        "B4": {"holds": all(x < 0.5 for _, _, x in b4), "bounded_share_at_g_0.98": b4},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", help="write the full record here as JSON")
    ap.add_argument("--previous", default=os.path.join(
        os.path.dirname(os.path.dirname(HERE)), "research", "vanishing-gap.json"))
    ap.add_argument("--quick", action="store_true",
                    help="smoke run: 20 trials of 4 cells; not the registered run")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    args = ap.parse_args()

    todo, trials = vg.cells(), vg.TRIALS
    if args.quick:
        todo, trials = [todo[0], todo[23], todo[-3], todo[-1]], 20
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        summary = list(pool.map(run_cell, todo, [trials] * len(todo)))
    record = {"plan": "research/2026-10-22-bias-corrected-plan.md",
              "trials_per_cell": trials, "bootstrap": vg.BOOT, "probes": vg.N_PROBES,
              "epsilon": vg.EPSILON, "z": vg.Z, "quick": bool(args.quick),
              "cells": summary}
    if not args.quick:
        with open(args.previous, encoding="utf-8") as fh:
            bad = check_reproduction(summary, json.load(fh))
        record["reproduction"] = {"matches_previous_record": not bad,
                                  "mismatch_count": len(bad), "mismatches": bad[:50]}
        record["predictions"] = score(summary)
        print("reproduction of V0/V2 against the previous record: %s"
              % ("exact" if not bad else "%d MISMATCHES" % len(bad)))
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    for c in summary:
        r = c["reports"]
        print("n=%-2d %-11s g=%-4s lam=%-4s | Fieller V2 %s JK %s MM %s | gap-cover V2 %s JK %s "
              "| JK gap err %+.4f V2 %+.4f" % (
                  c["n"], c["kind"], c["g"], c["lam"], _f(r["V2"]["cover_fieller"]),
                  _f(r["JK"]["cover_fieller"]), _f(r["MM"]["cover_fieller"]),
                  _f(r["V2"]["gap_cover_pct"]), _f(r["JK"]["gap_cover_pct"]),
                  r["JK"]["g_error_mean"], r["V2"]["g_error_mean"]))
    return 0 if args.quick or not record["reproduction"]["mismatches"] else 1


def _f(x):
    return "  -   " if x is None else "%.4f" % x


if __name__ == "__main__":
    raise SystemExit(main())
