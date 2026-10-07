#!/usr/bin/env python3
"""Red/green checks for the Problem 13 estimand tracer.

Each rule is shown failing on the shape of defect it exists to see -- with the
exact verdict code, so a catch-all cannot stand in for the detector -- and
passing on the legitimate case that most resembles it. The last class runs the
three historical incidents from git: red on the revision that carried each,
green on the commit that fixed it, and nothing written into the repository.
"""

import os
import subprocess
import tempfile
import types
import unittest

import audit_estimand as ae

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def call(fn, arrays, out):
    return ae.Call(fn, [list(map(float, a)) for a in arrays], tuple(out))


def verdicts(report, rule):
    return [v for r, v, _ in report["findings"] if r == rule]


def tree_status(root):
    """Everything git sees, ignored files included: a dry-run results file is
    ignored by .gitignore, so a status without --ignored cannot see one."""
    return subprocess.run(["git", "status", "--porcelain", "--ignored"],
                          cwd=root, capture_output=True, text=True).stdout


class RelationTests(unittest.TestCase):
    """Provenance by identity, then the relations, on hand-built calls."""

    def setUp(self):
        # Distinct float objects for every returned number, as a real call makes.
        self.lo, self.hi, self.p = float("0.10"), float("0.30"), float("0.002")

    def test_paired_interval_beside_unpaired_test_is_the_pairing_defect(self):
        a, b = [0.5, 0.7, 0.6, 0.9], [0.4, 0.3, 0.5, 0.6]
        diffs = [x - y for x, y in zip(a, b)]
        obs = sum(a) / 4 - sum(b) / 4
        calls = [call("bootstrap_ci", [diffs], (obs, self.lo, self.hi)),
                 call("permutation_diff", [a, b], (obs, self.p))]
        effect = {"value": calls[1].out[0], "ci95": [self.lo, self.hi],
                  "p_value": self.p}
        rep = ae.relate(effect, calls)
        self.assertEqual(verdicts(rep, "R2"), [ae.PAIRING])
        # A mean of differences equals a difference of means, so R1 cannot see
        # this one -- which is why R2 exists.
        self.assertEqual(verdicts(rep, "R1"), ["ok"])

    def test_an_unrelated_two_sample_test_is_not_reported_as_the_pairing_defect(self):
        xs, a, b = [0.1, 0.2, 0.3], [0.9, 0.8], [0.1, 0.4, 0.2]
        obs = sum(a) / 2 - sum(b) / 3
        calls = [call("bootstrap_ci", [xs], (obs, self.lo, self.hi)),
                 call("permutation_diff", [a, b], (obs, self.p))]
        effect = {"value": obs, "ci95": [self.lo, self.hi], "p_value": self.p}
        self.assertEqual(verdicts(ae.relate(effect, calls), "R2"), [ae.UNRECOGNISED])

    def test_paired_interval_beside_paired_test_on_the_same_array_passes(self):
        diffs = [0.1, 0.4, 0.1, 0.3]
        obs = sum(diffs) / 4
        calls = [call("bootstrap_ci", [diffs], (obs, self.lo, self.hi)),
                 call("paired_permutation", [diffs], (obs, self.p))]
        effect = {"value": obs, "ci95": [self.lo, self.hi], "p_value": self.p}
        rep = ae.relate(effect, calls)
        self.assertEqual(verdicts(rep, "R2"), ["ok"])
        self.assertEqual(verdicts(rep, "R1"), ["ok"])
        self.assertEqual(verdicts(rep, "R1b"), ["ok"])

    def test_a_test_of_a_different_quantity_fails_r1(self):
        """E-002c H3: a slope difference reported, a level difference tested."""
        levels = [0.05, -0.02, 0.04, 0.01]
        calls = [call("paired_permutation", [levels], (sum(levels) / 4, self.p))]
        effect = {"value": 0.2997, "ci95": [self.lo, self.hi], "p_value": self.p}
        rep = ae.relate(effect, calls)
        self.assertEqual(verdicts(rep, "R1"), ["FAIL:different-quantity"])
        self.assertEqual(verdicts(rep, "R3"), ["note"])     # the interval is inline

    def test_mean_of_contributions_whose_sum_is_the_value_passes_r1(self):
        """E-002c H3 as fixed: the sign-flip sees the mean, the record the sum."""
        contrib = [0.1, 0.05, 0.12, 0.03]
        calls = [call("paired_permutation", [contrib], (sum(contrib) / 4, self.p))]
        effect = {"value": sum(contrib), "p_value": self.p}
        self.assertEqual(verdicts(ae.relate(effect, calls), "R1"), ["ok"])

    def test_an_interval_of_another_quantity_fails_r1b(self):
        """A median interval beside a mean value and a mean test."""
        diffs = [0.1, 0.4, 0.1, 0.3]
        mean = sum(diffs) / 4
        calls = [call("bootstrap_ci", [diffs], (0.2, self.lo, self.hi)),   # median
                 call("paired_permutation", [diffs], (mean, self.p))]
        effect = {"value": mean, "ci95": [self.lo, self.hi], "p_value": self.p}
        rep = ae.relate(effect, calls)
        self.assertEqual(verdicts(rep, "R1b"), ["FAIL:interval-of-another-quantity"])
        self.assertEqual(verdicts(rep, "R1"), ["ok"])

    def test_one_sample_question_against_zeros_is_its_own_class(self):
        xs = [0.2, 0.1, 0.3, 0.25]
        obs = sum(xs) / 4
        calls = [call("bootstrap_ci", [xs], (obs, self.lo, self.hi)),
                 call("permutation_diff", [xs, [0.0] * 4], (obs, self.p))]
        effect = {"value": calls[0].out[0], "ci95": [self.lo, self.hi],
                  "p_value": self.p}
        self.assertEqual(verdicts(ae.relate(effect, calls), "R2"),
                         ["one-sample-as-two-sample"])

    def test_an_equal_value_from_another_call_does_not_bind(self):
        """Provenance is the returned object, not a number that happens to match."""
        calls = [call("permutation_diff", [[0.2, 0.1], [0.0, 0.0]], (0.15, float("0.5")))]
        effect = {"value": 0.15, "p_value": float("0.5")}
        rep = ae.relate(effect, calls)
        self.assertEqual(rep["p_source"], "untraced")
        self.assertEqual(verdicts(rep, "R1"), [])


class TracerTests(unittest.TestCase):
    """The wrapper must be transparent to every legitimate call form."""

    def module(self):
        from noophorics import inference
        mod = types.ModuleType("fake_runner")
        for name in ("bootstrap_ci", "permutation_diff", "paired_permutation"):
            setattr(mod, name, getattr(inference, name))
        return mod

    def test_keyword_arrays_are_read(self):
        mod = self.module()
        calls = ae.install_tracer(mod)
        mod.paired_permutation(differences=[0.1, 0.2, -0.1], permutations=50, seed=1)
        self.assertEqual(calls[0].arrays, [[0.1, 0.2, -0.1]])

    def test_a_generator_is_recorded_as_consumed_not_as_empty(self):
        mod = self.module()
        calls = ae.install_tracer(mod)
        _, lo, hi = mod.bootstrap_ci((x for x in [0.1, 0.2, 0.3]), resamples=50, seed=1)
        self.assertEqual(calls[0].arrays, [[0.1, 0.2, 0.3]])
        self.assertLessEqual(lo, hi)


class SummaryTests(unittest.TestCase):
    """R4's reading of a terminal table and its verdict on one draw."""

    def test_only_an_exact_supported_token_is_a_mark(self):
        self.assertTrue(ae._marked("  H1_x  +0.1  interval  [0, 1]  SUPPORTED"))
        self.assertFalse(ae._marked("  H1_x  +0.1  interval  [0, 1]  UNSUPPORTED"))
        self.assertFalse(ae._marked("  H1_x  +0.1  interval  [0, 1]  NOT SUPPORTED"))
        self.assertFalse(ae._marked("  H1_x  +0.1  interval  [0, 1]"))

    def test_a_supported_hypothesis_left_unmarked_fails(self):
        v, _ = ae._r4("H1", {"supported": True},
                      {"marks": {"H1": False}, "error": None})
        self.assertEqual(v, "FAIL:mark-disagrees")

    def test_a_supported_hypothesis_the_summary_omits_fails(self):
        v, _ = ae._r4("H1", {"supported": True},
                      {"marks": {"H2": True}, "error": None})
        self.assertEqual(v, "FAIL:omitted")

    def test_a_summary_that_raises_is_not_a_pass(self):
        v, _ = ae._r4("H1", {"supported": True},
                      {"marks": None, "error": "TypeError: boom"})
        self.assertEqual(v, "FAIL:summary-raised")

    def test_a_missing_verdict_is_reported_as_missing_not_as_false(self):
        v, _ = ae._r4("H3", {"value": 0.3}, {"marks": {"H3": False}, "error": None})
        self.assertEqual(v, "no-verdict")

    def test_agreement_passes(self):
        v, _ = ae._r4("H1", {"supported": False},
                      {"marks": {"H1": False}, "error": None})
        self.assertEqual(v, "ok")


class IncidentTests(unittest.TestCase):
    """The three incidents of Problem 13, from the revisions that carried them."""

    @classmethod
    def setUpClass(cls):
        cls.before = tree_status(ROOT)          # taken before any main() runs
        cls.rows = ae.run_fixtures()
        cls.after = tree_status(ROOT)

    def test_every_incident_is_red_before_and_green_after(self):
        for row in self.rows:
            with self.subTest(incident=row["incident"]):
                self.assertEqual(row["defect_status"], row["expected_fail"], row)
                self.assertTrue(row["red_on_defect"], row)
                self.assertEqual(row["fixed_status"], "ok", row)
                self.assertTrue(row["green_on_fix"], row)

    def test_the_audit_writes_nothing_into_the_repository(self):
        """main() runs for R4; its results file must land in the temp --out.

        Checked both ways: each summary reported writing inside its temporary
        directory, and the whole tree, ignored files included, is unchanged.
        """
        for row in self.rows:
            self.assertTrue(row["wrote_only_to_temp"], row)
        self.assertEqual(self.before, self.after)

    def test_the_tree_check_can_see_an_ignored_dry_run_file(self):
        """The red case for the check above, in a throwaway repository."""
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
            with open(os.path.join(tmp, ".gitignore"), "w") as fh:
                fh.write("*-dryrun.json\n")
            before = tree_status(tmp)
            with open(os.path.join(tmp, "E-0-20261007T000000Z-dryrun.json"), "w") as fh:
                fh.write("{}")
            self.assertNotEqual(before, tree_status(tmp))


if __name__ == "__main__":
    unittest.main()
