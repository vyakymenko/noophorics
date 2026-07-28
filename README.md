# Noophorics

**The quantitative science of transferring understanding across minds that do
not share a substrate.**

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
codebooks differ and are partially reconstructed on the fly. There is no theory
for that case. Noophorics builds one by replacing *symbol recovery* with
*behavioral convergence* as the measure of success: **B understood what A
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
| `F*` | transfer fidelity | Fraction of the closable gap that a message closed. `< 0` means the message made things worse — an **antinoophor**. |
| `η` | efficiency | `F* / cost`. Understanding per token. What engineering should optimize and almost nothing does. |
| `Φ` | **phantom agreement** | Claimed agreement minus observed. Both parties believe it landed; probes say otherwise. The field's central pathology. |
| `K` | channel capacity | Best fidelity any message could achieve. We conjecture `K < 1` always. |

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
python3 metrics/tests/test_metrics.py                        # 30 tests, no deps
python3 experiments/E-001-fluency-cost/runner.py --dry-run   # pipeline, no API calls
```

To run E-001 for real you need `pip install anthropic` and an Anthropic
credential (`ANTHROPIC_API_KEY`, or `ant auth login`):

```bash
python3 experiments/E-001-fluency-cost/runner.py --samples 6
```

Measuring a transfer yourself:

```python
from noophorics import mean_divergence, noise_floor, transfer_fidelity

d_prior = mean_divergence(sender_dists, receiver_before)
d_post  = mean_divergence(sender_dists, receiver_after)
floor   = noise_floor(sender_self_divergence, receiver_self_divergence)

f_star = transfer_fidelity(d_prior, d_post, floor)   # floor-corrected, unclipped
```

Never report a fidelity without the floor correction, and never report one
without naming the probe measure it was taken against.

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

## Status

**Version 0.1. Nothing here is established.**

One pre-registered experiment (not yet run), six conjectural laws, ten open
problems, zero confirmed findings. Every claim in this repository should be read
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

See [CITATION.cff](CITATION.cff), or:

> Noophorics: a quantitative science of transferring understanding across
> heterogeneous minds. Version 0.1, 2026. https://github.com/vyakymenko/noophorics
