# Can the four registers survive being pinned to a common length?

**Instrument check, before registration.** No hypothesis is tested here and none
may be read off it. It exists to answer whether E-001c is buildable at all,
after [E-001b was voided](../E-001b-fluency-factorial/VOID.md) by its cost
parity gate.

**Answer: yes, with a calibration problem that is measured rather than assumed.**

---

## What was replaced

E-001b instructed `Stay within 350 tokens` — a **ceiling**. A ceiling bounds
above and says nothing about below, so it cannot produce parity even when
obeyed, and it was not obeyed: every cell exceeded it, the fluent cells by 76%.

E-001c states a **two-sided word band** instead, and verifies realised token
cost afterwards. Words rather than tokens because a model cannot observe its own
tokenizer, and E-001b is direct evidence that it does not honour a token limit.
Nothing else in the prompts changed: the same five blocks, the same two varying
blocks, only the output block swapped.

## Result 1 — cost parity is achieved

Target 220 words (band 198–242), k=3 per cell, `gpt-oss:120b`, think=medium,
temperature 0.7:

| | fluent (A, B) | terse (C, D) | ratio |
|---|---|---|---|
| **E-001b**, ceiling instruction | 614.3 tok | 399.7 tok | **1.537** |
| **E-001c**, two-sided word band | 381.3 tok | 418.5 tok | **1.097** |

The 1.5× gap collapses to 1.10, and the *ordering reverses* — terse now costs
slightly more per message than fluent, which is what one expects once length is
the controlled variable and register is free to vary within it.

Parity across cell means: **1.160**, inside the 1.30 threshold. Parity across
individual messages: **1.320**, marginally outside it, driven entirely by
within-cell spread (a terse message at 474 tokens against a fluent one at 359).
The runner requires both readings to pass, so this configuration would still be
voided — see the calibration below, which is the reason it is close rather than
comfortable.

## Result 2 — the manipulation survives

This is the half that mattered more. Convergence bought by destroying the
distinction would be a null experiment with extra steps.

| structural marker | fluent | terse | ratio |
|---|---|---|---|
| mean sentence length (words) | 21.08 | 12.19 | 1.73 |
| connectives per 100 words | 2.15 | 0.61 | 3.52 |
| bullet fraction | 0.00 | 0.00 | — |

The two registers remain clearly separated at a common length: fluent writes
sentences nearly twice as long and uses subordinating connectives three and a
half times as often. Neither register produced bullet lists, so "terse" is
manifesting as short declarative sentences rather than as note form.

**These are proxies, not a validity check.** They distinguish prose from notes;
they do not establish that the *intended* style distinction is what survived.
Establishing that needs independent blind rating, and it is a precondition of
E-001c's registration, not something this script can supply. What the numbers do
rule out is the loud failure mode — pinning the length did not collapse the
registers into one.

## Result 3 — the model overshoots, systematically and in one direction

Six of twelve messages fell outside the ±10% band. **Every miss was long. None
was short.**

    target 220 words -> realised mean 238.2  (+8.3%)

A one-sided error is much better news than a symmetric one: it is a calibration
offset, not noise. Asking for 203 words should centre the realised distribution
on 220. That prediction is being measured at k=4 before it is relied on, because
predicting a calibration and assuming it are different things, and this
experiment has already spent a day on the difference.

Compliance at 50% also sets the price of rejection sampling on *words*: roughly
two compositions per accepted message. Affordable — and worth contrasting with
rejection sampling on *cost*, which the [voided
run](../E-001b-fluency-factorial/VOID.md) showed has acceptance **zero** for
every band, because the two families' realised costs were disjoint.

## What E-001c needs before it can be registered

1. **The calibration confirmed**, not predicted. In progress.
2. **Independent blind rating** that the four cells still instantiate the
   intended registers at a pinned length. The structural markers are not
   sufficient and are not offered as sufficient.
3. **A decision on the parity reading.** E-001b's pre-registration said "across
   cells" and its runner compared messages. E-001c will state one, require
   both, and evaluate them at composition — where their inputs already exist —
   rather than after the sweep.
4. **M33 repaired or removed.** `MERIDIAN-34` is superseded for new experiments
   ([SENSITIVITY-M33](../E-001b-fluency-factorial/SENSITIVITY-M33.md)); a probe
   whose key the source does not determine should not be inherited.

Registration follows those. Not before.

---

*This document is licensed CC BY 4.0.*
