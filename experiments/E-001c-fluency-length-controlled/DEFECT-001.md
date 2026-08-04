# DEFECT-001 — the band was calibrated on one instruction, and the run composed under another

**Found:** 2026-08-04, after the run of 2026-08-03 voided
**Status:** repaired; the void stands as a void, but not for the reason it records
**Data on disk when found:** one results file,
`results/E-001c-20260803T180306Z.json`, marked void. Forty rejected messages in
cell A with their text and register verdicts. **No draws.** The sweep never
started.

---

## What was wrong

`two_sided_output` — the function that writes the length instruction into every
cell prompt — existed **twice**, with different text:

`feasibility.py`:

> Write between 182 and 231 words. Not fewer, not more — a note outside that
> range is unusable to your colleague regardless of its quality. Output the note
> and nothing else: no preamble, no account of what you decided to include, no
> sign-off.

`runner.py`:

> Write between 182 and 231 words. Not fewer than 182, not more than 231.

[PREREGISTRATION §3](PREREGISTRATION.md) fixes the band at 182–231 and records
where the number came from: *"Calibrated on the feasibility messages, whose
realised range was 184–230 across both registers."*

A calibration transfers only if the instruction transfers with it. This one did
not. The band was measured against one prompt and enforced against another.

## Why that mattered — measured, not argued

Cell A, `gpt-oss:120b`, `think=medium`, `temperature=0.7`, band 182–231:

| instruction | in band | mean words |
|---|---|---|
| `feasibility.py`, verbatim | **4 / 4** | 218 |
| `runner.py`, as it ran | **3 / 40** | 288 |
| `runner.py` + the "nothing else" clause restored | **0 / 5** | 290 |

The third row is why this note does not blame the missing sentence about
preamble and sign-off. That was the first hypothesis, and executing it refuted
it: restoring only that clause left the mean at 290 words, unchanged. What binds
the model is the **justification** — *"a note outside that range is unusable to
your colleague regardless of its quality."* Without a reason the range is
treated as a suggestion.

That is worth stating plainly because it is a fact about instructions, which is
the thing E-001c exists to study: for this model, at this length, a constraint
with a stated consequence is obeyed and the same constraint stated twice as an
inequality is not.

## What the void is therefore not

The run recorded:

> register budget exhausted in cell A: 40 attempts produced 0 of 8 accepted
> messages. A register the model cannot reliably produce at a fixed length is a
> finding, not an obstacle to route around.

Two things are wrong with reading that as the finding
[§8](PREREGISTRATION.md) describes.

**It names the wrong axis.** Decomposing the same 40 attempts:

| filter | passed |
|---|---|
| register, both raters | 17 / 40 |
| band 182–231 | 3 / 40 |
| both | 0 / 40 |

The register filter behaved as registered — 17/40 sits inside the feasibility
CI `[0.245, 0.915]`. What emptied the budget was length.

**Its subject never occurred.** The claim would be that the model cannot
reliably produce this register at a fixed length. The repository's own
feasibility data says it can, four times in four, and the row above reproduces
that. The model was never asked the question the registration calibrated.

Recording this as the §8 outcome would have entered a defect into the record as
a result, and the claim it entered would have been contradicted by a file
already committed beside it.

## The repair

`runner.py` now imports `two_sided_output` from `feasibility.py`. One
definition, two callers, no copy to drift.

The file had already stated the principle, three hundred lines above the defect,
about a different object:

> The cells are imported from E-001b rather than copied, because the
> pre-registration says they are unchanged from it and **an import is the only
> form of "unchanged" that cannot drift.**

The cells were imported. The band instruction was pasted. The rule was written
and then not applied to the next thing that needed it.

**This is not an amendment.** The band stays 182–231; the cells, the model, the
raters, the probe measure and `λ` are untouched. What changes is that the runner
now sends the instruction the registration's calibration refers to.
[§7](PREREGISTRATION.md)'s cap is already spent on
[AMENDMENT-001](AMENDMENT-001.md) and nothing here draws on it.

One honest qualification: the pre-registration does not quote the instruction
verbatim. It fixes the band and names the calibration. The identification of
*which* instruction is registered therefore rests on §3's sentence pointing at
the feasibility messages, not on a literal string in the document. A future
registration should paste the prompt it means.

## What this does not fix

Compliance under the repaired instruction is **not** the 4/4 the first check
suggested. A wider draw at the registered band is recorded in
[CALIBRATION-001](CALIBRATION-001.md): the model lands slightly **above** the
stated ceiling, and the fluent cells may still exhaust their forty attempts.

If they do, under the calibrated instruction, that **is** the §8 finding and it
will be recorded as one. The point of this note is that the run of 2026-08-03
could not have established it.

## Why nothing caught it

The same shape as [AMENDMENT-001](AMENDMENT-001.md), in the same experiment,
three weeks apart: a document and a computation disagreeing with nothing between
them. AMENDMENT-001 closed with a task recorded and not performed —

> a check that a pre-registration's named probe measure matches the measure its
> runner loads

— and this is the second instance of exactly that class. `check_counts.py`
checks stated counts, `check_retracted.py` checks claims, `check_links.py`
checks pointers, and none of them knows that a prompt named in prose must match
the prompt a runner sends. See [Problem 13](../../theory/open-problems.md).

The dry run did not catch it either, because the dry run composes stub messages
built to sit inside the band. It exercises the path and cannot see the text.

## A second defect, found while repairing this one

`--messages-out` defaults to the live `messages.json`, and `--dry-run` wrote
**stub messages to it** — synthetic text on the path that holds the one artifact
composition cannot regenerate. E-001b's
[DEFECT-001](../E-001b-fluency-factorial/DEFECT-001.md) records what that costs:
draws with no record of which text produced them are not a damaged dataset, they
are not a dataset.

Repaired the same way the results file already handled it: a dry or smoke run
now stamps its messages file `-dryrun` / `-SMOKE` and cannot land on the live
path.

---

*This document is licensed CC BY 4.0.*
