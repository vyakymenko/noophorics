"""Divergence between agents' answer distributions.

Reference implementation of theory/definitions.md sections 2 and 3.

Everything here operates on *empirical* distributions built from repeated
sampling. An agent's answer to a probe is a distribution, never a point; code
that treats a single sample as the agent's disposition is measuring noise.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Dict, Iterable, Mapping, Sequence

__all__ = [
    "AnswerDist",
    "to_distribution",
    "jensen_shannon",
    "probe_divergence",
    "mean_divergence",
    "agreement_rate",
    "self_divergence",
    "noise_floor",
]

# An answer distribution: answer label -> probability. Sums to 1.
AnswerDist = Dict[str, float]

_EPS = 1e-12


def to_distribution(samples: Iterable[str]) -> AnswerDist:
    """Build an empirical distribution from sampled answers.

    Raises ValueError on an empty sample set: a probe with no samples is a
    missing measurement, not a uniform one, and silently substituting a
    uniform prior would bias every downstream quantity toward disagreement.
    """
    counts = Counter(samples)
    total = sum(counts.values())
    if total == 0:
        raise ValueError("cannot build a distribution from zero samples")
    return {answer: count / total for answer, count in counts.items()}


def _entropy(dist: Mapping[str, float]) -> float:
    """Shannon entropy in bits."""
    return -sum(p * math.log2(p) for p in dist.values() if p > _EPS)


def jensen_shannon(p: Mapping[str, float], q: Mapping[str, float]) -> float:
    """Jensen-Shannon divergence in bits. Bounded [0, 1].

    Chosen over KL because it is symmetric (noophoric divergence must not
    depend on which agent we call the sender), finite for distributions with
    disjoint support (agents routinely give answers the other never gives),
    and bounded, so per-probe values are directly comparable.
    """
    support = set(p) | set(q)
    mixture = {a: 0.5 * (p.get(a, 0.0) + q.get(a, 0.0)) for a in support}
    divergence = _entropy(mixture) - 0.5 * (_entropy(p) + _entropy(q))
    # Clamp: floating-point error can push a true zero slightly negative.
    return max(0.0, min(1.0, divergence))


def probe_divergence(a: Mapping[str, float], b: Mapping[str, float]) -> float:
    """d(A, B | pi) -- per-probe divergence. definitions.md 2.1"""
    return jensen_shannon(a, b)


def mean_divergence(
    a_dists: Sequence[AnswerDist],
    b_dists: Sequence[AnswerDist],
    weights: Sequence[float] = None,
) -> float:
    """D(A, B | P) -- divergence over a probe measure. definitions.md 2.2

    ``a_dists`` and ``b_dists`` are aligned per-probe distributions.
    ``weights`` defaults to uniform; it is the probe measure's density.
    """
    if len(a_dists) != len(b_dists):
        raise ValueError(
            "probe count mismatch: %d vs %d" % (len(a_dists), len(b_dists))
        )
    if not a_dists:
        raise ValueError("empty probe measure")

    if weights is None:
        weights = [1.0] * len(a_dists)
    if len(weights) != len(a_dists):
        raise ValueError("weights length does not match probe count")

    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("probe measure weights must sum to a positive value")

    weighted = sum(
        w * probe_divergence(a, b) for a, b, w in zip(a_dists, b_dists, weights)
    )
    return weighted / total_weight


def _mode(dist: Mapping[str, float]) -> str:
    """Modal answer. Ties broken by label sort order, for determinism."""
    return max(sorted(dist), key=lambda answer: dist[answer])


def agreement_rate(
    a_dists: Sequence[AnswerDist],
    b_dists: Sequence[AnswerDist],
    weights: Sequence[float] = None,
) -> float:
    """A-hat -- fraction of probes where modal answers match. definitions.md 2.3

    Coarser than divergence, but this is the quantity parties can actually
    estimate about themselves, which is what makes phantom agreement a
    same-units subtraction.
    """
    if len(a_dists) != len(b_dists):
        raise ValueError("probe count mismatch")
    if not a_dists:
        raise ValueError("empty probe measure")

    if weights is None:
        weights = [1.0] * len(a_dists)
    total_weight = sum(weights)

    matches = sum(
        w for a, b, w in zip(a_dists, b_dists, weights) if _mode(a) == _mode(b)
    )
    return matches / total_weight


def self_divergence(
    run_one: Sequence[AnswerDist],
    run_two: Sequence[AnswerDist],
    weights: Sequence[float] = None,
) -> float:
    """D_self -- an agent's divergence from itself. definitions.md 3.1

    ``run_one`` and ``run_two`` must come from *independent* sampling passes
    under identical conditions. Splitting one pass in half underestimates
    self-divergence whenever the sampler has any within-pass correlation.
    """
    return mean_divergence(run_one, run_two, weights)


def noise_floor(d_self_a: float, d_self_b: float) -> float:
    """D_floor -- irreducible divergence between aligned agents. 3.2

    The divergence two *perfectly aligned* agents would still show, given
    their own stochasticity. No transfer can push measured divergence below
    it. Failing to correct for the floor systematically reports ceilings below
    1 and mistakes sampling noise for untransferred meaning.
    """
    if not (0.0 <= d_self_a <= 1.0) or not (0.0 <= d_self_b <= 1.0):
        raise ValueError("self-divergences must lie in [0, 1]")
    return 0.5 * (d_self_a + d_self_b)
