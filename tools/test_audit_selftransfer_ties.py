#!/usr/bin/env python3
"""Red/green checks for raw-draw modal-tie sensitivity."""

import copy
from pathlib import Path
import unittest

import audit_selftransfer as base
import audit_selftransfer_ties as ties


def arm(reference_draws, reference_mode, receiver_draws, receiver_mode):
    return {"parties": {
        "sender": {"raw": [reference_draws], "modes": [reference_mode]},
        "b0": {"raw": [receiver_draws], "modes": [receiver_mode]},
    }}


class TieSensitivityTests(unittest.TestCase):
    def synthetic(self, self_arm, cross_arm):
        return ties.analyze_raw_arms({"self": self_arm, "cross": cross_arm},
                                     row_pairs=(("self", "cross"),), briefs=("b0",))

    def test_reference_matching_alternative_changes_exact_pair_count(self):
        result = self.synthetic(arm(["Z", "Z"], "Z", ["A", "Z"], "A"),
                                arm(["Z", "Z"], "Z", ["Z", "Z"], "Z"))
        self.assertEqual(result["modal_configuration_count"], 2)
        self.assertEqual([c["row_differences"] for c in result["configurations"]],
                         [[[1]], [[0]]])
        self.assertEqual(result["ties"][0]["choice_divergences"], [1, 0])

    def test_tie_without_reference_does_not_invent_a_match(self):
        result = self.synthetic(arm(["Z", "Z"], "Z", ["A", "B"], "A"),
                                arm(["Z", "Z"], "Z", ["Z", "Z"], "Z"))
        self.assertEqual(result["modal_configuration_count"], 2)
        self.assertEqual([c["row_differences"] for c in result["configurations"]],
                         [[[1]], [[1]]])
        self.assertFalse(result["ties"][0]["reference_among_co_modes"])

    def test_tied_reference_is_rejected_instead_of_moving_the_target(self):
        with self.assertRaisesRegex(ValueError, "reference has a modal tie"):
            self.synthetic(arm(["A", "Z"], "A", ["A", "A"], "A"),
                           arm(["Z", "Z"], "Z", ["Z", "Z"], "Z"))

    def test_saved_mode_must_match_raw_draws(self):
        with self.assertRaisesRegex(ValueError, "stored mode differs"):
            self.synthetic(arm(["Z", "Z"], "Z", ["A", "A"], "Z"),
                           arm(["Z", "Z"], "Z", ["Z", "Z"], "Z"))

    def test_exact_threshold_is_not_counted_as_below(self):
        sender = {"raw": [["Z", "Z"], ["Z", "Z"]], "modes": ["Z", "Z"]}
        self_arm = {"parties": {
            "sender": sender,
            "b0": {"raw": [["A", "A"], ["Z", "Z"]], "modes": ["A", "Z"]},
            "b1": {"raw": [["A", "A"], ["A", "A"]], "modes": ["A", "A"]},
        }}
        cross_arm = {"parties": {
            "sender": sender,
            "b0": {"raw": [["Z", "Z"], ["Z", "Z"]], "modes": ["Z", "Z"]},
            "b1": {"raw": [["Z", "Z"], ["Z", "Z"]], "modes": ["Z", "Z"]},
        }}
        result = ties.analyze_raw_arms({"self": self_arm, "cross": cross_arm},
                                       row_pairs=(("self", "cross"),),
                                       briefs=("b0", "b1"))
        self.assertEqual(result["configurations"][0]["row_differences"], [[1, 2]])
        self.assertFalse(result["configurations"][0]
                         ["both_absolute_means_below_1_5"])

    def test_real_result_enumeration_and_published_rule(self):
        report = ties.build(Path(__file__).resolve().parents[1])
        self.assertEqual(report["modal_configuration_count"], 8)
        self.assertEqual(report["rows"][0]["possible_mean_fractions"], ["0", "1/3"])
        self.assertEqual(report["rows"][1]["possible_mean_fractions"],
                         ["2/3", "1", "4/3"])
        self.assertTrue(all(c["both_absolute_means_below_1_5"]
                            for c in report["configurations"]))
        self.assertIn("strictly positive sign", ties.render_markdown(report))

    def test_guard_rejects_changed_row_range(self):
        report = ties.build(Path(__file__).resolve().parents[1])
        broken = copy.deepcopy(report)
        broken["rows"][0]["minimum_mean_fraction"] = "-1/3"
        with self.assertRaisesRegex(ValueError, "reviewed row ranges"):
            ties.render_markdown(broken)


class AbsenceClaimGuardTests(unittest.TestCase):
    """Retraction 22's struck claim must stay present, struck and closed."""

    STRUCK = ("direction is not established; ~~what is established is the "
              "absence of the naive\nadvantage.~~\n")

    def test_struck_claim_wrapped_across_lines_passes(self):
        self.assertTrue(base.absence_claim_struck(self.STRUCK))

    def test_unstruck_claim_fails(self):
        self.assertFalse(base.absence_claim_struck(self.STRUCK.replace("~~", "")))

    def test_deleted_claim_fails(self):
        self.assertFalse(base.absence_claim_struck("direction is not established.\n"))

    def test_unclosed_strike_fails(self):
        self.assertFalse(base.absence_claim_struck(
            self.STRUCK.replace("advantage.~~", "advantage.")))

    def test_the_real_results_file_passes(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "probes/riverside-30/RESULTS-selftransfer.md").read_text(
            encoding="utf-8")
        self.assertTrue(base.absence_claim_struck(text))


if __name__ == "__main__":
    unittest.main()
