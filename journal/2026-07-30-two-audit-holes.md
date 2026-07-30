# 2026-07-30 — Two audit holes, found by an agent sent to argue about definitions

Both were found while an adversarial panel was checking arithmetic for an
unrelated decision. Both are verified here by independent recomputation. Neither
was found by anyone reading the repository, including its author, over three
days of doing exactly that.

---

## 1. The evidence for the programme's central finding was not in the repository

[E-001's FINDINGS](../experiments/E-001-fluency-cost/FINDINGS.md) is the document
that forced the v0.3 rewrite: it established that the headline quantity rewards
mimicry, and every subsequent correction descends from it. Line 139 says:

> every number above is reproducible from `.sample-cache.json`, now tracked.

It was not tracked. It was committed in `0345350`, deleted in `6c59143`
("v0.3 runner"), and was absent from both the working tree and `git ls-files`.
The only tracked E-001 result is `results/E-001-20260728T184446Z.json`, which is
`void: true` with no conditions composed.

So for some days the repository asserted the reproducibility of numbers whose
inputs it did not contain. The `.gitignore` even records that excluding caches
had been "an audit hole" — the lesson was written down, and then the file was
deleted anyway by a commit about something else.

**Restored** to `experiments/E-001-fluency-cost/sample-cache.json`, without the
leading dot that hid it from `ls` and invited the exclusion. Every published
figure recomputes from it exactly: `D_prior 0.5625`, floors `0.0098 / 0.0091`,
`F* 0.7701 / 0.9082`.

The leading dot is not an incidental detail. A file named `.sample-cache.json`
is invisible by default, matches habitual ignore patterns, and reads as
machinery rather than as evidence. Evidence should be named like evidence.

## 2. The `CEILING` gate cannot fail

Every experiment since E-001 carries a gate requiring the `CEILING` arm — an
agent given the full source specification — to reach fidelity above 0.70. Its
purpose is to establish that the probe measure is answerable from the source at
all, so that a low receiver score means a bad transfer rather than an impossible
task.

The runners construct it as:

```python
contexts = {"sender": spec, "PRIOR": "", "CEILING": spec}
```

Same model. Same context. `CEILING` **is** the sender, sampled again.

Measured on E-001's restored cache: **25 of 25 draw sequences bit-identical**,
mean `JSD(sender, CEILING) = 0.0000`. Measured on E-002b's live cache: 32 of 33
identical, `JSD = 0.0010`, gate value **1.0000** against a threshold of 0.70.

The gate compares an agent to a copy of itself and asks whether they agree. It
has passed in every run that reported it, and it could not have done otherwise.

It is also pointed the wrong way. Fidelity is a *gap-closure toward the sender*,
so a "ceiling fidelity" of 1.0 says the reference agrees with the sender — not
that the reference is correct. On E-001's cache the `CEILING` arm is **wrong on
2 of 25 probes** (accuracy 0.920) while scoring a perfect 1.0 on the gate that
was supposed to certify it.

**Not repaired in this entry, deliberately.** E-002b is running under the
pre-registered gate list and changing a gate mid-run is the failure this
programme has already recorded. The gate stays, its vacuity is now on the
record, and the successor's registration will replace it with two things it
should have been all along: the reference's **accuracy against the key**, and an
explicit **independence check against the sender** that this construction would
fail outright.

---

## Why both were missed

Neither is subtle. Both are visible in four lines of code and one `git ls-files`.

They were missed because the repository was being read by people looking for
what it says, and found by an agent instructed to attack a claim, which had to
reconstruct the evidence to do so. Reading a document tells you what it asserts.
Trying to recompute its numbers tells you whether it can.

That distinction is the programme's own subject, and it keeps arriving as a
lesson about the programme rather than a result from it.

---

*This document is licensed CC BY 4.0.*
