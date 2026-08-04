# Agent exposure

[AGENTS.md](AGENTS.md) requires an agent that works in this repository to record
that it did, because `gpt-oss:120b`, `qwen3.5:35b`, `claude-*` and `codex` appear
here both as tools and as **subjects of measurement**:

> An agent that has read `theory/` or an experiment's hypotheses is contaminated
> as a subject of that experiment: it has seen what it is supposed to be measured
> against. […] An experiment that later uses your model must either exclude you
> or declare the exposure.

Until 2026-08-04 the rule had no artifact. It said *record that you did* and
there was nowhere to record it, so nothing was recorded — a norm with no file is
a norm with no evidence, which is the shape of gate this repository exists to
distrust. This is the file.

**What it is for.** Before an experiment names a model, check this table. If the
model appears here against material that experiment depends on, either exclude
it or declare the exposure in the pre-registration. This file does not decide
which; it only makes the choice visible.

---

## Log

| date | model | read | contaminates |
|---|---|---|---|
| 2026-08-03 – 2026-08-04 | `claude-opus-5` | AGENTS.md; E-001c `PREREGISTRATION.md` in full, including H1–H4, the gate table and the analysis plan; `PARAMETERS.md`; `AMENDMENT-001.md`; `runner.py`; `feasibility.py`; E-001b `prompts.py`, which is **the four cell prompts themselves**; E-001b `DEFECT-001.md` | E-001c and any successor, as composer, rater or subject. Knows the fluency × contrastiveness manipulation, the register the filter looks for, and that H4 is a predicted null. |

### Notes on the 2026-08-04 entry

The work was the diagnosis recorded in
[DEFECT-001](experiments/E-001c-fluency-length-controlled/DEFECT-001.md),
[CALIBRATION-001](experiments/E-001c-fluency-length-controlled/CALIBRATION-001.md)
and [VOID.md](experiments/E-001c-fluency-length-controlled/VOID.md).

**It composed messages using the live cell prompts.** Twenty-two compositions
across cells A and C, at `gpt-oss:120b` — so the *composer* was not contaminated,
but the agent choosing what to compose and reading the results had seen the
hypotheses. Those messages are instrument data
([CALIBRATION-001](experiments/E-001c-fluency-length-controlled/CALIBRATION-001.md))
and none entered an experiment.

**Not read:** `PRINCIPIA.md`, `theory/laws.md`, `theory/open-problems.md`,
`lexicon.md`, `RETRACTIONS.md` beyond single quoted lines, and no probe file —
`MERIDIAN-34`'s items were never loaded into this agent's context. So exposure
to the **probe measure** is nil, and a future experiment may use `claude-opus-5`
against MERIDIAN as a subject. Exposure to **E-001's fluency line** is total.

**A caution about this row.** It was written by the agent it describes, which is
the weakest possible provenance for a record of contamination — the party with
the incentive to under-report is the party holding the pen. It should be read as
a lower bound on what was seen, not an inventory.

---

*This document is licensed CC BY 4.0.*
