# E-001 — Amendment 001: domain replacement

**Date:** 2026-07-28
**Amends:** the instrument only. Hypotheses, analysis plan, significance
criteria, and promotion gates in [PREREGISTRATION.md](PREREGISTRATION.md) are
**unchanged and unedited.**

---

## What happened

The first live run of E-001 was **void**. It is recorded here rather than
discarded.

The sender answered all 34 probes successfully — 204 API calls — and then
failed at the next step, composing the handover brief:

```
stop_reason  : 'refusal'
stop_details : category='cyber'
               "This request triggered restrictions on violative cyber
                content and was blocked under Anthropic's Usage Policy."
usage        : 60 in / 2 out          <- blocked before generation
```

A safety classifier declined to write a handover brief about a fictional
fellowship eligibility rulebook. The run died with no messages, so no transfer
could be measured.

## Diagnosis

The trigger was isolated by ablation, one API call per cell:

| Request | Result |
|---|---|
| KESTREL spec + compose prompt | **refusal / cyber** |
| KESTREL spec + "summarise these rules" | `end_turn` |
| No spec + compose prompt | `end_turn` |
| KESTREL spec + compose prompt, handoff framing removed | **refusal / cyber** |

Neither component triggers the classifier alone. The **interaction** does.

Best available reading: a rulebook phrased in terms of who is *eligible*,
*exempt*, *excluded*, and who is barred "regardless of every other rule",
combined with a request to write instructions enabling a third party to decide
cases while *"seeing nothing except what you write"*, pattern-matches to
authoring guidance for circumventing an access-control system.

Note what that implies. The features that made KESTREL-34 a good instrument —
an overriding rule, a scoped exemption, an asymmetric auto-fix, boundary
conditions — are also what tripped the classifier. **The domain was well
designed for the experiment and badly chosen for the world it runs in.**

## Remedy

The domain was reskinned to **Meridian Review submission handling**: a
fictional manuscript-handling rulebook. The mapping is one-to-one — every
rule, every interaction, every probe, and every answer key is preserved. Only
the semantics changed:

| KESTREL-34 | MERIDIAN-34 |
|---|---|
| applicant age ≥ 22 | manuscript length ≥ 22 pages |
| completed degree / 3 years practice | official template / 3 years revision history |
| Tier-1 institutional affiliation | Tier-1 venue presentation |
| prior award recipient | accepted in a prior round |
| joint application, 2 applicants | paired submission, 2 manuscripts |
| Region D + 2 letters | Track D + 2 endorsements |
| open ethics finding (overriding) | open retraction notice (overriding) |
| budget 8,000–45,000 | figure count 8–45 |
| ELIGIBLE / INELIGIBLE / ADJUSTED | HANDLED / RETURNED / PADDED |

Class balance is identical: 13 / 18 / 3.

Verified before adoption: the same compose prompt against the reskinned spec
returns `end_turn` and produces a 728-token brief.

- Withdrawn measure: `KESTREL-34@cadcf2faaf74`
- Replacement measure: `MERIDIAN-34@707c48f18616`

## Second fix: the run was needlessly fragile

The failure destroyed 204 successful calls because composition happened
*after* the sender's probe sweep. Two changes:

1. **Composition now runs first.** A refusal costs two calls instead of
   discarding the sweep.
2. **Raw draws are cached to disk** (`--cache`), keyed by condition and probe,
   preserving draw order. A failed run resumes instead of restarting.

## Why this is an amendment and not a new experiment

The hypotheses did not change. H1, H2, H3, the permutation test, `α`, the
promotion gates, and the declared limitations are exactly as committed in
`6a72a94`, before any data existed. What changed is the material being
transferred — the instrument, not the claim.

Editing the pre-registration would have destroyed the audit trail. Opening an
E-001b would have implied the hypotheses moved. This file is the honest third
option, and it is committed **before** the replacement run produces any data.

## Standing

The void run produced no fidelity measurement and no evidence bearing on L5 or
L6. It produced one finding worth keeping, recorded in
[`journal/`](../../journal/): **a measurement instrument can be blocked by the
safety behavior of the system it measures, and the block can look like a
result.** Had the classifier declined only *one* of the two conditions instead
of both, the run would have completed and reported a spurious difference
between narrative and contrastive encodings.

---

*This document is licensed CC BY 4.0.*
