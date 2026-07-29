# Pre-specified sensitivity analysis: probe M33

**Committed 2026-07-29, while E-001b is still collecting.** No effect has been
computed, no condition beyond the three baselines has been sampled, and no
result exists to have seen. That timing is the point of this file.

---

## The defect

`MERIDIAN-34`'s probe **M33** has a ground truth that the source specification
does not determine. Our own standard requires probes to be *decidable*
([definitions §1.2](../../theory/definitions.md)); M33's answer *space* is
discrete, but its answer is not fixed by the text. The
[pre-registration's claim](../E-001-fluency-cost/PREREGISTRATION.md) that every
key is derivable from the spec is **false for this probe**.

The case: a paired submission, both manuscripts in Track D, neither using the
official template, each carrying 2 endorsements.

Two rules meet, and the spec does not say which governs:

> **R5** — Both manuscripts must independently **satisfy** R1 and R2.
>
> **R6** — A Track D manuscript is **exempt from** R2… R6 exempts the
> manuscript from R2 only, and from no other rule.

**Reading A → HANDLED** (the committed key). R6 displaces R2 for this
manuscript. Where R2 does not apply, R5's demand to satisfy it is met by
substitution — the endorsements stand in.

**Reading B → RETURNED.** R5 demands *satisfaction* of R2. An exemption from a
requirement is not satisfaction of it. And R6's own scope clause — "from R2
only, and from no other rule" — says the exemption does not reach R5, which is
another rule.

**Reading B is at least as well supported by the text, and arguably better**,
since it is the reading R6's explicit scope clause invites. The key was set by
the experimenter's reading and recorded as though it were derived.

## The evidence that it is contested, not merely arguable

| decider | M33 |
|---|---|
| `gpt-oss:120b` think=low | RETURNED |
| `claude-opus-4-8` | RETURNED |
| adversarial reviewer (independent) | flagged as textually undetermined |
| `gpt-oss:120b` think=medium *(E-001b's sender)* | HANDLED, 30/30 |
| committed key | HANDLED |

Three independent deciders read it against the key. The current sender reads it
*with* the key, unanimously — which is not evidence the key is right, only that
sender and key happen to agree.

## Why it matters here specifically

In v0.3 the answer key was promoted from a sanity check to a **load-bearing
input**: [`decompose()`](../../metrics/noophorics/decomposition.py) partitions
probes by whether the sender was correct, and computes
`fidelity_where_sender_right` and `error_replication` from that partition. A
wrong key puts a probe in the wrong half and biases both.

M33 also carries maximal divergence in [E-001](../E-001-fluency-cost/FINDINGS.md)
and sits inside the sender-accuracy gate's margin. It is not a quiet probe.

## What will be done

The probe measure is **not** being changed. E-001b is mid-collection, and
editing the instrument during a run is the failure this programme has already
recorded once.

Instead, **every E-001b effect will be reported twice: over all 34 probes, and
over the 33 excluding M33.** Both numbers go in the results file and in the
findings, whichever way they fall.

- If the two agree, M33 is a blemish on the instrument and nothing more.
- If they disagree, the disagreement is the finding, and no directional claim
  survives it.

This is pre-specified rather than chosen after seeing which version is more
favourable. That distinction is the only thing separating a sensitivity
analysis from a garden of forking paths.

## Consequences beyond this run

1. `MERIDIAN-34` is superseded for future experiments by a measure in which
   M33 is either repaired (R5 amended to say explicitly whether exemption
   counts as satisfaction) or removed.
2. **Probe review needs a procedure.** M33 was written by the same person who
   wrote the rules and the key, and read as obvious to its author. The
   contestability was found by outside readers — the same pattern as every
   other finding in this repository. A keyed probe should be adjudicated
   independently before it is committed, and that requirement belongs in
   [CONTRIBUTING](../../CONTRIBUTING.md).

## Siblings checked and cleared

`M22` (R7 override) and `M29` (R6 scope) also involve R6, and both are
determinate: R7 states it overrides "every other rule", and R6's scope clause
settles M29 by saying the exemption covers R2 and nothing else. Only the
R5 × R6 interaction is ambiguous, and M33 is its only instance.

---

*This document is licensed CC BY 4.0.*
