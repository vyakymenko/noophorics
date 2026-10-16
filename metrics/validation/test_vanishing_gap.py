#!/usr/bin/env python3
"""Checks on the vanishing-gap simulation, run before its results are read.

Each piece the simulation replaces or adds is held against the library it
stands in for, or against a case whose answer is known, and each check is shown
able to fail on the nearest wrong version.
"""

import os
import random
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import vanishing_gap as vg  # noqa: E402
from noophorics import jensen_shannon, permutation_floor  # noqa: E402

LABELS = vg.OPTIONS


def draws(counts):
    return [lab for lab, c in zip(LABELS, counts) for _ in range(c)]


class DivergenceTests(unittest.TestCase):
    def test_jsd_matches_the_library(self):
        rng = random.Random(3)
        for _ in range(200):
            p = [rng.random() for _ in LABELS]
            q = [rng.random() for _ in LABELS]
            p = [x / sum(p) for x in p]
            q = [x / sum(q) for x in q]
            lib = jensen_shannon(dict(zip(LABELS, p)), dict(zip(LABELS, q)))
            self.assertAlmostEqual(vg.jsd(p, q), lib, places=12)

    def test_exact_floor_is_the_limit_of_the_permutation_floor(self):
        """The library's Monte Carlo floor at many shuffles lands on the sum."""
        for a, b in (((10, 4, 2), (12, 3, 1)), ((16, 0, 0), (9, 5, 2)),
                     ((3, 3, 4), (5, 2, 3)), ((7, 7, 2), (1, 13, 2))):
            with self.subTest(a=a, b=b):
                mc = permutation_floor(draws(a), draws(b), permutations=40000, seed=1)
                self.assertAlmostEqual(vg.exact_floor(a, b), mc, delta=0.0015)

    def test_the_floor_check_can_fail(self):
        """A floor at half the draws -- the v0.1 mistake -- is not within tolerance."""
        a, b = (10, 4, 2), (12, 3, 1)
        half = vg.exact_floor((5, 2, 1), (6, 2, 0))
        mc = permutation_floor(draws(a), draws(b), permutations=40000, seed=1)
        self.assertGreater(abs(half - mc), 0.0015)

    def test_one_answer_throughout_has_floor_zero(self):
        self.assertEqual(vg.exact_floor((16, 0, 0), (10, 0, 0)), 0.0)


class SamplingTests(unittest.TestCase):
    def test_multinomial_counts_sum_to_n_and_match_their_means(self):
        rng = random.Random(5)
        p = (0.6, 0.3, 0.1)
        totals = [0, 0, 0]
        reps = 20000
        for _ in range(reps):
            c = vg.multinomial(rng, 16, p)
            self.assertEqual(sum(c), 16)
            self.assertEqual(len(c), 3)
            for i, x in enumerate(c):
                totals[i] += x
        for i, pi in enumerate(p):
            self.assertAlmostEqual(totals[i] / reps / 16, pi, delta=0.005)

    def test_degenerate_probabilities(self):
        rng = random.Random(1)
        self.assertEqual(vg.multinomial(rng, 10, (1.0, 0.0, 0.0)), (10, 0, 0))
        self.assertEqual(vg.multinomial(rng, 10, (0.0, 0.0, 1.0)), (0, 0, 10))
        self.assertEqual(vg.multinomial(rng, 10, (0.0, 1.0, 0.0)), (0, 10, 0))


class FiellerTests(unittest.TestCase):
    def test_a_well_separated_denominator_gives_a_bounded_set_around_the_ratio(self):
        shape = vg.fieller(0.2, 0.4, 0.0004, 0.0001, 0.0004)
        self.assertEqual(shape[0], "bounded")
        self.assertTrue(vg.in_set(shape, 0.5))
        self.assertFalse(vg.in_set(shape, 2.0))

    def test_zero_over_zero_is_the_whole_line(self):
        shape = vg.fieller(0.001, 0.001, 0.0004, 0.0, 0.0004)
        self.assertEqual(shape[0], "line")
        self.assertTrue(vg.in_set(shape, -1e6))

    def test_a_clear_numerator_over_a_noisy_denominator_is_two_rays(self):
        shape = vg.fieller(0.3, 0.01, 0.0001, 0.0, 0.0004)
        self.assertEqual(shape[0], "rays")
        self.assertTrue(vg.in_set(shape, 0.3 / 0.01))
        self.assertTrue(vg.in_set(shape, -1e6))
        self.assertFalse(vg.in_set(shape, 0.0))

    def test_a_linear_inequality_is_a_half_line_not_the_whole_line(self):
        """g^2 == z^2·vgg makes the quadratic linear; it is a half-line."""
        g, vgg = 0.05, (0.05 / vg.Z) ** 2
        shape = vg.fieller(0.1, g, 0.001, 0.0, vgg)
        self.assertIn(shape[0], ("below", "above"))
        self.assertTrue(vg.in_set(shape, 0.1 / g))
        self.assertFalse(vg.in_set(shape, -1e6) and vg.in_set(shape, 1e6))

    def test_the_set_always_holds_the_point_estimate(self):
        rng = random.Random(9)
        for _ in range(2000):
            m, g = rng.uniform(-0.5, 0.5), rng.uniform(-0.2, 0.5)
            if abs(g) < 1e-6:
                continue
            vmm, vgg = rng.uniform(0, 0.01), rng.uniform(0, 0.01)
            vmg = rng.uniform(-1, 1) * (vmm * vgg) ** 0.5
            self.assertTrue(vg.in_set(vg.fieller(m, g, vmm, vmg, vgg), m / g))


class TrialTests(unittest.TestCase):
    def test_a_trial_is_reproducible(self):
        cell = vg.cells()[5]
        saved = vg.BOOT
        vg.BOOT = 30
        try:
            self.assertEqual(vg.run_trial(cell, 2), vg.run_trial(cell, 2))
        finally:
            vg.BOOT = saved

    def test_the_registered_design_has_the_planned_cells(self):
        cs = vg.cells()
        self.assertEqual(len(cs), 52)
        self.assertEqual(sum(1 for c in cs if c["kind"] == "grid"), 48)
        self.assertEqual(vg.TRIALS, 400)
        self.assertEqual(vg.BOOT, 400)


if __name__ == "__main__":
    unittest.main()
