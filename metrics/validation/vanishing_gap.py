#!/usr/bin/env python3
"""F* near a vanishing gap: Fieller sets against the present report.

Runs the simulation registered in research/2026-10-16-vanishing-gap-plan.md,
which was committed before this file existed. Synthetic agents with exactly
known answer distributions, so the true F* -- and the true movement and gap --
are computed with no sampling; each trial then draws finite answers and asks
which reports cover the truth.

    python3 metrics/validation/vanishing_gap.py --out research/vanishing-gap.json
    python3 metrics/validation/vanishing_gap.py --quick      # a smoke run

Four decisions made while writing this file, before the registered run, because
the plan left them open; each is reported with the results. (This line said
"Three" above four items when it was committed; corrected 2026-10-16.)

1. **The present report's interval.** The plan's P2 speaks of "the present
   gated report" falling below a coverage level. A point has no coverage, so
   the present report is scored as the capped percentile interval, given only
   when the point itself passes the epsilon gate -- a refusal is a miss.
2. **Percentile intervals** use the bootstrap replicates whose denominator is
   positive. A trial with no such replicate gives no interval, scored a miss.
3. **The floor's exact form** -- see ``exact_floor`` -- is the limit of the
   library's Monte Carlo permutation floor; ``test_vanishing_gap.py`` checks
   the two agree before anything here is read.
4. **P2's "capped or not"** is read strictly: the capped and the uncapped
   percentile interval must *each* fall below 0.93 in some cell with
   ``g >= 0.9``, not merely one of them.

Standard library only, like everything in ``metrics/``.
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
from math import comb
from typing import Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

from synthetic import OPTIONS, _random_dist  # noqa: E402

K = len(OPTIONS)
N_PROBES = 33
EPSILON = 0.02          # metrics/noophorics/fidelity.py DEFAULT_EPSILON
Z = 1.959963984540054   # two-sided 95%
_EPS = 1e-12            # the library's entropy threshold

# The registered design. Order fixes every seed.
NS = (10, 16)
GS = (0.0, 0.6, 0.8, 0.9, 0.95, 0.98)
LAMS = (0.25, 0.5, 0.75, 1.0)
ZERO_GAP = ("null", "antinoophor")
ANTI_MU = 0.3
TRIALS = 400
BOOT = 400

Dist = Tuple[float, ...]
Counts = Tuple[int, ...]


# --------------------------------------------------------------------------
# divergence and floor, on count vectors


def _entropy(p: Sequence[float]) -> float:
    return -sum(x * math.log2(x) for x in p if x > _EPS)


def jsd(p: Sequence[float], q: Sequence[float]) -> float:
    """Jensen-Shannon divergence in bits, as ``divergence.jensen_shannon``."""
    m = [0.5 * (a + b) for a, b in zip(p, q)]
    d = _entropy(m) - 0.5 * (_entropy(p) + _entropy(q))
    return max(0.0, min(1.0, d))


@lru_cache(maxsize=None)
def jsd_counts(a: Counts, b: Counts) -> float:
    na, nb = sum(a), sum(b)
    return jsd([x / na for x in a], [x / nb for x in b])


@lru_cache(maxsize=None)
def exact_floor(a: Counts, b: Counts) -> float:
    """The permutation floor's limit, as an exact sum.

    ``permutation_floor`` pools the two parties' answers, shuffles, splits them
    back into groups of the original sizes and averages the divergence. Over
    all shuffles the first group's counts are multivariate hypergeometric, so
    the average it estimates is this finite sum. Like the library, a probe on
    which both parties gave one answer throughout has floor zero.
    """
    pooled = tuple(x + y for x, y in zip(a, b))
    na, total = sum(a), sum(pooled)
    if sum(1 for c in pooled if c) <= 1:
        return 0.0
    denom = comb(total, na)
    acc = 0.0
    for a0 in range(max(0, na - pooled[1] - pooled[2]), min(pooled[0], na) + 1):
        rest = na - a0
        for a1 in range(max(0, rest - pooled[2]), min(pooled[1], rest) + 1):
            a2 = rest - a1
            w = comb(pooled[0], a0) * comb(pooled[1], a1) * comb(pooled[2], a2)
            first = (a0, a1, a2)
            second = tuple(p - x for p, x in zip(pooled, first))
            acc += w * jsd_counts(first, second)
    return acc / denom


# --------------------------------------------------------------------------
# truth and sampling


def as_tuple(d: Dict[str, float]) -> Dist:
    return tuple(d[o] for o in OPTIONS)


def mix(a: Dist, b: Dist, w: float) -> Dist:
    """(1 - w)·a + w·b."""
    return tuple((1.0 - w) * x + w * y for x, y in zip(a, b))


def truth_for(rng: random.Random, cell: Dict) -> Tuple[List[Dist], List[Dist], List[Dist]]:
    sender, prior, post = [], [], []
    for _ in range(N_PROBES):
        a = as_tuple(_random_dist(rng, concentration=6.0))
        b = as_tuple(_random_dist(rng, concentration=1.2))
        if cell["kind"] == "grid":
            p = mix(b, a, cell["g"])
            q = mix(p, a, cell["lam"])
        elif cell["kind"] == "null":
            p, q = a, a
        else:
            w = as_tuple(_random_dist(rng, concentration=1.2))
            p, q = a, mix(a, w, ANTI_MU)
        sender.append(a)
        prior.append(p)
        post.append(q)
    return sender, prior, post


def multinomial(rng: random.Random, n: int, p: Sequence[float]) -> Counts:
    """Exact multinomial draw by conditional binomials."""
    out, left, mass = [], n, 1.0
    for i, pi in enumerate(p):
        if i == len(p) - 1 or left == 0:
            out.append(left)
            left = 0
            out.extend([0] * (len(p) - i - 1))
            break
        prob = min(1.0, max(0.0, pi / mass)) if mass > 0 else 0.0
        x = rng.binomialvariate(left, prob) if 0.0 < prob < 1.0 else (left if prob >= 1.0 else 0)
        out.append(x)
        left -= x
        mass -= pi
    return tuple(out)


# --------------------------------------------------------------------------
# estimators


def components(s: Sequence[Counts], p: Sequence[Counts], q: Sequence[Counts]) -> Dict[str, float]:
    """Mean over probes of D_prior, D_post and the two exact floors."""
    n = len(s)
    return {
        "d_prior": sum(jsd_counts(a, b) for a, b in zip(s, p)) / n,
        "d_post": sum(jsd_counts(a, b) for a, b in zip(s, q)) / n,
        "floor_prior": sum(exact_floor(a, b) for a, b in zip(s, p)) / n,
        "floor_post": sum(exact_floor(a, b) for a, b in zip(s, q)) / n,
    }


VARIANTS = ("V0", "V1", "V2")


def ratio_parts(c: Dict[str, float]) -> Dict[str, Tuple[float, float]]:
    """(numerator, denominator) for each registered variant."""
    m = c["d_prior"] - c["d_post"]
    return {
        "V0": (m, c["d_prior"] - c["floor_post"]),
        "V1": (m, c["d_prior"] - c["floor_prior"]),
        "V2": (m - c["floor_prior"] + c["floor_post"], c["d_prior"] - c["floor_prior"]),
    }


def fieller(m: float, g: float, vmm: float, vmg: float, vgg: float,
            z: float = Z) -> Tuple[str, Optional[float], Optional[float]]:
    """Fieller's set for m/g as a shape and two ends.

    Solves (m - r·g)^2 <= z^2 (vmm - 2 r vmg + r^2 vgg) for r. Returns
    ("bounded", lo, hi), ("rays", lo, hi) meaning (-inf, lo] u [hi, inf), or
    ("line", None, None). The set always contains m/g when g != 0.
    """
    a = g * g - z * z * vgg
    b = -2.0 * (m * g - z * z * vmg)
    c = m * m - z * z * vmm
    disc = b * b - 4.0 * a * c
    if a == 0:
        # Linear: b·r + c <= 0. Unreachable in the registered run, which needs
        # g^2 == z^2·vgg exactly in floats; handled so the shape is never wrong.
        if b > 0:
            return ("below", None, -c / b)
        if b < 0:
            return ("above", -c / b, None)
        return ("line", None, None) if c <= 0 else ("empty", None, None)
    if a > 0:
        root = math.sqrt(max(0.0, disc))
        return ("bounded", (-b - root) / (2 * a), (-b + root) / (2 * a))
    if disc <= 0:
        return ("line", None, None)
    root = math.sqrt(disc)
    lo, hi = sorted(((-b - root) / (2 * a), (-b + root) / (2 * a)))
    return ("rays", lo, hi)


def in_set(shape: Tuple[str, Optional[float], Optional[float]], r: float) -> bool:
    kind, lo, hi = shape
    if kind == "line":
        return True
    if kind == "empty":
        return False
    if kind == "bounded":
        return lo <= r <= hi
    if kind == "below":
        return r <= hi
    if kind == "above":
        return r >= lo
    return r <= lo or r >= hi


def _cov(xs: Sequence[float], ys: Sequence[float]) -> float:
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (len(xs) - 1)


def _percentile(sorted_xs: Sequence[float], q: float) -> float:
    i = min(len(sorted_xs) - 1, max(0, int(q * len(sorted_xs))))
    return sorted_xs[i]


# --------------------------------------------------------------------------
# one trial


def run_trial(cell: Dict, trial: int) -> Dict:
    rng = random.Random(1_000_003 * cell["index"] + trial)
    sender, prior, post = truth_for(rng, cell)
    n = cell["n"]
    t_prior = sum(jsd(a, b) for a, b in zip(sender, prior)) / N_PROBES
    t_post = sum(jsd(a, b) for a, b in zip(sender, post)) / N_PROBES
    t_move = t_prior - t_post
    t_f = t_move / t_prior if t_prior > 0 else None

    s = [multinomial(rng, n, d) for d in sender]
    p = [multinomial(rng, n, d) for d in prior]
    q = [multinomial(rng, n, d) for d in post]
    est = components(s, p, q)
    parts = ratio_parts(est)

    boot = {v: ([], []) for v in VARIANTS}
    boot_move: List[float] = []
    for _ in range(BOOT):
        bs = [multinomial(rng, n, [x / n for x in c]) for c in s]
        bp = [multinomial(rng, n, [x / n for x in c]) for c in p]
        bq = [multinomial(rng, n, [x / n for x in c]) for c in q]
        be = components(bs, bp, bq)
        for v, (m, g) in ratio_parts(be).items():
            boot[v][0].append(m)
            boot[v][1].append(g)
        boot_move.append(be["d_prior"] - be["d_post"])

    out: Dict = {"true_gap": t_prior, "true_move": t_move, "true_f": t_f, "variants": {}}
    for v in VARIANTS:
        m, g = parts[v]
        ms, gs = boot[v]
        shape = fieller(m, g, _cov(ms, ms), _cov(ms, gs), _cov(gs, gs))
        ratios = sorted(x / y for x, y in zip(ms, gs) if y > 0)
        reported = g > EPSILON
        point = min(1.0, m / g) if reported else None
        uncapped = (_percentile(ratios, 0.025), _percentile(ratios, 0.975)) if ratios else None
        capped = ((min(1.0, uncapped[0]), min(1.0, uncapped[1])) if uncapped else None)
        gsorted = sorted(gs)
        g_lo, g_hi = _percentile(gsorted, 0.025), _percentile(gsorted, 0.975)
        rec = {"reported": reported, "point": point, "g_hat": g,
               # Added after the registered run (see the results note): the
               # interval the plan's want-2 report puts beside the movement.
               "gap_pct": (g_lo, g_hi), "gap_basic": (2 * g - g_hi, 2 * g - g_lo),
               "at_cap": bool(reported and m / g >= 1.0),
               "fieller": shape[0],
               "fieller_width": (shape[2] - shape[1]) if shape[0] == "bounded" else None}
        if t_f is not None:
            rec.update({
                "cover_fieller": in_set(shape, t_f),
                "cover_pct_uncapped": bool(uncapped and uncapped[0] <= t_f <= uncapped[1]),
                "cover_pct_capped": bool(capped and capped[0] <= t_f <= capped[1]),
                "cover_present": bool(reported and capped and capped[0] <= t_f <= capped[1]),
                "error": (point - t_f) if reported else None,
                # Added after the registered run: the Fieller set is built
                # around m/g, not around the capped point.
                "error_uncapped": (m / g - t_f) if reported else None,
            })
        out["variants"][v] = rec
    moves = sorted(boot_move)
    lo, hi = _percentile(moves, 0.025), _percentile(moves, 0.975)
    out["move"] = {"estimate": est["d_prior"] - est["d_post"], "lo": lo, "hi": hi,
                   "cover": lo <= t_move <= hi,
                   "excludes_zero_away": hi < 0.0,
                   "excludes_zero": hi < 0.0 or lo > 0.0}
    return out


# --------------------------------------------------------------------------
# cells


def cells() -> List[Dict]:
    out, index = [], 0
    for n in NS:
        for g in GS:
            for lam in LAMS:
                out.append({"index": index, "n": n, "kind": "grid", "g": g, "lam": lam})
                index += 1
    for n in NS:
        for kind in ZERO_GAP:
            out.append({"index": index, "n": n, "kind": kind, "g": 1.0, "lam": None})
            index += 1
    return out


def _share(xs: Sequence[bool]) -> Optional[float]:
    return (sum(1 for x in xs if x) / len(xs)) if xs else None


def summarise(cell: Dict, trials: List[Dict]) -> Dict:
    out = dict(cell)
    out["trials"] = len(trials)
    out["true_gap_mean"] = statistics.fmean(t["true_gap"] for t in trials)
    defined = [t for t in trials if t["true_f"] is not None]
    out["true_f_mean"] = statistics.fmean(t["true_f"] for t in defined) if defined else None
    out["variants"] = {}
    for v in VARIANTS:
        recs = [t["variants"][v] for t in trials]
        drecs = [t["variants"][v] for t in defined]
        rep = [r for r in drecs if r["reported"]]
        errs = [r["error"] for r in rep]
        widths = sorted(r["fieller_width"] for r in recs if r["fieller_width"] is not None)
        out["variants"][v] = {
            "gate_pass": _share([r["reported"] for r in recs]),
            "fieller_bounded": _share([r["fieller"] == "bounded" for r in recs]),
            "fieller_rays": _share([r["fieller"] == "rays" for r in recs]),
            "fieller_line": _share([r["fieller"] == "line" for r in recs]),
            "fieller_bounded_median_width": (widths[len(widths) // 2] if widths else None),
            "cover_fieller": _share([r["cover_fieller"] for r in drecs]),
            "cover_pct_uncapped": _share([r["cover_pct_uncapped"] for r in drecs]),
            "cover_pct_capped": _share([r["cover_pct_capped"] for r in drecs]),
            "cover_present": _share([r["cover_present"] for r in drecs]),
            "cover_present_given_reported": _share([r["cover_pct_capped"] for r in rep]),
            "point_bias_given_reported": statistics.fmean(errs) if errs else None,
            "point_rmse_given_reported": (math.sqrt(statistics.fmean(e * e for e in errs))
                                          if errs else None),
            "at_cap_given_reported": _share([r["at_cap"] for r in rep]),
            # Added after the first registered run, to record a pattern seen in
            # it: the estimated gap itself. Every other field is unchanged.
            "g_hat_mean": statistics.fmean(r["g_hat"] for r in recs),
            "g_hat_negative": _share([r["g_hat"] < 0 for r in recs]),
            # Added after the registered run, with the fields in run_trial.
            "uncapped_bias_given_reported": (
                statistics.fmean(r["error_uncapped"] for r in rep) if rep else None),
            "fieller_half": _share([r["fieller"] in ("below", "above") for r in recs]),
            "gap_cover_pct": _share([t["variants"][v]["gap_pct"][0] <= t["true_gap"]
                                     <= t["variants"][v]["gap_pct"][1] for t in trials]),
            "gap_cover_basic": _share([t["variants"][v]["gap_basic"][0] <= t["true_gap"]
                                       <= t["variants"][v]["gap_basic"][1] for t in trials]),
            "gap_pct_above_zero": _share([t["variants"][v]["gap_pct"][0] > 0 for t in trials]),
            "gap_basic_above_zero": _share([t["variants"][v]["gap_basic"][0] > 0
                                            for t in trials]),
        }
    moves = [t["move"] for t in trials]
    out["move"] = {"cover": _share([m["cover"] for m in moves]),
                   "excludes_zero": _share([m["excludes_zero"] for m in moves]),
                   "excludes_zero_away": _share([m["excludes_zero_away"] for m in moves]),
                   "true_move_mean": statistics.fmean(t["true_move"] for t in trials)}
    return out


def run_cell(cell: Dict, trials: int = TRIALS) -> Dict:
    return summarise(cell, [run_trial(cell, i) for i in range(trials)])


# --------------------------------------------------------------------------
# predictions, scored exactly as registered


def score(summary: List[Dict]) -> Dict:
    grid = [c for c in summary if c["kind"] == "grid"]
    v0 = lambda c: c["variants"]["V0"]
    p1_fails = [(c["n"], c["g"], c["lam"], v0(c)["cover_fieller"])
                for c in grid if v0(c)["cover_fieller"] < 0.93]
    hi_g = [c for c in grid if c["g"] >= 0.9]
    capped_low = [(c["n"], c["g"], c["lam"]) for c in hi_g if v0(c)["cover_pct_capped"] < 0.93]
    uncapped_low = [(c["n"], c["g"], c["lam"]) for c in hi_g
                    if v0(c)["cover_pct_uncapped"] < 0.93]
    present_hi = [c for c in grid if c["g"] >= 0.95]
    p3 = []
    for n in NS:
        for lam in LAMS:
            at0 = next(c for c in grid if c["n"] == n and c["lam"] == lam and c["g"] == 0.0)
            at98 = next(c for c in grid if c["n"] == n and c["lam"] == lam and c["g"] == 0.98)
            p3.append((n, lam, v0(at0)["fieller_bounded"], v0(at98)["fieller_bounded"]))
    anti16 = next(c for c in summary if c["kind"] == "antinoophor" and c["n"] == 16)
    nulls = [c for c in summary if c["kind"] == "null"]
    return {
        "P1": {"holds": not p1_fails, "cells_below_0.93": p1_fails},
        "P2": {"holds": (bool(capped_low) and bool(uncapped_low)
                         and all(v0(c)["cover_present"] < 0.93 for c in present_hi)),
               "capped_percentile_below_0.93_at_g_ge_0.9": capped_low,
               "uncapped_percentile_below_0.93_at_g_ge_0.9": uncapped_low,
               "present_report_cover_at_g_ge_0.95":
                   [(c["n"], c["g"], c["lam"], v0(c)["cover_present"]) for c in present_hi]},
        "P3": {"holds": all(b98 < b0 and b98 < 0.5 for _, _, b0, b98 in p3),
               "bounded_share_g0_vs_g098": p3},
        "P4": {"holds": (anti16["move"]["excludes_zero_away"] >= 0.8
                         and all(c["move"]["excludes_zero"] <= 0.08 for c in nulls)),
               "antinoophor_n16_excludes_zero_away": anti16["move"]["excludes_zero_away"],
               "null_excludes_zero": [(c["n"], c["move"]["excludes_zero"]) for c in nulls]},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", help="write the full record here as JSON")
    ap.add_argument("--quick", action="store_true",
                    help="smoke run: 20 trials of 4 cells; not the registered run")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    args = ap.parse_args()

    todo = cells()
    trials = TRIALS
    if args.quick:
        todo, trials = [todo[0], todo[23], todo[-3], todo[-1]], 20
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        summary = list(pool.map(run_cell, todo, [trials] * len(todo)))
    record = {"plan": "research/2026-10-16-vanishing-gap-plan.md",
              "trials_per_cell": trials, "bootstrap": BOOT, "probes": N_PROBES,
              "epsilon": EPSILON, "z": Z, "quick": bool(args.quick),
              "cells": summary}
    if not args.quick:
        record["predictions"] = score(summary)
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    for c in summary:
        v = c["variants"]["V0"]
        print("n=%-2d %-11s g=%-4s lam=%-4s gap=%.4f pass=%.2f bounded=%.2f "
              "cover F=%s pct=%s present=%s move-cover=%.2f away=%.2f"
              % (c["n"], c["kind"], c["g"], c["lam"], c["true_gap_mean"], v["gate_pass"],
                 v["fieller_bounded"], _fmt(v["cover_fieller"]), _fmt(v["cover_pct_capped"]),
                 _fmt(v["cover_present"]), c["move"]["cover"], c["move"]["excludes_zero_away"]))
    return 0


def _fmt(x: Optional[float]) -> str:
    return "  - " if x is None else "%.2f" % x


if __name__ == "__main__":
    raise SystemExit(main())
