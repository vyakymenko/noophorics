# F* near a vanishing gap: the simulation's results

**2026-10-16 · results of the offline simulation registered in
[the plan](2026-10-16-vanishing-gap-plan.md)**, which was committed before the
[simulation code](../metrics/validation/vanishing_gap.py), itself committed
before its registered run. No model was called. Every number below is in the
[saved record](vanishing-gap.json); the tables are generated from it and checked
against it. **P1, the prediction held least firmly, failed — and its criterion
failed for every variant**, which is the branch where the plan said the report
would say so and Problem 12 would stay exactly as open as it is. It does.

## The predictions

P1 failed: the library-default (V0) Fieller set fell below 0.93 coverage in 10
of 48 cells. Re-read for the other variants from the same record, the criterion
also fails for V1 (26 cells) and V2 (6). P2, P3 and P4 held, and P2 and P3 hold
for every variant (Table 1). P1 stands as written.

The V0 and V2 failures are not where Problem 12 lives. V0's are all at the two
widest gaps, `g = 0` and `g = 0.6`; V2's are all at `g = 0`. Where the gap
shrinks toward the floor — `g ≥ 0.8` — the V0 set covered the true `F*` in
0.9525–1.00 of trials in every cell, and V2's in 0.9825–1.00. V1's did not: it
fell as low as 0.37 there.

## Choices fixed in the code before the registered run

The plan left four things open, and the code fixed them, in the commit that
predates the run: the present report is scored as its capped percentile
interval, given only when the point passes the epsilon gate, with a refusal
counted as a miss; percentile intervals use the bootstrap replicates whose
denominator is positive, and a trial with none scores a miss (no trial had
none); the floor is the exact hypergeometric sum, as the plan specified; and
P2's "capped or not" is read strictly, so both versions must fail somewhere.
`score()` reads P2 and P3 from V0; that reading was not listed among the four,
and the per-variant column of Table 1 shows it changes nothing. Before the code
was committed, a smoke run of four cells at 20 trials each — including the
`n = 16` antinoophor cell P4 is scored on — was executed for timing.

## What the present report does where the gap vanishes

At `g ≥ 0.95` the epsilon gate passes at most 0.155 of trials, and the present
report covers the true `F*` in 0.00–0.1025 of them (Table 2); at `g = 0.9`,
0.0325–0.24. That is P2. Its coverage never exceeds its gate's pass rate in any
of the 48 cells, which follows from scoring a refusal as a miss. Where it does
report, it mostly covers: at `λ = 0.25` and `g ≥ 0.95` the reported intervals
covered in every trial, and the same capped percentile interval without the gate
covered 0.9775–0.995.

It also misses where the gap is wide. At `λ = 1`, where the true `F*` is 1, the
percentile interval, capped or not, covers it in 0.045–0.105 of trials at every
gap including the widest. That is a count; why the bootstrap distribution sits
below the truth there is not tested here.

Among the trials it reports, the gated, capped point is biased upward in 32 of
the 47 cells where it reports anything and downward in 15 — all twelve `λ = 1`
cells among them, where the cap acts, at −0.006 to −0.269. At `g ≥ 0.6` with
`λ < 1` the bias runs from −0.079 to +0.533. At `g = 0`, where the gate passes
every trial and so selects nothing, it is already +0.024 to +0.069 for `λ < 1`.
No sign was predicted for it, and none is attributed here.

## The V0 and V2 Fieller sets widen as the gap closes, and hold coverage there

The share of V0 sets that are bounded intervals is 1.00 at `g = 0`, 0.9575–1.00
at `g = 0.6`, 0.24–0.985 at `g = 0.8`, 0.0325–0.47 at `g = 0.9`, and
0.0025–0.0125 at `g = 0.98`. Across the grid that report widens without bound as
the evidence for a gap disappears, instead of switching from a number to a
refusal — which is the first thing Problem 12 asked for — and from `g = 0.8` on
its coverage is never below 0.9525. The exception is the zero-gap antinoophor
cells, where the true gap is exactly zero and V0's set is still bounded in
0.695–0.74 of trials; the floor-convention section below shows why that set
has something to be bounded around.

## …and lose coverage at the widest gap, by what their centre's bias predicts

At `g = 0` the V0 set covers 0.7125–0.995, lowest at `λ = 0.75`; V2's covers
0.735–0.995. Table 4 fits the simplest model of that loss: a set of the observed
width, centred on the uncapped ratio `M̂/Ĝ` with its observed bias. At `g = 0`
with `λ < 1` it reproduces the observed coverage within 0.03 in every cell, for
both variants. At `g = 0.6` it predicts up to 0.06 too little, and at `λ = 1`,
where the truth sits on the cap, it predicts 0.95 against an observed
0.9875–1.00. Table 4 omits the two `n = 10`, `g = 0.6` cells where V0 fails,
because there not every trial is reported or not every set is bounded; the same
model, applied anyway, gives 0.883 against an observed 0.905 and 0.897 against
0.92 in them. So for the V0 and V2 sets, a set
of the right width around a biased centre reproduces the failures without
appeal to any property of the Fieller construction. Where the ratio's bias comes
from is not tested here. The model does not reproduce V1's losses: it predicts
0.95 where V1 covers 0.085 at `n = 10`, `g = 0`, `λ = 1`.

## The floor convention changes which gap is being estimated

*This section rests on fields added to the record after the first registered
run (see Limits).* The simulation has three estimator variants over two floor
conventions; Table 5 shows the denominator itself where the true gap is small.

- **V0**, with the floor on `(sender, post)`, estimates a gap that moves with the
  receiver. At `g = 0.95` and `n = 10` the true gap is 0.0074–0.0075 in every
  cell, and V0's mean estimate runs from 0.0044 at `λ = 0.25` to 0.0104 at
  `λ = 1`. At a true gap of zero, with a receiver that moved away from the
  sender, V0's estimated gap is negative in 0.995–1.00 of trials (Table 5), and
  its Fieller set is bounded in 0.695–0.74 of them (Table 3): it reports a gap
  that is not there.
- **V1 and V2**, with the floor on `(sender, prior)`, do not move with the
  receiver, and at zero gap their sets are bounded in at most 0.01 of trials. But
  their mean estimate sits below the true gap at `g ≥ 0.9` — 0.0047–0.0071
  against 0.0165–0.0169 at `g = 0.9`.
- **V1** leaves the numerator uncorrected while correcting the denominator, and
  its set covers the truth in as little as 0.085 of trials at `λ = 1`.

This is evidence for the question `fidelity_from_draws` leaves open, of which
pair the floor belongs to. It settles nothing: V2 behaves best of the three and
still fails at the widest gap, `g = 0` (six cells, as low as 0.735), and neither
convention estimates a small gap accurately.

## Want 2: the movement interval works; the gap beside it does not

At a true gap of zero `F*` is undefined. The movement `M = D_prior − D_post`,
with its own percentile interval, is not (Table 3). That is P4: with a receiver
that moved away, the interval excluded zero on the side of moving away in
0.99–1.00 of trials; with nothing moved, it excluded zero in at most 0.005.
Across the grid it covered the true movement in 0.78–1.00 of trials, below 0.93
in six cells, all at `g ≤ 0.6`: five with `λ ≥ 0.75` and one at `λ = 0.25`. No
cause is attributed to those six.

The plan's report for want 2 puts the movement *beside the gap and its
interval*, and the plan registered no measurement of that gap interval. It was
computed after the registered run (Table 6), and it fails. The percentile
interval for `Ĝ` covers the true gap in 0.07–0.92 of trials under V0 and
0.0875–0.94 under V1 across the grid, and in 0.07–0.67 at `g ≥ 0.9`. The basic
interval does no better (0.0425–0.815, 0.005–0.4675). In the zero-gap null cells
the percentile interval lies wholly above zero in 0.835–0.96 of trials: it
reports a gap that is not there.

So this simulation supports reporting the movement with its interval, and does
not support the gap that the plan's report pairs with it. Whether a movement
below zero at zero gap should be called an antinoophor is a separate question:
`lexicon.md` defines one by `F* < 0`, which is undefined there, so the name is a
definition for the owner, not a finding.

## What this does and does not change

**Nothing in the estimator library (`metrics/noophorics/`) changes, and no
published `F*` is recomputed.** The plan said a proposal would follow if P1
held, and it did not.

What the run shows is where each piece works and where it does not. Near the
vanishing gap, the V0 and V2 Fieller sets widen without bound and hold their
coverage, and the movement interval detects a receiver that moved, which the
ratio cannot express. At the widest gap the V0 and V2 sets lose coverage by about
what a biased centre predicts. The gap's own interval fails throughout. Whatever
the next step is, the evidence here points at the bias of the divergence
estimates rather than at the shape of the interval. Choosing it, like any change
to how `F*` is reported, belongs to the owner of the definitions.

## Limits

- Synthetic agents with three options, independent draws within a probe, and
  uniform weights; one generator of distributions. Real draws may be dependent.
- The frame is fixed. Nothing here bears on whether `F*` is stable across probe
  measures.
- 400 trials per cell: a coverage of 0.95 has a Monte Carlo standard error of
  about 0.011.
- **Fields added after the first registered run.** The first run showed V0's
  sets bounded at zero gap, and the estimated gap was then added to the record
  (Table 5). A same-model review of this note then asked for the gap's own
  interval (Table 6) and the bias of the uncapped ratio (Table 4's centre), and
  found that a linear case of the Fieller inequality returned the whole line
  where it should return a half-line; that case never occurred in the run. The
  full run was repeated after each change, and every field of the first run came
  out byte-for-byte identical both times.

## Reproduce

```bash
python3 metrics/validation/test_vanishing_gap.py
python3 metrics/validation/vanishing_gap.py --out research/vanishing-gap.json
python3 metrics/validation/vanishing_gap_report.py --check
```

The second command takes about six minutes on sixteen processes and rewrites the
record; the third checks these tables against it.

**Exposure.** `claude-opus-5-5` wrote the plan, its predictions, the simulation
and this report, and scored its own predictions. The scoring is mechanical
(`score()` in the simulation, run as registered), and the predictions are in a
commit that predates the code. A same-model review checked this note before it
was committed, including an independent reproduction of point estimates through
the library's `fidelity_from_draws`. See [EXPOSURE.md](../EXPOSURE.md).

<!-- tables:start -->
**Table 1 — the predictions, scored as registered.** `score()` reads P2 and P3 from V0; the last column re-reads every prediction for each variant from the same record.

| prediction | held? | the numbers it turned on | per variant |
|---|---|---|---|
| P1: V0 Fieller set covers ≥ 0.93 wherever `F*` is defined | **no** | below 0.93 in 10 of 48 grid cells, lowest 0.7125 | below 0.93 in V0 10, V1 26, V2 6 cells |
| P2: percentile intervals fall below 0.93 at some `g ≥ 0.9`, capped and uncapped; the present report below 0.93 at every `g ≥ 0.95` | **yes** | capped below in 18 cells, uncapped in 18; present report covers 0.0000–0.1025 at `g ≥ 0.95` | V0 holds, V1 holds, V2 holds |
| P3: bounded share of Fieller sets lower at `g = 0.98` than at `g = 0`, and below one half | **yes** | 1.0000–1.0000 at `g = 0`; 0.0025–0.0125 at `g = 0.98` | V0 holds, V1 holds, V2 holds |
| P4: zero-gap antinoophor detected ≥ 0.8 at `n = 16`; null cells exclude zero ≤ 0.08 | **yes** | 0.9975; nulls 0.0025 and 0.0050 | does not depend on the variant |

**Table 2 — every grid cell.** Coverage of the true `F*` at nominal 0.95; `present` is the gated, capped percentile interval with a refusal counted as a miss. Bias is of the gated, capped V0 point, among trials it reports.

| `n` | `g` | `λ` | true gap | V0 gate pass | V0 bounded | Fieller V0 | Fieller V1 | Fieller V2 | percentile, capped | present | V0 point bias | movement cover |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 0.0 | 0.25 | 0.3384 | 1.0000 | 1.0000 | 0.9125 | 0.9075 | 0.9175 | 0.9450 | 0.9450 | +0.036 | 0.9275 |
| 10 | 0.0 | 0.5 | 0.3387 | 1.0000 | 1.0000 | 0.8450 | 0.8175 | 0.8525 | 0.9700 | 0.9700 | +0.068 | 0.9325 |
| 10 | 0.0 | 0.75 | 0.3390 | 1.0000 | 1.0000 | 0.7125 | 0.4825 | 0.7500 | 0.9525 | 0.9525 | +0.069 | 0.8750 |
| 10 | 0.0 | 1.0 | 0.3391 | 1.0000 | 1.0000 | 0.9950 | 0.0850 | 0.9950 | 0.0850 | 0.0850 | -0.008 | 0.7800 |
| 10 | 0.6 | 0.25 | 0.0906 | 0.9950 | 0.9575 | 0.9500 | 0.9425 | 0.9725 | 0.9700 | 0.9650 | +0.102 | 0.9500 |
| 10 | 0.6 | 0.5 | 0.0894 | 0.9975 | 0.9800 | 0.9050 | 0.8100 | 0.9575 | 0.9675 | 0.9650 | +0.178 | 0.9625 |
| 10 | 0.6 | 0.75 | 0.0909 | 1.0000 | 0.9950 | 0.9200 | 0.4975 | 0.9675 | 0.7875 | 0.7875 | +0.099 | 0.9500 |
| 10 | 0.6 | 1.0 | 0.0904 | 1.0000 | 1.0000 | 1.0000 | 0.1800 | 1.0000 | 0.0925 | 0.0925 | -0.032 | 0.9300 |
| 10 | 0.8 | 0.25 | 0.0384 | 0.5550 | 0.2400 | 0.9950 | 0.9850 | 1.0000 | 0.9950 | 0.5550 | +0.298 | 1.0000 |
| 10 | 0.8 | 0.5 | 0.0385 | 0.7125 | 0.4100 | 0.9675 | 0.8775 | 0.9950 | 0.9275 | 0.6875 | +0.226 | 0.9750 |
| 10 | 0.8 | 0.75 | 0.0387 | 0.8775 | 0.6425 | 0.9900 | 0.7175 | 0.9975 | 0.6050 | 0.5550 | +0.076 | 0.9850 |
| 10 | 0.8 | 1.0 | 0.0382 | 0.9525 | 0.8400 | 1.0000 | 0.4875 | 1.0000 | 0.0775 | 0.0725 | -0.083 | 0.9525 |
| 10 | 0.9 | 0.25 | 0.0167 | 0.1500 | 0.0325 | 0.9825 | 0.9775 | 0.9975 | 0.9725 | 0.1475 | +0.462 | 0.9875 |
| 10 | 0.9 | 0.5 | 0.0169 | 0.2475 | 0.0750 | 0.9850 | 0.9400 | 1.0000 | 0.9000 | 0.2400 | +0.245 | 0.9875 |
| 10 | 0.9 | 0.75 | 0.0166 | 0.3800 | 0.1400 | 0.9925 | 0.8850 | 0.9975 | 0.5050 | 0.2350 | +0.041 | 0.9900 |
| 10 | 0.9 | 1.0 | 0.0168 | 0.5275 | 0.2675 | 0.9900 | 0.8025 | 0.9900 | 0.0775 | 0.0375 | -0.135 | 0.9825 |
| 10 | 0.95 | 0.25 | 0.0074 | 0.1025 | 0.0300 | 0.9825 | 0.9750 | 0.9925 | 0.9800 | 0.1025 | +0.439 | 0.9850 |
| 10 | 0.95 | 0.5 | 0.0074 | 0.0875 | 0.0300 | 0.9975 | 0.9900 | 0.9975 | 0.8575 | 0.0825 | +0.202 | 1.0000 |
| 10 | 0.95 | 0.75 | 0.0074 | 0.1275 | 0.0275 | 0.9900 | 0.9400 | 0.9975 | 0.4225 | 0.0725 | -0.016 | 0.9900 |
| 10 | 0.95 | 1.0 | 0.0075 | 0.1550 | 0.0550 | 0.9975 | 0.9150 | 0.9975 | 0.1050 | 0.0075 | -0.189 | 0.9875 |
| 10 | 0.98 | 0.25 | 0.0025 | 0.0300 | 0.0050 | 0.9950 | 0.9925 | 0.9950 | 0.9775 | 0.0300 | +0.455 | 0.9850 |
| 10 | 0.98 | 0.5 | 0.0025 | 0.0375 | 0.0025 | 0.9975 | 0.9850 | 1.0000 | 0.8225 | 0.0325 | +0.102 | 0.9950 |
| 10 | 0.98 | 0.75 | 0.0025 | 0.0325 | 0.0075 | 1.0000 | 0.9875 | 0.9975 | 0.3750 | 0.0150 | -0.079 | 0.9975 |
| 10 | 0.98 | 1.0 | 0.0025 | 0.0400 | 0.0050 | 1.0000 | 0.9800 | 1.0000 | 0.0600 | 0.0025 | -0.269 | 0.9975 |
| 16 | 0.0 | 0.25 | 0.3433 | 1.0000 | 1.0000 | 0.9250 | 0.9250 | 0.9275 | 0.9600 | 0.9600 | +0.024 | 0.9325 |
| 16 | 0.0 | 0.5 | 0.3400 | 1.0000 | 1.0000 | 0.8975 | 0.8975 | 0.8875 | 0.9450 | 0.9450 | +0.039 | 0.9350 |
| 16 | 0.0 | 0.75 | 0.3405 | 1.0000 | 1.0000 | 0.7225 | 0.6725 | 0.7350 | 0.9500 | 0.9500 | +0.047 | 0.8925 |
| 16 | 0.0 | 1.0 | 0.3380 | 1.0000 | 1.0000 | 0.9875 | 0.1800 | 0.9875 | 0.0525 | 0.0525 | -0.006 | 0.7900 |
| 16 | 0.6 | 0.25 | 0.0908 | 1.0000 | 1.0000 | 0.9525 | 0.9550 | 0.9675 | 0.9700 | 0.9700 | +0.068 | 0.9725 |
| 16 | 0.6 | 0.5 | 0.0904 | 1.0000 | 1.0000 | 0.9075 | 0.8450 | 0.9425 | 0.9500 | 0.9500 | +0.110 | 0.9575 |
| 16 | 0.6 | 0.75 | 0.0904 | 1.0000 | 1.0000 | 0.9150 | 0.5900 | 0.9575 | 0.8625 | 0.8625 | +0.101 | 0.9800 |
| 16 | 0.6 | 1.0 | 0.0904 | 1.0000 | 1.0000 | 0.9925 | 0.1925 | 0.9925 | 0.0800 | 0.0800 | -0.023 | 0.9250 |
| 16 | 0.8 | 0.25 | 0.0388 | 0.7425 | 0.6850 | 0.9725 | 0.9600 | 0.9850 | 0.9775 | 0.7375 | +0.218 | 0.9750 |
| 16 | 0.8 | 0.5 | 0.0382 | 0.7975 | 0.7525 | 0.9525 | 0.8775 | 0.9825 | 0.9175 | 0.7675 | +0.191 | 0.9850 |
| 16 | 0.8 | 0.75 | 0.0382 | 0.9100 | 0.8925 | 0.9775 | 0.6900 | 0.9925 | 0.6350 | 0.6000 | +0.095 | 0.9800 |
| 16 | 0.8 | 1.0 | 0.0386 | 0.9900 | 0.9850 | 0.9975 | 0.3700 | 0.9975 | 0.0600 | 0.0600 | -0.047 | 0.9700 |
| 16 | 0.9 | 0.25 | 0.0167 | 0.0975 | 0.0925 | 0.9900 | 0.9850 | 1.0000 | 0.9925 | 0.0975 | +0.437 | 0.9875 |
| 16 | 0.9 | 0.5 | 0.0167 | 0.1550 | 0.1575 | 0.9925 | 0.9450 | 1.0000 | 0.9150 | 0.1475 | +0.230 | 0.9925 |
| 16 | 0.9 | 0.75 | 0.0165 | 0.3125 | 0.3375 | 0.9950 | 0.8400 | 1.0000 | 0.5550 | 0.2000 | +0.073 | 0.9850 |
| 16 | 0.9 | 1.0 | 0.0169 | 0.4100 | 0.4700 | 0.9950 | 0.6925 | 0.9950 | 0.0800 | 0.0325 | -0.096 | 0.9875 |
| 16 | 0.95 | 0.25 | 0.0075 | 0.0300 | 0.0350 | 0.9850 | 0.9725 | 0.9975 | 0.9800 | 0.0300 | +0.533 | 0.9850 |
| 16 | 0.95 | 0.5 | 0.0074 | 0.0225 | 0.0300 | 0.9950 | 0.9850 | 1.0000 | 0.8700 | 0.0225 | +0.222 | 1.0000 |
| 16 | 0.95 | 0.75 | 0.0074 | 0.0225 | 0.0325 | 1.0000 | 0.9500 | 1.0000 | 0.4100 | 0.0125 | +0.044 | 0.9875 |
| 16 | 0.95 | 1.0 | 0.0075 | 0.1050 | 0.1175 | 0.9975 | 0.8825 | 0.9975 | 0.0800 | 0.0025 | -0.172 | 0.9925 |
| 16 | 0.98 | 0.25 | 0.0025 | 0.0000 | 0.0025 | 0.9975 | 0.9975 | 0.9975 | 0.9950 | 0.0000 | – | 0.9975 |
| 16 | 0.98 | 0.5 | 0.0025 | 0.0050 | 0.0050 | 0.9925 | 0.9900 | 0.9975 | 0.8275 | 0.0050 | +0.384 | 0.9950 |
| 16 | 0.98 | 0.75 | 0.0025 | 0.0125 | 0.0125 | 1.0000 | 0.9900 | 1.0000 | 0.3350 | 0.0075 | -0.049 | 0.9975 |
| 16 | 0.98 | 1.0 | 0.0025 | 0.0075 | 0.0050 | 0.9975 | 0.9875 | 0.9975 | 0.0450 | 0.0000 | -0.143 | 0.9925 |

**Table 3 — the zero-gap cells.** The true gap is 0 and `F*` is undefined; what can be reported is the movement.

| `n` | cell | true movement | movement interval excludes 0 | …on the side of moving away | movement cover | Fieller bounded, V0 / V1 / V2 | gate pass, V0 / V1 |
|---|---|---|---|---|---|---|---|
| 10 | null | +0.0000 | 0.0025 | 0.0000 | 0.9975 | 0.0150 / 0.0075 / 0.0075 | 0.0400 / 0.0350 |
| 10 | antinoophor | -0.0621 | 0.9900 | 0.9900 | 0.9550 | 0.7400 / 0.0025 / 0.0025 | 0.0000 / 0.0075 |
| 16 | null | +0.0000 | 0.0050 | 0.0050 | 0.9950 | 0.0025 / 0.0000 / 0.0000 | 0.0000 / 0.0000 |
| 16 | antinoophor | -0.0634 | 0.9975 | 0.9975 | 0.9600 | 0.6950 / 0.0100 / 0.0100 | 0.0000 / 0.0025 |

**Table 4 — the simplest model of the Fieller sets' coverage loss.** A set of the observed median width, centred on the uncapped ratio with its observed bias, would cover with the probability shown. For each variant, the cells where every trial is reported and every set of that variant is bounded.

| `n` | `g` | `λ` | variant | bias of `M̂/Ĝ` | SE from width | predicted cover | observed cover |
|---|---|---|---|---|---|---|---|
| 10 | 0.0 | 0.25 | V0 | +0.0358 | 0.0828 | 0.9283 | 0.9125 |
| 10 | 0.0 | 0.25 | V2 | +0.0344 | 0.0828 | 0.9301 | 0.9175 |
| 10 | 0.0 | 0.5 | V0 | +0.0681 | 0.0653 | 0.8193 | 0.8450 |
| 10 | 0.0 | 0.5 | V2 | +0.0653 | 0.0662 | 0.8332 | 0.8525 |
| 10 | 0.0 | 0.75 | V0 | +0.0690 | 0.0474 | 0.6926 | 0.7125 |
| 10 | 0.0 | 0.75 | V2 | +0.0660 | 0.0490 | 0.7295 | 0.7500 |
| 10 | 0.0 | 1.0 | V0 | +0.0009 | 0.0341 | 0.9499 | 0.9950 |
| 10 | 0.0 | 1.0 | V2 | +0.0011 | 0.0389 | 0.9499 | 0.9950 |
| 10 | 0.6 | 1.0 | V0 | +0.0071 | 0.1375 | 0.9497 | 1.0000 |
| 16 | 0.0 | 0.25 | V0 | +0.0237 | 0.0601 | 0.9320 | 0.9250 |
| 16 | 0.0 | 0.25 | V2 | +0.0242 | 0.0603 | 0.9314 | 0.9275 |
| 16 | 0.0 | 0.5 | V0 | +0.0388 | 0.0467 | 0.8679 | 0.8975 |
| 16 | 0.0 | 0.5 | V2 | +0.0392 | 0.0466 | 0.8658 | 0.8875 |
| 16 | 0.0 | 0.75 | V0 | +0.0473 | 0.0344 | 0.7204 | 0.7225 |
| 16 | 0.0 | 0.75 | V2 | +0.0463 | 0.0347 | 0.7333 | 0.7350 |
| 16 | 0.0 | 1.0 | V0 | -0.0002 | 0.0238 | 0.9500 | 0.9875 |
| 16 | 0.0 | 1.0 | V2 | -0.0002 | 0.0256 | 0.9500 | 0.9875 |
| 16 | 0.6 | 0.25 | V0 | +0.0684 | 0.2104 | 0.9378 | 0.9525 |
| 16 | 0.6 | 0.25 | V2 | +0.0608 | 0.2098 | 0.9403 | 0.9675 |
| 16 | 0.6 | 0.5 | V0 | +0.1104 | 0.1563 | 0.8913 | 0.9075 |
| 16 | 0.6 | 0.5 | V2 | +0.0916 | 0.1658 | 0.9143 | 0.9425 |
| 16 | 0.6 | 0.75 | V0 | +0.1065 | 0.1193 | 0.8548 | 0.9150 |
| 16 | 0.6 | 0.75 | V2 | +0.0947 | 0.1396 | 0.8959 | 0.9575 |
| 16 | 0.6 | 1.0 | V0 | +0.0030 | 0.0899 | 0.9499 | 0.9925 |
| 16 | 0.6 | 1.0 | V2 | +0.0043 | 0.1243 | 0.9499 | 0.9925 |

**Table 5 — the gap each floor convention estimates**, where the true gap is small. *Added after the first registered run* (see Limits). V1 and V2 share a denominator. A gap estimate that moves with `λ` at fixed `g` is one the receiver is changing.

| `n` | cell | `g` | `λ` | true gap | mean `Ĝ`, V0 | share `Ĝ < 0`, V0 | mean `Ĝ`, V1 = V2 | share `Ĝ < 0`, V1 = V2 |
|---|---|---|---|---|---|---|---|---|
| 10 | grid | 0.9 | 0.25 | 0.0167 | +0.0074 | 0.2875 | +0.0047 | 0.3100 |
| 10 | grid | 0.9 | 0.5 | 0.0169 | +0.0121 | 0.1600 | +0.0052 | 0.3250 |
| 10 | grid | 0.9 | 0.75 | 0.0166 | +0.0161 | 0.0750 | +0.0047 | 0.3025 |
| 10 | grid | 0.9 | 1.0 | 0.0168 | +0.0209 | 0.0375 | +0.0053 | 0.3025 |
| 10 | grid | 0.95 | 0.25 | 0.0074 | +0.0044 | 0.3750 | +0.0019 | 0.4525 |
| 10 | grid | 0.95 | 0.5 | 0.0074 | +0.0055 | 0.3150 | +0.0012 | 0.4725 |
| 10 | grid | 0.95 | 0.75 | 0.0074 | +0.0084 | 0.2275 | +0.0018 | 0.4050 |
| 10 | grid | 0.95 | 1.0 | 0.0075 | +0.0104 | 0.1375 | +0.0016 | 0.4550 |
| 10 | grid | 0.98 | 0.25 | 0.0025 | +0.0011 | 0.4825 | +0.0002 | 0.5325 |
| 10 | grid | 0.98 | 0.5 | 0.0025 | +0.0011 | 0.4975 | -0.0005 | 0.5625 |
| 10 | grid | 0.98 | 0.75 | 0.0025 | +0.0026 | 0.3750 | -0.0001 | 0.5250 |
| 10 | grid | 0.98 | 1.0 | 0.0025 | +0.0033 | 0.3925 | -0.0001 | 0.5375 |
| 16 | grid | 0.9 | 0.25 | 0.0167 | +0.0089 | 0.1450 | +0.0065 | 0.1600 |
| 16 | grid | 0.9 | 0.5 | 0.0167 | +0.0117 | 0.0775 | +0.0069 | 0.1175 |
| 16 | grid | 0.9 | 0.75 | 0.0165 | +0.0161 | 0.0250 | +0.0071 | 0.1225 |
| 16 | grid | 0.9 | 1.0 | 0.0169 | +0.0189 | 0.0050 | +0.0062 | 0.1750 |
| 16 | grid | 0.95 | 0.25 | 0.0075 | +0.0042 | 0.2725 | +0.0021 | 0.3650 |
| 16 | grid | 0.95 | 0.5 | 0.0074 | +0.0055 | 0.2175 | +0.0019 | 0.4275 |
| 16 | grid | 0.95 | 0.75 | 0.0074 | +0.0067 | 0.1425 | +0.0014 | 0.3950 |
| 16 | grid | 0.95 | 1.0 | 0.0075 | +0.0097 | 0.0925 | +0.0020 | 0.3775 |
| 16 | grid | 0.98 | 0.25 | 0.0025 | +0.0009 | 0.4475 | +0.0002 | 0.5100 |
| 16 | grid | 0.98 | 0.5 | 0.0025 | +0.0021 | 0.3875 | +0.0002 | 0.5125 |
| 16 | grid | 0.98 | 0.75 | 0.0025 | +0.0025 | 0.3425 | +0.0001 | 0.5300 |
| 16 | grid | 0.98 | 1.0 | 0.0025 | +0.0038 | 0.2700 | +0.0006 | 0.4875 |
| 10 | null | 1.0 | – | 0.0000 | -0.0001 | 0.5300 | -0.0000 | 0.5275 |
| 10 | antinoophor | 1.0 | – | 0.0000 | -0.0320 | 1.0000 | -0.0000 | 0.5175 |
| 16 | null | 1.0 | – | 0.0000 | +0.0001 | 0.4875 | +0.0002 | 0.5325 |
| 16 | antinoophor | 1.0 | – | 0.0000 | -0.0209 | 0.9950 | +0.0009 | 0.4725 |

**Table 6 — the gap's own interval**, which the plan's report for want 2 puts beside the movement but whose coverage the plan did not register. *Computed after the registered run* (see Limits). `percentile` is the 2.5th–97.5th percentile of `G*`; `basic` reflects it about `Ĝ`. Coverage is of the true gap; `above 0` is the share of trials whose whole interval lies above zero.

| `n` | cell | `g` | `λ` | true gap | V0 percentile | V0 basic | V1 percentile | V1 basic | V0 percentile above 0 | V1 percentile above 0 |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | grid | 0.0 | 0.25 | 0.3384 | 0.8300 | 0.2275 | 0.8450 | 0.2300 | 1.0000 | 1.0000 |
| 10 | grid | 0.0 | 0.5 | 0.3387 | 0.8225 | 0.1750 | 0.8775 | 0.2100 | 1.0000 | 1.0000 |
| 10 | grid | 0.0 | 0.75 | 0.3390 | 0.6300 | 0.3325 | 0.8600 | 0.2125 | 1.0000 | 1.0000 |
| 10 | grid | 0.0 | 1.0 | 0.3391 | 0.3175 | 0.7700 | 0.8425 | 0.2250 | 1.0000 | 1.0000 |
| 10 | grid | 0.6 | 0.25 | 0.0906 | 0.8150 | 0.0875 | 0.8700 | 0.0525 | 1.0000 | 1.0000 |
| 10 | grid | 0.6 | 0.5 | 0.0894 | 0.6650 | 0.1000 | 0.8575 | 0.0200 | 1.0000 | 1.0000 |
| 10 | grid | 0.6 | 0.75 | 0.0909 | 0.5225 | 0.2275 | 0.8800 | 0.0225 | 1.0000 | 1.0000 |
| 10 | grid | 0.6 | 1.0 | 0.0904 | 0.3000 | 0.5525 | 0.9150 | 0.0200 | 1.0000 | 1.0000 |
| 10 | grid | 0.8 | 0.25 | 0.0384 | 0.6900 | 0.0425 | 0.7975 | 0.0050 | 1.0000 | 1.0000 |
| 10 | grid | 0.8 | 0.5 | 0.0385 | 0.5175 | 0.1350 | 0.7725 | 0.0175 | 1.0000 | 1.0000 |
| 10 | grid | 0.8 | 0.75 | 0.0387 | 0.3250 | 0.2350 | 0.7725 | 0.0125 | 1.0000 | 1.0000 |
| 10 | grid | 0.8 | 1.0 | 0.0382 | 0.1450 | 0.5825 | 0.7075 | 0.0125 | 1.0000 | 1.0000 |
| 10 | grid | 0.9 | 0.25 | 0.0167 | 0.4975 | 0.0925 | 0.5200 | 0.0200 | 0.9650 | 1.0000 |
| 10 | grid | 0.9 | 0.5 | 0.0169 | 0.3825 | 0.1775 | 0.5150 | 0.0250 | 0.9900 | 1.0000 |
| 10 | grid | 0.9 | 0.75 | 0.0166 | 0.2250 | 0.2675 | 0.4925 | 0.0300 | 1.0000 | 1.0000 |
| 10 | grid | 0.9 | 1.0 | 0.0168 | 0.1375 | 0.4325 | 0.5200 | 0.0375 | 1.0000 | 0.9975 |
| 10 | grid | 0.95 | 0.25 | 0.0074 | 0.2875 | 0.2050 | 0.2425 | 0.0750 | 0.9350 | 0.9850 |
| 10 | grid | 0.95 | 0.5 | 0.0074 | 0.2375 | 0.2200 | 0.2350 | 0.0725 | 0.9675 | 0.9850 |
| 10 | grid | 0.95 | 0.75 | 0.0074 | 0.1700 | 0.3125 | 0.2200 | 0.0575 | 0.9825 | 0.9950 |
| 10 | grid | 0.95 | 1.0 | 0.0075 | 0.1200 | 0.3650 | 0.2475 | 0.0650 | 0.9975 | 0.9875 |
| 10 | grid | 0.98 | 0.25 | 0.0025 | 0.2300 | 0.2375 | 0.1250 | 0.1375 | 0.8825 | 0.9700 |
| 10 | grid | 0.98 | 0.5 | 0.0025 | 0.2000 | 0.2200 | 0.1650 | 0.1250 | 0.8875 | 0.9300 |
| 10 | grid | 0.98 | 0.75 | 0.0025 | 0.1475 | 0.2650 | 0.1525 | 0.1350 | 0.9200 | 0.9375 |
| 10 | grid | 0.98 | 1.0 | 0.0025 | 0.1525 | 0.3100 | 0.1300 | 0.1225 | 0.9200 | 0.9525 |
| 16 | grid | 0.0 | 0.25 | 0.3433 | 0.8575 | 0.4375 | 0.8550 | 0.4525 | 1.0000 | 1.0000 |
| 16 | grid | 0.0 | 0.5 | 0.3400 | 0.8675 | 0.3675 | 0.8850 | 0.4275 | 1.0000 | 1.0000 |
| 16 | grid | 0.0 | 0.75 | 0.3405 | 0.7525 | 0.4175 | 0.8325 | 0.4300 | 1.0000 | 1.0000 |
| 16 | grid | 0.0 | 1.0 | 0.3380 | 0.4200 | 0.8150 | 0.8425 | 0.4675 | 1.0000 | 1.0000 |
| 16 | grid | 0.6 | 0.25 | 0.0908 | 0.9200 | 0.0700 | 0.9400 | 0.0575 | 1.0000 | 1.0000 |
| 16 | grid | 0.6 | 0.5 | 0.0904 | 0.8150 | 0.1425 | 0.8950 | 0.1025 | 1.0000 | 1.0000 |
| 16 | grid | 0.6 | 0.75 | 0.0904 | 0.7075 | 0.2050 | 0.9225 | 0.0725 | 1.0000 | 1.0000 |
| 16 | grid | 0.6 | 1.0 | 0.0904 | 0.3475 | 0.6400 | 0.9225 | 0.0775 | 1.0000 | 1.0000 |
| 16 | grid | 0.8 | 0.25 | 0.0388 | 0.7750 | 0.0575 | 0.8475 | 0.0150 | 1.0000 | 1.0000 |
| 16 | grid | 0.8 | 0.5 | 0.0382 | 0.6600 | 0.0925 | 0.8525 | 0.0100 | 1.0000 | 1.0000 |
| 16 | grid | 0.8 | 0.75 | 0.0382 | 0.4475 | 0.1875 | 0.8650 | 0.0225 | 1.0000 | 1.0000 |
| 16 | grid | 0.8 | 1.0 | 0.0386 | 0.2200 | 0.5250 | 0.8675 | 0.0100 | 1.0000 | 1.0000 |
| 16 | grid | 0.9 | 0.25 | 0.0167 | 0.5450 | 0.0750 | 0.5975 | 0.0200 | 0.9975 | 1.0000 |
| 16 | grid | 0.9 | 0.5 | 0.0167 | 0.4150 | 0.1125 | 0.6100 | 0.0175 | 0.9975 | 1.0000 |
| 16 | grid | 0.9 | 0.75 | 0.0165 | 0.2050 | 0.2575 | 0.5450 | 0.0200 | 1.0000 | 1.0000 |
| 16 | grid | 0.9 | 1.0 | 0.0169 | 0.1575 | 0.3750 | 0.6700 | 0.0075 | 1.0000 | 1.0000 |
| 16 | grid | 0.95 | 0.25 | 0.0075 | 0.3000 | 0.1200 | 0.3175 | 0.0475 | 0.9800 | 0.9975 |
| 16 | grid | 0.95 | 0.5 | 0.0074 | 0.2350 | 0.1575 | 0.3075 | 0.0525 | 0.9875 | 0.9975 |
| 16 | grid | 0.95 | 0.75 | 0.0074 | 0.1800 | 0.2125 | 0.3175 | 0.0425 | 0.9900 | 0.9950 |
| 16 | grid | 0.95 | 1.0 | 0.0075 | 0.0875 | 0.3375 | 0.3100 | 0.0475 | 1.0000 | 0.9900 |
| 16 | grid | 0.98 | 0.25 | 0.0025 | 0.1850 | 0.1550 | 0.1350 | 0.1100 | 0.9425 | 0.9800 |
| 16 | grid | 0.98 | 0.5 | 0.0025 | 0.1450 | 0.2275 | 0.1350 | 0.0975 | 0.9475 | 0.9875 |
| 16 | grid | 0.98 | 0.75 | 0.0025 | 0.1225 | 0.1875 | 0.1300 | 0.0800 | 0.9650 | 0.9875 |
| 16 | grid | 0.98 | 1.0 | 0.0025 | 0.0700 | 0.3125 | 0.0875 | 0.1050 | 0.9825 | 0.9850 |
| 10 | null | 1.0 | – | 0.0000 | 0.1650 | 0.2700 | 0.0625 | 0.2050 | 0.8350 | 0.9375 |
| 10 | antinoophor | 1.0 | – | 0.0000 | 0.9700 | 0.0000 | 0.0775 | 0.1950 | 0.0275 | 0.9225 |
| 16 | null | 1.0 | – | 0.0000 | 0.1175 | 0.2500 | 0.0400 | 0.2075 | 0.8825 | 0.9600 |
| 16 | antinoophor | 1.0 | – | 0.0000 | 0.9600 | 0.0025 | 0.0600 | 0.2475 | 0.0275 | 0.9400 |
<!-- tables:end -->

---

*Prose: CC BY 4.0. Code: Apache-2.0.*
