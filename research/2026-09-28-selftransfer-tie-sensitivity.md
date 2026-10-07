# Draft sensitivity audit: modal ties in RIVERSIDE-30 self-transfer

**Reviewed 2026-10-07.** This note's finding that the `gpt-oss`-composed row
mean is 0 under another admissible tie choice is ground (c) of
[retraction 22](../RETRACTIONS.md). The note itself is unchanged.

**2026-09-28 — retrospective check for human review.** This note analyzes the
saved draws behind the [self-transfer result](../probes/riverside-30/RESULTS-selftransfer.md)
and its [arithmetic audit](2026-09-09-selftransfer-audit.md). It adds no model
responses, changes no registered prediction, and makes no formal correction.
The four saved arms are labelled instrument data in their source files.

The published runner chooses the lexicographically first answer when modal
counts tie. That rule is deterministic and remains the published calculation.
Across **360 receiver probe cells**, three have a
two-way modal tie; none of the **120 sender probe cells**
has one. The sender modal reference therefore stays fixed. For each of
the three receiver ties, one co-mode matches that reference and the published
choice does not. The tied answer labels and probe content are not reproduced
here.

Choosing either co-mode in each tied cell yields exactly
**8 modal configurations**. These are
alternative scoring resolutions of the **same saved draws**, not repeated
samples or equally likely outcomes.

| Composer row | Published self − cross differences (b0, b1, b2) | Published row mean | Possible row mean with any tied co-mode |
|---|---|---:|---:|
| `gpt-oss:120b` | -1, +1, +1 | 1/3 | 0 to 1/3 |
| `qwen3.5:35b` | 0, +1, +2 | 1 | 2/3 to 4/3 |

One tied `gpt-oss` self-reader cell can lower its b2 difference from +1 to 0,
making that row mean **0** instead of **+1/3**. In the qwen-composed row, a
tied cross-reader b0 cell can raise the difference from 0 to +1, while a tied
self-reader b2 cell can lower it from +2 to +1. That row mean ranges from
**+2/3 to +4/3**. No admissible tie choice produces a negative row mean.

**Every configuration keeps both absolute row means below the published
1.5-probe descriptive threshold.** The strictly positive sign of the
`gpt-oss`-composed row is sensitive to the tie rule; under another admissible
choice it becomes zero. The qwen-composed row remains positive. This check
does not establish equivalence, absence of a self-transfer effect, a cause for
the differences, or any population result. There is no new significance test.

The [machine summary](selftransfer-tie-sensitivity.json) lists all eight
configurations as co-mode **indices and divergence counts**, without answer
labels. It records source hashes and the exact threshold outcome for each
configuration. The tool first runs the existing raw-draw arithmetic audit and
requires its published modal result to reproduce before enumerating alternatives.

Recompute from the repository root without model calls:

```bash
python3 tools/audit_selftransfer_ties.py --check
python3 tools/test_audit_selftransfer_ties.py
```

**Exposure:** this Codex audit read the research index, register instrument
plan/readout, self-transfer audit, domain drafts and analysis code, including
selected prediction wording. The original prediction, result, measure, briefs
and raw answer arrays were also processed programmatically; probe text, keys,
individual answers and brief text were not printed into the agent context.
This working context should not be treated as a naive experimental subject.
The session belongs in [EXPOSURE.md](../EXPOSURE.md).

---

*Prose: CC BY 4.0. Audit code: Apache-2.0.*
