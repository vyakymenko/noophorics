# Lexicon

Canonical terms. When a term appears in this repository it means exactly what
this file says it means.

> The repository is English-only for now. Translations are planned as a
> separate layer once the core terminology stabilizes — translating a moving
> vocabulary is how a field ends up with three names for one quantity.

---

## Core

**noophorics** — the quantitative science of transferring understanding across
systems with non-identical priors. From νόος (mind) + φορά (carrying).

**noophor** — a single act of transfer: sender, artifact, receiver.

**antinoophor** — a noophor with `F* < 0`. A message that leaves the receiver
further from the sender than before it was sent.

**noophoric act** — the triple `(A, m, B)`. Synonym for noophor; used when the
components matter.

---

## Agents and probes

**agent** — any system that maps a probe to a distribution over answers.
Defined entirely by its answer distributions; internals are irrelevant.

**sender / receiver** — the two roles in a noophor. Roles, not properties: the
same system is routinely both.

**probe** — a decidable decision whose answer depends on the understanding being
transferred. *Decidable* means the answer space is finite and discrete.

**probe measure (`P`)** — a distribution over probes. The noophoric frame of
reference. No quantity is defined without one.

**admissible probe measure** — one on which the parties actually disagree
before transfer. Measuring fidelity where agreement already exists measures
nothing.

---

## Quantities

**divergence (`D`)** — expected Jensen–Shannon divergence between the agents'
answer distributions over `P`, in bits. Bounded `[0, 1]`.

**agreement rate (`Â`)** — fraction of probes on which the agents' modal
answers match. Coarser than `D`, but the quantity parties can actually estimate
about themselves.

**self-divergence (`D_self`)** — an agent's divergence from itself under
independent resampling. Agents are stochastic; this is the measure of it.

**noise floor (`D_floor`)** — mean self-divergence of the two agents. The
irreducible divergence between perfectly aligned parties. Not correcting for it
is the most common error in noophoric measurement.

**transfer fidelity (`F*`)** — the fraction of the closable gap that the
message closed, floor-corrected. `1` = fully closed, `0` = no effect,
`< 0` = antinoophor.

**cost (`C`)** — the price of the artifact, in the receiver's tokens unless
stated otherwise. The receiver pays to read it.

**noophoric efficiency (`η`)** — `F* / C`. Understanding per unit cost. The
quantity engineering should optimize and currently does not.

**channel capacity between minds (`K`)** — `sup_m F*(m)`. The best fidelity any
message could achieve at unbounded cost. Estimated as a lower bound `K̂` over a
stated search budget.

**residual (`R`)** — `1 − K`. The untransferable remainder. Axiom A3 asserts
it is nonzero.

---

## Phenomena

**phantom agreement (`Φ`)** — claimed agreement rate minus observed agreement
rate. `Φ > 0` is a shared illusion of successful transfer: both parties
believe it landed, probes say otherwise. The field's central pathology.

**invariant core** — the part of an understanding that survives arbitrarily
many chained transfers without loss. Conjectured (L4) to be constraints and
prohibitions rather than descriptions.

**contrastive encoding** — a message specifying where the parties would
diverge: boundaries, exclusions, edge cases, what *not* to do.

**declarative encoding** — a message describing what the sender understands.
The default form of nearly every handoff written today.

---

## Method

**pre-registration** — committing an experiment's hypothesis and analysis plan
before any data exists. The git history is the record.

**probe test** — running a probe measure after a transfer to measure what
landed. The noophoric analogue of replication.

**ablation ladder** — truncating a message to successive cost levels and
measuring the resulting `F*(C)` curve.

**reconstructive test** — asking whether the receiver can generate a message
that achieves comparable fidelity with a *third* party. Tests whether
understanding transferred deeply enough to be re-transmitted.

---

## Symbols

| Symbol | Reads as | Defined in |
|---|---|---|
| `A`, `B` | sender, receiver | [definitions §1.1](theory/definitions.md) |
| `π` | a probe | §1.2 |
| `P` | probe measure | §1.3 |
| `m` | the message / artifact | §1.4 |
| `B\|m` | receiver after conditioning on `m` | §1.4 |
| `d(A,B\|π)` | per-probe divergence | §2.1 |
| `D(A,B\|P)` | divergence over `P` | §2.2 |
| `Â` | observed agreement rate | §2.3 |
| `D_self` | self-divergence | §3.1 |
| `D_floor` | noise floor | §3.2 |
| `F*` | transfer fidelity | §4.1 |
| `C(m)` | message cost | §4.2 |
| `η` | noophoric efficiency | §4.3 |
| `Ĉ` | claimed agreement rate | §5 |
| `Φ` | phantom agreement | §5 |
| `K` | channel capacity | §6.1 |
| `R` | residual | §6.2 |

---

*This document is licensed CC BY 4.0.*
