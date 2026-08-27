# Prediction: does RIVERSIDE-30's probe-attributable structure hold for a second reader?

**Recorded 2026-08-20, before `qwen3.5:35b` answers any RIVERSIDE probe.**

## What is at stake

[The headroom run](RESULTS-headroom.md) found the claim this session leans on:
on `RIVERSIDE-30`, divergence is a property of the **probe** (8 probes diverge on
every brief, inter-brief correlation `+0.849 / +0.805 / +0.666`), where on
MERIDIAN it was a property of the **brief** (intersection 0, correlation ~0).
That is what makes pairing buy ×2.58 and what every downstream power claim rests
on.

It was measured on **one reader**. Today's other finding is that reader-specific
structure is real: on MERIDIAN the wobble/divergence association is strong for
`gpt-oss` and untestable for `qwen`. So the structure that unblocked the
arithmetic may be `gpt-oss`'s, exactly as the anti-correlation turned out to be.

## The prediction

**`qwen3.5:35b`'s diverged set on `RIVERSIDE-30` will overlap `gpt-oss`'s
substantially — Jaccard ≥ 0.4 on the union of always-diverging probes.**

If divergence is probe-attributable it is a property of the measure and should
survive a change of reader. If it is reader-attributable it will not, and
`qwen`'s set will be a small subset driven by its higher ability, which is
exactly what happened on MERIDIAN (`{X11, X26}` ⊂ `gpt-oss`'s nine).

| outcome | reading |
|---|---|
| **Jaccard ≥ 0.4, and qwen also clears the gate** | Probe-attributable structure is a property of `RIVERSIDE-30`, not of `gpt-oss`. The ×2.58 pairing gain and every MDE derived from it stand, and RIVERSIDE is the programme's instrument. |
| **qwen clears the gate but the sets barely overlap** | The rate is real, the *structure* is reader-specific, and pairing gains must be re-derived per reader. The MDEs published today are then `gpt-oss`-only. |
| **qwen diverges on ≤ 3** | Saturated for this reader, as MERIDIAN was. RIVERSIDE would be `gpt-oss`'s instrument and not the programme's, and [RESULTS-headroom](RESULTS-headroom.md) would need striking. |

The eight always-diverging probes are `T01 T02 T10 T11 T14 T16 T17 T19`, fixed
here so the overlap cannot be computed against a set chosen afterwards.

## Cost and limits

`qwen` at the measured **53.5 s/call**: sender 300 calls plus three receivers at
300 each = **1 200 calls ≈ 18 hours**.

Two readers still cannot estimate a variance component
([D-STUDY](../meridian-ix16/D-STUDY.md) obstacle 3); this tests whether the
structure survives a reader, not how much of it is reader variance. The briefs
are `gpt-oss`-composed, so a divergence difference confounds *reading* with
*being read something written by the other model* — which is the asymmetry E-003
would isolate and cannot, for reasons recorded in [L2](../../theory/laws.md#l2).

---

*This document is licensed CC BY 4.0.*
