# Bias-corrected divergences: the follow-up's results

**2026-10-22 · results of the offline simulation registered in
[the plan](2026-10-22-bias-corrected-plan.md)**, committed before the
[code](../metrics/validation/bias_corrected.py), itself committed before its
registered run. No model was called. Every number is in the
[saved record](bias-corrected.json); the tables below are generated from it and
checked against it. **The prediction that mattered held; of the other three, one
failed narrowly and one badly, and by the plan's rule that means no proposal.**
Problem 12 stays as open as it was.

## The built-in check passed

The run spends randomness in the order the previous simulation did, so its
plug-in V0 and V2 reports had to equal
[`vanishing-gap.json`](vanishing-gap.json) field for field. They did, with no
mismatching field (Table 1). The comparison below is the one the plan describes.

## The predictions

| prediction | result |
|---|---|
| **B1** jackknife gap estimate closer than V2's in ≥ 40 of 48 cells | **failed**: 37 of 48 |
| **B2** jackknife Fieller set covers ≥ 0.93 in every cell | **held**: 0.9525–0.995, no cell below |
| **B3** jackknife gap percentile interval covers ≥ 0.90 everywhere, and lies above zero in ≤ 0.10 of null trials | **failed**: covers 0.015–0.565, below 0.90 in all 48 cells; above zero in 0.9575–0.9775 of null trials |
| **B4** jackknife bounded share below one half at `g = 0.98` | **held**: 0.0325–0.06 |

**B2** is the claim the previous run failed. At the widest gap with `λ` of 0.5
or 0.75, the plug-in V0 set covered 0.7125–0.8975 and V2's 0.735–0.8875; the
jackknife set covers 0.9575–0.9775 there (Table 2). The plan committed to report
any coverage gained with the width it cost. At `g = 0` the jackknife set's median
bounded width is 0.93–1.03 times V2's, and at `g = 0.6` it is 0.64–0.82 times
V2's, so the coverage was not bought with width. Over the same cells the
uncapped ratio's bias moves from +0.0242 to +0.0660 for V2 (`λ < 1`) to
−0.0004 to −0.0097 for the jackknife. **B4** says the jackknife set still widens
without bound where the gap closes.

**B1** failed by three cells. The jackknife's gap estimate errs by +0.0012 to
+0.0070 across the grid and V2's by −0.0300 to −0.0019; V2's was the closer in
eleven cells, all at `g ≥ 0.95`, where the true gap is 0.0025–0.0075: all eight
at `g = 0.98` and three of the eight at `g = 0.95`. Everywhere the gap is larger
than that, the jackknife's error is the smaller. At a true gap of zero the
jackknife still estimates a gap of about 0.003–0.005, so it does not estimate a
small gap accurately either (Table 3).

**B3** failed in every cell, and by a wide margin. The plan registered two gap
intervals, and **both fail** for the jackknife: the percentile interval covers
0.015–0.565 and the basic interval 0.365–0.67 (Table 3).

Miller–Madow, for which nothing was predicted, is reported in full in Tables 2–5.
Its Fieller set falls below 0.93 in 22 cells, as low as 0.7925 — all twelve at
`λ = 1` and ten at `λ = 0.75`. Its gap intervals cover 0.0–0.2525 (percentile)
and 0.7575–0.92 (basic), and its movement interval 0.755–1.00. See Limits for why
its failure is not evidence against Miller–Madow correction in general.

## Why the gap intervals failed, tested after the run

*This section rests on fields added to the record after the registered run (the
† columns and Table 6; see Limits).*

A percentile interval takes its location from the bootstrap, and a basic
interval reflects that location about the point. In the bootstrap, the empirical
frequencies play the part of the truth, so the divergence the bootstrap treats as
true is the plug-in one — which is biased upward. Measured: across all 52 cells
the mean of the bootstrap jackknife gap sits **0.0009–0.0027 below the plug-in
estimate** from the same answers, and **0.0214–0.0500 above the jackknife point**
(Table 6). The percentile interval is centred near the plug-in value, and the
basic interval, reflected about the point, misses by about as much the other way.

Fieller's set takes only the covariance from the bootstrap, never its location.
That is consistent with B2 holding while both gap intervals failed; it is not by
itself a test of it. To test the location explanation, a Wald interval — centre
from the point, spread from the bootstrap — was added to the record. For the
jackknife it covers the true gap in 0.8875–0.9925 of trials, below 0.93 in seven
cells, all at `g ≤ 0.6`, and below B3's 0.90 bar in one (Table 3); in the null
cells it lies above zero in 0.0175–0.05 of trials (Table 5). For the movement the
jackknife's Wald interval covers 0.935–0.9975 in every cell, where its registered
percentile interval covers 0.88–1.00 (Table 4). These are post-registration
numbers, chosen after seeing B3 fail, and are reported as that.

## The zero-gap cells

With a receiver that moved away from the sender on a measure with no gap, the
jackknife's percentile movement interval excluded zero on the side of moving away
in 0.9425 (`n = 10`) and 0.995 (`n = 16`) of trials, and its post-registration
Wald interval † in 0.8775 and 0.9925. With nothing moved, either did so in at
most 0.0125 of trials (Table 5).

Compared cell for cell: with a receiver that moved, the jackknife's Fieller set is
bounded in 0.03–0.0475 of trials, against V0's 0.695–0.74 and V2's 0.0025–0.01;
with nothing moved, in 0.0175–0.0525, against V0's 0.0025–0.015 and V2's 0–0.0075.
At a true gap of zero a bounded set is a gap reported where there is none, so the
jackknife does this less often than V0 when a receiver moved, and more often than
V2 in every zero-gap cell.

## What this does and does not change

**Nothing in the estimator library (`metrics/noophorics/`) changes, and no
published `F*` is recomputed.** The plan said a proposal would follow if B2 and
B3 held. B3 did not, and Problem 12 stays as open as it was.

On this generator, a Fieller set for `F*` built from jackknife-corrected
divergences held its coverage across the grid at no cost in width, and still
widened without bound as the gap closed. The plug-in sets did not hold it.
Neither registered interval for the gap worked, and the jackknife's gap estimate
still sits above a gap of zero. A Wald construction, chosen after seeing that,
covered the movement everywhere and the gap in all but seven cells.

A jackknife-Fieller report with Wald intervals for the movement and the gap is
therefore an **untested candidate**. It would take a new registration, on a
different generator of distributions, to test it — not this one, where the Wald
construction was chosen after its results were seen. Whether to run that is the
owner's decision.

## Choices fixed in the code before the registered run

The docstring records two: the ratio's bias is the uncapped `M/G` over trials
with `G > 0.02`, as for the plug-in variants; and the jackknife leaves one answer
out using the library's definition of the divergence for unequal sample sizes. A
smoke run of four cells at 20 trials each was executed for timing before the
code was committed.

## Limits

The plan's limits, all of which stand: the previous plan's — synthetic agents,
three options, independent draws, one generator, a fixed frame; corrections
derived for entropy are applied to a difference of entropies, and their errors
need not cancel; and coverage bought with width is reported with the width, which
Table 2 does.

- **The registered Miller–Madow form is not first-order bias-corrected for this
  divergence.** It applies `N = 2n` to the pooled answers, but those are `n`
  answers from each party, not `2n` draws from their mixture. A same-model review
  found by exact enumeration that this leaves a first-order bias of about
  `Σ(p − q)²/(16 n m ln 2)` bits whenever the parties differ. Its results are
  reported as registered; they are not evidence against Miller–Madow correction
  done for a stratified sample.
- 400 trials per cell; a coverage of 0.95 has a Monte Carlo standard error of
  about 0.011.
- **Fields added after the registered run:** the Wald intervals and the
  bootstrap's location (the † columns and Table 6), and a total of mismatching
  fields beside the reproduction check. The full run was repeated after each
  addition, and every registered field came out byte-for-byte identical.

## Reproduce

```bash
python3 metrics/validation/test_bias_corrected.py
python3 metrics/validation/bias_corrected.py --out research/bias-corrected.json
python3 metrics/validation/bias_corrected_report.py --check
```

The second command takes about three and a half minutes on sixteen processes,
rewrites the record and checks the V0/V2 reproduction; the third checks these
tables against the record.

**Exposure.** `claude-opus-5-5` wrote the plan, its predictions, the code and
this report, and scored its own predictions; the scoring is `score()` in the
code, committed before the run. A same-model review checked the draft before it
was committed and reimplemented both estimators independently. See
[EXPOSURE.md](../EXPOSURE.md).

<!-- tables:start -->
**Table 1 — the predictions, scored as registered, and the built-in check.**

| item | held? | the numbers it turned on |
|---|---|---|
| check: V0 and V2 reproduce `vanishing-gap.json` exactly | **yes** | 0 mismatching fields |
| B1: jackknife `Ĝ` closer to the true gap than V2's in ≥ 40 of 48 cells | **no** | 37 of 48 |
| B2: jackknife Fieller set covers ≥ 0.93 in every grid cell | **yes** | 0.9525–0.9950 across the grid; below 0.93 in 0 cells |
| B3: jackknife gap percentile interval covers ≥ 0.90 everywhere, and lies above zero in ≤ 0.10 of null trials | **no** | covers 0.0150–0.5650; below 0.90 in 48 of 48 cells; above zero in 0.9575–0.9775 of null trials |
| B4: jackknife bounded share below one half at `g = 0.98` | **yes** | 0.0325–0.0600 |

**Table 2 — the Fieller set for `F*`, every grid cell.** Coverage of the true `F*`; the median width of the bounded sets, which the plan committed to report beside any coverage gained; and the bias of the uncapped ratio over trials with `Ĝ > 0.02`.

| `n` | `g` | `λ` | true gap | cover V0 | cover V2 | cover MM | cover JK | bounded JK | width V2 | width JK | ratio bias V2 | ratio bias MM | ratio bias JK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 0.0 | 0.25 | 0.3384 | 0.9125 | 0.9175 | 0.9475 | 0.9600 | 1.0000 | 0.3245 | 0.3008 | +0.0344 | -0.0214 | -0.0055 |
| 10 | 0.0 | 0.5 | 0.3387 | 0.8450 | 0.8525 | 0.9600 | 0.9700 | 1.0000 | 0.2596 | 0.2459 | +0.0653 | -0.0340 | -0.0085 |
| 10 | 0.0 | 0.75 | 0.3390 | 0.7125 | 0.7500 | 0.8850 | 0.9575 | 1.0000 | 0.1920 | 0.1911 | +0.0660 | -0.0443 | -0.0097 |
| 10 | 0.0 | 1.0 | 0.3391 | 0.9950 | 0.9950 | 0.8225 | 0.9800 | 1.0000 | 0.1523 | 0.1543 | +0.0011 | -0.0497 | -0.0126 |
| 10 | 0.6 | 0.25 | 0.0906 | 0.9500 | 0.9725 | 0.9625 | 0.9675 | 0.9975 | 1.3747 | 0.9017 | +0.0726 | -0.0630 | -0.0310 |
| 10 | 0.6 | 0.5 | 0.0894 | 0.9050 | 0.9575 | 0.9600 | 0.9800 | 0.9975 | 1.1583 | 0.7729 | +0.1417 | -0.1071 | -0.0338 |
| 10 | 0.6 | 0.75 | 0.0909 | 0.9200 | 0.9675 | 0.8550 | 0.9700 | 0.9975 | 1.0202 | 0.6720 | +0.1027 | -0.1545 | -0.0521 |
| 10 | 0.6 | 1.0 | 0.0904 | 1.0000 | 1.0000 | 0.8025 | 0.9675 | 1.0000 | 0.9834 | 0.6299 | +0.0141 | -0.1701 | -0.0476 |
| 10 | 0.8 | 0.25 | 0.0384 | 0.9950 | 1.0000 | 0.9900 | 0.9950 | 0.7550 | 4.3465 | 2.0309 | +0.1959 | -0.1400 | -0.0741 |
| 10 | 0.8 | 0.5 | 0.0385 | 0.9675 | 0.9950 | 0.9300 | 0.9675 | 0.8100 | 3.0004 | 1.7982 | +0.1681 | -0.2276 | -0.1097 |
| 10 | 0.8 | 0.75 | 0.0387 | 0.9900 | 0.9975 | 0.8575 | 0.9550 | 0.8000 | 2.9339 | 1.5502 | +0.0678 | -0.3029 | -0.1221 |
| 10 | 0.8 | 1.0 | 0.0382 | 1.0000 | 1.0000 | 0.8000 | 0.9600 | 0.8050 | 2.9866 | 1.4073 | -0.0620 | -0.3291 | -0.1285 |
| 10 | 0.9 | 0.25 | 0.0167 | 0.9825 | 0.9975 | 0.9800 | 0.9775 | 0.3050 | 2.0293 | 4.1600 | +0.3699 | -0.1791 | +0.0103 |
| 10 | 0.9 | 0.5 | 0.0169 | 0.9850 | 1.0000 | 0.9375 | 0.9800 | 0.3025 | 4.1178 | 2.8895 | +0.2048 | -0.3122 | -0.0407 |
| 10 | 0.9 | 0.75 | 0.0166 | 0.9925 | 0.9975 | 0.8825 | 0.9800 | 0.2925 | 3.0775 | 2.6827 | +0.0529 | -0.4328 | -0.1753 |
| 10 | 0.9 | 1.0 | 0.0168 | 0.9900 | 0.9900 | 0.7925 | 0.9600 | 0.3250 | 20.2894 | 2.4019 | -0.2584 | -0.5111 | -0.2481 |
| 10 | 0.95 | 0.25 | 0.0074 | 0.9825 | 0.9925 | 0.9775 | 0.9600 | 0.1400 | 6.5421 | 3.4530 | +0.4009 | -0.1210 | +0.1948 |
| 10 | 0.95 | 0.5 | 0.0074 | 0.9975 | 0.9975 | 0.9650 | 0.9800 | 0.1150 | – | 3.2685 | +0.2332 | -0.3540 | +0.0136 |
| 10 | 0.95 | 0.75 | 0.0074 | 0.9900 | 0.9975 | 0.8700 | 0.9875 | 0.1125 | 2.6116 | 3.5578 | -0.0049 | -0.4933 | -0.1481 |
| 10 | 0.95 | 1.0 | 0.0075 | 0.9975 | 0.9975 | 0.8025 | 0.9600 | 0.1275 | 4.3937 | 3.4733 | -0.1188 | -0.6002 | -0.3234 |
| 10 | 0.98 | 0.25 | 0.0025 | 0.9950 | 0.9950 | 0.9775 | 0.9825 | 0.0600 | 5.0885 | 5.4833 | +0.5371 | -0.1405 | +0.2173 |
| 10 | 0.98 | 0.5 | 0.0025 | 0.9975 | 1.0000 | 0.9350 | 0.9850 | 0.0400 | – | 5.1256 | +0.2001 | -0.3710 | -0.0602 |
| 10 | 0.98 | 0.75 | 0.0025 | 1.0000 | 0.9975 | 0.8625 | 0.9750 | 0.0575 | 32.3538 | 5.4192 | -0.1559 | -0.5800 | -0.2451 |
| 10 | 0.98 | 1.0 | 0.0025 | 1.0000 | 1.0000 | 0.7975 | 0.9600 | 0.0550 | – | 4.3010 | -0.2911 | -0.7397 | -0.3827 |
| 16 | 0.0 | 0.25 | 0.3433 | 0.9250 | 0.9275 | 0.9575 | 0.9525 | 1.0000 | 0.2365 | 0.2249 | +0.0242 | -0.0080 | -0.0004 |
| 16 | 0.0 | 0.5 | 0.3400 | 0.8975 | 0.8875 | 0.9400 | 0.9625 | 1.0000 | 0.1828 | 0.1781 | +0.0392 | -0.0213 | -0.0079 |
| 16 | 0.0 | 0.75 | 0.3405 | 0.7225 | 0.7350 | 0.9350 | 0.9775 | 1.0000 | 0.1359 | 0.1361 | +0.0463 | -0.0260 | -0.0061 |
| 16 | 0.0 | 1.0 | 0.3380 | 0.9875 | 0.9875 | 0.8675 | 0.9675 | 1.0000 | 0.1002 | 0.1033 | -0.0002 | -0.0312 | -0.0099 |
| 16 | 0.6 | 0.25 | 0.0908 | 0.9525 | 0.9675 | 0.9675 | 0.9700 | 1.0000 | 0.8223 | 0.6502 | +0.0608 | -0.0412 | -0.0183 |
| 16 | 0.6 | 0.5 | 0.0904 | 0.9075 | 0.9425 | 0.9500 | 0.9750 | 1.0000 | 0.6499 | 0.5319 | +0.0916 | -0.0764 | -0.0292 |
| 16 | 0.6 | 0.75 | 0.0904 | 0.9150 | 0.9575 | 0.9300 | 0.9900 | 1.0000 | 0.5473 | 0.4505 | +0.0947 | -0.0973 | -0.0317 |
| 16 | 0.6 | 1.0 | 0.0904 | 0.9925 | 0.9925 | 0.8700 | 0.9675 | 1.0000 | 0.4871 | 0.3898 | +0.0043 | -0.1024 | -0.0293 |
| 16 | 0.8 | 0.25 | 0.0388 | 0.9725 | 0.9850 | 0.9800 | 0.9775 | 0.9675 | 2.4742 | 1.3870 | +0.1710 | -0.0698 | -0.0213 |
| 16 | 0.8 | 0.5 | 0.0382 | 0.9525 | 0.9825 | 0.9500 | 0.9850 | 0.9700 | 2.1956 | 1.2575 | +0.1680 | -0.1560 | -0.0701 |
| 16 | 0.8 | 0.75 | 0.0382 | 0.9775 | 0.9925 | 0.9200 | 0.9850 | 0.9525 | 2.1827 | 1.1053 | +0.0851 | -0.2080 | -0.0809 |
| 16 | 0.8 | 1.0 | 0.0386 | 0.9975 | 0.9975 | 0.8900 | 0.9675 | 0.9675 | 2.0457 | 0.9802 | -0.0111 | -0.2049 | -0.0592 |
| 16 | 0.9 | 0.25 | 0.0167 | 0.9900 | 1.0000 | 0.9850 | 0.9875 | 0.4800 | 5.1092 | 3.0402 | +0.2815 | -0.0995 | +0.0458 |
| 16 | 0.9 | 0.5 | 0.0167 | 0.9925 | 1.0000 | 0.9650 | 0.9825 | 0.5125 | 5.1294 | 2.7193 | +0.0838 | -0.2102 | -0.0602 |
| 16 | 0.9 | 0.75 | 0.0165 | 0.9950 | 1.0000 | 0.9200 | 0.9825 | 0.5175 | 4.3315 | 2.2341 | +0.0979 | -0.3114 | -0.0844 |
| 16 | 0.9 | 1.0 | 0.0169 | 0.9950 | 0.9950 | 0.8575 | 0.9625 | 0.4900 | 12.9588 | 2.2035 | -0.1263 | -0.3668 | -0.1950 |
| 16 | 0.95 | 0.25 | 0.0075 | 0.9850 | 0.9975 | 0.9800 | 0.9825 | 0.1825 | 10.2074 | 4.2822 | +0.3463 | -0.0099 | +0.2543 |
| 16 | 0.95 | 0.5 | 0.0074 | 0.9950 | 1.0000 | 0.9650 | 0.9850 | 0.1650 | 6.7750 | 3.1539 | +0.2251 | -0.2136 | +0.0356 |
| 16 | 0.95 | 0.75 | 0.0074 | 1.0000 | 1.0000 | 0.9200 | 0.9850 | 0.1400 | – | 3.8224 | – | -0.3865 | -0.1454 |
| 16 | 0.95 | 1.0 | 0.0075 | 0.9975 | 0.9975 | 0.8550 | 0.9750 | 0.1800 | 5.1571 | 3.3960 | -0.5433 | -0.4565 | -0.2490 |
| 16 | 0.98 | 0.25 | 0.0025 | 0.9975 | 0.9975 | 0.9950 | 0.9925 | 0.0325 | – | 7.0646 | +0.8687 | +0.0204 | +0.2216 |
| 16 | 0.98 | 0.5 | 0.0025 | 0.9925 | 0.9975 | 0.9500 | 0.9850 | 0.0575 | – | 5.3323 | +0.3485 | -0.2161 | +0.0991 |
| 16 | 0.98 | 0.75 | 0.0025 | 1.0000 | 1.0000 | 0.9125 | 0.9750 | 0.0425 | 3.9383 | 2.7436 | – | -0.3767 | -0.0600 |
| 16 | 0.98 | 1.0 | 0.0025 | 0.9975 | 0.9975 | 0.8675 | 0.9925 | 0.0325 | 5.8621 | 6.4016 | – | -0.5468 | -0.0709 |

**Table 3 — the gap, every grid cell.** The mean error of `Ĝ` against the true gap, and coverage of the true gap by the two registered intervals (percentile and basic) and by a Wald interval †, for Miller–Madow and the jackknife.

| `n` | `g` | `λ` | error V2 | error MM | error JK | MM percentile | MM basic | MM Wald † | JK percentile | JK basic | JK Wald † |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 0.0 | 0.25 | -0.0244 | +0.0404 | +0.0055 | 0.0900 | 0.8800 | 0.6750 | 0.4350 | 0.5300 | 0.8875 |
| 10 | 0.0 | 0.5 | -0.0264 | +0.0381 | +0.0034 | 0.0950 | 0.9075 | 0.7000 | 0.4500 | 0.5200 | 0.9250 |
| 10 | 0.0 | 0.75 | -0.0236 | +0.0406 | +0.0054 | 0.0725 | 0.8925 | 0.6525 | 0.4075 | 0.5475 | 0.9225 |
| 10 | 0.0 | 1.0 | -0.0237 | +0.0408 | +0.0054 | 0.0650 | 0.8975 | 0.6725 | 0.4375 | 0.5225 | 0.9075 |
| 10 | 0.6 | 0.25 | -0.0263 | +0.0271 | +0.0068 | 0.0325 | 0.8675 | 0.7525 | 0.2400 | 0.5025 | 0.9225 |
| 10 | 0.6 | 0.5 | -0.0270 | +0.0258 | +0.0049 | 0.0250 | 0.8550 | 0.7700 | 0.2700 | 0.4650 | 0.9575 |
| 10 | 0.6 | 0.75 | -0.0282 | +0.0244 | +0.0036 | 0.0375 | 0.8550 | 0.8025 | 0.2775 | 0.4600 | 0.9700 |
| 10 | 0.6 | 1.0 | -0.0300 | +0.0225 | +0.0020 | 0.0575 | 0.8350 | 0.8025 | 0.3200 | 0.4300 | 0.9675 |
| 10 | 0.8 | 0.25 | -0.0207 | +0.0222 | +0.0046 | 0.0075 | 0.8475 | 0.7925 | 0.1350 | 0.4425 | 0.9725 |
| 10 | 0.8 | 0.5 | -0.0204 | +0.0233 | +0.0058 | 0.0100 | 0.8550 | 0.7425 | 0.1275 | 0.4475 | 0.9500 |
| 10 | 0.8 | 0.75 | -0.0204 | +0.0230 | +0.0056 | 0.0175 | 0.8625 | 0.7600 | 0.1325 | 0.4700 | 0.9575 |
| 10 | 0.8 | 1.0 | -0.0189 | +0.0245 | +0.0068 | 0.0125 | 0.8650 | 0.7275 | 0.1150 | 0.4875 | 0.9575 |
| 10 | 0.9 | 0.25 | -0.0120 | +0.0212 | +0.0051 | 0.0075 | 0.8375 | 0.7900 | 0.0975 | 0.4525 | 0.9575 |
| 10 | 0.9 | 0.5 | -0.0117 | +0.0220 | +0.0063 | 0.0025 | 0.8700 | 0.7375 | 0.0725 | 0.4575 | 0.9650 |
| 10 | 0.9 | 0.75 | -0.0119 | +0.0219 | +0.0057 | 0.0000 | 0.8525 | 0.7375 | 0.0650 | 0.4150 | 0.9575 |
| 10 | 0.9 | 1.0 | -0.0116 | +0.0218 | +0.0060 | 0.0025 | 0.8550 | 0.7450 | 0.0900 | 0.4450 | 0.9500 |
| 10 | 0.95 | 0.25 | -0.0055 | +0.0220 | +0.0070 | 0.0000 | 0.8450 | 0.7250 | 0.0475 | 0.4625 | 0.9475 |
| 10 | 0.95 | 0.5 | -0.0062 | +0.0209 | +0.0056 | 0.0000 | 0.8350 | 0.7550 | 0.0400 | 0.4150 | 0.9525 |
| 10 | 0.95 | 0.75 | -0.0055 | +0.0218 | +0.0066 | 0.0000 | 0.8525 | 0.7175 | 0.0350 | 0.4750 | 0.9675 |
| 10 | 0.95 | 1.0 | -0.0059 | +0.0211 | +0.0061 | 0.0000 | 0.8575 | 0.7375 | 0.0450 | 0.4450 | 0.9700 |
| 10 | 0.98 | 0.25 | -0.0023 | +0.0203 | +0.0060 | 0.0000 | 0.8600 | 0.7700 | 0.0300 | 0.4500 | 0.9675 |
| 10 | 0.98 | 0.5 | -0.0030 | +0.0192 | +0.0048 | 0.0000 | 0.8425 | 0.7825 | 0.0450 | 0.4175 | 0.9750 |
| 10 | 0.98 | 0.75 | -0.0026 | +0.0197 | +0.0053 | 0.0000 | 0.8175 | 0.7475 | 0.0550 | 0.4000 | 0.9725 |
| 10 | 0.98 | 1.0 | -0.0026 | +0.0198 | +0.0057 | 0.0000 | 0.8550 | 0.7600 | 0.0450 | 0.4475 | 0.9575 |
| 16 | 0.0 | 0.25 | -0.0119 | +0.0234 | +0.0035 | 0.2225 | 0.9200 | 0.7825 | 0.5375 | 0.6700 | 0.9400 |
| 16 | 0.0 | 0.5 | -0.0128 | +0.0224 | +0.0028 | 0.2425 | 0.8725 | 0.7975 | 0.5375 | 0.6500 | 0.9050 |
| 16 | 0.0 | 0.75 | -0.0127 | +0.0224 | +0.0026 | 0.2525 | 0.9100 | 0.7650 | 0.5650 | 0.6025 | 0.9100 |
| 16 | 0.0 | 1.0 | -0.0104 | +0.0245 | +0.0047 | 0.2100 | 0.9175 | 0.7625 | 0.5100 | 0.6300 | 0.9375 |
| 16 | 0.6 | 0.25 | -0.0188 | +0.0131 | +0.0021 | 0.1375 | 0.8150 | 0.9000 | 0.3875 | 0.5475 | 0.9650 |
| 16 | 0.6 | 0.5 | -0.0181 | +0.0139 | +0.0026 | 0.1550 | 0.7900 | 0.8625 | 0.3825 | 0.5200 | 0.9475 |
| 16 | 0.6 | 0.75 | -0.0194 | +0.0123 | +0.0012 | 0.1575 | 0.8075 | 0.8750 | 0.4275 | 0.4850 | 0.9725 |
| 16 | 0.6 | 1.0 | -0.0181 | +0.0139 | +0.0028 | 0.1200 | 0.8275 | 0.8850 | 0.3750 | 0.5300 | 0.9600 |
| 16 | 0.8 | 0.25 | -0.0151 | +0.0130 | +0.0033 | 0.0300 | 0.8050 | 0.8300 | 0.1775 | 0.4550 | 0.9675 |
| 16 | 0.8 | 0.5 | -0.0153 | +0.0125 | +0.0028 | 0.0300 | 0.7575 | 0.8475 | 0.1775 | 0.4375 | 0.9625 |
| 16 | 0.8 | 0.75 | -0.0157 | +0.0121 | +0.0023 | 0.0275 | 0.7775 | 0.8800 | 0.2050 | 0.4350 | 0.9700 |
| 16 | 0.8 | 1.0 | -0.0155 | +0.0123 | +0.0027 | 0.0250 | 0.8025 | 0.8650 | 0.1975 | 0.4525 | 0.9725 |
| 16 | 0.9 | 0.25 | -0.0102 | +0.0120 | +0.0030 | 0.0100 | 0.7700 | 0.8350 | 0.0900 | 0.3975 | 0.9750 |
| 16 | 0.9 | 0.5 | -0.0098 | +0.0124 | +0.0034 | 0.0025 | 0.8075 | 0.8350 | 0.0725 | 0.4000 | 0.9800 |
| 16 | 0.9 | 0.75 | -0.0094 | +0.0132 | +0.0041 | 0.0025 | 0.8150 | 0.8225 | 0.0600 | 0.4050 | 0.9625 |
| 16 | 0.9 | 1.0 | -0.0107 | +0.0116 | +0.0028 | 0.0050 | 0.7725 | 0.8475 | 0.1125 | 0.3650 | 0.9675 |
| 16 | 0.95 | 0.25 | -0.0054 | +0.0125 | +0.0042 | 0.0000 | 0.8175 | 0.8275 | 0.0400 | 0.4375 | 0.9675 |
| 16 | 0.95 | 0.5 | -0.0054 | +0.0123 | +0.0038 | 0.0025 | 0.7825 | 0.8100 | 0.0475 | 0.3925 | 0.9725 |
| 16 | 0.95 | 0.75 | -0.0060 | +0.0116 | +0.0031 | 0.0050 | 0.8050 | 0.8625 | 0.0525 | 0.3850 | 0.9850 |
| 16 | 0.95 | 1.0 | -0.0054 | +0.0125 | +0.0038 | 0.0000 | 0.7900 | 0.8250 | 0.0425 | 0.4125 | 0.9600 |
| 16 | 0.98 | 0.25 | -0.0023 | +0.0112 | +0.0030 | 0.0000 | 0.7650 | 0.8750 | 0.0300 | 0.3800 | 0.9875 |
| 16 | 0.98 | 0.5 | -0.0023 | +0.0118 | +0.0037 | 0.0000 | 0.8050 | 0.8300 | 0.0275 | 0.4050 | 0.9800 |
| 16 | 0.98 | 0.75 | -0.0024 | +0.0113 | +0.0032 | 0.0000 | 0.8050 | 0.8800 | 0.0150 | 0.3825 | 0.9700 |
| 16 | 0.98 | 1.0 | -0.0019 | +0.0119 | +0.0038 | 0.0000 | 0.7875 | 0.8225 | 0.0200 | 0.4175 | 0.9925 |

**Table 4 — the movement, every grid cell.** Coverage of the true movement by the registered percentile interval and by a Wald interval †. V0's movement is the plug-in `D̂_prior − D̂_post`.

| `n` | `g` | `λ` | V0 percentile | MM percentile | JK percentile | V0 Wald † | MM Wald † | JK Wald † |
|---|---|---|---|---|---|---|---|---|
| 10 | 0.0 | 0.25 | 0.9275 | 0.9150 | 0.9350 | 0.9375 | 0.9350 | 0.9350 |
| 10 | 0.0 | 0.5 | 0.9325 | 0.9050 | 0.9375 | 0.9425 | 0.9325 | 0.9450 |
| 10 | 0.0 | 0.75 | 0.8750 | 0.8225 | 0.9250 | 0.9250 | 0.9025 | 0.9475 |
| 10 | 0.0 | 1.0 | 0.7800 | 0.7550 | 0.8800 | 0.8800 | 0.8700 | 0.9350 |
| 10 | 0.6 | 0.25 | 0.9500 | 0.9525 | 0.9525 | 0.9575 | 0.9575 | 0.9650 |
| 10 | 0.6 | 0.5 | 0.9625 | 0.9625 | 0.9725 | 0.9725 | 0.9725 | 0.9725 |
| 10 | 0.6 | 0.75 | 0.9500 | 0.9650 | 0.9775 | 0.9775 | 0.9775 | 0.9675 |
| 10 | 0.6 | 1.0 | 0.9300 | 0.9550 | 0.9825 | 0.9825 | 0.9825 | 0.9725 |
| 10 | 0.8 | 0.25 | 1.0000 | 1.0000 | 0.9975 | 0.9975 | 0.9975 | 0.9950 |
| 10 | 0.8 | 0.5 | 0.9750 | 0.9825 | 0.9825 | 0.9825 | 0.9800 | 0.9725 |
| 10 | 0.8 | 0.75 | 0.9850 | 0.9800 | 0.9800 | 0.9825 | 0.9825 | 0.9775 |
| 10 | 0.8 | 1.0 | 0.9525 | 0.9575 | 0.9825 | 0.9725 | 0.9800 | 0.9725 |
| 10 | 0.9 | 0.25 | 0.9875 | 0.9875 | 0.9850 | 0.9850 | 0.9850 | 0.9875 |
| 10 | 0.9 | 0.5 | 0.9875 | 0.9900 | 0.9875 | 0.9875 | 0.9900 | 0.9850 |
| 10 | 0.9 | 0.75 | 0.9900 | 0.9900 | 0.9950 | 0.9925 | 0.9925 | 0.9875 |
| 10 | 0.9 | 1.0 | 0.9825 | 0.9900 | 0.9925 | 0.9925 | 0.9875 | 0.9750 |
| 10 | 0.95 | 0.25 | 0.9850 | 0.9825 | 0.9850 | 0.9825 | 0.9775 | 0.9675 |
| 10 | 0.95 | 0.5 | 1.0000 | 1.0000 | 0.9975 | 0.9975 | 0.9950 | 0.9900 |
| 10 | 0.95 | 0.75 | 0.9900 | 0.9900 | 0.9925 | 0.9925 | 0.9900 | 0.9825 |
| 10 | 0.95 | 1.0 | 0.9875 | 0.9875 | 0.9900 | 0.9900 | 0.9875 | 0.9775 |
| 10 | 0.98 | 0.25 | 0.9850 | 0.9875 | 0.9900 | 0.9875 | 0.9900 | 0.9875 |
| 10 | 0.98 | 0.5 | 0.9950 | 0.9950 | 0.9975 | 0.9975 | 0.9975 | 0.9975 |
| 10 | 0.98 | 0.75 | 0.9975 | 0.9975 | 0.9950 | 0.9950 | 0.9900 | 0.9850 |
| 10 | 0.98 | 1.0 | 0.9975 | 0.9975 | 0.9975 | 0.9950 | 0.9850 | 0.9725 |
| 16 | 0.0 | 0.25 | 0.9325 | 0.9250 | 0.9325 | 0.9375 | 0.9275 | 0.9425 |
| 16 | 0.0 | 0.5 | 0.9350 | 0.9250 | 0.9475 | 0.9475 | 0.9425 | 0.9525 |
| 16 | 0.0 | 0.75 | 0.8925 | 0.8700 | 0.9200 | 0.9225 | 0.9150 | 0.9425 |
| 16 | 0.0 | 1.0 | 0.7900 | 0.7750 | 0.8975 | 0.8950 | 0.8900 | 0.9450 |
| 16 | 0.6 | 0.25 | 0.9725 | 0.9775 | 0.9775 | 0.9725 | 0.9750 | 0.9725 |
| 16 | 0.6 | 0.5 | 0.9575 | 0.9625 | 0.9650 | 0.9700 | 0.9650 | 0.9625 |
| 16 | 0.6 | 0.75 | 0.9800 | 0.9850 | 0.9850 | 0.9850 | 0.9900 | 0.9925 |
| 16 | 0.6 | 1.0 | 0.9250 | 0.9400 | 0.9600 | 0.9550 | 0.9600 | 0.9500 |
| 16 | 0.8 | 0.25 | 0.9750 | 0.9800 | 0.9825 | 0.9825 | 0.9800 | 0.9775 |
| 16 | 0.8 | 0.5 | 0.9850 | 0.9950 | 0.9975 | 0.9950 | 0.9975 | 0.9925 |
| 16 | 0.8 | 0.75 | 0.9800 | 0.9850 | 0.9900 | 0.9875 | 0.9900 | 0.9875 |
| 16 | 0.8 | 1.0 | 0.9700 | 0.9800 | 0.9850 | 0.9825 | 0.9850 | 0.9800 |
| 16 | 0.9 | 0.25 | 0.9875 | 0.9875 | 0.9875 | 0.9925 | 0.9925 | 0.9850 |
| 16 | 0.9 | 0.5 | 0.9925 | 0.9950 | 0.9950 | 0.9950 | 0.9925 | 0.9900 |
| 16 | 0.9 | 0.75 | 0.9850 | 0.9875 | 0.9875 | 0.9875 | 0.9850 | 0.9850 |
| 16 | 0.9 | 1.0 | 0.9875 | 0.9925 | 0.9975 | 0.9950 | 0.9950 | 0.9875 |
| 16 | 0.95 | 0.25 | 0.9850 | 0.9825 | 0.9825 | 0.9875 | 0.9850 | 0.9825 |
| 16 | 0.95 | 0.5 | 1.0000 | 0.9975 | 1.0000 | 1.0000 | 0.9975 | 0.9900 |
| 16 | 0.95 | 0.75 | 0.9875 | 0.9925 | 0.9925 | 0.9950 | 0.9950 | 0.9900 |
| 16 | 0.95 | 1.0 | 0.9925 | 0.9900 | 0.9900 | 0.9900 | 0.9875 | 0.9825 |
| 16 | 0.98 | 0.25 | 0.9975 | 0.9975 | 1.0000 | 0.9975 | 0.9975 | 0.9975 |
| 16 | 0.98 | 0.5 | 0.9950 | 0.9975 | 0.9950 | 0.9900 | 0.9925 | 0.9850 |
| 16 | 0.98 | 0.75 | 0.9975 | 0.9975 | 0.9975 | 0.9975 | 0.9975 | 0.9900 |
| 16 | 0.98 | 1.0 | 0.9925 | 0.9950 | 0.9975 | 0.9950 | 0.9950 | 0.9950 |

**Table 5 — the zero-gap cells, every estimator.** The share of trials whose gap interval lies wholly above zero (a gap reported where there is none), and whose movement interval excludes zero on the side of moving away. † added after the registered run.

| `n` | cell | estimator | gap above 0, percentile | gap above 0, Wald † | movement away, percentile | movement away, Wald † | Fieller bounded |
|---|---|---|---|---|---|---|---|
| 10 | null | V0 | 0.8350 | 0.0100 | 0.0000 | 0.0025 | 0.0150 |
| 10 | null | V2 | 0.9375 | 0.0050 | 0.0000 | 0.0025 | 0.0075 |
| 10 | null | MM | 1.0000 | 0.2250 | 0.0000 | 0.0075 | 0.2250 |
| 10 | null | JK | 0.9575 | 0.0500 | 0.0000 | 0.0125 | 0.0525 |
| 10 | antinoophor | V0 | 0.0275 | 0.0000 | 0.9900 | 0.9525 | 0.7400 |
| 10 | antinoophor | V2 | 0.9225 | 0.0000 | 0.7900 | 0.4850 | 0.0025 |
| 10 | antinoophor | MM | 1.0000 | 0.2250 | 0.9625 | 0.9125 | 0.2250 |
| 10 | antinoophor | JK | 0.9675 | 0.0250 | 0.9425 | 0.8775 | 0.0300 |
| 16 | null | V0 | 0.8825 | 0.0000 | 0.0050 | 0.0050 | 0.0025 |
| 16 | null | V2 | 0.9600 | 0.0000 | 0.0025 | 0.0025 | 0.0000 |
| 16 | null | MM | 1.0000 | 0.1400 | 0.0050 | 0.0075 | 0.1400 |
| 16 | null | JK | 0.9775 | 0.0175 | 0.0050 | 0.0100 | 0.0175 |
| 16 | antinoophor | V0 | 0.0275 | 0.0000 | 0.9975 | 0.9975 | 0.6950 |
| 16 | antinoophor | V2 | 0.9400 | 0.0100 | 0.9875 | 0.9425 | 0.0100 |
| 16 | antinoophor | MM | 1.0000 | 0.1700 | 0.9950 | 0.9950 | 0.1700 |
| 16 | antinoophor | JK | 0.9850 | 0.0475 | 0.9950 | 0.9925 | 0.0475 |

**Table 6 — where the bootstrap centres the gap †.** Across all 52 cells, the mean of the bootstrap `G*` minus the point estimate, and minus the plug-in `D̂_prior` computed from the same answers; the second column is meaningful for the estimators without a floor (MM, JK).

| estimator | `mean(G*) − Ĝ` | `mean(G*) − D̂_prior, plug-in` | gap Wald cover, grid † | movement Wald cover, grid † |
|---|---|---|---|---|
| V0 | +0.0203–+0.0492 | -0.0360–+0.0040 | 0.7550–0.9975 | 0.8800–1.0000 |
| V2 | +0.0203–+0.0437 | -0.0383–-0.0053 | 0.5925–0.9975 | 0.7075–1.0000 |
| MM | +0.0200–+0.0460 | +0.0052–+0.0287 | 0.6525–0.9000 | 0.8700–0.9975 |
| JK | +0.0214–+0.0500 | -0.0027–-0.0009 | 0.8875–0.9925 | 0.9350–0.9975 |
<!-- tables:end -->

---

*Prose: CC BY 4.0. Code: Apache-2.0.*
