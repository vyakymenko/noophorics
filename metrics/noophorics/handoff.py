"""NHP-0001 v0.2 — the handoff gate, and the four defects it repairs.

v0.1 of the protocol was published as a document with no implementation, on the
stated grounds that publishing early lets it be wrong in public. It was. Four
defects, all of which survive a careful reading of the prose and none of which
survive an attempt to run it.

D1 -- THE EXAM SHIPPED WITH ITS ANSWER KEY
    v0.1's message carries ``"expected": "compat_shim"`` inside the payload the
    receiver reads, and §3.1 asks the receiver to answer "without consulting
    expected". For a human that is an honour system. For a language model it is
    not even that: the key is in context, and an in-context answer is not
    evidence about what the receiver reconstructed from the constraints. Every
    Â measured under v0.1 would be an upper bound of unknown tightness.

    Repaired by ``seal()``: keys never enter the transmitted payload. The
    payload carries a hash over probes-and-keys, which binds the sender to a key
    it cannot revise after seeing answers, and ``verify_no_key_leak()`` refuses
    any payload in which a key survives.

D2 -- THE GATE PASSES ITS OWN WORST CASE
    v0.1 blocks when ``Φ > θ``. Take a sender claiming 0.30 agreement, a
    receiver claiming 0.30, and an observed 0.30. Φ = 0.00, the gate passes,
    and the parties proceed having agreed on 30% of the probes. The protocol
    green-lights a well-calibrated catastrophe, because Φ measures whether the
    parties were *right about* the transfer, not whether the transfer happened.

    Repaired with two gates. Calibration (Φ) and fidelity (Â) are different
    quantities and neither implies the other; a protocol that acts on one alone
    is blind in one of two directions.

D3 -- Â IS NOT FLOOR-CORRECTED
    Every other number in this programme is corrected against a baseline, on
    the argument that an uncorrected quantity is unfinished. v0.1's Â is raw
    agreement against a key. On a two-option probe set a receiver that ignores
    the message entirely scores about 0.50, and v0.1 would call that a
    half-successful transfer.

    Repaired against the key's own marginal: the baseline is what a receiver
    scores by drawing from the distribution of correct answers without reading
    anything. Reported alongside the raw number, never instead of it.

D4 -- THE THRESHOLD IS FINER THAN THE INSTRUMENT
    v0.1 requires "at least three probes" and sets θ = 0.15. With three probes
    answered once each, Â can only take the values 0, ⅓, ⅔, 1 — the measurement
    grid is 0.33 wide and the decision threshold is 0.15. Before any question of
    sampling error, the gate is being asked to resolve a difference the
    instrument cannot represent.

    Repaired by deriving the minimum from θ (``minimum_draws``) and by refusing
    to return a verdict the evidence cannot support: ``Decision.proceed`` is
    None, not True, when the draw count is inadequate. Underpowered is a third
    outcome, not a quiet pass.

The M33 lesson applies to this protocol more sharply than anywhere else in the
repository: here the sender writes the rules, writes the exam, and writes the
key. See ``adjudicate(independent_key=...)``.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Dict, List, Mapping, NamedTuple, Optional, Sequence

__all__ = [
    "seal",
    "verify_no_key_leak",
    "adjudicate",
    "minimum_draws",
    "key_marginal_baseline",
    "Decision",
    "KeyLeak",
    "DEFAULT_THETA",
    "DEFAULT_FIDELITY_FLOOR",
]

DEFAULT_THETA = 0.15
# Fidelity gate. Deliberately not derived from anything: it is a policy choice
# about how much divergence a caller will act on, and pretending otherwise
# would repeat v0.1's habit of presenting a guess in the voice of a result.
DEFAULT_FIDELITY_FLOOR = 0.80

# Field names that must never appear in a transmitted payload. Checked at every
# depth, because a key nested three levels down is still in context.
_KEY_FIELDS = frozenset(
    {"expected", "expected_answer", "answer", "key", "answers", "keys",
     "correct", "ground_truth", "solution"}
)


class KeyLeak(Exception):
    """A payload carries answers. Refuse to send it; the measurement is void."""


# ---------------------------------------------------------------------------
# D1 -- sealing


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def seal(probes: Sequence[Mapping[str, Any]], keys: Mapping[str, str]):
    """Split a probe set into a transmittable payload and a withheld checkset.

    The payload gets prompts and options. The checkset gets the keys and never
    leaves the adjudicator. Both carry the same ``probe_measure_id`` — a hash
    over probes *and* keys — so a sender that revises a key after seeing the
    receiver's answers produces a checkset that no longer matches the payload
    the receiver was given. The commitment is what makes the sender's own key
    admissible as evidence at all.
    """
    ids = [p["id"] for p in probes]
    if len(set(ids)) != len(ids):
        raise ValueError("probe ids must be unique")
    missing = [i for i in ids if i not in keys]
    if missing:
        raise ValueError("no key for probes: %s" % ", ".join(missing))

    payload_probes = [
        {"id": p["id"], "prompt": p["prompt"], "options": list(p["options"])}
        for p in probes
    ]
    for p, original in zip(payload_probes, probes):
        if keys[p["id"]] not in p["options"]:
            raise ValueError(
                "key for %s is not among its options -- an undecidable probe"
                % p["id"]
            )
        del original  # documentation of intent: nothing else is copied over

    digest = hashlib.sha256(
        (_canonical(payload_probes) + "\x1f" + _canonical(dict(keys))).encode()
    ).hexdigest()[:12]

    checkset = {
        "probe_measure_id": digest,
        "keys": dict(keys),
        # The baseline depends on whether every probe shares one answer space.
        # MERIDIAN-33 has one; RIVERSIDE-30 has 28 across 30 probes, and pooling
        # its keys returns 0.098 -- an artifact of the keys being nearly unique,
        # not a chance rate. Recording the spaces removes the guess.
        "option_spaces": {p["id"]: list(p["options"]) for p in payload_probes},
    }
    payload = {"probe_measure_id": digest, "probes": payload_probes}
    verify_no_key_leak(payload)
    return payload, checkset


def verify_no_key_leak(payload: Any, _path: str = "$") -> None:
    """Raise if anything answer-shaped survives anywhere in the payload.

    Walks to arbitrary depth. A protocol whose central safeguard is "the
    receiver promises not to look" has no safeguard, so this is checked
    mechanically and raises rather than warns.
    """
    if isinstance(payload, Mapping):
        for k, v in payload.items():
            if str(k).lower() in _KEY_FIELDS:
                raise KeyLeak(
                    "payload carries %s at %s.%s -- the receiver would answer "
                    "with the key in context, and Â would measure reading, not "
                    "transfer" % (k, _path, k)
                )
            verify_no_key_leak(v, "%s.%s" % (_path, k))
    elif isinstance(payload, (list, tuple)):
        for i, v in enumerate(payload):
            verify_no_key_leak(v, "%s[%d]" % (_path, i))


# ---------------------------------------------------------------------------
# D3 -- baseline


def key_marginal_baseline(
    keys: Mapping[str, str],
    option_spaces: Optional[Mapping[str, Sequence[str]]] = None,
) -> float:
    """Agreement reachable without reading the handoff at all.

    A receiver that knows only the distribution of correct answers and draws
    from it matches with probability Σ p(o)². This is the honest zero for Â: a
    probe set whose answers are 90% one option hands out 0.82 for free, and an
    uncorrected 0.85 on such a set is worse than nothing.

    THAT ARGUMENT ASSUMES ONE SHARED ANSWER SPACE, and the assumption was
    unstated until a measure violated it. `MERIDIAN-33` has a single space
    (HANDLED / RETURNED / PADDED) across all 33 probes, so pooling the keys is
    meaningful. `RIVERSIDE-30` has 28 distinct spaces across 30 probes -- dates,
    amounts, verdict strings -- and pooling them returns 0.0978, which is not a
    baseline but an artifact of the keys being mostly unique. The correct rate
    there is uniform guessing *within each probe*: 0.3333.

    Pass ``option_spaces`` and the right thing happens either way. Omit it and
    this raises when the keys look like they came from more than one space,
    because silently returning the wrong baseline is how an uncorrected number
    gets called corrected.
    """
    if not keys:
        raise ValueError("no keys")
    if option_spaces is not None:
        spaces = {tuple(sorted(option_spaces[k])) for k in keys}
        if len(spaces) > 1:
            # Per-probe spaces: the chance rate is the mean of 1/|options|.
            return sum(1.0 / len(option_spaces[k]) for k in keys) / len(keys)
    # Without option_spaces this assumes ONE shared space. That assumption is
    # documented rather than guessed at: a heuristic on "how many distinct keys
    # look like too many" fires on any small probe set and is a worse failure
    # than the thing it guards. seal() now records the spaces in the checkset,
    # so adjudicate() never has to assume.
    counts: Dict[str, int] = {}
    for value in keys.values():
        counts[value] = counts.get(value, 0) + 1
    total = float(len(keys))
    return sum((c / total) ** 2 for c in counts.values())


# ---------------------------------------------------------------------------
# D4 -- resolution


def minimum_draws(theta: float = DEFAULT_THETA, confidence: float = 0.95) -> int:
    """Total draws (probes × samples) needed for θ to be a resolvable threshold.

    Two requirements, and the binding one is not the obvious one:

    1. *Grid*: Â is a multiple of 1/N, so N ≥ 1/θ or the threshold falls between
       representable values.
    2. *Noise*: Â has standard error ≤ 0.5/√N. For the gate to separate Φ = 0
       from Φ = θ at the stated confidence, the half-width of the interval must
       fit inside θ.

    At θ = 0.15 the grid wants 7 draws and the noise wants 43. v0.1's floor of
    three probes answered once is short of the binding requirement by 14×.
    """
    if not 0 < theta < 1:
        raise ValueError("theta must lie in (0, 1)")
    z = {0.90: 1.6449, 0.95: 1.9600, 0.99: 2.5758}.get(confidence)
    if z is None:
        raise ValueError("confidence must be one of 0.90, 0.95, 0.99")
    grid = math.ceil(1.0 / theta)
    noise = math.ceil((z * 0.5 / theta) ** 2)
    return max(grid, noise)


# ---------------------------------------------------------------------------
# adjudication


class Decision(NamedTuple):
    proceed: Optional[bool]          # None == underpowered, not a pass
    agreement: float                 # Â, raw
    baseline: float                  # D3
    agreement_corrected: float       # (Â − b) / (1 − b)
    phi: float                       # mean(claims) − Â
    gate_fidelity: bool
    gate_calibration: bool
    n_draws: int
    n_required: int
    diverged: List[str]
    notes: List[str]


def adjudicate(
    answers: Mapping[str, Sequence[str]],
    checkset: Mapping[str, Any],
    sender_claim: float,
    receiver_claim: float,
    theta: float = DEFAULT_THETA,
    fidelity_floor: float = DEFAULT_FIDELITY_FLOOR,
    independent_key: bool = False,
) -> Decision:
    """Run both gates over a receiver's probe answers.

    ``answers`` maps probe id to the receiver's draws for that probe, in draw
    order and unaggregated — the same primitive the rest of the metrics take,
    for the same reason: a caller that collapses draws to a mode before handing
    them over has thrown away the variance the floor is computed from.

    Returns ``proceed=None`` when there is not enough evidence to rule. That
    third state is the whole repair to D4: v0.1 could only say yes or no, so an
    underpowered run was reported as a pass.
    """
    keys = checkset["keys"]
    notes: List[str] = []

    unknown = sorted(set(answers) - set(keys))
    if unknown:
        raise ValueError("answers for probes not in the checkset: %s"
                         % ", ".join(unknown))
    unanswered = sorted(set(keys) - set(answers))
    if unanswered:
        # Missing data, never a zero. A probe the receiver declined is not a
        # probe the receiver got wrong.
        notes.append("%d probe(s) unanswered and excluded from Â: %s"
                     % (len(unanswered), ", ".join(unanswered)))

    matched = 0
    n_draws = 0
    diverged: List[str] = []
    for probe_id, draws in answers.items():
        if not draws:
            notes.append("probe %s returned no draws; excluded" % probe_id)
            continue
        hits = sum(1 for d in draws if d == keys[probe_id])
        matched += hits
        n_draws += len(draws)
        if hits * 2 <= len(draws):        # majority-divergent
            diverged.append(probe_id)

    if n_draws == 0:
        raise ValueError("no draws to adjudicate")

    agreement = matched / n_draws
    spaces = checkset.get("option_spaces")
    baseline = key_marginal_baseline(
        {k: keys[k] for k in answers},
        {k: spaces[k] for k in answers} if spaces else None)
    corrected = ((agreement - baseline) / (1.0 - baseline)
                 if baseline < 1.0 else float("nan"))
    if baseline >= 1.0:
        notes.append("every key is the same option: Â is uninformative and the "
                     "probe set cannot distinguish transfer from a constant")

    phi = (sender_claim + receiver_claim) / 2.0 - agreement

    gate_fidelity = agreement >= fidelity_floor
    gate_calibration = phi <= theta
    if phi < -theta:
        # Not a block. Both parties underestimated the transfer, which is a
        # calibration failure in the safe direction -- but it is still a
        # calibration failure and silently passing it is how θ never gets
        # empirically justified.
        notes.append("Φ = %.3f: both parties underestimated the transfer; "
                     "calibration is off in the benign direction" % phi)

    n_required = minimum_draws(theta)
    if n_draws < n_required:
        notes.append(
            "underpowered: %d draws against %d required to resolve θ = %.2f. "
            "No verdict is returned; collect more before acting."
            % (n_draws, n_required, theta)
        )
        proceed: Optional[bool] = None
    else:
        proceed = gate_fidelity and gate_calibration

    if not independent_key:
        notes.append(
            "key not independently adjudicated: the sender wrote the rules, "
            "the exam, and the answers. Treat Â as the sender's self-report."
        )
    if len(answers) < 3:
        notes.append("fewer than three probes: the probe set cannot cover the "
                     "cases the sender thinks are contestable")

    return Decision(
        proceed=proceed,
        agreement=agreement,
        baseline=baseline,
        agreement_corrected=corrected,
        phi=phi,
        gate_fidelity=gate_fidelity,
        gate_calibration=gate_calibration,
        n_draws=n_draws,
        n_required=n_required,
        diverged=sorted(diverged),
        notes=notes,
    )
