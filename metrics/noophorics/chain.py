"""Chained transfer, typed. v0.3

L4 as first written was not well-formed:

    "Fidelity is multiplicative along a chain:
     F*(A->B->C) ~ F*(A->B) . F*(B->C)"

Two defects, both fatal to the statement rather than to the idea.

**Frames.** F*(A->B) is a fraction of the A-B prior gap; F*(B->C) is a fraction
of the B-C gap. Multiplying them multiplies two percentages of different bases
and reports the result as a percentage of the first. And F*(A->C) was never
defined at all -- every noophoric quantity is stated relative to a probe measure
and a pair (axiom A2), and the composite names a pair whose prior gap nobody
measured.

**Sign.** F* is unbounded below. Two antinoophors compose to a positive
product: hops of -0.629 and -1.000 multiply to +0.629, so two transfers that
each left the receiver *further* from the sender are reported as a substantially
successful chain.

The repair is to stop composing per-hop numbers and measure the chain
end-to-end **in the original sender's frame**. That quantity is well-typed, its
sign means what it says, and whether it decays geometrically becomes an
empirical question about a defined thing rather than an artifact of notation.
"""

from __future__ import annotations

import math
from typing import List, NamedTuple, Optional, Sequence

from .divergence import mean_divergence, mean_permutation_floor, to_distribution
from .fidelity import DEFAULT_EPSILON, transfer_fidelity
from .probes import ProbeMeasure

__all__ = ["ChainPoint", "ChainDecay", "chain_fidelity", "fit_decay"]


class ChainPoint(NamedTuple):
    """One hop, scored against the ORIGINAL sender."""

    hop: int                # 1 = the first receiver
    d_to_origin: float      # divergence from agent A, not from the previous hop
    fidelity: float         # F* in A's frame, against A's prior gap
    agreement: float


class ChainDecay(NamedTuple):
    """Whether chain fidelity decays geometrically, and how fast."""

    points: List[ChainPoint]
    monotone: bool             # non-increasing, as L4(a) requires
    half_life_hops: Optional[float]   # hops until fidelity halves, if decaying
    log_slope: Optional[float]        # slope of log F* against hop count
    positive_hops: int         # hops before fidelity reaches zero

    def summary(self) -> str:
        return "hops=%d monotone=%s half-life=%s slope=%s" % (
            len(self.points),
            self.monotone,
            "n/a" if self.half_life_hops is None else "%.2f" % self.half_life_hops,
            "n/a" if self.log_slope is None else "%+.3f" % self.log_slope,
        )


def chain_fidelity(
    measure: ProbeMeasure,
    origin_draws: Sequence[Sequence[str]],
    prior_draws: Sequence[Sequence[str]],
    hop_draws: Sequence[Sequence[Sequence[str]]],
    epsilon: float = DEFAULT_EPSILON,
    permutations: int = 300,
    seed: int = 0,
) -> List[ChainPoint]:
    """Fidelity of every hop against the ORIGIN, in the origin's frame.

    ``hop_draws`` is one draw-set per hop, in order. Every hop is scored
    against ``origin_draws`` -- never against the hop before it, which is what
    made the per-hop product meaningless.

    The prior gap and the floor come from the origin-vs-prior comparison and are
    shared by every hop, so the hops differ only in their numerators and are
    therefore comparable to each other. That is the whole point: a decay curve
    whose points are measured in different units is not a curve.
    """
    origin = [to_distribution(d) for d in origin_draws]
    prior = [to_distribution(d) for d in prior_draws]
    d_prior = mean_divergence(origin, prior, measure.weights)
    floor = mean_permutation_floor(
        origin_draws, prior_draws, measure.weights, permutations, seed
    )

    points: List[ChainPoint] = []
    for index, draws in enumerate(hop_draws, start=1):
        dists = [to_distribution(d) for d in draws]
        d_post = mean_divergence(origin, dists, measure.weights)
        matches = sum(
            w for a, b, w in zip(origin, dists, measure.weights)
            if max(sorted(a), key=lambda k: a[k]) == max(sorted(b), key=lambda k: b[k])
        )
        points.append(ChainPoint(
            hop=index,
            d_to_origin=d_post,
            fidelity=transfer_fidelity(d_prior, d_post, floor, epsilon),
            agreement=matches / sum(measure.weights),
        ))
    return points


def fit_decay(points: Sequence[ChainPoint]) -> ChainDecay:
    """Test L4(b): is the decay geometric?

    Fits log(F*) against hop index over the hops where F* is still positive.
    Hops at or below zero are excluded rather than clipped -- a chain that has
    reached zero fidelity has stopped carrying anything, and forcing it onto a
    log scale would invent a decay rate for a dead signal.
    """
    if not points:
        raise ValueError("no chain points to fit")
    fids = [p.fidelity for p in points]
    monotone = all(b <= a + 1e-9 for a, b in zip(fids, fids[1:]))

    usable = [(p.hop, p.fidelity) for p in points if p.fidelity > 1e-6]
    slope = half_life = None
    if len(usable) >= 2:
        xs = [float(h) for h, _ in usable]
        ys = [math.log(f) for _, f in usable]
        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        denom = sum((x - mx) ** 2 for x in xs)
        if denom > 0:
            slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
            if slope < 0:
                half_life = math.log(0.5) / slope
    return ChainDecay(
        points=list(points),
        monotone=monotone,
        half_life_hops=half_life,
        log_slope=slope,
        positive_hops=len(usable),
    )
