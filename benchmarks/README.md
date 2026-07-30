# The Noophora Benchmark

**Status: not yet populated.** This file specifies what it will be, so that the
design is criticizable before it is built.

---

## Purpose

A standard battery of transfer tasks that any sender/receiver pair can be
scored on, producing comparable `F*_R`, `η`, and `Φ` numbers across labs,
architectures, and time.

The unit of comparison is a **transfer**, not a task. Existing benchmarks ask
whether a model can do a thing. Noophora asks whether a model can *hand a thing
over* — and whether it knows when it failed to.

---

## Planned tracks

| Track | Question | Probe style |
|---|---|---|
| **T1 — Rule transfer** | Can A convey a rule system so B decides cases identically? | Decidable case verdicts |
| **T2 — Intent transfer** | Can a specification convey what the requester actually wanted? | Choice between plausible implementations |
| **T3 — Self-transfer** | How much of an agent survives its own compaction? | Probes before and after compaction |
| **T4 — Chain decay** | How does fidelity fall across N hops? | Same probe measure at each hop |
| **T5 — Calibration** | Does the sender know how much landed? | `Φ` as the primary score |

T3 has the most economic weight today — every long-running agent compacts
itself constantly — and the least existing theory. See
[Problem 9](../theory/open-problems.md).

---

## Scoring

A submission reports, per track:

- `F*_R` — floor-corrected, unclipped, **against a declared reference**.
  A submission without its `R` and that `R`'s provenance is not scorable: where
  `R` is the sender the number is *replication*, and the two are not comparable.
- `η` — fidelity per kilotoken
- `Φ` — phantom agreement
- `K̂` — capacity estimate, with its search budget stated

**There is no single headline number, and there will not be one.** A pair with
high `F*` and high `Φ` is *worse* than one with lower `F*` and `Φ ≈ 0`: the
first transfers well but cannot tell when it hasn't, which is the failure mode
that reaches production. Collapsing that distinction into one score would
destroy the benchmark's only real contribution.

---

## Design constraints

- **Fictional domains only.** Real-world domains let receivers score well from
  training data rather than from the transfer, which measures recall and calls
  it fidelity.
- **Held-out probe sets.** A public set for development, a private set for
  scoring, to blunt [Problem 6](../theory/open-problems.md) — encodings
  optimized against a visible `P` that generalize to nothing.
- **Sender and receiver reported separately.** A pair is the unit; a model's
  score as a sender and as a receiver are different numbers and
  [L2](../theory/laws.md#l2) predicts they will differ systematically.
- **Cost always reported.** An unbounded-length transfer is not an achievement.

---

## Open design questions

Genuinely unresolved, and the reason this is a specification rather than a
release:

- How to prevent overfitting to the benchmark's probe style without keeping
  everything private forever.
- Whether `Φ` should be scored on elicited claims (cheap, gameable once the
  incentive exists) or on some behavioral proxy (expensive, not yet designed).
- How to keep fictional domains hard without making them arbitrary. A domain
  nobody could reason about measures nothing.

Proposals welcome. See [CONTRIBUTING.md](../CONTRIBUTING.md).
