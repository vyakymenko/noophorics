"""The reference disposition `R` — the target a transfer is scored against.

WHY THIS EXISTS
---------------
For three versions `F*` measured movement toward **the sender**, and never said
so. The sender was not a parameter, it was an assumption, and
[E-001](../../experiments/E-001-fluency-cost/FINDINGS.md) showed what that
assumption costs: both receivers out-decided the sender against the key, `F*`
ranked them the other way, and 62% of the headline effect sat on the four probes
where the sender was wrong and a receiver was right.

The repair is not to score against the key instead. It is to make the target a
**declared argument** with recorded provenance, the way forecast verification
has done since at least Murphy (1988), where the reference is a named argument
of the skill score and *which* reference you pick changes what the score means.
See [prior-art §8](../../theory/prior-art.md).

THE LICENSING RULE, which is the point of the module
----------------------------------------------------
The word *understanding* is licensed only where `R` is independent of the
sender. Where `R` is the sender, the quantity measured is **replication**, and
naming it that is the whole repair: nothing about the arithmetic changes, and
everything about what may be claimed does.

Independence from the *message* is not the criterion and does not bite — the
sender's own probe draws are not descendants of its message, so a sender
reference would pass that test. The criterion is independence from the sender.

THE TRAP THIS MODULE REFUSES
----------------------------
A reference built by resampling the sender is not a reference. The repository
already shipped one: the `CEILING` arm gave the same model the same context and
scored 25 of 25 draw sequences **bit-identical** to the sender, mean JSD 0.0000,
while passing a 0.70 gate at 1.0000 (journal, 2026-07-30). `independence_of`
exists so that construction fails loudly rather than certifying itself.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, NamedTuple, Optional, Sequence

from .divergence import jensen_shannon, to_distribution
from .probes import ProbeMeasure

__all__ = ["Reference", "independence_of", "INDEPENDENCE_EPSILON"]

# Below this mean JSD from the sender, a reference is not independent of it.
# Not tuned: it is the smallest gap that is not obviously sampling noise at the
# sample sizes used here, and it is stated rather than justified.
INDEPENDENCE_EPSILON = 0.02


class Reference(NamedTuple):
    """A per-probe target distribution, declared before data with its provenance.

    ``distributions`` is parallel to the probe measure. ``provenance`` is
    required and free text: who set this reference, from what, and whether it
    was independently adjudicated. A reference without a provenance is an
    undeclared assumption wearing a parameter's clothes, which is the thing
    being repaired.
    """

    id: str
    kind: str                       # "key" | "panel" | "sender"
    distributions: List[Dict[str, float]]
    provenance: str
    adjudicated: bool = False

    @property
    def licenses_understanding(self) -> bool:
        """Whether results against this reference may use the word.

        A sender reference measures replication. That is a real quantity and
        often the right one -- transferring a preference, a house style, a
        judgment call whose owner defines the correct answer -- but it is not
        understanding, and the two were conflated for three versions.
        """
        return self.kind != "sender"

    @classmethod
    def from_key(cls, measure: ProbeMeasure, provenance: str,
                 adjudicated: bool = False,
                 contested: Optional[Mapping[str, Mapping[str, float]]] = None
                 ) -> "Reference":
        """The certified case: a point mass on each probe's key.

        ``contested`` overrides individual probes with a non-degenerate
        distribution over the defensible readings. That is not a nicety: `M33`
        of MERIDIAN-34 has a key the source text does not determine
        (SENSITIVITY-M33.md), and a binary key cannot express "two readings, one
        slightly better supported" while a distribution can.
        """
        missing = [p.id for p in measure if p.key is None]
        if missing:
            raise ValueError("no key for probes: %s" % ", ".join(missing))
        dists: List[Dict[str, float]] = []
        for p in measure:
            override = (contested or {}).get(p.id)
            if override is not None:
                unknown = set(override) - set(p.options)
                if unknown:
                    raise ValueError("%s: contested mass on non-options %s"
                                     % (p.id, sorted(unknown)))
                total = float(sum(override.values()))
                if total <= 0:
                    raise ValueError("%s: contested distribution sums to zero" % p.id)
                dists.append({k: v / total for k, v in override.items()})
            else:
                dists.append({p.key: 1.0})
        return cls("key@%s" % measure.qualified_id, "key", dists, provenance,
                   adjudicated)

    @classmethod
    def from_panel(cls, measure: ProbeMeasure,
                   panel_draws: Mapping[str, Sequence[Sequence[str]]],
                   provenance: str) -> "Reference":
        """A declared mixture over independent adjudicators.

        Each adjudicator contributes draws parallel to the measure; the
        reference is their equal-weight mixture. **Inter-adjudicator agreement
        must be reported alongside**, and a unanimous panel is a warning rather
        than a validation: a panel that shares the sender's bias reproduces
        "the sender is always right" at group level.
        """
        if len(panel_draws) < 2:
            raise ValueError("a panel needs at least two adjudicators; got %d"
                             % len(panel_draws))
        names = sorted(panel_draws)
        for name in names:
            if len(panel_draws[name]) != len(measure):
                raise ValueError("%s: %d draw rows for %d probes"
                                 % (name, len(panel_draws[name]), len(measure)))
        dists = []
        for i in range(len(measure)):
            mixed: Dict[str, float] = {}
            for name in names:
                for answer, mass in to_distribution(panel_draws[name][i]).items():
                    mixed[answer] = mixed.get(answer, 0.0) + mass / len(names)
            dists.append(mixed)
        return cls("panel[%s]" % ",".join(names), "panel", dists, provenance)

    @classmethod
    def from_agent(cls, measure: ProbeMeasure,
                   draws: Sequence[Sequence[str]], name: str,
                   provenance: str) -> "Reference":
        """The sender itself. Measures replication; does not license the word."""
        if len(draws) != len(measure):
            raise ValueError("%d draw rows for %d probes" % (len(draws), len(measure)))
        return cls("sender[%s]" % name, "sender",
                   [to_distribution(d) for d in draws], provenance)


def independence_of(reference: Reference,
                    sender_draws: Sequence[Sequence[str]]) -> Dict[str, Any]:
    """Is this reference distinguishable from the sender at all?

    Returns the mean JSD, the count of bit-identical rows, and a verdict. A
    reference that resamples the sender degenerates `F*_R` back into movement
    toward the sender while wearing the vocabulary of a criterion -- which is
    strictly worse than the undeclared version, because it looks checked.
    """
    if len(reference.distributions) != len(sender_draws):
        raise ValueError("reference and sender draws are different lengths")
    s = [to_distribution(d) for d in sender_draws]
    per = [jensen_shannon(r, x) for r, x in zip(reference.distributions, s)]
    mean = sum(per) / len(per)
    identical = sum(1 for r, x in zip(reference.distributions, s) if r == x)
    by_construction = reference.kind != "sender"
    distinguishable = mean > INDEPENDENCE_EPSILON

    # These are two different facts and the first version conflated them, which
    # would have rejected a perfectly legitimate key. A key drawn from the
    # source specification IS independently constructed; on a measure where the
    # sender happens to answer every probe correctly it is nonetheless
    # behaviourally indistinguishable from the sender, and F*_key then equals
    # F*_sender identically. That is not a defect in the reference. It is the
    # measure failing to discriminate between references at all.
    if not by_construction:
        verdict = "sender reference: replication, never understanding"
    elif not distinguishable:
        verdict = ("independently constructed but behaviourally indistinguishable "
                   "from the sender on this measure -- F*_R will equal "
                   "F*_sender, and the reference choice cannot inform anything "
                   "here. A perfect sender hides the entire problem.")
    else:
        verdict = "independent and discriminating"

    return {
        "mean_jsd_from_sender": mean,
        "identical_distributions": identical,
        "n_probes": len(per),
        "independent_by_construction": by_construction,
        "distinguishable_on_this_measure": distinguishable,
        "usable": bool(by_construction and distinguishable),
        "verdict": verdict,
    }
