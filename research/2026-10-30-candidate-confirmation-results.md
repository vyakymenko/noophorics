# The candidate report on a generator it had not seen: the confirmation's results

**2026-10-30 · results of the offline confirmation registered in
[the plan](2026-10-30-candidate-confirmation-plan.md)**, committed before the
[code](../metrics/validation/confirm_candidate.py), itself committed before its
registered run. No model was called. Every measured number is in the
[saved record](candidate-confirmation.json). The tables below are generated from
it and checked against it, and the binomial probabilities are computed from its
counts. **C1, C2 and C3 failed; C4 and C5 held. By the plan's
rule there is no proposal: the candidate is not confirmed, and Problem 12 stays
as open as it was.**

## The run

The registered run was made at commit `461f21f`: 64 cells, 400 trials each, 400
bootstrap replicates per trial. `score()`, committed with the code, scored the
predictions. Fields were then added to the record to locate the failures (Tables
5–6, marked †). The full run was repeated, and every registered field came out
byte-for-byte identical in all 64 cells.

## The predictions

Table 1 has each prediction against its numbers. In brief:

- **C1 failed in two of 24 cells.** The Fieller set covered the true `F*` in
  0.9075–0.995 of trials with independent answers, and in at least 0.93 in 22 of
  the 24 grid cells. The two below are both at five options, `n = 10`, `λ = 0.75`:
  0.9225 at `g = 0.8` and 0.9075 at `g = 0.95`. At three options it covered
  0.9575–0.995 (Table 2).
- **C2 failed on two of its three clauses.** The movement's Wald interval covered
  0.9275–0.995, below 0.93 in one cell (five options, `n = 10`, `g = 0`,
  `λ = 0.25`) by one trial in 400. With a receiver moved away and no gap, at
  `n = 16` it excluded zero on the away side in 0.75 (three options) and 0.6775
  (five options) of trials, against the registered 0.80. With nothing moved, it
  excluded zero in 0.005–0.0275 of trials, within the registered 0.08 (Table 4).
- **C3 failed in seven of 24 cells.** The gap's Wald interval covered
  0.8275–0.99, below 0.90 in seven cells, all at five options. Five are at
  `n = 10` (`g = 0` and `g = 0.8` at both `λ`, and `g = 0.95` at `λ = 0.75`) and
  two at `n = 16` (`g = 0`, both `λ`). At three options it covered 0.92–0.99. In
  the null cells it lay wholly above zero in 0.015–0.095 of trials, within the
  registered 0.10.
- **C4 held in all 24 cells.** With correlated answers the Fieller set covered
  0.0825–0.8975 of trials, below 0.93 in every grid cell (Table 3).
- **C5 held.** At `g = 0.95` the share of bounded Fieller sets was
  0.035–0.1775. The median width of the bounded sets grows from 0.20–0.41 at
  `g = 0` to 2.12–3.06 at `g = 0.8` and 3.11–4.92 at `g = 0.95` (Table 2).

**How strict each bar was.** A coverage measured over 400 trials has a Monte
Carlo standard error of about 0.011 at 0.95. If a cell's true coverage were
exactly 0.95, it would read below 0.93 with probability about 0.031, and at
least one of 24 such cells would, with probability about 0.53. C1's bar could
therefore have failed on noise alone. Its lower cell could not easily have done
so: 363 or fewer of 400 has probability 0.0003 if the coverage is 0.95, and 0.007
for the lowest of 24 such cells, so that cell's coverage is below nominal.
Whether it is also below 0.93 is not settled (0.052 if it is 0.93). C2's grid
failure is 371 of 400 against a bar of 372. Its power clause is not near noise:
300 and 271 of 400 against a bar of 320 have probability 0.009 and 5.5 × 10⁻⁹ if
the power were 0.80. For C3's lowest cell, 331 or fewer of 400 has probability
6 × 10⁻⁶ if the coverage is 0.90, and 1.4 × 10⁻⁴ for the lowest of 24.
The failures stand as registered; this paragraph only says how far each one is
from noise. The plan named five options at `n = 10` in advance as the regime
where the candidate might fail, and C1's two failing cells and five of C3's
seven are there.

## Where the failing intervals went wrong †

*This section rests on fields added after the registered run, and on a model
chosen after the failures were seen (Tables 5 and 6; see Limits).* A Wald
interval misses either because it is off-centre or because it is too narrow. The
record now holds, per cell, the mean and standard deviation over trials of each
estimate's error, and the bootstrap's mean estimate of that standard deviation
(Table 5). Of these, only the gap's mean error was registered.

**The movement is centred.** With independent answers, its mean error lies
between −0.13 and +0.20 of its own spread in every grid cell. The bootstrap's
spread is 0.93–1.39 of the actual spread. The one failing cell has the lowest
ratio (0.93) and the largest mean error (+0.20) of the 24.

**The gap is not centred at five options.** The jackknife gap's mean error is
+0.0071 to +0.0215 bits at five options, which is 0.27–0.88 of its spread, and
+0.0011 to +0.0072 bits (0.07–0.49) at three. The ranges overlap: at five options
it is off-centre in passing cells as well as failing ones. A normal error with
the measured centre and spread reproduces the observed Wald coverage. In every
one of the 64 cells, for the gap and for the movement, observed and model differ
by less than 1.8 Monte Carlo standard errors of the model's coverage (Table 6's
caption). Within that model, Table 6 splits the seven failures:

- **At `g ≥ 0.8` (three cells):** the mean error alone, with the spread right,
  gives 0.857–0.884, and the spread alone gives 0.961–0.964.
- **At `g = 0` (four cells):** each alone gives 0.89–0.94, and together they give
  0.83–0.90, against the observed 0.83–0.89.

Under this model, which was chosen after the failures were seen, that says how
the coverage was lost. It does not say why the jackknife leaves
that error at five options; nothing here tests that.

**With correlated answers.** The plan's reason for C4 was that the bootstrap
understates the spread. It does: the bootstrap's spread is below the actual one
in 22 of the 24 grid cells for the gap (0.63–1.02 of it) and in 23 for the
movement (0.74–1.02). But the gap's mean error is also +0.031 to +0.107 bits,
1.18–3.54 times its spread. In Table 6 the mean error alone gives 0.057–0.782
across those cells, and the spread alone 0.784–0.955. **C4 held as a count. For
the gap's interval, the reason the plan gave accounts for the smaller part of the
lost coverage. The Fieller set, on which C4 is scored, is not decomposed here.**
The movement's mean error stays within −0.07 to +0.23 of its spread, and its
Wald interval covers 0.8525–0.965. The Fieller set covers 0.6875–0.8975 at
`λ = 0.25` and 0.0825–0.50 at `λ = 0.75`, lower at `λ = 0.75` in all twelve
pairs of cells (Table 3); nothing here tests why.

## With correlated answers, a gap where there is none

In the zero-gap cells with correlated answers, the gap's interval lies wholly
above zero — a gap reported where there is none — in 0.6625–0.7350 of trials
at three options and 0.955–0.9725 at five, whether the receiver moved or not.
The Fieller set is bounded in the same shares of trials. The two are one
condition, `Ĝ² > z²·var(G*)`, which the gap's interval also meets when it lies
wholly below zero. The movement's interval excluded zero in 0.0325–0.0775 of
null trials (Table 4).
With persistent answers, then, this report would state a gap that does not exist
in most trials. Its movement interval excludes zero in at most 0.0775 of null
trials, which is near its 0.05 level at `n = 16` and about 1.5 times it at
`n = 10`.

## What this does and does not change

**Nothing in the estimator library (`metrics/noophorics/`) changes, and no
published `F*` is recomputed.** The plan said a proposal would follow only if
C1, C2 and C3 held. None did. Problem 12 stays as open as it was, and the
jackknife-Fieller report with Wald intervals is still a candidate. It is now one
that has failed a confirmation.

What the run does show is a set of counts. With independent answers at three
options, every coverage clause held: the Fieller set at 0.9575–0.995, the
movement at 0.9625–0.995, the gap at 0.92–0.99. At five options the gap's
interval fell short in seven cells, the Fieller set in two, and the movement's
interval in one, by one trial in 400. Power against a receiver moved away at
`n = 16`, which the plan bounded at 0.80, was 0.6775–0.75 (0.335–0.365 at
`n = 10`, where nothing was registered). Correlated answers
broke the report's gap. No narrower proposal — three options only, say — is made
from this. Choosing that scope after seeing which cells passed is what the plan
was written to prevent.

## Choices fixed in the code before the registered run

The code's docstring records the details the plan left open: the trial seeds,
the Dirichlet sampler, that a fresh draw under persistence may land on the
previous answer, and that a bootstrap replicate redraws each party's counts as
a multinomial from its observed shares. The docstring does not record one more:
the code reads the plan's concentrations as the per-option parameter of a
symmetric Dirichlet, so the total concentration is 0.4 or 1.5 times the number
of options. The divergence caches are cleared at the
start of each trial to bound memory. They are pure functions of the counts, so
clearing them changes no value.

A smoke run of four cells at 20 trials each was executed for timing and seen
before the code was committed. One of those cells has independent answers
(three options, `n = 10`, `g = 0`, `λ = 0.25`) and three have correlated ones.
Its trials are the first 20 of the registered run's 400 in those cells: the
seeds are the same, and the code did not change between the smoke run and its
commit. The smoke run came after the plan's commit, `cf33566`.

**A correction to a commit message.** The message of `461f21f` says fifteen
mutations of the module were each caught by its tests. Ten distinct mutations
were run, and all ten were caught. A first batch stopped after four on a search
pattern that matched twice, and a second batch ran six. The commit is pushed and
is not amended; this paragraph is the correction.

## Limits

The plan's limits stand: synthetic agents, one new generator family, one kind of
dependence (persistence), a fixed frame, and the candidate tested as frozen.

- 400 trials per cell. The Monte Carlo standard error of a coverage is about
  0.011 at 0.95 and 0.013 at 0.93, and a per-cell bar over 24 cells is strict
  (see above).
- The distributions are redrawn every trial, so a cell's "true gap" is a mean
  over trials. Coverage is over the generator, not of one fixed truth.
- The plan set C2's power bar without computing the true movement it would face.
  That movement is −0.041 bits at three options and −0.048 at five (Table 5).
- **Fields added after the registered run:** per-trial bootstrap spreads (kept
  in the record as per-cell means), the movement's mean error, both errors'
  standard deviations, and the true movement (the † columns of Table 5, and
  Table 6). The gap's mean error was registered. The run was repeated, and every
  registered field came out byte-for-byte identical in all 64 cells. The normal
  model in Table 6 was chosen after the failures were seen.
- **Tests added after the registered run.** A same-model review found that the
  committed tests left fifteen mutations of the module green. Four tests were
  added to `test_confirm_candidate.py`: the plan's constants, every per-trial
  field rebuilt from its parts, the truth mixed as registered, and the summary's
  shares. They pass on the committed code, which did not change, and turn all
  twenty-five mutations tried, those fifteen included, red.

<!-- tables:start -->
**Table 1 — the predictions, scored as registered.** C1–C3 are scored on the 24 grid cells with independent answers, C2 and C3 also on the zero-gap cells with independent answers, C5 on the 8 grid cells at `g = 0.95` with independent answers, and C4 on the 24 grid cells with correlated ones.

| prediction | held? | the numbers it turned on |
|---|---|---|
| C1: Fieller set covers ≥ 0.93 in every grid cell, `ρ = 0` | **no** | 0.9075–0.9950; below 0.93 in 2 of 24 cells |
| C2: movement Wald covers ≥ 0.93 in every grid cell; antinoophor at `n = 16` excludes zero away in ≥ 0.80; nulls exclude zero in ≤ 0.08 | **no** | covers 0.9275–0.9950, below 0.93 in 1 of 24 cells; antinoophor 0.6775–0.7500; nulls 0.0050–0.0275 |
| C3: gap Wald covers ≥ 0.90 in every grid cell; above zero in ≤ 0.10 of null trials | **no** | covers 0.8275–0.9900, below 0.90 in 7 of 24 cells; nulls above zero 0.0150–0.0950 |
| C4: at `ρ = 0.3`, Fieller covers < 0.93 in at least half the grid cells | **yes** | 24 of 24 cells; coverage 0.0825–0.8975 |
| C5: bounded share < 0.5 at `g = 0.95` in every grid cell, `ρ = 0` | **yes** | 0.0350–0.1775 |

**Table 2 — independent answers (`ρ = 0`), every grid cell.** Coverage of the true `F*` by the Fieller set, the share of bounded sets and their median width, coverage of the true movement and gap by their Wald intervals, and the mean error of the jackknife gap.

| `K` | `n` | `g` | `λ` | true gap | Fieller cover | bounded | median width | movement Wald cover | gap Wald cover | mean error of `Ĝ` |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 10 | 0.0 | 0.25 | 0.2525 | 0.9650 | 1.0000 | 0.4072 | 0.9625 | 0.9200 | +0.0048 |
| 3 | 10 | 0.0 | 0.75 | 0.2538 | 0.9575 | 1.0000 | 0.2837 | 0.9650 | 0.9250 | +0.0056 |
| 3 | 10 | 0.8 | 0.25 | 0.0233 | 0.9875 | 0.3075 | 3.0550 | 0.9925 | 0.9650 | +0.0037 |
| 3 | 10 | 0.8 | 0.75 | 0.0232 | 0.9775 | 0.2875 | 2.5062 | 0.9775 | 0.9650 | +0.0044 |
| 3 | 10 | 0.95 | 0.25 | 0.0037 | 0.9850 | 0.0375 | 4.4820 | 0.9875 | 0.9775 | +0.0046 |
| 3 | 10 | 0.95 | 0.75 | 0.0035 | 0.9650 | 0.0625 | 3.6653 | 0.9750 | 0.9575 | +0.0072 |
| 3 | 16 | 0.0 | 0.25 | 0.2523 | 0.9575 | 1.0000 | 0.2964 | 0.9625 | 0.9425 | +0.0027 |
| 3 | 16 | 0.0 | 0.75 | 0.2529 | 0.9850 | 1.0000 | 0.1964 | 0.9700 | 0.9450 | +0.0016 |
| 3 | 16 | 0.8 | 0.25 | 0.0235 | 0.9950 | 0.5250 | 2.8106 | 0.9925 | 0.9900 | +0.0018 |
| 3 | 16 | 0.8 | 0.75 | 0.0233 | 0.9900 | 0.4575 | 2.2935 | 0.9850 | 0.9700 | +0.0011 |
| 3 | 16 | 0.95 | 0.25 | 0.0036 | 0.9825 | 0.0550 | 3.5511 | 0.9825 | 0.9700 | +0.0029 |
| 3 | 16 | 0.95 | 0.75 | 0.0035 | 0.9875 | 0.0350 | 4.2855 | 0.9950 | 0.9800 | +0.0031 |
| 5 | 10 | 0.0 | 0.25 | 0.3046 | 0.9500 | 1.0000 | 0.3637 | 0.9275 | 0.8275 | +0.0215 |
| 5 | 10 | 0.0 | 0.75 | 0.3005 | 0.9450 | 1.0000 | 0.2950 | 0.9450 | 0.8625 | +0.0214 |
| 5 | 10 | 0.8 | 0.25 | 0.0274 | 0.9700 | 0.4800 | 2.8074 | 0.9850 | 0.8975 | +0.0181 |
| 5 | 10 | 0.8 | 0.75 | 0.0274 | 0.9225 | 0.4625 | 2.6228 | 0.9650 | 0.8900 | +0.0165 |
| 5 | 10 | 0.95 | 0.25 | 0.0042 | 0.9625 | 0.1050 | 4.9186 | 0.9850 | 0.9350 | +0.0165 |
| 5 | 10 | 0.95 | 0.75 | 0.0043 | 0.9075 | 0.1775 | 4.3674 | 0.9725 | 0.8850 | +0.0183 |
| 5 | 16 | 0.0 | 0.25 | 0.3038 | 0.9750 | 1.0000 | 0.2855 | 0.9600 | 0.8825 | +0.0071 |
| 5 | 16 | 0.0 | 0.75 | 0.3018 | 0.9675 | 1.0000 | 0.2116 | 0.9475 | 0.8900 | +0.0081 |
| 5 | 16 | 0.8 | 0.25 | 0.0275 | 0.9900 | 0.5675 | 2.3210 | 0.9825 | 0.9325 | +0.0074 |
| 5 | 16 | 0.8 | 0.75 | 0.0272 | 0.9600 | 0.5425 | 2.1157 | 0.9925 | 0.9400 | +0.0072 |
| 5 | 16 | 0.95 | 0.25 | 0.0042 | 0.9850 | 0.0725 | 4.2414 | 0.9825 | 0.9675 | +0.0086 |
| 5 | 16 | 0.95 | 0.75 | 0.0041 | 0.9775 | 0.0725 | 3.1149 | 0.9925 | 0.9425 | +0.0078 |

**Table 3 — correlated answers (`ρ = 0.3`), every grid cell.** The same columns.

| `K` | `n` | `g` | `λ` | true gap | Fieller cover | bounded | median width | movement Wald cover | gap Wald cover | mean error of `Ĝ` |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 10 | 0.0 | 0.25 | 0.2559 | 0.8175 | 1.0000 | 0.3418 | 0.8575 | 0.4400 | +0.0564 |
| 3 | 10 | 0.0 | 0.75 | 0.2539 | 0.4350 | 1.0000 | 0.2581 | 0.8525 | 0.3950 | +0.0596 |
| 3 | 10 | 0.8 | 0.25 | 0.0235 | 0.8500 | 0.9425 | 1.5653 | 0.9175 | 0.3325 | +0.0487 |
| 3 | 10 | 0.8 | 0.75 | 0.0235 | 0.4075 | 0.9600 | 1.3883 | 0.9125 | 0.3175 | +0.0478 |
| 3 | 10 | 0.95 | 0.25 | 0.0036 | 0.8750 | 0.8300 | 2.3172 | 0.9375 | 0.2450 | +0.0481 |
| 3 | 10 | 0.95 | 0.75 | 0.0036 | 0.4225 | 0.8025 | 2.2059 | 0.9250 | 0.2925 | +0.0474 |
| 3 | 16 | 0.0 | 0.25 | 0.2521 | 0.8075 | 1.0000 | 0.2752 | 0.8650 | 0.5750 | +0.0339 |
| 3 | 16 | 0.0 | 0.75 | 0.2530 | 0.5000 | 1.0000 | 0.1904 | 0.8775 | 0.5175 | +0.0389 |
| 3 | 16 | 0.8 | 0.25 | 0.0233 | 0.8700 | 0.9925 | 1.4430 | 0.9350 | 0.3850 | +0.0316 |
| 3 | 16 | 0.8 | 0.75 | 0.0235 | 0.4225 | 0.9625 | 1.1029 | 0.9300 | 0.3650 | +0.0328 |
| 3 | 16 | 0.95 | 0.25 | 0.0036 | 0.8975 | 0.8450 | 2.2452 | 0.9650 | 0.2725 | +0.0318 |
| 3 | 16 | 0.95 | 0.75 | 0.0036 | 0.4300 | 0.8175 | 2.1210 | 0.9450 | 0.2825 | +0.0312 |
| 5 | 10 | 0.0 | 0.25 | 0.3039 | 0.6875 | 1.0000 | 0.2903 | 0.8550 | 0.1075 | +0.1074 |
| 5 | 10 | 0.0 | 0.75 | 0.3045 | 0.0825 | 1.0000 | 0.2393 | 0.8725 | 0.1025 | +0.1045 |
| 5 | 10 | 0.8 | 0.25 | 0.0274 | 0.7575 | 0.9950 | 1.0182 | 0.9100 | 0.0300 | +0.0956 |
| 5 | 10 | 0.8 | 0.75 | 0.0273 | 0.1100 | 1.0000 | 0.9232 | 0.9275 | 0.0300 | +0.0965 |
| 5 | 10 | 0.95 | 0.25 | 0.0043 | 0.7875 | 0.9775 | 1.4023 | 0.9350 | 0.0500 | +0.0893 |
| 5 | 10 | 0.95 | 0.75 | 0.0042 | 0.0900 | 0.9575 | 1.3374 | 0.9225 | 0.0575 | +0.0891 |
| 5 | 16 | 0.0 | 0.25 | 0.3035 | 0.7475 | 1.0000 | 0.2401 | 0.8625 | 0.1850 | +0.0700 |
| 5 | 16 | 0.0 | 0.75 | 0.3027 | 0.1100 | 1.0000 | 0.1868 | 0.8950 | 0.1975 | +0.0684 |
| 5 | 16 | 0.8 | 0.25 | 0.0274 | 0.8025 | 1.0000 | 0.9850 | 0.9250 | 0.0675 | +0.0620 |
| 5 | 16 | 0.8 | 0.75 | 0.0274 | 0.1400 | 0.9975 | 0.8544 | 0.9100 | 0.0550 | +0.0635 |
| 5 | 16 | 0.95 | 0.25 | 0.0042 | 0.8000 | 0.9850 | 1.4040 | 0.9300 | 0.0350 | +0.0611 |
| 5 | 16 | 0.95 | 0.75 | 0.0042 | 0.1200 | 0.9775 | 1.3887 | 0.9225 | 0.0450 | +0.0599 |

**Table 4 — the zero-gap cells.** The share of trials whose movement interval excludes zero, excludes it on the side of moving away, and whose gap interval lies wholly above zero; and the share of bounded Fieller sets.

| `K` | `ρ` | `n` | cell | movement excludes 0 | movement away | gap above 0 | Fieller bounded | mean error of `Ĝ` |
|---|---|---|---|---|---|---|---|---|
| 3 | 0.0 | 10 | null | 0.0150 | 0.0075 | 0.0275 | 0.0300 | +0.0052 |
| 3 | 0.0 | 10 | antinoophor | 0.3650 | 0.3650 | 0.0325 | 0.0350 | +0.0053 |
| 3 | 0.0 | 16 | null | 0.0050 | 0.0000 | 0.0150 | 0.0150 | +0.0024 |
| 3 | 0.0 | 16 | antinoophor | 0.7500 | 0.7500 | 0.0250 | 0.0275 | +0.0029 |
| 3 | 0.3 | 10 | null | 0.0775 | 0.0425 | 0.6775 | 0.6775 | +0.0442 |
| 3 | 0.3 | 10 | antinoophor | 0.4100 | 0.4100 | 0.7350 | 0.7350 | +0.0462 |
| 3 | 0.3 | 16 | null | 0.0325 | 0.0200 | 0.6625 | 0.6625 | +0.0295 |
| 3 | 0.3 | 16 | antinoophor | 0.6875 | 0.6875 | 0.7200 | 0.7200 | +0.0303 |
| 5 | 0.0 | 10 | null | 0.0275 | 0.0150 | 0.0950 | 0.0950 | +0.0163 |
| 5 | 0.0 | 10 | antinoophor | 0.3350 | 0.3350 | 0.0975 | 0.1000 | +0.0163 |
| 5 | 0.0 | 16 | null | 0.0175 | 0.0075 | 0.0475 | 0.0500 | +0.0077 |
| 5 | 0.0 | 16 | antinoophor | 0.6775 | 0.6775 | 0.0525 | 0.0525 | +0.0078 |
| 5 | 0.3 | 10 | null | 0.0750 | 0.0375 | 0.9550 | 0.9550 | +0.0867 |
| 5 | 0.3 | 10 | antinoophor | 0.4550 | 0.4550 | 0.9725 | 0.9725 | +0.0884 |
| 5 | 0.3 | 16 | null | 0.0550 | 0.0250 | 0.9675 | 0.9675 | +0.0574 |
| 5 | 0.3 | 16 | antinoophor | 0.6550 | 0.6550 | 0.9550 | 0.9550 | +0.0571 |

**Table 5 — the errors' spread beside the bootstrap's estimate of it †, every cell.** For the movement and the gap: the true value's mean over trials, the mean and standard deviation over trials of the estimate's error, the mean bootstrap standard deviation, the bootstrap's spread as a share of the actual one, and the mean error in units of the actual spread.

| `K` | `ρ` | `n` | cell | true movement † | `M̂` error † | `M̂` error sd † | `M*` sd † | ratio † | bias/sd † | true gap | `Ĝ` error | `Ĝ` error sd † | `G*` sd † | ratio † | bias/sd † |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 0.0 | 10 | g 0.0, λ 0.25 | +0.0991 | +0.0001 | 0.0295 | 0.0311 | 1.05 | +0.00 | 0.2525 | +0.0048 | 0.0296 | 0.0264 | 0.89 | +0.16 |
| 3 | 0.0 | 10 | g 0.0, λ 0.75 | +0.2221 | +0.0018 | 0.0274 | 0.0295 | 1.08 | +0.07 | 0.2538 | +0.0056 | 0.0276 | 0.0265 | 0.96 | +0.20 |
| 3 | 0.0 | 10 | g 0.8, λ 0.25 | +0.0075 | -0.0012 | 0.0180 | 0.0228 | 1.27 | -0.07 | 0.0233 | +0.0037 | 0.0171 | 0.0185 | 1.08 | +0.22 |
| 3 | 0.0 | 10 | g 0.8, λ 0.75 | +0.0197 | -0.0006 | 0.0183 | 0.0223 | 1.21 | -0.03 | 0.0232 | +0.0044 | 0.0165 | 0.0185 | 1.12 | +0.27 |
| 3 | 0.0 | 10 | g 0.95, λ 0.25 | +0.0012 | -0.0008 | 0.0178 | 0.0208 | 1.17 | -0.04 | 0.0037 | +0.0046 | 0.0144 | 0.0170 | 1.18 | +0.32 |
| 3 | 0.0 | 10 | g 0.95, λ 0.75 | +0.0030 | +0.0009 | 0.0172 | 0.0208 | 1.21 | +0.05 | 0.0035 | +0.0072 | 0.0146 | 0.0171 | 1.17 | +0.49 |
| 3 | 0.0 | 16 | g 0.0, λ 0.25 | +0.0993 | +0.0016 | 0.0208 | 0.0231 | 1.11 | +0.08 | 0.2523 | +0.0027 | 0.0210 | 0.0205 | 0.98 | +0.13 |
| 3 | 0.0 | 16 | g 0.0, λ 0.75 | +0.2213 | +0.0000 | 0.0198 | 0.0218 | 1.10 | +0.00 | 0.2529 | +0.0016 | 0.0215 | 0.0205 | 0.95 | +0.07 |
| 3 | 0.0 | 16 | g 0.8, λ 0.25 | +0.0076 | -0.0003 | 0.0113 | 0.0154 | 1.36 | -0.03 | 0.0235 | +0.0018 | 0.0102 | 0.0126 | 1.23 | +0.18 |
| 3 | 0.0 | 16 | g 0.8, λ 0.75 | +0.0197 | -0.0016 | 0.0122 | 0.0151 | 1.24 | -0.13 | 0.0233 | +0.0011 | 0.0111 | 0.0127 | 1.14 | +0.10 |
| 3 | 0.0 | 16 | g 0.95, λ 0.25 | +0.0012 | -0.0002 | 0.0111 | 0.0138 | 1.25 | -0.02 | 0.0036 | +0.0029 | 0.0095 | 0.0113 | 1.19 | +0.31 |
| 3 | 0.0 | 16 | g 0.95, λ 0.75 | +0.0030 | +0.0000 | 0.0100 | 0.0139 | 1.39 | +0.00 | 0.0035 | +0.0031 | 0.0091 | 0.0114 | 1.26 | +0.34 |
| 3 | 0.3 | 10 | g 0.0, λ 0.25 | +0.1006 | +0.0005 | 0.0394 | 0.0311 | 0.79 | +0.01 | 0.2559 | +0.0564 | 0.0375 | 0.0254 | 0.68 | +1.50 |
| 3 | 0.3 | 10 | g 0.0, λ 0.75 | +0.2222 | +0.0092 | 0.0402 | 0.0297 | 0.74 | +0.23 | 0.2539 | +0.0596 | 0.0364 | 0.0253 | 0.69 | +1.64 |
| 3 | 0.3 | 10 | g 0.8, λ 0.25 | +0.0076 | -0.0009 | 0.0282 | 0.0243 | 0.86 | -0.03 | 0.0235 | +0.0487 | 0.0218 | 0.0195 | 0.89 | +2.23 |
| 3 | 0.3 | 10 | g 0.8, λ 0.75 | +0.0199 | +0.0005 | 0.0271 | 0.0238 | 0.88 | +0.02 | 0.0235 | +0.0478 | 0.0216 | 0.0195 | 0.90 | +2.22 |
| 3 | 0.3 | 10 | g 0.95, λ 0.25 | +0.0012 | +0.0021 | 0.0234 | 0.0223 | 0.95 | +0.09 | 0.0036 | +0.0481 | 0.0187 | 0.0181 | 0.97 | +2.57 |
| 3 | 0.3 | 10 | g 0.95, λ 0.75 | +0.0030 | +0.0016 | 0.0240 | 0.0222 | 0.92 | +0.07 | 0.0036 | +0.0474 | 0.0213 | 0.0181 | 0.85 | +2.22 |
| 3 | 0.3 | 16 | g 0.0, λ 0.25 | +0.0993 | -0.0021 | 0.0307 | 0.0235 | 0.77 | -0.07 | 0.2521 | +0.0339 | 0.0288 | 0.0200 | 0.69 | +1.18 |
| 3 | 0.3 | 16 | g 0.0, λ 0.75 | +0.2213 | +0.0061 | 0.0278 | 0.0224 | 0.80 | +0.22 | 0.2530 | +0.0389 | 0.0272 | 0.0199 | 0.73 | +1.43 |
| 3 | 0.3 | 16 | g 0.8, λ 0.25 | +0.0076 | -0.0002 | 0.0176 | 0.0170 | 0.96 | -0.01 | 0.0233 | +0.0316 | 0.0140 | 0.0137 | 0.98 | +2.26 |
| 3 | 0.3 | 16 | g 0.8, λ 0.75 | +0.0199 | +0.0010 | 0.0182 | 0.0165 | 0.91 | +0.06 | 0.0235 | +0.0328 | 0.0161 | 0.0137 | 0.85 | +2.03 |
| 3 | 0.3 | 16 | g 0.95, λ 0.25 | +0.0012 | +0.0014 | 0.0150 | 0.0153 | 1.02 | +0.09 | 0.0036 | +0.0318 | 0.0122 | 0.0125 | 1.02 | +2.60 |
| 3 | 0.3 | 16 | g 0.95, λ 0.75 | +0.0030 | +0.0000 | 0.0157 | 0.0153 | 0.97 | +0.00 | 0.0036 | +0.0312 | 0.0123 | 0.0125 | 1.02 | +2.54 |
| 5 | 0.0 | 10 | g 0.0, λ 0.25 | +0.1222 | +0.0079 | 0.0384 | 0.0359 | 0.93 | +0.20 | 0.3046 | +0.0215 | 0.0340 | 0.0291 | 0.86 | +0.63 |
| 5 | 0.0 | 10 | g 0.0, λ 0.75 | +0.2638 | +0.0063 | 0.0344 | 0.0346 | 1.01 | +0.18 | 0.3005 | +0.0214 | 0.0354 | 0.0290 | 0.82 | +0.61 |
| 5 | 0.0 | 10 | g 0.8, λ 0.25 | +0.0089 | -0.0002 | 0.0248 | 0.0294 | 1.19 | -0.01 | 0.0274 | +0.0181 | 0.0223 | 0.0235 | 1.05 | +0.81 |
| 5 | 0.0 | 10 | g 0.8, λ 0.75 | +0.0232 | -0.0012 | 0.0262 | 0.0287 | 1.10 | -0.05 | 0.0274 | +0.0165 | 0.0221 | 0.0235 | 1.06 | +0.75 |
| 5 | 0.0 | 10 | g 0.95, λ 0.25 | +0.0014 | -0.0015 | 0.0236 | 0.0274 | 1.16 | -0.06 | 0.0042 | +0.0165 | 0.0186 | 0.0222 | 1.20 | +0.88 |
| 5 | 0.0 | 10 | g 0.95, λ 0.75 | +0.0036 | +0.0015 | 0.0235 | 0.0271 | 1.15 | +0.07 | 0.0043 | +0.0183 | 0.0207 | 0.0222 | 1.07 | +0.88 |
| 5 | 0.0 | 16 | g 0.0, λ 0.25 | +0.1220 | +0.0020 | 0.0265 | 0.0268 | 1.01 | +0.07 | 0.3038 | +0.0071 | 0.0266 | 0.0227 | 0.85 | +0.27 |
| 5 | 0.0 | 16 | g 0.0, λ 0.75 | +0.2649 | +0.0012 | 0.0246 | 0.0257 | 1.04 | +0.05 | 0.3018 | +0.0081 | 0.0259 | 0.0227 | 0.88 | +0.31 |
| 5 | 0.0 | 16 | g 0.8, λ 0.25 | +0.0089 | +0.0006 | 0.0166 | 0.0200 | 1.20 | +0.04 | 0.0275 | +0.0074 | 0.0154 | 0.0162 | 1.05 | +0.48 |
| 5 | 0.0 | 16 | g 0.8, λ 0.75 | +0.0230 | -0.0016 | 0.0155 | 0.0197 | 1.27 | -0.10 | 0.0272 | +0.0072 | 0.0150 | 0.0162 | 1.08 | +0.48 |
| 5 | 0.0 | 16 | g 0.95, λ 0.25 | +0.0013 | -0.0009 | 0.0152 | 0.0186 | 1.22 | -0.06 | 0.0042 | +0.0086 | 0.0121 | 0.0151 | 1.24 | +0.71 |
| 5 | 0.0 | 16 | g 0.95, λ 0.75 | +0.0035 | +0.0001 | 0.0136 | 0.0184 | 1.35 | +0.01 | 0.0041 | +0.0078 | 0.0125 | 0.0151 | 1.21 | +0.63 |
| 5 | 0.3 | 10 | g 0.0, λ 0.25 | +0.1220 | +0.0058 | 0.0455 | 0.0347 | 0.76 | +0.13 | 0.3039 | +0.1074 | 0.0428 | 0.0270 | 0.63 | +2.51 |
| 5 | 0.3 | 10 | g 0.0, λ 0.75 | +0.2673 | +0.0085 | 0.0440 | 0.0340 | 0.77 | +0.19 | 0.3045 | +0.1045 | 0.0406 | 0.0272 | 0.67 | +2.57 |
| 5 | 0.3 | 10 | g 0.8, λ 0.25 | +0.0089 | +0.0035 | 0.0344 | 0.0303 | 0.88 | +0.10 | 0.0274 | +0.0956 | 0.0287 | 0.0241 | 0.84 | +3.33 |
| 5 | 0.3 | 10 | g 0.8, λ 0.75 | +0.0231 | +0.0054 | 0.0317 | 0.0295 | 0.93 | +0.17 | 0.0273 | +0.0965 | 0.0272 | 0.0239 | 0.88 | +3.54 |
| 5 | 0.3 | 10 | g 0.95, λ 0.25 | +0.0014 | +0.0016 | 0.0307 | 0.0284 | 0.93 | +0.05 | 0.0043 | +0.0893 | 0.0263 | 0.0229 | 0.87 | +3.40 |
| 5 | 0.3 | 10 | g 0.95, λ 0.75 | +0.0036 | +0.0015 | 0.0311 | 0.0282 | 0.91 | +0.05 | 0.0042 | +0.0891 | 0.0271 | 0.0229 | 0.85 | +3.29 |
| 5 | 0.3 | 16 | g 0.0, λ 0.25 | +0.1217 | +0.0033 | 0.0344 | 0.0267 | 0.78 | +0.10 | 0.3035 | +0.0700 | 0.0305 | 0.0216 | 0.71 | +2.29 |
| 5 | 0.3 | 16 | g 0.0, λ 0.75 | +0.2658 | +0.0040 | 0.0315 | 0.0258 | 0.82 | +0.13 | 0.3027 | +0.0684 | 0.0299 | 0.0216 | 0.72 | +2.29 |
| 5 | 0.3 | 16 | g 0.8, λ 0.25 | +0.0088 | -0.0000 | 0.0232 | 0.0215 | 0.93 | -0.00 | 0.0274 | +0.0620 | 0.0192 | 0.0172 | 0.89 | +3.24 |
| 5 | 0.3 | 16 | g 0.8, λ 0.75 | +0.0232 | +0.0028 | 0.0236 | 0.0210 | 0.89 | +0.12 | 0.0274 | +0.0635 | 0.0197 | 0.0171 | 0.87 | +3.22 |
| 5 | 0.3 | 16 | g 0.95, λ 0.25 | +0.0014 | +0.0014 | 0.0217 | 0.0200 | 0.92 | +0.06 | 0.0042 | +0.0611 | 0.0177 | 0.0162 | 0.92 | +3.44 |
| 5 | 0.3 | 16 | g 0.95, λ 0.75 | +0.0036 | +0.0010 | 0.0221 | 0.0198 | 0.90 | +0.05 | 0.0042 | +0.0599 | 0.0176 | 0.0162 | 0.92 | +3.40 |
| 3 | 0.0 | 10 | null | +0.0000 | -0.0001 | 0.0164 | 0.0203 | 1.24 | -0.01 | 0.0000 | +0.0052 | 0.0142 | 0.0167 | 1.17 | +0.36 |
| 3 | 0.0 | 10 | antinoophor | -0.0409 | +0.0016 | 0.0193 | 0.0230 | 1.19 | +0.08 | 0.0000 | +0.0053 | 0.0139 | 0.0167 | 1.20 | +0.38 |
| 3 | 0.0 | 16 | null | +0.0000 | -0.0004 | 0.0107 | 0.0134 | 1.25 | -0.03 | 0.0000 | +0.0024 | 0.0084 | 0.0110 | 1.31 | +0.29 |
| 3 | 0.0 | 16 | antinoophor | -0.0407 | +0.0011 | 0.0127 | 0.0158 | 1.24 | +0.08 | 0.0000 | +0.0029 | 0.0088 | 0.0111 | 1.25 | +0.33 |
| 3 | 0.3 | 10 | null | +0.0000 | -0.0031 | 0.0233 | 0.0217 | 0.93 | -0.13 | 0.0000 | +0.0442 | 0.0201 | 0.0177 | 0.88 | +2.20 |
| 3 | 0.3 | 10 | antinoophor | -0.0407 | -0.0040 | 0.0267 | 0.0243 | 0.91 | -0.15 | 0.0000 | +0.0462 | 0.0189 | 0.0178 | 0.94 | +2.45 |
| 3 | 0.3 | 16 | null | +0.0000 | -0.0005 | 0.0147 | 0.0149 | 1.01 | -0.03 | 0.0000 | +0.0295 | 0.0126 | 0.0121 | 0.96 | +2.35 |
| 3 | 0.3 | 16 | antinoophor | -0.0406 | -0.0024 | 0.0195 | 0.0172 | 0.88 | -0.12 | 0.0000 | +0.0303 | 0.0129 | 0.0122 | 0.94 | +2.35 |
| 5 | 0.0 | 10 | null | +0.0000 | +0.0003 | 0.0228 | 0.0266 | 1.17 | +0.02 | 0.0000 | +0.0163 | 0.0200 | 0.0217 | 1.09 | +0.82 |
| 5 | 0.0 | 10 | antinoophor | -0.0477 | +0.0004 | 0.0259 | 0.0295 | 1.14 | +0.02 | 0.0000 | +0.0163 | 0.0199 | 0.0220 | 1.11 | +0.82 |
| 5 | 0.0 | 16 | null | +0.0000 | +0.0001 | 0.0149 | 0.0180 | 1.21 | +0.01 | 0.0000 | +0.0077 | 0.0124 | 0.0148 | 1.19 | +0.62 |
| 5 | 0.0 | 16 | antinoophor | -0.0477 | +0.0004 | 0.0183 | 0.0202 | 1.11 | +0.02 | 0.0000 | +0.0078 | 0.0119 | 0.0148 | 1.25 | +0.66 |
| 5 | 0.3 | 10 | null | +0.0000 | -0.0011 | 0.0308 | 0.0277 | 0.90 | -0.03 | 0.0000 | +0.0867 | 0.0262 | 0.0226 | 0.86 | +3.32 |
| 5 | 0.3 | 10 | antinoophor | -0.0473 | -0.0078 | 0.0355 | 0.0300 | 0.85 | -0.22 | 0.0000 | +0.0884 | 0.0254 | 0.0226 | 0.89 | +3.48 |
| 5 | 0.3 | 16 | null | +0.0000 | -0.0002 | 0.0196 | 0.0195 | 0.99 | -0.01 | 0.0000 | +0.0574 | 0.0155 | 0.0159 | 1.03 | +3.70 |
| 5 | 0.3 | 16 | antinoophor | -0.0479 | -0.0034 | 0.0234 | 0.0215 | 0.92 | -0.14 | 0.0000 | +0.0571 | 0.0166 | 0.0158 | 0.95 | +3.44 |

**Table 6 — the gap's Wald coverage against a normal model built from Table 5 †, every grid cell.** *model*: an error normal with the measured mean and standard deviation, against an interval of half-width `z` × the mean bootstrap standard deviation; *centre only*: the same error against `z` × its own standard deviation; *spread only*: a centred error against `z` × the mean bootstrap standard deviation. Over all 64 cells, observed minus model lies between -0.0280 and +0.0333 for the gap and between -0.0206 and +0.0176 for the movement; the largest difference is 1.77 Monte Carlo standard errors of the model's coverage, over 128 cell–quantity pairs. The model was chosen after the failures were seen.

| `K` | `ρ` | `n` | `g` | `λ` | observed | model | centre only | spread only |
|---|---|---|---|---|---|---|---|---|
| 3 | 0.0 | 10 | 0.0 | 0.25 | 0.9200 | 0.9149 | 0.9469 | 0.9190 |
| 3 | 0.0 | 10 | 0.0 | 0.75 | 0.9250 | 0.9351 | 0.9452 | 0.9405 |
| 3 | 0.0 | 10 | 0.8 | 0.25 | 0.9650 | 0.9622 | 0.9445 | 0.9665 |
| 3 | 0.0 | 10 | 0.8 | 0.75 | 0.9650 | 0.9662 | 0.9419 | 0.9718 |
| 3 | 0.0 | 10 | 0.95 | 0.25 | 0.9775 | 0.9732 | 0.9383 | 0.9797 |
| 3 | 0.0 | 10 | 0.95 | 0.75 | 0.9575 | 0.9615 | 0.9216 | 0.9782 |
| 3 | 0.0 | 16 | 0.0 | 0.25 | 0.9425 | 0.9421 | 0.9481 | 0.9441 |
| 3 | 0.0 | 16 | 0.0 | 0.75 | 0.9450 | 0.9373 | 0.9494 | 0.9380 |
| 3 | 0.0 | 16 | 0.8 | 0.25 | 0.9900 | 0.9827 | 0.9464 | 0.9844 |
| 3 | 0.0 | 16 | 0.8 | 0.75 | 0.9700 | 0.9738 | 0.9488 | 0.9746 |
| 3 | 0.0 | 16 | 0.95 | 0.25 | 0.9700 | 0.9740 | 0.9389 | 0.9801 |
| 3 | 0.0 | 16 | 0.95 | 0.75 | 0.9800 | 0.9809 | 0.9366 | 0.9865 |
| 3 | 0.3 | 10 | 0.0 | 0.25 | 0.4400 | 0.4271 | 0.6760 | 0.8148 |
| 3 | 0.3 | 10 | 0.0 | 0.75 | 0.3950 | 0.3898 | 0.6268 | 0.8262 |
| 3 | 0.3 | 10 | 0.8 | 0.25 | 0.3325 | 0.3143 | 0.3927 | 0.9196 |
| 3 | 0.3 | 10 | 0.8 | 0.75 | 0.3175 | 0.3268 | 0.3987 | 0.9229 |
| 3 | 0.3 | 10 | 0.95 | 0.25 | 0.2450 | 0.2500 | 0.2703 | 0.9422 |
| 3 | 0.3 | 10 | 0.95 | 0.75 | 0.2925 | 0.2888 | 0.3969 | 0.9040 |
| 3 | 0.3 | 16 | 0.0 | 0.25 | 0.5750 | 0.5669 | 0.7822 | 0.8262 |
| 3 | 0.3 | 16 | 0.0 | 0.75 | 0.5175 | 0.5010 | 0.7025 | 0.8487 |
| 3 | 0.3 | 16 | 0.8 | 0.25 | 0.3850 | 0.3652 | 0.3824 | 0.9444 |
| 3 | 0.3 | 16 | 0.8 | 0.75 | 0.3650 | 0.3568 | 0.4707 | 0.9044 |
| 3 | 0.3 | 16 | 0.95 | 0.25 | 0.2725 | 0.2743 | 0.2600 | 0.9549 |
| 3 | 0.3 | 16 | 0.95 | 0.75 | 0.2825 | 0.2922 | 0.2809 | 0.9538 |
| 5 | 0.0 | 10 | 0.0 | 0.25 | 0.8275 | 0.8413 | 0.9030 | 0.9065 |
| 5 | 0.0 | 10 | 0.0 | 0.75 | 0.8625 | 0.8292 | 0.9071 | 0.8927 |
| 5 | 0.0 | 10 | 0.8 | 0.25 | 0.8975 | 0.8936 | 0.8720 | 0.9613 |
| 5 | 0.0 | 10 | 0.8 | 0.75 | 0.8900 | 0.9071 | 0.8836 | 0.9630 |
| 5 | 0.0 | 10 | 0.95 | 0.25 | 0.9350 | 0.9270 | 0.8566 | 0.9809 |
| 5 | 0.0 | 10 | 0.95 | 0.75 | 0.8850 | 0.8862 | 0.8569 | 0.9640 |
| 5 | 0.0 | 16 | 0.0 | 0.25 | 0.8825 | 0.8927 | 0.9417 | 0.9046 |
| 5 | 0.0 | 16 | 0.0 | 0.75 | 0.8900 | 0.8990 | 0.9387 | 0.9143 |
| 5 | 0.0 | 16 | 0.8 | 0.25 | 0.9325 | 0.9370 | 0.9229 | 0.9605 |
| 5 | 0.0 | 16 | 0.8 | 0.75 | 0.9400 | 0.9442 | 0.9231 | 0.9656 |
| 5 | 0.0 | 16 | 0.95 | 0.25 | 0.9675 | 0.9571 | 0.8905 | 0.9852 |
| 5 | 0.0 | 16 | 0.95 | 0.75 | 0.9425 | 0.9583 | 0.9041 | 0.9823 |
| 5 | 0.3 | 10 | 0.0 | 0.25 | 0.1075 | 0.1015 | 0.2914 | 0.7837 |
| 5 | 0.3 | 10 | 0.0 | 0.75 | 0.1025 | 0.1040 | 0.2694 | 0.8118 |
| 5 | 0.3 | 10 | 0.8 | 0.25 | 0.0300 | 0.0460 | 0.0846 | 0.9010 |
| 5 | 0.3 | 10 | 0.8 | 0.75 | 0.0300 | 0.0343 | 0.0568 | 0.9148 |
| 5 | 0.3 | 10 | 0.95 | 0.25 | 0.0500 | 0.0456 | 0.0749 | 0.9131 |
| 5 | 0.3 | 10 | 0.95 | 0.75 | 0.0575 | 0.0512 | 0.0918 | 0.9024 |
| 5 | 0.3 | 16 | 0.0 | 0.25 | 0.1850 | 0.1827 | 0.3690 | 0.8354 |
| 5 | 0.3 | 16 | 0.0 | 0.75 | 0.1975 | 0.1922 | 0.3723 | 0.8433 |
| 5 | 0.3 | 16 | 0.8 | 0.25 | 0.0675 | 0.0691 | 0.1010 | 0.9205 |
| 5 | 0.3 | 16 | 0.8 | 0.75 | 0.0550 | 0.0641 | 0.1043 | 0.9102 |
| 5 | 0.3 | 16 | 0.95 | 0.25 | 0.0350 | 0.0496 | 0.0690 | 0.9272 |
| 5 | 0.3 | 16 | 0.95 | 0.75 | 0.0450 | 0.0545 | 0.0751 | 0.9275 |
<!-- tables:end -->

## Reproduce

```bash
python3 metrics/validation/test_confirm_candidate.py
python3 metrics/validation/confirm_candidate.py --out research/candidate-confirmation.json
python3 metrics/validation/confirm_candidate_report.py --check
```

The second command takes about eighteen minutes on sixteen processes and
rewrites the record. The third checks these tables against the record.

**Exposure.** `claude-opus-5-5` wrote the plan, its predictions, the code and
this report, and scored its own predictions. The scoring is `score()` in the
code, committed before the run. A same-model review checked the draft before it
was committed. It reran the code as registered at `461f21f` on the five cells
that hold the deciding numbers, and every registered field came out identical.
It reimplemented the estimator and the generator from their definitions and
found they agreed. It also rescored the record independently. See
[EXPOSURE.md](../EXPOSURE.md).

---

*Prose: CC BY 4.0. Code: Apache-2.0.*
