# Estimand audit: Problem 13's incidents, traced to their arrays

**2026-10-07 · offline instrument and report, for human review.** No model was
called, no published result was recomputed, and no rule is adopted here. The
[tracer](../tools/audit_estimand.py) runs the E-002b and E-002c runners'
`analyse()` on synthetic draws and records which array produced each interval
and p-value that the shared inference helpers return. Its
[tests](../tools/test_audit_estimand.py) include the three incidents
[Problem 13](../theory/open-problems.md) names, run from the revisions that
carried them.

## Why a results file cannot show the defect

[Problem 13](../theory/open-problems.md) records three claims whose interval and
p-value came from different quantities. A results file holds the numbers, not
the arrays behind them, and the defect does not always show in the numbers. A
CI that excludes zero beside a large `p` was the symptom in E-002b's H4. E-002c's
H3 was coherent on its face: both of its numbers said "supported", and they
measured different things.

So the binding has to be made where the numbers are computed. The tracer
replaces the shared `bootstrap_ci`, `permutation_diff` and `paired_permutation`
in a runner's namespace with wrappers that keep each call's inputs and returned
objects. Each effect's `ci95` and `p_value` are then bound to the call that
produced them **by object identity**: they are the very float objects a wrapped
call returned, so the binding is exact and changes no value. A number no wrapped
call returned — one computed inline — stays unbound and is reported as such.

| rule | asks | the incident it exists for |
|---|---|---|
| **R1** | Is the test's observed statistic the reported value, or the mean of per-unit terms whose sum is? | E-002c H3: a slope difference reported, a level difference tested |
| **R1b** | Is the interval's own point estimate the reported value? | the same shape, on the interval's side |
| **R2** | Do interval and test resample the same units, paired the same way? | E-002b H4: an interval over paired differences, an unpaired test |
| **R3** | Did a wrapped call produce the number at all? | none; an untraced number is reported, not failed |
| **R4** | Does the runner's own terminal summary mark a registered hypothesis exactly when the record calls it supported? | E-002c H1: the summary gated on a p-value H1 has by design none of |

R1, R1b and R2 are properties of which arrays the code passes where, so one
synthetic draw exercises them. R4 is not. Whether a record and a summary
disagree depends on where a draw falls relative to their two decision rules,
so R4 executes each runner's `main()` — with `run()` replaced by the traced
result and `--out` pointed at a temporary directory — over forty synthetic
draws, and a FAIL names the first that shows it. The tests check both that
each summary reported writing inside its temporary directory and that the
whole tree, ignored files included, is unchanged afterwards.

## Each incident, red on its revision and green on its fix

| incident | rule | revision that carried it | commit that fixed it |
|---|---|---|---|
| E-002b H4 | R2 | `a62d2d6`: `FAIL:unpaired-test-of-paired-differences` | `df0305b`: ok |
| E-002c H3 | R1 | `cea9243`: `FAIL:different-quantity` | `c97005b`: ok |
| E-002c H1 | R4 | `549ff54`: `FAIL:mark-disagrees` | `cea9243`: ok |

Each red result must carry its own code, so a catch-all branch cannot stand in
for the detector the incident needs. The historical runners are loaded from
git and run against the current `metrics` library. The H3 fixture uses
`cea9243` rather than the runner's first revision, because both of that
runner's first two revisions carry the H3 and summary defects together and only
the `549ff54` → `cea9243` pair isolates the summary.

## What it reports on the runners as they stand

**Two more instances of E-002b H4's shape.** E-002b's registered H3 and E-002c's
`recorded_conditional_asymmetry` build their interval from paired
over-minus-under differences and test with an unpaired two-sample permutation of
the same pairs: R2 `FAIL:unpaired-test-of-paired-differences`. Both concatenate
sender and receiver, so each runs over two values per brief: 32 for E-002b's 16
briefs, 48 for E-002c's 24. Their published verdicts are not changed by
anything here. E-002b H3's unpaired `p` is already 1/10 001, the smallest a
10 000-permutation test can return, so a paired test on the same draws could
not give a smaller one; whether it would give a larger one is not computed.

**A record and a summary that can disagree.** In both runners most registered
hypotheses' `supported` is decided by the interval alone — E-002c's H3, whose
verdict is its corrected test, is the exception — while the terminal summary
marks a hypothesis that carries a p-value only if its Holm-corrected `p` is
also below 0.05. On a draw where the interval excludes zero and the
corrected `p` does not reach 0.05, the record says supported and the summary
says nothing. R4 finds that for E-002b's H2 and E-002c's H4, first at synthetic
seed 9. It is E-002c H1's defect class, reached through a different rule. No
published record of the present runners lands in that region. The first
E-002b results file did — H4 at `supported: true` beside
`significant_at_005: false` — and that is Problem 13's first incident.

**A one-sample question asked with a two-sample test.** E-002b H1 and H2, and
E-002c's H4 and `recorded_bias_positive`, test "mean above zero" by permuting
the values against a vector of zeros. That is reported as its own class rather
than as a pairing defect, because the interval and the test do use one array.
Whether that test answers the registered question is not decided here.

**Untraced intervals.** Seven of the fifteen effects' intervals are computed
inline: E-002b's H5, whose p-value is inline too, and E-002c's `beta_pooled`,
`beta_sender`, `beta_receiver`, H1, H2 and H3. Four of the nine registered
hypotheses are among them, E-002c's primary H1 included. R3 reports them as
untraced. An inline estimator can be correct, and this tool cannot see inside
one.

**A label, not an estimate.** E-002c's results file records H3's
`sum_of_contributions` as `0.012489` beside a value of `0.299731`. The ratio is
24.0, the number of briefs: the field holds the *mean* `paired_permutation`
returns, under the name of the sum.
[FINDINGS](../experiments/E-002c-calibration-slope/FINDINGS.md) checks the sum by
hand and gets it right; the record mislabels its own estimand, which is the
Problem 13 class at the level of a field name.

## What it does not establish

- **Synthetic draws exercise code paths, not published numbers.** A FAIL says
  the runner *computes* an interval and a test from different structures, or
  that its record and summary *can* part. It does not say a published verdict
  is wrong, and none is recomputed here.
- **Two runners.** The E-001 family computes its statistics locally. E-001b
  and E-001c use `bootstrap_effect_ci`, `permutation_main_effect` and a local
  `holm_adjust`; E-001 has its own `permutation_test` and `bootstrap_ci` and no
  Holm step. None is in the tracer's reach. E-001c is the one experiment whose
  pre-registration registers a same-array rule.
- **Only what the shared helpers return is bound.** A number computed inline,
  or through a helper reached by another name, is reported as untraced.
- **Not a gate.** It reports FAILs on registered hypotheses at HEAD, before
  anyone has decided what a registration should require. A check that turns
  current work red on rules nobody chose teaches its reader to ignore it. The
  tool is not in the pre-push list.

## Decisions this leaves for the owner of the analysis plans

1. **Which relation a registration requires.** E-001c's pre-registration
   (section 6, item 6) asks that effect, interval and p-value come from *the
   same array*. Corrected E-002c H3 fails that, and legitimately so: its
   interval bootstraps briefs jointly and its test sign-flips per-brief
   contributions. R1 accepts it. One of the two is the rule.
2. **Whether two party values per brief satisfy "brief-level".** E-002b's
   pre-registration says "permutation test over briefs" for H3. E-002b's H2 and
   H3 pool sender and receiver into 32 units for 16 briefs, and E-002c's H4 into
   48 for 24.
3. **Which verdict the record and the summary carry when interval and corrected
   `p` disagree.** At present they carry different ones.
4. **Whether the R2 findings need addenda** in their FINDINGS, under the rule
   that results files are never rewritten.
5. **Whether a future runner must pass this audit before its registration is
   committed**, which is the point at which fixing it costs nothing.

## Reproduce

```bash
python3 tools/test_audit_estimand.py
python3 tools/audit_estimand.py --fixtures
python3 tools/audit_estimand.py
python3 tools/audit_estimand.py --check-record research/estimand-audit.json
```

The counts this note states are read back from the saved
[record](estimand-audit.json) by `tools/check_counts.py`; the last command
recomputes that record and fails if it no longer matches.

**Exposure.** Written by `claude-opus-5-5`. It read both runners in full,
including their composition and framing prompt templates, and five historical
revisions of them. It read E-002b's pre-registration §5 items 3–6, E-001c's §6
items 4–7, E-002c's FINDINGS lines 160–180 and the H3 entry of its last
results file, and Problem 13 in full. E-002c's hypotheses it knows from that
runner's comments and from scouting agents' summaries; it did not open E-002c's
pre-registration. Of the E-001 runners it read only their statistics functions'
names. No probe item, key or brief text was opened. See
[EXPOSURE.md](../EXPOSURE.md).

---

*Prose: CC BY 4.0. Code: Apache-2.0.*
