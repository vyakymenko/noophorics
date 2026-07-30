# E-002b instrument notes

**Written before registration**, from the wreckage of
[E-002](../E-002-phantom-agreement/VOID.md). Two design corrections, one of
which is a correction to a *gate*, and gates are the part a pre-registration
cannot fix afterwards.

---

## 1. The gate was on the wrong quantity

E-002 voided on **elicitation degeneracy**: every per-probe claim came back
identical, so resolution was zero by construction and H2 was untestable.

That gate was wrong in principle, and it is worth being precise about why,
because it very nearly discarded the best result the design could have
produced.

Consider the four cases:

| claims | outcomes | what it is |
|---|---|---|
| vary | vary | the ordinary case — bias and resolution both measurable |
| vary | **constant** | nothing to predict; **void** |
| **constant** | vary | *maximal phantom agreement with zero resolution* |
| constant | constant | void, twice over |

The third row is not a degeneracy. A party that says "we will agree" on every
case while the parties actually diverge on a third of them is exhibiting
**exactly** the pathology this programme exists to measure, at its most extreme.
Voiding on it would be discarding the headline.

E-002 escaped this only by accident: its outcomes were *also* constant (0 of 33
probes diverged), so the run was void on row four regardless of which gate
fired. The gate was right by luck.

**E-002b gates on the outcome, per rung**: a rung whose probes all fall the same
way is uninformative and is dropped. Constant *claims* are recorded as a
finding, not as a fault.

## 2. The elicitation needs no default answer

E-002 asked *"will your colleague reach the same verdict as you on this case?"*
— a yes/no with an obvious answer, taken 330 times out of 330.

Keysar & Henly's speakers were shown two paraphrases and had to say **which one**
the listener took. There is no "everything is fine" response available; the
speaker must commit to a reading, and the overconfidence shows up in *which*
reading it commits to. The 72% is an aggregate the experimenters computed
afterwards.

**E-002b elicits a verdict, not an assessment.** The sender is shown the brief
it wrote and asked what verdict its colleague will reach **from that brief
alone**, choosing among the probe's own options. The receiver is asked what
verdict the person who briefed them would reach. Agreement is scored afterwards,
by comparison.

The sender may still predict its own verdict every time. That is now a
*substantive* prediction that can be wrong — and at the rungs below, it would be
wrong on a third of the probes. Under the corrected gate that outcome is the
finding rather than the void.

## 3. The budget ladder exists, and it has a plateau

Measured before registration, `gpt-oss:120b` both roles, n=8, MERIDIAN-33:

| brief budget | realised | sender–receiver agreement | probes diverged |
|---|---|---|---|
| none (`PRIOR`) | 0 words | 0.5152 | — |
| ~30 words | 35 words | **0.6667** | 11 / 33 |
| ~70 words | 84 words | **0.6667** | 11 / 33 |
| ~150 words | 193 words | **0.9394** | 2 / 33 |
| ~200 words ([E-002](../E-002-phantom-agreement/VOID.md)) | 180–260 words | **1.0000** | 0 / 33 |

Two things follow.

**The channel constraint works.** At 35 words the transfer is genuinely partial
and eleven probes diverge — the regime where `Φ` can exist at all. This is the
repair [Problem 11](../../theory/open-problems.md) calls for: constrain the
channel, not the frame. Hardening the probe measure after seeing it was too easy
would be tuning the frame until the result appears.

**The curve is not smooth.** Going from 35 to 84 words — nearly two and a half
times the budget — bought **nothing**. Agreement sat at 0.6667 both times, and
then rose steeply to 0.9394 by 193 words. The whole transition is compressed
between 84 and ~193 words, so a ladder spaced evenly from zero would spend most
of its rungs on the plateau and none where the interesting change happens.

Whether the same eleven probes diverged at both budgets is **not known** — the
ladder probe recorded counts, not identities. That is a defect in a throwaway
script and it is stated rather than glossed: identical counts are consistent
with identical probes and with two disjoint sets of eleven, and those mean
different things. E-002b records probe identities.

## 4. Word-target compliance degrades with the target, within a prompt

Recorded after composition, before any outcome data. Brief lengths are the
treatment, not the outcome; they were fixed and committed when the run started.

| source | target | realised mean | overshoot | range |
|---|---|---|---|---|
| E-002b | 30 | 30.0 | **+0.0%** | 27–34 |
| E-002b | 70 | 73.8 | +5.4% | 69–78 |
| E-002b | 110 | 118.8 | +8.0% | 109–128 |
| E-002b | 150 | 176.0 | **+17.3%** | 160–198 |
| [E-001c](../E-001c-fluency-length-controlled/FEASIBILITY.md) | 203 | 214.6 | +5.7% | 183–243 |
| E-001c | 220 | 238.2 | +8.3% | 207–269 |

Within the single E-002b prompt the overshoot is monotone in the target: the
model hits a 30-word band exactly and misses a 150-word one by 17%. Short
instructions are obeyed; long ones drift.

**The pooled trend is not a real quantity, and the temptation to report it
should be resisted.** Fitting a line through all six rows gives +3.6 percentage
points of overshoot per 100 words of target, and that number is an artifact:
E-001c's 203-word target produced *less* overshoot (5.7%) than E-002b's 150-word
one (17.3%), which is the opposite order. The two used different prompts —
E-001c's four styled cell prompts against E-002b's single neutral one — and
compliance is a property of the prompt as much as of the target. Six points
across two instruments do not make a curve.

What survives is narrower and still useful: **a budget-controlled design must
measure realised length rather than assume it, and must recalibrate whenever the
prompt changes.** E-001b was voided for assuming exactly this
([VOID](../E-001b-fluency-factorial/VOID.md)).

The consequence for E-002b specifically: the top rung asked for 150 words and
realised 160–198, which lands close to the region where the
[ladder](ladder.json) showed transfer approaching saturation (193 words →
0.9394 agreement, 2 of 33 diverged). That rung is therefore at more risk of
failing the outcome-variation gate than the design intended. The gate drops it
if so, the ladder survives on three rungs, and this paragraph is here so that
outcome reads as anticipated rather than as an excuse.

---

*This document is licensed CC BY 4.0.*
