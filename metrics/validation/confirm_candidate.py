#!/usr/bin/env python3
"""The candidate F* report on a generator it was not chosen on.

Runs the confirmation registered in
research/2026-10-30-candidate-confirmation-plan.md, committed before this file.
The candidate is used exactly as frozen: ``bias_corrected.jsd_jk`` for each
probe's divergence, no floor, 400 draw-level bootstrap replicates resampled as
independent answers, Fieller's set for ``M/G`` and Wald intervals for ``M`` and
``G``. Only the generator is new: Dirichlet distributions, three or five options,
and answers within a probe that may persist from one to the next.

    python3 metrics/validation/confirm_candidate.py --out research/candidate-confirmation.json

Details the plan does not fix, settled while writing this file and before any
run: a trial's seed is ``7_000_003 * cell index + trial``; Dirichlet draws are
normalised gamma variates; a fresh draw under persistence may land on the
previous answer, and at ``rho = 0`` no repeat coin is tossed at all; a bootstrap
replicate redraws each party's counts on a probe as a multinomial from that
party's observed shares, which is resampling its answers independently.

Standard library only.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import random
import statistics
import sys
from typing import Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bias_corrected as bc  # noqa: E402
import vanishing_gap as vg  # noqa: E402

N_PROBES = 33
KS = (3, 5)
RHOS = (0.0, 0.3)
NS = (10, 16)
GS = (0.0, 0.8, 0.95)
LAMS = (0.25, 0.75)
ZERO_GAP = ("null", "antinoophor")
ALPHA_SENDER, ALPHA_DIFFUSE = 0.4, 1.5
ANTI_MU = 0.3
TRIALS = 400
BOOT = 400
Z = vg.Z

Dist = Tuple[float, ...]
Counts = Tuple[int, ...]


# --------------------------------------------------------------------------
# the new generator


def dirichlet(rng: random.Random, alpha: float, k: int) -> Dist:
    """A symmetric Dirichlet draw, by normalised gamma variates."""
    while True:
        x = [rng.gammavariate(alpha, 1.0) for _ in range(k)]
        total = sum(x)
        if total > 0:
            return tuple(v / total for v in x)


def truth_for(rng: random.Random, cell: Dict) -> Tuple[List[Dist], List[Dist], List[Dist]]:
    k = cell["k"]
    sender, prior, post = [], [], []
    for _ in range(N_PROBES):
        a = dirichlet(rng, ALPHA_SENDER, k)
        b = dirichlet(rng, ALPHA_DIFFUSE, k)
        if cell["kind"] == "grid":
            p = vg.mix(b, a, cell["g"])
            q = vg.mix(p, a, cell["lam"])
        elif cell["kind"] == "null":
            p, q = a, a
        else:
            w = dirichlet(rng, ALPHA_DIFFUSE, k)
            p, q = a, vg.mix(a, w, ANTI_MU)
        sender.append(a)
        prior.append(p)
        post.append(q)
    return sender, prior, post


def _categorical(rng: random.Random, p: Sequence[float]) -> int:
    u, acc = rng.random(), 0.0
    for i, pi in enumerate(p):
        acc += pi
        if u <= acc:
            return i
    return len(p) - 1


def persistent_answers(rng: random.Random, n: int, p: Sequence[float], rho: float) -> List[int]:
    """n answers whose marginal is p, each repeating the last with probability rho."""
    answers = [_categorical(rng, p)]
    for _ in range(n - 1):
        if rho > 0.0 and rng.random() < rho:
            answers.append(answers[-1])
        else:
            answers.append(_categorical(rng, p))
    return answers


def persistent_counts(rng: random.Random, n: int, p: Sequence[float], rho: float) -> Counts:
    counts = [0] * len(p)
    for a in persistent_answers(rng, n, p, rho):
        counts[a] += 1
    return tuple(counts)


# --------------------------------------------------------------------------
# one trial, the candidate exactly as frozen


def run_trial(cell: Dict, trial: int) -> Dict:
    # Both divergences are cached pure functions of the counts; at five options
    # the caches outgrow memory within a cell, so they start empty each trial.
    bc.jsd_jk.cache_clear()
    vg.jsd_counts.cache_clear()
    rng = random.Random(7_000_003 * cell["index"] + trial)
    sender, prior, post = truth_for(rng, cell)
    n, rho = cell["n"], cell["rho"]
    t_gap = sum(vg.jsd(a, b) for a, b in zip(sender, prior)) / N_PROBES
    t_post = sum(vg.jsd(a, b) for a, b in zip(sender, post)) / N_PROBES
    t_move = t_gap - t_post
    t_f = t_move / t_gap if t_gap > 0 else None

    s = [persistent_counts(rng, n, d, rho) for d in sender]
    p = [persistent_counts(rng, n, d, rho) for d in prior]
    q = [persistent_counts(rng, n, d, rho) for d in post]
    m, g = bc.corrected(bc.jsd_jk, s, p, q)

    ms: List[float] = []
    gs: List[float] = []
    for _ in range(BOOT):
        bs = [vg.multinomial(rng, n, [x / n for x in c]) for c in s]
        bp = [vg.multinomial(rng, n, [x / n for x in c]) for c in p]
        bq = [vg.multinomial(rng, n, [x / n for x in c]) for c in q]
        bm, bg = bc.corrected(bc.jsd_jk, bs, bp, bq)
        ms.append(bm)
        gs.append(bg)

    shape = vg.fieller(m, g, vg._cov(ms, ms), vg._cov(ms, gs), vg._cov(gs, gs))
    msd, gsd = statistics.stdev(ms), statistics.stdev(gs)
    rec = {
        "true_gap": t_gap, "true_move": t_move, "true_f": t_f,
        "g_hat": g, "m_hat": m,
        "fieller": shape[0],
        "fieller_width": (shape[2] - shape[1]) if shape[0] == "bounded" else None,
        "move_cover": m - Z * msd <= t_move <= m + Z * msd,
        "move_excludes_zero": m + Z * msd < 0 or m - Z * msd > 0,
        "move_excludes_zero_away": m + Z * msd < 0,
        "gap_cover": g - Z * gsd <= t_gap <= g + Z * gsd,
        "gap_above_zero": g - Z * gsd > 0,
        # Added after the registered run, to say whether a failing interval was
        # off-centre or too narrow: the bootstrap's spread, kept per trial.
        "m_boot_sd": msd, "g_boot_sd": gsd,
    }
    if t_f is not None:
        rec["cover_fieller"] = vg.in_set(shape, t_f)
    return rec


# --------------------------------------------------------------------------
# cells, summaries and the registered predictions


def cells() -> List[Dict]:
    out, index = [], 0
    for k in KS:
        for rho in RHOS:
            for n in NS:
                for g in GS:
                    for lam in LAMS:
                        out.append({"index": index, "k": k, "rho": rho, "n": n,
                                    "kind": "grid", "g": g, "lam": lam})
                        index += 1
    for k in KS:
        for rho in RHOS:
            for n in NS:
                for kind in ZERO_GAP:
                    out.append({"index": index, "k": k, "rho": rho, "n": n,
                                "kind": kind, "g": 1.0, "lam": None})
                    index += 1
    return out


def _share(xs) -> Optional[float]:
    xs = list(xs)
    return sum(1 for x in xs if x) / len(xs) if xs else None


def summarise(cell: Dict, trials: List[Dict]) -> Dict:
    out = dict(cell)
    out["trials"] = len(trials)
    out["true_gap_mean"] = statistics.fmean(t["true_gap"] for t in trials)
    defined = [t for t in trials if t["true_f"] is not None]
    widths = sorted(t["fieller_width"] for t in trials if t["fieller_width"] is not None)
    out.update({
        "cover_fieller": _share(t["cover_fieller"] for t in defined) if defined else None,
        "fieller_bounded": _share(t["fieller"] == "bounded" for t in trials),
        "fieller_bounded_median_width": widths[len(widths) // 2] if widths else None,
        "move_cover": _share(t["move_cover"] for t in trials),
        "move_excludes_zero": _share(t["move_excludes_zero"] for t in trials),
        "move_excludes_zero_away": _share(t["move_excludes_zero_away"] for t in trials),
        "gap_cover": _share(t["gap_cover"] for t in trials),
        "gap_above_zero": _share(t["gap_above_zero"] for t in trials),
        "g_error_mean": statistics.fmean(t["g_hat"] - t["true_gap"] for t in trials),
    })
    # Added after the registered run: the errors' actual spread across trials
    # beside the bootstrap's mean estimate of it, and the true movement's size.
    out.update({
        "true_move_mean": statistics.fmean(t["true_move"] for t in trials),
        "m_error_mean": statistics.fmean(t["m_hat"] - t["true_move"] for t in trials),
        "m_error_sd": statistics.stdev(t["m_hat"] - t["true_move"] for t in trials),
        "g_error_sd": statistics.stdev(t["g_hat"] - t["true_gap"] for t in trials),
        "m_boot_sd_mean": statistics.fmean(t["m_boot_sd"] for t in trials),
        "g_boot_sd_mean": statistics.fmean(t["g_boot_sd"] for t in trials),
    })
    return out


def run_cell(cell: Dict, trials: int = TRIALS) -> Dict:
    return summarise(cell, [run_trial(cell, i) for i in range(trials)])


def score(summary: List[Dict]) -> Dict:
    ind = [c for c in summary if c["rho"] == 0.0]
    dep = [c for c in summary if c["rho"] == 0.3]
    grid0 = [c for c in ind if c["kind"] == "grid"]
    grid3 = [c for c in dep if c["kind"] == "grid"]
    key = lambda c: (c["k"], c["n"], c["g"], c["lam"])
    c1 = [key(c) + (c["cover_fieller"],) for c in grid0 if c["cover_fieller"] < 0.93]
    c2_grid = [key(c) + (c["move_cover"],) for c in grid0 if c["move_cover"] < 0.93]
    c2_anti = [(c["k"], c["move_excludes_zero_away"]) for c in ind
               if c["kind"] == "antinoophor" and c["n"] == 16]
    c2_null = [(c["k"], c["n"], c["move_excludes_zero"]) for c in ind if c["kind"] == "null"]
    c3_grid = [key(c) + (c["gap_cover"],) for c in grid0 if c["gap_cover"] < 0.90]
    c3_null = [(c["k"], c["n"], c["gap_above_zero"]) for c in ind if c["kind"] == "null"]
    c4_low = [key(c) + (c["cover_fieller"],) for c in grid3 if c["cover_fieller"] < 0.93]
    c5 = [key(c) + (c["fieller_bounded"],) for c in grid0 if c["g"] == 0.95]
    return {
        "C1": {"holds": not c1, "cells_below_0.93": c1},
        "C2": {"holds": (not c2_grid and all(x >= 0.80 for _, x in c2_anti)
                         and all(x <= 0.08 for _, _, x in c2_null)),
               "grid_cells_below_0.93": c2_grid,
               "antinoophor_n16_excludes_zero_away": c2_anti,
               "null_excludes_zero": c2_null},
        "C3": {"holds": not c3_grid and all(x <= 0.10 for _, _, x in c3_null),
               "grid_cells_below_0.90": c3_grid, "null_gap_above_zero": c3_null},
        "C4": {"holds": len(c4_low) * 2 >= len(grid3),
               "dependent_cells_below_0.93": len(c4_low), "of": len(grid3),
               "cells": c4_low},
        "C5": {"holds": all(x < 0.5 for *_, x in c5), "bounded_share_at_g_0.95": c5},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", help="write the full record here as JSON")
    ap.add_argument("--quick", action="store_true",
                    help="smoke run: 20 trials of 4 cells; not the registered run")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    args = ap.parse_args()

    todo, trials = cells(), TRIALS
    if args.quick:
        todo, trials = [todo[0], todo[23], todo[47], todo[-1]], 20
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        summary = list(pool.map(run_cell, todo, [trials] * len(todo)))
    record = {"plan": "research/2026-10-30-candidate-confirmation-plan.md",
              "trials_per_cell": trials, "bootstrap": BOOT, "probes": N_PROBES,
              "z": Z, "alpha_sender": ALPHA_SENDER, "alpha_diffuse": ALPHA_DIFFUSE,
              "quick": bool(args.quick), "cells": summary}
    if not args.quick:
        record["predictions"] = score(summary)
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    for c in summary:
        print("K=%d rho=%.1f n=%-2d %-11s g=%-4s lam=%-4s | Fieller %s bounded %.3f | "
              "move %.3f | gap %.3f above0 %.3f" % (
                  c["k"], c["rho"], c["n"], c["kind"], c["g"], c["lam"],
                  "  -  " if c["cover_fieller"] is None else "%.3f" % c["cover_fieller"],
                  c["fieller_bounded"], c["move_cover"], c["gap_cover"], c["gap_above_zero"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
