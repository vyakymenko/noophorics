#!/usr/bin/env python3
"""E-001 -- The Cost of Fluency.

Runs the pre-registered experiment in PREREGISTRATION.md. Read that file before
this one: the hypotheses and analysis plan were fixed before any data existed,
and nothing here may be changed after seeing results without a new commit
saying so.

    python3 runner.py --dry-run     # verify the pipeline, no API calls
    python3 runner.py               # real run

Self-divergence is estimated by splitting each probe's samples into two halves.
Every sample is a separate API call, so the halves are genuinely independent
and the split does not underestimate the floor the way a within-pass split
would.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "metrics"))

from noophorics import (  # noqa: E402
    InadmissibleProbeMeasure,
    ProbeMeasure,
    agreement_rate,
    load_probe_measure,
    mean_divergence,
    mean_permutation_floor,
    to_distribution,
    transfer_fidelity,
)
from noophorics.decomposition import decompose  # noqa: E402
from noophorics.agents import DEFAULT_MODEL, AnthropicAgent  # noqa: E402

MESSAGE_BUDGET_TOKENS = 350
PERMUTATIONS = 10_000
SEED = 20260728
SENDER_ACCURACY_GATE = 0.85
# A gate on the MEAN cannot protect a statistic whose effect concentrates on a
# handful of probes: E-001's sender passed at 0.882 while its four errors
# carried 62% of the headline effect. The decomposition reports error
# replication directly, and this second gate bounds the count.
SENDER_MAX_ERRORS = 2
BOOTSTRAP = 5000
CEILING_FIDELITY_GATE = 0.70

# Both prompts were written by an independent agent that was blind to the
# hypotheses, the laws, and which condition the experimenter expected to win.
# It received only the source spec and the two style descriptions, and was
# instructed to make the pair equally strong. This replaces an earlier pair
# written by the experimenter, which on inspection favoured the contrastive
# condition: it was prescriptive ("Write ONLY the boundaries. No prose.")
# where the narrative prompt was vague ("Make it read well"). See
# AMENDMENT-002.md.

NARRATIVE_PROMPT = """You are handing off your work. A colleague you respect \
— capable, careful, but with no access to the document you are holding — is \
about to decide real cases with nothing in front of them but what you write \
now. You will not be reachable for questions. Whatever you leave out, they \
will have to guess, and their guesses will become decisions.

Write the handover brief.

Write it as prose: paragraphs with connective reasoning, organized so that \
each part prepares the reader for the next. Explain how the material fits \
together, not just what it says — a reader who understands the shape of a \
system can extend it to a case you never anticipated, while a reader who has \
only been told facts is stranded the moment reality goes slightly off-script. \
Where the material has structure (things that interact, things that take \
precedence, thresholds that decide outcomes), make that structure legible in \
the writing.

You have {budget} tokens. That is far less than the material deserves, so \
triage ruthlessly: prose earns its keep only when the connective tissue is \
carrying real information. Spend words where a wrong reading is likely and \
costly; compress or omit where a careful reader would land correctly anyway. \
Be precise about anything a paraphrase would blur — approximate is worse than \
absent, because it is believed.

Do not describe the brief, apologize for its limits, or comment on what you \
left out. Output the brief itself and nothing else. Hard limit: {budget} \
tokens."""

CONTRASTIVE_PROMPT = """You are handing off your work. A colleague you respect \
— capable, careful, but with no access to the document you are holding — is \
about to decide real cases with nothing in front of them but what you write \
now. You will not be reachable for questions. They will reason competently \
from whatever they have; your job is to make sure their competent reasoning \
does not land in the wrong place.

Write the handover brief as boundaries only.

Include only what a smart reader would get wrong unaided: exact thresholds and \
which side of the line is in or out; exceptions and their precise scope; what \
does not follow from what; which provisions override which, and which override \
everything; cases that look alike but resolve differently; and conditions that \
are easy to assume are required, or assume are sufficient, when they are not. \
Where a wrong default is likely, name the wrong reading and correct it.

Omit everything else. No opening summary, no general picture, no restating \
what holds in the ordinary case, no explanation of purpose or rationale, no \
transitions. One boundary per line, terse, each line able to stand alone. \
Assume the reader can handle the easy cases; you are spending the entire \
budget on the ones that trap them.

You have {budget} tokens. Order lines so the most consequential traps survive \
if you run short. Be exact — an approximate boundary is worse than a missing \
one, because it is believed.

Do not describe the brief or comment on what you left out. Output the brief \
itself and nothing else. Hard limit: {budget} tokens."""


# --------------------------------------------------------------------------
# statistics


def permutation_test(
    differences: Sequence[float], permutations: int = PERMUTATIONS, seed: int = SEED
) -> Tuple[float, float]:
    """Two-sided paired permutation test on per-probe differences.

    Returns (observed mean difference, p-value). Sign-flipping is the correct
    permutation scheme for paired data: under the null the two conditions are
    exchangeable within each probe.
    """
    values = [float(d) for d in differences]
    if not values:
        raise ValueError("no differences to test")
    observed = sum(values) / len(values)
    rng = random.Random(seed)
    extreme = 0
    for _ in range(permutations):
        total = sum(v if rng.random() < 0.5 else -v for v in values)
        if abs(total / len(values)) >= abs(observed) - 1e-15:
            extreme += 1
    return observed, (extreme + 1) / (permutations + 1)


def bootstrap_ci(
    values: Sequence[float], resamples: int = BOOTSTRAP, seed: int = SEED
) -> Tuple[float, float, float]:
    """Percentile bootstrap over probes. Returns (mean, lo95, hi95).

    Every fidelity this repository reported in v0.1 and v0.2 was a bare point
    estimate of a ratio whose sampling distribution nobody had characterised.
    """
    vals = list(values)
    if not vals:
        raise ValueError("nothing to bootstrap")
    rng = random.Random(seed)
    n = len(vals)
    means = []
    for _ in range(resamples):
        means.append(sum(vals[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return (
        sum(vals) / n,
        means[int(0.025 * resamples)],
        means[int(0.975 * resamples) - 1],
    )


# --------------------------------------------------------------------------
# agents


class _StubAgent(object):
    """Deterministic stand-in for --dry-run. Verifies the pipeline, not the science.

    Fidelity is faked by how often the agent copies the ground-truth key, so a
    dry run produces plausible-shaped numbers. Those numbers are meaningless
    and the results file records them as such.
    """

    def __init__(self, name: str, accuracy: float, claim: float, seed: int):
        self.name = name
        self._accuracy = accuracy
        self._claim = claim
        self._rng = random.Random(seed)

    def answer_samples(self, probe, n_samples: int) -> List[str]:
        out = []
        for _ in range(n_samples):
            if self._rng.random() < self._accuracy and probe.key is not None:
                out.append(probe.key)
            else:
                out.append(self._rng.choice(probe.options))
        return out

    def claim_agreement(self, measure, counterpart: str, artifact=None,
                        n_elicitations: int = 3, seed: int = 0):
        # Slight jitter so the dry run exercises the multi-elicitation path.
        return [max(0.0, min(1.0, self._claim + 0.02 * (i - 1)))
                for i in range(n_elicitations)]

    def cost_of(self, message: str) -> int:
        return max(1, len(message.split()))

    def compose(self, prompt: str) -> str:
        return "STUB BRIEF (%s): %s" % (self.name, prompt.splitlines()[0][:60])


class _LiveSender(object):
    """The sender: a model holding the full source specification."""

    def __init__(self, spec: str, model: str, samples_effort: str = "low"):
        self.name = "%s/spec" % model
        self.model = model
        self._prober = AnthropicAgent(
            name=self.name, context=spec, model=model, effort=samples_effort
        )
        # ONE sender, one effort. v0.1 answered probes at effort=low and
        # composed at effort=high, so F* measured convergence toward an agent
        # that did not write the message being measured.
        self._composer = AnthropicAgent(
            name=self.name + "/composer", context=spec, model=model,
            effort=samples_effort, max_tokens=4096,
        )

    def answer_samples(self, probe, n_samples: int) -> List[str]:
        # Raw draw order, never round-tripped through a distribution: the
        # halves-split floor estimate depends on it.
        return self._prober.answer_samples(probe, n_samples)

    def claim_agreement(self, measure, counterpart: str, artifact=None,
                        n_elicitations: int = 3, seed: int = 0):
        return self._prober.claim_agreement(
            measure, counterpart, artifact, n_elicitations, seed
        )

    def compose(self, prompt: str) -> str:
        import anthropic  # noqa: F401  (import checked in AnthropicAgent)

        response = self._composer._client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=[{
                "type": "text",
                "text": "You are handing work off to a colleague who will see "
                        "only what you write.",
            }, {
                "type": "text",
                "text": self._composer.context,
                "cache_control": {"type": "ephemeral"},
            }],
            output_config={"effort": self._composer.effort},
            messages=[{"role": "user", "content": prompt}],
        )
        if response.stop_reason == "refusal":
            raise RuntimeError("sender declined to compose the brief")
        return "".join(b.text for b in response.content if b.type == "text").strip()

    def cost_of(self, message: str) -> int:
        return self._prober.cost_of(message)


class _LiveReceiver(object):
    def __init__(self, label: str, context: str, model: str, effort: str = "low"):
        self.name = "%s/%s" % (model, label)
        self._agent = AnthropicAgent(
            name=self.name, context=context, model=model, effort=effort
        )

    def answer_samples(self, probe, n_samples: int) -> List[str]:
        return self._agent.answer_samples(probe, n_samples)

    def claim_agreement(self, measure, counterpart: str, artifact=None,
                        n_elicitations: int = 3, seed: int = 0):
        return self._agent.claim_agreement(
            measure, counterpart, artifact, n_elicitations, seed
        )

    def cost_of(self, message: str) -> int:
        return self._agent.cost_of(message)


# --------------------------------------------------------------------------
# core


class SampleCache(object):
    """On-disk cache of raw draws, so a failed run does not discard its calls.

    Keyed by (condition label, probe id). Draw order is preserved verbatim --
    the halves-split floor estimate depends on it, so the cache stores sample
    lists, never distributions.
    """

    def __init__(self, path: Optional[str]):
        self.path = path
        self._data: Dict[str, Dict[str, List[str]]] = {}
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                self._data = json.load(fh)

    def get(self, label: str, probe_id: str, n: int) -> Optional[List[str]]:
        cached = self._data.get(label, {}).get(probe_id)
        if cached is not None and len(cached) == n:
            return list(cached)
        return None

    def put(self, label: str, probe_id: str, samples: Sequence[str]) -> None:
        self._data.setdefault(label, {})[probe_id] = list(samples)
        if self.path:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh)

    def count(self) -> int:
        return sum(len(v) for v in self._data.values())


def collect(
    agent,
    measure: ProbeMeasure,
    n_samples: int,
    label: str,
    verbose: bool,
    cache: Optional["SampleCache"] = None,
):
    """Sample every probe. Returns (full dists, modes, raw draws).

    The half-splits the v0.1 floor needed are gone: the permutation floor is
    computed from the full draws, at the same n as the divergence it corrects.
    """
    full, modes, raws = [], [], []
    for index, probe in enumerate(measure, 1):
        samples = cache.get(label, probe.id, n_samples) if cache else None
        if samples is None:
            samples = agent.answer_samples(probe, n_samples)
            if cache:
                cache.put(label, probe.id, samples)
        full.append(to_distribution(samples))
        modes.append(max(sorted(full[-1]), key=lambda k: full[-1][k]))
        raws.append(list(samples))
        if verbose:
            sys.stderr.write("\r  %-12s %d/%d" % (label, index, len(measure)))
            sys.stderr.flush()
    if verbose:
        sys.stderr.write("\r  %-12s %d/%d  done\n" % (label, len(measure), len(measure)))
    return full, modes, raws


def run(args) -> Dict[str, Any]:
    measure = load_probe_measure(os.path.join(HERE, "probes.json"))
    with open(os.path.join(HERE, "source-spec.md"), "r", encoding="utf-8") as fh:
        spec = fh.read()

    n = args.samples
    if n < 4:
        raise SystemExit("--samples must be at least 4")

    print("E-001 The Cost of Fluency")
    print("probe measure : %s (%d probes)" % (measure.qualified_id, len(measure)))
    print("samples/probe : %d   mode: %s" % (n, "DRY RUN" if args.dry_run else "live"))
    print("models        : sender=%s receiver=%s" % (args.sender_model, args.receiver_model))
    print()

    # Cache keys carry the model: samples drawn from one model must never be
    # reused for another. A stale cache across a model change would silently
    # compare an agent against draws it never made.
    def key(label: str) -> str:
        return "%s@%s/%s" % (label, args.sender_model, args.receiver_model)

    cache = SampleCache(args.cache)
    if cache.count():
        print("resuming from cache: %s (%d conditions already collected)\n"
              % (args.cache, cache.count()))

    if args.dry_run:
        sender = _StubAgent("stub-sender", accuracy=0.93, claim=0.88, seed=1)
    else:
        sender = _LiveSender(spec, args.sender_model)

    # --- messages FIRST ---------------------------------------------------
    # Composition is the step most likely to fail outright (a safety
    # classifier can decline it, as the KESTREL-34 domain did). Doing it
    # before the ~200-call probe sweep means such a failure costs two calls
    # rather than discarding the whole sweep. See AMENDMENT-001.md.
    messages = {}
    for label, template in (
        ("NARRATIVE", NARRATIVE_PROMPT), ("CONTRASTIVE", CONTRASTIVE_PROMPT)
    ):
        try:
            messages[label] = sender.compose(
                template.format(budget=MESSAGE_BUDGET_TOKENS)
            )
        except RuntimeError as exc:
            # VOID GATE. A condition whose message failed to generate must
            # never contribute a zero-fidelity data point: an empty message
            # scores F* ~ 0 and would read as a large, clean, significant
            # effect against whichever condition was blocked. Refusal is
            # missing data, not evidence. See AMENDMENT-001.md and
            # journal/2026-07-28-first-live-run-void.md.
            return {
                "experiment": "E-001",
                "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "dry_run": bool(args.dry_run),
                "probe_measure": measure.qualified_id,
                "void": True,
                "void_reason": "message generation failed for condition %s: %s"
                               % (label, exc),
                "conditions_composed": sorted(messages),
            }
    print("  composed NARRATIVE (%d chars) and CONTRASTIVE (%d chars)\n"
          % (len(messages["NARRATIVE"]), len(messages["CONTRASTIVE"])))

    # --- sender probes ----------------------------------------------------
    s_full, s_modes, s_raw = collect(
        sender, measure, n, key("sender"), args.verbose, cache
    )
    raw_draws: Dict[str, List[List[str]]] = {"sender": s_raw}
    sender_accuracy = measure.accuracy(s_modes)

    # --- receivers -------------------------------------------------------
    contexts = {
        "PRIOR": "",
        "NARRATIVE": messages["NARRATIVE"],
        "CONTRASTIVE": messages["CONTRASTIVE"],
        "CEILING": spec,
    }

    receivers, collected = {}, {}
    for index, (label, context) in enumerate(contexts.items()):
        if args.dry_run:
            faked = {"PRIOR": 0.30, "NARRATIVE": 0.66, "CONTRASTIVE": 0.78, "CEILING": 0.92}
            claim = {"PRIOR": 0.30, "NARRATIVE": 0.86, "CONTRASTIVE": 0.72, "CEILING": 0.93}
            receivers[label] = _StubAgent(
                "stub-" + label.lower(), faked[label], claim[label], seed=100 + index
            )
        else:
            receivers[label] = _LiveReceiver(label.lower(), context, args.receiver_model)
        collected[label] = collect(
            receivers[label], measure, n, key(label.lower()), args.verbose, cache
        )
        raw_draws[label] = collected[label][2]

    costs = {
        label: receivers["PRIOR"].cost_of(messages[label]) for label in messages
    }

    # --- quantities ------------------------------------------------------
    #
    # ONE floor for the whole experiment, not one per condition. v0.1 computed
    # each condition's floor from that condition's own receiver, so
    # F*(NARRATIVE) and F*(CONTRASTIVE) had DIFFERENT denominators -- and
    # perversely, a noisier receiver earned a higher floor, a smaller
    # denominator and therefore a higher fidelity. On the cached run that
    # asymmetry alone inflated the H1 margin by ~17%. The floor belongs to the
    # comparison in the denominator, so it is the null for sender-vs-PRIOR, and
    # every condition is now scored against the same one.
    d_prior = mean_divergence(s_full, collected["PRIOR"][0], measure.weights)
    floor = mean_permutation_floor(
        raw_draws["sender"], raw_draws["PRIOR"], measure.weights, 300, SEED
    )

    admissible = (d_prior - floor) > args.epsilon
    results: Dict[str, Any] = {
        "experiment": "E-001",
        "core_version": "0.3",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dry_run": bool(args.dry_run),
        "probe_measure": measure.qualified_id,
        "n_probes": len(measure),
        "samples_per_probe": n,
        "sender_model": args.sender_model,
        "receiver_model": args.receiver_model,
        "message_budget_tokens": MESSAGE_BUDGET_TOKENS,
        "sender_accuracy_vs_key": sender_accuracy,
        "sender_errors": [
            measure.probes[i].id
            for i, (p, a) in enumerate(zip(measure, s_modes)) if a != p.key
        ],
        "d_prior": d_prior,
        "d_floor_common": floor,
        "floor_method": "permutation-null on sender vs PRIOR, shared by all conditions",
        "admissible": admissible,
        "epsilon": args.epsilon,
        "messages": messages,
        "message_costs_tokens": costs,
        # The reproducibility bundle: without raw draws nothing above can be
        # recomputed, and a result that cannot be recomputed is an assertion.
        "raw_draws": raw_draws,
        "conditions": {},
        "gates": {},
        "tests": {},
    }

    if not admissible:
        results["aborted"] = (
            "inadmissible probe measure: prior gap %.4f does not exceed floor "
            "%.4f by epsilon %.4f" % (d_prior, floor, args.epsilon)
        )
        return results

    per_probe: Dict[str, List[float]] = {}
    for label in ("NARRATIVE", "CONTRASTIVE", "CEILING"):
        full, modes, _ = collected[label]
        d_post = mean_divergence(s_full, full, measure.weights)
        per_probe[label] = [
            mean_divergence([a], [b]) for a, b in zip(s_full, full)
        ]

        claims_s = claims_r = None
        if label in messages:
            claims_s = sender.claim_agreement(
                measure, "your colleague", artifact=messages[label]
            )
            claims_r = receivers[label].claim_agreement(
                measure, "the person who briefed you"
            )

        observed = agreement_rate(s_full, full, measure.weights)
        try:
            fidelity = transfer_fidelity(d_prior, d_post, floor, args.epsilon)
        except InadmissibleProbeMeasure as exc:
            results["conditions"][label] = {"error": str(exc)}
            continue

        cost = float(costs.get(label, receivers["PRIOR"].cost_of(spec)))
        entry = {
            "d_post": d_post,
            "fidelity": fidelity,
            "efficiency_per_ktok": fidelity * 1000.0 / cost,
            "cost_tokens": cost,
            "cost_unit": "tokens",
            "agreement_observed": observed,
            "accuracy_vs_key": measure.accuracy(modes),
        }
        if claims_s is not None:
            claimed = (sum(claims_s) / len(claims_s) + sum(claims_r) / len(claims_r)) / 2
            entry.update({
                "claims_sender": claims_s,
                "claims_receiver": claims_r,
                "claimed_agreement": claimed,
                "phi": claimed - observed,
                "phi_sender": sum(claims_s) / len(claims_s) - observed,
                "phi_receiver": sum(claims_r) / len(claims_r) - observed,
            })
        # v0.3: the aggregate alone is a methodological error.
        try:
            dec = decompose(
                measure, raw_draws["sender"], raw_draws["PRIOR"], raw_draws[label]
            )
            entry["decomposition"] = dec._asdict()
        except ValueError as exc:
            entry["decomposition_error"] = str(exc)
        results["conditions"][label] = entry
        print("  %-12s F*=%+.3f  A=%.3f  %s"
              % (label, fidelity, observed,
                 entry.get("decomposition", {}).get("error_replication", "")))

    # --- pre-registered tests --------------------------------------------
    #
    # With a common floor, F* is a strictly decreasing affine function of
    # D_post, so a test on per-probe divergence differences IS a test of the
    # fidelity ordering. In v0.1 the floors differed by condition and the test
    # therefore addressed a different statistic than the verdict it decorated.
    diffs = [n_ - c for n_, c in zip(per_probe["NARRATIVE"], per_probe["CONTRASTIVE"])]
    observed_diff, p_h1 = permutation_test(diffs)
    mean_d, lo_d, hi_d = bootstrap_ci(diffs)
    results["tests"]["H1"] = {
        "statistic": "per-probe divergence, NARRATIVE minus CONTRASTIVE",
        "mean_difference": observed_diff,
        "p_value": p_h1,
        "bootstrap_ci95": [lo_d, hi_d],
        "permutations": PERMUTATIONS,
        "seed": SEED,
        "note": "valid as a test of the F* ordering only because the floor is shared",
    }

    # H2 had no test at all in v0.1 -- the hypothesis was adjudicated by
    # eyeballing a margin. Phi's per-probe term is the agreement indicator, so
    # it bootstraps; the claims are scalars and enter as constants.
    nar, con = results["conditions"]["NARRATIVE"], results["conditions"]["CONTRASTIVE"]
    if "phi" in nar and "phi" in con:
        ind_n = [1.0 if _mode_of(a) == _mode_of(b) else 0.0
                 for a, b in zip(s_full, collected["NARRATIVE"][0])]
        ind_c = [1.0 if _mode_of(a) == _mode_of(b) else 0.0
                 for a, b in zip(s_full, collected["CONTRASTIVE"][0])]
        phi_diffs = [
            (nar["claimed_agreement"] - a) - (con["claimed_agreement"] - b)
            for a, b in zip(ind_n, ind_c)
        ]
        _, p_h2 = permutation_test(phi_diffs, seed=SEED + 1)
        m_p, lo_p, hi_p = bootstrap_ci(phi_diffs, seed=SEED + 1)
        claim_gap = abs(nar["claimed_agreement"] - con["claimed_agreement"])
        results["tests"]["H2"] = {
            "statistic": "per-probe Phi contribution, NARRATIVE minus CONTRASTIVE",
            "mean_difference": m_p,
            "p_value": p_h2,
            "bootstrap_ci95": [lo_p, hi_p],
            "claim_gap": claim_gap,
            "degenerate_with_H1": claim_gap < 0.05,
            "note": (
                "if the claims barely differ by condition, Phi(N)-Phi(K) is "
                "-(A(N)-A(K)) and H2 is H1 measured with a coarser statistic; "
                "the pre-registration's no-multiplicity-correction argument "
                "does not survive that case"
            ),
        }

    fid = {k: results["conditions"][k].get("fidelity") for k in ("NARRATIVE", "CONTRASTIVE")}
    phi = {k: results["conditions"][k].get("phi") for k in fid}
    eff = {k: results["conditions"][k].get("efficiency_per_ktok") for k in fid}
    cost_gap = abs(costs["NARRATIVE"] - costs["CONTRASTIVE"]) / max(costs.values())
    cost_parity = cost_gap <= 0.15

    n_errors = len(results["sender_errors"])
    results["gates"] = {
        "sender_accuracy": {
            "value": sender_accuracy, "threshold": SENDER_ACCURACY_GATE,
            "passed": bool(sender_accuracy is not None
                           and sender_accuracy > SENDER_ACCURACY_GATE),
        },
        "sender_error_count": {
            "value": n_errors, "threshold": SENDER_MAX_ERRORS,
            "passed": bool(n_errors <= SENDER_MAX_ERRORS),
            "note": "a mean-accuracy gate cannot protect an effect that "
                    "concentrates on the sender's few wrong probes",
        },
        "ceiling_fidelity": {
            "value": results["conditions"].get("CEILING", {}).get("fidelity"),
            "threshold": CEILING_FIDELITY_GATE,
            "passed": bool((results["conditions"].get("CEILING", {}).get("fidelity")
                            or -1) > CEILING_FIDELITY_GATE),
        },
        "cost_parity": {
            "relative_gap": cost_gap, "threshold": 0.15, "passed": bool(cost_parity),
        },
    }

    # The pre-registration promised this substitution; v0.1 computed the gate
    # and then ignored it. It is applied here, and recorded as applied.
    h1_metric = "fidelity" if cost_parity else "efficiency_per_ktok"
    h1_values = fid if cost_parity else eff
    results["hypotheses"] = {
        "H1_contrastive_higher": dict(
            _verdict(h1_values["CONTRASTIVE"], h1_values["NARRATIVE"]),
            metric=h1_metric,
            metric_substituted=not cost_parity,
        ),
        "H2_narrative_higher_phantom": _verdict(phi["NARRATIVE"], phi["CONTRASTIVE"]),
    }
    return results


def _mode_of(dist):
    return max(sorted(dist), key=lambda k: dist[k])


def _verdict(predicted_larger: Optional[float], predicted_smaller: Optional[float]):
    if predicted_larger is None or predicted_smaller is None:
        return {"direction_holds": None, "margin": None}
    return {
        "direction_holds": bool(predicted_larger > predicted_smaller),
        "margin": predicted_larger - predicted_smaller,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="E-001 The Cost of Fluency")
    parser.add_argument("--dry-run", action="store_true",
                        help="verify the pipeline with stub agents, no API calls")
    parser.add_argument("--samples", type=int, default=30,
                        help="samples per probe (even, >=4). Default 30: "
                             "synthetic validation shows n=6 carries ~0.11 of "
                             "estimator error, which is not a measurement")
    parser.add_argument("--sender-model", default=DEFAULT_MODEL)
    parser.add_argument("--receiver-model", default=DEFAULT_MODEL)
    parser.add_argument("--epsilon", type=float, default=0.02)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--cache", default=os.path.join(HERE, ".sample-cache.json"),
                        help="resumable raw-sample cache; delete it to force a fresh run")
    parser.add_argument("--out", default=os.path.join(HERE, "results"))
    args = parser.parse_args()

    results = run(args)

    os.makedirs(args.out, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    path = os.path.join(
        args.out, "E-001-%s%s.json" % (stamp, "-dryrun" if args.dry_run else "")
    )
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print()
    if results.get("void"):
        print("VOID: %s" % results["void_reason"])
        print("No fidelity was measured. This run bears on no hypothesis.")
    elif results.get("aborted"):
        print("ABORTED: %s" % results["aborted"])
    else:
        for name, verdict in results["hypotheses"].items():
            holds = verdict["direction_holds"]
            mark = "?" if holds is None else ("holds" if holds else "FAILS")
            print("  %-38s %-6s (margin %+.4f)" % (name, mark, verdict["margin"] or 0.0))
        for hid in ("H1", "H2"):
            t = results["tests"].get(hid)
            if t:
                print("  %s  p = %.4f  CI95 [%+.4f, %+.4f]%s"
                      % (hid, t["p_value"], t["bootstrap_ci95"][0],
                         t["bootstrap_ci95"][1],
                         "  DEGENERATE WITH H1" if t.get("degenerate_with_H1") else ""))
        gates = results["gates"]
        failed = [k for k, v in gates.items() if not v["passed"]]
        print("  gates failed: %s" % (", ".join(failed) if failed else "none"))
    print("\nwrote %s" % path)
    if results.get("dry_run"):
        print("DRY RUN -- numbers above are synthetic and carry no scientific weight.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
