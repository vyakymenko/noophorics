# 2026-07-28 — First live run: void, and the reason is worth keeping

E-001 ran against the API for the first time and died. Full record in
[AMENDMENT-001.md](../experiments/E-001-fluency-cost/AMENDMENT-001.md); this
entry is for what it means.

---

## What happened

The sender answered all 34 probes, then a safety classifier declined to let it
write the handover brief. Category `cyber`, blocked before generation, on a
fictional rulebook about fellowship eligibility.

Ablation localized it: neither the spec nor the compose prompt triggers the
classifier alone. The interaction does. A rulebook about who is *eligible*,
*exempt*, and barred "regardless of every other rule", plus a request to write
instructions letting someone else decide cases while *seeing nothing except
what you write* — that reads, from the outside, like authoring a guide to
getting around an access-control system.

Reskinned the domain to manuscript handling, one-to-one, keys preserved.
Verified it composes. Recorded as an amendment to the instrument, not a change
to the hypotheses.

---

## The near miss

The classifier blocked **both** conditions, so the run died loudly and I went
looking for the cause.

Suppose it had blocked only the contrastive one.

The contrastive prompt is the one that asks for exclusions, overrides, and
"what does NOT follow from what" — measurably closer to the pattern that
triggered the block. It is entirely plausible that the narrative brief composes
and the contrastive brief refuses. In that world the runner does not crash.
`sender.compose()` raises only on refusal; had I instead written the tolerant
thing — return empty string, log a warning, continue — the contrastive
condition would have received an empty message, scored `F* ≈ 0`, and E-001
would have reported a large, clean, statistically significant result in the
direction **opposite** to my hypothesis. With a permutation test and a p-value
attached.

I would have written that up. It would have looked like evidence.

The only thing standing between this repository and a fabricated finding was a
`raise` I put in for tidiness rather than for safety. That is not a margin I
want to rely on twice.

**Concrete consequence:** any condition whose message failed to generate must
mark the whole run void, never contribute a zero. Adding this as an explicit
gate, not leaving it to an exception that happens to propagate.

---

## The finding worth keeping

> A measurement instrument can be blocked by the safety behavior of the system
> it measures — and the block can be silent, asymmetric, and shaped like a
> result.

This generalizes past our setup. Any evaluation harness that varies prompt
*style* across conditions is varying classifier surface across conditions.
Refusals are not distributed uniformly over phrasings; contrastive,
boundary-focused, adversarial-sounding phrasings will attract them more than
smooth expository ones. An eval comparing such conditions is partly measuring
the classifier, and if it handles refusals by scoring them as failures rather
than as missing data, it is measuring the classifier while believing it is
measuring the model.

I do not know how large this effect is in published evaluation work. I do know
our own field has to treat refusal as **missing data**, never as a zero, and
I am writing that into the method rather than trusting anyone to remember it.

---

## Cost of the lesson

204 API calls discarded, because composition ran after the probe sweep instead
of before it. Fixed: compose first, and cache raw draws to disk so a failure
resumes instead of restarting.

Filed under things that were obvious in retrospect and that I did not think
about while writing a runner I expected to work.

---

## Still open

The prompt-bias problem from the [founding entry](2026-07-28-founding.md) is
untouched and is now the largest remaining threat to E-001. Both generation
prompts are mine, and L5 is a hypothesis I find satisfying. Today's near miss
was a *different* mechanism producing the same outcome — a spurious result in
my preferred direction — which does not make me feel better about the one I
already knew about.
