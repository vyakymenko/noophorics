# Qwen register feasibility: prospective measurement plan

**Drafted 2026-09-09; finalized 2026-09-14 before collection. Instrument check,
not a successor experiment.** This plan and
[`plan.json`](plan.json) are to be committed before the first rating. The source
compositions and their length outcomes already exist. Register outcomes for this
check have not been collected. No new scientific hypothesis or law is tested.

## The missing observation

[`RESULTS-qwen-floor.md`](../../experiments/E-001c-fluency-length-controlled/RESULTS-qwen-floor.md)
reports length compliance while explicitly leaving the register filter
unmeasured. The existing absolute question in
[`blind_rating.py`](../../experiments/E-001c-fluency-length-controlled/blind_rating.py)
asks whether a passage connects its points in prose or lists separate items.
Unlike the earlier forced choice between two passages, it permits both passages
to fail their intended register.

This check applies that question to the archived qwen compositions. Its output
is the observed intersection of length and register acceptance, not the product
of their marginal rates. All source messages are included, even when their
length fails the band.

## Frozen inputs and raters

The machine-readable plan pins the full SHA-256 of the source JSON, the existing
question and its containing file, the word band, the cell mapping, the control
passages, and the two installed rater model digests. The runner checks these
before collection. The original composer is `qwen3.5:35b`; its historical
weights digest was not recorded in that artifact and is explicitly unknown.

The raters are `gpt-oss:120b` with `think=medium` and `llama3.3:70b` with the
thinking field omitted, both at temperature 0.7. These are different inference
regimes. The observation is agreement between these particular configured
judges, not a controlled comparison of model ability. Neither is the composer.
Different model names or lineages alone do not prove independent errors.

The coordinating Codex agents have read the instructions and labels, so none
serves as a blind rater. Their exposure belongs in [EXPOSURE.md](../../EXPOSURE.md).

## Collection and calibration

- Four fixed control passages are rated first by each judge: two connected
  prose passages and two lists. The controls are procedural checks written for
  this run, not a validated register benchmark. A separate agent reviews their
  labels before the plan is committed; same-model review is disclosed. That
  review agreed with all four labels on 2026-09-09 without opening the source
  corpus. It is a procedural sanity check, not external validation.
- A judge must classify every control correctly before its corpus ratings
  begin. A failed or missing control skips that judge's corpus; it does not
  trigger prompt changes, replacement controls, or another judge.
- Each eligible judge rates all 48 archived messages, twelve in each cell,
  once each, in a deterministic shuffled order. The prompt contains only the
  exact absolute question and one passage. It contains no cell, expected label,
  composer, source specification, previous answer, or experimental hypothesis.
- A/B cells expect connected prose (`A`); C/D cells expect a list (`B`). These
  expected labels remain outside the model request. The structured response
  requests one verdict; this wrapper and every complete request are retained.
- The cap is **104 HTTP rating attempts**: two judges times four controls plus
  48 corpus messages. There are no retries, replacements, optional stopping on
  a favourable corpus result, or extra compositions. The timeout is 120 seconds
  per request. Seeds, request bodies, responses, errors, and timing are saved.
- Each attempted request is checkpointed before it is sent. A crash with an
  unresolved request leaves an indeterminate observation that is never resent.
  Resume requires matching plan, source, question, runner, and model digests.
  Every failed, invalid, or missing response remains visible.

The four controls test gross misuse of the question. Passing them does not
establish that a judge correctly classifies borderline experimental passages.
An otherwise blind judge can infer register or task content from the passage
itself; blinding does not remove that information.

## Output fixed before collection

For each cell, report total messages, word-band acceptance, valid ratings by
judge, expected-register acceptance by judge, two-judge disagreement, missing
ratings, and the **direct count passing both the band and both judges**. Save
the message identity and hash behind each count. Count an invalid response as
missing, never as a list verdict. If a judge fails calibration, the two-judge
result is unavailable rather than a measured zero. Any unresolved corpus
ratings make the complete joint count unavailable; observed acceptances and
missingness may still be reported explicitly.

There is no new significance threshold or inferred population acceptance rate.
These are finite-corpus counts from a single rating per message and judge.
There is no fidelity estimate, no reference-based decision task, and no measure
of phantom agreement. Register acceptance says nothing about factual accuracy,
contrastiveness, transfer, or the usefulness of these passages.

## What follows, conditionally

E-001c remains void and its pre-registration stays unchanged. These archived
compositions remain instrument data. A full successor requires a new
registration, fresh experimental compositions, declared references and
independently checked probes, and an outcome-variation check. The
[void's amendment](../../experiments/E-001c-fluency-length-controlled/VOID.md)
already identifies saturation of MERIDIAN-34 at the relevant lengths.

After collection, save the raw artifact and mechanically reproduced counts.
Any scientific interpretation, promotion, or correction is a draft for human
review under [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

*This document is licensed CC BY 4.0.*
