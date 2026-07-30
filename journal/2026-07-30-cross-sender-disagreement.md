# 2026-07-30 — Two models disagree exactly where one is wrong

**Status: an observation, not a finding.** Post-hoc, on data collected for
another purpose, with a statistic chosen after seeing it. It is written down
because it is the most interesting thing in the repository and because writing
it down is how it becomes testable rather than remembered fondly.

---

## What was found

An adversarial panel was asked whether a sender's own **self-consistency**
could stand in for its reliability — a way to weight probes without needing an
answer key. To test it, an agent recovered E-001's cache from git history and
reproduced every published number exactly.

The angle died immediately, and the way it died is the point.

**The E-001 sender's modal mass is 1.0000 on all 34 probes** — including all
four where it is wrong.

```
sender@claude-opus-4-8, n=6 draws
  modal mass: min 1.0000   mean 1.0000   over 34 probes
  errors vs key: M14, M19, M26, M33
  modal mass on those four: 1.0, 1.0, 1.0, 1.0
```

Weight variance is exactly zero, so a consistency-weighted fidelity is not
*approximately* `F*`, it is numerically identical to it. A confidently wrong
sender is maximally decisive, so the weighting rewards precisely what it was
meant to discount.

**But the reliability signal exists. It lives between agents, not inside one.**

```
probes with draws from both senders : 34 of 34
claude-opus-4-8 errors vs key       : M14, M19, M26, M33
gpt-oss:120b    errors vs key       : (none)
cross-sender disagreement           : M14, M19, M26, M33
```

Two models, different providers, different training, answering the same 34
probes from the same source specification. **They disagree on exactly the four
probes where one of them is wrong.** Recall 4/4, precision 4/4, zero false
positives across the other thirty — and **no answer key was used to produce
that list.**

Under a null in which four flags are placed at random among thirty-four probes,
landing all four on the four errors has probability `1/C(34,4) = 2.2 × 10⁻⁵`.

## Why it matters, if it survives

Three things, in ascending order of importance.

**It is a keyless error detector.** MERIDIAN-34's key was written by the same
person who wrote the rules, and M33's key turned out to be undetermined by the
source text ([SENSITIVITY-M33](../experiments/E-001b-fluency-factorial/SENSITIVITY-M33.md)).
A signal that locates contestable probes without consulting a key is worth more
to this programme than one that assumes the key is right — and note that the
disagreement set *contains M33*, the probe independently found to be defective.

**It bears on [Problem 2](../theory/open-problems.md).** That problem asks for a
non-circular measure of prior overlap, and every construction the
[research review](../theory/prior-art.md) attacked was found circular or fatally
instrumented. Cross-agent disagreement on a shared source is not obviously
circular in the same way: it does not use transfer fidelity, and it does not use
the probe measure's key.

**It is a candidate reference.** The panel's surviving proposal replaces "the
sender" with a *declared reference* against which fidelity is measured. A panel
of independent senders is one admissible construction, and this observation is
the first evidence that such a panel carries information.

## What it is not

- **Not pre-registered.** The data were collected to measure fluency effects.
  The statistic was chosen after the pattern was visible. Under this
  repository's own rules that makes it a hypothesis, and nothing more.
- **Not two-sided.** `gpt-oss:120b` made zero errors on this measure, so what
  was actually demonstrated is that disagreement locates *claude's* errors. A
  symmetric claim needs a case where each model is wrong somewhere.
- **Not replicated.** One domain, one model pair, four errors, 34 probes. Four
  is a small number to build a detector on.
- **Not independent of the key's own defects.** M33 is in both lists, and M33's
  key is known to be contestable. Whether the detector found an *error* or a
  *bad probe* is not separable here — and that ambiguity is itself informative,
  because the two are worth finding for different reasons.

## What happens next

It gets pre-registered and tested on data that does not yet exist, with the
hypothesis and the statistic committed first: **more model pairs, more domains,
and a design in which each model is wrong somewhere so the claim can be
symmetric.** If it survives that, it is a finding. Until then this file is the
whole of the claim, and it is filed in the journal rather than in `theory/`
because [that is where anecdotes belong](../CONTRIBUTING.md).

The uncomfortable symmetry: this programme has spent three days accumulating
void runs, and the most promising thing it has produced came out of an agent
being told to attack an idea, recovering deleted data to do it properly, and
finding something else on the way.

---

*This document is licensed CC BY 4.0.*
