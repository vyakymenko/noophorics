# Pre-data risk note: outcome degeneracy

**Committed 2026-07-29, before the sweep, with no outcome data in existence.**
Recorded now so that it cannot later read as an excuse.

## The risk

E-002's per-probe outcome is `1(mode sender = mode receiver)`. Resolution (H2)
and the conditional asymmetry (H3) are both **undefined when that outcome is
constant**: if the receiver matches the sender on all 33 probes, there is no
diverged probe to have predicted, and there is nothing for a claim to
discriminate.

This is not hypothetical. `gpt-oss:120b` scored 1.000 accuracy with 0 errors on
this probe measure in the parameter selection for E-001b, and the receiver here
is the same model reading a competent brief about a rule set the model already
handles well. A ceiling on agreement is a live possibility.

## What is not being done about it

**No gate is being added.** The [pre-registration](PREREGISTRATION.md) lists six
gates and its amendment policy makes adding one impermissible. Adding a gate
after seeing that the design might fail is how a pre-registration becomes
decoration.

The pre-registered handling already covers the case: §7 says that if both H1 and
H2 fail, the run is reported as an **instrument result, not as evidence about
the world**. Outcome degeneracy is the mechanism by which that would happen, and
naming the mechanism in advance is disclosure, not amendment.

## What it would mean

If the outcome is constant, E-002 has measured one thing and it is worth
knowing: **this probe measure cannot discriminate a good transfer from a
perfect one for this model pair.** That is an admissibility problem on the
*post* side, and the theory has no post-side admissibility criterion —
[definitions §3.3](../../theory/definitions.md) gates only the prior gap. If
the run dies this way, the correct output is a new open problem and a
harder probe measure, not a second attempt at the same one.

---

*This document is licensed CC BY 4.0.*
