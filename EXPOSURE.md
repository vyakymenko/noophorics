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
| 2026-08-04 (extended again) | `claude-opus-5` | `theory/open-problems.md` 12–14, and **authored Problem 15** | The open-problem set. It knows which defects the programme considers unsolved, including the one it raised — so it cannot serve as an independent judge of whether Problem 15 is real. Twelve further subagents of the same model read the same material designing E-001c's successor; their designs are **not** committed, and none was adopted. |
| 2026-08-07 | `claude-opus-5` | The `MERIDIAN` source specification in full, and **authored the 16 probes of `MERIDIAN-IX16` and their keys** | That measure, totally and irrecoverably. It cannot be a subject against `MERIDIAN-IX16`, and it cannot judge whether those probes are good — the keys and the probes have the same author. `MERIDIAN-33` and `MERIDIAN-34` items remain unread, so those two are still clean. |
| 2026-08-10 | `claude-opus-5` | **Authored `X17`–`X32` and their keys**, and the `predicted_discriminating` prediction they carry | `MERIDIAN-IX32` entire. **This row was missing until 2026-08-18.** `157b80f` took the probe file from 16 probes to 32 and did not touch this file, so for eight days the log recorded exposure to half the measure it should have. Dated to the commit rather than to its discovery, because the exposure happened when the probes were written. |
| 2026-08-18 | `claude-opus-5` | All 32 probes with keys and tags; every sender pass and the 12-message divergence data; `RETRACTIONS.md`; `theory/open-problems.md` 11–15; `AGENTS.md` | `MERIDIAN-IX32` as subject **and as judge**. It computed the prompt clustering behind [retraction 15](RETRACTIONS.md) and cannot independently assess whether that retraction is right. It has also now seen the divergence outcomes probe by probe, so it cannot serve as a receiver against this measure. |
| 2026-08-19 (same session, extended) | `claude-opus-5` | `theory/prior-art.md` in full and **authored its §11**; `PRINCIPIA.md` A2 and the falsification criteria; `theory/definitions.md` §7; the complete `qwen3.5:35b` receiver run probe by probe | Everything the previous row names, plus the **prior-art set**: it now knows which of this programme's constructs are already owned by other fields, so it cannot judge whether a novelty claim here is novel. It authored [retraction 16](RETRACTIONS.md) against its own finding of the previous day and the §11 that supersedes it, which is the weakest possible provenance for both. As in the 2026-08-04 note, **the exposure grew because the agent kept working** — this row exists because that lesson was written twice already and drifted anyway. |

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

**Still not read:** `lexicon.md`, and
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

**And the lesson did not take.** The paragraph above was written on 2026-08-04.
Six days later `157b80f` doubled `MERIDIAN-IX32` from sixteen probes to
thirty-two, by the same model, and no row was added — the file went on
describing exposure to sixteen probes while the measure held thirty-two, for
eight days, through four commits that reasoned about those probes. It was found
on 2026-08-18 by an agent reading the log to add its own row, which is luck
rather than a mechanism. Nothing checks this file: `check_counts.py` compares
numbers to sources and there is no number here, and the probe count is not
derivable from a table of prose. The 2026-08-04 caution therefore stands twice
over — this log is a lower bound written by the party with the incentive to
under-report, and it is now demonstrated to drift as well.

**A caution about this row.** It was written by the agent it describes, which is
the weakest possible provenance for a record of contamination — the party with
the incentive to under-report is the party holding the pen. It should be read as
a lower bound on what was seen, not an inventory.

---

*This document is licensed CC BY 4.0.*
