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
    Measurement,
    ProbeMeasure,
    agreement_rate,
    load_probe_measure,
    mean_divergence,
    noise_floor,
    to_distribution,
    transfer_fidelity,
)
from noophorics.agents import DEFAULT_MODEL, AnthropicAgent  # noqa: E402

MESSAGE_BUDGET_TOKENS = 350
PERMUTATIONS = 10_000
SEED = 20260728
SENDER_ACCURACY_GATE = 0.85
CEILING_FIDELITY_GATE = 0.70

NARRATIVE_PROMPT = """You have been given a set of eligibility rules. A colleague \
must decide real cases using these rules, and will see nothing except what you \
write. Write them a handover brief.

Write it as fluent, well-organized explanatory prose. Use clear paragraphs and \
connective reasoning, the way you would brief a capable new colleague you \
respect. Make it read well.

Hard limit: {budget} tokens. Write the brief and nothing else."""

CONTRASTIVE_PROMPT = """You have been given a set of eligibility rules. A colleague \
must decide real cases using these rules, and will see nothing except what you \
write. Write them a handover brief.

Write ONLY the boundaries: the edge cases, the exclusions, the places where a \
reasonable person would guess wrong, what does NOT follow from what, and which \
rules override which. No prose, no introduction, no summary of the general \
picture. Terse lines. If a fact would not change anyone's verdict on any case, \
leave it out.

Hard limit: {budget} tokens. Write the brief and nothing else."""


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


def split_halves(samples: Sequence[str]) -> Tuple[List[str], List[str]]:
    mid = len(samples) // 2
    return list(samples[:mid]), list(samples[mid:])


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

    def claim_agreement(self, measure, counterpart: str) -> float:
        return self._claim

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
        self._composer = AnthropicAgent(
            name=self.name + "/composer", context=spec, model=model,
            effort="high", max_tokens=4096,
        )

    def answer_samples(self, probe, n_samples: int) -> List[str]:
        # Raw draw order, never round-tripped through a distribution: the
        # halves-split floor estimate depends on it.
        return self._prober.answer_samples(probe, n_samples)

    def claim_agreement(self, measure, counterpart: str) -> float:
        return self._prober.claim_agreement(measure, counterpart)

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
            output_config={"effort": "high"},
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

    def claim_agreement(self, measure, counterpart: str) -> float:
        return self._agent.claim_agreement(measure, counterpart)

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
    """Sample every probe. Returns (full dists, half-A dists, half-B dists, modes)."""
    full, half_a, half_b, modes = [], [], [], []
    for index, probe in enumerate(measure, 1):
        samples = cache.get(label, probe.id, n_samples) if cache else None
        if samples is None:
            samples = agent.answer_samples(probe, n_samples)
            if cache:
                cache.put(label, probe.id, samples)
        a, b = split_halves(samples)
        full.append(to_distribution(samples))
        half_a.append(to_distribution(a))
        half_b.append(to_distribution(b))
        modes.append(max(sorted(full[-1]), key=lambda k: full[-1][k]))
        if verbose:
            sys.stderr.write("\r  %-12s %d/%d" % (label, index, len(measure)))
            sys.stderr.flush()
    if verbose:
        sys.stderr.write("\r  %-12s %d/%d  done\n" % (label, len(measure), len(measure)))
    return full, half_a, half_b, modes


def run(args) -> Dict[str, Any]:
    measure = load_probe_measure(os.path.join(HERE, "probes.json"))
    with open(os.path.join(HERE, "source-spec.md"), "r", encoding="utf-8") as fh:
        spec = fh.read()

    n = args.samples
    if n < 4 or n % 2 != 0:
        raise SystemExit("--samples must be an even number >= 4 (halves for the floor)")

    print("E-001 The Cost of Fluency")
    print("probe measure : %s (%d probes)" % (measure.qualified_id, len(measure)))
    print("samples/probe : %d   mode: %s" % (n, "DRY RUN" if args.dry_run else "live"))
    print("models        : sender=%s receiver=%s" % (args.sender_model, args.receiver_model))
    print()

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
    s_full, s_a, s_b, s_modes = collect(
        sender, measure, n, "sender", args.verbose, cache
    )
    sender_accuracy = measure.accuracy(s_modes)
    d_self_sender = mean_divergence(s_a, s_b, measure.weights)

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
            receivers[label], measure, n, label.lower(), args.verbose, cache
        )

    costs = {
        label: receivers["PRIOR"].cost_of(messages[label]) for label in messages
    }

    # --- quantities ------------------------------------------------------
    d_prior = mean_divergence(s_full, collected["PRIOR"][0], measure.weights)
    floor_prior = noise_floor(
        d_self_sender,
        mean_divergence(collected["PRIOR"][1], collected["PRIOR"][2], measure.weights),
    )

    admissible = (d_prior - floor_prior) > args.epsilon
    results: Dict[str, Any] = {
        "experiment": "E-001",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dry_run": bool(args.dry_run),
        "probe_measure": measure.qualified_id,
        "n_probes": len(measure),
        "samples_per_probe": n,
        "sender_model": args.sender_model,
        "receiver_model": args.receiver_model,
        "message_budget_tokens": MESSAGE_BUDGET_TOKENS,
        "sender_accuracy_vs_key": sender_accuracy,
        "d_self_sender": d_self_sender,
        "d_prior": d_prior,
        "d_floor_prior": floor_prior,
        "admissible": admissible,
        "epsilon": args.epsilon,
        "messages": messages,
        "message_costs_tokens": costs,
        "conditions": {},
        "gates": {},
        "tests": {},
    }

    if not admissible:
        results["aborted"] = (
            "inadmissible probe measure: prior gap %.4f does not exceed floor "
            "%.4f by epsilon %.4f" % (d_prior, floor_prior, args.epsilon)
        )
        return results

    per_probe_divergence: Dict[str, List[float]] = {}
    for label in ("NARRATIVE", "CONTRASTIVE", "CEILING"):
        full, half_a, half_b, modes = collected[label]
        d_post = mean_divergence(s_full, full, measure.weights)
        floor = noise_floor(
            d_self_sender, mean_divergence(half_a, half_b, measure.weights)
        )
        per_probe_divergence[label] = [
            mean_divergence([s], [r]) for s, r in zip(s_full, full)
        ]

        claim_s = claim_r = None
        if label in messages:
            claim_s = sender.claim_agreement(measure, "your colleague")
            claim_r = receivers[label].claim_agreement(measure, "the person who briefed you")

        try:
            measurement = Measurement(
                probe_measure_id=measure.qualified_id,
                samples_per_probe=n,
                sender=getattr(sender, "name", "sender"),
                receiver=receivers[label].name,
                d_prior=d_prior,
                d_post=d_post,
                d_floor=floor,
                cost_tokens=float(costs.get(label, len(spec.split()))),
                cost_unit="tokens",
                agreement_observed=agreement_rate(s_full, full, measure.weights),
                claim_sender=claim_s,
                claim_receiver=claim_r,
                condition=label,
            )
            entry = measurement._asdict()
            entry.update({
                "fidelity": measurement.fidelity,
                "efficiency_per_ktok": measurement.efficiency,
                "phantom_agreement": measurement.phantom,
                "is_antinoophor": measurement.is_antinoophor,
                "accuracy_vs_key": measure.accuracy(modes),
            })
            print("  " + measurement.summary())
        except InadmissibleProbeMeasure as exc:
            entry = {"error": str(exc)}
        results["conditions"][label] = entry

    # --- pre-registered tests --------------------------------------------
    diffs = [
        nar - con
        for nar, con in zip(
            per_probe_divergence["NARRATIVE"], per_probe_divergence["CONTRASTIVE"]
        )
    ]
    observed, p_value = permutation_test(diffs)
    results["tests"]["H1_divergence_narrative_minus_contrastive"] = {
        "mean_difference": observed,
        "p_value": p_value,
        "permutations": PERMUTATIONS,
        "seed": SEED,
        "reading": "positive mean difference favours H1 (contrastive diverges less)",
    }

    fid = {k: results["conditions"][k].get("fidelity") for k in ("NARRATIVE", "CONTRASTIVE")}
    phi = {k: results["conditions"][k].get("phantom_agreement") for k in fid}
    eff = {k: results["conditions"][k].get("efficiency_per_ktok") for k in fid}
    cost_gap = abs(costs["NARRATIVE"] - costs["CONTRASTIVE"]) / max(costs.values())

    results["gates"] = {
        "sender_accuracy": {
            "value": sender_accuracy,
            "threshold": SENDER_ACCURACY_GATE,
            "passed": bool(sender_accuracy is not None and sender_accuracy > SENDER_ACCURACY_GATE),
        },
        "ceiling_fidelity": {
            "value": results["conditions"]["CEILING"].get("fidelity"),
            "threshold": CEILING_FIDELITY_GATE,
            "passed": bool((results["conditions"]["CEILING"].get("fidelity") or -1) > CEILING_FIDELITY_GATE),
        },
        "cost_parity": {
            "relative_gap": cost_gap,
            "threshold": 0.15,
            "passed": bool(cost_gap <= 0.15),
            "note": "if failed, H1 is evaluated on efficiency rather than raw fidelity",
        },
    }
    results["hypotheses"] = {
        "H1_contrastive_higher_fidelity": _verdict(fid["CONTRASTIVE"], fid["NARRATIVE"]),
        "H2_narrative_higher_phantom": _verdict(phi["NARRATIVE"], phi["CONTRASTIVE"]),
        "H3_contrastive_higher_efficiency": _verdict(eff["CONTRASTIVE"], eff["NARRATIVE"]),
    }
    return results


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
    parser.add_argument("--samples", type=int, default=6,
                        help="samples per probe (even, >=4); default 6")
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
        test = results["tests"]["H1_divergence_narrative_minus_contrastive"]
        print("  permutation test p = %.4f" % test["p_value"])
        gates = results["gates"]
        failed = [k for k, v in gates.items() if not v["passed"]]
        print("  gates failed: %s" % (", ".join(failed) if failed else "none"))
    print("\nwrote %s" % path)
    if results.get("dry_run"):
        print("DRY RUN -- numbers above are synthetic and carry no scientific weight.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
