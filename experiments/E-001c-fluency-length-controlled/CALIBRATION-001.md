# CALIBRATION-001 — the model writes to the ceiling it is told, and slightly past it

**Measured 2026-08-04**, after the run of 2026-08-03 voided and
[DEFECT-001](DEFECT-001.md) established that the void could not mean what it
said.

**This is instrument data. It is not E-001c's data** and no hypothesis is
touched by it, on the same footing as the feasibility messages
[PREREGISTRATION](PREREGISTRATION.md) discards before collection.

---

## What was asked

DEFECT-001 repaired a divergence between the instruction the band was calibrated
on and the instruction the runner sent. The obvious next question is whether the
repair is sufficient — whether the calibrated instruction, carrying the
**registered** band numbers, fills a fluent cell.

It does not, and the reason is more interesting than the defect was.

## What was measured

`gpt-oss:120b`, `think=medium`, `temperature=0.7`, one composition per draw,
realised word counts. Cell A is fluent × declarative; cell C is terse ×
declarative.

| cell | instruction | stated ceiling | n | mean | range | inside 182–231 |
|---|---|---|---|---|---|---|
| A | calibrated wording | **223** | 8 | 222.5 | 197–230 | **8 / 8** |
| A | calibrated wording | **231** | 11 | 244.3 | 208–326 | **2 / 11** |
| **C** | calibrated wording | **231** | 6 | 220.7 | 207–232 | **5 / 6** |
| A | runner's, pre-repair | 231 | 40 | 287.8 | 199–361 | 3 / 40 |
| A | runner's + "nothing else" restored | 231 | 5 | 290.4 | 243–338 | 0 / 5 |

Row 1 pools the four cell-A messages in [`feasibility.json`](feasibility.json)
with four composed on 2026-08-04. Row 4 is the void run's own rejection record.

Fisher exact, rows 1 and 2 — **p = 0.00071**. Rows 2 and 3 — **p = 0.0345**.

**Revision.** The first version of this file reported row 2 as `n = 8, 1/8`. A
background job's output was buffered and read as though it had died after three
draws; it had not, and its remaining draws are now included. The direction and
the conclusion are unchanged and the sample is larger. The number is corrected
here rather than left standing, and the correction is recorded rather than made
silently.

## What it says

**The stated ceiling is not a limit the model respects — it is a target it
approaches from below and overshoots.** Told 223, it wrote 197–230. Told 231,
it wrote 208–326. The eight-word difference in the instruction moved the mean by
twenty-six words, in the same direction and past the new number.

That is why the registered band cannot be hit by stating it. 182–231 is the
**acceptance** band. The runner also uses it as the **instruction**, and an
instruction of 231 produces cell-A messages around 244.

**And it binds one register and not the other.** At the same stated ceiling of
231, the terse cell complied 5 times in 6 while the fluent cell complied 2 in 11
(p = 0.0345). The terse instruction produces messages that sit *below* the
ceiling, so moving the ceiling does not move them; the fluent instruction
produces messages that sit *at* it, so it does. The pre-registration declared
this in advance as a limitation and did not draw the consequence:

> **The fluent register imposes a length of its own.** Feasibility Result 4:
> fluent messages land at 226 words with `sd = 1.5` against `sd = 14.5` for
> terse. The band admits both, but the fluent arm is not complying with the
> target so much as coinciding with it. If a future calibration moves the
> target, that coincidence may not survive.

The target moved by eight words between the calibration and the registration,
and the coincidence did not survive. §6.2 called it.

## What this predicts for the run of 2026-08-04

Cell A at 18% band compliance and 42.5% register acceptance — the latter
measured live, 17 of 40, on the void run — gives a joint acceptance of about
**7.7%**. Eight accepted messages would need roughly **104 attempts** against a
budget of **40**.

So the run in flight is expected to exhaust cell A. This projection is recorded
before its outcome is known, so that it can be wrong where anyone can see it.

### It was right about the outcome and wrong about the reason

The run exhausted cell A at 09:48:32Z on 2026-08-04 — 40 attempts, 0 of 8
accepted, 80.4 minutes. The projection above called that. Two of its three
components were wrong anyway, and the way they were wrong is the finding:

| quantity | projected | measured over 40 attempts |
|---|---|---|
| band compliance, cell A | 18% (from `n = 11`) | **5%** (2/40) |
| register acceptance | 42.5% | 40% (16/40) |
| joint | 7.7%, assuming independence | **0%** (0/40) |

Band compliance was overestimated more than threefold: `2/11` from a small
sample against `2/40` measured. And the joint rate is not the product, because
the two filters are not independent — **of the two messages that landed inside
the band, neither was judged fluent prose.**

The realised range makes the mechanism plain. Cell A over 40 attempts:
**229–318 words, mean 242.1, minimum 229.** The band's ceiling is 231. The
fluent-declarative register has a floor two words inside the band, so the only
way into the band is the very bottom of what the register produces — and at that
length it stops reading as connected prose to both raters.

That is not a length failure and not a register failure. It is the statement
that, for this model and this instruction set, **fluent prose and this length
are not simultaneously available.** Which is a claim about the confound E-001c
exists to break, arrived at from the wrong end.

## Where that leaves §3

[PREREGISTRATION §3](PREREGISTRATION.md) fixed the band this way:

> Calibrated on the feasibility messages, whose realised range was 184–230
> across both registers; a single target at ±10% admits 7 of 8 fluent and 6 of 8
> terse, and ±12% admits all sixteen.

Every one of those sixteen messages was composed under an instruction that said
**223**. The band was then widened to 182–231 so that all sixteen fell inside
it — a sound way to choose an acceptance criterion, and it would have been fine
if the criterion stayed a criterion. But the same numbers are then read back to
the model as the instruction, and the model moves when they move. The
calibration measured compliance with one ceiling and the run demands compliance
with another.

Nothing in the document is false. §3 says what it did. What it does not say is
that the band it derives will also be spoken aloud, and the two roles are only
safe to conflate for a model that treats a stated range as a boundary. This one
does not.

## What is NOT being done about it

**The band is not being changed.** [§7](PREREGISTRATION.md) forbids touching it,
the amendment cap is spent on [AMENDMENT-001](AMENDMENT-001.md), and a stated
ceiling of 223 chosen *after* measuring that 223 works is the acceptance
criterion being picked to fit the data — the precise failure
[E-001b's VOID](../E-001b-fluency-factorial/VOID.md) records.

So the run of 2026-08-04 states 182–231, as registered, and is expected to
exhaust cell A's forty attempts. If it does, that **is** the
[§8](PREREGISTRATION.md) outcome — *"the model cannot reliably produce one of
the four registers at a fixed length, and the 2×2 is not buildable with this
instruction set"* — and §8 already names the successor: a different prompt,
under a new registration, not a different analysis.

This file exists so that when that void arrives it is read correctly: the
instruction set fails, and the specific way it fails is that this model
negotiates with a number rather than obeying it.

## Limitations

- **Two of four cells.** A (fluent × declarative) and C (terse × declarative).
  The contrastive cells B and D are not measured; the effect is claimed on the
  fluency axis, where it was found, and not on the contrastiveness one.
- **n = 6 to 11 per arm**, unrandomised and unblinded, composed in blocks rather
  than interleaved. The arms ran on the same local model on consecutive days.
- The cell C arm is `n = 6`. `5/6` is not a precise compliance rate and the
  interval around it is wide; it establishes that the terse register behaves
  differently from the fluent one, not by how much.
- The second arm's later draws competed with the live run for the GPU. That
  changes latency, not text.
- One model. Nothing here generalises past `gpt-oss:120b` at `think=medium`.
- A twelve-draw arm was cut short at five once the live run began, because the
  run's own composition stage measures the same quantity against the real
  raters and the two were contending for one GPU.

---

*This document is licensed CC BY 4.0.*
