# Noophorics

**Measure what survives a handoff.**

Noophorics is an open research programme developing falsifiable measurements
for transfers of understanding between people, models, and sessions. It asks
whether the receiver's decisions after the transfer move toward a stated
reference — not whether they repeat the same words.

[noophorics.org](https://noophorics.org) · founded 2026 by
[Valentyn Yakymenko](https://github.com/vyakymenko) ·
[authorship and contributor roles](AUTHORS.md)

[See Φ in 60 seconds](https://noophorics.org/#instrument) ·
[run the reference metrics](#quick-start) ·
[read the research programme](https://noophorics.org/#gap)

Two minds are given the same problem. One explains it to the other. Both agree
the explanation landed.

Nobody measures what was lost.

Every handoff makes a claim. Noophorics is the attempt to test it — with units,
falsifiable predictions, and experiments that can fail.

> **Experimental by design.** No law is established, and several of our own
> claims have already been refuted or revised.

---

## The idea in one paragraph

Shannon's information theory measures how much uncertainty a message removes,
**assuming sender and receiver share a codebook**. Between a human and a model,
or between two models, or between a session and its own compacted summary, the
codebooks differ and are partially reconstructed on the fly. Adjacent
literatures address parts of this — decision-preserving compression, semantic
rate–distortion for heterogeneous agents, goal-oriented semantic communication.
What we have not found elsewhere is one instrument carrying fidelity, cost,
**and the calibration of both parties** together. That is a claim about
*coverage*, not about discovery, and it is deliberately narrower than what this
document said before 2026-07-29: the believed-versus-actual gap itself has been
measured in humans since at least 1990, and
[PRINCIPIA §1](PRINCIPIA.md) carries the retraction and
[theory/prior-art.md](theory/prior-art.md) the verified ledger. That gap where sender and
receiver are both language models had not been measured by anyone, including
us, until [E-002b](experiments/E-002b-phantom-agreement-ladder/FINDINGS.md) on
2026-07-31: `Φ = +0.2961`, CI `[+0.2200, +0.3649]`, **one model in both roles**,
and the number is the parties' near-constant 95.5% claim rate minus their 65.9%
actual agreement. The level is measured. Whether confidence *responds* to
transfer is [E-002c](experiments/E-002c-calibration-slope/PREREGISTRATION.md),
registered and not yet run. Noophorics builds it by
replacing *symbol recovery* with *behavioral convergence*: **B understood what A
understood, over a domain, to the extent that B's decisions moved toward a stated
reference for that domain.** That single move makes understanding measurable,
comparable across substrates, and falsifiable. ~~"…to the extent that B would make
the same decisions A would make"~~ was the v0.1 form; where the reference is A's
own decisions the quantity is *replication of A*, which is weaker and is not the
same claim ([amended v0.4](PRINCIPIA.md), [retractions](RETRACTIONS.md)).

---

## Φ in 60 seconds

A coding agent hands a migration task to another agent. Against a stated probe
measure of ten held-out decisions:

| Observable | Rate |
|---|---:|
| Sender's predicted agreement | 90% |
| Receiver's predicted agreement | 80% |
| Observed agreement | 60% |

`Φ = mean(90%, 80%) − 60% = 25 percentage points`

Both agents are confident, yet their decisions diverge. We call that gap
**phantom agreement**.

*Illustrative example only. Whether Φ is reliable and useful across domains
remains an open empirical question.*

---

## Available today

- [`metrics/`](metrics/) — reference implementations of divergence, transfer
  fidelity, its decomposition, and synthetic validation.
- [`probes/`](probes/) — a format for stating the decisions against which a
  transfer is measured.
- [`NHP-0001`](protocols/NHP-0001-handoff.md) — a draft handoff protocol
  carrying constraints, probes, and a fidelity claim. v0.1 was published
  without an implementation; writing one found four defects in it, including a
  gate that passed the case it existed to catch. All four are repaired in v0.2
  and left visible in the document.
- [`experiments/`](experiments/) and [`journal/`](journal/) — pre-registrations,
  void and null results, corrections, and refuted claims kept in the public
  record.

These are research instruments, not a validated standard or production
product.

---

## Why now

Understanding is difficult to instrument because the receiver's state is
private. You can ask a listener what they understood, but the report is not the
state, and you cannot run ten thousand controlled trials on one human mind.

Language models create a newly instrumentable case: resample their
dispositions, probe arbitrary decisions, ablate the input, and repeat at a cost
measured in cents. The same is true of the sender. This repository is an attempt
to build a measurement programme around that capability.

---

## Core quantities

Formal definitions in [`theory/definitions.md`](theory/definitions.md);
reference implementation in [`metrics/`](metrics/).

| Symbol | Name | Meaning |
|---|---|---|
| `P` | probe measure | The frame of reference. **There is no understanding in general, only understanding relative to a `P`.** |
| `D` | divergence | How differently two agents decide, over `P`. |
| `D_floor` | noise floor | Divergence between *perfectly aligned* agents, from their own stochasticity. Not correcting for it is the field's most common error. |
| `F*_R` | transfer fidelity | Fraction of the closable gap **toward a declared reference `R`** that a message closed. `< 0` = **antinoophor**. **Not reportable without its `R`** — where `R` is the sender the quantity is *replication*, and it rewards copying the sender's errors. |
| `η` | efficiency | `F*/cost`, and **valid only for `F* ≥ 0`**: a ratio with a signed numerator is not an ordering, and it ranked a long antinoophor above a short one for three versions. Use `V_λ = F* − λC` when the sign is unknown. |
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

[E-001](experiments/E-001-fluency-cost/) was pre-registered to test both, but
the run was void and the partial data tested neither. It still exposed a defect
in aggregate `F*`: a receiver can outperform the sender and be penalised for not
copying the sender's errors. L5 and L6 remain conjectured.

---

## Repository

```
PRINCIPIA.md          the research program: axioms, motivation, falsifiers
theory/
  definitions.md      formal definitions of every quantity
  laws.md             six falsifiable conjectures, each with a kill condition
  open-problems.md    ten problems for the first decade
metrics/              reference metrics, decomposition, and agent adapters
probes/               probe-measure format and schema
experiments/          one directory per experiment, pre-registration first
protocols/            NHP-0001: a handoff format carrying a fidelity claim
benchmarks/           the Noophora Benchmark (not yet populated)
journal/              dated lab notebook
docs/                 website and condensed language summaries
lexicon.md            canonical terminology
```

---

## Quick start

```bash
git clone https://github.com/vyakymenko/noophorics
cd noophorics
python3 metrics/tests/test_metrics.py       # 92 tests, no deps
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

- **`F*` rewards replicating the sender's errors.** *(Repaired in v0.4: the
  reference is now a declared argument, and a sender reference measures
  replication by name.)* On E-001's own data both
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

**Version 0.5. One pre-registered result stands, and several things are refuted.**

Six conjectural laws (two restated after refutation), twelve open problems, zero
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

The narrower claim is that no single lineage supplies the combined instrument
used here: fidelity, cost, and the calibration of both parties over an explicit
probe measure.

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
> understanding across heterogeneous minds.* Version 0.5.
> https://noophorics.org
