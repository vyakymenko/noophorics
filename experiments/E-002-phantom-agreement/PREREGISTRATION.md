# E-002 — The first measurement of Φ, per probe

**Status:** pre-registered, not yet run
**Registered:** 2026-07-29
**Attacks:** [PRINCIPIA §5](../../PRINCIPIA.md), falsification criterion 2
**Probe measure:** `MERIDIAN-33@256672ea3852` (MERIDIAN-34 with
[M33 dropped](../E-001b-fluency-factorial/SENSITIVITY-M33.md))

> Committed before any data exists. If the results contradict what is written
> here, this file is not edited — the finding is added and this stands.

---

## 1. Why this experiment, and why now

**This repository has never measured Φ.** Zero times. E-001 voided at message
generation; E-001b voided on cost parity before a single probe was answered.
The quantity the site calls "the central pathology of the field" is, in our own
record, an assertion.

The [prior-art audit](../../theory/prior-art.md) narrowed what is ours to one
thing: *no measurement of this gap exists where sender and receiver are both
language models.* Everything else about Φ was measured in humans, some of it
thirty-six years ago, with instruments better than ours.

So this experiment does two things at once. It measures Φ here for the first
time, and it does so with the **instrument that measured it in humans**, rather
than the weaker one our own definitions specified.

## 2. The instrument, and why it changes

[definitions §5](../../theory/definitions.md#5-phantom-agreement) elicits **one
global number** per party: *"over probes of this kind, what fraction of your
decisions would match the other party's?"* That yields a mean difference — a
**bias** term — and nothing else.

Keysar & Henly (2002) did not do that. Their speakers made a **per-trial**
forced choice about what the listener had understood, and 72%/61% are
aggregates the experimenters computed afterwards. Because the judgment is
per-trial, each prediction can be paired with *that trial's* outcome, which
yields three quantities instead of one — and their headline result is the third:

- **bias** — mean claimed minus mean observed;
- **resolution** — whether a party can tell *which* probes diverged;
- **conditional asymmetry** — `P(claims match | actually diverged)` against
  `P(claims diverged | actually matched)`, which in their data was 46% against
  12%, present in 80% of individual speakers.

E-002 elicits per probe. This is not a refinement, it is the repair of a
regression: our global elicitation cannot compute resolution or asymmetry at
all, and [falsification criterion 2](../../PRINCIPIA.md) was invalid precisely
because it treated a bias term as the whole of calibration.

## 3. Design

Single condition. **No style manipulation** — that is E-001c's job, and mixing
them is what made E-001 uninterpretable.

```
sender    : gpt-oss:120b + MERIDIAN source spec
PRIOR     : gpt-oss:120b + nothing              (the pre-transfer receiver)
post_i    : gpt-oss:120b + brief_i              (i = 1..k)
CEILING   : gpt-oss:120b + the source spec      (upper reference)
```

`k = 8` briefs, composed by the sender under one neutral instruction.
`n = 30` draws per probe per condition. 33 probes.

**Elicitation, per probe, from both parties, after answering and before seeing
anything:**

- sender: *"Your colleague has only the brief you wrote. On this case, will
  their verdict be the same as yours?"* → yes / no
- receiver: *"On this case, will your verdict be the same as the verdict of the
  person who briefed you?"* → yes / no

Both are binary per-probe judgments, elicited `n_c = 5` times each and averaged
to a per-probe claim in `[0,1]`. Neither party is told the other's answers, the
key, or any outcome.

`sender`, `PRIOR` and `CEILING` draws at n=30 **already exist** in the tracked
sample cache from the voided E-001b run and are reused; they do not depend on
any brief. Only the `post_i` conditions and all elicitations are new. Reuse is
recorded rather than hidden: the cache is committed and the conditions are
keyed by model.

## 4. Hypotheses

Directions committed now.

**H1 — bias is positive.** `Φ = mean(claim) − mean(observed) > 0`. Both parties
overestimate how much transferred.

**H2 — resolution is above chance.** The per-probe association between claims
and outcomes exceeds zero. *This is the quantity the old instrument could not
produce, and the one that decides whether Φ ≈ 0 would mean anything.*

**H3 — the asymmetry replicates.** `P(claims match | actually diverged)` >
`P(claims diverged | actually matched)`. This is Keysar & Henly's headline
ported to language models.

**H4 — the sender is worse calibrated than the receiver.** `Φ_sender >
Φ_receiver`. In humans the bias attaches to *producing* the message: Keysar &
Henly's Experiment 2 overhearers, who knew the intent but did not speak, showed
no bias, and Newton's listeners were well calibrated. If H4 fails while H1
holds, the mechanism does not port, and that is a finding about machines rather
than a failure of the experiment.

**Recorded, not hypothesised:** `F*`, the decomposition, realised cost, and the
association between per-brief `Φ` and per-brief `F*`.

## 5. Analysis plan

Fixed before collection.

1. Shared floor by permutation null on `sender` vs `PRIOR`, 300 permutations,
   seeded. Admissibility gate `D_prior − floor > ε = 0.02`.
2. Per probe and per brief: observed match = `1(mode sender = mode receiver)`;
   claimed match = mean of that party's `n_c` binary judgments.
3. **Bias** `Φ` = mean claimed − mean observed, reported for each party
   separately and pooled, with a bootstrap 95% CI over **briefs** (the
   exchangeable unit is the brief, not the probe — E-001's error).
4. **Resolution** = point-biserial correlation between per-probe claim and
   per-probe observed match, within party, pooled across briefs with a
   brief-level bootstrap CI. Reported alongside Goodman–Kruskal γ, since the
   metacomprehension literature reports γ and comparability matters.
5. **Asymmetry** = the two conditional rates in H3, with a permutation test
   over briefs, 10 000 permutations, two-sided.
6. `α = 0.05`. H1–H4 are one family and are **Holm-corrected**, because they
   are four claims about one instrument on one dataset.
7. Every effect reported with a bootstrap CI. No point estimate without one.

### 5.1 Gates — the run is void if any fails

| gate | threshold | why |
|---|---|---|
| sender accuracy vs key | > 0.90 | a sender that cannot decide the domain is not transferring it |
| sender error count | ≤ 2 of 33 | a mean gate cannot protect a statistic whose effect concentrates (E-001) |
| `D_prior − floor` | > 0.02 | admissibility |
| CEILING fidelity | > 0.70 | the probe measure must be answerable from the spec |
| elicitation degeneracy | claims not constant across probes | a party that says "yes" to everything has zero resolution *by construction*, and H2 would be untestable rather than false |
| refusals | 0 | a refusal is missing data and voids the run |

**Gates are evaluated at the earliest point their inputs exist**, per
[E-001b's postmortem](../E-001b-fluency-factorial/VOID.md). The elicitation
degeneracy gate fires after the first brief, not after the sweep.

### 5.2 Declared limitations

- **One model in both roles.** Cross-provider Φ is E-003. A single model
  predicting its own copy is the *easiest* case for calibration and the hardest
  for H4, and any positive H1 here is therefore conservative.
- **One domain**, and [Problem 6](../../theory/open-problems.md) is unsolved.
- **Not a replication of Keysar & Henly.** Their participants were human, their
  stimulus was sentence ambiguity, their forced choice was between two
  paraphrases. This is the same *instrument logic* on a different substrate, and
  a difference in result is not evidence against them.
- The elicitation is itself a language-model self-report and inherits whatever
  pathologies those have. That is the object of study, not a confound to remove.

## 6. Amendment policy

Permissible without a new registration, instrument only: fixing a defect in the
metrics library (applied identically everywhere), and reducing `k` for budget.
**Not permissible:** changing `n`, `n_c`, the hypotheses, the gates, the
analysis plan, the elicitation wording, or the model.

**Cap: one amendment.** E-001 amended three times and E-001b twice-plus; the
budget shrinks each time the programme demonstrates it cannot hold still.

## 7. What each outcome means

- **H1 and H2 both hold** — Φ exists between language models and the parties
  have *some* insight into where it lives. The first result the programme
  actually owns.
- **H1 holds, H2 fails** — the parties are systematically overconfident and
  cannot localise it at all. Worse than H1 alone, and the strongest possible
  case for the field.
- **H1 fails, H2 holds** — well calibrated on average and discriminating. This
  is the corrected falsification criterion firing, and the programme loses its
  motivating phenomenon in this setting.
- **Both fail** — the instrument produced nothing. Report as an instrument
  result, not as evidence about the world.
- **H4 fails** — the human mechanism does not port. Interesting, and it would
  make Φ a different animal in machines than in people.

---

*This document is licensed CC BY 4.0.*
