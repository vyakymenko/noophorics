"""Tests for the noophoric metrics.

These check the properties the definitions claim, not just that the code runs:
boundedness of JSD, the meaning of the fidelity endpoints, that antinoophors
survive unclipped, and that inadmissible probe measures refuse to produce a
flattering number instead of an error.
"""

from __future__ import annotations

import math
import random
import sys
import unittest
from os.path import abspath, dirname, join

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from noophorics import (  # noqa: E402
    InadmissibleProbeMeasure,
    Measurement,
    Probe,
    ProbeMeasure,
    agreement_rate,
    capacity_estimate,
    capacity_lower_bound,
    claimed_agreement,
    efficiency,
    jensen_shannon,
    mean_divergence,
    noise_floor,
    phantom_agreement,
    self_divergence,
    to_distribution,
    transfer_fidelity,
)


class TestDivergence(unittest.TestCase):
    def test_identical_distributions_have_zero_divergence(self):
        p = {"A": 0.7, "B": 0.3}
        self.assertAlmostEqual(jensen_shannon(p, dict(p)), 0.0, places=12)

    def test_disjoint_support_is_maximal(self):
        # Base-2 JSD between fully disjoint point masses is exactly 1 bit.
        self.assertAlmostEqual(
            jensen_shannon({"A": 1.0}, {"B": 1.0}), 1.0, places=12
        )

    def test_divergence_is_symmetric(self):
        p, q = {"A": 0.9, "B": 0.1}, {"A": 0.2, "C": 0.8}
        self.assertAlmostEqual(jensen_shannon(p, q), jensen_shannon(q, p), places=12)

    def test_divergence_is_bounded(self):
        for p, q in [
            ({"A": 1.0}, {"A": 1.0}),
            ({"A": 1.0}, {"B": 1.0}),
            ({"A": 0.5, "B": 0.5}, {"B": 0.5, "C": 0.5}),
        ]:
            value = jensen_shannon(p, q)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_empty_sample_set_is_an_error_not_a_uniform_prior(self):
        with self.assertRaises(ValueError):
            to_distribution([])

    def test_mean_divergence_rejects_misaligned_probes(self):
        with self.assertRaises(ValueError):
            mean_divergence([{"A": 1.0}], [{"A": 1.0}, {"B": 1.0}])

    def test_agreement_rate_uses_modal_answers(self):
        a = [{"YES": 0.6, "NO": 0.4}, {"YES": 1.0}]
        b = [{"YES": 0.9, "NO": 0.1}, {"NO": 1.0}]
        self.assertAlmostEqual(agreement_rate(a, b), 0.5)


class TestNoiseFloor(unittest.TestCase):
    def test_floor_is_the_mean_of_self_divergences(self):
        self.assertAlmostEqual(noise_floor(0.10, 0.20), 0.15)

    def test_floor_rejects_out_of_range_inputs(self):
        with self.assertRaises(ValueError):
            noise_floor(-0.1, 0.2)

    def test_sample_order_must_be_preserved_when_splitting_halves(self):
        """Regression: round-tripping samples through a distribution loses the
        draw order, sorts them, and inflates the floor to its maximum.

        An agent that genuinely alternates between two answers has moderate
        self-divergence. The same six draws, sorted, split into two pure
        halves and read as an agent that never agrees with itself.
        """
        drawn = ["A", "B", "A", "B", "A", "B"]
        sorted_same_counts = ["A", "A", "A", "B", "B", "B"]

        def floor_from(samples):
            mid = len(samples) // 2
            return self_divergence(
                [to_distribution(samples[:mid])], [to_distribution(samples[mid:])]
            )

        drawn_floor = floor_from(drawn)
        sorted_floor = floor_from(sorted_same_counts)

        # Same six draws, same answer counts -- only the order differs.
        self.assertLess(drawn_floor, 0.1)
        self.assertAlmostEqual(sorted_floor, 1.0, places=12)
        self.assertGreater(sorted_floor / max(drawn_floor, 1e-9), 10.0)


class TestFidelity(unittest.TestCase):
    def test_closing_the_gap_to_the_floor_is_unity(self):
        self.assertAlmostEqual(
            transfer_fidelity(d_prior=0.60, d_post=0.10, d_floor=0.10), 1.0
        )

    def test_no_change_is_zero(self):
        self.assertAlmostEqual(
            transfer_fidelity(d_prior=0.60, d_post=0.60, d_floor=0.10), 0.0
        )

    def test_half_the_closable_gap_is_one_half(self):
        # closable gap = 0.60 - 0.10 = 0.50; post at 0.35 closed 0.25 of it.
        self.assertAlmostEqual(
            transfer_fidelity(d_prior=0.60, d_post=0.35, d_floor=0.10), 0.5
        )

    def test_ignoring_the_floor_understates_fidelity(self):
        corrected = transfer_fidelity(0.60, 0.15, 0.10)
        uncorrected = (0.60 - 0.15) / 0.60
        self.assertGreater(corrected, uncorrected)

    def test_antinoophor_stays_negative(self):
        # A message that pushed the receiver further away must not be clipped.
        value = transfer_fidelity(d_prior=0.40, d_post=0.65, d_floor=0.05)
        self.assertLess(value, 0.0)

    def test_capped_above_one(self):
        # Post-transfer divergence below the floor is sampling luck.
        self.assertAlmostEqual(
            transfer_fidelity(d_prior=0.60, d_post=0.02, d_floor=0.10), 1.0
        )

    def test_inadmissible_measure_raises_rather_than_flattering(self):
        with self.assertRaises(InadmissibleProbeMeasure):
            transfer_fidelity(d_prior=0.11, d_post=0.02, d_floor=0.10)


class TestEfficiencyAndPhantom(unittest.TestCase):
    def test_efficiency_is_fidelity_per_kilotoken(self):
        self.assertAlmostEqual(efficiency(0.8, cost=400.0), 2.0)

    def test_zero_cost_is_rejected(self):
        with self.assertRaises(ValueError):
            efficiency(0.8, cost=0.0)

    def test_shared_illusion_is_positive(self):
        claimed = claimed_agreement(sender_claim=0.9, receiver_claim=0.8)
        self.assertAlmostEqual(phantom_agreement(claimed, observed=0.5), 0.35)

    def test_mutual_underconfidence_is_negative(self):
        claimed = claimed_agreement(0.4, 0.3)
        self.assertLess(phantom_agreement(claimed, observed=0.7), 0.0)

    def test_claims_must_be_rates(self):
        with self.assertRaises(ValueError):
            claimed_agreement(1.4, 0.5)

    def test_capacity_is_the_best_found(self):
        self.assertAlmostEqual(capacity_estimate([0.2, 0.71, 0.55]), 0.71)


class TestProbes(unittest.TestCase):
    def _measure(self) -> ProbeMeasure:
        return ProbeMeasure(
            id="TEST-1",
            probes=[
                Probe("p1", "Case one.", ["YES", "NO"], key="YES"),
                Probe("p2", "Case two.", ["YES", "NO"], key="NO"),
            ],
        )

    def test_answer_space_needs_two_options(self):
        with self.assertRaises(ValueError):
            Probe("p", "prompt", ["ONLY"])

    def test_key_must_be_in_the_answer_space(self):
        with self.assertRaises(ValueError):
            Probe("p", "prompt", ["YES", "NO"], key="MAYBE")

    def test_content_hash_is_stable_across_roundtrip(self):
        measure = self._measure()
        restored = ProbeMeasure.from_dict(measure.to_dict())
        self.assertEqual(measure.content_hash, restored.content_hash)

    def test_content_hash_changes_when_a_probe_changes(self):
        before = self._measure().content_hash
        after = ProbeMeasure(
            id="TEST-1",
            probes=[
                Probe("p1", "Case one, amended.", ["YES", "NO"], key="YES"),
                Probe("p2", "Case two.", ["YES", "NO"], key="NO"),
            ],
        ).content_hash
        self.assertNotEqual(before, after)

    def test_accuracy_against_the_key(self):
        self.assertAlmostEqual(self._measure().accuracy(["YES", "YES"]), 0.5)


class TestMeasurement(unittest.TestCase):
    def _m(self, **overrides) -> Measurement:
        base = dict(
            probe_measure_id="TEST-1@abc123",
            samples_per_probe=5,
            sender="claude-opus-5/spec",
            receiver="claude-opus-5/blank",
            d_prior=0.60,
            d_post=0.20,
            d_floor=0.10,
            cost_tokens=350.0,
            cost_unit="tokens",
            agreement_observed=0.62,
            claim_sender=0.85,
            claim_receiver=0.80,
            condition="narrative",
        )
        base.update(overrides)
        return Measurement(**base)

    def test_derived_quantities(self):
        m = self._m()
        self.assertAlmostEqual(m.fidelity, 0.8)
        self.assertAlmostEqual(m.efficiency, 0.8 * 1000 / 350)
        self.assertAlmostEqual(m.phantom, 0.825 - 0.62)
        self.assertFalse(m.is_antinoophor)

    def test_phantom_is_none_without_claims(self):
        self.assertIsNone(self._m(claim_sender=None, claim_receiver=None).phantom)

    def test_summary_is_printable(self):
        self.assertIn("F*=", self._m().summary())




class TestV03Decomposition(unittest.TestCase):
    """The v0.3 decomposition: understanding vs mimicry vs decisiveness."""

    def _measure(self) -> ProbeMeasure:
        return ProbeMeasure(
            id="D-4",
            probes=[
                Probe("d1", "one", ["A", "B"], key="A"),
                Probe("d2", "two", ["A", "B"], key="A"),
                Probe("d3", "three", ["A", "B"], key="B"),
                Probe("d4", "four", ["A", "B"], key="B"),
            ],
        )

    def test_error_replication_is_visible(self):
        from noophorics.decomposition import decompose

        measure = self._measure()
        # Sender is wrong on d4: says A where the key says B.
        sender = [["A"] * 4, ["A"] * 4, ["B"] * 4, ["A"] * 4]
        prior = [["B"] * 4, ["B"] * 4, ["A"] * 4, ["B"] * 4]

        mimic = [["A"] * 4, ["A"] * 4, ["B"] * 4, ["A"] * 4]   # copies the error
        correct = [["A"] * 4, ["A"] * 4, ["B"] * 4, ["B"] * 4]  # gets d4 right

        d_mimic = decompose(measure, sender, prior, mimic)
        d_correct = decompose(measure, sender, prior, correct)

        self.assertAlmostEqual(d_mimic.error_replication, 1.0)
        self.assertAlmostEqual(d_correct.error_replication, 0.0)
        # The mimic scores HIGHER on aggregate fidelity while being less
        # accurate -- the exact pathology E-001 exposed.
        self.assertGreater(d_mimic.fidelity_aggregate, d_correct.fidelity_aggregate)
        self.assertGreater(d_correct.accuracy_gain, d_mimic.accuracy_gain)

    def test_decomposition_requires_a_key(self):
        from noophorics.decomposition import decompose

        unkeyed = ProbeMeasure("U", [Probe("u1", "one", ["A", "B"])])
        with self.assertRaises(ValueError):
            decompose(unkeyed, [["A"] * 4], [["B"] * 4], [["A"] * 4])

    def test_class_prior_baseline_carries_no_rule_content(self):
        from noophorics.decomposition import class_prior_baseline_draws

        sender = [["A"] * 4, ["A"] * 4, ["B"] * 4, ["B"] * 4]
        baseline = class_prior_baseline_draws(sender, 4, seed=3)
        self.assertEqual(len(baseline), 4)
        self.assertTrue(all(len(b) == 4 for b in baseline))
        # Every draw comes from the sender's pooled marginal, never the probe.
        self.assertTrue(all(a in ("A", "B") for b in baseline for a in b))


class TestHeldOutProbes(unittest.TestCase):
    """A3's repair: capacity is only meaningful on probes the sender never saw."""

    def _measure(self, holdout=None) -> ProbeMeasure:
        return ProbeMeasure(
            id="H-4",
            probes=[Probe("h%d" % i, "p", ["A", "B"], key="A") for i in range(4)],
            holdout=holdout,
        )

    def test_split_partitions_the_measure(self):
        m = self._measure(holdout=["h0", "h1"])
        self.assertEqual(len(m.visible()), 2)
        self.assertEqual(len(m.held_out()), 2)
        self.assertEqual(
            sorted(p.id for p in m.held_out()), ["h0", "h1"]
        )

    def test_holdout_must_name_real_probes(self):
        with self.assertRaises(ValueError):
            self._measure(holdout=["nope"])

    def test_holdout_changes_the_frame_identity(self):
        self.assertNotEqual(
            self._measure().content_hash,
            self._measure(holdout=["h0"]).content_hash,
        )

    def test_weights_are_part_of_the_frame(self):
        base = ProbeMeasure("W", [Probe("w1", "p", ["A", "B"]), Probe("w2", "p", ["A", "B"])])
        reweighted = ProbeMeasure(
            "W", [Probe("w1", "p", ["A", "B"]), Probe("w2", "p", ["A", "B"])],
            weights=[3.0, 1.0],
        )
        self.assertNotEqual(base.content_hash, reweighted.content_hash)

class TestCapacityWinnersCurse(unittest.TestCase):
    """K-hat as max-of-noisy-estimates is biased UP, not a lower bound."""

    def _search(self, n_candidates, true_f=0.60, sd=0.10, seed=5):
        rng = random.Random(seed)
        selection = [true_f + rng.gauss(0, sd) for _ in range(n_candidates)]
        holdout = [true_f + rng.gauss(0, sd) for _ in range(n_candidates)]
        return selection, holdout

    def test_v01_max_is_biased_upward_and_grows_with_search_size(self):
        small, _ = self._search(3)
        large, _ = self._search(100)
        self.assertGreater(capacity_estimate(large), capacity_estimate(small))
        # It overshoots the truth it is supposed to bound from below.
        self.assertGreater(capacity_estimate(large), 0.60)

    def test_split_selection_recovers_the_truth_across_search_sizes(self):
        means = []
        for n in (3, 100):
            total = 0.0
            for trial in range(400):
                sel, hold = self._search(n, seed=1000 + trial)
                total += capacity_lower_bound(sel, hold).lower_bound
            means.append(total / 400)
        for mean in means:
            self.assertLess(abs(mean - 0.60), 0.03)
        # And unlike the max, it does not drift with search size.
        self.assertLess(abs(means[0] - means[1]), 0.03)

    def test_bound_records_how_it_was_obtained(self):
        sel, hold = self._search(10)
        bound = capacity_lower_bound(sel, hold, cost_ceiling=350)
        self.assertEqual(bound.search_size, 10)
        self.assertEqual(bound.cost_ceiling, 350)
        self.assertAlmostEqual(
            bound.winners_curse, bound.selection_score - bound.lower_bound
        )

    def test_splits_must_be_aligned(self):
        with self.assertRaises(ValueError):
            capacity_lower_bound([0.1, 0.2], [0.1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
