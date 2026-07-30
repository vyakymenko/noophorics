#!/usr/bin/env python3
"""E-002b -- does Phi rise where fidelity falls?

Runs the design pre-registered in PREREGISTRATION.md. Read that first, and
INSTRUMENT.md for why E-002's two defects are fixed in the design rather than
in prose.

    python3 runner.py --dry-run
    python3 runner.py --provider ollama
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
    ProbeMeasure, agreement_rate, bootstrap_ci, goodman_kruskal_gamma,
    holm_adjust, load_probe_measure, mean_divergence, mean_permutation_floor,
    permutation_diff, point_biserial, to_distribution, transfer_fidelity,
)
from noophorics.decomposition import decompose  # noqa: E402
from noophorics.ollama_agent import OllamaAgent, ollama_available  # noqa: E402

SEED = 20260730
FLOOR_PERMUTATIONS = 300
PERMUTATIONS = 10_000
BOOTSTRAP = 5_000
SENDER_ACCURACY_GATE = 0.90
SENDER_MAX_ERRORS = 2
CEILING_GATE = 0.70
EPSILON = 0.02
RUNGS = (30, 70, 110, 150)          # target words; see INSTRUMENT.md
RUNG_MIN_DIVERGED = 3               # of 33
RUNG_MAX_DIVERGED = 30
MIN_SURVIVING_RUNGS = 3
OLLAMA_THINK = "medium"
OLLAMA_TEMPERATURE = 0.7

COMPOSE = """You are holding a set of submission-handling rules. A colleague \
who has never seen those rules, and never will, has to decide real cases with \
them. The note you are about to write is the only thing they will have.

Write the note in between {low} and {high} words. Output the note and nothing \
else: no preamble, no sign-off."""

SENDER_FRAMING = """Your colleague has only the note below -- nothing else, \
they have never seen the rules, and they cannot ask you anything. Predict the \
verdict THEY will reach on the case that follows."""

RECEIVER_FRAMING = """Predict the verdict that the person who wrote your note \
would reach on the case that follows. They wrote the note and they hold the \
full rules."""


def fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]


def mode_of(rows: Sequence[Sequence[str]]) -> List[str]:
    out = []
    for row in rows:
        d = to_distribution(row)
        out.append(max(sorted(d), key=lambda k: d[k]))
    return out


class Cache:
    def __init__(self, path: Optional[str]):
        self.path = path
        self._data: Dict[str, Dict[str, Any]] = {}
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                self._data = json.load(fh)

    def get(self, cond: str, pid: str, n: int) -> Optional[List[Any]]:
        got = self._data.get(cond, {}).get(pid)
        return list(got) if got is not None and len(got) == n else None

    def put(self, cond: str, pid: str, samples: Sequence[Any]) -> None:
        self._data.setdefault(cond, {})[pid] = list(samples)
        if self.path:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh)
            os.replace(tmp, self.path)

    def seed_from(self, donor_path: str, conditions: Sequence[str],
                  probe_ids: Sequence[str]) -> Dict[str, int]:
        out: Dict[str, int] = {}
        if not os.path.exists(donor_path):
            return out
        with open(donor_path, "r", encoding="utf-8") as fh:
            donor = json.load(fh)
        want = set(probe_ids)
        for cond in conditions:
            rows = {p: v for p, v in donor.get(cond, {}).items() if p in want}
            if len(rows) == len(want):
                self._data.setdefault(cond, {}).update(rows)
                out[cond] = len(rows)
        if out and self.path:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh)
        return out


class Stub:
    """Dry-run stand-in whose divergence scales with the brief budget.

    Deliberately not constant: a stub that always agrees would let the outcome
    gate pass trivially and would not exercise the analysis the gate protects.
    """

    def __init__(self, name: str, accuracy: float, seed: int):
        self.name, self._acc = name, accuracy
        self._rng = random.Random(seed)

    def answer_samples(self, probe, n: int) -> List[str]:
        wrong = [o for o in probe.options if o != probe.key]
        return [probe.key if self._rng.random() < self._acc
                else self._rng.choice(wrong) for _ in range(n)]

    def predict_verdict(self, probe, framing, artifact=None,
                        n_elicitations: int = 3) -> List[str]:
        wrong = [o for o in probe.options if o != probe.key]
        return [probe.key if self._rng.random() < 0.9
                else self._rng.choice(wrong) for _ in range(n_elicitations)]

    def compose(self, prompt: str, seed: int = 0) -> str:
        return "synthetic %d %s" % (seed, "word " * 60)

    def cost_of(self, message: str) -> int:
        return max(1, len(message.split()))


def make_agent(provider: str, name: str, context: str, model: str, seed: int,
               accuracy: float = 0.9):
    if provider == "ollama":
        return OllamaAgent(name, context, model=model, think=OLLAMA_THINK,
                           temperature=OLLAMA_TEMPERATURE)
    return Stub(name, accuracy, seed)


def collect(agent, measure, n, cond, cache, progress) -> List[List[str]]:
    rows = []
    for probe in measure:
        got = cache.get(cond, probe.id, n)
        if got is None:
            got = agent.answer_samples(probe, n)
            cache.put(cond, probe.id, got)
        rows.append(got)
        progress["done"] += 1
        sys.stderr.write("\r  %-40s %d/%d" % (cond[:40], progress["done"],
                                              progress["total"]))
        sys.stderr.flush()
    return rows


def predict(agent, measure, framing, artifact, n_c, cond, cache) -> List[List[str]]:
    rows = []
    for probe in measure:
        got = cache.get(cond, probe.id, n_c)
        if got is None:
            got = agent.predict_verdict(probe, framing, artifact=artifact,
                                        n_elicitations=n_c)
            cache.put(cond, probe.id, got)
        rows.append(got)
    return rows


def claimed_match(predictions: Sequence[Sequence[str]],
                  own_modes: Sequence[str]) -> List[float]:
    """Claimed agreement per probe: did the party predict its own verdict?

    This is how 72% was computed in 2002 -- by the experimenter, afterwards,
    never by asking the party for a rate.
    """
    return [sum(1.0 for p in preds if p == own) / len(preds)
            for preds, own in zip(predictions, own_modes)]


# --------------------------------------------------------------------------


def analyse(measure: ProbeMeasure, raw: Dict[str, List[List[str]]],
            preds: Dict[str, Dict[str, List[List[str]]]],
            meta: Dict[str, Dict[str, Any]], epsilon: float) -> Dict[str, Any]:
    s_dists = [to_distribution(d) for d in raw["sender"]]
    p_dists = [to_distribution(d) for d in raw["PRIOR"]]
    d_prior = mean_divergence(s_dists, p_dists, measure.weights)
    floor = mean_permutation_floor(raw["sender"], raw["PRIOR"], measure.weights,
                                   FLOOR_PERMUTATIONS, SEED)
    s_modes = mode_of(raw["sender"])
    probe_ids = [p.id for p in measure]

    briefs = sorted(k for k in raw if k not in ("sender", "PRIOR", "CEILING"))
    per_brief: Dict[str, Any] = {}
    for label in briefs:
        r_dists = [to_distribution(d) for d in raw[label]]
        r_modes = mode_of(raw[label])
        observed = [1.0 if a == b else 0.0 for a, b in zip(s_modes, r_modes)]
        cs = claimed_match(preds[label]["sender"], s_modes)
        cr = claimed_match(preds[label]["receiver"], r_modes)
        dec = decompose(measure, raw["sender"], raw["PRIOR"], raw[label])
        d_post = mean_divergence(s_dists, r_dists, measure.weights)
        rec: Dict[str, Any] = {
            "rung": meta[label]["rung"], "brief_words": meta[label]["words"],
            "cost_tokens": meta[label]["cost"],
            "d_post": d_post,
            "fidelity": transfer_fidelity(d_prior, d_post, floor, epsilon),
            "fidelity_where_sender_right": dec.fidelity_where_sender_right,
            "error_replication": dec.error_replication,
            "agreement_observed": agreement_rate(s_dists, r_dists, measure.weights),
            "diverged_probes": [i for i, o in zip(probe_ids, observed) if o == 0.0],
            "observed_per_probe": observed,
            "claims_sender": cs, "claims_receiver": cr,
            "phi_sender": statistics.mean(cs) - statistics.mean(observed),
            "phi_receiver": statistics.mean(cr) - statistics.mean(observed),
            "phi": statistics.mean([(a + b) / 2 for a, b in zip(cs, cr)])
                   - statistics.mean(observed),
            "resolution_sender": point_biserial(cs, observed),
            "resolution_receiver": point_biserial(cr, observed),
            "gamma_sender": goodman_kruskal_gamma(cs, observed),
            "gamma_receiver": goodman_kruskal_gamma(cr, observed),
        }
        for who, cl in (("sender", cs), ("receiver", cr)):
            div = [c for c, o in zip(cl, observed) if o == 0.0]
            mat = [c for c, o in zip(cl, observed) if o == 1.0]
            rec["overestimation_%s" % who] = statistics.mean(div) if div else None
            rec["underestimation_%s" % who] = (1.0 - statistics.mean(mat)) if mat else None
        per_brief[label] = rec

    # --- per-rung outcome gate -------------------------------------------
    rung_status: Dict[str, Any] = {}
    for rung in sorted({per_brief[b]["rung"] for b in briefs}):
        members = [b for b in briefs if per_brief[b]["rung"] == rung]
        diverged = statistics.mean([len(per_brief[b]["diverged_probes"])
                                    for b in members])
        passed = RUNG_MIN_DIVERGED <= diverged <= RUNG_MAX_DIVERGED
        rung_status[str(rung)] = {
            "briefs": members, "mean_diverged": diverged,
            "bounds": [RUNG_MIN_DIVERGED, RUNG_MAX_DIVERGED], "passed": passed,
            "reason": ("" if passed else
                       "no variation for a prediction to discriminate; "
                       "dropped, not voided (Problem 11)"),
        }
    live = [b for b in briefs if rung_status[str(per_brief[b]["rung"])]["passed"]]
    surviving = sum(1 for r in rung_status.values() if r["passed"])

    out: Dict[str, Any] = {
        "d_prior": d_prior, "d_floor": floor,
        "admissible": bool((d_prior - floor) > epsilon),
        "sender_accuracy": measure.accuracy(s_modes),
        "sender_errors": [p.id for p, m in zip(measure, s_modes) if m != p.key],
        "per_brief": per_brief, "rungs": rung_status,
        "surviving_rungs": surviving, "analysed_briefs": live,
    }
    if surviving < MIN_SURVIVING_RUNGS:
        out["void"] = True
        out["void_reason"] = (
            "only %d of %d rungs produced outcome variation; the ladder cannot "
            "support H5 and Problem 11 got harder rather than being worked "
            "around" % (surviving, len(rung_status)))
        return out

    def u(field: str) -> List[float]:
        return [per_brief[b][field] for b in live if per_brief[b][field] is not None]

    effects: Dict[str, Any] = {}

    phi, lo, hi = bootstrap_ci(u("phi"), resamples=BOOTSTRAP, seed=SEED)
    _, p1 = permutation_diff(u("phi"), [0.0] * len(live), PERMUTATIONS, SEED)
    effects["H1_bias_positive"] = {"value": phi, "ci95": [lo, hi], "p_value": p1,
                                   "supported": bool(lo > 0.0)}

    res = u("resolution_sender") + u("resolution_receiver")
    r, rlo, rhi = bootstrap_ci(res, resamples=BOOTSTRAP, seed=SEED)
    _, p2 = permutation_diff(res, [0.0] * len(res), PERMUTATIONS, SEED)
    effects["H2_resolution_above_chance"] = {
        "value": r, "ci95": [rlo, rhi], "p_value": p2,
        "gamma": statistics.mean(u("gamma_sender") + u("gamma_receiver")),
        "supported": bool(rlo > 0.0)}

    over = u("overestimation_sender") + u("overestimation_receiver")
    under = u("underestimation_sender") + u("underestimation_receiver")
    if over and under and len(over) == len(under):
        obs3, p3 = permutation_diff(over, under, PERMUTATIONS, SEED)
        _, alo, ahi = bootstrap_ci([a - b for a, b in zip(over, under)],
                                   resamples=BOOTSTRAP, seed=SEED)
        effects["H3_conditional_asymmetry"] = {
            "value": obs3, "overestimation": statistics.mean(over),
            "underestimation": statistics.mean(under),
            "ci95": [alo, ahi], "p_value": p3, "supported": bool(alo > 0.0),
            "human_reference": {"source": "Keysar & Henly 2002",
                                "overestimation": 0.46, "underestimation": 0.12}}
    else:
        effects["H3_conditional_asymmetry"] = {"uncomputable": "one side empty"}

    obs4, p4 = permutation_diff(u("phi_sender"), u("phi_receiver"),
                                PERMUTATIONS, SEED)
    _, dlo, dhi = bootstrap_ci([per_brief[b]["phi_sender"]
                                - per_brief[b]["phi_receiver"] for b in live],
                               resamples=BOOTSTRAP, seed=SEED)
    effects["H4_sender_worse_than_receiver"] = {
        "value": obs4, "phi_sender": statistics.mean(u("phi_sender")),
        "phi_receiver": statistics.mean(u("phi_receiver")),
        "ci95": [dlo, dhi], "p_value": p4, "supported": bool(dlo > 0.0)}

    # H5 -- the reason the ladder exists
    xs = [per_brief[b]["fidelity_where_sender_right"] for b in live]
    ys = [per_brief[b]["phi"] for b in live]
    rho = point_biserial(xs, ys)          # Pearson; both series continuous
    rng = random.Random(SEED)
    extreme = 0
    for _ in range(PERMUTATIONS):
        shuffled = ys[:]
        rng.shuffle(shuffled)
        if abs(point_biserial(xs, shuffled)) >= abs(rho) - 1e-15:
            extreme += 1
    p5 = (extreme + 1) / (PERMUTATIONS + 1)
    # Bootstrap the correlation over briefs. The pre-registration says no point
    # estimate is reported without a CI, and a correlation is a point estimate.
    boot = random.Random(SEED + 1)
    draws = []
    for _ in range(BOOTSTRAP):
        idx = [boot.randrange(len(xs)) for _ in range(len(xs))]
        bx, by = [xs[i] for i in idx], [ys[i] for i in idx]
        draws.append(point_biserial(bx, by))
    draws.sort()
    ci5 = [draws[int(0.025 * BOOTSTRAP)], draws[min(BOOTSTRAP - 1, int(0.975 * BOOTSTRAP))]]
    effects["H5_phi_rises_as_fidelity_falls"] = {
        "value": rho, "p_value": p5, "ci95": ci5,
        "direction_predicted": "negative",
        "supported": bool(ci5[1] < 0.0),
        "per_rung": {r: {"mean_phi": statistics.mean(
                            [per_brief[b]["phi"] for b in v["briefs"]]),
                         "mean_fidelity": statistics.mean(
                            [per_brief[b]["fidelity_where_sender_right"]
                             for b in v["briefs"]])}
                     for r, v in rung_status.items() if v["passed"]}}

    for name, p_adj in holm_adjust({k: v["p_value"] for k, v in effects.items()
                                    if "p_value" in v}).items():
        effects[name]["p_value_holm"] = p_adj
        effects[name]["significant_at_005"] = bool(p_adj < 0.05)

    out["effects"] = effects
    out["multiplicity"] = {"correction": "holm",
                           "family": sorted(k for k in effects if "p_value" in effects[k])}
    return out


def run(args) -> Dict[str, Any]:
    measure = load_probe_measure(os.path.join(HERE, "..",
                                              "E-002-phantom-agreement",
                                              "probes.json"))
    cache = Cache(args.cache)
    probe_ids = [p.id for p in measure]

    print("\nE-002b  Does Phi rise where fidelity falls?")
    print("measure   : %s (%d probes)" % (measure.qualified_id, len(measure)))
    print("ladder    : %s target words, k=%d each" % (list(RUNGS), args.k))
    print("draws     : n=%d, elicitations n_c=%d" % (args.samples, args.elicitations))
    print("provider  : %s\n" % args.provider)

    imported = cache.seed_from(
        os.path.join(REPO, "experiments", "E-002-phantom-agreement",
                     "sample-cache.json"),
        ["sender@%s" % args.model, "PRIOR@%s" % args.model,
         "CEILING@%s" % args.model], probe_ids) if args.provider == "ollama" else {}
    if imported:
        print("  reused (message-independent):", ", ".join(
            "%s=%d" % (k.split("@")[0], v) for k, v in sorted(imported.items())))

    with open(os.path.join(REPO, "experiments", "E-001-fluency-cost",
                           "source-spec.md"), "r", encoding="utf-8") as fh:
        spec = fh.read()
    sender = make_agent(args.provider, "sender", spec, args.model, 1, 0.94)

    briefs: Dict[str, str] = {}
    meta: Dict[str, Dict[str, Any]] = {}
    for rung in RUNGS:
        low, high = int(rung * 0.85), int(rung * 1.15)
        for j in range(args.k):
            label = "r%03d_%d" % (rung, j)
            text = sender.compose(COMPOSE.format(low=low, high=high), seed=j)
            briefs[label] = text
            meta[label] = {"rung": rung, "words": len(text.split()),
                           "cost": float(sender.cost_of(text))}
    with open(args.briefs_out, "w", encoding="utf-8") as fh:
        json.dump({"probe_measure": measure.qualified_id, "model": args.model,
                   "rungs": list(RUNGS), "briefs": briefs, "meta": meta,
                   "fingerprints": {l: fingerprint(m) for l, m in briefs.items()}},
                  fh, indent=1, sort_keys=True)
    print("  composed %d briefs -> %s" % (len(briefs), args.briefs_out))
    for rung in RUNGS:
        w = [meta[l]["words"] for l in meta if meta[l]["rung"] == rung]
        print("    rung %3d -> realised %s words" % (rung, sorted(w)))

    contexts = {"sender": spec, "PRIOR": "", "CEILING": spec}
    contexts.update(briefs)
    progress = {"done": 0, "total": len(contexts) * len(measure)}
    raw: Dict[str, List[List[str]]] = {}
    preds: Dict[str, Dict[str, List[List[str]]]] = {}

    for label, ctx in contexts.items():
        # Stub receiver accuracy scales with the rung, so the dry run reaches
        # the analysis rather than stopping at the outcome gate. A pipeline
        # check that only exercises the void path is the DEFECT-001 mistake
        # with a different function name.
        if label in briefs:
            acc = 0.36 + 0.17 * (RUNGS.index(meta[label]["rung"])
                                 / max(1, len(RUNGS) - 1))
        elif label == "PRIOR":
            acc = 0.40
        else:
            acc = 0.94
        agent = (sender if label == "sender"
                 else make_agent(args.provider, label, ctx, args.model,
                                 hash(label) % 999, acc))
        cond = "%s@%s" % (label, args.model)
        if label in briefs:
            cond += "#" + fingerprint(briefs[label])
        raw[label] = collect(agent, measure, args.samples, cond, cache, progress)
        if label in briefs:
            fp = fingerprint(briefs[label])
            preds[label] = {
                "sender": predict(sender, measure, SENDER_FRAMING, briefs[label],
                                  args.elicitations,
                                  "pred-sender@%s#%s" % (args.model, fp), cache),
                "receiver": predict(agent, measure, RECEIVER_FRAMING, None,
                                    args.elicitations,
                                    "pred-receiver@%s#%s" % (args.model, fp), cache),
            }
    sys.stderr.write("\n\n")

    results: Dict[str, Any] = {
        "experiment": "E-002b", "core_version": "0.3",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dry_run": bool(args.provider != "ollama"),
        "probe_measure": measure.qualified_id, "provider": args.provider,
        "model": args.model, "rungs": list(RUNGS), "k": args.k,
        "samples_per_probe": args.samples,
        "elicitations_per_probe": args.elicitations,
        "sampling_regime": {"think": OLLAMA_THINK, "temperature": OLLAMA_TEMPERATURE},
        "reused_conditions": imported, "briefs": briefs, "brief_meta": meta,
        "raw_draws": raw, "predictions": preds,
    }
    results.update(analyse(measure, raw, preds, meta, args.epsilon))

    ceil_f = transfer_fidelity(
        results["d_prior"],
        mean_divergence([to_distribution(d) for d in raw["sender"]],
                        [to_distribution(d) for d in raw["CEILING"]],
                        measure.weights),
        results["d_floor"], args.epsilon)
    results["gates"] = {
        "sender_accuracy": {"value": results["sender_accuracy"],
                            "threshold": SENDER_ACCURACY_GATE,
                            "passed": bool(results["sender_accuracy"] > SENDER_ACCURACY_GATE)},
        "sender_error_count": {"value": len(results["sender_errors"]),
                               "threshold": SENDER_MAX_ERRORS,
                               "passed": bool(len(results["sender_errors"]) <= SENDER_MAX_ERRORS)},
        "admissibility": {"gap": results["d_prior"] - results["d_floor"],
                          "threshold": args.epsilon,
                          "passed": bool(results["admissible"])},
        "ceiling_fidelity": {"value": ceil_f, "threshold": CEILING_GATE,
                             "passed": bool(ceil_f > CEILING_GATE)},
        "surviving_rungs": {"value": results["surviving_rungs"],
                            "threshold": MIN_SURVIVING_RUNGS,
                            "passed": bool(results["surviving_rungs"] >= MIN_SURVIVING_RUNGS)},
    }
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="E-002b phantom agreement ladder")
    ap.add_argument("--provider", choices=("ollama", "dry"), default="dry")
    ap.add_argument("--model", default="gpt-oss:120b")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--elicitations", type=int, default=3)
    ap.add_argument("--epsilon", type=float, default=EPSILON)
    ap.add_argument("--cache", default=os.path.join(HERE, "sample-cache.json"))
    ap.add_argument("--briefs-out", default=os.path.join(HERE, "briefs.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    args = ap.parse_args()

    if args.provider == "ollama" and not ollama_available():
        print("ollama is not reachable", file=sys.stderr)
        return 2

    results = run(args)
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "E-002b-%s%s.json"
                        % (time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()),
                           "-dryrun" if results.get("dry_run") else ""))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)

    print("  rung   mean diverged / 33   gate")
    for r, v in sorted(results["rungs"].items(), key=lambda x: int(x[0])):
        print("   %-5s  %5.1f                %s" % (r, v["mean_diverged"],
                                                    "pass" if v["passed"] else "DROPPED"))
    if results.get("void"):
        print("\nVOID: %s" % results["void_reason"])
    else:
        print("\n  hypothesis                           value   p(holm)  CI95")
        for name, e in sorted(results["effects"].items()):
            if "value" not in e:
                print("  %-36s uncomputable" % name)
                continue
            ci = e.get("ci95", [float("nan")] * 2)
            print("  %-36s %+7.4f %7.4f  [%+.4f, %+.4f]%s"
                  % (name, e["value"], e.get("p_value_holm", float("nan")),
                     ci[0], ci[1],
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
