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
import hashlib
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
from noophorics.ollama_agent import OllamaAgent, ollama_available  # noqa: E402
from noophorics.decomposition import decompose  # noqa: E402

# The cells are imported from E-001b rather than copied, because the
# pre-registration says they are unchanged from it and an import is the
# only form of "unchanged" that cannot drift. E-001b is void; its prompts
# are not, and they are committed and immutable.
sys.path.insert(0, os.path.join(REPO, "experiments", "E-001b-fluency-factorial"))
sys.path.insert(0, HERE)   # blind_rating.ABSOLUTE, the register question
from prompts import CELL_AXES, CELLS, _OUTPUT  # noqa: E402

# The band instruction is imported from the feasibility script for the same
# reason the cells are imported from E-001b: the pre-registration calibrates
# the band on the messages FEASIBILITY composed, and that calibration only
# transfers if the instruction is the same one. It was not -- see DEFECT-001.
from feasibility import two_sided_output  # noqa: E402

# E-001c constants. Every one of these is fixed by the pre-registration and
# none may be changed after composition begins.
WORD_TARGET = 207                 # PREREGISTRATION section 3
WORD_TOLERANCE = 0.12             # band 182-231, admits both registers
ELICITATIONS = 9                  # E-002c H4: a four-value grid hid signal
COMPOSE_BUDGET_FLUENT = 40        # section 4; exhausting it VOIDS the run
COMPOSE_BUDGET_TERSE = 16
LAMBDA_PER_TOKEN = 0.001          # section 5; declared before data
MODAL_MARGIN_DIVISOR = 4          # a mode winning by < n/4 is unresolved
MAX_UNRESOLVED = 4                # of 33 probes
RATERS = ("codex", "claude-opus-4-8")   # section 4, named in advance
BUDGET_TOKENS = 350               # retained only for the prompt template
PERMUTATIONS = 10_000
BOOTSTRAP = 5_000
SEED = 20260803
SENDER_ACCURACY_GATE = 0.90
SENDER_MAX_ERRORS = 2
CEILING_GATE = 0.70
COST_PARITY_MAX_RATIO = 1.30
H4_CI_MAX_WIDTH = 0.15
# Below this spread in the sender's claims across cells, Phi is -A up to a
# constant, H2 restates H1, and the two become one family (prereg §4.6).
CLAIM_SPREAD_DEGENERACY = 0.05
# Permutations for the shared floor. Identical in the full-measure analysis and
# in the M33 sensitivity, so the two floors differ only by the dropped probe.
FLOOR_PERMUTATIONS = 300

# Local-provider sampling regime. Reported, never assumed -- see the note in
# PARAMETERS.md. think=medium is the setting at which gpt-oss:120b clears the
# sender gate perfectly (0 errors of 34); at low it makes 3, all on interaction
# probes. temperature>0 is required BY the pre-registered analysis plan: at 0
# the model is deterministic, per-probe distributions collapse, and the
# permutation floor is identically zero.
OLLAMA_THINK = "medium"
OLLAMA_TEMPERATURE = 0.7


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


def restrict(full_ids: Sequence[str], rows: Sequence[Sequence[str]],
             keep_ids: Sequence[str]) -> List[List[str]]:
    """Select the draw rows for `keep_ids`, preserving the restricted order.

    Draws are stored as a list parallel to the probe measure, so restricting the
    measure without restricting the draws in the same order silently pairs each
    probe with a different probe's answers.
    """
    index = {pid: i for i, pid in enumerate(full_ids)}
    return [list(rows[index[p]]) for p in keep_ids]


def unresolved_probes(measure: ProbeMeasure,
                      sender_rows: Sequence[Sequence[str]]) -> Dict[str, Any]:
    """Probes whose modal answer is nearly a tie: unresolved, not measured.

    Every experiment in this programme reduces a probe to the mode of n draws
    and then treats it as the thing measured. E-004 showed the cost: of eleven
    errors three were near-ties, and one took the modal slot six votes to five,
    so a different sixteen draws would have produced a different error set and a
    different p-value with nothing showing it.

    Problem 14 is open and this is the registered stopgap. It lives in its own
    function and its own results key because the first version put it inside the
    per-message table, where every downstream consumer iterates -- and the dry
    run found that in one call, which is the whole reason the dry run has to
    reach the analysis rather than stopping at a gate.
    """
    out = []
    for idx, probe in enumerate(measure):
        counts: Dict[str, int] = {}
        for a in sender_rows[idx]:
            counts[a] = counts.get(a, 0) + 1
        ranked = sorted(counts.values(), reverse=True)
        top = ranked[0] if ranked else 0
        second = ranked[1] if len(ranked) > 1 else 0
        if (top - second) * MODAL_MARGIN_DIVISOR < len(sender_rows[idx]):
            out.append({"probe": probe.id, "top": top, "second": second,
                        "n": len(sender_rows[idx])})
    return {"probes": out, "count": len(out), "threshold": MAX_UNRESOLVED,
            "margin_divisor": MODAL_MARGIN_DIVISOR,
            "passes": len(out) <= MAX_UNRESOLVED}


def derive_per_message(
    measure: ProbeMeasure,
    sender_rows: Sequence[Sequence[str]],
    prior_rows: Sequence[Sequence[str]],
    post_rows_by_label: Dict[str, Sequence[Sequence[str]]],
    elicited: Dict[str, Dict[str, Any]],
    d_prior: float,
    floor: float,
    epsilon: float,
) -> Dict[str, Dict[str, Any]]:
    """Everything downstream of the draws, with no live calls.

    Split out from `run` so the same computation serves three callers: the run
    itself, the M33 sensitivity on a restricted measure, and a re-analysis from
    a stored record. Costs and claim elicitations are inputs here rather than
    being fetched, because they are properties of the message and do not change
    when the probe measure is restricted.
    """
    s_dists = [to_distribution(d) for d in sender_rows]

    table: Dict[str, Dict[str, Any]] = {}
    for label in sorted(post_rows_by_label):
        post = post_rows_by_label[label]
        p_dists = [to_distribution(d) for d in post]
        dec = decompose(measure, sender_rows, prior_rows, post)
        observed = agreement_rate(s_dists, p_dists, measure.weights)
        cs = elicited[label]["claims_sender"]
        cr = elicited[label]["claims_receiver"]
        cost = float(elicited[label]["cost_tokens"])
        claimed = (statistics.mean(cs) + statistics.mean(cr)) / 2
        cell = label[0]
        table[label] = {
            "cell": cell, "polish": CELL_AXES[cell][0],
            "selection": CELL_AXES[cell][1],
            "d_post": mean_divergence(s_dists, p_dists, measure.weights),
            "fidelity_aggregate": transfer_fidelity(
                d_prior,
                mean_divergence(s_dists, p_dists, measure.weights),
                floor, epsilon),
            "fidelity_where_sender_right": dec.fidelity_where_sender_right,
            "error_replication": dec.error_replication,
            "rule_content": dec.rule_content,
            "accuracy_gain": dec.accuracy_gain,
            "agreement_observed": observed,
            "claims_sender": list(cs), "claims_receiver": list(cr),
            "phi": claimed - observed,
            "phi_sender": statistics.mean(cs) - observed,
            "phi_receiver": statistics.mean(cr) - observed,
            "cost_tokens": cost,
            # V_lambda, not eta. Retraction 3 withdrew a ratio with a signed
            # numerator as an ordering: at F* = -1 a cheap antinoophor outranks
            # an expensive one. V_lambda is monotone at every sign, and lambda
            # is declared in the pre-registration before any data existed.
            "net_value": dec.fidelity_where_sender_right - LAMBDA_PER_TOKEN * cost,
            # Reported where the sign permits it, never as a hypothesis.
            "efficiency_per_ktok": (dec.fidelity_where_sender_right * 1000.0 / cost
                                    if dec.fidelity_where_sender_right >= 0 else None),
        }
    return table


HYPOTHESES = [
    # (name, quantity, axis, high level, low level)
    ("H1_contrastiveness_on_understanding", "fidelity_where_sender_right", 1,
     "contrastive", "declarative"),
    ("H2_fluency_on_phantom", "phi", 0, "fluent", "terse"),
    ("H3_contrastiveness_on_net_value", "net_value", 1,
     "contrastive", "declarative"),
    ("H4_fluency_on_understanding", "fidelity_where_sender_right", 0,
     "fluent", "terse"),
]


def compute_effects(per_message: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """The four pre-registered main effects. Exchangeable unit: message."""
    effects: Dict[str, Any] = {}
    for name, quantity, axis, hi, lo in HYPOTHESES:
        a = [v[quantity] for v in per_message.values()
             if CELL_AXES[v["cell"]][axis] == hi]
        b = [v[quantity] for v in per_message.values()
             if CELL_AXES[v["cell"]][axis] == lo]
        obs, p = permutation_main_effect(a, b)
        mean, lo95, hi95 = bootstrap_effect_ci(a, b)
        effects[name] = {
            "quantity": quantity, "contrast": "%s minus %s" % (hi, lo),
            "effect": obs, "p_value": p, "ci95": [lo95, hi95],
            "ci_width": hi95 - lo95, "n_messages": [len(a), len(b)],
        }
    h4 = effects["H4_fluency_on_understanding"]
    h4["predicted_null_survives"] = bool(
        h4["ci95"][0] <= 0.0 <= h4["ci95"][1] and h4["ci_width"] < H4_CI_MAX_WIDTH)
    h4["note"] = ("a wide CI containing zero is not evidence of no effect; the "
                  "width gate is why this is not adjudicated by failure to reject")
    return effects


def sensitivity_without(
    measure: ProbeMeasure,
    raw: Dict[str, Sequence[Sequence[str]]],
    elicited: Dict[str, Dict[str, Any]],
    epsilon: float,
    drop: Sequence[str] = ("M33",),
    permutations: int = FLOOR_PERMUTATIONS,
) -> Dict[str, Any]:
    """Recompute every effect over the measure with `drop` removed.

    Pre-specified in SENSITIVITY-M33.md while collection was still running and
    before any effect had been computed. M33's key is not determined by the
    source specification, and in v0.3 the key is load-bearing: `decompose`
    partitions probes by whether the sender was right, so a wrong key puts a
    probe in the wrong half of two reported quantities.

    Everything is recomputed, not just the effects: dropping a probe changes the
    prior gap and the floor as well, and reusing the full-measure values here
    would compare effects computed against different denominators.
    """
    full_ids = [p.id for p in measure]
    keep_ids = [pid for pid in full_ids if pid not in set(drop)]
    if len(keep_ids) == len(full_ids):
        return {"applicable": False,
                "reason": "none of %s is in the measure" % list(drop)}
    reduced = measure._subset([p for p in measure if p.id in set(keep_ids)],
                              measure.id + "-minus-" + "-".join(drop))

    r = {label: restrict(full_ids, rows, keep_ids) for label, rows in raw.items()}
    s_dists = [to_distribution(d) for d in r["sender"]]
    p_dists = [to_distribution(d) for d in r["PRIOR"]]
    d_prior = mean_divergence(s_dists, p_dists, reduced.weights)
    floor = mean_permutation_floor(r["sender"], r["PRIOR"], reduced.weights,
                                   permutations, SEED)

    labels = {k: v for k, v in r.items()
              if k not in ("sender", "PRIOR", "CEILING")}
    table = derive_per_message(reduced, r["sender"], r["PRIOR"], labels,
                               elicited, d_prior, floor, epsilon)
    return {
        "applicable": True,
        "dropped": list(drop),
        "probe_measure": reduced.qualified_id,
        "n_probes": len(reduced),
        "d_prior": d_prior,
        "d_floor_shared": floor,
        "admissible": bool((d_prior - floor) > epsilon),
        "effects": compute_effects(table),
        "note": ("pre-specified in SENSITIVITY-M33.md before any effect existed. "
                 "If these disagree with the full-measure effects, the "
                 "disagreement is the finding and no directional claim survives it."),
    }


def holm_adjust(p_values: Dict[str, float]) -> Dict[str, float]:
    """Holm-Bonferroni step-down, applied when the degeneracy condition fires.

    The pre-registration says correction *is applied* in that case. Detecting a
    multiplicity problem and then reporting uncorrected p-values is the same as
    not detecting it, and it is the more misleading of the two because the
    detection appears in the record as though it had been acted on.

    Holm rather than Bonferroni: uniformly more powerful, no extra assumption.
    Adjusted values are enforced monotone, so a later hypothesis can never be
    reported as more significant than an earlier one it dominates.
    """
    ordered = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(ordered)
    out: Dict[str, float] = {}
    running = 0.0
    for i, (name, p) in enumerate(ordered):
        running = max(running, min(1.0, (m - i) * p))
        out[name] = running
    return out


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


def make_rater(name: str):
    """A register judge with no context. The empty context is the blinding."""
    if name.startswith("codex"):
        from noophorics.codex_agent import CodexAgent
        return CodexAgent("rater", context="", reasoning_effort="low")
    if name.startswith("claude"):
        from noophorics.agents import AnthropicAgent
        return AnthropicAgent(name, "", model=name)
    from noophorics.ollama_agent import OllamaAgent
    return OllamaAgent("rater", "", model=name, think="medium", temperature=0.7)


def judge_register(agent, text: str) -> str:
    """A -> connected prose, B -> a list. Absolute, never comparative.

    A forced choice between one message of each register cannot fail: the rater
    must name one even when neither is connected prose, and it names the
    wordier one, which tracks the label perfectly. That scored 64/64 on
    feasibility messages of which three in eight were lists.
    """
    from noophorics.probes import Probe
    from blind_rating import ABSOLUTE
    return agent.answer_samples(
        Probe(id="reg", prompt=ABSOLUTE % text, options=("A", "B")), 1)[0].strip()


def message_fingerprint(message: str) -> str:
    """Short content hash binding a set of draws to the text that produced it."""
    return hashlib.sha256(message.encode("utf-8")).hexdigest()[:10]


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
                        n_elicitations=ELICITATIONS, seed=0) -> List[float]:
        return [max(0.0, min(1.0, self._claim + 0.02 * (i - 1)))
                for i in range(n_elicitations)]

    def cost_of(self, message: str) -> int:
        return max(1, len(message.split()))

    def compose(self, prompt: str, seed: int = 0) -> str:
        """A message inside the word band, so the dry run reaches the analysis.

        The eight-word stub this replaces could never satisfy a 182-231 word
        band, so every dry run voided on the register budget and the analysis
        path was never executed. A pipeline check that only exercises the void
        path is the DEFECT-001 mistake with a different function name -- the
        phrasing is E-002c's, which had to learn the same thing.

        The length is drawn just inside the band and varies with the seed, so
        the parity statistics have something to be computed from.
        """
        target = WORD_TARGET + ((seed * 7) % 21) - 10
        body = ("stub %s seed %d " % (self.name, seed)) + "word " * max(1, target - 4)
        return body.strip()


def _make_agent(provider: str, name: str, context: str, model: str, effort: str):
    """Provider selection. PREREGISTRATION 2.4 records the model per run rather
    than fixing one, so choosing a provider before any data exists is a run
    parameter and not an amendment."""
    if provider == "ollama":
        if not ollama_available():
            raise SystemExit("--provider ollama but no server on :11434")
        return OllamaAgent(name, context=context, model=model,
                           think=OLLAMA_THINK, temperature=OLLAMA_TEMPERATURE)
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
                        n_elicitations=ELICITATIONS, seed=0) -> List[float]:
        return self._agent.claim_agreement(
            measure, counterpart, artifact, n_elicitations, seed
        )

    def cost_of(self, message: str) -> int:
        return self._agent.cost_of(message)

    def compose(self, prompt: str, seed: int = 0) -> str:
        """One generation, in a fresh request. Independence is per message."""
        # Delegate whenever the provider supplies its own generator. Naming
        # providers one by one here is what let ollama fall through to the
        # Anthropic client path and crash on a missing attribute.
        own = getattr(self._agent, "compose", None)
        if callable(own):
            return own(prompt, seed)
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
                        n_elicitations=ELICITATIONS, seed=0) -> List[float]:
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

    print("E-001c  Fluency x Contrastiveness, at controlled length")
    print("measure   : %s (%d probes)" % (measure.qualified_id, len(measure)))
    print("design    : 4 cells x k=%d messages, n=%d samples/probe" % (k, n))
    print("provider  : %s" % args.provider)
    print("model     : %s (both roles)" % (
        "codex CLI default" if args.provider == "codex" else args.model))
    print("mode      : %s\n" % ("DRY RUN" if args.dry_run else "live"))

    cache = Cache(args.cache)
    sender = (Stub("stub-sender", 0.94, 0.88, 1) if args.dry_run
              else Sender(spec, args.model, provider=args.provider))

    # --- compose under the band, and filter on register ---------------------
    #
    # Two things E-001b did not do. The output instruction is a two-sided word
    # band, because a ceiling bounds above and says nothing below and was not
    # obeyed anyway. And every fluent message is judged, alone, by two raters on
    # two providers, because the blind rating found the fluent instruction
    # produces the intended register five times in eight while a forced-choice
    # rating scored 64/64 on the same messages and could not see it.
    low = int(WORD_TARGET * (1 - WORD_TOLERANCE))
    high = int(WORD_TARGET * (1 + WORD_TOLERANCE))
    print("  band      : %d-%d words (target %d +/-%.0f%%)"
          % (low, high, WORD_TARGET, WORD_TOLERANCE * 100))
    raters = [] if args.dry_run else [make_rater(r) for r in RATERS]
    if not args.dry_run:
        print("  raters    : %s" % ", ".join(RATERS))

    messages: Dict[str, str] = {}
    rejected: Dict[str, List[Dict[str, Any]]] = {}
    for cell, prompt in sorted(CELLS.items()):
        want_prose = CELL_AXES[cell][0] == "fluent"
        budget = COMPOSE_BUDGET_FLUENT if want_prose else COMPOSE_BUDGET_TERSE
        rejected[cell], attempts, accepted = [], 0, 0
        seed = 0
        while accepted < k:
            if attempts >= budget:
                return {
                    "experiment": "E-001c", "void": True,
                    "void_reason": ("register budget exhausted in cell %s: %d "
                                    "attempts produced %d of %d accepted "
                                    "messages. A register the model cannot "
                                    "reliably produce at a fixed length is a "
                                    "finding, not an obstacle to route around."
                                    % (cell, attempts, accepted, k)),
                    "rejected": rejected, "composed": sorted(messages),
                }
            attempts += 1
            label = "%s%d" % (cell, accepted)
            try:
                text = sender.compose(
                    prompt.replace(_OUTPUT, two_sided_output(low, high)), seed=seed)
            except RuntimeError as exc:
                return {
                    "experiment": "E-001c", "void": True,
                    "void_reason": "composition failed for %s: %s" % (label, exc),
                    "composed": sorted(messages),
                }
            seed += 1
            words = len(text.split())
            verdicts = ([judge_register(r, text) for r in raters]
                        if raters else ["A" if want_prose else "B"] * 2)
            ok_register = all(v == ("A" if want_prose else "B") for v in verdicts)
            ok_band = low <= words <= high
            if ok_register and ok_band:
                messages[label] = text
                accepted += 1
            else:
                rejected[cell].append({
                    "seed": seed - 1, "words": words, "in_band": ok_band,
                    "verdicts": verdicts, "text": text})
            print("  %s  attempt %2d  %4d words  band %-3s  register %-3s  -> %s"
                  % (cell, attempts, words, "ok" if ok_band else "no",
                     "ok" if ok_register else "no",
                     "accepted %d/%d" % (accepted, k) if ok_register and ok_band
                     else "rejected"), flush=True)
    # Persist before anything else touches them. The messages exist only in
    # memory until this point, and the sweep that follows runs for tens of
    # hours: a crash anywhere after composition would strand every draw, because
    # a draw is only interpretable against the message it answered. Composition
    # is not deterministic (temperature > 0), so re-composing does not recover
    # them -- it produces different messages wearing the same labels.
    if args.messages_out:
        # A synthetic run must never land on the live path. --messages-out
        # defaults to the real messages.json, so a dry run used to overwrite
        # the one artifact that cannot be regenerated: composition is not
        # deterministic, and E-001b's DEFECT-001 records that thirty hours of
        # draws with no record of which text produced them is not a damaged
        # dataset but no dataset. The results file already carries this
        # marker; the messages file now carries it too.
        stamp = "-dryrun" if args.dry_run else ("-SMOKE" if args.smoke else "")
        if stamp:
            root, ext = os.path.splitext(args.messages_out)
            args.messages_out = root + stamp + ext
        with open(args.messages_out, "w", encoding="utf-8") as fh:
            json.dump({"probe_measure": measure.qualified_id,
                       "model": args.model, "provider": args.provider,
                       "budget_tokens": BUDGET_TOKENS,
                       "fingerprints": {l: message_fingerprint(m)
                                        for l, m in messages.items()},
                       "messages": messages}, fh, indent=1, sort_keys=True)
        print("  messages persisted -> %s" % args.messages_out)
    print("  composed %d messages across %d cells (%d rejected)"
          % (len(messages), len(CELLS), sum(len(v) for v in rejected.values())))

    # --- gates that are decidable now are decided now ----------------------
    # Cost parity depends only on the composed messages. E-001b placed it at the
    # end of the analysis, so a run that was already void by construction would
    # have spent thirty hours discovering it (VOID.md). A gate evaluated later
    # than its inputs allow is not a gate, it is a postmortem.
    realised = {l: float(sender.cost_of(m)) for l, m in sorted(messages.items())}
    by_cell: Dict[str, List[float]] = {}
    for label, c in realised.items():
        by_cell.setdefault(label[0], []).append(c)
    cell_means = [statistics.mean(v) for v in by_cell.values()]
    parity = {
        "across_messages": max(realised.values()) / min(realised.values()),
        "across_cell_means": max(cell_means) / min(cell_means),
        "threshold": COST_PARITY_MAX_RATIO,
        "realised_cost_tokens": realised,
    }
    # The gate is the CELL-MEANS reading, which is what the pre-registration
    # says. Both numbers are recorded, but max/min over messages is not a
    # scale-free statistic: sample extremes drift outward as the sample grows,
    # so the same design fails the same threshold merely for collecting more
    # messages. Measured by parametric bootstrap on real cost distributions
    # (E-001c/FEASIBILITY.md): a genuinely cost-parous design fails the
    # across-messages reading 40% of the time at k=3 and 86% at k=8. A gate that
    # tightens with sample size penalises power, which is backwards.
    parity["gate_reading"] = "across_cell_means"
    parity["passed"] = bool(parity["across_cell_means"] <= COST_PARITY_MAX_RATIO)
    print("  cost parity: %.3f across messages, %.3f across cell means "
          "(threshold %.2f) -- %s"
          % (parity["across_messages"], parity["across_cell_means"],
             COST_PARITY_MAX_RATIO, "pass" if parity["passed"] else "FAIL"))
    if not parity["passed"] and not args.ignore_early_gates:
        return {
            "experiment": "E-001c", "void": True,
            "void_reason": ("cost parity failed on the composed messages, "
                            "before any probe was answered"),
            "voided_at": "composition",
            "cost_parity": parity,
            "messages": messages,
            "note": ("Nothing about probe outcomes was computed or examined. "
                     "The sweep did not run."),
        }
    print()

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
        # Message conditions carry a fingerprint of the message itself. Without
        # it the cache is keyed by a label, and a resumed run whose messages
        # were re-composed would silently inherit draws that answered different
        # text -- the cache would report a hit and the data would be wrong in a
        # way nothing downstream could detect.
        cond = "%s@%s" % (label, args.model)
        if label in messages:
            cond += "#" + message_fingerprint(messages[label])
        raw[label] = collect_concurrent(
            agent, measure, n, cond, cache, args.workers, progress,
        )
    sys.stderr.write("\n\n")

    # --- shared floor and denominator -------------------------------------
    s_dists = [to_distribution(d) for d in raw["sender"]]
    p_dists = [to_distribution(d) for d in raw["PRIOR"]]
    d_prior = mean_divergence(s_dists, p_dists, measure.weights)
    floor = mean_permutation_floor(raw["sender"], raw["PRIOR"], measure.weights,
                                  FLOOR_PERMUTATIONS, SEED)

    s_modes = [max(sorted(d), key=lambda x: d[x]) for d in s_dists]
    errors = [p.id for p, m in zip(measure, s_modes) if m != p.key]
    sender_acc = measure.accuracy(s_modes)

    results: Dict[str, Any] = {
        "experiment": "E-001c", "core_version": "0.3",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dry_run": bool(args.dry_run), "probe_measure": measure.qualified_id,
        "provider": args.provider,
        "model": ("codex-cli-default" if args.provider == "codex" else args.model),
        "cost_unit": ("approx-tokens-from-words" if args.provider == "codex"
                      else "tokens"),
        "sampling_regime": ({"think": OLLAMA_THINK, "temperature": OLLAMA_TEMPERATURE}
                            if args.provider == "ollama" else None),
        "k": k, "samples_per_probe": n,
        "cell_axes": CELL_AXES, "messages": messages,
        "d_prior": d_prior, "d_floor_shared": floor,
        "sender_accuracy": sender_acc, "sender_errors": errors,
        "raw_draws": raw, "per_message": {}, "effects": {}, "gates": {},
    }
    if (d_prior - floor) <= args.epsilon:
        results["aborted"] = "inadmissible: gap %.4f <= epsilon" % (d_prior - floor)
        return results

    # --- elicitation: the only live calls left in the analysis path ---------
    # Separated from computation so that every derived number can be recomputed
    # from the stored record without contacting a model. Costs and claims are
    # properties of the message, not of the probe measure, so they are elicited
    # once and reused by the M33 sensitivity.
    elicited: Dict[str, Dict[str, Any]] = {}
    for label in sorted(messages):
        elicited[label] = {
            "cost_tokens": float(sender.cost_of(messages[label])),
            "claims_sender": sender.claim_agreement(
                measure, "your colleague", artifact=messages[label]),
            "claims_receiver": (
                Stub("stub-r", 0.9, 0.8, 7) if args.dry_run
                else Receiver(label, messages[label], args.model,
                              provider=args.provider)
            ).claim_agreement(measure, "the person who briefed you"),
        }
    results["elicited"] = elicited

    # --- per message -------------------------------------------------------
    results["per_message"] = derive_per_message(
        measure, raw["sender"], raw["PRIOR"],
        {k: v for k, v in raw.items()
         if k not in ("sender", "PRIOR", "CEILING")},
        elicited, d_prior, floor, args.epsilon,
    )

    # --- main effects, message as unit -------------------------------------
    # The registered unresolved-probe gate. Computed here, reported in its own
    # key, and gating before the effects are read.
    results["unresolved"] = unresolved_probes(measure, raw["sender"])
    print("  unresolved probes: %d of %d (threshold %d) -- %s"
          % (results["unresolved"]["count"], len(measure), MAX_UNRESOLVED,
             "pass" if results["unresolved"]["passes"] else "VOID"), flush=True)
    if not results["unresolved"]["passes"]:
        results["void"] = True
        results["void_reason"] = (
            "%d probes of %d have a modal answer winning by fewer than n/%d "
            "draws. A mode that close is manufactured rather than recovered, "
            "and the design has no way to tell the two apart downstream."
            % (results["unresolved"]["count"], len(measure),
               MODAL_MARGIN_DIVISOR))
        return results

    results["effects"] = compute_effects(results["per_message"])

    # Pre-specified sensitivity: M33's ground truth is not determined by the
    # source spec (SENSITIVITY-M33.md, committed mid-collection). Every effect
    # is computed over all probes AND over the measure without M33, so the
    # choice cannot be made after seeing which is more favourable.
    results["sensitivity_M33"] = sensitivity_without(
        measure, raw, elicited, args.epsilon, drop=("M33",)
    )

    # Degeneracy: if claims barely move, Phi is -A and H2 restates H1.
    claims = [results["per_message"][m]["claims_sender"][0] for m in results["per_message"]]
    gap = max(claims) - min(claims)
    degenerate = gap < CLAIM_SPREAD_DEGENERACY
    results["effects"]["H2_fluency_on_phantom"]["claim_spread"] = gap
    results["effects"]["H2_fluency_on_phantom"]["degenerate_with_H1"] = degenerate

    # ...and if it does, the pre-registration says Holm is APPLIED, not merely
    # that the condition is noted. Detecting a multiplicity problem and
    # reporting uncorrected p-values is the same as not detecting it.
    results["multiplicity"] = {
        "condition": "claim spread < %.2f" % CLAIM_SPREAD_DEGENERACY,
        "claim_spread": gap,
        "triggered": degenerate,
        "family": ["H1_contrastiveness_on_understanding", "H2_fluency_on_phantom"],
        "rationale": (
            "H1 and H2 are separate hypotheses about separate quantities and are "
            "not corrected against each other -- unless the sender's claims barely "
            "move between cells, in which case Phi is -A up to a constant, H2 is "
            "H1 restated, and the two are one family."
        ),
    }
    if degenerate:
        family = results["multiplicity"]["family"]
        for name, p_adj in holm_adjust({n: results["effects"][n]["p_value"]
                                        for n in family}).items():
            results["effects"][name]["p_value_holm"] = p_adj
            results["effects"][name]["significant_at_005"] = bool(p_adj < 0.05)
    else:
        for name in results["multiplicity"]["family"]:
            results["effects"][name]["significant_at_005"] = bool(
                results["effects"][name]["p_value"] < 0.05)

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
    ap.add_argument("--provider", choices=("anthropic", "codex", "ollama"), default="anthropic",
                    help="codex uses the codex CLI (subscription auth, no "
                         "platform billing). Cost is then measured in "
                         "approximate tokens from a word count -- the CLI "
                         "exposes no tokenizer -- so eta is NOT comparable "
                         "with an anthropic run")
    ap.add_argument("--epsilon", type=float, default=0.02)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--cache", default=os.path.join(HERE, "sample-cache.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    ap.add_argument("--ignore-early-gates", action="store_true",
                    help="collect even when a pre-composition gate fails. For "
                         "instrument work only: the resulting run is void by "
                         "its own pre-registration and cannot support a claim.")
    ap.add_argument("--messages-out", default=os.path.join(HERE, "messages.json"),
                    help="where composed messages are written, immediately "
                         "after composition and before the sweep begins")
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
    path = os.path.join(args.out, "E-001c-%s%s.json" % (stamp, suffix))
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
