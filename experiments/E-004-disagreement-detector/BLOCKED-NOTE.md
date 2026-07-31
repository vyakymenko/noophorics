# The third arm is blocked, and what happens if it stays blocked

**Written 2026-07-31 at 38% collection, before any analysis and before the
question is live.** The decision below is made now precisely because it will be
inconvenient later.

---

## The state

E-004 registers **three models**: `gpt-oss:120b` and `qwen3.5:35b` locally,
`claude-opus-4-8` via API, giving three unordered pairs across two providers.

The local two are collecting normally. The third arm failed on its first call:

```
anthropic.BadRequestError: 400
Your credit balance is too low to access the Anthropic API.
```

That is not a defect to repair. It is a billing state, and it is the
maintainer's to resolve. The queue entry has moved to `blocked` in
`automation/queue.json` with its reason, so the loop does not burn a run slot
re-discovering it every pass.

## The decision, made in advance

**If the third arm never runs, E-004 is VOID. It does not become a two-model
experiment.**

Its own [amendment policy](PREREGISTRATION.md#6-amendment-policy) says so
without ambiguity — *"Not permissible: changing the detector, the **models**,
the hypotheses, the gates, or either probe measure after collection begins"* —
and collection began on 2026-07-31 at 10:58.

There is no reading under which a two-model run satisfies this registration:

- **The design is three pairs, not one.** With two models there is a single
  pair, and the Fisher combination across cells that H1 is tested with has one
  cell per measure instead of three.
- **H3 becomes untestable in the way that matters.** Symmetry asks whether the
  detector finds errors of *both* members. One pair can show that for one pair,
  which is exactly the single-comparison weakness that made the
  [motivating observation](../../journal/2026-07-30-cross-sender-disagreement.md)
  unusable in the first place.
- **Two of the two are open-weight local models** that may share training data.
  Shared bias is the pre-registered standing threat, and the cross-provider arm
  was the only thing in the design positioned to detect it.

Reporting a two-model result under E-004's id would be describing an
**unregistered design**, and a launch built on this repository's audit record
cannot survive that accusation — correctly.

## Why this is written now rather than then

Three days ago this programme voided a run on a cost-parity gate and noticed,
while writing it up, that the gate's ambiguity had been spotted *after* knowing
which way it would resolve. It resolved the same way under both readings, which
is the only reason that call was trustworthy.

This one will not be so clean. When the local arms finish and the data is
sitting there, the pull toward "we have two models, let us just report the pair
and note the limitation" will be strong, and every ingredient of a good excuse
will be available: the data is real, the analysis runs, the limitation is
declared. That is how designs get quietly changed — not by anyone deciding to
cheat, but by a reasonable-sounding step taken at the moment it is most
tempting.

So the decision is made at 38%, with nothing to gain from it either way.

## What may still be done

- **Collect the local arms to completion.** The draws are valid, cached and
  committed regardless of what happens to the analysis. If credits arrive next
  week, the third arm slots in and the registration completes.
- **Report nothing publicly.** The [launch plan](../../launch/) already gates
  every E-004 mention on the run completing as registered or being declared
  void, dated, in the repository.
- **If it is declared void**, the successor is a new id with its own
  registration, and the honest thing it must carry is that E-004 died of a
  billing state rather than of anything about the world.

---

*This document is licensed CC BY 4.0.*
