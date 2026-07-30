# E-004 — Does cross-model disagreement locate errors without a key?

**Status:** pre-registered, not yet run
**Registered:** 2026-07-30
**Tests:** the observation in
[journal/2026-07-30-cross-sender-disagreement.md](../../journal/2026-07-30-cross-sender-disagreement.md),
which is post-hoc and is not a finding
**Bears on:** [Problem 2](../../theory/open-problems.md) and the `R_panel`
construction in [definitions §4.1.1](../../theory/definitions.md)

> Committed before any data exists. If the results contradict what is written
> here, this file is not edited. The finding is added and this stands.

---

## 1. What is being tested, and why it is not yet a finding

Two models from different providers answered the same 34 probes from the same
source specification. They disagreed on **exactly** the four probes where one of
them was wrong — recall 4/4, precision 4/4, zero false positives across the
other thirty, **and no answer key was used to produce the disagreement list**.
Under random placement of four flags among thirty-four probes, `p = 2.2 × 10⁻⁵`.

That is an observation on data collected for another purpose, with a statistic
chosen after the pattern was visible. Under this repository's own rules it is a
hypothesis. E-004 is the test.

**Why it would matter.** A signal that locates contestable probes *without
consulting a key* is worth more to this programme than one that assumes the key
is right — `MERIDIAN-34`'s key was written by the person who wrote the rules,
and `M33`'s turned out to be undetermined by the source text
([SENSITIVITY-M33](../E-001b-fluency-factorial/SENSITIVITY-M33.md)). The
disagreement set **contained M33**. It also uses neither transfer fidelity nor
the key, which is what [Problem 2](../../theory/open-problems.md) asks for, and
it is the only evidence that a panel reference carries information at all.

## 2. The three defects of the observation, and how each is repaired

| defect | repair |
|---|---|
| **Post-hoc.** The statistic was chosen after seeing the pattern. | Stated here, before collection. |
| **One-sided.** `gpt-oss:120b` made zero errors, so what was shown is that disagreement finds *claude's* errors. | Three models, and a domain chosen so that **each model is wrong somewhere**. Gate G2 below refuses the run otherwise. |
| **Tiny.** One model pair, four errors, 34 probes. | Two probe measures, three models → three pairs, and a pre-specified minimum error count. |

## 3. Design

**Models.** `gpt-oss:120b` and `qwen3.5:35b` locally, `claude-opus-4-8` via API.
Three unordered pairs. All three answer both measures from the same source
specification, at `n = 16` draws, `think=medium`, `temperature = 0.7`.

**Probe measures.** `MERIDIAN-33` (M33 dropped), and a **second measure in a
different domain**, authored before any model answers it and adjudicated by a
party who did not write the rules — the requirement
[CONTRIBUTING](../../CONTRIBUTING.md) added after M33. Both measures are
committed before collection.

**The detector, fixed now.** For a pair `(X, Y)`, flag probe `π` iff
`mode X(π) ≠ mode Y(π)`. No key, no threshold, no tuning. A modal comparison
and nothing else — deliberately the crudest form of the thing, because the
observation was made with the crudest form and a fancier detector would be a
different hypothesis.

## 4. Hypotheses

**H1 — the detector beats chance.** Across all pairs and both measures, flagged
probes contain the union of the two models' errors at a rate exceeding the
hypergeometric null. *Primary.*

**H2 — precision is above the base rate.** A flagged probe is more likely to be
an error than an unflagged one. Stated separately from H1 because a detector
that flags everything has perfect recall and is useless.

**H3 — symmetry.** The detector locates errors of **both** members of a pair,
not only the weaker one. This is the defect the original observation could not
address, and it is the one most likely to fail.

**H4 — it finds contested probes, not only wrong ones.** Flagged probes that are
*not* errors against the key are enriched for probes an independent adjudicator
marks as textually undetermined. `M33` is the motivating case. *Exploratory and
labelled as such: the adjudication is a second judgment and inherits its own
error.*

**Recorded, not hypothesised:** per-pair agreement rates, whether the same
probes are flagged across pairs, and each model's accuracy.

## 5. Analysis plan

1. Per pair and measure: flag set, error set (union of both models' errors
   against the key), recall, precision.
2. **H1** by exact hypergeometric test per pair-measure, then Fisher-combined
   across the six cells. `α = 0.05`.
3. **H2** by comparing `P(error | flagged)` against `P(error | not flagged)`,
   with a bootstrap CI over probes.
4. **H3** by requiring, for each pair, that flagged probes include at least one
   error from *each* member. Reported per pair; a pair where one model made no
   errors is **excluded from H3 and said so**, not counted as a pass.
5. **H4** descriptively, with the adjudicator's labels collected **before** the
   flag sets are computed.
6. H1–H3 are one family and are Holm-corrected. No point estimate without a CI.

### 5.1 Gates

| gate | threshold | when |
|---|---|---|
| each model's accuracy | > 0.60 on each measure | before analysis |
| **each model wrong at least twice** on at least one measure | required | before analysis — **this is the run's reason for existing** |
| total errors across the design | ≥ 12 | before analysis |
| refusals | 0 | continuously |
| probe measure 2 adjudicated by a non-author | required | before collection |

**If the "each model wrong twice" gate fails the run is void**, not
reinterpreted. A design in which one model is never wrong reproduces exactly the
one-sidedness that makes the original observation unusable, and reporting it
anyway would be reporting the defect as the result.

### 5.2 Declared limitations

- Three models is enough to refute a strong claim and not enough to establish a
  general one.
- Two of the three are local open-weight models and may share training data.
  **Shared bias is the standing threat**: two models wrong in the same way agree,
  and the detector is silent exactly where it would be most needed. This is
  measured, not assumed — H3's per-pair breakdown is where it would show.
- The detector cannot distinguish "one model is wrong" from "the probe is
  contested". H4 is the attempt and it is exploratory.
- Nothing here establishes `R_panel` as a solution to Problem 2. It establishes
  at most that the ingredient carries signal.

## 6. Amendment policy

Permissible: fixing a defect in the metrics library, applied identically
everywhere. **Not permissible:** changing the detector, the models, the
hypotheses, the gates, or either probe measure after collection begins.

**Cap: one.**

## 7. What each outcome means

- **H1–H3 hold** — the programme has its first positive result, and it is a
  keyless instrument rather than a law. `R_panel` becomes constructible and
  Problem 2 gets an ingredient it did not have.
- **H1 holds, H3 fails** — the detector finds the weaker model's errors only.
  Still useful, and much weaker: it presupposes knowing which model is weaker,
  which is the thing you wanted to find out.
- **H1 fails** — the 2026-07-30 observation was four probes' worth of luck. That
  is the likeliest single outcome and the reason this file exists.

---

*This document is licensed CC BY 4.0.*
