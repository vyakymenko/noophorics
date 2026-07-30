"""Decomposing fidelity into understanding, mimicry, and decisiveness. v0.3

E-001 established that F* alone is not a measure of transferred understanding.
On its own cached data, both receivers out-decided the sender that briefed
them, F* ranked them the other way, and 62% of the headline effect came from
probes where the sender was wrong and one receiver was right -- rewarded for
copying the sender's mistakes.

That is not an estimator defect. It follows from the definition: "B would make
the same decisions A would make" cannot separate

    (a) B reconstructed the domain, from
    (b) B reconstructed A's defects, from
    (c) B merely became as decisive as A, matching the class prior.

This module separates them. Doing so requires an answer key -- promoted here
from the sanity check it was in v0.1 to a load-bearing input. Where no key
exists, only the aggregate F* is available, and its ambiguity must be stated.

See experiments/E-001-fluency-cost/FINDINGS.md.
"""

from __future__ import annotations

import random
from typing import Dict, List, NamedTuple, Optional, Sequence

from .divergence import (
    AnswerDist,
    mean_divergence,
    mean_permutation_floor,
    to_distribution,
)
from .fidelity import DEFAULT_EPSILON, transfer_fidelity
from .probes import ProbeMeasure

__all__ = [
    "Decomposition",
    "decompose",
    "class_prior_baseline_draws",
    "sender_split",
]


def _mode(dist: AnswerDist) -> str:
    return max(sorted(dist), key=lambda answer: dist[answer])


def sender_split(
    measure: ProbeMeasure, sender_draws: Sequence[Sequence[str]]
) -> Dict[str, List[int]]:
    """Partition probe indices by whether the sender got the key right.

    Raises if the measure is unkeyed: the decomposition is undefined without a
    key, and returning an aggregate anyway is how the ambiguity got hidden the
    first time.
    """
    if any(p.key is None for p in measure):
        raise ValueError(
            "decomposition requires a fully keyed probe measure; without a key "
            "there is no way to tell understanding from error replication"
        )
    right, wrong = [], []
    for index, (probe, draws) in enumerate(zip(measure, sender_draws)):
        (right if _mode(to_distribution(draws)) == probe.key else wrong).append(index)
    return {"right": right, "wrong": wrong}


def class_prior_baseline_draws(
    sender_draws: Sequence[Sequence[str]], n_samples: int, seed: int = 0
) -> List[List[str]]:
    """Draws from an agent with the sender's class prior and no rule knowledge.

    For every probe it samples from the sender's *marginal* answer distribution,
    pooled across the whole measure, ignoring the probe entirely. It therefore
    knows how often each verdict occurs and nothing about when.

    This is the decisiveness control. A large part of a raw D_prior is the
    mismatch between a decisive sender and a hedging receiver, and closing that
    costs nothing but a sentence about the base rates. Any encoding whose
    fidelity does not exceed this baseline transferred no rule content, however
    good its F* looks.
    """
    pooled: List[str] = []
    for draws in sender_draws:
        pooled.extend(draws)
    if not pooled:
        raise ValueError("no sender draws to build a class prior from")
    rng = random.Random(seed)
    return [
        [rng.choice(pooled) for _ in range(n_samples)] for _ in sender_draws
    ]


class Decomposition(NamedTuple):
    """Fidelity separated into its three components. All relative to a stated P."""

    fidelity_aggregate: float          # F* over the whole measure -- the v0.1 number
    # The two keyed fields are None on a measure with no key. They are the only
    # ones that need one; everything else here is computed from the sender's own
    # draws. The first version raised instead, so a keyless measure -- a
    # preference, a house style, a judgment call, all of which the theory
    # explicitly admits -- lost the baseline and the rule-content number for
    # want of something neither of them uses.
    fidelity_where_sender_right: Optional[float]
    error_replication: Optional[float] # rate of copying the sender's wrong answers
    fidelity_class_prior_baseline: float  # what a rule-free class-prior agent scores
    rule_content: float                # aggregate minus the baseline
    accuracy_gain: Optional[float]     # receiver accuracy minus prior accuracy
    n_right: Optional[int]
    n_wrong: Optional[int]
    keyed: bool = True                 # False when the measure carries no key

    @property
    def is_mimicry_dominated(self) -> Optional[bool]:
        """The receiver copies the sender's errors more than it avoids them.

        None without a key: on a keyless measure there is no sender error to
        replicate, and returning False would assert the absence of a pathology
        that was never measurable.
        """
        if self.error_replication is None:
            return None
        return self.error_replication > 0.5

    @property
    def transferred_rule_content(self) -> bool:
        """Fidelity exceeds what class-prior matching alone would buy."""
        return self.rule_content > 0.0

    def summary(self) -> str:
        return (
            "F*=%.3f | where-right %.3f | err-repl %.2f (n=%d) | "
            "baseline %.3f -> rule content %+.3f | acc gain %+.3f"
            % (
                self.fidelity_aggregate,
                self.fidelity_where_sender_right,
                self.error_replication,
                self.n_wrong,
                self.fidelity_class_prior_baseline,
                self.rule_content,
                self.accuracy_gain,
            )
        )


def decompose(
    measure: ProbeMeasure,
    sender_draws: Sequence[Sequence[str]],
    prior_draws: Sequence[Sequence[str]],
    post_draws: Sequence[Sequence[str]],
    epsilon: float = DEFAULT_EPSILON,
    permutations: int = 300,
    seed: int = 0,
) -> Decomposition:
    """Split a transfer into understanding, mimicry, and induced decisiveness.

    All four draw sequences are raw ordered samples, one list per probe. Draw
    order is preserved throughout: the permutation floor depends on it.
    """
    keyed = all(p.key is not None for p in measure)
    if keyed:
        split = sender_split(measure, sender_draws)
        right, wrong = split["right"], split["wrong"]
    else:
        right, wrong = [], []

    def fstar(idx: Sequence[int]) -> float:
        if not idx:
            return float("nan")
        s = [to_distribution(sender_draws[i]) for i in idx]
        p = [to_distribution(prior_draws[i]) for i in idx]
        o = [to_distribution(post_draws[i]) for i in idx]
        w = [measure.weights[i] for i in idx]
        d_prior = mean_divergence(s, p, w)
        d_post = mean_divergence(s, o, w)
        floor = mean_permutation_floor(
            [sender_draws[i] for i in idx], [post_draws[i] for i in idx],
            w, permutations, seed,
        )
        if (d_prior - floor) <= epsilon:
            return float("nan")
        return transfer_fidelity(d_prior, d_post, floor, epsilon)

    all_idx = list(range(len(measure)))
    aggregate = fstar(all_idx)
    where_right = fstar(right) if keyed else None

    # Error replication: on probes the sender got wrong, how often does the
    # receiver's modal answer match the SENDER rather than the key?
    replication = float("nan") if keyed else None
    if wrong:
        hits = 0
        for i in wrong:
            sender_mode = _mode(to_distribution(sender_draws[i]))
            post_mode = _mode(to_distribution(post_draws[i]))
            if post_mode == sender_mode:
                hits += 1
        replication = hits / len(wrong)

    # Decisiveness control: what a rule-free agent with the sender's class
    # prior scores under the identical pipeline.
    n = len(post_draws[0])
    baseline_draws = class_prior_baseline_draws(sender_draws, n, seed)
    s_all = [to_distribution(d) for d in sender_draws]
    p_all = [to_distribution(d) for d in prior_draws]
    b_all = [to_distribution(d) for d in baseline_draws]
    d_prior_all = mean_divergence(s_all, p_all, measure.weights)
    d_base = mean_divergence(s_all, b_all, measure.weights)
    floor_base = mean_permutation_floor(
        sender_draws, baseline_draws, measure.weights, permutations, seed
    )
    baseline = (
        transfer_fidelity(d_prior_all, d_base, floor_base, epsilon)
        if (d_prior_all - floor_base) > epsilon
        else float("nan")
    )

    def accuracy(draws: Sequence[Sequence[str]]) -> float:
        return sum(
            1 for probe, d in zip(measure, draws)
            if _mode(to_distribution(d)) == probe.key
        ) / len(measure)

    return Decomposition(
        fidelity_aggregate=aggregate,
        fidelity_where_sender_right=where_right,
        error_replication=replication,
        fidelity_class_prior_baseline=baseline,
        rule_content=aggregate - baseline,
        accuracy_gain=(accuracy(post_draws) - accuracy(prior_draws)
                       if keyed else None),
        n_right=len(right) if keyed else None,
        n_wrong=len(wrong) if keyed else None,
        keyed=keyed,
    )
