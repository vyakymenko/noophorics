# Do real draws persist from one to the next? The audit's results

**2026-10-30 · results of the offline audit registered in
[the plan](2026-10-30-draw-dependence-plan.md)**, committed before the
[code](../tools/audit_draw_dependence.py), itself committed before it read an
answer. No model was called. The audit read the answers already in the
experiments' sample caches; the agent that ran it saw counts and statistics only.
Every number here is in the [saved record](draw-dependence.json) or computed from
it, and the tables below are generated from the record and checked against it.
**All four predictions held. None of the three models' draws shows persistence
on the registered test, and each model's simulated upper bound is below the 0.3
that broke the candidate report.** The bound is tight only for gpt-oss:120b,
and for claude-opus-4-8 the test itself was narrow; both are read below.

## The run

The registered run was made at commit `1f596b8`. Of 2,120 answer-draw sequences
read, 297 were dropped as imported copies of a longer or equal sequence, and
1,823 were kept. Most of them are uninformative: a model gave one answer
throughout in 982 of gpt-oss:120b's 1,519 sequences, 53 of qwen3.5:35b's 63 and
214 of claude-opus-4-8's 241. Such a sequence has the same repeats in every
order, so, given its counts, it says nothing about order. The test rests on the
rest: 537, 10 and 27 sequences (Table 2).

## The predictions

- **P1 held.** gpt-oss:120b has 27.3 *fewer* adjacent repeats than its
  sequences' counts imply. Its `ρ̂` is −0.0099 and its p-value 0.84. Its
  simulated bound is 0.00, the floor of the grid. At `ρ = 0.01`, 0.034 of
  simulated datasets had an excess of repeats as low as observed, against the
  0.05 the bound requires. That is 17 of 500 datasets, with a Wilson 95% interval
  of 0.021–0.054, so the bound is at the edge of the simulation's precision. At
  `ρ = 0.02` the share is 0.010. Its power against `ρ = 0.05` is 0.988.
- **P2 held.** qwen3.5:35b: `ρ̂` +0.054, Holm-adjusted p 0.49, bound 0.23. It
  rests on 10 sequences. Its power against `ρ = 0.1` is 0.296 at the unadjusted
  0.05 level, as registered; at the Holm threshold that decided it, power is
  lower.
- **P3 held on the registered criterion, narrowly.** claude-opus-4-8: `ρ̂`
  +0.090, raw p **0.033**, Holm-adjusted p 0.0999, bound 0.24. It is the only
  registered p-value below 0.05; E-004 alone, which the plan registers only as
  a description, has 0.043. The plan corrects across the three models, and the
  correction takes it above 0.05. The test rests on 27 sequences. Its power
  against `ρ = 0.1` is 0.552 at the unadjusted 0.05 level, as registered, and
  lower at the Holm threshold that decided it. These draws neither show
  persistence on the registered test nor rule out persistence of 0.24 or less.
  They are read as "not shown", not as "absent".
- **P4 held.** No model shows drift at `p < 0.05`: p 0.94 (gpt-oss:120b), 0.46
  (qwen3.5:35b) and 0.15 (claude-opus-4-8). The drift test's power was not
  computed.

**The rebuilt-sequence diagnostic flagged no source.** Its smallest p-value was
0.20: claude-opus-4-8 in E-004, with 2 fully grouped sequences against 0.85
expected (Table 3). No sensitivity analysis was therefore triggered.

By source, which the plan registers only as a description: claude-opus-4-8's
E-004 sequences hold 82% of its room for repeats and +8.25 of its +9.58 excess.
Its `ρ̂` is +0.095 there and +0.069 in E-001, with uncorrected p-values of 0.043
and 0.34. Its E-001b sequences are all uninformative (Table 3). Nothing here
tests why.

## What this does and does not change

By the plan's rule: **no model rejects, and every bound is below 0.30, so the
candidate report's correlated-answer failure is a limit these draws do not show
at the simulated strength.** A note is added to Problem 12. What is ruled out
differs by model:

- **gpt-oss:120b**, which made 26,208 of the 29,326 draws kept after removing
  duplicates: persistence of 0.01 or more is ruled out by the registered rule.
  The share at 0.01 is within the simulation's error of 0.05, and the share at
  0.02 is not.
- **qwen3.5:35b**: persistence of 0.24 or more is ruled out on the grid.
- **claude-opus-4-8**: persistence of 0.25 or more is ruled out on the grid.

For qwen3.5:35b and claude-opus-4-8, smaller persistence is not ruled out, and
their bounds rest on 10 and 27 sequences.

On this test, the assumption written in the gpt-oss:120b runners, that each draw
is "a fresh call to a stateless endpoint at temperature > 0", is not contradicted
for any of the three models. For claude-opus-4-8 that holds only after the
correction (raw p 0.033). Persistence of this kind is bounded tightly only for
gpt-oss:120b.

**Nothing about the candidate changes.** It had already failed its confirmation
with independent answers. What this audit removes is a reason to expect it to
fail worse on gpt-oss:120b's real draws. For qwen3.5:35b and claude-opus-4-8 it
rules out only persistence as strong as the 0.3 simulated. Weaker persistence is
compatible with their draws, and the candidate was not simulated under it.
Problem 12's open part is the failures with independent answers: the gap's
interval at five options, and power against a receiver who moved away.

## Choices fixed in the code before the registered run

The code's docstring records the details the plan left open:

- answers are compared as values;
- a model written `a/b` in a condition name is `b` (E-001's
  `claude-opus-4-8/claude-opus-4-8`);
- permutations run in 20 seeded chunks, so the result does not depend on the
  number of processes;
- how the null's 95th percentile is read.

Two more choices were made in the code before the run but not written in its
docstring until the review; neither changes a result here:

- a duplicate is matched by the full cache key, model and fingerprint included;
- the rebuilt-sequence diagnostic is computed per model and source, not per
  source.

No run was made on real draws before the code was committed. Timing was taken on
a synthetic tree.

After the run, a same-model review led to changes in the code's checks, not its
computation. `--check` now compares every observed field and the numbers quoted
in prose. `--check-full` reruns the seeded audit. Three tests were added. The
rerun reproduces the registered record byte for byte.

## Limits

The plan's limits stand. One kind of dependence is tested, with drift as the
secondary test. The simulated bound draws from each sequence's observed shares,
so it is approximate. The draws were collected for other purposes and are pooled
per model. E-002's draws are used although the experiment is void, because it was
voided at its elicitation gate.

- **Most sequences carry no information about order.** The bounds come from
  537, 10 and 27 sequences, not from 1,823.
- **Each grid point is one seeded estimate from 500 datasets.** Near the 5% cut,
  a share has a standard error of about 0.01. qwen3.5:35b's shares stay within
  that noise of 0.05 up to 0.27, and claude-opus-4-8's up to 0.26. Their bounds
  of 0.23 and 0.24 are resolved only to within a few grid steps. From 0.28 up, every
  share for both is clearly below 0.05, so P1–P3 do not depend on this.
- **A bound by test inversion is tighter where the observed count falls low.**
  gpt-oss:120b's excess sat at the 18th percentile of the datasets simulated with
  no persistence (0.184 at or below it). The bound of 0.00 reflects that as well
  as the volume of its draws.
- **The bound is for one persistence common to all of a model's sequences.**
  Persistence confined to some sources or conditions is bounded only on average.
- **claude-opus-4-8's draws come from three experiments.** E-001 used 6 draws
  per sequence, E-001b 8 and E-004 16, all through the same `AnthropicAgent`
  sampler. E-001b's sequences are all uninformative, and 18 of the 27
  informative ones are E-004's. The pool is not a designed sample.

<!-- tables:start -->
**Table 1 — the predictions, scored as registered.**

| prediction | held? | the numbers it turned on |
|---|---|---|
| P1: gpt-oss:120b: Holm p > 0.05 and `ρ_upper` < 0.10 | **yes** | Holm p 0.8377, `ρ_upper` 0.00 |
| P2: qwen3.5:35b: Holm p > 0.05 and `ρ_upper` < 0.30 | **yes** | Holm p 0.4902, `ρ_upper` 0.23 |
| P3: claude-opus-4-8: Holm p > 0.05 and `ρ_upper` < 0.30 | **yes** | Holm p 0.0999, `ρ_upper` 0.24 |
| P4: no family drifts at p < 0.05 | **yes** | drift p claude-opus-4-8 0.1541, gpt-oss:120b 0.9413, qwen3.5:35b 0.4557 |

**Table 2 — each model's draws.** Sequences after removing duplicates; those with more than one answer (informative); the excess of adjacent repeats over their expectation given each sequence's counts; `ρ̂`; the one-sided permutation p-value, raw and Holm-adjusted; the simulated upper bound on persistence; and the power against `ρ` = 0.05, 0.1 and 0.3.

| model | sequences | informative | draws | excess repeats | `ρ̂` | p | Holm p | `ρ_upper` | power 0.05 | power 0.1 | power 0.3 | drift p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-opus-4-8 | 241 | 27 | 2110 | +9.58 | +0.0899 | 0.0333 | 0.0999 | 0.24 | 0.240 | 0.552 | 0.998 | 0.1541 |
| gpt-oss:120b | 1519 | 537 | 26208 | -27.26 | -0.0099 | 0.8377 | 0.8377 | 0.00 | 0.988 | 1.000 | 1.000 | 0.9413 |
| qwen3.5:35b | 63 | 10 | 1008 | +2.75 | +0.0542 | 0.2451 | 0.4902 | 0.23 | 0.160 | 0.296 | 0.914 | 0.4557 |

**Table 3 — by source, as a description.** The same quantities for each experiment's cache, and the diagnostic for sequences rebuilt from a distribution: fully grouped informative sequences against their mean under permutation.

| model | source | sequences | informative | excess repeats | `ρ̂` | p | drift p | grouped | grouped, null mean | grouped p |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-opus-4-8 | E-001 | 161 | 9 | +1.33 | +0.0690 | 0.3367 | 0.1765 | 2 | 2.25 | 0.7031 |
| claude-opus-4-8 | E-001b | 17 | 0 | +0.00 | – | – | – | – | – | – |
| claude-opus-4-8 | E-004 | 63 | 18 | +8.25 | +0.0946 | 0.0430 | 0.2265 | 2 | 0.85 | 0.2046 |
| gpt-oss:120b | E-001b | 103 | 35 | -13.53 | -0.0335 | 0.8987 | 0.8393 | 0 | 0.36 | 1.0000 |
| gpt-oss:120b | E-002 | 33 | 1 | +1.40 | +0.2593 | 0.1925 | 1.0000 | 0 | 0.00 | 1.0000 |
| gpt-oss:120b | E-002b | 528 | 177 | -18.75 | -0.0246 | 0.9056 | 0.8162 | 6 | 8.29 | 0.8481 |
| gpt-oss:120b | E-002c | 792 | 319 | +3.62 | +0.0023 | 0.4422 | 0.7888 | 11 | 12.06 | 0.6739 |
| gpt-oss:120b | E-004 | 63 | 5 | +0.00 | +0.0000 | 0.5931 | 1.0000 | 0 | 0.39 | 1.0000 |
| qwen3.5:35b | E-004 | 63 | 10 | +2.75 | +0.0542 | 0.2451 | 0.4557 | 0 | 0.30 | 1.0000 |

Sequences read: 2120; dropped as duplicates of a longer or equal sequence: 297; kept: 1823.
<!-- tables:end -->

## Reproduce

```bash
python3 tools/test_audit_draw_dependence.py
python3 tools/audit_draw_dependence.py --out research/draw-dependence.json
python3 tools/audit_draw_dependence.py --check
python3 tools/audit_draw_dependence.py --check-full
```

The second command takes about seven seconds on sixteen processes and rewrites
the record. The third recomputes the observed quantities from the caches,
rescores the predictions, checks these tables against the record and checks the
numbers this note, Problem 12 and the research index quote from it. The fourth
reruns the seeded audit in memory and compares it with the saved record byte
for byte, which covers the p-values and bounds.

**Exposure.** `claude-opus-5-5` wrote the plan, its predictions, the code and
this report, and scored its own predictions. The scoring is `score()` in the
code, committed before the run. claude-opus-4-8, one of the audited models, is
an earlier model in the same family as the author. See
[EXPOSURE.md](../EXPOSURE.md).

---

*Prose: CC BY 4.0. Code: Apache-2.0.*
