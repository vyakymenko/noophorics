#!/usr/bin/env python3
"""Checks on the confirmation's generator and scoring, before its results are read.

Each check is paired with the case it must reject: the Dirichlet test tells the
two registered concentrations apart, the persistence test tells correlated from
independent answers by an exact variance, and the scoring tests sit on each
registered threshold from both sides.
"""

import os
import random
import statistics
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bias_corrected as bc  # noqa: E402
import confirm_candidate as cc  # noqa: E402
import vanishing_gap as vg  # noqa: E402


def dirichlet_var(alpha, k):
    m = 1.0 / k
    return m * (1 - m) / (k * alpha + 1)


def persistent_count_var(n, p, rho):
    """Exact variance of one option's count: lag-h correlation of its indicator is rho**h."""
    base = p * (1 - p)
    return n * base + 2 * base * sum((n - h) * rho ** h for h in range(1, n))


class GeneratorTests(unittest.TestCase):
    def test_dirichlet_has_its_mean_and_variance_and_not_the_others(self):
        for k in cc.KS:
            for alpha, other in ((cc.ALPHA_SENDER, cc.ALPHA_DIFFUSE),
                                 (cc.ALPHA_DIFFUSE, cc.ALPHA_SENDER)):
                with self.subTest(k=k, alpha=alpha):
                    rng = random.Random(11)
                    xs = [cc.dirichlet(rng, alpha, k) for _ in range(40000)]
                    for i in range(k):
                        col = [x[i] for x in xs]
                        self.assertAlmostEqual(statistics.fmean(col), 1.0 / k, delta=0.006)
                    v = statistics.pvariance([x[0] for x in xs])
                    self.assertLess(abs(v / dirichlet_var(alpha, k) - 1), 0.05)
                    self.assertGreater(abs(v / dirichlet_var(other, k) - 1), 0.4)

    def test_persistence_keeps_the_marginal(self):
        p = (0.6, 0.3, 0.1)
        for rho in cc.RHOS:
            with self.subTest(rho=rho):
                rng = random.Random(5)
                total = [0, 0, 0]
                for _ in range(20000):
                    for i, c in enumerate(cc.persistent_counts(rng, 16, p, rho)):
                        total[i] += c
                shares = [t / sum(total) for t in total]
                for s, pi in zip(shares, p):
                    self.assertAlmostEqual(s, pi, delta=0.006)

    def test_persistence_repeats_at_the_stated_rate(self):
        p = (0.5, 0.3, 0.2)
        for rho in cc.RHOS:
            with self.subTest(rho=rho):
                rng = random.Random(9)
                same = pairs = 0
                for _ in range(20000):
                    a = cc.persistent_answers(rng, 10, p, rho)
                    same += sum(1 for x, y in zip(a, a[1:]) if x == y)
                    pairs += len(a) - 1
                want = rho + (1 - rho) * sum(x * x for x in p)
                self.assertAlmostEqual(same / pairs, want, delta=0.006)

    def test_count_variance_is_exact_and_correlation_widens_it(self):
        # The registered C4 rests on this: at rho = 0.3 a count varies more than
        # the multinomial the bootstrap assumes; at rho = 0 it does not.
        p, n = (0.5, 0.3, 0.2), 16
        multinomial = n * p[0] * (1 - p[0])
        for rho in cc.RHOS:
            with self.subTest(rho=rho):
                rng = random.Random(13)
                xs = [cc.persistent_counts(rng, n, p, rho)[0] for _ in range(40000)]
                v = statistics.pvariance(xs)
                self.assertLess(abs(v / persistent_count_var(n, p[0], rho) - 1), 0.04)
                if rho == 0.0:
                    self.assertLess(abs(v / multinomial - 1), 0.04)
                else:
                    self.assertGreater(v / multinomial, 1.5)

    def test_zero_gap_cells_have_zero_gap_and_the_right_movement(self):
        for k in cc.KS:
            for kind in cc.ZERO_GAP:
                cell = {"index": 0, "k": k, "rho": 0.0, "n": 10, "kind": kind,
                        "g": 1.0, "lam": None}
                s, p, q = cc.truth_for(random.Random(3), cell)
                with self.subTest(k=k, kind=kind):
                    self.assertEqual(s, p)
                    self.assertTrue(all(len(x) == k for x in s + p + q))
                    move = -sum(vg.jsd(a, b) for a, b in zip(s, q))
                    if kind == "null":
                        self.assertEqual(move, 0.0)
                    else:
                        self.assertLess(move, 0.0)


class TrialTests(unittest.TestCase):
    def test_the_frozen_estimator_is_the_one_used(self):
        cell = cc.cells()[5]
        rec = cc.run_trial(cell, 2)
        rng = random.Random(7_000_003 * cell["index"] + 2)
        sender, prior, post = cc.truth_for(rng, cell)
        draws = [[cc.persistent_counts(rng, cell["n"], d, cell["rho"]) for d in ds]
                 for ds in (sender, prior, post)]
        m, g = bc.corrected(bc.jsd_jk, *draws)
        self.assertEqual((rec["m_hat"], rec["g_hat"]), (m, g))
        plug_m, plug_g = bc.corrected(vg.jsd_counts, *draws)
        self.assertNotEqual(rec["g_hat"], plug_g)

    def test_trials_are_deterministic_and_distinct(self):
        cell = cc.cells()[40]
        self.assertEqual(cc.run_trial(cell, 1), cc.run_trial(cell, 1))
        self.assertNotEqual(cc.run_trial(cell, 1)["g_hat"], cc.run_trial(cell, 2)["g_hat"])

    def test_the_cells_are_the_registered_ones(self):
        cs = cc.cells()
        self.assertEqual(len(cs), 64)
        self.assertEqual(sum(1 for c in cs if c["kind"] == "grid"), 48)
        self.assertEqual([c["index"] for c in cs], list(range(64)))
        self.assertEqual(len({(c["k"], c["rho"], c["n"], c["kind"], c["g"], c["lam"])
                              for c in cs}), 64)


def summary(over=None):
    """A synthetic record on which every registered prediction holds."""
    out = []
    for c in cc.cells():
        row = dict(c)
        grid = c["kind"] == "grid"
        row.update({
            "cover_fieller": (0.95 if c["rho"] == 0.0 else 0.90) if grid else None,
            "fieller_bounded": 0.3 if grid and c["g"] == 0.95 else 0.9,
            "move_cover": 0.95, "gap_cover": 0.95,
            "move_excludes_zero": 0.05, "move_excludes_zero_away": 0.9,
            "gap_above_zero": 0.05,
        })
        out.append(row)
    for (index, key), value in (over or {}).items():
        out[index][key] = value
    return out


class ScoreTests(unittest.TestCase):
    def holds(self, rows):
        return {k: v["holds"] for k, v in cc.score(rows).items()}

    def test_all_hold_on_the_green_record(self):
        self.assertEqual(self.holds(summary()), {f"C{i}": True for i in range(1, 6)})

    def test_each_threshold_is_met_at_the_boundary_and_missed_below(self):
        cs = cc.cells()
        g0 = next(c["index"] for c in cs if c["kind"] == "grid" and c["rho"] == 0.0)
        g3 = next(c["index"] for c in cs if c["kind"] == "grid" and c["rho"] == 0.3)
        hi = next(c["index"] for c in cs if c["kind"] == "grid" and c["rho"] == 0.0
                  and c["g"] == 0.95)
        anti = next(c["index"] for c in cs if c["kind"] == "antinoophor" and c["rho"] == 0.0
                    and c["n"] == 16)
        anti10 = next(c["index"] for c in cs if c["kind"] == "antinoophor" and c["rho"] == 0.0
                      and c["n"] == 10)
        null = next(c["index"] for c in cs if c["kind"] == "null" and c["rho"] == 0.0)
        cases = [
            ("C1", (g0, "cover_fieller"), 0.93, 0.9299),
            ("C2", (g0, "move_cover"), 0.93, 0.9299),
            ("C2", (anti, "move_excludes_zero_away"), 0.80, 0.7999),
            ("C2", (null, "move_excludes_zero"), 0.08, 0.0801),
            ("C3", (g0, "gap_cover"), 0.90, 0.8999),
            ("C3", (null, "gap_above_zero"), 0.10, 0.1001),
            ("C5", (hi, "fieller_bounded"), 0.4999, 0.5),
        ]
        for name, where, ok, bad in cases:
            with self.subTest(name=name, where=where):
                self.assertTrue(self.holds(summary({where: ok}))[name])
                self.assertFalse(self.holds(summary({where: bad}))[name])
        # outside the registered scope a value does not count
        self.assertTrue(self.holds(summary({(anti10, "move_excludes_zero_away"): 0.1}))["C2"])
        self.assertTrue(self.holds(summary({(g3, "move_cover"): 0.5}))["C2"])

    def test_c4_needs_half_the_dependent_cells_below(self):
        dep = [c["index"] for c in cc.cells() if c["kind"] == "grid" and c["rho"] == 0.3]
        self.assertEqual(len(dep), 24)
        for below, want in ((12, True), (11, False)):
            over = {(i, "cover_fieller"): (0.90 if j < below else 0.95)
                    for j, i in enumerate(dep)}
            with self.subTest(below=below):
                self.assertEqual(self.holds(summary(over))["C4"], want)


if __name__ == "__main__":
    unittest.main()
