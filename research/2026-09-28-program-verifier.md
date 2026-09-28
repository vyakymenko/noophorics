# Program-output verifier: offline instrument check

**2026-09-28 · instrument prototype, not an E-003 experiment.** This is the
first implementation step proposed by the [domain methods note](2026-09-14-domain-methods.md).
It checks a deliberately small task format without calling a model. The
[validation record](program-verifier-validation.json) contains the exact runtime,
manifest and instrument hashes, checked fixture identities, and negative-test
rejection codes.

The format starts with two integer registers and runs one to eight straight-line
arithmetic instructions. Its last instruction reduces the declared output
register modulo four, giving a fixed answer vocabulary `{0, 1, 2, 3}`. The
[format description](../probes/domain-code/README.md) specifies the bounds,
operations and provenance fields. The [verifier](../tools/verify_program_output.py)
checks schema, pinned source/runtime identities, bounded execution and each
recorded state transition through a second calculation path. It rejects a key
that disagrees with the computed output. It executes this restricted data format;
it never evaluates supplied Python source.

The saved run accepted **4 of 4 synthetic fixtures** and produced the expected
rejection code for **8 of 8 deliberately damaged copies**. The damaged cases
include a wrong answer key, changed source hash, wrong runtime, false holdout
claim, corrupt trace, unsupported operation, missing final normalization and
state overflow. The [unit tests](../tools/test_verify_program_output.py) also
inject faults into both execution and verification paths and passed **13 of
13** checks. These are engineering checks on this finite fixture set. They do
not estimate performance on a task population.

The fixtures and keys were authored together. The two code paths can catch an
inconsistent trace or key, but cannot independently adjudicate whether a
model-facing text accurately specifies a program. The fixtures are therefore
labelled `holdout_eligible: false` and `independent_key_adjudication: false` in
the [manifest](../tools/fixtures/program_output/manifest.json). They are test
material, not an independent probe measure or a clean confirmation bank. No
model responses, transfer scores or domain-prior measurements were collected;
E-003 remains planned.

Reproduce the saved validation from the repository root with CPython 3.14.6:

```bash
python3 tools/test_verify_program_output.py
python3 tools/verify_program_output.py tools/fixtures/program_output/manifest.json --self-check
```

The second command emits JSON. Compare that output with
[`program-verifier-validation.json`](program-verifier-validation.json); any
changed instrument, fixture or negative check must be reviewed as a new
validation record. A future model-facing study still requires separately
authored items, independent key adjudication, a frozen protocol and an untouched
confirmation set before subject calls.

**Exposure:** the Codex implementation agent read the domain-selection and
methods drafts and authored the synthetic fixtures and keys. The original
repository probe items, keys and subject responses were not displayed in this
work. This agent cannot independently adjudicate its own fixtures or serve as a
naive E-003 subject; the session is recorded in [EXPOSURE.md](../EXPOSURE.md).

---

*This document is licensed CC BY 4.0. Code is Apache-2.0.*
