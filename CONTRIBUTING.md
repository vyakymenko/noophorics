# Contributing

Noophorics is an experimental science or it is nothing. These rules exist to
keep it from becoming a blog with equations in it.

---

## The pre-registration norm

**This is the one rule that matters.**

Every experiment commits its hypothesis, design, and analysis plan **before any
data exists**. The git history is the pre-registration record — that is why it
is not negotiable and why it cannot be faked after the fact.

The flow:

1. **Commit 1** — `PREREGISTRATION.md` with hypotheses, predicted directions,
   analysis plan, significance criteria, declared limitations, and promotion
   criteria. No data. No results directory.
2. **Commit 2+** — the runner, the probe set, the source material.
3. **Commit N** — results. Raw output, then interpretation.

A pull request that introduces results and their hypothesis in the same commit
will be asked to split. Not as a formality: a hypothesis written after seeing
the data is a description, and describing your own data as if you had predicted
it is the mechanism by which fields accumulate false results.

**If the results contradict the pre-registration, the pre-registration stays
exactly as written.** Do not edit it. Add the finding. That contradiction is
the most valuable artifact the experiment produced.

---

## Adding a law

Laws go in [`theory/laws.md`](theory/laws.md) and must include:

- A one-sentence statement in the imperative form of a claim about the world.
- Why we expect it — a mechanism, not a vibe.
- **A refutation condition.** Concrete, and reachable by an experiment someone
  could actually run.
- A status tag and, ideally, the experiment that attacks it.

A conjecture without a refutation condition is not a law. It will be declined,
politely, and you will be invited to add one.

## Killing a law

Strike it through in place, link the experiment that killed it, and leave it
where it is. Refuted laws are never deleted — knowing what is false is the
larger part of the record, and a file that only contains survivors tells a
flattering lie about how the field got here.

---

## Reporting a measurement

Every number in `theory/` or `benchmarks/` must carry the full reporting
standard from
[definitions.md §7](theory/definitions.md#7-reporting-standard):

| Field | Why |
|---|---|
| Probe measure `P` (with content hash) | A2 — the frame |
| Reference `R`, its kind and its provenance | A2 — the other half of the frame *(v0.4)* |
| Regime: criterion-bearing or criterion-free | Decides whether *understanding* is licensed at all |
| Samples per probe `n` | JSD estimates are biased at small `n` |
| `D_prior`, `D_post`, `D_floor` | so `F*` can be recomputed and audited |
| `C(m)` and its unit | η is not comparable across units |
| Sender and receiver identity | model IDs, versions, decoding parameters |
| `Ĉ` for each party, separately | the asymmetry is data |

Two hard requirements:

- **Floor-correct everything.** An uncorrected `F*` is not wrong, it is
  unfinished, and it systematically understates fidelity.
- **Never clip `F*` below zero.** Antinoophors are real, informative, and
  invisible in clipped data.
- **Never report a fidelity without its reference.** *(v0.4)* `F*` takes a
  declared `R`. Where `R` is the sender the quantity is **replication**, and
  calling it understanding is the specific error
  [E-001](experiments/E-001-fluency-cost/FINDINGS.md) cost a live run to find.

Anecdotes are welcome in [`journal/`](journal/). They are not welcome in
`theory/`.

---

## Adding an experiment

```
experiments/E-0NN-short-name/
  PREREGISTRATION.md   # commit this first, alone
  source-spec.md       # the material being transferred
  probes.json          # the probe measure
  runner.py            # reproducible; must support --dry-run
  results/             # timestamped JSON, one file per run
  FINDINGS.md          # written after results, links back to the prereg
```

Runners must:

- support `--dry-run` so the pipeline can be verified without spending money,
- be seeded and deterministic in their analysis,
- write results as JSON containing every field of the reporting standard **and
  the raw messages verbatim**, so any claim can be recomputed from the record,
- depend on nothing beyond the standard library and `anthropic`.

---

## Automation: what may be looped

Experiments here are reproducible by construction — probe measures are data,
runners are seeded, laws carry kill conditions — so it is tempting to put the
whole cycle on a loop and let it run. Half of that cycle may be automated. The
other half may not.

| Automate freely | Never automate |
|---|---|
| Running an already-pre-registered protocol | Generating new hypotheses |
| Replication sweeps across model pairs, seeds, probe subsets | Promoting a law to `supported` |
| Collecting data and committing raw results | Writing `FINDINGS.md` without human review |
| Regenerating derived tables from committed results | Editing a pre-registration |

The line is **execution versus interpretation**, and it is not a matter of
taste.

An agent that generates a hypothesis, designs the test, writes the prompts,
runs it, and rules on whether it passed is a machine for confirming its own
priors at speed. It does not violate the pre-registration norm — every
hypothesis is still committed before its data — which is exactly why the norm
alone does not protect against it. The commit order stays honest while the
independence that made the order meaningful quietly disappears.

There is a second reason, specific to this field. A long-running loop is a
chain of **self-transfers**: each iteration hands its understanding to the next
through the narrow channel of a commit message and a journal entry. That is
[Problem 9](theory/open-problems.md), and [L5](theory/laws.md#l5) predicts
self-transfer should exhibit *maximal* phantom agreement — an agent has every
reason to believe its own summary preserved what mattered. An automated
research loop in noophorics is therefore not only an instrument of the science
but an instance of its central pathology, and should be instrumented as one:

- Log `Φ` across iterations where the loop hands work to itself.
- Treat a rising `Φ` across iterations as a stop condition, not a curiosity.

**Operational requirements** for any automated sweep:

- A hard cap on total runs, set in advance. Not a time interval — runs cost
  money and an interval-bounded loop has no bounded cost.
- Every run committed, including failures and void runs. A sweep that silently
  drops its failures is worse than no sweep.
- Gates verified on a **manual** first run before the sweep starts. Looping an
  instrument whose gates have never passed multiplies broken data.

## Keyed probes need independent adjudication

A probe whose ground truth is contestable is a defective probe, and its author
is the last person able to see that. `MERIDIAN-34`'s M33 was written by the
person who wrote the rules and set the key, read as obvious to him, and turned
out to be undetermined by the source text — found by outside readers, like every
other finding in this repository.

So: **before a keyed probe is committed, its key must be adjudicated by someone
who did not write it**, working from the source specification alone. A
disagreement means the probe is repaired or dropped, not argued.

Probes are the frame of reference (axiom A2). A frame nobody checked is not a
frame.

## Null results

Committed with the same prominence as positive ones, in the same format, in the
same place.

A field that only publishes wins converges on nonsense within a decade. The
concrete commitment: `FINDINGS.md` for a null result is written to the same
standard as one for a positive result, gets the same link from the law it
tested, and is never quietly dropped from a summary.

---

## Adversarial review

Where a bound is claimed, an attempt to violate it is expected **in the same
pull request**. Where an encoding is claimed to be optimal, an attempt to beat
it belongs alongside it.

Reviewers are asked to attack the measurement before the conclusion. The most
useful review this project can receive is *"your probe measure is inadmissible
and here is why."*

---

## Style

- Prose is edited for clarity, not for enthusiasm.
- Claims are stated with their confidence. "We conjecture", "we measured",
  and "we believe" are different words and are used differently.
- No result is described as proving anything.
- Terminology comes from [`lexicon.md`](lexicon.md). If you need a new term,
  add it there in the same PR.

---

## Licensing

By contributing you agree that:

- **code** contributions are licensed under **Apache-2.0**,
- **prose, theory, and experimental documentation** are licensed under
  **CC BY 4.0**.

Both licenses are in the repository root.

---

## Conduct

Attack measurements, designs, and claims as hard as you like. Do not attack
people. A contributor who kills one of our laws with a clean experiment has
done us the largest possible favour and should be thanked in the commit
message.
