# Amendment 001 — the probe measure is MERIDIAN-34, not MERIDIAN-33

**Raised 2026-08-03, before any experimental datum exists.** Found by executing
the dry run, not by re-reading the document.

---

## The error

[PREREGISTRATION §3](PREREGISTRATION.md) says:

> **Probe measure.** `MERIDIAN-33`, the same instrument E-001b registered.

The two halves of that sentence contradict each other.
[E-001b](../E-001b-fluency-factorial/PREREGISTRATION.md) registered
**`MERIDIAN-34`**, 24 visible and 10 held out. `MERIDIAN-33` is a different
measure — the 34 with probe M33 removed — and it belongs to the E-002 line, not
the E-001 line.

The same error propagates to the gate table, which reads *"Sender error count
≤ 2 of 33"*.

## Which reading governs, and why

**`MERIDIAN-34`.** The subordinate clause names the source unambiguously and the
inherited runner loads `E-001-fluency-cost/probes.json`, which is the 34-probe
measure. `MERIDIAN-33` appears once, as a name; the design it sits in is the
34-probe one throughout.

The gate is therefore **≤ 2 errors of 34**, which is the threshold E-001b
registered and the one the count was reasoned about: E-001's sender passed a
mean-accuracy gate at 0.882 while four errors of 34 carried 62% of the headline.

## What this costs

**It consumes the amendment cap.** §7 of the pre-registration allows one
amendment. A clerical contradiction is arguably not the "instrument only"
category the policy describes, and it would be easy to rule that a correction of
an internal inconsistency does not count.

It counts. A policy whose exceptions are decided by the person who needs one is
not a policy, and this programme has already recorded what happens when an
ambiguity is resolved after knowing which way it helps
([E-001b VOID](../E-001b-fluency-factorial/VOID.md)). E-001c now has **no
amendments remaining**; anything further requires a new registration under a new
id.

## Why it was not caught

The document was written after a long stretch of work on E-002c and E-004, both
of which use `MERIDIAN-33`. The name was carried across by hand while the design
around it was inherited from E-001b.

Nothing would have caught it. `check_counts.py` checks stated counts against
their sources, `check_retracted.py` checks claims, `check_links.py` checks
pointers — and none of them knows that a probe measure named in prose must match
the one a runner loads. The dry run caught it because a dry run prints what it
actually loaded, which is the only artifact in this repository that could have.

**Recorded as a task, not performed here:** a check that a pre-registration's
named probe measure matches the measure its runner loads. It is the same shape
as [Problem 13](../../theory/open-problems.md) — a document and a computation
disagreeing with nothing between them — and it should probably be solved with it
rather than separately.

---

*This document is licensed CC BY 4.0.*
