#!/usr/bin/env python3
"""Checks on the bias-corrected divergences, before their results are read.

The bias claims are tested exactly: every pair of multinomial outcomes is
enumerated, so the expected value of each estimator is computed, not sampled.
"""

import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bias_corrected as bc  # noqa: E402
import vanishing_gap as vg  # noqa: E402


def outcomes(n):
    for a in range(n + 1):
        for b in range(n + 1 - a):
            yield (a, b, n - a - b)


def pmf(c, p):
    n = sum(c)
    coef = math.factorial(n) / math.prod(math.factorial(x) for x in c)
    return coef * math.prod(pi ** ci for pi, ci in zip(p, c))


def exact_bias(p, q, n):
    space = list(outcomes(n))
    pp = {o: pmf(o, p) for o in space}
    qq = {o: pmf(o, q) for o in space}
    acc = {"plug": 0.0, "MM": 0.0, "JK": 0.0}
    for a in space:
        for b in space:
            w = pp[a] * qq[b]
            acc["plug"] += w * vg.jsd_counts(a, b)
            acc["MM"] += w * bc.jsd_mm(a, b)
            acc["JK"] += w * bc.jsd_jk(a, b)
    truth = vg.jsd(p, q)
    return {k: v - truth for k, v in acc.items()}


PAIRS = [((.7, .2, .1), (.7, .2, .1)),          # identical: the null case
         ((.7, .2, .1), (.6, .25, .15)),        # close
         ((.8, .15, .05), (.3, .4, .3)),        # far
         ((.9, .05, .05), (.1, .1, .8))]        # very far


class BiasTests(unittest.TestCase):
    def test_both_corrections_shrink_the_plug_in_bias_exactly(self):
        for p, q in PAIRS:
            for n in (10, 16):
                with self.subTest(p=p, q=q, n=n):
                    b = exact_bias(p, q, n)
                    self.assertGreater(b["plug"], 0.0)            # plug-in is biased up
                    self.assertLess(abs(b["JK"]), abs(b["plug"]))
                    self.assertLess(abs(b["MM"]), abs(b["plug"]))

    def test_the_bias_check_can_fail(self):
        """An estimator that adds bias instead of removing it is caught."""
        p, q, n = PAIRS[1][0], PAIRS[1][1], 10
        space = list(outcomes(n))
        wrong = sum(pmf(a, p) * pmf(b, q) * (2 * vg.jsd_counts(a, b))
                    for a in space for b in space) - vg.jsd(p, q)
        self.assertGreater(abs(wrong), abs(exact_bias(p, q, n)["plug"]))


class EstimatorTests(unittest.TestCase):
    def test_miller_madow_matches_its_formula(self):
        a, b = (5, 3, 2), (4, 4, 2)
        pooled = (9, 7, 4)

        def h(c, n):
            return (-sum((x / n) * math.log2(x / n) for x in c if x)
                    + (sum(1 for x in c if x) - 1) / (2 * n * math.log(2)))
        expected = h(pooled, 20) - 0.5 * (h(a, 10) + h(b, 10))
        self.assertAlmostEqual(bc.jsd_mm(a, b), expected, places=12)

    def test_miller_madow_refuses_unequal_sizes(self):
        with self.assertRaises(ValueError):
            bc.jsd_mm((5, 3, 2), (4, 4, 3))

    def test_the_jackknife_is_symmetric_in_its_parties(self):
        for a, b in (((5, 3, 2), (4, 4, 2)), ((10, 0, 0), (2, 3, 5))):
            self.assertAlmostEqual(bc.jsd_jk(a, b), bc.jsd_jk(b, a), places=12)

    def test_corrected_divergences_may_go_below_zero(self):
        """Neither correction is clamped; a clamp would reintroduce the bias."""
        self.assertLess(bc.jsd_jk((5, 3, 2), (5, 3, 2)), 0.0)


class ReproductionTests(unittest.TestCase):
    def test_plug_in_reports_equal_the_previous_simulation_from_the_same_seed(self):
        """Same seed, same draw order: V0/V2 here must be vanishing_gap's exactly."""
        saved = vg.BOOT
        vg.BOOT = 30
        try:
            for cell in (vg.cells()[5], vg.cells()[-1]):
                with self.subTest(cell=cell["index"]):
                    mine = bc.run_trial(cell, 3)["reports"]
                    theirs = vg.run_trial(cell, 3)["variants"]
                    for v in bc.PLUGIN:
                        self.assertEqual(mine[v]["g_hat"], theirs[v]["g_hat"])
                        self.assertEqual(mine[v]["fieller"], theirs[v]["fieller"])
                        self.assertEqual(mine[v].get("cover_fieller"),
                                         theirs[v].get("cover_fieller"))
        finally:
            vg.BOOT = saved


if __name__ == "__main__":
    unittest.main()
