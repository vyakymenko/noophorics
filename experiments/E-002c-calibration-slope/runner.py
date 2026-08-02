#!/usr/bin/env python3
"""E-002c -- is confidence responsive to transfer at all?

Runs the design pre-registered in PREREGISTRATION.md. Read that first.

The primary quantity is the CALIBRATION SLOPE beta = d(claimed)/d(observed) over
briefs, not E-002b's corr(fidelity, Phi) -- which returns -0.977 against
counterfactual parties calibrated anywhere from 0 to 0.99 and therefore cannot
fail. beta can. Perfect calibration is 1.0; total unresponsiveness is 0.0.

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
    paired_permutation, permutation_diff, point_biserial, to_distribution,
    transfer_fidelity,
)
from noophorics.decomposition import decompose  # noqa: E402
from noophorics.ollama_agent import OllamaAgent, ollama_available  # noqa: E402

SEED = 20260731
FLOOR_PERMUTATIONS = 300
PERMUTATIONS = 10_000
BOOTSTRAP = 5_000
SENDER_ACCURACY_GATE = 0.90
SENDER_MAX_ERRORS = 2
CEILING_GATE = 0.70
EPSILON = 0.02
RUNGS = (30, 70, 110, 150)   # unchanged from E-002b, deliberately
MIN_VARYING_BRIEFS = 4       # claim-variance gate, prereg 5.1
BOOTSTRAP_BETA = 20_000
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
                  probe_ids: Sequence[str], n: Optional[int] = None) -> Dict[str, int]:
        """Import message-independent conditions from another experiment's cache.

        Donor rows longer than ``n`` are truncated to their FIRST ``n`` draws.
        The draws are independent -- each is a fresh call to a stateless
        endpoint at temperature > 0 -- so a prefix of a length-30 sample is a
        valid length-16 sample. Taking a prefix rather than a random subset
        keeps the operation deterministic and keeps draw order, which the
        permutation floor depends on.

        Rows SHORTER than n are not padded and not partially imported; that
        condition is simply recollected.
        """
        out: Dict[str, int] = {}
        if not os.path.exists(donor_path):
            return out
        with open(donor_path, "r", encoding="utf-8") as fh:
            donor = json.load(fh)
        want = set(probe_ids)
        for cond in conditions:
            rows = {p: (list(v)[:n] if n else list(v))
                    for p, v in donor.get(cond, {}).items()
                    if p in want and (n is None or len(v) >= n)}
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
    varying = sum(1 for b in briefs
                  if len(set(per_brief[b]["claims_sender"]
                             + per_brief[b]["claims_receiver"])) > 1)
    surviving = sum(1 for r in rung_status.values() if r["passed"])

    out: Dict[str, Any] = {
        "d_prior": d_prior, "d_floor": floor,
        "admissible": bool((d_prior - floor) > epsilon),
        "sender_accuracy": measure.accuracy(s_modes),
        "sender_errors": [p.id for p, m in zip(measure, s_modes) if m != p.key],
        "per_brief": per_brief, "rungs": rung_status,
        "varying_briefs_count": varying,
        "surviving_rungs": surviving, "analysed_briefs": live,
    }
    if varying < MIN_VARYING_BRIEFS:
        out["void"] = True
        out["void_reason"] = (
            "only %d of %d briefs produced a non-constant claim series "
            "(minimum %d). beta is a slope of claim on outcome: with claims "
            "identical it is not 'zero responsiveness measured' but 'no "
            "measurement possible', and reporting 0.0 would assert the finding "
            "the instrument failed to test."
            % (varying, len(briefs), MIN_VARYING_BRIEFS))
        out["varying_briefs"] = varying
        return out
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

    # PAIRED. Both parties are measured on the SAME briefs, and the
    # pre-registration names the brief as the exchangeable unit. The first
    # version used the unpaired two-sample test here while building the CI from
    # the paired differences, so one hypothesis got a paired interval and an
    # unpaired test -- which is why the record carried supported=true beside
    # significant_at_005=false. Conformance fix, not a change of plan.
    paired_diffs = [per_brief[b]["phi_sender"] - per_brief[b]["phi_receiver"]
                    for b in live]
    obs4, p4 = paired_permutation(paired_diffs, PERMUTATIONS, SEED)
    _, dlo, dhi = bootstrap_ci([per_brief[b]["phi_sender"]
                                - per_brief[b]["phi_receiver"] for b in live],
                               resamples=BOOTSTRAP, seed=SEED)
    effects["H4_sender_worse_than_receiver"] = {
        "value": obs4, "phi_sender": statistics.mean(u("phi_sender")),
        "phi_receiver": statistics.mean(u("phi_receiver")),
        "ci95": [dlo, dhi], "p_value": p4, "supported": bool(dlo > 0.0)}

    # --- beta: the calibration slope, prereg 5.3 ---------------------------
    def _slope(x, y):
        mx, my = statistics.mean(x), statistics.mean(y)
        den = sum((a - mx) ** 2 for a in x)
        return (sum((a - mx) * (b - my) for a, b in zip(x, y)) / den
                if den else float("nan"))

    def _boot_slope(x, y, seed):
        rng = random.Random(seed)
        draws = []
        for _ in range(BOOTSTRAP_BETA):
            idx = [rng.randrange(len(x)) for _ in range(len(x))]
            v = _slope([x[i] for i in idx], [y[i] for i in idx])
            if v == v:
                draws.append(v)
        draws.sort()
        return draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws))]

    obs_b = [statistics.mean(per_brief[b]["observed_per_probe"]) for b in live]
    cs_b = [statistics.mean(per_brief[b]["claims_sender"]) for b in live]
    cr_b = [statistics.mean(per_brief[b]["claims_receiver"]) for b in live]
    pooled_b = [(a + c) / 2 for a, c in zip(cs_b, cr_b)]

    # Attenuation: sampling noise in a per-brief claim mean biases beta TOWARD
    # zero, which is the direction of the hypothesis. Both values are reported;
    # neither is corrected silently.
    within = statistics.mean([
        statistics.variance(per_brief[b]["claims_sender"]
                            + per_brief[b]["claims_receiver"])
        / len(per_brief[b]["claims_sender"] + per_brief[b]["claims_receiver"])
        for b in live])
    between = statistics.variance(pooled_b) if len(pooled_b) > 1 else 0.0
    reliability = (between - within) / between if between > 0 else float("nan")

    for name, claims, seed in (("pooled", pooled_b, SEED),
                               ("sender", cs_b, SEED + 1),
                               ("receiver", cr_b, SEED + 2)):
        b = _slope(obs_b, claims)
        lo, hi = _boot_slope(obs_b, claims, seed)
        entry = {"value": b, "ci95": [lo, hi],
                 "beta_reliability_corrected": (b / reliability
                                                if reliability == reliability
                                                and reliability > 0 else None)}
        if name == "pooled":
            entry["supported_H1_below_half"] = bool(hi < 0.5)
            entry["supported_H2_includes_zero"] = bool(lo <= 0.0 <= hi)
        effects["beta_%s" % name] = entry

    effects["H1_beta_below_half"] = {
        "value": effects["beta_pooled"]["value"],
        "ci95": effects["beta_pooled"]["ci95"],
        "supported": effects["beta_pooled"]["supported_H1_below_half"],
        "note": "interval decision, not a p-value: the claim is about a "
                "magnitude, and a p-value against a nil null answers a "
                "question nobody asked",
    }
    effects["H2_beta_includes_zero"] = {
        "value": effects["beta_pooled"]["value"],
        "ci95": effects["beta_pooled"]["ci95"],
        "supported": effects["beta_pooled"]["supported_H2_includes_zero"],
    }
    # H3 -- PAIRED from the start. E-002b reported the level version of this
    # under an unpaired test and called it unsupported at p = 0.385; the paired
    # test on the same data gave 0.0033.
    per_brief_gap = [c - s2 for c, s2 in zip(cr_b, cs_b)]
    obs3b, p3b = paired_permutation(per_brief_gap, PERMUTATIONS, SEED)
    # A CI on the slope DIFFERENCE, resampling briefs jointly so the pairing
    # survives the bootstrap. "No point estimate without a CI" applies here too.
    rng3 = random.Random(SEED + 3)
    diffs = []
    for _ in range(BOOTSTRAP_BETA):
        idx = [rng3.randrange(len(obs_b)) for _ in range(len(obs_b))]
        o = [obs_b[i] for i in idx]
        v = _slope(o, [cr_b[i] for i in idx]) - _slope(o, [cs_b[i] for i in idx])
        if v == v:
            diffs.append(v)
    diffs.sort()
    effects["H3_sender_less_responsive"] = {
        "value": _slope(obs_b, cr_b) - _slope(obs_b, cs_b),
        "ci95": [diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs))]],
        "claim_gap_receiver_minus_sender": obs3b,
        "p_value": p3b,
    }
    effects["H4_resolution_survives_finer_grid"] = effects.pop(
        "H2_resolution_above_chance")

    # E-002b's quantities carry over as RECORDED, not hypothesised -- the
    # pre-registration lists them under "recorded, not hypothesised" and names
    # exactly four hypotheses. Leaving them named H* would put eight members in
    # a family the plan says has four, and Holm would divide the alpha among
    # quantities nobody predicted.
    for old_name in ("H1_bias_positive", "H3_conditional_asymmetry",
                     "H4_sender_worse_than_receiver"):
        if old_name in effects:
            effects["recorded_" + old_name.split("_", 1)[1]] = effects.pop(old_name)

    results_extra = {
        "beta_attenuation": {"within_brief_variance": within,
                             "between_brief_variance": between,
                             "reliability": reliability},
    }

    FAMILY = ("H1_beta_below_half", "H2_beta_includes_zero",
              "H3_sender_less_responsive", "H4_resolution_survives_finer_grid")
    for name, p_adj in holm_adjust({k: effects[k]["p_value"] for k in FAMILY
                                    if k in effects
                                    and effects[k].get("p_value") is not None}).items():
        effects[name]["p_value_holm"] = p_adj
        effects[name]["significant_at_005"] = bool(p_adj < 0.05)

    # H3's verdict has to be written down. The paired test ran and the CI was
    # built, and then nothing recorded whether the hypothesis held -- the
    # results file carried `supported: null` for a registered hypothesis. A
    # value with no verdict is the half of E-002b's H4 defect that survived:
    # there, a record and a report disagreed; here there was no record to
    # disagree with.
    #
    # The rule is the registered one (section 5.5 and section 8): a paired
    # sign-flip permutation, Holm-corrected, and directional -- the hypothesis
    # names which party is less responsive, so a significant difference the
    # other way refutes it rather than supporting it.
    if "H3_sender_less_responsive" in effects:
        h3 = effects["H3_sender_less_responsive"]
        h3["supported"] = bool(h3.get("significant_at_005")
                               and h3["value"] > 0.0)
        h3["decision_rule"] = ("paired sign-flip permutation, Holm-corrected, "
                               "one-sided by design: beta_receiver > beta_sender")

    out["effects"] = effects
    out.update(results_extra)
    # The declared family is the REGISTERED one. Built as "everything carrying a
    # p_value", it swept in the three recorded_* quantities that the block above
    # had just renamed out of the hypothesis family on purpose -- so the results
    # file declared a five-member family while Holm had correctly divided alpha
    # among the registered four. A multiplicity declaration that contradicts the
    # correction actually applied is worse than none: it is checkable, and it
    # would have been checked.
    corrected = [k for k in FAMILY
                 if k in effects and effects[k].get("p_value") is not None]
    out["multiplicity"] = {
        "correction": "holm",
        "family": list(FAMILY),
        "corrected": corrected,
        "uncorrected_by_design": [k for k in FAMILY if k not in corrected],
        "note": ("H1-H4 are one family (preregistration section 8). H1 and H2 "
                 "are interval decisions with no p-value, so Holm divides alpha "
                 "among the members that use one. The recorded_* quantities are "
                 "not hypotheses and are not in the family."),
    }
    return out


def _shows_supported(effect: Dict[str, Any]) -> bool:
    """Whether the summary table marks an effect as supported.

    The previous condition required `significant_at_005`, which H1 and H2 can
    never have: they are interval decisions by design, deliberately given no
    p-value, so the *primary* hypothesis of this experiment could not print as
    supported however the data came out. The record was right and the report
    was silent -- which is the shape of the E-002b H4 defect, and the terminal
    summary is what a person reads at the end of a forty-five hour run.
    """
    if not effect.get("supported"):
        return False
    if effect.get("p_value") is None:
        return True                     # interval decision; nothing to correct
    return bool(effect.get("significant_at_005"))


def run(args) -> Dict[str, Any]:
    measure = load_probe_measure(os.path.join(HERE, "..",
                                              "E-002-phantom-agreement",
                                              "probes.json"))
    cache = Cache(args.cache)
    probe_ids = [p.id for p in measure]

    print("\nE-002c  Is confidence responsive to transfer at all?")
    print("measure   : %s (%d probes)" % (measure.qualified_id, len(measure)))
    print("ladder    : %s target words, k=%d each" % (list(RUNGS), args.k))
    print("draws     : n=%d, elicitations n_c=%d" % (args.samples, args.elicitations))
    print("provider  : %s\n" % args.provider)

    imported = cache.seed_from(
        os.path.join(REPO, "experiments", "E-002b-phantom-agreement-ladder",
                     "sample-cache.json"),
        ["sender@%s" % args.model, "PRIOR@%s" % args.model,
         "CEILING@%s" % args.model], probe_ids,
        args.samples) if args.provider == "ollama" else {}
    if imported:
        print("  reused (message-independent):", ", ".join(
            "%s=%d" % (k.split("@")[0], v) for k, v in sorted(imported.items())))

    with open(os.path.join(REPO, "experiments", "E-001-fluency-cost",
                           "source-spec.md"), "r", encoding="utf-8") as fh:
        spec = fh.read()
    sender = make_agent(args.provider, "sender", spec, args.model, 1, 0.94)

    # Resume path. Composition is stochastic, so re-composing after an
    # interruption produces different briefs wearing the same labels and
    # orphans every draw already collected against them -- the cache is keyed by
    # brief fingerprint precisely so that mismatch cannot pass silently.
    # briefs.json is written before the sweep for exactly this case.
    if args.resume_briefs and os.path.exists(args.briefs_out):
        with open(args.briefs_out, "r", encoding="utf-8") as fh:
            saved = json.load(fh)
        briefs = saved["briefs"]
        meta = {k: v for k, v in saved["meta"].items()}
        if sorted(briefs) != sorted("r%03d_%d" % (r, j)
                                    for r in RUNGS for j in range(args.k)):
            raise SystemExit("briefs.json does not match the registered ladder; "
                             "refusing to resume against a different design")
        print("  resumed %d briefs from %s (not re-composed)"
              % (len(briefs), args.briefs_out))
        costs_ok = True
    else:
        briefs = {}
        meta = {}
        costs_ok = False

    if not briefs:
     for rung in RUNGS:
        low, high = int(rung * 0.85), int(rung * 1.15)
        for j in range(args.k):
            label = "r%03d_%d" % (rung, j)
            text = sender.compose(COMPOSE.format(low=low, high=high), seed=j)
            briefs[label] = text
            meta[label] = {"rung": rung, "words": len(text.split()),
                           "cost": float(sender.cost_of(text))}
    if not costs_ok:
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
        "experiment": "E-002c", "core_version": "0.4",
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
        "claim_variance": {"varying_briefs": results.get("varying_briefs_count"),
                           "threshold": MIN_VARYING_BRIEFS,
                           "passed": True},
        "surviving_rungs": {"value": results["surviving_rungs"],
                            "threshold": MIN_SURVIVING_RUNGS,
                            "passed": bool(results["surviving_rungs"] >= MIN_SURVIVING_RUNGS)},
    }
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="E-002c calibration slope")
    ap.add_argument("--provider", choices=("ollama", "dry"), default="dry")
    ap.add_argument("--model", default="gpt-oss:120b")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--elicitations", type=int, default=9)
    ap.add_argument("--epsilon", type=float, default=EPSILON)
    ap.add_argument("--cache", default=os.path.join(HERE, "sample-cache.json"))
    ap.add_argument("--briefs-out", default=os.path.join(HERE, "briefs.json"))
    ap.add_argument("--resume-briefs", action="store_true",
                    help="load briefs.json instead of re-composing. Required "
                         "after an interruption: re-composing orphans every "
                         "draw already collected against the old briefs.")
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    args = ap.parse_args()

    if args.provider == "ollama" and not ollama_available():
        print("ollama is not reachable", file=sys.stderr)
        return 2

    results = run(args)
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "E-002c-%s%s.json"
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
        print("\n  beta = d(claimed)/d(observed). calibration = 1.0, "
              "unresponsive = 0.0")
        for who in ("pooled", "sender", "receiver"):
            e = results["effects"].get("beta_%s" % who)
            if e:
                print("   %-9s %+7.4f   CI [%+.4f, %+.4f]"
                      % (who, e["value"], e["ci95"][0], e["ci95"][1]))
        print("\n  hypothesis                           value   p(holm)  CI95"
              "\n  (~ = raw p, recorded not hypothesised, deliberately "
              "uncorrected; 'interval' = decided by the CI, no p by design)")
        for name, e in sorted(results["effects"].items()):
            if "value" not in e:
                print("  %-36s uncomputable" % name)
                continue
            ci = e.get("ci95", [float("nan")] * 2)
            # "nan" in a p-value column reads as a broken statistic, and a
            # line that reads as broken gets discounted. These two have no
            # p-value by design; say so rather than printing a float that
            # cannot exist.
            # Three states, and collapsing any two of them misdescribes a
            # number. A Holm-corrected p, a raw p that was deliberately left
            # uncorrected because the quantity is recorded rather than
            # hypothesised, and no p at all because the decision is an interval
            # one. The first draft printed "interval" for all of the last two
            # and so told the reader that the recorded quantities had no
            # p-value, which is not true of any of them.
            ph, praw = e.get("p_value_holm"), e.get("p_value")
            if ph is not None:
                pcol = "%8.4f" % ph
            elif praw is not None:
                pcol = "%7.4f~" % praw
            else:
                pcol = " interval"
            print("  %-36s %+7.4f %s  [%+.4f, %+.4f]%s"
                  % (name, e["value"], pcol, ci[0], ci[1],
                     "  SUPPORTED" if _shows_supported(e) else ""))
        failed = [g for g, v in results["gates"].items() if not v["passed"]]
        print("\n  gates failed: %s" % (", ".join(failed) if failed else "none"))
    print("\nwrote %s" % path)
    if results.get("dry_run"):
        print("DRY RUN -- synthetic, no scientific weight.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
