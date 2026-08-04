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

Cell A (fluent × declarative), `gpt-oss:120b`, `think=medium`,
`temperature=0.7`, one composition per draw, realised word counts:

| instruction | stated ceiling | n | mean | range | inside 182–231 |
|---|---|---|---|---|---|
| calibrated wording | **223** | 8 | 222.5 | 197–230 | **8 / 8** |
| calibrated wording | **231** | 8 | 248.8 | 208–326 | **1 / 8** |
| runner's, pre-repair | 231 | 40 | 287.8 | 199–361 | 3 / 40 |
| runner's + "nothing else" restored | 231 | 5 | 290.4 | 243–338 | 0 / 5 |

Row 1 pools the four cell-A messages in
[`feasibility.json`](feasibility.json) with four composed on 2026-08-04. Row 3
is the void run's own rejection record. Fisher exact on rows 1 and 2:
**p = 0.0014**.

## What it says

**The stated ceiling is not a limit the model respects — it is a target it
approaches from below and overshoots.** Told 223, it wrote 197–230. Told 231,
it wrote 208–326. The eight-word difference in the instruction moved the mean by
twenty-six words, in the same direction and past the new number.

That is why the registered band cannot be hit by stating it. 182–231 is the
**acceptance** band. The runner also uses it as the **instruction**, and an
instruction of 231 produces messages around 249.

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

- **Cell A only.** The terse cells are not measured here; feasibility put them
  at 184–204, well below the ceiling, so the effect may not bind there at all.
- **n = 8 per arm**, unrandomised and unblinded, composed in blocks rather than
  interleaved. The two arms ran on the same local model on consecutive days.
- The second arm's later draws competed with the live run for the GPU. That
  changes latency, not text.
- One model. Nothing here generalises past `gpt-oss:120b` at `think=medium`.
- A twelve-draw arm was cut short at five once the live run began, because the
  run's own composition stage measures the same quantity against the real
  raters and the two were contending for one GPU.

---

*This document is licensed CC BY 4.0.*
