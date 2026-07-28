# E-001 — Amendment 003: Amendment 001 was wrong; the refusal is model-side

**Date:** 2026-07-28
**Corrects:** [AMENDMENT-001.md](AMENDMENT-001.md), whose diagnosis does not
survive measurement.
**Amends:** the instrument only. [PREREGISTRATION.md](PREREGISTRATION.md)
remains unchanged and unedited.

---

## The retraction

Amendment 001 concluded that the `cyber`-category refusal was caused by an
*interaction* between the KESTREL domain's access-control semantics and the
compose prompt, and replaced the domain on that basis.

**That conclusion was reached from one API call per ablation cell.** The
phenomenon is stochastic. One call per cell cannot distinguish "triggers this"
from "sometimes triggers anything", and the inference was therefore not
supported by its evidence.

This is the same error the field's own reporting standard exists to prevent:
[definitions.md §1.1](../../theory/definitions.md) says an agent's response is
a *distribution*, and that treating a single sample as a disposition is the
most common methodological error here. It was made three files later, on the
first real diagnosis.

## What measurement actually shows

Refusal rates, compose requests, 10 attempts per cell:

| Spec | Prompt | Refusals |
|---|---|---|
| MERIDIAN | NARRATIVE | 9/10 |
| MERIDIAN | CONTRASTIVE | 9/10 |
| KESTREL (withdrawn) | NARRATIVE | 5/6 |
| KESTREL (withdrawn) | CONTRASTIVE | 1/6 |

The domain replacement did not help. The withdrawn domain refuses *less* in one
cell than its replacement does in either.

Controls, same session:

| Request | Refusals |
|---|---|
| Spec + "summarise these rules" — returned `end_turn` earlier the same day | 4/4 |
| Spec + a single probe question — **204 of these succeeded earlier the same day** | 4/4 |
| No spec, unrelated benign request | 0/4 |
| A three-line rulebook of the same shape | 0/5 |

Anything carrying either full spec now refuses, including a trivial
"how many rules are listed?". The account and the API are healthy.

## The actual cause

| Model | Probe | Compose |
|---|---|---|
| `claude-opus-5` | 4/4 refused | 4/4 refused |
| `claude-opus-4-8` | 0/4 | 0/4 |
| `claude-sonnet-5` | 0/4 | 0/4 |

The refusal is **model-specific to `claude-opus-5`**, and it is **not stable
over time**: the same probe request that succeeded 204 consecutive times in the
morning refused 5 out of 5 in the evening, with an unchanged spec and an
unchanged prompt.

Whether this is session- or account-level escalation, or a classifier update
between the two measurements, is not determinable from outside. Both are
outside the experiment's control.

## Consequences for the method

**1. Classifier state is a confound with a time axis.** An experiment whose
conditions are collected at different times can have its conditions differ by
classifier state rather than by treatment. E-001 collects four conditions
sequentially over roughly an hour. Any run must record the model, and any
mid-run change in refusal behaviour voids it.

**2. Retry-until-success is not available.** At a 90% per-call refusal rate,
retrying until both briefs compose selects the briefs that happened to pass —
selection applied directly to the treatment. Prohibited: a refusal voids the
run.

**3. `--sender-model` / `--receiver-model` are now load-bearing.** E-001 is
being run on `claude-opus-4-8`, and the results will state that
`claude-opus-5` could not be used as either party. This is a real limitation on
generality, not a footnote: the model whose behaviour prompted the field is the
one the field currently cannot measure.

**4. Cache keys now carry both model ids.** Samples drawn from one model must
never be reused for another.

## What stands and what falls

**Falls:** the causal claim in Amendment 001 — that the domain's access-control
semantics triggered the classifier. Unsupported.

**Stands:** the domain replacement itself, as a neutral change. MERIDIAN-34 is
structurally identical to KESTREL-34, so no scientific content depends on which
is used, and switching back would cost more than it gains. It is kept for
continuity and no longer justified by the retracted diagnosis.

**Stands:** everything in Amendment 001 that was not a causal claim — compose
running before the probe sweep, the resumable cache, and the void gate. The
void gate in particular was vindicated in the very next run: it caught a
single-condition refusal that would otherwise have reported a large significant
effect in the experimenter's favoured direction.

---

*This document is licensed CC BY 4.0.*
