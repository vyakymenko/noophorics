"""noophorics -- reference implementation of the noophoric metrics.

The quantitative science of transferring understanding across systems with
non-identical priors. See PRINCIPIA.md for the research program and
theory/definitions.md for the formal definitions these functions implement.

Quick start::

    from noophorics import (
        ProbeMeasure, mean_divergence, noise_floor, transfer_fidelity,
    )

    d_prior = mean_divergence(sender_dists, receiver_prior_dists)
    d_post  = mean_divergence(sender_dists, receiver_post_dists)
    floor   = noise_floor(sender_self_div, receiver_self_div)
    f_star  = transfer_fidelity(d_prior, d_post, floor)

Never report a fidelity without the floor correction, and never report one
without naming the probe measure it was taken against.
"""

from .divergence import (
    AnswerDist,
    agreement_rate,
    jensen_shannon,
    mean_divergence,
    mean_permutation_floor,
    noise_floor,
    permutation_floor,
    probe_divergence,
    self_divergence,
    to_distribution,
)
from .fidelity import (
    DEFAULT_EPSILON,
    InadmissibleProbeMeasure,
    Measurement,
    capacity_estimate,
    claimed_agreement,
    efficiency,
    is_admissible,
    phantom_agreement,
    residual_estimate,
    transfer_fidelity,
)
from .probes import Probe, ProbeMeasure, load_probe_measure

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # divergence
    "AnswerDist",
    "to_distribution",
    "jensen_shannon",
    "probe_divergence",
    "mean_divergence",
    "agreement_rate",
    "self_divergence",
    "noise_floor",
    "permutation_floor",
    "mean_permutation_floor",
    # fidelity
    "DEFAULT_EPSILON",
    "InadmissibleProbeMeasure",
    "is_admissible",
    "transfer_fidelity",
    "efficiency",
    "claimed_agreement",
    "phantom_agreement",
    "capacity_estimate",
    "residual_estimate",
    "Measurement",
    # probes
    "Probe",
    "ProbeMeasure",
    "load_probe_measure",
]
