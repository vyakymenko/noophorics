#!/usr/bin/env python3
"""Positive and negative checks for the synthetic program-output verifier."""

from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import verify_program_output as verifier


FIXTURE = Path(__file__).parent / "fixtures" / "program_output" / "manifest.json"


class ProgramOutputVerifierTest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def assert_rejected(self, code, manifest=None):
        with self.assertRaises(verifier.Rejection) as caught:
            verifier.verify_manifest(self.manifest if manifest is None else manifest)
        self.assertEqual(caught.exception.code, code)

    def rehash_item(self, item):
        item["spec_sha256"] = verifier.canonical_sha256(
            {key: value for key, value in item.items() if key not in ("key", "spec_sha256")})

    def test_all_synthetic_classes_pass_independent_trace_check(self):
        verified = verifier.verify_manifest(self.manifest)
        self.assertEqual([entry["key"] for entry in verified], [3, 0, 1, 2])
        self.assertTrue(all(len(entry["trace_sha256"]) == 64 for entry in verified))
        self.assertFalse(self.manifest["provenance"]["holdout_eligible"])
        self.assertFalse(self.manifest["provenance"]["independent_key_adjudication"])

    def test_wrong_key_is_rejected_after_valid_execution(self):
        self.manifest["items"][0]["key"] = 2
        self.assert_rejected("KEY_MISMATCH")

    def test_corrupted_trace_transition_is_rejected(self):
        item = self.manifest["items"][0]
        trace, output = verifier.execute_program(item)
        trace[1]["after"]["b"] += 1
        with self.assertRaises(verifier.Rejection) as caught:
            verifier.check_trace(item, trace, output)
        self.assertEqual(caught.exception.code, "TRACE_TRANSITION")

    def test_corrupted_runtime_is_caught_without_trusting_its_output(self):
        original = verifier.execute_program

        def faulty(item):
            trace, output = original(item)
            trace[0]["after"]["a"] += 1
            return trace, output

        with patch.object(verifier, "execute_program", side_effect=faulty):
            self.assert_rejected("TRACE_TRANSITION")

    def test_corrupted_trace_start_and_result_are_rejected(self):
        item = self.manifest["items"][0]
        trace, output = verifier.execute_program(item)
        start_fault = deepcopy(trace)
        start_fault[0]["before"]["a"] += 1
        with self.assertRaises(verifier.Rejection) as caught:
            verifier.check_trace(item, start_fault, output)
        self.assertEqual(caught.exception.code, "TRACE_BEFORE")
        with self.assertRaises(verifier.Rejection) as caught:
            verifier.check_trace(item, trace, output + 1)
        self.assertEqual(caught.exception.code, "TRACE_OUTPUT")

    def test_bool_cannot_pose_as_equal_integer_in_trace(self):
        item = self.manifest["items"][2]
        trace, output = verifier.execute_program(item)
        self.assertEqual(trace[-1]["after"]["a"], 1)
        trace[-1]["after"]["a"] = True
        with self.assertRaises(verifier.Rejection) as caught:
            verifier.check_trace(item, trace, output)
        self.assertEqual(caught.exception.code, "TRACE_STATE")

    def test_tampered_source_or_instrument_identity_is_rejected(self):
        self.manifest["items"][0]["input"]["a"] += 1
        self.assert_rejected("SPEC_HASH_MISMATCH")
        self.manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.manifest["instrument_sha256"] = "0" * 64
        self.assert_rejected("INSTRUMENT_HASH_MISMATCH")

    def test_pinned_runtime_and_fixture_only_scope_are_enforced(self):
        self.manifest["runtime"]["version"] = "0.0.0"
        self.assert_rejected("RUNTIME_MISMATCH")
        self.manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.manifest["provenance"]["holdout_eligible"] = True
        self.assert_rejected("PROVENANCE_SCOPE")

    def test_arbitrary_source_text_and_bool_as_number_are_rejected(self):
        item = self.manifest["items"][0]
        item["program"][0]["src"] = "__import__('os').system('false')"
        self.rehash_item(item)
        self.assert_rejected("OPERAND")
        self.manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))
        item = self.manifest["items"][0]
        item["input"]["a"] = True
        self.rehash_item(item)
        self.assert_rejected("INPUT_RANGE")

    def test_zero_modulus_and_missing_final_mod_are_rejected(self):
        item = self.manifest["items"][0]
        item["program"][-1]["src"] = 0
        self.rehash_item(item)
        self.assert_rejected("MODULUS")
        self.manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))
        item = self.manifest["items"][0]
        item["program"][-1] = {"op": "add", "dst": "a", "src": 1}
        self.rehash_item(item)
        self.assert_rejected("FINAL_NORMALIZATION")

    def test_program_and_state_bounds_can_fail(self):
        item = self.manifest["items"][0]
        item["program"] = [{"op": "add", "dst": "a", "src": 1}] * 8 + [
            {"op": "mod", "dst": "a", "src": 4}]
        self.rehash_item(item)
        self.assert_rejected("PROGRAM_LENGTH")
        self.manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))
        item = self.manifest["items"][0]
        item["input"]["a"] = 9
        item["program"] = [
            {"op": "mul", "dst": "a", "src": "a"},
            {"op": "mul", "dst": "a", "src": "a"},
            {"op": "mul", "dst": "a", "src": "a"},
            {"op": "mod", "dst": "a", "src": 4},
        ]
        self.rehash_item(item)
        self.assert_rejected("STATE_LIMIT")

    def test_duplicate_ids_and_json_keys_are_rejected(self):
        duplicate = deepcopy(self.manifest["items"][0])
        self.manifest["items"].append(duplicate)
        self.assert_rejected("DUPLICATE_ITEM_ID")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"schema":"first","schema":"second"}', encoding="utf-8")
            with self.assertRaises(verifier.Rejection) as caught:
                verifier.load_manifest(path)
            self.assertEqual(caught.exception.code, "DUPLICATE_JSON_KEY")

    def test_escaped_lone_surrogate_returns_structured_rejection(self):
        self.manifest["items"][0]["input"]["a"] = "\ud800"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "surrogate.json"
            path.write_text(json.dumps(self.manifest, ensure_ascii=True), encoding="utf-8")
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(verifier.main([str(path)]), 1)
            self.assertEqual(json.loads(output.getvalue()),
                             {"status": "rejected", "code": "INPUT_RANGE",
                              "item_id": "fixture-mixed-registers"})

    def test_manifest_size_is_checked_with_a_bounded_read(self):
        class GuardedReader:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self, size=-1):
                self_size = verifier.MAX_JSON_BYTES + 1
                if size != self_size:
                    raise AssertionError(f"unbounded read: {size}")
                return b" " * self_size

        with patch.object(Path, "open", return_value=GuardedReader()):
            with self.assertRaises(verifier.Rejection) as caught:
                verifier.load_manifest(Path("unused.json"))
        self.assertEqual(caught.exception.code, "MANIFEST_SIZE")

    def test_cli_reports_structured_acceptance_and_failure(self):
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(verifier.main([str(FIXTURE), "--self-check"]), 0)
        accepted = json.loads(output.getvalue())
        self.assertEqual(accepted["status"], "accepted")
        self.assertEqual(accepted["accepted_fixture_count"], 4)
        self.assertEqual(accepted["negative_check_count"], 8)
        self.assertTrue(all(check["passed"] for check in accepted["negative_checks"]))
        self.assertEqual(len(accepted["items"]), 4)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong.json"
            wrong = deepcopy(self.manifest)
            wrong["items"][0]["key"] = 2
            path.write_text(json.dumps(wrong), encoding="utf-8")
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(verifier.main([str(path)]), 1)
            rejected = json.loads(output.getvalue())
            self.assertEqual(rejected, {"status": "rejected", "code": "KEY_MISMATCH",
                                        "item_id": "fixture-mixed-registers"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
