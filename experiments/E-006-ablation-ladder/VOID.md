# E-006 is void before collection

**2026-08-20. Zero model calls.** Void on its own pre-registered power gate,
which was computed before any draw and refused the design.

[PREREGISTRATION §5](PREREGISTRATION.md) committed to: *"If that fraction is
below 0.80, this experiment does not run as designed. Either the rung count
rises or the hypothesis is withdrawn before any draw. A design that cannot
detect its own effect is not evidence of absence."*

[POWER.md](POWER.md) returns **0.117** against a moderately concave truth on 32
probes. The gate refuses the run, and raising the rung count does not repair it —
the noise is probe-level, so eight rungs or eighty make no difference.

**Required: about 512 probes.** `MERIDIAN-IX32` has 32, and about nine
independent prompt templates. The instrument is short by more than an order of
magnitude.

## Why this is the useful outcome

E-002c's ladder was underpowered for exactly this question, nobody computed it,
and its fidelity column was subsequently read as bearing on L1 — which is how
[retraction 17](../../RETRACTIONS.md) was found and how this experiment came to
be designed at all. The difference here is only that the check ran first.

Nothing is claimed. Nothing is withdrawn. `L1` remains `conjectured` and remains
untested, and now the reason is on the record: **not that it has not been tried,
but that no probe measure this programme owns can carry the test.**

The successor is not a better ladder. It is a probe measure an order of magnitude
larger — and [retraction 15](../../RETRACTIONS.md) is the warning attached to
building one, since thirty-two probes that are nine templates would become five
hundred probes that are ninety.

---

*This document is licensed CC BY 4.0.*
