#!/usr/bin/env python3
"""E-001b -- Fluency x Contrastiveness, factorial.

Runs the experiment pre-registered in PREREGISTRATION.md (k raised 4 -> 8 by
AMENDMENT-001, before any data existed). Read those first: the hypotheses and
analysis plan are fixed, and the amendment budget is one remaining.

    python3 runner.py --dry-run          # pipeline check, no API calls
    python3 runner.py --samples 30 --k 8 # real run, ~38k calls

The message is the unit of analysis. Probes are within-message noise.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "metrics"))
sys.path.insert(0, HERE)

from noophorics import (  # noqa: E402
    ProbeMeasure,
    agreement_rate,
    load_probe_measure,
    mean_divergence,
    mean_permutation_floor,
    to_distribution,
    transfer_fidelity,
)
from noophorics.agents import DEFAULT_MODEL, AnthropicAgent  # noqa: E402
from noophorics.codex_agent import CodexAgent, codex_available  # noqa: E402
from noophorics.decomposition import decompose  # noqa: E402
from prompts import CELL_AXES, CELLS  # noqa: E402

BUDGET_TOKENS = 350
PERMUTATIONS = 10_000
BOOTSTRAP = 5_000
SEED = 20260729
SENDER_ACCURACY_GATE = 0.90
SENDER_MAX_ERRORS = 2
CEILING_GATE = 0.70
COST_PARITY_MAX_RATIO = 1.30
H4_CI_MAX_WIDTH = 0.15


# --------------------------------------------------------------------------
# statistics -- message-level


def permutation_main_effect(
    group_a: Sequence[float], group_b: Sequence[float],
    permutations: int = PERMUTATIONS, seed: int = SEED,
) -> Tuple[float, float]:
    """Two-sided permutation test on a main effect. Exchangeable unit: message.

    Labels are permuted, not probes. E-001 permuted probes while the treatment
    had one message per condition, which tested a within-message quantity and
    reported it as a between-condition result.
    """
    a, b = [float(x) for x in group_a], [float(x) for x in group_b]
    if not a or not b:
        raise ValueError("empty group in main-effect test")
    observed = statistics.mean(a) - statistics.mean(b)
    pool, n_a = a + b, len(a)
    rng = random.Random(seed)
    extreme = 0
    for _ in range(permutations):
        rng.shuffle(pool)
        diff = statistics.mean(pool[:n_a]) - statistics.mean(pool[n_a:])
        if abs(diff) >= abs(observed) - 1e-15:
            extreme += 1
    return observed, (extreme + 1) / (permutations + 1)


def bootstrap_effect_ci(
    group_a: Sequence[float], group_b: Sequence[float],
    resamples: int = BOOTSTRAP, seed: int = SEED,
) -> Tuple[float, float, float]:
    """Percentile bootstrap CI for a difference of means, over messages."""
    a, b = list(group_a), list(group_b)
    rng = random.Random(seed)
    diffs = []
    for _ in range(resamples):
        ra = [a[rng.randrange(len(a))] for _ in a]
        rb = [b[rng.randrange(len(b))] for _ in b]
        diffs.append(statistics.mean(ra) - statistics.mean(rb))
    diffs.sort()
    return (
        statistics.mean(a) - statistics.mean(b),
        diffs[int(0.025 * resamples)],
        diffs[int(0.975 * resamples) - 1],
    )


# --------------------------------------------------------------------------
# cache


class Cache:
    """Tracked, resumable, thread-safe. Keyed by model, condition and probe."""

    def __init__(self, path: Optional[str]):
        self.path = path
        self._data: Dict[str, Dict[str, List[str]]] = {}
        self._lock = threading.Lock()
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                self._data = json.load(fh)

    def get(self, cond: str, probe_id: str, n: int) -> Optional[List[str]]:
        with self._lock:
            got = self._data.get(cond, {}).get(probe_id)
            return list(got) if got is not None and len(got) == n else None

    def put(self, cond: str, probe_id: str, samples: Sequence[str]) -> None:
        with self._lock:
            self._data.setdefault(cond, {})[probe_id] = list(samples)
            if self.path:
                tmp = self.path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as fh:
                    json.dump(self._data, fh)
                os.replace(tmp, self.path)


# --------------------------------------------------------------------------
# agents


class Stub:
    """Dry-run stand-in. Numbers are synthetic and the results file says so."""

    def __init__(self, name: str, accuracy: float, claim: float, seed: int):
        self.name, self._acc, self._claim = name, accuracy, claim
        self._rng = random.Random(seed)

    def answer_samples(self, probe, n: int) -> List[str]:
        return [
            probe.key if (self._rng.random() < self._acc and probe.key)
            else self._rng.choice(probe.options)
            for _ in range(n)
        ]

    def claim_agreement(self, measure, counterpart, artifact=None,
                        n_elicitations=3, seed=0) -> List[float]:
        return [max(0.0, min(1.0, self._claim + 0.02 * (i - 1)))
                for i in range(n_elicitations)]

    def cost_of(self, message: str) -> int:
        return max(1, len(message.split()))

    def compose(self, prompt: str, seed: int = 0) -> str:
        return "STUB(%s/%d): %s" % (self.name, seed, prompt.splitlines()[0][:40])


def _make_agent(provider: str, name: str, context: str, model: str, effort: str):
    """Provider selection. PREREGISTRATION 2.4 records the model per run rather
    than fixing one, so choosing a provider before any data exists is a run
    parameter and not an amendment."""
    if provider == "codex":
        if not codex_available():
            raise SystemExit("--provider codex but the codex CLI is not on PATH")
        return CodexAgent(name, context=context, reasoning_effort=effort)
    return AnthropicAgent(name, context=context, model=model, effort=effort)


class Sender:
    """One agent, one effort, both roles. See E-001's AMENDMENT-003."""

    def __init__(self, spec: str, model: str, effort: str = "low",
                 provider: str = "anthropic"):
        self.name = "%s/spec" % model
        self.model, self.spec, self.effort = model, spec, effort
        self.provider = provider
        self._agent = _make_agent(provider, self.name, spec, model, effort)

    def answer_samples(self, probe, n: int) -> List[str]:
        return self._agent.answer_samples(probe, n)

    def claim_agreement(self, measure, counterpart, artifact=None,
                        n_elicitations=3, seed=0) -> List[float]:
        return self._agent.claim_agreement(
            measure, counterpart, artifact, n_elicitations, seed
        )

    def cost_of(self, message: str) -> int:
        return self._agent.cost_of(message)

    def compose(self, prompt: str, seed: int = 0) -> str:
        """One generation, in a fresh request. Independence is per message."""
        if self.provider == "codex":
            return self._agent.compose(prompt, seed)
        response = self._agent._client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=[
                {"type": "text",
                 "text": "You are handing work off to a colleague who will see "
                         "only what you write."},
                {"type": "text", "text": self.spec,
                 "cache_control": {"type": "ephemeral"}},
            ],
            output_config={"effort": self.effort},
            messages=[{"role": "user", "content": prompt}],
        )
        if response.stop_reason == "refusal":
            raise RuntimeError(
                "sender declined to compose (category=%s)"
                % getattr(response.stop_details, "category", None)
            )
        return "".join(b.text for b in response.content if b.type == "text").strip()


class Receiver:
    def __init__(self, label: str, context: str, model: str, effort: str = "low",
                 provider: str = "anthropic"):
        self.name = "%s/%s" % (model, label)
        self._agent = _make_agent(provider, self.name, context, model, effort)

    def answer_samples(self, probe, n: int) -> List[str]:
        return self._agent.answer_samples(probe, n)

    def claim_agreement(self, measure, counterpart, artifact=None,
                        n_elicitations=3, seed=0) -> List[float]:
        return self._agent.claim_agreement(
            measure, counterpart, artifact, n_elicitations, seed
        )

    def cost_of(self, message: str) -> int:
        return self._agent.cost_of(message)


# --------------------------------------------------------------------------
# collection


def collect_concurrent(
    agent, measure: ProbeMeasure, n: int, cond: str, cache: Cache,
    workers: int, progress: Optional[Dict[str, int]] = None,
) -> List[List[str]]:
    """Sample every probe for one condition. Probes run in parallel.

    Parallelism is at the PROBE level, never within a probe: the n draws for a
    single probe stay sequential so their order is the order they were drawn in.
    """
    out: List[Optional[List[str]]] = [None] * len(measure)

    def one(index: int) -> Tuple[int, List[str]]:
        probe = measure.probes[index]
        cached = cache.get(cond, probe.id, n)
        if cached is not None:
            return index, cached
        samples = agent.answer_samples(probe, n)
        cache.put(cond, probe.id, samples)
        return index, samples

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for future in as_completed([pool.submit(one, i) for i in range(len(measure))]):
            index, samples = future.result()
            out[index] = samples
            if progress is not None:
                progress["done"] += 1
                sys.stderr.write("\r  %s  %d/%d probe-conditions"
                                 % (cond[:28].ljust(28), progress["done"], progress["total"]))
                sys.stderr.flush()
    return [s for s in out if s is not None]


# --------------------------------------------------------------------------


def run(args) -> Dict[str, Any]:
    measure = load_probe_measure(os.path.join(REPO, "experiments",
                                              "E-001-fluency-cost", "probes.json"))
    with open(os.path.join(REPO, "experiments", "E-001-fluency-cost",
                           "source-spec.md"), "r", encoding="utf-8") as fh:
        spec = fh.read()

    n, k = args.samples, args.k
    if n < 4:
        raise SystemExit("--samples must be at least 4")

    print("E-001b  Fluency x Contrastiveness")
    print("measure   : %s (%d probes)" % (measure.qualified_id, len(measure)))
    print("design    : 4 cells x k=%d messages, n=%d samples/probe" % (k, n))
    print("provider  : %s" % args.provider)
    print("model     : %s (both roles)" % (
        "codex CLI default" if args.provider == "codex" else args.model))
    print("mode      : %s\n" % ("DRY RUN" if args.dry_run else "live"))

    cache = Cache(args.cache)
    sender = (Stub("stub-sender", 0.94, 0.88, 1) if args.dry_run
              else Sender(spec, args.model, provider=args.provider))

    # --- compose first: a refusal must cost k calls, not the whole sweep ----
    messages: Dict[str, str] = {}
    for cell, prompt in sorted(CELLS.items()):
        for i in range(k):
            label = "%s%d" % (cell, i)
            try:
                messages[label] = sender.compose(
                    prompt.format(budget=BUDGET_TOKENS), seed=i
                )
            except RuntimeError as exc:
                return {
                    "experiment": "E-001b", "void": True,
                    "void_reason": "composition failed for %s: %s" % (label, exc),
                    "composed": sorted(messages),
                }
    print("  composed %d messages across %d cells\n" % (len(messages), len(CELLS)))

    # --- conditions --------------------------------------------------------
    contexts = {"sender": spec, "PRIOR": "", "CEILING": spec}
    contexts.update(messages)

    total_units = len(contexts) * len(measure)
    progress = {"done": 0, "total": total_units}
    raw: Dict[str, List[List[str]]] = {}
    for label, ctx in contexts.items():
        agent = (Stub("stub-" + label, 0.5 + 0.45 * (label != "PRIOR"), 0.8, hash(label) % 999)
                 if args.dry_run
                 else (sender if label == "sender"
                       else Receiver(label, ctx, args.model, provider=args.provider)))
        raw[label] = collect_concurrent(
            agent, measure, n, "%s@%s" % (label, args.model), cache,
            args.workers, progress,
        )
    sys.stderr.write("\n\n")

    # --- shared floor and denominator -------------------------------------
    s_dists = [to_distribution(d) for d in raw["sender"]]
    p_dists = [to_distribution(d) for d in raw["PRIOR"]]
    d_prior = mean_divergence(s_dists, p_dists, measure.weights)
    floor = mean_permutation_floor(raw["sender"], raw["PRIOR"], measure.weights, 300, SEED)

    s_modes = [max(sorted(d), key=lambda x: d[x]) for d in s_dists]
    errors = [p.id for p, m in zip(measure, s_modes) if m != p.key]
    sender_acc = measure.accuracy(s_modes)

    results: Dict[str, Any] = {
        "experiment": "E-001b", "core_version": "0.3",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dry_run": bool(args.dry_run), "probe_measure": measure.qualified_id,
        "provider": args.provider,
        "model": ("codex-cli-default" if args.provider == "codex" else args.model),
        "cost_unit": ("approx-tokens-from-words" if args.provider == "codex"
                      else "tokens"),
        "k": k, "samples_per_probe": n,
        "cell_axes": CELL_AXES, "messages": messages,
        "d_prior": d_prior, "d_floor_shared": floor,
        "sender_accuracy": sender_acc, "sender_errors": errors,
        "raw_draws": raw, "per_message": {}, "effects": {}, "gates": {},
    }
    if (d_prior - floor) <= args.epsilon:
        results["aborted"] = "inadmissible: gap %.4f <= epsilon" % (d_prior - floor)
        return results

    # --- per message -------------------------------------------------------
    for label in sorted(messages):
        cell = label[0]
        post = raw[label]
        d_post = mean_divergence(s_dists, [to_distribution(d) for d in post], measure.weights)
        dec = decompose(measure, raw["sender"], raw["PRIOR"], post)
        observed = agreement_rate(s_dists, [to_distribution(d) for d in post], measure.weights)
        cost = float(sender.cost_of(messages[label]))
        cs = sender.claim_agreement(measure, "your colleague", artifact=messages[label])
        cr = (Stub("stub-r", 0.9, 0.8, 7) if args.dry_run
              else Receiver(label, messages[label], args.model,
                            provider=args.provider)).claim_agreement(
                  measure, "the person who briefed you")
        claimed = (statistics.mean(cs) + statistics.mean(cr)) / 2
        results["per_message"][label] = {
            "cell": cell, "polish": CELL_AXES[cell][0], "selection": CELL_AXES[cell][1],
            "d_post": d_post,
            "fidelity_aggregate": transfer_fidelity(d_prior, d_post, floor, args.epsilon),
            "fidelity_where_sender_right": dec.fidelity_where_sender_right,
            "error_replication": dec.error_replication,
            "rule_content": dec.rule_content,
            "accuracy_gain": dec.accuracy_gain,
            "agreement_observed": observed,
            "claims_sender": cs, "claims_receiver": cr,
            "phi": claimed - observed,
            "phi_sender": statistics.mean(cs) - observed,
            "phi_receiver": statistics.mean(cr) - observed,
            "cost_tokens": cost,
            "efficiency_per_ktok": dec.fidelity_where_sender_right * 1000.0 / cost,
        }

    # --- main effects, message as unit -------------------------------------
    def margin(axis: int, value: str) -> List[str]:
        return [m for m in results["per_message"]
                if CELL_AXES[m[0]][axis] == value]

    def effect(name: str, quantity: str, axis: int, hi: str, lo: str) -> None:
        a = [results["per_message"][m][quantity] for m in margin(axis, hi)]
        b = [results["per_message"][m][quantity] for m in margin(axis, lo)]
        obs, p = permutation_main_effect(a, b)
        mean, lo95, hi95 = bootstrap_effect_ci(a, b)
        results["effects"][name] = {
            "quantity": quantity, "contrast": "%s minus %s" % (hi, lo),
            "effect": obs, "p_value": p, "ci95": [lo95, hi95],
            "ci_width": hi95 - lo95, "n_messages": [len(a), len(b)],
        }

    effect("H1_contrastiveness_on_understanding",
           "fidelity_where_sender_right", 1, "contrastive", "declarative")
    effect("H2_fluency_on_phantom", "phi", 0, "fluent", "terse")
    effect("H3_contrastiveness_on_efficiency",
           "efficiency_per_ktok", 1, "contrastive", "declarative")
    effect("H4_fluency_on_understanding",
           "fidelity_where_sender_right", 0, "fluent", "terse")

    h4 = results["effects"]["H4_fluency_on_understanding"]
    results["effects"]["H4_fluency_on_understanding"]["predicted_null_survives"] = bool(
        h4["ci95"][0] <= 0.0 <= h4["ci95"][1] and h4["ci_width"] < H4_CI_MAX_WIDTH
    )
    results["effects"]["H4_fluency_on_understanding"]["note"] = (
        "a wide CI containing zero is not evidence of no effect; the width gate "
        "is why this is not adjudicated by failure to reject"
    )

    # Degeneracy: if claims barely move, Phi is -A and H2 restates H1.
    claims = [results["per_message"][m]["claims_sender"][0] for m in results["per_message"]]
    gap = max(claims) - min(claims)
    results["effects"]["H2_fluency_on_phantom"]["claim_spread"] = gap
    results["effects"]["H2_fluency_on_phantom"]["degenerate_with_H1"] = gap < 0.05

    # --- gates -------------------------------------------------------------
    costs = [results["per_message"][m]["cost_tokens"] for m in results["per_message"]]
    ceil_f = transfer_fidelity(
        d_prior,
        mean_divergence(s_dists, [to_distribution(d) for d in raw["CEILING"]], measure.weights),
        floor, args.epsilon,
    )
    results["gates"] = {
        "sender_accuracy": {"value": sender_acc, "threshold": SENDER_ACCURACY_GATE,
                            "passed": bool(sender_acc > SENDER_ACCURACY_GATE)},
        "sender_error_count": {"value": len(errors), "threshold": SENDER_MAX_ERRORS,
                               "passed": bool(len(errors) <= SENDER_MAX_ERRORS)},
        "ceiling_fidelity": {"value": ceil_f, "threshold": CEILING_GATE,
                             "passed": bool(ceil_f > CEILING_GATE)},
        "cost_parity": {"ratio": max(costs) / min(costs), "threshold": COST_PARITY_MAX_RATIO,
                        "passed": bool(max(costs) / min(costs) <= COST_PARITY_MAX_RATIO)},
    }
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="E-001b factorial")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--smoke", action="store_true",
                    help="instrument check below pre-registered parameters. "
                         "Stamps the results file as non-inferential: a run at "
                         "reduced k or n cannot support any hypothesis, and a "
                         "file in results/ without this marker could later be "
                         "mistaken for the experiment")
    ap.add_argument("--samples", type=int, default=30)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--provider", choices=("anthropic", "codex"), default="anthropic",
                    help="codex uses the codex CLI (subscription auth, no "
                         "platform billing). Cost is then measured in "
                         "approximate tokens from a word count -- the CLI "
                         "exposes no tokenizer -- so eta is NOT comparable "
                         "with an anthropic run")
    ap.add_argument("--epsilon", type=float, default=0.02)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--cache", default=os.path.join(HERE, "sample-cache.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    args = ap.parse_args()

    results = run(args)
    if args.smoke:
        results["SMOKE_TEST"] = True
        results["inferential"] = False
        results["smoke_note"] = (
            "Instrument check at k=%d, n=%d -- both below the pre-registered "
            "k=8, n=30. Supports NO hypothesis. Its numbers exist to show the "
            "pipeline runs live and the gates evaluate, nothing more."
            % (args.k, args.samples)
        )
    os.makedirs(args.out, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    suffix = "-dryrun" if args.dry_run else ("-SMOKE" if args.smoke else "")
    path = os.path.join(args.out, "E-001b-%s%s.json" % (stamp, suffix))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    if results.get("void"):
        print("VOID: %s\nNo effect was measured." % results["void_reason"])
    elif results.get("aborted"):
        print("ABORTED: %s" % results["aborted"])
    else:
        print("  %-38s %-9s %-9s %s" % ("effect", "estimate", "p", "CI95"))
        for name, e in sorted(results["effects"].items()):
            print("  %-38s %+9.4f %-9.4f [%+.4f, %+.4f]%s"
                  % (name, e["effect"], e["p_value"], e["ci95"][0], e["ci95"][1],
                     "  DEGENERATE" if e.get("degenerate_with_H1") else ""))
        failed = [g for g, v in results["gates"].items() if not v["passed"]]
        print("\n  gates failed: %s" % (", ".join(failed) if failed else "none"))
    print("\nwrote %s" % path)
    if results.get("dry_run"):
        print("DRY RUN -- synthetic, no scientific weight.")
    elif results.get("SMOKE_TEST"):
        print("SMOKE TEST -- below pre-registered parameters. Supports no hypothesis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
