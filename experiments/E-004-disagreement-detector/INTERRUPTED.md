# Collection stopped at 104 of 126 cells, on one socket timeout

**2026-07-31, 19:04 local.** Written before the run is resumed and before any
analysis, so that what happened is on the record independently of what the
remaining data turns out to say.

---

## What happened

The runner raised an uncaught `socket.timeout` in the middle of
`RIVERSIDE-30@qwen3.5:35b` and exited. The read timeout was already 900 s, so
this was not an impatient client: one call to a 30 GB local model did not come
back inside fifteen minutes, and there was no second attempt anywhere in the
stack.

```
RIVERSIDE-30@qwen3.5:35b   104/126
  ollama_agent.py:96  in _chat
  urllib/request.py   urlopen(request, timeout=self.timeout_s)
socket.timeout: timed out
```

Elapsed before the crash: 8 h 06 m of a run that began at 10:58.

## What is on disk, and what is missing

| condition | cells | draws per cell |
|---|---|---|
| MERIDIAN-33@gpt-oss:120b | 33 / 33 | 16 |
| MERIDIAN-33@qwen3.5:35b | 33 / 33 | 16 |
| RIVERSIDE-30@gpt-oss:120b | 30 / 30 | 16 |
| RIVERSIDE-30@qwen3.5:35b | **8 / 30** | 16 |

**Every cell present holds exactly 16 draws. There are no partial cells.** The
cell that timed out wrote nothing at all — `Cache.put` is called once, after a
cell completes, and writes atomically through a temporary file and `os.replace`.

Missing: `T09`–`T30` on `RIVERSIDE-30@qwen3.5:35b`, 22 cells.

## One timeout, and why that matters

There is exactly **one** timeout in the entire run log, and it was fatal. The
collect path contains no `except` that continues, so no draw was ever skipped
and retried-past in silence.

That is worth stating because the opposite would have been much worse. A
transport failure that is caught and skipped would drop probes *non-randomly* —
the probes that make a model think longest are the ones most likely to time
out, and on this measure that is a property of the probe, not of the network.
Silent dropout would have quietly deleted the hardest probes from the sample.
That did not happen here. The run crashed instead, which is the failure mode to
prefer.

## Resuming

The remaining 22 cells can be collected without recollecting anything, because
`Cache.get` returns a cached cell **only when its length equals the requested
`n`**:

```python
return list(got) if got is not None and len(got) == n else None
```

The trap this creates is worth naming: **the resume must pass `--samples 16`.**
Any other value makes every one of the 104 cached cells fail the length test and
be redrawn — eight hours of collection discarded by a flag.

Resuming is not an amendment. The
[pre-registration](PREREGISTRATION.md#6-amendment-policy) forbids changing *"the
detector, the models, the hypotheses, the gates, or either probe measure after
collection begins"*, and finishing an interrupted collection with the same
runner, the same two models and the same probe measures changes none of them.

## The instrument changed between cell 104 and cell 105, and that is declared

After this crash, `metrics/noophorics/ollama_agent.py` gained a bounded retry:
three attempts on transport failures only — socket timeout, connection refused
or reset, HTTP 5xx — with backoff, and **every retry printed to stderr**. A 4xx,
a malformed body and an empty completion are not retried; the last of those is a
real observation about the model, and this module already refuses to coerce it
into a verdict.

So the first 104 cells were collected by a client that could not retry, and the
last 22 will be collected by one that can. The argument that this does not
compromise the run:

- A retry changes whether a draw is **obtained**, not what a draw **is**. Draws
  are independent samples at a fixed temperature; nothing about the answer
  returned depends on whether an earlier TCP read timed out.
- **Zero retries were used in the first 104 cells** — there was one timeout and
  it was fatal, not retried. So the two regimes differ only in what *would* have
  happened, not in anything that did.
- If no retry fires during the remaining 22 cells, the two halves were collected
  under identical conditions in fact.

That last line is a check, not a hope. **When the resume finishes, count the
`[ollama_agent]` lines in its log and report the number here — including if it
is zero.** A declaration that is never checked is decoration.

### The check could not be performed

**2026-08-03.** The resume completed at 09:12 UTC: 126 of 126 cells, every one
at exactly `n = 16`, exit 0. The retry count is **unknown and unrecoverable**.

The loop reads the child process's `stderr` only in its failure branch, so a run
that exits 0 discards it. The retry lines this file asked to be counted were
printed to `stderr` by a run that succeeded, and nothing wrote them down.

So the declaration above stands unverified. What can still be said is narrower
and worth separating from what cannot:

- **Zero retries were used in the first 104 cells.** That is established: there
  was one timeout in that run's log and it was fatal, not retried.
- **At most two retries fired on any single call in the last 22**, since a third
  failure raises and the run exited 0.
- **How many fired in total is not knowable from what was kept.** It could be
  zero. Reporting it as zero because zero is likely would be inventing a
  measurement, which is the thing this file exists to avoid.

The loop now persists both streams of every run under
`automation/state/runs/`, on success as well as failure. That does not recover
this number; it prevents the next one from being lost. Recorded here rather than
quietly dropped, because a declaration that turns out to be uncheckable is a
finding about the instrument.

## What this does not change

The third arm is still blocked, and
[BLOCKED-NOTE](BLOCKED-NOTE.md) still governs: **if `claude-opus-4-8` never
runs, E-004 is void, not a two-model experiment.** Completing the local 126
cells does not produce a reportable result; it produces committed draws that the
third arm can still be added to.

Nothing here is reported publicly. The [launch plan](../../launch/) gates every
mention of E-004 on the run completing as registered or being declared void,
dated, in the repository.

---

*This document is licensed CC BY 4.0.*
