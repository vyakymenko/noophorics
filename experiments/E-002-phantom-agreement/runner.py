#!/usr/bin/env python3
"""E-002 -- the first measurement of Phi in this repository, elicited per probe.

Runs the design pre-registered in PREREGISTRATION.md. Read that first: the
hypotheses and the analysis plan are fixed and the amendment budget is one.

    python3 runner.py --dry-run                 # full pipeline, synthetic
    python3 runner.py --provider ollama --k 8   # real run

Three lessons from the void runs are wired into the structure rather than left
to discipline:

- Gates are evaluated at the earliest point their inputs exist. E-001b spent a
  restart discovering a gate failure that was decidable from the composed
  messages (../E-001b-fluency-factorial/VOID.md).
- Messages are persisted the moment they exist, and cached draws are keyed by
  the message they answered. Composition is stochastic, so a re-composed brief
  wearing the same label is a different condition (DEFECT-001.md).
- The analysis path runs in --dry-run. E-001b's did not, and called a function
  that was never defined.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import statistics
import sys
import time
from typing import Any, Dict, List, Optional, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "metrics"))

from noophorics import (  # noqa: E402
    ProbeMeasure,
    agreement_rate,
    bootstrap_ci,
    goodman_kruskal_gamma,
    holm_adjust,
    load_probe_measure,
    mean_divergence,
    mean_permutation_floor,
    permutation_diff,
    point_biserial,
    to_distribution,
    transfer_fidelity,
)
from noophorics.decomposition import decompose  # noqa: E402
from noophorics.ollama_agent import OllamaAgent, ollama_available  # noqa: E402

SEED = 20260729
FLOOR_PERMUTATIONS = 300
PERMUTATIONS = 10_000
BOOTSTRAP = 5_000
SENDER_ACCURACY_GATE = 0.90
SENDER_MAX_ERRORS = 2
CEILING_GATE = 0.70
EPSILON = 0.02
OLLAMA_THINK = "medium"
OLLAMA_TEMPERATURE = 0.7

# One neutral instruction. E-002 does not manipulate style -- that is E-001c's
# job, and mixing the two is what made E-001 uninterpretable.
COMPOSE_PROMPT = """You are holding a set of submission-handling rules. A \
colleague who has never seen those rules, and never will, has to decide real \
cases with them. The note you are about to write is the only thing they will \
have: they cannot ask you anything afterwards, they cannot look at the source, \
and the verdicts they issue are final.

Write the note. Cover what the scheme is for and what each rule requires, so \
your colleague can decide cases they have not seen. Write between 180 and 260 \
words. Output the note and nothing else: no preamble, no sign-off."""


def fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]


# --------------------------------------------------------------------------


class Cache:
    """Tracked, resumable. Keyed by model, condition and probe."""

    def __init__(self, path: Optional[str]):
        self.path = path
        self._data: Dict[str, Dict[str, Any]] = {}
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                self._data = json.load(fh)

    def get(self, cond: str, probe_id: str, n: int) -> Optional[List[Any]]:
        got = self._data.get(cond, {}).get(probe_id)
        return list(got) if got is not None and len(got) == n else None

    def put(self, cond: str, probe_id: str, samples: Sequence[Any]) -> None:
        self._data.setdefault(cond, {})[probe_id] = list(samples)
        if self.path:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh)
            os.replace(tmp, self.path)

    def seed_from(self, other_path: str, conditions: Sequence[str],
                  probe_ids: Sequence[str]) -> Dict[str, int]:
        """Import message-independent conditions from another experiment's cache.

        `sender`, `PRIOR` and `CEILING` are conditioned on the source spec or on
        nothing, so no brief can invalidate them. Reuse is recorded in the
        results rather than hidden: the donor cache is committed, and a reader
        can check that these draws predate this run.
        """
        imported: Dict[str, int] = {}
        if not os.path.exists(other_path):
            return imported
        with open(other_path, "r", encoding="utf-8") as fh:
            donor = json.load(fh)
        wanted = set(probe_ids)
        for cond in conditions:
            if cond not in donor:
                continue
            rows = {p: v for p, v in donor[cond].items() if p in wanted}
            if len(rows) == len(wanted):
                self._data.setdefault(cond, {}).update(rows)
                imported[cond] = len(rows)
        if imported and self.path:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh)
        return imported


class Stub:
    """Dry-run stand-in. Synthetic, and the results file says so."""

    def __init__(self, name: str, accuracy: float, claim_rate: float, seed: int):
        self.name, self._acc, self._claim = name, accuracy, claim_rate
        self._rng = random.Random(seed)

    def answer_samples(self, probe, n: int) -> List[str]:
        wrong = [o for o in probe.options if o != probe.key]
        return [probe.key if self._rng.random() < self._acc
                else self._rng.choice(wrong) for _ in range(n)]

    def claim_per_probe(self, probe, counterpart, artifact=None,
                        n_elicitations: int = 5) -> List[bool]:
        return [self._rng.random() < self._claim for _ in range(n_elicitations)]

    def compose(self, prompt: str, seed: int = 0) -> str:
        return "synthetic brief %d %s" % (seed, "word " * 200)

    def cost_of(self, message: str) -> int:
        return max(1, len(message.split()))


def make_agent(provider: str, name: str, context: str, model: str, seed: int):
    if provider == "ollama":
        return OllamaAgent(name, context, model=model, think=OLLAMA_THINK,
                           temperature=OLLAMA_TEMPERATURE)
    return Stub(name, 0.94 if context else 0.45, 0.8, seed)


def collect(agent, measure: ProbeMeasure, n: int, cond: str, cache: Cache,
            progress: Dict[str, int]) -> List[List[str]]:
    rows: List[List[str]] = []
    for probe in measure:
        got = cache.get(cond, probe.id, n)
        if got is None:
            got = agent.answer_samples(probe, n)
            cache.put(cond, probe.id, got)
        rows.append(got)
        progress["done"] += 1
        sys.stderr.write("\r  %-34s %d/%d" % (cond[:34], progress["done"],
                                              progress["total"]))
        sys.stderr.flush()
    return rows


def elicit(agent, measure: ProbeMeasure, counterpart: str, artifact: Optional[str],
           n_c: int, cond: str, cache: Cache) -> List[float]:
    """Per-probe claims, averaged over n_c binary draws. Raw draws are cached."""
    out: List[float] = []
    for probe in measure:
        got = cache.get(cond, probe.id, n_c)
        if got is None:
            got = agent.claim_per_probe(probe, counterpart, artifact=artifact,
                                        n_elicitations=n_c)
            cache.put(cond, probe.id, got)
        out.append(sum(1.0 for x in got if x) / len(got))
    return out


# --------------------------------------------------------------------------
# analysis -- pure over the collected draws, no live calls


def analyse(measure: ProbeMeasure, raw: Dict[str, List[List[str]]],
            claims: Dict[str, Dict[str, List[float]]],
            costs: Dict[str, float], epsilon: float) -> Dict[str, Any]:
    s_dists = [to_distribution(d) for d in raw["sender"]]
    p_dists = [to_distribution(d) for d in raw["PRIOR"]]
    d_prior = mean_divergence(s_dists, p_dists, measure.weights)
    floor = mean_permutation_floor(raw["sender"], raw["PRIOR"], measure.weights,
                                   FLOOR_PERMUTATIONS, SEED)
    s_modes = [max(sorted(d), key=lambda x: d[x]) for d in s_dists]

    briefs = sorted(k for k in raw if k not in ("sender", "PRIOR", "CEILING"))
    per_brief: Dict[str, Any] = {}
    for label in briefs:
        post = raw[label]
        r_dists = [to_distribution(d) for d in post]
        r_modes = [max(sorted(d), key=lambda x: d[x]) for d in r_dists]
        # The outcome each per-probe claim is a prediction about.
        observed = [1.0 if a == b else 0.0 for a, b in zip(s_modes, r_modes)]
        cs = claims[label]["sender"]
        cr = claims[label]["receiver"]
        pooled = [(a + b) / 2.0 for a, b in zip(cs, cr)]
        dec = decompose(measure, raw["sender"], raw["PRIOR"], post)
        per_brief[label] = {
            "d_post": mean_divergence(s_dists, r_dists, measure.weights),
            "fidelity": transfer_fidelity(
                d_prior, mean_divergence(s_dists, r_dists, measure.weights),
                floor, epsilon),
            "fidelity_where_sender_right": dec.fidelity_where_sender_right,
            "error_replication": dec.error_replication,
            "agreement_observed": agreement_rate(s_dists, r_dists, measure.weights),
            "observed_per_probe": observed,
            "claims_sender": cs, "claims_receiver": cr,
            "cost_tokens": costs[label],
            # bias, per party and pooled
            "phi_sender": statistics.mean(cs) - statistics.mean(observed),
            "phi_receiver": statistics.mean(cr) - statistics.mean(observed),
            "phi": statistics.mean(pooled) - statistics.mean(observed),
            # resolution
            "resolution_sender": point_biserial(cs, observed),
            "resolution_receiver": point_biserial(cr, observed),
            "gamma_sender": goodman_kruskal_gamma(cs, observed),
            "gamma_receiver": goodman_kruskal_gamma(cr, observed),
        }
        # conditional asymmetry, Keysar & Henly's headline
        for who, cl in (("sender", cs), ("receiver", cr)):
            diverged = [c for c, o in zip(cl, observed) if o == 0.0]
            matched = [c for c, o in zip(cl, observed) if o == 1.0]
            per_brief[label]["overestimation_%s" % who] = (
                statistics.mean(diverged) if diverged else None)
            per_brief[label]["underestimation_%s" % who] = (
                1.0 - statistics.mean(matched) if matched else None)

    def unit(field: str) -> List[float]:
        return [per_brief[b][field] for b in briefs
                if per_brief[b][field] is not None]

    effects: Dict[str, Any] = {}

    # H1 -- bias positive
    phi, lo, hi = bootstrap_ci(unit("phi"), resamples=BOOTSTRAP, seed=SEED)
    _, p1 = permutation_diff(unit("phi"), [0.0] * len(briefs),
                             permutations=PERMUTATIONS, seed=SEED)
    effects["H1_bias_positive"] = {
        "phi": phi, "ci95": [lo, hi], "p_value": p1,
        "direction_predicted": "positive",
        "supported": bool(lo > 0.0),
    }

    # H2 -- resolution above chance
    res, rlo, rhi = bootstrap_ci(
        unit("resolution_sender") + unit("resolution_receiver"),
        resamples=BOOTSTRAP, seed=SEED)
    _, p2 = permutation_diff(
        unit("resolution_sender") + unit("resolution_receiver"),
        [0.0] * (2 * len(briefs)), permutations=PERMUTATIONS, seed=SEED)
    effects["H2_resolution_above_chance"] = {
        "resolution": res, "ci95": [rlo, rhi], "p_value": p2,
        "gamma": statistics.mean(unit("gamma_sender") + unit("gamma_receiver")),
        "supported": bool(rlo > 0.0),
    }

    # H3 -- conditional asymmetry
    over = unit("overestimation_sender") + unit("overestimation_receiver")
    under = unit("underestimation_sender") + unit("underestimation_receiver")
    if over and under:
        obs3, p3 = permutation_diff(over, under, permutations=PERMUTATIONS,
                                    seed=SEED)
        _, alo, ahi = bootstrap_ci([o - u for o, u in zip(over, under)],
                                   resamples=BOOTSTRAP, seed=SEED)
        effects["H3_conditional_asymmetry"] = {
            "overestimation_rate": statistics.mean(over),
            "underestimation_rate": statistics.mean(under),
            "difference": obs3, "ci95": [alo, ahi], "p_value": p3,
            "supported": bool(alo > 0.0),
            "human_reference": {"source": "Keysar & Henly 2002",
                                "overestimation": 0.46, "underestimation": 0.12},
        }
    else:
        effects["H3_conditional_asymmetry"] = {
            "uncomputable": "every probe fell on one side; no conditional rates"}

    # H4 -- sender worse calibrated than receiver
    obs4, p4 = permutation_diff(unit("phi_sender"), unit("phi_receiver"),
                                permutations=PERMUTATIONS, seed=SEED)
    _, dlo, dhi = bootstrap_ci(
        [per_brief[b]["phi_sender"] - per_brief[b]["phi_receiver"] for b in briefs],
        resamples=BOOTSTRAP, seed=SEED)
    effects["H4_sender_worse_than_receiver"] = {
        "phi_sender": statistics.mean(unit("phi_sender")),
        "phi_receiver": statistics.mean(unit("phi_receiver")),
        "difference": obs4, "ci95": [dlo, dhi], "p_value": p4,
        "supported": bool(dlo > 0.0),
    }

    # One family, one dataset, one instrument: Holm.
    adjusted = holm_adjust({k: v["p_value"] for k, v in effects.items()
                            if "p_value" in v})
    for name, p_adj in adjusted.items():
        effects[name]["p_value_holm"] = p_adj
        effects[name]["significant_at_005"] = bool(p_adj < 0.05)

    return {
        "d_prior": d_prior, "d_floor": floor,
        "admissible": bool((d_prior - floor) > epsilon),
        "sender_accuracy": measure.accuracy(s_modes),
        "sender_errors": [p.id for p, m in zip(measure, s_modes) if m != p.key],
        "per_brief": per_brief, "effects": effects,
        "multiplicity": {"family": sorted(adjusted), "correction": "holm",
                         "rationale": "four claims about one instrument on one "
                                      "dataset are one family"},
    }


# --------------------------------------------------------------------------


def run(args) -> Dict[str, Any]:
    measure = load_probe_measure(os.path.join(HERE, "probes.json"))
    probe_ids = [p.id for p in measure]
    cache = Cache(args.cache)

    print("\nE-002  Phantom agreement, per probe")
    print("measure   : %s (%d probes)" % (measure.qualified_id, len(measure)))
    print("design    : k=%d briefs, n=%d draws, n_c=%d elicitations"
          % (args.k, args.samples, args.elicitations))
    print("provider  : %s" % args.provider)
    print("mode      : %s\n" % ("DRY RUN" if args.provider != "ollama" else "live"))

    imported = cache.seed_from(
        os.path.join(REPO, "experiments", "E-001b-fluency-factorial",
                     "sample-cache.json"),
        ["sender@%s" % args.model, "PRIOR@%s" % args.model,
         "CEILING@%s" % args.model],
        probe_ids) if args.provider == "ollama" else {}
    if imported:
        print("  reused from E-001b's cache (message-independent conditions):")
        for c, n in sorted(imported.items()):
            print("    %-30s %d probes" % (c, n))

    with open(os.path.join(REPO, "experiments", "E-001-fluency-cost",
                           "source-spec.md"), "r", encoding="utf-8") as fh:
        spec = fh.read()

    sender = make_agent(args.provider, "sender", spec, args.model, 1)

    # --- compose, then persist before anything else touches them -----------
    briefs: Dict[str, str] = {}
    for i in range(args.k):
        briefs["b%d" % i] = sender.compose(COMPOSE_PROMPT, seed=i)
    costs = {l: float(sender.cost_of(m)) for l, m in briefs.items()}
    with open(args.briefs_out, "w", encoding="utf-8") as fh:
        json.dump({"probe_measure": measure.qualified_id, "model": args.model,
                   "prompt": COMPOSE_PROMPT, "briefs": briefs,
                   "cost_tokens": costs,
                   "fingerprints": {l: fingerprint(m) for l, m in briefs.items()}},
                  fh, indent=1, sort_keys=True)
    print("  composed %d briefs -> %s" % (len(briefs), args.briefs_out))
    print("  cost: min %.0f  median %.0f  max %.0f tokens"
          % (min(costs.values()),
             statistics.median(costs.values()), max(costs.values())))

    # --- sweep -------------------------------------------------------------
    contexts = {"sender": spec, "PRIOR": "", "CEILING": spec}
    contexts.update(briefs)
    progress = {"done": 0, "total": len(contexts) * len(measure)}
    raw: Dict[str, List[List[str]]] = {}
    claims: Dict[str, Dict[str, List[float]]] = {}

    for label, ctx in contexts.items():
        agent = (sender if label == "sender"
                 else make_agent(args.provider, label, ctx, args.model,
                                 hash(label) % 999))
        cond = "%s@%s" % (label, args.model)
        if label in briefs:
            cond += "#" + fingerprint(briefs[label])
        raw[label] = collect(agent, measure, args.samples, cond, cache, progress)

        if label in briefs:
            claims[label] = {
                "sender": elicit(sender, measure, "your colleague",
                                 briefs[label], args.elicitations,
                                 "claim-sender@%s#%s" % (args.model,
                                                         fingerprint(briefs[label])),
                                 cache),
                "receiver": elicit(agent, measure,
                                   "the person who briefed you", None,
                                   args.elicitations,
                                   "claim-receiver@%s#%s" % (args.model,
                                                             fingerprint(briefs[label])),
                                   cache),
            }
            # --- degeneracy gate, at the earliest point its inputs exist ---
            flat = claims[label]["sender"] + claims[label]["receiver"]
            if len(set(flat)) == 1:
                sys.stderr.write("\n")
                return {
                    "experiment": "E-002", "void": True,
                    "voided_at": "first brief's elicitation",
                    "void_reason": (
                        "elicitation is degenerate: every per-probe claim on "
                        "brief %s is %.2f, from both parties. Resolution is "
                        "zero by construction, so H2 is untestable rather than "
                        "false, and Phi collapses to -A." % (label, flat[0])),
                    "briefs": briefs,
                }
    sys.stderr.write("\n\n")

    results: Dict[str, Any] = {
        "experiment": "E-002", "core_version": "0.3",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dry_run": bool(args.provider != "ollama"),
        "probe_measure": measure.qualified_id,
        "provider": args.provider, "model": args.model,
        "sampling_regime": {"think": OLLAMA_THINK, "temperature": OLLAMA_TEMPERATURE},
        "k": args.k, "samples_per_probe": args.samples,
        "elicitations_per_probe": args.elicitations,
        "reused_conditions": imported,
        "briefs": briefs, "brief_costs": costs,
        "raw_draws": raw, "claims": claims,
    }
    results.update(analyse(measure, raw, claims, costs, args.epsilon))

    ceil_f = transfer_fidelity(
        results["d_prior"],
        mean_divergence([to_distribution(d) for d in raw["sender"]],
                        [to_distribution(d) for d in raw["CEILING"]],
                        measure.weights),
        results["d_floor"], args.epsilon)
    results["gates"] = {
        "sender_accuracy": {"value": results["sender_accuracy"],
                            "threshold": SENDER_ACCURACY_GATE,
                            "passed": bool(results["sender_accuracy"]
                                           > SENDER_ACCURACY_GATE)},
        "sender_error_count": {"value": len(results["sender_errors"]),
                               "threshold": SENDER_MAX_ERRORS,
                               "passed": bool(len(results["sender_errors"])
                                              <= SENDER_MAX_ERRORS)},
        "admissibility": {"gap": results["d_prior"] - results["d_floor"],
                          "threshold": args.epsilon,
                          "passed": bool(results["admissible"])},
        "ceiling_fidelity": {"value": ceil_f, "threshold": CEILING_GATE,
                             "passed": bool(ceil_f > CEILING_GATE)},
    }
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="E-002 phantom agreement")
    ap.add_argument("--provider", choices=("ollama", "dry"), default="dry")
    ap.add_argument("--model", default="gpt-oss:120b")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--samples", type=int, default=30)
    ap.add_argument("--elicitations", type=int, default=5)
    ap.add_argument("--epsilon", type=float, default=EPSILON)
    ap.add_argument("--cache", default=os.path.join(HERE, "sample-cache.json"))
    ap.add_argument("--briefs-out", default=os.path.join(HERE, "briefs.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    args = ap.parse_args()
    ap.set_defaults()

    if args.provider == "ollama" and not ollama_available():
        print("ollama is not reachable", file=sys.stderr)
        return 2

    results = run(args)
    os.makedirs(args.out, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    path = os.path.join(args.out, "E-002-%s%s.json"
                        % (stamp, "-dryrun" if results.get("dry_run") else ""))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)

    if results.get("void"):
        print("VOID at %s: %s" % (results["voided_at"], results["void_reason"]))
    else:
        print("  hypothesis                          estimate   p(holm)  CI95")
        for name, e in sorted(results["effects"].items()):
            val = e.get("phi", e.get("resolution", e.get("difference")))
            if val is None:
                print("  %-36s uncomputable" % name)
                continue
            print("  %-36s %+8.4f  %7.4f  [%+.4f, %+.4f]%s"
                  % (name, val, e.get("p_value_holm", float("nan")),
                     e["ci95"][0], e["ci95"][1],
                     "  SUPPORTED" if e.get("supported")
                     and e.get("significant_at_005") else ""))
        failed = [g for g, v in results["gates"].items() if not v["passed"]]
        print("\n  gates failed: %s" % (", ".join(failed) if failed else "none"))

    print("\nwrote %s" % path)
    if results.get("dry_run"):
        print("DRY RUN -- synthetic, no scientific weight.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
