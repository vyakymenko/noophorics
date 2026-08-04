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
| 2026-08-04 (extended, same session) | `claude-opus-5` | E-002c `PREREGISTRATION.md` §1–3 and `FINDINGS.md` §1–6, including β and the sender/receiver split; `PRINCIPIA.md` §4–5 and the falsification criteria; `theory/laws.md` L5 and L6 in full; `theory/prior-art.md`; `RETRACTIONS.md` | The E-002 line as well as the E-001 line, and **L5/L6 as a subject**: it has read the laws it would be measured against. Also knows E-002b's withdrawn pull-quote and why it was too strong. |

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

**Still not read:** `theory/open-problems.md` beyond its count, `lexicon.md`, and
**no probe file** — neither `MERIDIAN-34`'s nor `MERIDIAN-33`'s items were ever
loaded into this agent's context. Exposure to the **probe measures** is therefore
nil, and a future experiment may still use `claude-opus-5` against MERIDIAN as a
subject.

Everything else is now exposed. The second row was added when writing
[the paper draft](paper/) required reading the theory and the E-002 line, which
the first row's own scope did not cover. That is worth naming: **the exposure
grew because the agent kept working, and the record had to be revised rather
than written once.** An exposure log that is only written at the end of a
session records the session the author remembers, not the one that happened.

**A caution about this row.** It was written by the agent it describes, which is
the weakest possible provenance for a record of contamination — the party with
the incentive to under-report is the party holding the pen. It should be read as
a lower bound on what was seen, not an inventory.

---

*This document is licensed CC BY 4.0.*
