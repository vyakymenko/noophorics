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
inject faults into both execution and verification paths and passed **15 of
15** checks. These are engineering checks on this finite fixture set. They do
not estimate performance on a task population.

An adversarial input review found that a JSON escaped lone surrogate in an
input register caused an uncaught `UnicodeEncodeError`: the verifier encoded
the item specification for its hash before checking the input's type. The
current version validates the specification fields first and returns the
structured `INPUT_RANGE` rejection. The loader also now reads at most 100,001
bytes before enforcing its 100,000-byte file limit; previously it read the
whole file into memory before checking. Both failures have regression tests.
This is an instrument correction, not a new observation about model behavior.
The saved validation record has been regenerated against the corrected source
and manifest hashes; the earlier record remains in git history.

The count gate now checks both sides of the stated fixture and negative-check
counts against the manifest and saved validation record, and the stated unit
test count against defined test methods. It checks this source and the generated
site page separately. A test deliberately makes each page's unit-test count
stale and requires the gate to fail; the test suite itself must still be run to
verify that those tests pass.
An adversarial follow-up found that a damaged validation row with both rejection
codes missing was counted as passing when its `passed` flag was true, because
the two missing values compared equal. The gate now requires a nonempty expected
rejection code and an identical observed code; a regression test demonstrates
the former false green and the corrected refusal. The saved validation rows
themselves were unchanged.

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
