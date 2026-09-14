# Qwen register feasibility: instrument readout

**2026-09-14 (UTC start date). Collection complete.**

The complete two-judge corpus result is **available**. Recorded HTTP rating attempts: **104 / 104** (fixed cap); invalid or indeterminate attempted responses: **0**. Corpus messages missing at least one valid rating: **0 / 48**.

Direct joint acceptance across the archived corpus: **32 / 48**. The judges disagreed on **16 / 48** messages.

These are descriptive counts for this finite archived corpus and these configured judges. This readout introduces no scientific hypothesis, law, significance test, or population acceptance estimate.

## Calibration

| Judge | Status | Controls attempted / planned | Valid responses | Correct controls |
|---|---|---:|---:|---:|
| `gpt-oss:120b` | passed | 4 / 4 | 4 | 4 |
| `llama3.3:70b` | passed | 4 / 4 | 4 | 4 |

Every control must be correct before that judge's corpus calls are eligible. A failed or missing control excludes its corpus ratings; it does not authorize a replacement judge or retry. These procedural controls are not a validated benchmark, and passing them does not establish correctness on borderline passages.

## Corpus counts

| Cell | Expected register | Messages | In word band | `gpt-oss:120b` expected | `llama3.3:70b` expected | Both expected | Disagreements | Direct joint acceptance |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A | connected prose | 12 | 11 | 7 | 12 | 7 | 5 | 7 |
| B | connected prose | 12 | 12 | 8 | 12 | 8 | 4 | 8 |
| C | list | 12 | 12 | 12 | 12 | 12 | 0 | 12 |
| D | list | 12 | 11 | 12 | 5 | 5 | 7 | 5 |

The word band is 182–231 whitespace-separated words. Direct joint acceptance counts the same messages passing the band and both judges' expected register; it is the observed intersection, not a product or minimum of marginal counts. Expected-register counts use valid observed ratings. Both-expected and disagreement counts use only messages with two valid ratings. A complete joint count is unavailable for a cell with any missing rating, or if either judge fails calibration.

### Missing data

| Cell | `gpt-oss:120b` valid | `gpt-oss:120b` missing | `llama3.3:70b` valid | `llama3.3:70b` missing | Two valid | Any missing |
|---|---:|---:|---:|---:|---:|---:|
| A | 12 | 0 | 12 | 0 | 12 | 0 |
| B | 12 | 0 | 12 | 0 | 12 | 0 |
| C | 12 | 0 | 12 | 0 | 12 | 0 |
| D | 12 | 0 | 12 | 0 | 12 | 0 |

Missing includes unattempted, skipped, invalid, and indeterminate corpus ratings. An invalid response never becomes a list verdict. A reserved call interrupted before a definitive response stays missing and is never resent.

## Scope and provenance

All 48 archived compositions were fixed before the register outcomes were collected; their length outcomes already existed. Every composition is included, including those outside the word band. There is one draw per eligible message and judge, with no retries or replacement compositions.

The configured regimes differ: `gpt-oss:120b` uses `think=medium`; `llama3.3:70b` omits the thinking field. Both use temperature 0.7. These are observations from these particular judges, not a controlled comparison of model ability. Different model lineages do not establish independent errors. The historical `qwen3.5:35b` composer digest is unknown.

Register acceptance does not test factual accuracy, contrastiveness, transfer, fidelity, phantom agreement, or usefulness. E-001c remains void, and its pre-registration is unchanged. Scientific interpretation requires human review; this file is a mechanical instrument readout.

Collection started: `2026-09-14T07:42:05.627766+00:00`. Plan committed before ratings: `544e6fe`. Frozen runner commit: `d0de1a3`.

| Pinned input | SHA-256 |
|---|---|
| Archived source JSON | `cfbd5d776cec1bb430f0bb9ec82b5d1a08f2c0a22c5dff43520a7f1fb8f5d0f9` |
| Plan JSON | `8709fb5c79ed1c7d306ef15dac4a42d2e860fdd34359fd0f8126922d5cdb4f6c` |
| Runner | `32a5120cb6c410fff2f0c9737fc71c353fd2348b4240d5722dabd954900757fe` |
| Absolute question | `44571477c1c92e7ce9526c707a88fc08eda3075fa87459871153f1f7cdcb6590` |
| `gpt-oss:120b` weights | `a951a23b46a1f6093dafee2ea481d634b4e31ac720a8a16f3f91e04f5a40ecd9` |
| `llama3.3:70b` weights | `a6eb4748fd2990ad2952b2335a95a7f952d1a06119a0aa6a2df6cd052a93a3fa` |

Sources: [prospective plan](../probes/qwen-register/PLAN.md), [machine-readable plan](../probes/qwen-register/plan.json), [archived source](../experiments/E-001c-fluency-length-controlled/floor-by-register-qwen.json), [result manifest and item identities](../probes/qwen-register/results/20260914T074205Z/manifest.json), [saved summary](../probes/qwen-register/results/20260914T074205Z/summary.json), [raw call records](../probes/qwen-register/results/20260914T074205Z/calls).

Every count above is recomputed from checked raw call records, not copied from the saved summary. The manifest binds item identities and text hashes; the runner checks them alongside the source, question, plan, model, and runner identities.

Recompute from the saved raw records, starting at the repository root:

```bash
python3 tools/rate_register.py --out probes/qwen-register/results/20260914T074205Z --summarize
python3 tools/report_register.py --out probes/qwen-register/results/20260914T074205Z --report research/2026-09-14-register-feasibility.md --check
```

---

*This document is licensed CC BY 4.0.*
