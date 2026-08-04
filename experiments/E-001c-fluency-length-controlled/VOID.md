# E-001c is void — the fluent register has a floor where the band has a ceiling

**Status:** void · closed · successor not yet registered
**Voided:** 2026-08-04, during composition, before any probe outcome existed
**Gate:** register filter exhausted in cell A
([PREREGISTRATION §4](PREREGISTRATION.md), §6.1)

---

## Two runs, and only the second one counts

E-001c voided twice, and the difference between them is the whole reason this
document can be trusted.

**2026-08-03** — cell A exhausted its budget in 38.9 minutes. That void
establishes nothing. The runner held its own copy of the length instruction,
diverged from the one §3 calibrates the band on, and 37 of 40 attempts overshot
the band under it. [DEFECT-001](DEFECT-001.md) records it.

**2026-08-04** — the instruction repaired to the calibrated one, the same cell
exhausted the same budget in 80.4 minutes. **That** is this void.

The distinction matters because the two runs record the identical `void_reason`
string, and a reader who found only the first would have read a defect as a
finding.

## The numbers

Cell A (fluent × declarative), `gpt-oss:120b` at `think=medium`,
`temperature=0.7`, band 182–231 words, both raters judging each message alone:

| | 2026-08-03 (defective instruction) | 2026-08-04 (calibrated instruction) |
|---|---|---|
| attempts | 40 | 40 |
| mean words | 287.8 | **242.1** |
| median | 306.5 | 236.5 |
| range | 199–361 | **229–318** |
| inside the band | 3 / 40 | **2 / 40** |
| register accepted, both raters | 17 / 40 | 16 / 40 |
| **both filters** | **0 / 40** | **0 / 40** |

The repair moved the mean 46 words and moved nothing else. Band compliance went
from 3/40 to 2/40; joint acceptance stayed at zero.

## What the run actually found

**The minimum over 40 attempts is 229 words. The band's ceiling is 231.**

The fluent-declarative register, for this model, has a floor two words inside
the band. Getting into the band requires the very bottom of what the register
produces — and of the two messages that got there, **neither was judged fluent
prose by either rater.**

So the two filters are not independent, and not merely non-independent but
opposed: the messages short enough to be admitted are the ones that have stopped
being connected prose. [CALIBRATION-001](CALIBRATION-001.md) projected a joint
rate of 7.7% by multiplying the two marginals. The measured rate is 0%.

That is the finding, and [§8](PREREGISTRATION.md) named it in advance:

> **A register filter exhausts its budget** — the model cannot reliably produce
> one of the four registers at a fixed length, and the 2×2 is not buildable with
> this instruction set. That is a finding about instructions, and the successor
> is a different prompt rather than a different analysis.

It is sharper than §8 anticipated in one respect. The failure is not that the
register is unreliable at a fixed length; it is that *this* register and *this*
length are mutually exclusive. Fluent prose about this specification, from this
model, does not come in under 229 words.

## What was and was not seen

Voiding is a decision, and a decision made after seeing outcome data is not the
same decision. Precisely:

**Examined:** composed message texts, their word counts, their register
verdicts, the per-cell rejection counts.
**Not examined:** any probe answer, any divergence, any fidelity, any `Φ`, any
`β`, any effect. The sweep never began in either run. No `messages.json` was
written, because composition never completed. No hypothesis was computed.

Cells B, C and D were never reached by either run: cell A is composed first and
voids the run on exhaustion. They were measured **off-run**, after the void, by
[`floor_by_register.py`](floor_by_register.py) — instrument data that cannot
revive E-001c and exists so a successor knows what it is designing around:

| cell | register | floor | median | max | in band 182–231 |
|---|---|---|---|---|---|
| A | fluent · declarative | **232** | 238 | 308 | **0 / 12** |
| B | fluent · contrastive | 223 | 232 | 237 | 5 / 12 |
| C | terse · declarative | 184 | 210 | 232 | 11 / 12 |
| D | terse · contrastive | 189 | 212 | 225 | 12 / 12 |

**The floor belongs to the fluency axis.** Fluent cells put 5 of 24 messages
inside the band; terse cells put 23 of 24, Fisher exact `p = 1.2e-07`. Along the
other axis — declarative 11 of 24 against contrastive 17 of 24 — `p = 0.14`. The
fluency instruction moves the median length 24 words; the contrastiveness
instruction moves it 7.

So the 2×2 did not fail as a design. **Half of it did.** The terse row composes
inside the registered band without difficulty, and would have filled its cells.
The fluent row cannot, and cell A cannot even in principle: its floor of 232 sits
one word above the band's ceiling of 231, measured at 0 of 12 here and 0 of 40 in
the run.

## What survives for the successor

Not everything here failed, and a successor that rebuilt all of it would be
discarding what the two voids paid for.

- **The absolute register filter works.** It rejected 24 of 40 messages and
  accepted 16, on two providers with no shared point of failure. The
  forced-choice rating it replaced scored 64/64 on feasibility messages of which
  three in eight were lists — an estimator that could not fail. This one can and
  did.
- **The two-sided band works as a measurement** even though it failed as a
  constraint. It is what made the floor visible.
- **The instruction is now imported, not copied**, so the calibration and the
  run cannot diverge again ([DEFECT-001](DEFECT-001.md)).
- **The ceiling effect is characterised**: this model writes to the ceiling it
  is told and slightly past it, and the effect binds the fluent register and not
  the terse one ([CALIBRATION-001](CALIBRATION-001.md), Fisher p = 0.0345).

What the successor must change is the instruction set, as §8 says — and it now
has a specific target rather than a general one. A design that pins length and
varies register cannot use a band whose ceiling sits at the fluent register's
floor. The measurement above says where the band would have to go: **the fluent
row's floor is 223 and its median 234**, so a band centred near 240 admits both
fluent cells, and the terse row — floor 184, median 210, and demonstrably able to
hit a target — would be the arm asked to **pad up** rather than the fluent arm
asked to cut down. Which direction the padding runs is not cosmetic: asking a
terse register to reach a length is asking it to add content, and that
reintroduces the confound from the other side. A successor has to say what it
does about that before it collects.

**Neither choice is available to E-001c.** §7 forbids moving the band, the
amendment cap is spent on [AMENDMENT-001](AMENDMENT-001.md), and a band chosen
after measuring which band works is the acceptance criterion picked to fit the
data — the failure [E-001b's VOID](../E-001b-fluency-factorial/VOID.md) exists
to record. It requires a new registration under a new id.

## Amended 2026-08-04: §8's successor is the wrong successor

This document said above, following [§8](PREREGISTRATION.md), that the successor
is a different prompt. Measured afterwards, that is wrong, and the correction
belongs here rather than in a document nobody reading this void would find.

[`headroom_check.py`](headroom_check.py) took three of the fluent messages this
run rejected — they passed both blind register raters and failed only the band —
and three terse ones, all 221–233 words, and ran the draws this experiment never
reached. Observed agreement is **0.951 fluent against 0.941 terse**: a difference
of one third of one probe in 34, with 1 to 3 probes diverging per message where
E-002c's outcome-variation gate wants at least 3.

`MERIDIAN-34` is saturated at the length the fluent register requires. A
successor with a better prompt and this measure would compose successfully and
then measure nothing. See [Problem 15](../../theory/open-problems.md).

The correction is recorded and §8 is not edited, because a pre-registration
stands as written.

## The programme cost so far

E-001 confounded style with length. E-001b tried to fix it with a shared token
budget and voided on its parity gate. E-001c tried to fix it with a two-sided
word band and voided on its register filter. Three designs, one confound, no
result.

That is worth stating plainly rather than burying: the question *does fluency
buy understanding* has now consumed three experiments without being answered
once, and each void was caused by the same underlying fact from a different
angle — **this model's registers are not separable from their lengths.** A
fourth attempt that does not treat that as its central obstacle will void too.

---

*This document is licensed CC BY 4.0.*
