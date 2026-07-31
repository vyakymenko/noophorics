#!/usr/bin/env python3
"""Reproduce E-002b's finding that its own headline statistic could not fail.

FINDINGS section 5 reports that corr(fidelity, Phi) returns the same value
against counterfactual parties calibrated anywhere from beta = 0 to beta = 0.99,
breaking only at exactly 1.0. That table existed only as prose: no file in the
repository produced it, in a project whose whole ask is that its numbers be
recomputed. This is the file.

    python3 metrics/validation/beta_sweep.py

The construction: replace each brief's actual claim with a counterfactual claim
that tracks that brief's observed agreement at slope beta,

    C_beta = mean(C) + beta * (O - mean(O))

so beta = 0 is a party whose confidence ignores the outcome entirely and
beta = 1 is a perfectly calibrated one. Then recompute the statistic H5 was
pre-registered on. If it is a good estimator of "does confidence track
transfer", it should move a great deal across that range.
"""

from __future__ import annotations

import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "metrics"))

from noophorics import point_biserial  # noqa: E402

RESULTS = os.path.join(
    REPO, "experiments", "E-002b-phantom-agreement-ladder", "results",
    "E-002b-20260731T064958Z.json")
BETAS = (0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0)


def main() -> int:
    if not os.path.exists(RESULTS):
        print("no results file at %s" % RESULTS, file=sys.stderr)
        return 2
    with open(RESULTS, "r", encoding="utf-8") as fh:
        r = json.load(fh)
    pb = r["per_brief"]
    labs = sorted(pb)

    fid = [pb[l]["fidelity_where_sender_right"] for l in labs]
    obs = [statistics.mean(pb[l]["observed_per_probe"]) for l in labs]
    claim = [(statistics.mean(pb[l]["claims_sender"])
              + statistics.mean(pb[l]["claims_receiver"])) / 2 for l in labs]

    reported = r["effects"]["H5_phi_rises_as_fidelity_falls"]["value"]
    actual = point_biserial(fid, [c - o for c, o in zip(claim, obs)])
    print("E-002b, %d briefs" % len(labs))
    print("  H5 as reported in the results file : %+.4f" % reported)
    print("  recomputed from the raw record     : %+.4f  %s\n"
          % (actual, "match" if abs(actual - reported) < 5e-4 else "MISMATCH"))

    mo, mc = statistics.mean(obs), statistics.mean(claim)
    print("  beta   corr(fidelity, Phi)   sd(Phi)")
    print("  ----   ------------------   -------")
    for b in BETAS:
        cf = [mc + b * (o - mo) for o in obs]
        phi = [c - o for c, o in zip(cf, obs)]
        sd = statistics.pstdev(phi)
        print("  %4.2f        %+7.4f          %.4f" % (b, point_biserial(fid, phi), sd))

    print("\n  The statistic is flat to four decimals from beta = 0 to 0.99 and")
    print("  flips only at exactly 1.0, where Phi becomes constant. It would have")
    print("  read about -0.98 against parties calibrated at 99%.")
    print("\n  sd(Phi) is the column that carries the information: it scales as")
    print("  (1 - beta) and is the reason E-002c is pre-registered on the slope")
    print("  rather than on this correlation.")

    # The decomposition, which is the same fact stated as covariances.
    def cov(x, y):
        mx, my = statistics.mean(x), statistics.mean(y)
        return sum((a - mx) * (b - my) for a, b in zip(x, y)) / len(x)

    c_fp = cov(fid, [c - o for c, o in zip(claim, obs)])
    c_fc, c_fo = cov(fid, claim), cov(fid, obs)
    print("\n  cov(fid, Phi) = cov(fid, claimed) - cov(fid, observed)")
    print("     %+.5f  =        %+.5f    -       %+.5f" % (c_fp, c_fc, c_fo))
    print("  claim movement contributes %+.1f%%, outcome movement %+.1f%%"
          % (100 * c_fc / c_fp, 100 * -c_fo / c_fp))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
