# Which reference E-002b's numbers are against

**Written 2026-07-30 while the run is at 37%, before any result exists.** The
theory changed underneath a running experiment, and the honest moment to say
what that does to its numbers is now, not when they land.

---

## What happened

E-002b was [registered](PREREGISTRATION.md) under v0.3, where `F*` measured
movement toward the sender and the target was not a stated parameter. v0.4
amended [A1 and A2](../../PRINCIPIA.md): every fidelity now takes a **declared
reference `R`**, and where `R` is the sender the reportable claim is
*replication*, not understanding.

The runner was not changed and will not be. Editing an instrument mid-run is
the failure this repository has already recorded, and `F*_{R=sender}` is
identically the pre-v0.4 quantity, so no number moves either way.

## What each E-002b quantity takes

| quantity | reference | how to report it |
|---|---|---|
| `Φ`, bias | **none** | `Φ` compares a *claimed* agreement rate against an *observed* one, and both are between the two parties. No target enters. |
| resolution, γ | **none** | Same: a within-party association between per-probe claims and per-probe outcomes. |
| conditional asymmetry (H3) | **none** | Two conditional rates over the same pairwise outcome. |
| `fidelity` | **sender** | Replication fidelity. Must not be reported as understanding. |
| `fidelity_where_sender_right` | **sender, restricted** | Convergence to the sender *on the probes where the sender matches the key* — so on that subset the sender **is** the key, and this is closer to a key-referenced quantity than the aggregate is. That restriction is the whole reason the decomposition exists. |
| `error_replication` | **sender** | Explicitly a replication measure, and named as one already. |

**H1–H4 are unaffected**: they are stated on `Φ`, resolution and the asymmetry,
none of which takes a reference.

**H5 is stated on `fidelity_where_sender_right`**, so it inherits the restricted
sender reference above.

## Why the distinction provably cannot bite here

Measured on the committed cache, before results:

```
JSD(key, sender) on MERIDIAN-33, gpt-oss:120b sender = 0.0010
sender accuracy against the key                       = 33/33
```

The sender answers every probe correctly, so the key reference and the sender
reference are **behaviourally the same object on this measure**, and `F*_key`
would equal `F*_sender` to within sampling noise. The reference choice cannot
change an E-002b number.

That is not reassurance, it is the opposite. [definitions §4.1.1](../../theory/definitions.md)
records it as the reason to declare `R` even where it demonstrably does not
move anything: **a perfect sender hides the entire problem.** E-001's sender was
wrong on four probes and there `JSD(key, sender) = 0.1176` — the same
measurement, on a measure where the distinction bites, and it is exactly where
the programme's headline failed.

## What the successor must do

E-003 and anything after it declares `R` in its pre-registration, with its
provenance and its
[`independence_of`](../../metrics/noophorics/reference.py) result, per the four
rows [§7](../../theory/definitions.md) now requires. That is a registration
obligation, not a code change, and it is cheap.

---

*This document is licensed CC BY 4.0.*
