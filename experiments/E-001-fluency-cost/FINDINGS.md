# E-001 — Findings

**Status:** the run was interrupted at the CEILING condition and never completed.
It nonetheless produced the most important result this programme has: **the
central quantity, as defined, does not measure what the field's name promises.**

Recomputed from `.sample-cache.json` (sender / PRIOR / NARRATIVE / CONTRASTIVE
complete at 34 probes × 6 draws; CEILING interrupted at 25/34). Sender and
receiver both `claude-opus-4-8`.

---

## 1. F\* rewards replicating the sender's errors

| | accuracy vs key |
|---|---|
| Sender (holds the spec) | 0.882 |
| PRIOR receiver (no message) | 0.441 |
| NARRATIVE receiver | **0.971** |
| CONTRASTIVE receiver | **0.941** |

**Both receivers decided cases better than the sender that briefed them.**

Fidelity orders them the other way:

| condition | D_post | floor | F\* |
|---|---|---|---|
| NARRATIVE | 0.1369 | 0.0098 | 0.770 |
| CONTRASTIVE | 0.0599 | 0.0091 | **0.908** |

The sender was wrong on four probes. On those four:

| probe | key | sender | narrative | contrastive | d(nar) | d(con) |
|---|---|---|---|---|---|---|
| M14 | HANDLED | RETURNED | **HANDLED** | RETURNED | 0.65 | 0.19 |
| M19 | PADDED | RETURNED | **PADDED** | RETURNED | 1.00 | 0.19 |
| M26 | HANDLED | RETURNED | **HANDLED** | HANDLED | 1.00 | 0.65 |
| M33 | HANDLED | RETURNED | **HANDLED** | HANDLED | 1.00 | 1.00 |

On M14 and M19 the contrastive receiver **copies the sender's wrong answer and
is rewarded for it**; the narrative receiver answers **correctly** and is
charged near-maximal divergence.

> **62% of the entire H1 effect (1.618 of 2.618) comes from the four probes
> where the sender was wrong and the narrative receiver was right.**

Had this run completed and been analysed as pre-registered, "contrastive
transfers better" would have substantially meant *"contrastive reproduces the
sender's mistakes more faithfully."*

## 2. The pre-registered test is a null anyway

Permutation test, exactly as specified in
[PREREGISTRATION.md §4](PREREGISTRATION.md), seed 20260728:

```
mean difference +0.0770    p = 0.123
```

Above α = 0.05. Under the promotion criteria, L5 and L6 stay `conjectured`.
The F\* margin (0.908 vs 0.770) looks decisive to the eye and is not supported
by the test — which is itself a finding about how these numbers read.

## 3. Why this is a construct failure, not an estimator failure

> **Prior art, added 2026-07-29.** The separation this experiment forced —
> agreement with the source is not the same quantity as being right — is
> established in machine learning. Stanton et al. (2021), *Does Knowledge
> Distillation Really Work?* (NeurIPS 34, 6906–6919), distinguish **fidelity**
> (student–teacher prediction agreement, measured by top-1 agreement and
> predictive KL) from **generalization**, supply dedicated fidelity metrics, and
> show that good student accuracy does not imply good fidelity. Burns et al.
> (arXiv:2312.09390) hit it from the other side: high student–supervisor
> agreement is their *failure* signal, the imitation mode an auxiliary
> confidence loss exists to suppress.
>
> Ours is an independent rediscovery in a different domain, and the framing
> below is ours, not theirs: "construct failure" is our vocabulary about our
> metric, Stanton et al. say nothing about understanding, meaning, or
> communication, their evidence is supervised image classification, and their
> prescription is to pursue fidelity *harder*. Their result is also
> regime-dependent rather than general — fidelity and generalization are in
> tension under self-distillation and positively correlated when distilling
> large ensembles.
>
> It cost this programme a live run and an amendment to find something a
> five-year-old NeurIPS paper reports in its abstract. That is a reading
> failure, and it is the reason [`theory/prior-art.md`](../../theory/prior-art.md)
> now exists.

No floor estimator, no sample size, and no amendment repairs this. It follows
directly from the definition:

> B understands what A understands to the extent that B would make the same
> decisions A would make.

That definition cannot distinguish

- **(a)** B reconstructed the domain, from
- **(b)** B reconstructed A's *defects*.

A transfer leaving the receiver **more competent than the sender** — arguably
the best outcome a handoff can have — is scored as partial failure.

There is a second, quieter component. `D_prior = 0.5625` between a decisive
sender and a guessing receiver is largely *class-prior and decisiveness*
mismatch, not domain content. A message reading "default to RETURNED unless the
case is plainly baseline" carries no rule structure and would close much of
that gap. F\* therefore mixes understanding, mimicry, and induced decisiveness
in unknown proportions.

The sender-accuracy gate was supposed to protect against exactly this and did
not: at 0.85 over 34 probes it tolerates five errors, and the sender's four
errors carried most of the signal. A gate on the *mean* cannot protect a
statistic whose effect concentrates on the tail.

## 4. Consequence

`F*` as defined in [definitions.md §4.1](../../theory/definitions.md) is
retained but **is no longer sufficient on its own**. Required decomposition,
with the answer key promoted from sanity check to load-bearing input:

- convergence to the sender **on probes where the sender is right**,
- **error replication** on probes where the sender is wrong,
- **induced decisiveness** — gap closure attributable to class-prior matching
  rather than to rule content.

Until fidelity separates those three, every number this programme produces is a
mixture in unknown proportions.

## 5. Standing

E-001 tested nothing about L5 or L6. Both remain `conjectured`. The run is
recorded as **incomplete and non-inferential**; its data is kept because it
falsified something more important than its own hypotheses.

This finding came from an adversarial review, not from the authors. It was
verified independently against the cached draws before being accepted, and
every number above is reproducible from `.sample-cache.json`, now tracked.

---

*This document is licensed CC BY 4.0.*
