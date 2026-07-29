# E-001b — run parameters, and why they are not an amendment

**Date:** 2026-07-29 · **Data on disk at commit time:** none.

The pre-registration fixes `n`, the probe measure, the budget, the floor
method, `ε`, and the analysis plan. It records the **model per run** rather
than fixing one. This file records the remaining run parameters, chosen before
any data existed, applied identically to every cell.

## Provider and model

`gpt-oss:120b`, served locally by ollama. Chosen by **measurement against our
own gate**, not by published benchmarks:

| candidate | accuracy on MERIDIAN-34 | errors | s/probe | gate |
|---|---|---|---|---|
| `gpt-oss:120b` think=low | 0.912 | 3 | 2.2 | **fail** |
| `gpt-oss:120b` think=medium | **1.000** | **0** | 4.8 | **pass** |
| `gpt-oss:120b` think=high | 1.000 | 0 | 12.2 | pass |
| `qwen3.5:35b` think=low | 1.000 | 0 | 17.3 | pass |
| `claude-opus-4-8` | 0.882 | 4 | ~2 | fail |

Two things worth recording. **Both local models out-decided the hosted one**
on this task. And gpt-oss's three low-effort errors were all interaction probes
— M19 (R9+R8), M25 (R10→R3), M33 (R5+R6) — which vanish at medium. MERIDIAN-34
turns out to discriminate reasoning depth specifically, which is fortunate
instrument design and was not deliberate.

`gpt-oss:120b` at medium is taken over `qwen3.5:35b` purely on throughput: same
perfect gate, 3.6× faster.

## `think = "medium"`

Not a free knob. At `think=False` this model returns an **empty response** —
the same failure class Claude Opus 5 shows with thinking disabled. Turning
reasoning off is a mode with its own pathologies, not a neutral setting, and
the agent raises on empty output rather than coercing it into a verdict.

Medium is the lowest setting that clears the sender gate.

## `temperature = 0.7`

**This is required by the pre-registered analysis plan, not added to it.**

The plan specifies a permutation-null floor. At `temperature = 0` the model is
deterministic, every per-probe distribution collapses to a point mass, and the
floor is identically zero — which would silently return the programme to
uncorrected fidelity, the exact defect [v0.2](../../metrics/validation/synthetic.py)
was built to fix. A temperature producing a non-degenerate floor is what makes
the stated plan operable.

The realised self-divergence at 0.7 is reported with the results. If it comes
back near zero anyway, that is stated loudly rather than passed over — the
founding journal already made that promise once about `D_floor` and the
programme was slow to keep it.

## Wall clock

~35 hours. Measured, not estimated: 3.55 s/call at one worker and 3.78 s at
four. **Concurrency does not help** — local inference is GPU-bound, so parallel
workers share one accelerator and add overhead. That is the opposite of the
hosted-API case and had to be measured rather than assumed.

The run is resumable: the sample cache is atomic and tracked, so an interruption
costs nothing but time.

## What is deliberately unchanged

`n = 30`, `k = 8`, the hypotheses, the gates, the analysis plan, the factorial
structure, and the amendment budget — one of two remains unspent.
