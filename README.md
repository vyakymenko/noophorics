# Noophorics

**The quantitative science of transferring understanding across minds that do
not share a substrate.**

[noophorics.org](https://noophorics.org) · founded 2026 by
[Valentyn Yakymenko](https://github.com/vyakymenko) ·
[authorship and contributor roles](AUTHORS.md)

Two minds are given the same problem. One explains it to the other. Both agree
the explanation landed.

Nobody measures what was lost.

Noophorics is the attempt to measure it — with units, laws, falsifiable
predictions, and experiments that can fail.

---

## The idea in one paragraph

Shannon's information theory measures how much uncertainty a message removes,
**assuming sender and receiver share a codebook**. Between a human and a model,
or between two models, or between a session and its own compacted summary, the
codebooks differ and are partially reconstructed on the fly. Adjacent
literatures address parts of this — decision-preserving compression, semantic
rate–distortion for heterogeneous agents, goal-oriented semantic communication.
What we have not found elsewhere is one instrument carrying fidelity, cost,
**and the calibration of both parties** together. Noophorics builds it by
replacing *symbol recovery* with *behavioral convergence*: **B understood what A
understood, over a domain, to the extent that B would make the same decisions
A would make.** That single move makes understanding measurable, comparable
across substrates, and falsifiable.

---

## Why now

Every science begins with an instrument. The telescope made astronomy; the
microscope made microbiology.

The science of communication never got its instrument, because it could never
open the receiver. You can ask a listener what they understood, but the report
is not the state, and you cannot run ten thousand controlled trials on one
human mind.

Language models change this. **For the first time the receiver is
instrumentable** — resample its dispositions, probe arbitrary decisions, ablate
its input, repeat at a cost measured in cents. And the sender too. That is the
instrument. This repository is what we are building with it.

---

## Core quantities

Formal definitions in [`theory/definitions.md`](theory/definitions.md);
reference implementation in [`metrics/`](metrics/).

| Symbol | Name | Meaning |
|---|---|---|
| `P` | probe measure | The frame of reference. **There is no understanding in general, only understanding relative to a `P`.** |
| `D` | divergence | How differently two agents decide, over `P`. |
| `D_floor` | noise floor | Divergence between *perfectly aligned* agents, from their own stochasticity. Not correcting for it is the field's most common error. |
| `F*` | transfer fidelity | Fraction of the closable gap a message closed. `< 0` = **antinoophor**. **Not reportable alone** — it rewards copying the sender's errors, so it must be decomposed (see below). |
| `η` | efficiency | `F* / cost`. Understanding per token. What engineering should optimize and almost nothing does. |
| `Φ` | **phantom agreement** | Claimed agreement minus observed. Both parties believe it landed; probes say otherwise. The field's central pathology. |
| `K` | channel capacity | Best fidelity any message could achieve. A curve `K(C)`, estimated only on **held-out** probes — against a visible probe measure a lookup table trivially reaches 1. |

---

## The two claims worth arguing about

**[L6](theory/laws.md#l6) — optimal encoding is contrastive, not declarative.**
Don't send your model of the problem. Send its *boundaries* — the cases where
you and the receiver would diverge. The receiver already has a prior; spending
tokens re-describing what it would have reconstructed anyway is waste.

**[L5](theory/laws.md#l5) — fluency inflates phantom agreement.** The more
polished the message, the more both parties believe it worked — faster than it
actually works. Eloquence is a stronger signal of transfer than a cause of one.

Together they predict something uncomfortable: **the encoding that transfers
best is the one that feels worst.** Every party's sense of a good handoff would
be anticorrelated with its quality.

[E-001](experiments/E-001-fluency-cost/) tests both. It is pre-registered and
designed so that a null result is publishable and damaging.

---

## Repository

```
PRINCIPIA.md          the research program: axioms, motivation, falsifiers
theory/
  definitions.md      formal definitions of every quantity
  laws.md             six falsifiable conjectures, each with a kill condition
  open-problems.md    ten problems for the first decade
metrics/              reference implementation (stdlib + anthropic only)
probes/               probe-measure format and schema
experiments/          one directory per experiment, pre-registration first
protocols/            NHP-0001: a handoff format carrying a fidelity claim
benchmarks/           the Noophora Benchmark (not yet populated)
journal/              dated lab notebook
lexicon.md            canonical terminology
```

---

## Quick start

```bash
git clone https://github.com/vyakymenko/noophorics
cd noophorics
python3 metrics/tests/test_metrics.py       # 38 tests, no deps
python3 metrics/validation/synthetic.py    # does the estimator recover a known F*?
python3 experiments/E-001-fluency-cost/runner.py --dry-run   # pipeline, no API calls
```

To run E-001 for real you need `pip install anthropic` and an Anthropic
credential (`ANTHROPIC_API_KEY`, or `ant auth login`):

```bash
python3 experiments/E-001-fluency-cost/runner.py --samples 30
```

Measuring a transfer yourself:

```python
from noophorics import mean_divergence, mean_permutation_floor, transfer_fidelity
from noophorics.decomposition import decompose

d_prior = mean_divergence(sender_dists, receiver_before)
d_post  = mean_divergence(sender_dists, receiver_after)
floor   = mean_permutation_floor(sender_draws, prior_draws)   # same n as above

f_star = transfer_fidelity(d_prior, d_post, floor)   # aggregate -- not enough alone

# What the aggregate hides: mimicry, and gap closure bought by class priors.
print(decompose(measure, sender_draws, prior_draws, post_draws).summary())
```

Never report a fidelity without the floor correction, without naming the probe
measure it was taken against, or **without the decomposition** — the aggregate
cannot tell understanding from copying the sender's mistakes.

---

## Method

- Every experiment **pre-registers** its hypothesis before any data exists. The
  git history is the record.
- Every number carries its probe measure, sample count, and noise floor.
- Null results are committed with the same prominence as positive ones.
- Refuted laws are struck through, never deleted.

See [CONTRIBUTING.md](CONTRIBUTING.md). The pre-registration norm is the one
rule that is not negotiable — it is what keeps this a science rather than a
collection of confirmations.

---

## What we already refuted, in our own work

The programme's only completed result so far is negative, and it is about the
programme itself:

- **`F*` rewards replicating the sender's errors.** On E-001's own data both
  receivers out-decided the sender that briefed them, while fidelity ranked
  them the other way; 62% of the headline effect came from the four probes
  where the sender was wrong. `F*` now decomposes into convergence-where-the-
  sender-is-right, error replication, and class-prior matching.
  ([FINDINGS](experiments/E-001-fluency-cost/FINDINGS.md))
- **Axiom A3 (`K < 1` always) is false as first stated** — a 113-token lookup
  table over a visible probe measure reaches `F* = 1`. Restated for held-out
  probes and bounded cost.
- **The v0.1 noise floor was inflated**, by roughly 51% at the sample size the
  experiment used. ([validation](metrics/validation/synthetic.py))

## Status

**Version 0.3. Nothing is established, and several things are refuted.**

Six conjectural laws (one restated after refutation), ten open problems, zero
confirmed positive findings. Every claim in this repository should be read
as a bet, and its confidence calibrated accordingly.

The correct response to this repository is not agreement. It is a probe.

---

## Intellectual lineage

Standing on, and departing from: Shannon (information without shared
codebooks), Quine (indeterminacy of translation — our axiom A3 is its
quantitative form), Grice and Clark (common ground, made numerical), Sperber &
Wilson (relevance), Frank & Goodman (RSA), Gärdenfors (conceptual spaces), and
the knowledge-distillation literature (transfer between networks, but measured
as task accuracy rather than as understanding).

None of them had the instrument.

---

## Licensing

Dual-licensed, deliberately:

- **Code** — [Apache-2.0](LICENSE). Not MIT: Apache carries an explicit patent
  grant, and this project describes *methods of measurement* that someone might
  otherwise try to enclose.
- **Prose, theory, and experimental documentation** —
  [CC BY 4.0](LICENSE-CC-BY-4.0.txt), so results can be cited and built on with
  attribution.

---

## Citation

Contributor roles, and the disclosure of AI contribution, are in
[AUTHORS.md](AUTHORS.md). See [CITATION.cff](CITATION.cff), or:

> Yakymenko, V. (2026). *Noophorics: a quantitative science of transferring
> understanding across heterogeneous minds.* Version 0.3.
> https://noophorics.org
