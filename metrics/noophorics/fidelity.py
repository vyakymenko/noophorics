"""Fidelity, efficiency, phantom agreement, capacity.

Reference implementation of theory/definitions.md sections 4, 5 and 6.
"""

from __future__ import annotations

from typing import Iterable, NamedTuple, Optional, Sequence

__all__ = [
    "DEFAULT_EPSILON",
    "InadmissibleProbeMeasure",
    "is_admissible",
    "transfer_fidelity",
    "efficiency",
    "claimed_agreement",
    "phantom_agreement",
    "capacity_estimate",
    "capacity_lower_bound",
    "CapacityBound",
    "residual_estimate",
    "Measurement",
]

# Minimum gap above the noise floor for a probe measure to be admissible.
# Below this the fidelity denominator collapses and F* is undefined.
DEFAULT_EPSILON = 0.02


class InadmissibleProbeMeasure(ValueError):
    """The parties did not disagree enough before transfer to measure anything."""


def is_admissible(
    d_prior: float, d_floor: float, epsilon: float = DEFAULT_EPSILON
) -> bool:
    """Whether a probe measure admits a fidelity measurement. definitions.md 3.3

    Fidelity is a fraction of a gap. If there is no gap above the noise floor,
    there is nothing to close and the measurement is vacuous -- a common and
    flattering mistake, since inadmissible measures produce F* near 1 for any
    message at all.
    """
    return (d_prior - d_floor) > epsilon


def transfer_fidelity(
    d_prior: float,
    d_post: float,
    d_floor: float,
    epsilon: float = DEFAULT_EPSILON,
) -> float:
    """F* -- floor-corrected transfer fidelity. definitions.md 4.1

        F* = (D_prior - D_post) / (D_prior - D_floor)

    Returned *unclipped* below zero. A negative F* is an antinoophor: the
    message left the receiver further from the sender than before. Clipping
    would hide them, and they are among the most informative observations in
    the field.

    Capped at 1.0 above, since a post-transfer divergence below the noise floor
    is sampling luck, not superhuman transfer.
    """
    if not is_admissible(d_prior, d_floor, epsilon):
        raise InadmissibleProbeMeasure(
            "d_prior (%.4f) does not exceed d_floor (%.4f) by epsilon (%.4f); "
            "the parties already agreed, so there is no gap to close"
            % (d_prior, d_floor, epsilon)
        )
    return min(1.0, (d_prior - d_post) / (d_prior - d_floor))


def efficiency(fidelity: float, cost: float, per: float = 1000.0) -> float:
    """eta -- fidelity per unit cost. definitions.md 4.3

    ``cost`` in the receiver's tokens by default; ``per`` rescales the result
    (default: fidelity per kilotoken, to keep the numbers legible).
    """
    if cost <= 0:
        raise ValueError("cost must be positive; a free message is not a message")
    return fidelity * per / cost


def claimed_agreement(sender_claim: float, receiver_claim: float) -> float:
    """C-hat -- mean of the two parties' claimed agreement rates. 5

    Both claims are elicited in the same units as the observed agreement rate:
    "over probes of this kind, what fraction of your decisions would match the
    other party's?" Report the two claims separately as well -- the asymmetry
    between them is data, not noise.
    """
    for name, claim in (("sender", sender_claim), ("receiver", receiver_claim)):
        if not (0.0 <= claim <= 1.0):
            raise ValueError("%s claim %.4f is not a rate in [0, 1]" % (name, claim))
    return 0.5 * (sender_claim + receiver_claim)


def phantom_agreement(claimed: float, observed: float) -> float:
    """Phi -- belief minus reality. definitions.md 5

        Phi = C-hat - A-hat

    Phi > 0: shared illusion. Both parties overestimate what landed. This is
             the field's central pathology.
    Phi ~ 0: calibrated.
    Phi < 0: mutual underconfidence -- more transferred than either believes.
             Rarer, and its own failure mode: it causes redundant
             re-explanation and unnecessary escalation.
    """
    return claimed - observed


def capacity_estimate(fidelities: Iterable[float]) -> float:
    """DEPRECATED (v0.1). Biased UPWARD. Use capacity_lower_bound. v0.3

    This returns the max of N noisy fidelity estimates and was documented as a
    *lower* bound on K. That is wrong in expectation: the maximum of noisy
    estimates is biased upward, and the bias grows with both N and the
    per-estimate noise. Measured, with every candidate sharing a true F* of
    0.60 and the ~0.10 estimator noise the validation reports at small n:

        N =   3  ->  K-hat 0.685
        N =  10  ->  K-hat 0.754
        N =  30  ->  K-hat 0.804
        N = 100  ->  K-hat 0.850

    At sd = 0.20 and N = 30 it exceeds 1.0 outright. So PRINCIPIA's third
    falsification criterion -- "K ~ 1 in practice" -- would fire from search
    size alone, independent of the truth. A criterion guaranteed to trigger
    is worse than an unfalsifiable one: it manufactures its own refutation.

    Kept only so v0.1 numbers stay recomputable.
    """
    values = list(fidelities)
    if not values:
        raise ValueError("cannot estimate capacity from an empty search")
    return max(values)


class CapacityBound(NamedTuple):
    """A capacity estimate that states how it was obtained. v0.3"""

    lower_bound: float        # held-out fidelity of the selected encoding
    selected_index: int
    selection_score: float    # its score on the selection split -- the biased one
    winners_curse: float      # selection_score - lower_bound
    search_size: int
    cost_ceiling: Optional[float]  # K is a curve K(C); this is the C it belongs to

    def summary(self) -> str:
        return (
            "K(C<=%s) >= %.3f  [selected #%d of %d; selection score %.3f, "
            "winner's curse %+.3f]"
            % (
                "inf" if self.cost_ceiling is None else "%.0f" % self.cost_ceiling,
                self.lower_bound, self.selected_index, self.search_size,
                self.selection_score, self.winners_curse,
            )
        )


def capacity_lower_bound(
    selection_scores: Sequence[float],
    holdout_scores: Sequence[float],
    cost_ceiling: Optional[float] = None,
) -> CapacityBound:
    """K(C) lower bound by sample splitting. definitions.md 6.1 (v0.3)

    Choose the best encoding using one probe split, then report its fidelity on
    a split that played no part in choosing it. The held-out score is unbiased
    for the encoding that was selected, so it is a genuine lower bound on K --
    which is what v0.1 claimed to return and did not.

    ``selection_scores`` and ``holdout_scores`` are aligned: one pair per
    candidate encoding. The splits must be disjoint, and the holdout must be
    probes the *sender* never saw either -- otherwise a lookup table wins (the
    counterexample that refuted axiom A3).

    ``cost_ceiling`` records which point of the curve this is. Capacity without
    a cost bound is not a quantity: at unbounded cost and visible probes it is
    trivially 1.
    """
    if len(selection_scores) != len(holdout_scores):
        raise ValueError("candidate count mismatch between the two splits")
    if not selection_scores:
        raise ValueError("cannot estimate capacity from an empty search")
    best = max(range(len(selection_scores)), key=lambda i: selection_scores[i])
    return CapacityBound(
        lower_bound=holdout_scores[best],
        selected_index=best,
        selection_score=selection_scores[best],
        winners_curse=selection_scores[best] - holdout_scores[best],
        search_size=len(selection_scores),
        cost_ceiling=cost_ceiling,
    )


def residual_estimate(capacity: float) -> float:
    """R-hat = 1 - K-hat. definitions.md 6.2

    An *upper* bound on the residual, since K-hat is a lower bound on K.
    """
    return 1.0 - capacity


class Measurement(NamedTuple):
    """A complete, reportable noophoric measurement.

    The fields are exactly the reporting standard in definitions.md section 7.
    A measurement missing any of them is an anecdote; anecdotes belong in
    journal/, not in theory/.
    """

    probe_measure_id: str
    samples_per_probe: int
    sender: str
    receiver: str
    d_prior: float
    d_post: float
    d_floor: float
    cost_tokens: float
    cost_unit: str
    agreement_observed: float
    claim_sender: Optional[float] = None
    claim_receiver: Optional[float] = None
    condition: str = ""
    notes: str = ""

    @property
    def fidelity(self) -> float:
        return transfer_fidelity(self.d_prior, self.d_post, self.d_floor)

    @property
    def efficiency(self) -> float:
        return efficiency(self.fidelity, self.cost_tokens)

    @property
    def phantom(self) -> Optional[float]:
        """Phi, or None if neither party was asked to predict."""
        claims = [c for c in (self.claim_sender, self.claim_receiver) if c is not None]
        if not claims:
            return None
        return phantom_agreement(sum(claims) / len(claims), self.agreement_observed)

    @property
    def is_antinoophor(self) -> bool:
        return self.fidelity < 0.0

    def summary(self) -> str:
        phi = self.phantom
        return (
            "[%s] %s -> %s | F*=%+.3f  eta=%.3f/kTok  A=%.3f  Phi=%s  C=%.0f %s"
            % (
                self.condition or "unnamed",
                self.sender,
                self.receiver,
                self.fidelity,
                self.efficiency,
                self.agreement_observed,
                ("%+.3f" % phi) if phi is not None else "n/a",
                self.cost_tokens,
                self.cost_unit,
            )
        )
