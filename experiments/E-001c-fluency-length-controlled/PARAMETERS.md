# E-001c — run parameters, and the one the pre-registration forgot

**Date:** 2026-08-03 · **Data on disk at commit time:** none.

E-001b's equivalent file opens *"the pre-registration fixes `n`"*. E-001c's does
not, and that is a gap rather than a delegation. This file closes it before any
datum exists.

## `n = 30` draws per probe

Inherited from [E-001b §2](../E-001b-fluency-factorial/PREREGISTRATION.md),
which fixed 30 after E-001's `n = 6` was found to sit below the estimator's
usable range — roughly 0.11 of error at that size, against a gate the design
needs to be tighter than.

**It is load-bearing, and not only for precision.** The registered
unresolved-probe rule marks a probe unresolved when its modal answer wins by
fewer than `n / 4` draws. At `n = 30` that is a margin of 7.5; at `n = 16` it
would be 4. So `n` decides how many probes the gate removes, which makes it
exactly the kind of parameter that must not be chosen after seeing which probes
it removes. It is chosen here, from the predecessor, with no data in existence.

Recording it is not an amendment: the pre-registration does not state `n`, so
there is nothing to amend. It states `k = 8` and `n_c = 9` and is silent on the
third. The silence is the defect;
[AMENDMENT-001](AMENDMENT-001.md) has already consumed the cap, and filling a
silence is not the same act as contradicting a sentence.

## Provider and model

`gpt-oss:120b` at `think=medium`, served locally by ollama, `temperature = 0.7`,
both roles. Fixed by the pre-registration, not chosen here. E-001b's
[PARAMETERS](../E-001b-fluency-factorial/PARAMETERS.md) records the measurement
that selected it — perfect accuracy on MERIDIAN-34 at medium effort, against
0.882 with four errors for `claude-opus-4-8`, which failed the gate.

That measurement has since been replicated by an experiment that was not looking
for it: [E-004](../E-004-disagreement-detector/VOID.md) put `claude-opus-4-8` at
0.909 on the same measure and 0.733 on a second one, against 1.000 and 0.967 for
`gpt-oss:120b`. Two independent runs, the same ordering.

## Register raters

`codex` and `claude-opus-4-8`, named in
[PREREGISTRATION §4](PREREGISTRATION.md). `codex` authenticates through a
ChatGPT subscription and `claude-opus-4-8` through an API key, so the two judges
have different providers, different billing and no shared point of failure. A
quota exhaustion on one cannot silence the other.

## What this run costs

```
draw calls        35 700   35 conditions x 34 probes x 30 samples
elicitation       19 584   32 messages x 2 parties x 34 probes x 9
compositions          ~40  register-filtered, ~3 attempts per fluent message
judge calls           ~80  two raters per composition
                  -------
                  ~55 300 model calls
```

At the 3.5–5.0 s per call this machine has been observed to sustain, **54 to 77
hours** of continuous local GPU. The run is resumable: the sample cache is
written per condition and `Cache.get` returns a cell only when its length equals
the requested `n`, so an interruption costs the cell in flight and nothing else.

---

*This document is licensed CC BY 4.0.*
