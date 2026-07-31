"""Tests for the noophoric metrics.

These check the properties the definitions claim, not just that the code runs:
boundedness of JSD, the meaning of the fidelity endpoints, that antinoophors
survive unclipped, and that inadmissible probe measures refuse to produce a
flattering number instead of an error.
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
import unittest
from os.path import abspath, dirname, join

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from noophorics import (  # noqa: E402
    Reference,
    fidelity_to_reference,
    independence_of,
    net_value,
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
from noophorics.inference import (  # noqa: E402
    bootstrap_ci, goodman_kruskal_gamma, holm_adjust, permutation_diff,
    point_biserial,
)
from noophorics.handoff import (  # noqa: E402
    DEFAULT_THETA, KeyLeak, adjudicate, key_marginal_baseline,
    minimum_draws, seal, verify_no_key_leak,
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
        from noophorics.decomposition import sender_split, decompose

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

    def test_decomposition_without_a_key_returns_what_it_can(self):
        """Changed behaviour, deliberately. This test used to assert a raise.

        `decompose` refused any measure without a key, so a keyless transfer --
        a preference, a house style, a judgment call whose owner defines the
        right answer, all of which the theory admits -- lost the class-prior
        baseline and the rule-content number too. Neither of those uses a key:
        the baseline is drawn from the SENDER's own pooled marginal.

        The keyed fields are None rather than NaN or 0.0, because "not
        measurable here" and "measured as zero" are different states and the
        second would assert the absence of a pathology that was never
        observable.
        """
        from noophorics.decomposition import decompose

        unkeyed = ProbeMeasure(
            id="unkeyed",
            probes=[Probe(id="p%d" % i, prompt="?", options=["A", "B"])
                    for i in range(3)],
        )
        draws = [["A"] * 4 for _ in range(3)]
        prior = [["B"] * 4 for _ in range(3)]
        d = decompose(unkeyed, draws, prior, draws)
        self.assertFalse(d.keyed)
        self.assertIsNone(d.fidelity_where_sender_right)
        self.assertIsNone(d.error_replication)
        self.assertIsNone(d.accuracy_gain)
        self.assertIsNone(d.is_mimicry_dominated)
        self.assertFalse(math.isnan(d.fidelity_class_prior_baseline))

    def test_sender_split_still_requires_a_key(self):
        """The one function that genuinely cannot work without one."""
        from noophorics.decomposition import sender_split

        unkeyed = ProbeMeasure(
            id="unkeyed",
            probes=[Probe(id="p%d" % i, prompt="?", options=["A", "B"])
                    for i in range(3)],
        )
        with self.assertRaises(ValueError):
            sender_split(unkeyed, [["A"] * 4 for _ in range(3)])

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


class TestChainTyping(unittest.TestCase):
    """L4's original form was ill-typed; the restated form must not be."""

    def test_two_antinoophors_multiply_to_a_positive_number(self):
        """The defect that withdrew L4 as written. Kept as a standing witness."""
        f1 = transfer_fidelity(d_prior=0.40, d_post=0.62, d_floor=0.05)
        f2 = transfer_fidelity(d_prior=0.30, d_post=0.55, d_floor=0.05)
        self.assertLess(f1, 0.0)
        self.assertLess(f2, 0.0)
        self.assertGreater(f1 * f2, 0.0)   # two failures compose to a success

    def _chain(self):
        from noophorics.chain import chain_fidelity
        measure = ProbeMeasure(
            "C-6", [Probe("c%d" % i, "p", ["A", "B"], key="A") for i in range(6)]
        )
        origin = [["A"] * 6 for _ in range(6)]
        prior = [["B"] * 6 for _ in range(6)]
        # Each hop keeps fewer probes aligned with the ORIGIN.
        hops = []
        for kept in (5, 3, 1):
            hops.append(
                [["A"] * 6 if i < kept else ["B"] * 6 for i in range(6)]
            )
        return chain_fidelity(measure, origin, prior, hops)

    def test_every_hop_is_scored_against_the_origin(self):
        points = self._chain()
        self.assertEqual([p.hop for p in points], [1, 2, 3])
        # Decaying alignment with the origin must show as decaying fidelity.
        self.assertGreater(points[0].fidelity, points[1].fidelity)
        self.assertGreater(points[1].fidelity, points[2].fidelity)

    def test_decay_fit_reports_monotonicity_and_half_life(self):
        from noophorics.chain import fit_decay

        decay = fit_decay(self._chain())
        self.assertTrue(decay.monotone)
        self.assertIsNotNone(decay.log_slope)
        self.assertLess(decay.log_slope, 0.0)
        self.assertGreater(decay.half_life_hops, 0.0)

    def test_dead_hops_are_excluded_not_clipped(self):
        from noophorics.chain import ChainPoint, fit_decay

        points = [
            ChainPoint(1, 0.2, 0.80, 0.9),
            ChainPoint(2, 0.4, 0.40, 0.7),
            ChainPoint(3, 0.6, 0.00, 0.5),   # signal is gone
        ]
        decay = fit_decay(points)
        self.assertEqual(decay.positive_hops, 2)


class HandoffGateTest(unittest.TestCase):
    """NHP-0001 v0.2. Each test names the v0.1 defect it pins down."""

    def _probes(self, n=10):
        probes = [{"id": "p%d" % i, "prompt": "?", "options": ["a", "b"]}
                  for i in range(n)]
        keys = {p["id"]: ("a" if i % 2 else "b") for i, p in enumerate(probes)}
        return probes, keys

    # D1 -- the exam shipped with its answer key -------------------------

    def test_sealed_payload_carries_no_key(self):
        probes, keys = self._probes()
        payload, checkset = seal(probes, keys)
        self.assertNotIn("expected", json.dumps(payload))
        self.assertEqual(set(checkset["keys"]), set(keys))
        self.assertEqual(payload["probe_measure_id"],
                         checkset["probe_measure_id"])

    def test_key_leak_detected_at_any_depth(self):
        for leaky in (
            {"probes": [{"id": "p1", "expected": "a"}]},
            {"a": {"b": {"c": [{"ground_truth": "x"}]}}},
            {"answers": {"p1": "a"}},
        ):
            with self.assertRaises(KeyLeak):
                verify_no_key_leak(leaky)

    def test_commitment_breaks_when_a_key_is_revised(self):
        """The hash is what makes the sender's own key admissible."""
        probes, keys = self._probes()
        _, before = seal(probes, keys)
        keys["p0"] = "a" if keys["p0"] == "b" else "b"
        _, after = seal(probes, keys)
        self.assertNotEqual(before["probe_measure_id"],
                            after["probe_measure_id"])

    def test_undecidable_probe_rejected(self):
        probes, keys = self._probes(3)
        keys["p0"] = "c"                       # not among the options
        with self.assertRaises(ValueError):
            seal(probes, keys)

    # D2 -- the gate passes its own worst case ---------------------------

    def test_well_calibrated_catastrophe_blocked(self):
        probes, keys = self._probes()
        _, checkset = seal(probes, keys)
        # Receiver diverges on every probe; both parties predicted it.
        answers = {pid: [("a" if k == "b" else "b")] * 6
                   for pid, k in keys.items()}
        d = adjudicate(answers, checkset, 0.0, 0.0, independent_key=True)
        self.assertEqual(d.agreement, 0.0)
        self.assertLessEqual(d.phi, DEFAULT_THETA)   # v0.1 would proceed
        self.assertTrue(d.gate_calibration)          # calibration is perfect
        self.assertFalse(d.gate_fidelity)            # and nothing transferred
        self.assertIs(d.proceed, False)
        self.assertEqual(len(d.diverged), len(keys))

    def test_overclaim_blocked_on_calibration(self):
        probes, keys = self._probes()
        _, checkset = seal(probes, keys)
        answers = {pid: [k] * 5 for pid, k in keys.items()}
        for pid in ("p0", "p1"):                     # 8/10 probes transfer
            answers[pid] = ["a" if keys[pid] == "b" else "b"] * 5
        d = adjudicate(answers, checkset, 1.0, 1.0, independent_key=True)
        self.assertAlmostEqual(d.agreement, 0.80)
        self.assertTrue(d.gate_fidelity)             # 0.80 did transfer
        self.assertFalse(d.gate_calibration)         # but they claimed 1.00
        self.assertIs(d.proceed, False)

    # D3 -- Â is not floor-corrected -------------------------------------

    def test_lopsided_key_set_has_a_high_baseline(self):
        keys = {"p%d" % i: ("a" if i < 9 else "b") for i in range(10)}
        self.assertAlmostEqual(key_marginal_baseline(keys), 0.82, places=6)

    def test_corrected_agreement_can_fall_below_zero(self):
        """0.80 raw against a 0.82 baseline is worse than not reading."""
        keys = {"p%d" % i: ("a" if i < 9 else "b") for i in range(10)}
        checkset = {"probe_measure_id": "x", "keys": keys}
        answers = {pid: (["a"] * 8 + ["b"] * 2) for pid in keys}
        d = adjudicate(answers, checkset, 0.8, 0.8, independent_key=True)
        self.assertAlmostEqual(d.baseline, 0.82, places=6)
        self.assertLess(d.agreement_corrected, 0.0)  # never clipped

    def test_constant_key_set_is_flagged_not_scored(self):
        keys = {"p%d" % i: "a" for i in range(10)}
        checkset = {"probe_measure_id": "x", "keys": keys}
        d = adjudicate({pid: ["a"] * 5 for pid in keys}, checkset, 1.0, 1.0,
                       independent_key=True)
        self.assertTrue(math.isnan(d.agreement_corrected))
        self.assertTrue(any("uninformative" in n for n in d.notes))

    # D4 -- the threshold is finer than the instrument -------------------

    def test_minimum_draws_is_bound_by_noise_not_grid(self):
        self.assertEqual(minimum_draws(0.15), 43)    # grid alone wants 7
        self.assertGreater(minimum_draws(0.10), minimum_draws(0.20))

    def test_underpowered_returns_no_verdict_rather_than_a_pass(self):
        probes, keys = self._probes(3)
        _, checkset = seal(probes, keys)
        d = adjudicate({pid: [k] for pid, k in keys.items()},
                       checkset, 1.0, 1.0, independent_key=True)
        self.assertEqual(d.agreement, 1.0)           # a perfect score
        self.assertIsNone(d.proceed)                 # and still no verdict
        self.assertTrue(any("underpowered" in n for n in d.notes))

    # standing obligations ------------------------------------------------

    def test_unanswered_probes_are_missing_data_not_zeros(self):
        probes, keys = self._probes()
        _, checkset = seal(probes, keys)
        answers = {pid: [k] * 5 for pid, k in list(keys.items())[:8]}
        d = adjudicate(answers, checkset, 1.0, 1.0, independent_key=True)
        self.assertEqual(d.agreement, 1.0)           # not 0.8
        self.assertTrue(any("unanswered" in n for n in d.notes))

    def test_self_written_key_is_disclosed(self):
        probes, keys = self._probes()
        _, checkset = seal(probes, keys)
        answers = {pid: [k] * 5 for pid, k in keys.items()}
        d = adjudicate(answers, checkset, 1.0, 1.0)  # independent_key default
        self.assertTrue(any("independently adjudicated" in n for n in d.notes))


class EfficiencyOrderingTest(unittest.TestCase):
    """eta is a ratio with a signed numerator, so it is not an ordering."""

    def test_eta_refuses_an_antinoophor(self):
        with self.assertRaises(ValueError):
            efficiency(-0.5, cost=200.0)

    def test_the_inversion_eta_would_have_produced(self):
        """Pin the defect itself, so a future 'simplification' cannot restore it."""
        short_damage = -1.0 / (100.0 / 1000.0)      # what eta would return
        long_damage = -1.0 / (800.0 / 1000.0)
        self.assertGreater(long_damage, short_damage)   # the wrong ordering
        # net_value gets it right at the same inputs
        self.assertLess(net_value(-1.0, 800.0, 0.5), net_value(-1.0, 100.0, 0.5))

    def test_net_value_is_monotone_at_both_signs(self):
        for f in (-1.0, -0.2, 0.0, 0.5, 1.0):
            self.assertLess(net_value(f, 900.0, 0.5), net_value(f, 100.0, 0.5),
                            "more cost must always be worse, at F*=%.1f" % f)
        for c in (100.0, 900.0):
            self.assertLess(net_value(-0.5, c, 0.5), net_value(0.5, c, 0.5),
                            "more fidelity must always be better")

    def test_net_value_requires_a_declared_lambda(self):
        with self.assertRaises(TypeError):
            net_value(0.5, 100.0)          # lam is positional and required

    def test_report_yields_none_rather_than_an_unprintable_antinoophor(self):
        r = Measurement(
            probe_measure_id="m@abc", samples_per_probe=30, sender="a", receiver="b",
            d_prior=0.40, d_post=0.70, d_floor=0.05, cost_tokens=300.0,
            cost_unit="tokens", agreement_observed=0.2,
        )
        self.assertLess(r.fidelity, 0.0)          # an antinoophor
        self.assertIsNone(r.efficiency)           # no eta, and no exception
        self.assertLess(r.net_value_at(0.5), 0.0)


class InferenceTest(unittest.TestCase):
    """Bias and resolution are independent. The tests say so explicitly."""

    def test_holm_is_monotone_and_bounded(self):
        adj = holm_adjust({"a": 0.01, "b": 0.04, "c": 0.5})
        self.assertLessEqual(adj["a"], adj["b"])
        self.assertLessEqual(adj["b"], adj["c"])
        self.assertLessEqual(adj["c"], 1.0)
        self.assertAlmostEqual(adj["a"], 0.03)      # 3 * 0.01

    def test_holm_never_exceeds_one(self):
        self.assertTrue(all(v <= 1.0 for v in
                            holm_adjust({"a": 0.6, "b": 0.7}).values()))

    def test_zero_bias_with_zero_resolution(self):
        """The case that invalidated PRINCIPIA falsifier 2.

        A party claiming 0.5 on every probe, right on average, that cannot tell
        a single diverged probe from a matched one.
        """
        claims = [0.5] * 10
        outcomes = [1.0] * 5 + [0.0] * 5
        bias = statistics.mean(claims) - statistics.mean(outcomes)
        self.assertAlmostEqual(bias, 0.0)             # perfectly calibrated
        self.assertEqual(point_biserial(claims, outcomes), 0.0)   # and useless
        self.assertEqual(goodman_kruskal_gamma(claims, outcomes), 0.0)

    def test_perfect_resolution_with_large_bias(self):
        """And the converse: badly biased, perfectly discriminating."""
        outcomes = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
        claims = [1.0, 1.0, 1.0, 0.4, 0.4, 0.4]       # every claim inflated
        self.assertAlmostEqual(
            statistics.mean(claims) - statistics.mean(outcomes), 0.2)
        self.assertAlmostEqual(point_biserial(claims, outcomes), 1.0)
        self.assertAlmostEqual(goodman_kruskal_gamma(claims, outcomes), 1.0)

    def test_gamma_excludes_ties_rather_than_scoring_them(self):
        self.assertEqual(goodman_kruskal_gamma([1, 1, 1], [1, 0, 1]), 0.0)

    def test_bootstrap_is_seeded_and_brackets_the_point(self):
        v = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        a = bootstrap_ci(v, seed=3)
        self.assertEqual(a, bootstrap_ci(v, seed=3))       # deterministic
        self.assertLessEqual(a[1], a[0])
        self.assertLessEqual(a[0], a[2])

    def test_bootstrap_refuses_a_single_unit(self):
        with self.assertRaises(ValueError):
            bootstrap_ci([0.5])

    def test_permutation_detects_a_real_difference(self):
        _, p = permutation_diff([1.0] * 8, [0.0] * 8, permutations=2000, seed=1)
        self.assertLess(p, 0.01)
        _, q = permutation_diff([0.5, 0.5, 0.5, 0.5], [0.5, 0.5, 0.5, 0.5],
                                permutations=2000, seed=1)
        self.assertGreater(q, 0.5)


class ReferenceTest(unittest.TestCase):
    """F*_R. The first test is the one that lets the migration ship."""

    def _measure(self):
        return ProbeMeasure(
            id="R",
            probes=[Probe(id="p%d" % i, prompt="?", options=["A", "B", "C"],
                          key=("A" if i % 2 else "B")) for i in range(6)],
        )

    def test_sender_reference_is_the_old_quantity_exactly(self):
        """F*_{R=sender} == transfer_fidelity, term for term.

        This is the regression guard for the whole v0.4 change. If it ever
        fails, a published number has silently moved.
        """
        m = self._measure()
        rng = random.Random(11)
        opts = ["A", "B", "C"]
        sender = [[rng.choice(opts) for _ in range(8)] for _ in m]
        prior = [[rng.choice(opts) for _ in range(8)] for _ in m]
        post = [[rng.choice(opts) for _ in range(8)] for _ in m]

        s_d = [to_distribution(x) for x in sender]
        p_d = [to_distribution(x) for x in prior]
        o_d = [to_distribution(x) for x in post]
        floor = 0.05
        old = transfer_fidelity(
            mean_divergence(s_d, p_d, m.weights),
            mean_divergence(s_d, o_d, m.weights), floor)

        ref = Reference.from_agent(m, sender, "s", provenance="the sender")
        new = fidelity_to_reference(ref, p_d, o_d, m.weights, d_floor=floor)
        self.assertAlmostEqual(old, new, places=12)

    def test_a_sender_reference_does_not_license_the_word(self):
        m = self._measure()
        sender = [["A"] * 4 for _ in m]
        self.assertFalse(
            Reference.from_agent(m, sender, "s", provenance="x")
            .licenses_understanding)
        self.assertTrue(Reference.from_key(m, provenance="x")
                        .licenses_understanding)

    def test_independence_separates_construction_from_discriminability(self):
        """A key is independently CONSTRUCTED even when it cannot discriminate.

        Conflating the two would reject a legitimate key merely because the
        sender happened to answer every probe correctly.
        """
        m = self._measure()
        perfect = [[p.key] * 4 for p in m]          # sender is never wrong
        r = independence_of(Reference.from_key(m, provenance="x"), perfect)
        self.assertTrue(r["independent_by_construction"])
        self.assertFalse(r["distinguishable_on_this_measure"])
        self.assertFalse(r["usable"])
        self.assertIn("perfect sender", r["verdict"])

        wrong = [[("C")] * 4 for _ in m]            # sender is always wrong
        r2 = independence_of(Reference.from_key(m, provenance="x"), wrong)
        self.assertTrue(r2["usable"])

    def test_the_ceiling_trap_is_refused(self):
        """A reference that resamples the sender is caught, not certified."""
        m = self._measure()
        sender = [["A"] * 4 for _ in m]
        ceiling = {"c1": [["A"] * 4 for _ in m], "c2": [["A"] * 4 for _ in m]}
        r = independence_of(
            Reference.from_panel(m, ceiling, provenance="same model, same context"),
            sender)
        self.assertEqual(r["identical_distributions"], len(m))
        self.assertFalse(r["usable"])

    def test_a_panel_needs_more_than_one_adjudicator(self):
        m = self._measure()
        with self.assertRaises(ValueError):
            Reference.from_panel(m, {"only": [["A"] * 4 for _ in m]},
                                 provenance="x")

    def test_a_contested_key_may_be_a_distribution(self):
        """M33 has a key the source does not determine; a point mass lies."""
        m = self._measure()
        ref = Reference.from_key(
            m, provenance="x", contested={"p0": {"A": 0.5, "B": 0.5}})
        self.assertEqual(ref.distributions[0], {"A": 0.5, "B": 0.5})
        self.assertEqual(sum(ref.distributions[1].values()), 1.0)

    def test_contested_mass_on_a_non_option_is_refused(self):
        m = self._measure()
        with self.assertRaises(ValueError):
            Reference.from_key(m, provenance="x",
                               contested={"p0": {"Z": 1.0}})


class ReportingStandardTest(unittest.TestCase):
    """definitions 7 requires four v0.4 fields. The type must be able to hold them."""

    def _m(self, **kw):
        base = dict(probe_measure_id="P@abc", samples_per_probe=30,
                    sender="a", receiver="b", d_prior=0.40, d_post=0.10,
                    d_floor=0.02, cost_tokens=300.0, cost_unit="tokens",
                    agreement_observed=0.8)
        base.update(kw)
        return Measurement(**base)

    def test_an_undeclared_reference_is_not_reportable(self):
        missing = self._m().is_reportable()
        self.assertTrue(any("reference_kind" in x for x in missing))
        self.assertTrue(any("regime" in x for x in missing))

    def test_an_undeclared_reference_does_not_measure_understanding(self):
        """Undeclared WAS the sender for three versions; treat it as such."""
        self.assertFalse(self._m().measures_understanding)
        self.assertFalse(self._m(reference_kind="sender").measures_understanding)
        self.assertTrue(self._m(reference_kind="key").measures_understanding)

    def test_a_declared_key_reference_is_reportable(self):
        m = self._m(reference_kind="key", reference_provenance="set by X, adjudicated",
                    regime="criterion-bearing",
                    reference_independence={"usable": True})
        self.assertEqual(m.is_reportable(), [])

    def test_a_non_sender_reference_must_carry_its_independence_check(self):
        """The CEILING trap: a reference that resamples the sender."""
        m = self._m(reference_kind="panel", reference_provenance="three judges",
                    regime="criterion-bearing")
        self.assertTrue(any("independence" in x for x in m.is_reportable()))

    def test_a_sender_reference_needs_no_independence_check(self):
        """It is not independent by construction; asking would be theatre."""
        m = self._m(reference_kind="sender", reference_provenance="the sender",
                    regime="criterion-free")
        self.assertEqual(m.is_reportable(), [])
        self.assertFalse(m.measures_understanding)

    def test_historical_measurements_stay_constructible(self):
        """Pre-v0.4 records are real numbers; they are simply not reportable."""
        m = self._m()
        self.assertAlmostEqual(m.fidelity,
                               transfer_fidelity(0.40, 0.10, 0.02))
        self.assertNotEqual(m.is_reportable(), [])


class TestTransportRetry(unittest.TestCase):
    """What may be retried, and what must never be.

    E-004 lost 22 of its 126 cells to one `socket.timeout` three and a half
    hours into collection. The retry added afterwards is only defensible if it
    is confined to failures that produced no answer -- a retry on a real
    observation would manufacture persistence the model never showed. These
    tests are the boundary, stated as behaviour rather than as intention.
    """

    def _serve(self, script):
        """A local ollama stand-in that plays `script`, one entry per request."""
        import json as _json
        import threading
        import time as _time
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

        state = {"script": list(script), "seen": []}
        lock = threading.Lock()

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def log_message(self, *a):
                pass

            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", 0)))
                with lock:
                    mode = state["script"].pop(0) if state["script"] else "ok"
                    state["seen"].append(mode)
                if mode == "hang":
                    _time.sleep(1.5)
                    return
                if mode in ("500", "400"):
                    self.send_error(int(mode))
                    return
                content = "" if mode == "empty" else "GREEN"
                body = _json.dumps({"message": {"content": content}}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        return "http://127.0.0.1:%d" % srv.server_address[1], state

    def _call(self, script):
        import io as _io
        from contextlib import redirect_stderr

        from noophorics import ollama_agent as oa

        url, state = self._serve(script)
        old = oa.CHAT_BACKOFF_S
        oa.CHAT_BACKOFF_S = 0.01
        self.addCleanup(lambda: setattr(oa, "CHAT_BACKOFF_S", old))
        agent = oa.OllamaAgent(name="t", endpoint=url, timeout_s=0.5)
        log = _io.StringIO()
        try:
            with redirect_stderr(log):
                out = agent._chat("hi")["_content"]
            return out, len(state["seen"]), log.getvalue(), None
        except Exception as exc:                       # noqa: BLE001
            return None, len(state["seen"]), log.getvalue(), exc

    def test_timeout_is_retried(self):
        out, calls, _, exc = self._call(["hang", "ok"])
        self.assertIsNone(exc)
        self.assertEqual(out, "GREEN")
        self.assertEqual(calls, 2)

    def test_server_error_is_retried(self):
        out, calls, _, exc = self._call(["500", "ok"])
        self.assertIsNone(exc)
        self.assertEqual(calls, 2)

    def test_retries_are_bounded_and_then_give_up(self):
        out, calls, _, exc = self._call(["hang", "hang", "hang"])
        self.assertIsNotNone(exc)
        self.assertEqual(calls, 3)
        # The message must say no draw was obtained -- a caller that reads this
        # as "the model failed" would record an observation that never happened.
        self.assertIn("nothing about the model was observed", str(exc))

    def test_client_error_is_not_retried(self):
        """4xx means the request is wrong and will stay wrong."""
        out, calls, _, exc = self._call(["400", "ok"])
        self.assertIsNotNone(exc)
        self.assertEqual(calls, 1)

    def test_empty_completion_is_not_retried(self):
        """An empty answer is a real observation, not a transport failure."""
        out, calls, _, exc = self._call(["empty", "ok"])
        self.assertIsNotNone(exc)
        self.assertEqual(calls, 1)
        self.assertIn("empty response", str(exc))

    def test_every_retry_is_logged(self):
        """A silent retry hides a probe that systematically needs three."""
        _, _, log, _ = self._call(["hang", "500", "ok"])
        self.assertEqual(log.count("[ollama_agent]"), 2)
        self.assertIn("attempt 1/3", log)
        self.assertIn("attempt 2/3", log)


if __name__ == "__main__":
    unittest.main(verbosity=2)
