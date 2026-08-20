"""Fidelity, efficiency, phantom agreement, capacity.

Reference implementation of theory/definitions.md sections 4, 5 and 6.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, NamedTuple, Optional, Sequence

from .divergence import (jensen_shannon, mean_divergence,
                         mean_permutation_floor, to_distribution)

__all__ = [
    "DEFAULT_EPSILON",
    "InadmissibleProbeMeasure",
    "MismatchedFloorPair",
    "fidelity_from_draws",
    "is_admissible",
    "transfer_fidelity",
    "efficiency",
    "net_value",
    "fidelity_to_reference",
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


class MismatchedFloorPair(ValueError):
    """The floor corrects a comparison other than the one being made.

    `D_floor` is finite-sample estimator bias *for a stated pair of parties*.
    The permutation null pools that pair's draws, so a floor taken on one pair
    does not correct another. E-002c computed the floor between sender and
    PRIOR and applied it to sender-versus-receiver -- different pairs, and the
    sender was a point mass on every probe while PRIOR was not, so the floor
    came out an order of magnitude too large and inflated every fidelity it
    touched ([retraction 17](../../RETRACTIONS.md)).

    Seventeen days, a published table, and nothing could see it: the estimator
    received three floats and had no way to know which comparisons produced
    them. This exception is that missing argument.
    """


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
    post_pair=None,
    floor_pair=None,
) -> float:
    """F* -- floor-corrected transfer fidelity. definitions.md 4.1

        F* = (D_prior - D_post) / (D_prior - D_floor)

    Returned *unclipped* below zero. A negative F* is an antinoophor: the
    message left the receiver further from the sender than before. Clipping
    would hide them, and they are among the most informative observations in
    the field.

    Capped at 1.0 above, since a post-transfer divergence below the noise floor
    is sampling luck, not superhuman transfer.

    `post_pair` and `floor_pair` are optional declarations of *which two
    parties* produced `d_post` and `d_floor`. When both are given and differ,
    this raises `MismatchedFloorPair`. They are optional because callers that
    already pass bare floats cannot be made to know, and a required argument
    would have broken every one of them into silence; prefer
    `fidelity_from_draws`, where the mismatch cannot be expressed at all.
    """
    if (post_pair is not None and floor_pair is not None
            and tuple(post_pair) != tuple(floor_pair)):
        raise MismatchedFloorPair(
            "d_floor was taken on %r but d_post compares %r; a floor corrects "
            "the bias of one comparison and does not transfer to another"
            % (tuple(floor_pair), tuple(post_pair)))
    if not is_admissible(d_prior, d_floor, epsilon):
        raise InadmissibleProbeMeasure(
            "d_prior (%.4f) does not exceed d_floor (%.4f) by epsilon (%.4f); "
            "the parties already agreed, so there is no gap to close"
            % (d_prior, d_floor, epsilon)
        )
    return min(1.0, (d_prior - d_post) / (d_prior - d_floor))


def fidelity_from_draws(
    sender_draws,
    prior_draws,
    post_draws,
    weights=None,
    permutations: int = 400,
    seed: int = 0,
    epsilon: float = DEFAULT_EPSILON,
    floor_on: str = "post",
) -> dict:
    """`F*` with all three quantities computed from the same draws.

    `transfer_fidelity` takes three floats and cannot know which comparisons
    produced them. This takes the draws instead, so the mismatch that produced
    [retraction 17](../../RETRACTIONS.md) cannot be written.

        D_prior  divergence(sender, prior)
        D_post   divergence(sender, post)
        D_floor  permutation floor on the pair named by `floor_on`

    **`floor_on` is a real choice and it is left to the caller on purpose.**
    The default `"post"` takes the floor on `(sender, post)`, on the argument
    that `D_floor` corrects the bias of the `D_post` term: a receiver that had
    perfectly reconstructed the sender would score `D_floor`, not zero, at this
    `n`. `"prior"` takes it on `(sender, prior)` and reproduces what E-002c did
    -- available so an old number can be regenerated deliberately, never by
    accident.

    What the choice costs is not settled here. A `"post"` floor is per-receiver,
    so each message gets its own denominator and fidelities are no longer on one
    common scale; a `"prior"` floor is shared, and wrong whenever the receiver's
    spread differs from the prior's. [Retraction 2](../../RETRACTIONS.md)
    established that the floor is estimator bias rather than a property of the
    agents, which points at `"post"`; comparability points at `"prior"`. Nobody
    has stated which the definition intends, and this docstring is the first
    place the question is written down.

    Returns every intermediate, because a fidelity whose floor cannot be
    inspected is how seventeen days happened.
    """
    if floor_on not in ("post", "prior"):
        raise ValueError("floor_on must be 'post' or 'prior', not %r" % (floor_on,))
    s_d = [to_distribution(c) for c in sender_draws]
    p_d = [to_distribution(c) for c in prior_draws]
    r_d = [to_distribution(c) for c in post_draws]
    d_prior = mean_divergence(s_d, p_d, weights)
    d_post = mean_divergence(s_d, r_d, weights)
    other = post_draws if floor_on == "post" else prior_draws
    d_floor = mean_permutation_floor(sender_draws, other, weights,
                                     permutations, seed)
    return {
        "d_prior": d_prior,
        "d_post": d_post,
        "d_floor": d_floor,
        "floor_on": floor_on,
        "fidelity": transfer_fidelity(d_prior, d_post, d_floor, epsilon),
    }


def fidelity_to_reference(
    reference,
    prior_dists: Sequence[Dict[str, float]],
    post_dists: Sequence[Dict[str, float]],
    weights: Optional[Sequence[float]] = None,
    d_floor: float = 0.0,
    epsilon: float = DEFAULT_EPSILON,
) -> float:
    """F*_R -- the fraction of the receiver's distance to R that the message closed.

        F*_R = (D_R(B) - D_R(B|m)) / (D_R(B) - D_floor,R)

    The reference is an ARGUMENT, not an assumption. For three versions this
    quantity measured movement toward the sender and never said so; see
    ``reference.py`` for why that cost E-001 its headline.

    WHICH F* THIS GENERALISES, stated because the repository defines two
    objects and they are not the same. definitions.md 3 defines F* over TRUE
    distributions as (D_prior - D_post) / D_prior; 4.1 and this module compute
    the floor-corrected ESTIMATOR. F*_R generalises the definition, and the
    floor stays exactly where v0.3 put it -- inside the estimator, correcting
    finite-sample bias, never inside the definition.

    THE FLOOR UNDER A DECLARED REFERENCE. ``D_floor`` is a permutation null over
    *the pair being compared*, so under reference R it is the null between R's
    draws and the receiver's. Where R is a declared distribution carrying no
    sampling noise -- a key -- there is nothing to permute and the null is
    UNDEFINED, not zero. The receiver's finite-sample bias does not vanish
    because the reference is exact. Passing ``d_floor=0.0`` for a keyed
    reference is a choice to leave that bias uncorrected, and it is the caller's
    to make and to report.

    ``F*_{R=sender} `` is identically the v0.1-v0.3 ``transfer_fidelity``. Every
    published number stays valid under a longer name; the test suite pins it.
    """
    dists = reference.distributions if hasattr(reference, "distributions") else reference
    if not (len(dists) == len(prior_dists) == len(post_dists)):
        raise ValueError("reference, prior and post must be the same length")
    w = list(weights) if weights is not None else [1.0] * len(dists)
    total = float(sum(w))
    d_prior = sum(jensen_shannon(r, b) * wi for r, b, wi in
                  zip(dists, prior_dists, w)) / total
    d_post = sum(jensen_shannon(r, b) * wi for r, b, wi in
                 zip(dists, post_dists, w)) / total
    return transfer_fidelity(d_prior, d_post, d_floor, epsilon)


def net_value(fidelity: float, cost: float, lam: float, per: float = 1000.0) -> float:
    """V_lambda = F* - lambda*C. definitions.md 4.3

    The cost-adjusted comparison that works at every sign. ``lam`` is the
    exchange rate between one unit of fidelity and ``per`` tokens, and it is a
    required argument because it is a policy choice: pretending a ratio avoided
    that choice was most of the appeal of the ratio, and the ratio was wrong.

    Monotone in both arguments regardless of sign, so it orders messages the way
    the field means to: more fidelity better, more cost worse, always. Sweeping
    ``lam`` traces the frontier, which is the capacity curve K(C) seen sideways.
    """
    if cost <= 0:
        raise ValueError("cost must be positive; a free message is not a message")
    return fidelity - lam * (cost / per)


def efficiency(fidelity: float, cost: float, per: float = 1000.0) -> float:
    """eta -- fidelity per unit cost. definitions.md 4.3

    ``cost`` in the receiver's tokens by default; ``per`` rescales the result
    (default: fidelity per kilotoken, to keep the numbers legible).

    REFUSES A NEGATIVE FIDELITY, and this is the interesting part. A ratio with
    a signed numerator is not an ordering: at F* = -1.0 a 100-token antinoophor
    scores -10.00 and an 800-token one scores -1.25, so the message that spends
    eight times as much to do the same damage ranks higher. eta inverts exactly
    on the observations this library refuses to clip because they are the most
    informative ones -- and it did so in the shipped implementation for three
    versions, until an external prior-art review pointed at the ratio and the
    inversion fell out of running our own code.

    Use ``net_value`` when the sign is not known in advance.
    """
    if fidelity < 0:
        raise ValueError(
            "eta is not defined for an antinoophor (F* = %.4f): dividing a "
            "negative fidelity by cost ranks the more expensive failure higher. "
            "Use net_value(fidelity, cost, lam) with a declared lambda."
            % fidelity
        )
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

    The four reference fields are v0.4 and default to the sender convention,
    which is what every pre-v0.4 measurement in this repository actually used.
    Defaulting rather than requiring is deliberate: a hard break would have
    invalidated the constructor for historical records that are still correct.
    ``is_reportable`` is where the standard is enforced, and it refuses the
    default, so an unmigrated measurement is *constructible* and not
    *reportable*. That is the honest split -- the old numbers are real, and they
    are not fidelity-toward-a-criterion.
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
    # --- v0.4 reporting standard, definitions.md section 7 -----------------
    reference_id: Optional[str] = None
    reference_kind: Optional[str] = None        # "key" | "panel" | "sender"
    reference_provenance: Optional[str] = None
    reference_adjudicated: Optional[bool] = None
    regime: Optional[str] = None                # "criterion-bearing" | "criterion-free"
    reference_independence: Optional[Dict[str, object]] = None

    @property
    def measures_understanding(self) -> bool:
        """Whether this measurement may use the word at all.

        False for a sender reference, and False for an undeclared one -- an
        undeclared reference WAS the sender for three versions, so treating the
        two the same is the accurate reading rather than a strict one.
        """
        return self.reference_kind not in (None, "sender")

    def is_reportable(self) -> List[str]:
        """Missing fields of the reporting standard. Empty means reportable.

        Returns the list rather than a bool because "what is missing" is the
        useful answer and "no" is not.
        """
        missing = []
        if self.reference_kind is None:
            missing.append("reference_kind (undeclared reference = the sender, "
                           "silently, which is what v0.4 exists to stop)")
        if not self.reference_provenance:
            missing.append("reference_provenance (who set R, from what, and "
                           "whether it was independently adjudicated)")
        if self.regime is None:
            missing.append("regime (criterion-bearing or criterion-free)")
        if self.reference_kind not in (None, "sender") \
                and self.reference_independence is None:
            missing.append("reference_independence (a reference that resamples "
                           "the sender must fail loudly, not certify itself)")
        return missing

    @property
    def fidelity(self) -> float:
        return transfer_fidelity(self.d_prior, self.d_post, self.d_floor)

    @property
    def efficiency(self) -> Optional[float]:
        """eta, or None for an antinoophor -- where eta does not order.

        None rather than a raise: a report of a negative-fidelity transfer is a
        legitimate report and should not be unprintable. It simply has no eta.
        Use ``net_value_at`` for a cost-adjusted comparison that survives the
        sign.
        """
        if self.fidelity < 0:
            return None
        return efficiency(self.fidelity, self.cost_tokens)

    def net_value_at(self, lam: float) -> float:
        """V_lambda for this report. Defined at every sign; lambda is declared."""
        return net_value(self.fidelity, self.cost_tokens, lam)

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
