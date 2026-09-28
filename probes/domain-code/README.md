# Program-output instrument prototype

This directory contains **no probe items, keys, model responses or untouched
holdout**. The current deliverable is an offline verifier for a small language,
in [`tools/verify_program_output.py`](../../tools/verify_program_output.py).
Its examples live only in
[`tools/fixtures/program_output/`](../../tools/fixtures/program_output/) and
are synthetic, self-keyed test fixtures. They are ineligible for selection or
confirmation as independent items. No E-003 experiment is registered or run by
this prototype.

## Bounded language and answer

A program starts with two signed integer registers, `a` and `b`, each from
`-9` through `9`. It has one to eight straight-line instructions. Each
instruction names a destination register, an operation (`set`, `add`, `sub`,
`mul`, or `mod`), and a source. A source is one register's value at the **start**
of that instruction or a literal from `-9` through `9`. `mod` instead requires
a positive literal from `2` through `9`, and uses Euclidean remainder. Every
intermediate register value must stay within `-10000` through `10000`. There are
no branches, loops, calls, strings, imports or effects. The final instruction
must be `mod` by `4` on the declared output register, giving the fixed answer
vocabulary `{0, 1, 2, 3}`.

The manifest schema is `noophorics.offline_program_output.v1`. It pins exact
CPython version and verifier source SHA-256. Manifest provenance records author,
source, creation time, fixture-only purpose, and the absence of independent key
adjudication. Each item records an id, family and structural-template ids,
initial registers, instruction list, output register, answer key, and SHA-256
of its canonical item specification excluding the key and hash. The checker
refuses duplicate JSON fields or item IDs, unexpected fields, malformed hashes,
out-of-range values, wrong keys, wrong runtime or verifier identity, and
out-of-scope provenance. It reads no more than 100,001 bytes before rejecting a
manifest over 100,000 bytes. Wrongly typed or out-of-range item fields receive
structured rejection before specification hashing.

The runtime executes the bounded instructions and records every before/after
state. A separate checker reconstructs each transition from the source item
without calling the runtime function. It also checks the final output and
fixture key. This catches faulty traces; agreement between two local code
paths **does not constitute independent adjudication** of the text-to-program
mapping or license any scientific claim.

Run the checked synthetic fixtures with:

```bash
python3 tools/test_verify_program_output.py
python3 tools/verify_program_output.py tools/fixtures/program_output/manifest.json --self-check
```

The second command returns a JSON summary with accepted fixture count, exact
manifest and instrument hashes, and the expected and observed rejection codes
for deliberately broken copies. A nonmatching negative check exits nonzero.

Any later model-facing measure needs its own prospective protocol, separately
authored items, independent adjudication of source/keys and exposed template
families, and a reserved confirmation set. The prototype fixtures must not be
renamed into a holdout.

---

*This document is licensed CC BY 4.0.*
