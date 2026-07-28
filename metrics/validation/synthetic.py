#!/usr/bin/env python3
"""Synthetic validation: does the estimator recover a known F*?

Every test in metrics/tests checks the *algebra* -- that F* is 1 when the gap
closes, 0 when nothing changes, negative for an antinoophor. Not one of them
checks the *estimator*: whether the number computed from finite samples
recovers the truth. That gap is how the v0.1 noise floor shipped inflated.

Here the agents are synthetic, so their true answer distributions are known
exactly and the true F* is computable in closed form with no sampling at all.
We then draw n samples per probe, estimate F* three ways, and see which one
recovers the truth.

    python3 metrics/validation/synthetic.py

Three estimators under test:

    naive         no floor correction at all
    v0.1          split-halves floor (n/2 vs n/2), the shipped version
    v0.2          permutation-null floor at full n

Run this before trusting any fidelity number this repository produces.
"""

from __future__ import annotations

import os
import random
import sys
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from noophorics import (  # noqa: E402
    jensen_shannon,
    mean_divergence,
    mean_permutation_floor,
    noise_floor,
    to_distribution,
)

OPTIONS = ("HANDLED", "RETURNED", "PADDED")
N_PROBES = 40


# --------------------------------------------------------------------------
# ground truth


def make_true_distributions(
    rng: random.Random, lam: float
) -> Tuple[List[Dict[str, float]], List[Dict[str, float]], List[Dict[str, float]]]:
    """Build exact answer distributions for sender, prior receiver, post receiver.

    ``lam`` is how far the message moved the receiver toward the sender:
    0.0 = the message changed nothing, 1.0 = the receiver now matches exactly.

    True F* is NOT lam -- JSD is not linear in the mixture -- so it is computed
    from the exact distributions below rather than assumed.
    """
    sender, prior, post = [], [], []
    for _ in range(N_PROBES):
        a = _random_dist(rng, concentration=6.0)   # sender: fairly decided
        b = _random_dist(rng, concentration=1.2)   # prior receiver: diffuse, far
        c = {k: (1.0 - lam) * b.get(k, 0.0) + lam * a.get(k, 0.0) for k in OPTIONS}
        sender.append(a)
        prior.append(b)
        post.append(c)
    return sender, prior, post


def _random_dist(rng: random.Random, concentration: float) -> Dict[str, float]:
    """A random categorical distribution. Higher concentration = more decided."""
    weights = [rng.random() ** concentration + 1e-6 for _ in OPTIONS]
    total = sum(weights)
    return {opt: w / total for opt, w in zip(OPTIONS, weights)}


def true_fidelity(
    sender: Sequence[Dict[str, float]],
    prior: Sequence[Dict[str, float]],
    post: Sequence[Dict[str, float]],
) -> Tuple[float, float, float]:
    """Exact D_prior, D_post and F*, computed with no sampling.

    With exact distributions the noise floor is zero by construction: there is
    no sampling, so there is nothing for a floor to correct.
    """
    d_prior = sum(jensen_shannon(a, b) for a, b in zip(sender, prior)) / len(sender)
    d_post = sum(jensen_shannon(a, c) for a, c in zip(sender, post)) / len(sender)
    return d_prior, d_post, (d_prior - d_post) / d_prior


# --------------------------------------------------------------------------
# sampling and estimation


def draw(dist: Dict[str, float], n: int, rng: random.Random) -> List[str]:
    """n independent draws, order preserved."""
    out = []
    for _ in range(n):
        u, acc = rng.random(), 0.0
        for opt, p in dist.items():
            acc += p
            if u <= acc:
                out.append(opt)
                break
        else:
            out.append(list(dist)[-1])
    return out


def estimate(
    sender_s: List[List[str]],
    prior_s: List[List[str]],
    post_s: List[List[str]],
) -> Dict[str, float]:
    """F* under each estimator, from the same draws."""
    sd = [to_distribution(s) for s in sender_s]
    pd = [to_distribution(s) for s in prior_s]
    od = [to_distribution(s) for s in post_s]

    d_prior = mean_divergence(sd, pd)
    d_post = mean_divergence(sd, od)

    out = {"naive": (d_prior - d_post) / d_prior if d_prior > 0 else float("nan")}

    # v0.1: split-halves self-divergence, averaged -- the shipped floor.
    half = len(sender_s[0]) // 2
    d_self_sender = mean_divergence(
        [to_distribution(s[:half]) for s in sender_s],
        [to_distribution(s[half:]) for s in sender_s],
    )
    d_self_post = mean_divergence(
        [to_distribution(s[:half]) for s in post_s],
        [to_distribution(s[half:]) for s in post_s],
    )
    f_v1 = noise_floor(d_self_sender, d_self_post)
    denom_v1 = d_prior - f_v1
    out["v0.1"] = (d_prior - d_post) / denom_v1 if denom_v1 > 1e-9 else float("nan")

    # v0.2: permutation null at full n.
    f_v2 = mean_permutation_floor(sender_s, post_s, permutations=200)
    denom_v2 = d_prior - f_v2
    out["v0.2"] = (d_prior - d_post) / denom_v2 if denom_v2 > 1e-9 else float("nan")

    out["_floor_v0.1"] = f_v1
    out["_floor_v0.2"] = f_v2
    return out


# --------------------------------------------------------------------------


def run(n_samples: int, trials: int = 60) -> None:
    print("\n  n = %d samples per probe, %d probes, %d trials per cell"
          % (n_samples, N_PROBES, trials))
    print("  %-9s %-9s | %-27s | %s"
          % ("lambda", "true F*", "estimated F* (mean err)", "floor"))
    print("  " + "-" * 74)

    for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
        truths, acc = [], {"naive": [], "v0.1": [], "v0.2": [],
                           "_floor_v0.1": [], "_floor_v0.2": []}
        for trial in range(trials):
            rng = random.Random(1000 * trial + int(lam * 97))
            sender, prior, post = make_true_distributions(rng, lam)
            _, _, f_true = true_fidelity(sender, prior, post)
            truths.append(f_true)
            s = [draw(d, n_samples, rng) for d in sender]
            p = [draw(d, n_samples, rng) for d in prior]
            o = [draw(d, n_samples, rng) for d in post]
            est = estimate(s, p, o)
            for k in acc:
                acc[k].append(est[k])

        t = sum(truths) / len(truths)
        errs = {
            k: sum(v) / len(v) - t
            for k, v in acc.items() if not k.startswith("_")
        }
        floors = {k: sum(v) / len(v) for k, v in acc.items() if k.startswith("_")}
        print("  %-9.2f %-9.3f | naive %+.3f  v0.1 %+.3f  v0.2 %+.3f | %.3f / %.3f"
              % (lam, t, errs["naive"], errs["v0.1"], errs["v0.2"],
                 floors["_floor_v0.1"], floors["_floor_v0.2"]))


def main() -> int:
    print("=" * 78)
    print("  SYNTHETIC VALIDATION -- does the estimator recover a known F*?")
    print("=" * 78)
    print("""
  Agents are synthetic: their true answer distributions are known exactly, so
  the true F* is computed in closed form. Columns show the MEAN ERROR of each
  estimator against that truth -- closer to zero is better. The last column is
  the mean floor each method estimated; the true floor is 0, because exact
  distributions involve no sampling.""")
    for n in (6, 12, 30):
        run(n)
    print("""
  Reading -- three findings, and the third is the one that matters.

  1. The v0.1 split-halves floor overshoots badly. At n=6 and a true F* of
     0.646 it reports +0.330 of error: a 51% inflation. E-001 was configured
     at n=6, so every fidelity it would have produced was wrong by about half.

  2. The naive estimator errs the other way. With no correction, sampling
     noise in D_post drags fidelity down -- the mirror-image mistake.

  3. THE PERMUTATION FLOOR IS BETTER, NOT CORRECT. At n=6 it still carries
     +0.113 of error at the same point. Three times better than v0.1 is not
     the same as usable. No floor estimator rescues n=6; the sample size is
     the binding constraint, and only by n=30 does v0.2 fall under ~0.02.

  The honest conclusion is not "the floor is fixed". It is that fidelity
  measured at n=6 is not a measurement, whichever floor you subtract.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
