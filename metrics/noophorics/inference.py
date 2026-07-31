"""Inference helpers shared by experiment runners.

Extracted when E-002 needed the same Holm step-down E-001b already had. Two
copies of a multiplicity correction is two chances to correct differently, and
the failure would be silent: both runners would report p-values, and only one
would be right.

Everything here is dependency-free, seeded, and deterministic. Bootstrap and
permutation both take an explicit seed because a confidence interval that moves
between reruns of the same data is not a confidence interval.
"""

from __future__ import annotations

import math
import random
import statistics
from typing import Callable, Dict, List, Sequence, Tuple

__all__ = [
    "holm_adjust",
    "paired_permutation",
    "bootstrap_ci",
    "permutation_diff",
    "point_biserial",
    "goodman_kruskal_gamma",
]


def holm_adjust(p_values: Dict[str, float]) -> Dict[str, float]:
    """Holm-Bonferroni step-down over a family of hypotheses.

    Holm rather than Bonferroni: uniformly more powerful, no extra assumption.
    Adjusted values are enforced monotone, so a later hypothesis can never be
    reported as more significant than an earlier one that dominates it.
    """
    if not p_values:
        return {}
    ordered = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(ordered)
    out: Dict[str, float] = {}
    running = 0.0
    for i, (name, p) in enumerate(ordered):
        running = max(running, min(1.0, (m - i) * p))
        out[name] = running
    return out


def bootstrap_ci(
    values: Sequence[float],
    statistic: Callable[[Sequence[float]], float] = statistics.mean,
    resamples: int = 5000,
    seed: int = 0,
    alpha: float = 0.05,
) -> Tuple[float, float, float]:
    """Percentile bootstrap over the exchangeable unit. Returns (point, lo, hi).

    The caller chooses the unit by choosing what is in ``values``. In these
    experiments that is the brief, never the probe: probes within a brief are
    not independent observations of the treatment, and E-001 reported a
    within-message quantity as a between-condition result by getting this wrong.
    """
    v = [float(x) for x in values]
    if len(v) < 2:
        raise ValueError("bootstrap needs at least two units; got %d" % len(v))
    rng = random.Random(seed)
    n = len(v)
    draws = sorted(statistic([v[rng.randrange(n)] for _ in range(n)])
                   for _ in range(resamples))
    lo = draws[int((alpha / 2) * resamples)]
    hi = draws[min(resamples - 1, int((1 - alpha / 2) * resamples))]
    return statistic(v), lo, hi


def permutation_diff(
    group_a: Sequence[float],
    group_b: Sequence[float],
    permutations: int = 10000,
    seed: int = 0,
) -> Tuple[float, float]:
    """Two-sided permutation test on a difference of means. (observed, p)."""
    a, b = [float(x) for x in group_a], [float(x) for x in group_b]
    if not a or not b:
        raise ValueError("empty group in permutation test")
    observed = statistics.mean(a) - statistics.mean(b)
    pool, n_a = a + b, len(a)
    rng = random.Random(seed)
    extreme = 0
    for _ in range(permutations):
        rng.shuffle(pool)
        if abs(statistics.mean(pool[:n_a]) - statistics.mean(pool[n_a:])) \
                >= abs(observed) - 1e-15:
            extreme += 1
    return observed, (extreme + 1) / (permutations + 1)


def paired_permutation(
    differences: Sequence[float],
    permutations: int = 10000,
    seed: int = 0,
) -> Tuple[float, float]:
    """Sign-flip permutation on paired differences. (observed mean, p).

    Use this whenever both series are measured on the SAME exchangeable units.
    `permutation_diff` shuffles labels between two groups, which assumes the
    units are independent across groups -- and when they are not, it discards
    the pairing and loses most of the power.

    E-002b is the cautionary case: it measured sender and receiver calibration
    on the same 16 briefs, computed the confidence interval from the paired
    per-brief differences, and computed the p-value with the unpaired test. The
    results file therefore reported a CI excluding zero beside p = 0.385, and
    carried `supported: true` next to `significant_at_005: false`. The paired
    test on the same data gives p = 0.0033.
    """
    d = [float(x) for x in differences]
    if len(d) < 2:
        raise ValueError("paired test needs at least two units")
    observed = statistics.mean(d)
    rng = random.Random(seed)
    extreme = 0
    for _ in range(permutations):
        flipped = [x if rng.random() < 0.5 else -x for x in d]
        if abs(statistics.mean(flipped)) >= abs(observed) - 1e-15:
            extreme += 1
    return observed, (extreme + 1) / (permutations + 1)


def point_biserial(claims: Sequence[float], outcomes: Sequence[float]) -> float:
    """Correlation between a per-probe claim and that probe's outcome.

    This is RESOLUTION: whether a party can tell *which* cases diverged, as
    distinct from whether it is right on average. The two are independent, and
    a programme that measures only the second cannot distinguish a
    well-calibrated agent from one that says the same thing about every case
    and happens to average out. That confusion invalidated a falsification
    criterion in PRINCIPIA 7.

    Returns 0.0 when either series is constant -- undefined rather than zero,
    strictly, but a constant claim series IS zero resolution and the
    experiment's degeneracy gate is what catches the case where that is an
    artifact rather than a finding.
    """
    x, y = [float(a) for a in claims], [float(b) for b in outcomes]
    if len(x) != len(y):
        raise ValueError("claims and outcomes must be the same length")
    if len(x) < 3:
        raise ValueError("need at least three probes for a correlation")
    mx, my = statistics.mean(x), statistics.mean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def goodman_kruskal_gamma(claims: Sequence[float],
                          outcomes: Sequence[float]) -> float:
    """Rank association between claims and outcomes, ties excluded.

    Reported alongside the point-biserial because the metacomprehension
    literature reports gamma, and a number that cannot be compared to the field
    it is replicating is worth less than one that can. Baseline relative
    accuracy in that literature sits around +.20 to +.30 without intervention.
    """
    x, y = list(claims), list(outcomes)
    if len(x) != len(y):
        raise ValueError("claims and outcomes must be the same length")
    concordant = discordant = 0
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            dx, dy = x[i] - x[j], y[i] - y[j]
            if dx == 0 or dy == 0:
                continue
            if (dx > 0) == (dy > 0):
                concordant += 1
            else:
                discordant += 1
    total = concordant + discordant
    if total == 0:
        return 0.0
    return (concordant - discordant) / total
