# Draft audit: RIVERSIDE-30 self-transfer arithmetic and claim scope

**Reviewed 2026-10-07.** The repository owner adopted this audit's suggested
wording, and the claim it reviews is withdrawn as
[retraction 22](../RETRACTIONS.md). The text below is the 2026-09-09 draft as
generated; regeneration refreshes only its source hashes.

**2026-09-09 — draft for human review.** This audit adds no experimental result,
changes no prediction, and makes no formal retraction. It reconstructs the
[existing result](../probes/riverside-30/RESULTS-selftransfer.md) from its saved
draws and reviews the wording against the
[existing prediction](../probes/riverside-30/PREDICTION-selftransfer.md).

The arithmetic reproduces. The statement that the absence of a self-transfer
advantage is established exceeds the evidence. Both observed row means favour
the cross reader, and both satisfy the descriptive 1.5-probe criterion; this
does not establish equivalence or absence beyond these observations.

## Mechanically reconstructed measurement

Measure: **`RIVERSIDE-30@2e6afe2f3c92`**, with 30 probes.
All arm identifiers match a fresh semantic hash computed from the current
measure's IDs, prompts, options, keys, weights and holdout. The program reads
those fields without emitting their contents. All stored modes, modal margins,
divergence lists/counts, agreements, and sender accuracies match their raw draws.

The outcome is a count of unequal modal answers against **each reader's own
full-specification sender condition**. It is not `F*`, criterion accuracy, or a
measurement of understanding. Every party has **10 draws per probe**. Each arm
contains **300 reference draws and 900 receiver draws**; four arms therefore
contain **4,800 stored answers**, including **1,200 reference answers**. All
four artifacts label themselves `not_experimental_data: true`; their existing
status is instrument data.

| Composer | Reader | b0 | b1 | b2 | Mean diverged of 30 |
|---|---|---:|---:|---:|---:|
| gpt-oss:120b | gpt-oss:120b | 9 | 9 | 12 | 10.00 |
| gpt-oss:120b | qwen3.5:35b | 10 | 8 | 11 | 9.67 |
| qwen3.5:35b | gpt-oss:120b | 11 | 8 | 12 | 10.33 |
| qwen3.5:35b | qwen3.5:35b | 11 | 9 | 14 | 11.33 |

For each composer, subtract the cross-reader count from the self-reader count.
A positive value means self has more modal divergence:

| Composer | b0 | b1 | b2 | Mean self − cross | Absolute mean < 1.5 |
|---|---:|---:|---:|---:|---|
| gpt-oss:120b | -1 | +1 | +1 | +0.333 | Yes |
| qwen3.5:35b | +0 | +1 | +2 | +1.000 | Yes |

The six paired differences are **-1, +1, +1, +0, +1, +2**.
Their descriptive mean is **+0.666667** probes. The source's
reported SD of 0.94 is the **population SD** of these six observed numbers
(0.942809, denominator 6); the sample SD would be
1.032796 (denominator 5). Neither is an uncertainty interval.
**1** per-brief absolute difference
reaches or exceeds 1.5, the qwen-composed b2 pair at +2.

The reported sign calculation also reproduces: **4 positive,
1 negative, 1 zero**. Excluding the zero leaves
5 signs; the two-sided fair-binomial arithmetic is
`2 × (C(5,0) + C(5,1)) / 2^5 = 12/32 = 0.375`.
This is a reconstruction of the published calculation, not a new confirmatory
test or an endorsement of independence across the six pairs.

The lexicographically first label wins a modal tie, matching the runner.
There are **3 receiver probe cells with tied modes**: gpt-oss self b2, gpt-oss cross on qwen b0, qwen self b2.
No reference probe has a modal tie.
The result is consequently conditional on this declared deterministic rule.

## References and identity limits

Each arm has its own saved sender draws; none of the four sender raw arrays
are identical. Within each reader model, however, its sender modal vector is
identical across composers. Across the two reader models, the sender modal
vectors differ on **1 of 30 probes** in each composer row. Thus the reference
*kind* is matched, while the reference answer vector differs by reader. The
comparison is relative to the respective readers' references; it does not
compare both readers against one common criterion vector.

The present source briefs have **423/389/403 words** for gpt-oss and
**240/239/241** for qwen. Their stored word counts match a fresh whitespace
count, and the two arms in each composer row have matching brief IDs/lengths
and equal sampling effort. The arm files omit consumed-text hashes, prompt
bytes, model digests, decoding settings and per-draw seed metadata. Current
brief-text hashes and whole-file SHA-256 values are in the
[machine audit](selftransfer-audit.json); these fingerprint present files and
do not independently prove which exact text or model version a past call used.
The first two arms omit an explicit composer field; their composer is taken
from the current `briefs.json` metadata and the documented design.

## Review issues, without changing the scientific record

**Absence is not established by the reported p-value.** The measured row means
show no observed self advantage. A non-significant sign test does not establish
the absence of a population effect; a large p-value alone is insufficient
evidence for a null hypothesis. This follows the
[ASA statement on p-values](https://doi.org/10.1080/00031305.2016.1154108).
The 1.5 threshold is an observed row-mean rule here. Neither the prediction nor
this audit supplies a registered equivalence test and uncertainty calculation
that would turn satisfying that rule into evidence of equivalence.
The prediction explicitly records that the gpt-oss-composed row was already
observed before it was written; only the qwen-composed arms were still to be
drawn. The six-pair sign test is not specified in that prediction document.
It should not be described as a fully prospective confirmatory test of all
four arms.

**The prediction has two different sign conditions.** Its main sentence says
the sign is not consistently in self's favour; both positive row means satisfy
that wording. Its first outcome-table row instead requires “signs inconsistent”;
both positive row means fail that stronger condition. The table also lists
“self clearly worse in both rows” without defining “clearly.” The correct audit
result is that the numerical threshold and the main sentence's weaker sign
condition are met, while the table's inconsistent-sign condition is not met.
This ambiguity should be acknowledged in human review, not resolved by
rewriting the prediction after the data.

**The design limits the inferential unit.** The six pairs use two composers,
two reader models, one probe set, and the same sender reference within each
arm's three brief comparisons. Each paired comparison deliberately reuses one
brief across readers. The record does not establish six independent draws
from a population of composers, readers, tasks, or references. The sign test's
usual independent-sign assumption therefore cannot be treated as verified
population evidence. The +0.667 value is retained solely as the published
descriptive average; it is not a between-composer comparison or a newly pooled
effect estimate. No confidence interval, bootstrap, causal model, or new
confirmatory test is added by this audit.

The causal claim that the probes carry the signal is outside this arithmetic
audit. Reproducing the self-transfer counts does not supply an independent
test of probe attribution. This audit also supplies no measurement of `Φ`
and does not measure a system before and after its own compaction.

**Suggested wording for review:** “On these saved draws, self has 0.33 and
1.00 more diverged probes than cross in the two composer rows. Both absolute
row means satisfy the predicted 1.5-probe threshold. The descriptive means
show no self advantage; they establish neither equivalence nor the absence
of a self-transfer advantage beyond this design.” This is a proposal, not an
applied correction.

## Reproduction and exposure

Run `python3 tools/audit_selftransfer.py` to regenerate this draft and its JSON.
Run `python3 tools/audit_selftransfer.py --check` to compare both generated
artifacts byte-for-byte with a new computation. Run
`python3 tools/audit_selftransfer.py --self-test` for synthetic red/green checks
of the audit. These commands make no model calls. Every quantitative statement
above is derived from, or explicitly checked against, the linked source files;
the source result's means, six differences, SD and sign arithmetic are checked
independently of its stored summaries.

The Codex audit agent read `AGENTS.md`, `CONTRIBUTING.md`, the self-transfer
prediction and result, and selected analysis/metadata excerpts from
`headroom_riverside.py`, `metrics/noophorics/probes.py` and
`metrics/noophorics/divergence.py`. The latter excerpts include methodological
comments, so this is exposure to the experimental hypotheses and measurement
design. Probe texts, key values, individual answer labels and brief text were
processed programmatically for hashing and reconstruction without entering the
agent's visible context. No source specification, adjudication, other probe
content, or full `theory/` file was read for this audit. The agent must be
excluded as a naive subject of this self-transfer experiment or its exposure
declared. The parent task records the session in the repository exposure log.

---

*Prose: CC BY 4.0. Audit code: Apache-2.0.*
