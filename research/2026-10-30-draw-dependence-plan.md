# Do real draws persist from one to the next? A plan, committed before its code

**2026-10-30 · prospective plan for an offline audit of draws already on disk,
not an experiment.** No model is called. The audit reads answers the repository
already holds, and the agent running it sees only aggregate statistics, never an
answer, a probe or a brief. This plan is committed before its code and before
any of those answers is read. Its predictions stay as written whatever the audit
finds.

## Why

The [candidate confirmation](2026-10-30-candidate-confirmation-results.md) found
that the candidate `F*` report breaks when a party's answers persist from one
draw to the next. With persistence `ρ = 0.3` its Fieller set covered as little
as 0.0825, and its gap interval reported a gap where there was none in 0.66–0.97
of null trials. That was a property of a simulated generator. Whether it matters
depends on whether real draws persist, and the repository's samplers assume they
do not: `seed_from` in the E-002c runner says that each draw is "a fresh call to
a stateless endpoint at temperature > 0". This audit tests that assumption on
the draws the repository already has.

## The draws

Every answer-draw sequence in the experiments' sample caches is used. Each one is
a single party's answers to one probe in one condition, kept in the order they
were drawn. The samplers make the draws as sequential calls with the same prompt
(`OllamaAgent.answer_samples`, `AnthropicAgent.answer_samples`), and the caches
keep that order.

| source | model | conditions | draws per sequence |
|---|---|---|---|
| E-001 | claude-opus-4-8 | 5 | 6 |
| E-001b | gpt-oss:120b; claude-opus-4-8 (`sender` only) | 4; 1 | 30; 8 |
| E-002 (void, at its elicitation gate) | gpt-oss:120b | 4 | 30 |
| E-002b | gpt-oss:120b | 19 | 16 |
| E-002c | gpt-oss:120b | 27 | 16 |
| E-004 | gpt-oss:120b, qwen3.5:35b, claude-opus-4-8 | 2 each | 16 |

These counts were read from the caches' condition names and row lengths before
this plan was written; no answer value was read.

**Out of scope:** the prediction and claim elicitations (conditions named
`pred-…` or `claim-…`). They are not the draws `F*` is computed from.

**Duplicates.** Some conditions were imported from an earlier experiment's
cache, truncated to their first draws. Such a sequence would be counted twice.
For the same condition name and probe, a sequence equal to or a prefix of
another is dropped, and the longer one is kept. The number dropped is reported.

**Families.** The audit is run separately for each model: gpt-oss:120b,
qwen3.5:35b and claude-opus-4-8. The two providers' samplers differ.
gpt-oss:120b and qwen3.5:35b run through Ollama at temperature 0.7 with no seed.
Claude runs at the provider's default and accepts no temperature.

## The test

A sequence of `n` answers with counts `c_k` has `R` adjacent repeats, the number
of positions `t` where answer `t + 1` equals answer `t`. If order carries no
information, every ordering of the answers is equally likely. That holds for
independent draws, and it is the assumption under test. Given the counts, `R`
then has exact expectation `E₀ = Σ_k c_k (c_k − 1) / n`. For a family the
statistic is

`T = Σ (R − E₀)`, over its sequences.

Persistence makes `T` positive. A sequence with one answer throughout has
`R = E₀`, so it adds nothing; such sequences are counted and reported as
uninformative.

- **The null distribution** comes from 10,000 joint permutations, each
  shuffling every sequence independently. The p-value is one-sided:
  `(1 + #{T* ≥ T}) / (1 + 10,000)`. The three families are tested with Holm's
  correction at 0.05.
- **The strength** is `ρ̂ = T / Σ (n − 1 − E₀)` over informative sequences. That
  is the excess of repeats as a share of the room for them. Under the persistence
  model of the confirmation, it estimates `ρ`, with a downward bias the
  calibration below takes into account.
- **An upper bound by simulation.** For `ρ` from 0 to 0.50 in steps of 0.01, 500
  synthetic datasets per step are drawn. Each keeps the family's sequences, their
  lengths and each sequence's observed shares, and draws persistent answers with
  that `ρ`. `ρ_upper` is the largest `ρ` at which the simulated `T` is at most
  the observed `T` in at least 5% of datasets. If that holds at 0.50, the bound
  is reported as `> 0.50`, that is, uninformative.
- **Power.** The share of the `ρ = 0.05`, `0.1` and `0.3` datasets whose `T`
  exceeds the 95th percentile of the observed permutation null.

**Secondary: drift.** A sequence could also change over its length without
persisting. For each sequence, `D = Σ_k (first-half count − second-half count)²`,
with the first half the first `⌊n/2⌋` draws. `T_drift = Σ D`, tested against the
same within-sequence permutations, one-sided.

**Diagnostic: rebuilt sequences.** A sequence rebuilt from a distribution comes
out grouped (`AAABBB`). The library warns of exactly this in
`Agent.answer_samples`, and it would look like persistence. For each source, the
share of informative sequences that are fully grouped (as many runs as distinct
answers) is compared with its expectation under permutation. A source with an
excess at `p < 0.001` is flagged, and the primary test is reported again without
it, beside the registered result.

Every quantity is also reported per source, as a description.

## Predictions, recorded before any code runs

- **P1.** gpt-oss:120b shows no persistence. Its Holm-adjusted p-value exceeds
  0.05 and its `ρ_upper` is below **0.10**.
- **P2.** qwen3.5:35b: Holm-adjusted p above 0.05, and `ρ_upper` below
  **0.30**.
- **P3.** claude-opus-4-8: Holm-adjusted p above 0.05, and `ρ_upper` below
  **0.30**.
- **P4.** No family shows drift at `p < 0.05`, unadjusted.

P1 and P4 are held with moderate confidence. P2 and P3 are held with low
confidence, because those families have few sequences. Many sequences may be
uninformative, since a model often gives one answer to a probe throughout, so
the bound may be too wide to fall below 0.30 even without persistence.

## What would change what

- **If no family rejects, and every `ρ_upper` is below 0.30:** the
  correlated-answer failure is a limit these models' draws do not show at the
  simulated strength. Problem 12's open part is then the failures with
  independent answers. A note is added to Problem 12.
- **If a family rejects:** that model's draws are not exchangeable within a
  probe. Any interval in the repository that resamples its draws as independent
  rests on an assumption the data contradict. The places that do so are listed
  for the owner. Whether any published interval is withdrawn is the owner's
  decision, not this audit's. Its `ρ̂` is reported as a count; what causes the
  persistence is not tested here.
- **If a bound is uninformative:** that is the result for that family, reported
  as such. It is not read as absence of persistence.

## Limits stated in advance

- One kind of dependence is tested: repetition of the immediately preceding
  answer. Drift is the secondary test. Other kinds can escape both.
- The simulated bound draws from each sequence's observed shares, which
  persistence itself distorts. The bound is approximate.
- Draws were collected for other purposes, under different conditions and
  dates. A family is a pool across them, not a designed sample.
- A void experiment's draws are used (E-002). It was voided at its elicitation
  gate, not for how it drew answers.

## Exposure

Drafted by `claude-opus-5-5`, which wrote the confirmation, offered the options
for this direction, and will score these predictions itself.
`claude-opus-4-8`, a subject of earlier experiments, is one of the families
audited; the audit reads that model's draws as data and asks it nothing. The
running agent sees aggregates only. See [EXPOSURE.md](../EXPOSURE.md).

---

*This document is licensed CC BY 4.0.*
