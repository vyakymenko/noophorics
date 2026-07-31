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

**criterion-bearing / criterion-free** — the two regimes a probe measure can be
in (v0.4). *Criterion-bearing*: an answer exists independently of the sender, so
a key or an adjudicator panel is an admissible reference and the word
*understanding* is licensed. *Criterion-free*: the sender **is** the criterion by
construction — a preference, a house style, a judgment call whose owner defines
the right answer — so `R = sender` is correct rather than tolerated, and there
is no sender error available to be replicated. Key *absence* does not move a
measure into the second regime: that is an epistemic fact about the
experimenter, not an ontological one about the probe.

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

**noise floor (`D_floor`)** — ~~mean self-divergence of the two agents; the
irreducible divergence between perfectly aligned parties~~. **Retracted in
v0.3** ([retraction 2](RETRACTIONS.md)): two perfectly aligned stochastic
agents have identical true distributions, so their true divergence is exactly
zero and there is nothing irreducible. `D_floor` is **finite-sample estimator
bias at a stated `n`**, obtained by a permutation null over the pooled draws. It
is a property of the measurement, not of the agents, and it belongs in the
estimator rather than in the definition. Not correcting for it is still the most
common error.

**transfer fidelity (`F*_R`)** — the fraction of the closable gap **toward a
declared reference `R`** that the message closed, floor-corrected. `1` = fully
closed, `0` = no effect, `< 0` = antinoophor. **Never reportable without its
`R`** (v0.4). `F*_{R=A}` is identically the pre-v0.4 quantity.

**cost (`C`)** — the price of the artifact, in the receiver's tokens unless
stated otherwise. The receiver pays to read it.

**noophoric efficiency (`η`)** — `F*/C`, understanding per unit cost, and
**valid only where `F* ≥ 0`**. ~~The quantity engineering should optimize.~~
A ratio with a signed numerator is not an ordering
([retraction 3](RETRACTIONS.md)): at `F* = −1` a 100-token antinoophor scores
−10.00 and an 800-token one −1.25, ranking the costlier failure higher. Use
`V_λ` when the sign is unknown.

**net value (`V_λ`)** — `F*_R − λ·C`. Monotone in both arguments at every sign,
so it orders messages the way the field means to. `λ` is the declared exchange
rate between fidelity and a token; sweeping it traces the frontier, which makes
`V_λ` and `K_R(C)` the same object seen twice.

**channel capacity between minds (`K_R`)** — `sup_m F*_R(m)`. The best fidelity
any message could achieve at unbounded cost, toward a declared reference.
Estimated as a lower bound `K̂` over a stated search budget, by sample-splitting
— a max-over-search estimate is a winner's curse and overstates.

**residual (`U`)** — `1 − K_R`. The untransferable remainder toward a declared
reference. Axiom A3 asserts it is nonzero. ~~Written `R` before 2026-07-31~~ —
renamed because v0.4 gave `R` to the reference disposition without checking the
symbol was free, and for a day this glossary listed `R` as the residual directly
above a section defining `R` as the reference.

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
| `F*_R` | transfer fidelity | §4.1 |
| `C(m)` | message cost | §4.2 |
| `η` | noophoric efficiency | §4.3 |
| `Ĉ` | claimed agreement rate | §5 |
| `Φ` | phantom agreement | §5 |
| `K_R` | channel capacity | §6.1 |
| `U` | residual | §6.2 |
| `R` | reference disposition | §4.1.1 |
| `V_λ` | net value | §4.3 |


## Reference disposition `R` *(v0.4)*

The per-probe target distribution a transfer is scored against, declared with
`P` before data exists and carrying a recorded provenance. Kinds: `key`,
`panel`, `sender`. See [definitions §4.1.1](theory/definitions.md).

Before v0.4 the target was the sender, silently. It was an assumption wearing a
parameter's clothes.

## Replication fidelity *(v0.4)*

`F*_{R=sender}` — movement toward the sender specifically. Numerically identical
to the pre-v0.4 `F*`. A real quantity and often the right one, when what is
being transferred is a preference, a house style, or a judgment call whose owner
defines the correct answer. **It may not be reported as understanding.**

## Transfer surplus

`F*_R(m) − F*_R(A)` — how much closer to the reference the receiver ended than
the sender that briefed it. Positive values were unscoreable before v0.4:
[E-001](experiments/E-001-fluency-cost/FINDINGS.md) produced them and recorded
them as partial failure.


---

*This document is licensed CC BY 4.0.*
