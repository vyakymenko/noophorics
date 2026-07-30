#!/usr/bin/env python3
"""E-004 -- does cross-model disagreement locate errors without a key?

Runs the design pre-registered in PREREGISTRATION.md. Read that first.

    python3 runner.py --dry-run
    python3 runner.py --models gpt-oss:120b,qwen3.5:35b --provider ollama

There is no transfer in this experiment and no message. Every model answers
every probe from the source specification alone, and the detector is a modal
comparison between two models -- no key, no threshold, no tuning. The
observation that motivated it was made with exactly that, and a better detector
would be a different hypothesis.
"""

from __future__ import annotations

import argparse
import collections
import itertools
import json
import math
import os
import random
import statistics
import sys
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "metrics"))

from noophorics import (  # noqa: E402
    ProbeMeasure, bootstrap_ci, holm_adjust, load_probe_measure, to_distribution,
)
from noophorics.ollama_agent import OllamaAgent, ollama_available  # noqa: E402

SEED = 20260731
BOOTSTRAP = 5_000
ACCURACY_GATE = 0.60
MIN_ERRORS_PER_MODEL = 2
MIN_TOTAL_ERRORS = 12
OLLAMA_THINK = "medium"
OLLAMA_TEMPERATURE = 0.7

MEASURES = {
    "MERIDIAN-33": ("experiments/E-002-phantom-agreement/probes.json",
                    "experiments/E-001-fluency-cost/source-spec.md"),
    "RIVERSIDE-30": ("probes/riverside-30/probes.json",
                     "probes/riverside-30/source-spec.md"),
}


def mode(draws: Sequence[str]) -> str:
    d = to_distribution(draws)
    return max(sorted(d), key=lambda k: d[k])


def hypergeom_sf(k: int, N: int, K: int, n: int) -> float:
    """P(X >= k) for X ~ Hypergeometric(N, K, n). Exact, stdlib only.

    N probes, K of them errors, n flagged; k of the flagged are errors.
    """
    total = math.comb(N, n)
    if total == 0:
        return 1.0
    return sum(math.comb(K, i) * math.comb(N - K, n - i)
               for i in range(k, min(K, n) + 1)
               if 0 <= n - i <= N - K) / total


def fisher_combine(pvalues: Sequence[float]) -> Tuple[float, float]:
    """Fisher's method. Returns (chi2, p). Survival of chi2 by series, no scipy.

    Verified against an independent analytic computation: two independent
    p = 0.05 give chi2 = 11.9829 on df = 4 and a combined p = 0.017479, which
    is what the closed form for even df returns. A first verification note put
    the expected value at 0.1991, which was simply wrong -- the code was right
    and the check was not, and it took recomputing the closed form from scratch
    to tell which. Null sanity: two p = 0.50 combine to 0.5966.
    """
    ps = [max(p, 1e-12) for p in pvalues]
    chi2 = -2.0 * sum(math.log(p) for p in ps)
    df = 2 * len(ps)
    # P(chi2_df > x) for even df has a closed form.
    k = df // 2
    x = chi2 / 2.0
    term, total = 1.0, 1.0
    for i in range(1, k):
        term *= x / i
        total += term
    return chi2, min(1.0, math.exp(-x) * total)


class Cache:
    def __init__(self, path: Optional[str]):
        self.path, self._d = path, {}
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                self._d = json.load(fh)

    def get(self, cond: str, pid: str, n: int):
        got = self._d.get(cond, {}).get(pid)
        return list(got) if got is not None and len(got) == n else None

    def put(self, cond: str, pid: str, draws: Sequence[str]) -> None:
        self._d.setdefault(cond, {})[pid] = list(draws)
        if self.path:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self._d, fh)
            os.replace(tmp, self.path)


class Stub:
    """Dry-run stand-in. Each model errs on its own probes, so the analysis runs."""

    def __init__(self, name: str, seed: int, error_ids: Sequence[str]):
        self.name, self._errs = name, set(error_ids)
        self._rng = random.Random(seed)

    def answer_samples(self, probe, n: int) -> List[str]:
        wrong = [o for o in probe.options if o != probe.key]
        target = self._rng.choice(wrong) if probe.id in self._errs else probe.key
        return [target if self._rng.random() < 0.9
                else self._rng.choice(probe.options) for _ in range(n)]


def collect(agent, measure: ProbeMeasure, n: int, cond: str, cache: Cache,
            progress: Dict[str, int]) -> Dict[str, List[str]]:
    out = {}
    for probe in measure:
        got = cache.get(cond, probe.id, n)
        if got is None:
            got = agent.answer_samples(probe, n)
            cache.put(cond, probe.id, got)
        out[probe.id] = got
        progress["done"] += 1
        sys.stderr.write("\r  %-44s %d/%d" % (cond[:44], progress["done"],
                                              progress["total"]))
        sys.stderr.flush()
    return out


def analyse(modes: Dict[str, Dict[str, Dict[str, str]]],
            measures: Dict[str, ProbeMeasure]) -> Dict[str, Any]:
    """modes[measure][model][probe_id] -> modal answer."""
    models = sorted({m for mm in modes.values() for m in mm})
    cells: List[Dict[str, Any]] = []
    accuracy: Dict[str, Dict[str, float]] = {}
    errors: Dict[str, Dict[str, List[str]]] = {}

    for mname, measure in measures.items():
        keys = {p.id: p.key for p in measure}
        ids = list(keys)
        accuracy[mname] = {}
        errors[mname] = {}
        for model in modes.get(mname, {}):
            wrong = [i for i in ids if modes[mname][model][i] != keys[i]]
            errors[mname][model] = wrong
            accuracy[mname][model] = 1.0 - len(wrong) / len(ids)

        for a, b in itertools.combinations(sorted(modes.get(mname, {})), 2):
            flagged = [i for i in ids if modes[mname][a][i] != modes[mname][b][i]]
            err = set(errors[mname][a]) | set(errors[mname][b])
            hit = [i for i in flagged if i in err]
            N, K, n = len(ids), len(err), len(flagged)
            p = hypergeom_sf(len(hit), N, K, n) if (K and n) else 1.0
            # H3: does the flag set contain an error from EACH member?
            from_a = [i for i in flagged if i in errors[mname][a]]
            from_b = [i for i in flagged if i in errors[mname][b]]
            both_wrong_somewhere = bool(errors[mname][a] and errors[mname][b])
            cells.append({
                "measure": mname, "pair": [a, b],
                "n_probes": N, "n_errors": K, "n_flagged": n,
                "hits": len(hit), "flagged_ids": flagged,
                "errors_a": errors[mname][a], "errors_b": errors[mname][b],
                "recall": (len(hit) / K) if K else None,
                "precision": (len(hit) / n) if n else None,
                "p_hypergeom": p,
                "h3_applicable": both_wrong_somewhere,
                "h3_symmetric": bool(from_a and from_b) if both_wrong_somewhere else None,
                "unflagged_errors": sorted(err - set(flagged)),
            })

    live = [c for c in cells if c["n_errors"] > 0]
    effects: Dict[str, Any] = {}

    if live:
        chi2, p1 = fisher_combine([c["p_hypergeom"] for c in live])
        effects["H1_detector_beats_chance"] = {
            "value": statistics.mean([c["recall"] for c in live if c["recall"] is not None]),
            "fisher_chi2": chi2, "p_value": p1, "n_cells": len(live),
            "note": "value is mean recall; the test is Fisher over per-cell "
                    "hypergeometric p-values",
        }
        # H2: P(error | flagged) vs P(error | not flagged), per cell then bootstrapped
        diffs = []
        for c in live:
            n_un = c["n_probes"] - c["n_flagged"]
            p_f = (c["hits"] / c["n_flagged"]) if c["n_flagged"] else 0.0
            p_u = (len(c["unflagged_errors"]) / n_un) if n_un else 0.0
            diffs.append(p_f - p_u)
        if len(diffs) >= 2:
            v, lo, hi = bootstrap_ci(diffs, resamples=BOOTSTRAP, seed=SEED)
            effects["H2_precision_above_base_rate"] = {
                "value": v, "ci95": [lo, hi], "p_value": None,
                "supported": bool(lo > 0.0),
            }
        applicable = [c for c in live if c["h3_applicable"]]
        effects["H3_symmetry"] = {
            "applicable_cells": len(applicable),
            "symmetric_cells": sum(1 for c in applicable if c["h3_symmetric"]),
            "excluded_cells": [c["pair"] + [c["measure"]] for c in live
                               if not c["h3_applicable"]],
            "note": "cells where one model made no errors are EXCLUDED, not "
                    "counted as passes",
            "supported": bool(applicable) and all(c["h3_symmetric"] for c in applicable),
        }
        fam = {k: v["p_value"] for k, v in effects.items()
               if v.get("p_value") is not None}
        for name, adj in holm_adjust(fam).items():
            effects[name]["p_value_holm"] = adj
            effects[name]["significant_at_005"] = bool(adj < 0.05)

    gates = {
        "accuracy": {"per_model": accuracy,
                     "passed": all(a > ACCURACY_GATE
                                   for mm in accuracy.values() for a in mm.values())},
        "each_model_wrong_twice": {
            "per_model": {m: max((len(errors[mn].get(m, [])) for mn in errors),
                                 default=0) for m in models},
            "threshold": MIN_ERRORS_PER_MODEL,
        },
        "total_errors": {"value": sum(len(v) for mm in errors.values()
                                      for v in mm.values()),
                         "threshold": MIN_TOTAL_ERRORS},
    }
    gates["each_model_wrong_twice"]["passed"] = all(
        v >= MIN_ERRORS_PER_MODEL
        for v in gates["each_model_wrong_twice"]["per_model"].values())
    gates["total_errors"]["passed"] = \
        gates["total_errors"]["value"] >= MIN_TOTAL_ERRORS

    out = {"cells": cells, "accuracy": accuracy, "errors": errors,
           "effects": effects, "gates": gates}
    if not gates["each_model_wrong_twice"]["passed"]:
        out["void"] = True
        out["void_reason"] = (
            "a model made fewer than %d errors anywhere: %s. A design in which "
            "one model is never wrong reproduces the one-sidedness that makes "
            "the motivating observation unusable, and reporting it would be "
            "reporting the defect as the result."
            % (MIN_ERRORS_PER_MODEL,
               gates["each_model_wrong_twice"]["per_model"]))
    return out


def run(args) -> Dict[str, Any]:
    measures, specs = {}, {}
    for name, (ppath, spath) in MEASURES.items():
        measures[name] = load_probe_measure(os.path.join(REPO, ppath))
        with open(os.path.join(REPO, spath), "r", encoding="utf-8") as fh:
            specs[name] = fh.read()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    cache = Cache(args.cache)
    total = sum(len(m) for m in measures.values()) * len(models)
    progress = {"done": 0, "total": total}

    print("\nE-004  Disagreement as a keyless error detector")
    for n, m in measures.items():
        print("  %-14s %d probes, %d distinct answer spaces"
              % (n, len(m), len({tuple(sorted(p.options)) for p in m})))
    print("  models   : %s" % ", ".join(models))
    print("  draws    : n=%d\n" % args.samples)

    modes: Dict[str, Dict[str, Dict[str, str]]] = {}
    for mname, measure in measures.items():
        modes[mname] = {}
        for i, model in enumerate(models):
            if args.provider == "ollama":
                agent = OllamaAgent(model, specs[mname], model=model,
                                    think=OLLAMA_THINK,
                                    temperature=OLLAMA_TEMPERATURE)
            else:
                # Dry run: give each model its own error set so H3 is exercised.
                ids = [p.id for p in measure]
                agent = Stub(model, 100 + i, ids[i::len(models)][:3])
            draws = collect(agent, measure, args.samples,
                            "%s@%s" % (mname, model), cache, progress)
            modes[mname][model] = {pid: mode(d) for pid, d in draws.items()}
    sys.stderr.write("\n\n")

    results: Dict[str, Any] = {
        "experiment": "E-004", "core_version": "0.4",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dry_run": bool(args.provider != "ollama"),
        "measures": {n: m.qualified_id for n, m in measures.items()},
        "models": models, "samples_per_probe": args.samples,
        "detector": "flag probe iff mode X != mode Y; no key, no threshold",
        "modal_answers": modes,
    }
    results.update(analyse(modes, measures))
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="E-004 disagreement detector")
    ap.add_argument("--provider", choices=("ollama", "dry"), default="dry")
    ap.add_argument("--models", default="gpt-oss:120b,qwen3.5:35b")
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--cache", default=os.path.join(HERE, "sample-cache.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    args = ap.parse_args()

    if args.provider == "ollama" and not ollama_available():
        print("ollama is not reachable", file=sys.stderr)
        return 2

    results = run(args)
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "E-004-%s%s.json"
                        % (time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()),
                           "-dryrun" if results.get("dry_run") else ""))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)

    print("  measure       pair                        err  flag  hit  recall  prec   p")
    for c in results["cells"]:
        print("  %-13s %-27s %3d %5d %4d  %s  %s  %.4f"
              % (c["measure"], "+".join(x[:12] for x in c["pair"]),
                 c["n_errors"], c["n_flagged"], c["hits"],
                 ("%.2f" % c["recall"]) if c["recall"] is not None else "  - ",
                 ("%.2f" % c["precision"]) if c["precision"] is not None else "  - ",
                 c["p_hypergeom"]))
    if results.get("void"):
        print("\nVOID: %s" % results["void_reason"])
    else:
        print()
        for name, e in sorted(results["effects"].items()):
            if "value" in e:
                print("  %-34s %+7.4f  %s" % (name, e["value"],
                      ("p(holm)=%.4f" % e["p_value_holm"]) if e.get("p_value_holm")
                      else ("CI [%.3f, %.3f]" % tuple(e["ci95"]) if e.get("ci95") else "")))
            else:
                print("  %-34s %d/%d applicable cells symmetric"
                      % (name, e.get("symmetric_cells", 0), e.get("applicable_cells", 0)))
        failed = [g for g, v in results["gates"].items() if not v.get("passed")]
        print("\n  gates failed: %s" % (", ".join(failed) if failed else "none"))
    print("\nwrote %s" % path)
    if results.get("dry_run"):
        print("DRY RUN -- synthetic, no scientific weight.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
