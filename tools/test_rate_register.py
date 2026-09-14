#!/usr/bin/env python3
"""Offline defect/legitimate-case tests for the prospective register instrument."""
from __future__ import annotations

import base64
import copy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import rate_register as rr


def raw_response(data, status=200):
    raw = json.dumps(data, ensure_ascii=False).encode()
    return {"status": status, "headers": [["Content-Type", "application/json"]],
            "body_base64": base64.b64encode(raw).decode(), "body": raw.decode(), "error": None}


def answer(letter, model):
    return raw_response({"model": model, "done": True, "done_reason": "stop", "message": {
        "role": "assistant", "content": json.dumps({"verdict": letter})}})


class FakeTransport:
    def __init__(self, protocol, overrides=None, interrupt_at=None, digests=None):
        self.protocol = protocol
        self.overrides = overrides or {}
        self.interrupt_at = interrupt_at
        self.calls = []
        self.requests = []
        self.digests = digests or protocol["identity"]["model_digests"]
        self.lookup = {rr.encoded(rr.payload(protocol, call)): call for call in protocol["schedule"]}

    def __call__(self, method, path, body, timeout):
        self.requests.append((method, path, body, timeout))
        if method == "GET":
            return raw_response({"models": [{"name": name, "digest": digest}
                                            for name, digest in self.digests.items()]})
        call = self.lookup[body]
        self.calls.append(call["sequence"])
        if call["sequence"] == self.interrupt_at:
            raise KeyboardInterrupt("simulated process interruption after reservation")
        result = self.overrides.get(call["sequence"], call["item"]["expected"])
        if isinstance(result, Exception):
            raise result
        return answer(result, call["rater"]["model"]) if isinstance(result, str) else result


class RegisterTest(unittest.TestCase):
    def setUp(self):
        self.directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.directory)
        self.plan_path = self.directory / "plan.json"
        self.plan_path.write_bytes((rr.ROOT / "probes/qwen-register/plan.json").read_bytes())
        self.protocol = rr.load_protocol(self.plan_path)
        self.out = self.directory / "results"

    def changed_plan(self, callback):
        plan = rr.read_json(self.plan_path)
        callback(plan)
        self.plan_path.write_text(json.dumps(plan), encoding="utf-8")
        return rr.load_protocol(self.plan_path)

    def source_call(self, rater_index=0, cell="A", in_band=None):
        return next(c for c in self.protocol["schedule"] if
                    c["rater"] == self.protocol["plan"]["raters"][rater_index]
                    and c["item"]["kind"] == "source" and c["item"]["cell"] == cell
                    and (in_band is None or c["item"]["in_band"] == in_band))

    def test_offline_dry_run_has_no_network_and_does_not_create_output(self):
        output = io.StringIO()
        with patch.object(rr, "HTTPTransport", side_effect=AssertionError("network")), redirect_stdout(output):
            self.assertEqual(rr.main(["--plan", str(self.plan_path), "--out", str(self.out), "--dry-run"]), 0)
        self.assertFalse(self.out.exists())
        self.assertEqual(json.loads(output.getvalue())["max_calls"], 104)

    def test_source_includes_every_row_and_recomputes_band(self):
        self.assertEqual(len(self.protocol["rows"]), 48)
        self.assertEqual({cell: sum(r["in_band"] for r in self.protocol["rows"] if r["cell"] == cell)
                          for cell in "ABCD"}, {"A": 11, "B": 12, "C": 12, "D": 11})
        for row in self.protocol["rows"]:
            self.assertEqual(row["words"], len(row["text"].split()))

    def test_source_mismatch_rejected_before_transport(self):
        root = self.directory / "root"
        path = root / rr.SOURCE
        path.parent.mkdir(parents=True)
        path.write_bytes((rr.ROOT / rr.SOURCE).read_bytes() + b" ")
        with self.assertRaisesRegex(rr.CheckError, "source file checksum"):
            rr.load_protocol(self.plan_path, root)

    def test_false_word_count_or_band_flag_rejected_even_with_matching_file_hash(self):
        for field, value in [("words", 999), ("in_band", False)]:
            with self.subTest(field=field):
                root = self.directory / field
                source = rr.read_json(rr.ROOT / rr.SOURCE)
                source["cells"]["A"][0][field] = value
                source_path = root / rr.SOURCE
                source_path.parent.mkdir(parents=True)
                source_path.write_text(json.dumps(source), encoding="utf-8")
                prompt_path = root / rr.PROMPT_SOURCE
                prompt_path.write_bytes((rr.ROOT / rr.PROMPT_SOURCE).read_bytes())
                plan = copy.deepcopy(self.protocol["plan"])
                plan["source"]["sha256"] = rr.sha(source_path.read_bytes())
                altered_plan = root / "plan.json"
                altered_plan.write_text(json.dumps(plan), encoding="utf-8")
                with patch.object(rr, "SOURCE_SHA", plan["source"]["sha256"]), self.assertRaisesRegex(rr.CheckError, "stored.*mismatch"):
                    rr.load_protocol(altered_plan, root)

    def test_composer_rater_and_duplicate_digest_rejected(self):
        for key, value in [("model", "qwen3.5:35b"),
                           ("digest", self.protocol["plan"]["raters"][1]["digest"])]:
            with self.subTest(key=key), self.assertRaises(rr.CheckError):
                self.changed_plan(lambda p: p["raters"][0].update({key: value}))
            self.plan_path.write_text(json.dumps(self.protocol["plan"]), encoding="utf-8")

    def test_question_loaded_without_execution_and_has_exact_checksum(self):
        path = self.directory / "literal.py"
        path.write_text("raise AssertionError('module executed')\nABSOLUTE = " + repr(self.protocol["question"]))
        self.assertEqual(rr.absolute_question(path), self.protocol["question"])
        path.write_text("ABSOLUTE = 'different'")
        with self.assertRaisesRegex(rr.CheckError, "checksum"):
            rr.absolute_question(path)

    def test_exact_single_passage_payload_no_labels_and_llama_think_omitted(self):
        for call in self.protocol["schedule"]:
            body = rr.payload(self.protocol, call)
            self.assertEqual(body["messages"], [{"role": "user", "content":
                              self.protocol["question"] % call["item"]["text"]}])
            self.assertNotIn("system", body)
            self.assertNotIn("context", body)
            self.assertNotIn("item_id", body)
            self.assertNotIn("cell", body)
            self.assertEqual(body["format"], rr.VERDICT_FORMAT)
            self.assertEqual(body["options"], {"seed": call["seed"], "temperature": 0.7})
            if call["rater"]["model"].startswith("llama"):
                self.assertNotIn("think", body)
            else:
                self.assertEqual(body["think"], "medium")

    def test_shuffle_and_per_item_seeds_repeat_exactly(self):
        again = rr.load_protocol(self.plan_path)
        self.assertEqual(self.protocol["schedule"], again["schedule"])
        source_ids = [c["item"]["id"] for c in self.protocol["schedule"][:52] if c["item"]["kind"] == "source"]
        self.assertEqual(len(set(source_ids)), 48)
        self.assertNotEqual(source_ids, sorted(source_ids))
        self.assertEqual(len({c["seed"] for c in self.protocol["schedule"]}), 104)

    def test_complete_success_retains_requests_responses_and_checks_offline(self):
        transport = FakeTransport(self.protocol)
        summary = rr.run(self.protocol, self.out, transport=transport)
        self.assertTrue(summary["usable"])
        self.assertEqual(len(transport.calls), 104)
        self.assertTrue(all(request[3] == 120 for request in transport.requests))
        self.assertEqual([summary["cells"][c]["joint_acceptance"] for c in "ABCD"], [11, 12, 12, 11])
        records = rr.checked_results(self.protocol, self.out)
        self.assertEqual(summary, rr.summarize(self.protocol, records))
        for record in records.values():
            self.assertEqual(record["response"]["body"],
                             base64.b64decode(record["response"]["body_base64"]).decode())

    def test_joint_acceptance_is_intersection_not_minimum_of_marginals(self):
        # All register ratings pass except one in-band A row for one rater.
        # Band marginal=11 and both-register marginal=11; true intersection=10.
        call = self.source_call(cell="A", in_band=True)
        summary = rr.run(self.protocol, self.out,
                         transport=FakeTransport(self.protocol, {call["sequence"]: "B"}))
        cell = summary["cells"]["A"]
        self.assertEqual((cell["in_band"], cell["both_expected_register"], cell["joint_acceptance"]), (11, 11, 10))
        self.assertEqual(cell["disagreement"], 1)

    def test_all_controls_attempted_after_failure_other_rater_still_runs(self):
        transport = FakeTransport(self.protocol, {0: "B", 1: TimeoutError("lost reply")})
        summary = rr.run(self.protocol, self.out, transport=transport)
        self.assertEqual(transport.calls, [0, 1, 2, 3] + list(range(52, 104)))
        self.assertEqual(summary["calibration"]["gpt-oss:120b"]["status"], "failed")
        self.assertEqual(summary["calibration"]["llama3.3:70b"]["status"], "passed")
        self.assertTrue(summary["complete"])
        self.assertFalse(summary["usable"])
        self.assertEqual(summary["cells"]["C"]["missing_any_rating"], 12)
        self.assertIsNone(summary["cells"]["C"]["joint_acceptance"])
        self.assertFalse(summary["cells"]["C"]["joint_result_available"])
        self.assertEqual(summary["invalid_or_indeterminate_attempts"], 1)

    def test_transport_invalid_http_and_incomplete_output_never_become_B(self):
        call = self.source_call(cell="C")
        wrong = [TimeoutError("timeout"), raw_response({"error": "server"}, 500),
                 raw_response([]), raw_response(None),
                 raw_response({"model": call["rater"]["model"], "done": True, "message": None}),
                 raw_response({"model": call["rater"]["model"], "done": True, "message": []}),
                 raw_response({"model": call["rater"]["model"], "done": True, "message": {"role": "assistant", "content": "B"}}),
                 raw_response({"model": call["rater"]["model"], "done": False, "message": {"role": "assistant", "content": '{"verdict":"B"}'}}),
                 raw_response({"model": call["rater"]["model"], "done": True, "message": {"role": "assistant", "content": '{"verdict":"B","extra":1}'}})]
        for index, bad in enumerate(wrong):
            with self.subTest(index=index):
                destination = self.directory / f"bad-{index}"
                transport = FakeTransport(self.protocol, {call["sequence"]: bad})
                summary = rr.run(self.protocol, destination, transport=transport)
                self.assertFalse(summary["usable"])
                self.assertEqual(summary["cells"]["C"]["missing_any_rating"], 1)
                self.assertEqual(summary["cells"]["C"]["both_expected_register"], 11)
                self.assertIsNone(summary["cells"]["C"]["joint_acceptance"])
                self.assertEqual(summary["cells"]["C"]["observed_joint_acceptance"], 11)
                self.assertEqual(transport.calls.count(call["sequence"]), 1)
                self.assertEqual(len(transport.calls), 104)

    def test_existing_output_cannot_be_overwritten_and_completed_resume_makes_no_calls(self):
        rr.run(self.protocol, self.out, transport=FakeTransport(self.protocol))
        with self.assertRaisesRegex(rr.CheckError, "existing output needs"):
            rr.run(self.protocol, self.out, transport=FakeTransport(self.protocol))
        transport = FakeTransport(self.protocol)
        result = rr.run(self.protocol, self.out, resume=True, transport=transport)
        self.assertTrue(result["usable"])
        self.assertEqual(transport.calls, [])

    def test_interrupted_reserved_call_is_retained_and_never_retried(self):
        first = FakeTransport(self.protocol, interrupt_at=5)
        with self.assertRaises(KeyboardInterrupt):
            rr.run(self.protocol, self.out, transport=first)
        reservation = rr.read_json(rr.record_path(self.out, 5))
        self.assertEqual(reservation["state"], "reserved")
        second = FakeTransport(self.protocol)
        summary = rr.run(self.protocol, self.out, resume=True, transport=second)
        self.assertNotIn(5, second.calls)
        self.assertEqual(len(first.calls) + len(second.calls), 104)
        self.assertEqual(summary["invalid_or_indeterminate_attempts"], 1)
        self.assertFalse(summary["usable"])
        self.assertEqual(rr.read_json(rr.record_path(self.out, 5)), reservation)

    def test_resume_rejects_plan_script_model_or_payload_conflict(self):
        rr.run(self.protocol, self.out, transport=FakeTransport(self.protocol))
        modified = copy.deepcopy(self.protocol)
        modified["identity"]["script_sha256"] = "0" * 64
        with self.assertRaisesRegex(rr.CheckError, "identity conflict"):
            rr.run(modified, self.out, resume=True, transport=FakeTransport(modified))
        changed = self.changed_plan(lambda p: p.update(seed=p["seed"] + 1))
        with self.assertRaisesRegex(rr.CheckError, "identity conflict"):
            rr.run(changed, self.out, resume=True, transport=FakeTransport(changed))
        altered = dict(self.protocol["identity"]["model_digests"])
        altered["gpt-oss:120b"] = "0" * 64
        with self.assertRaisesRegex(rr.CheckError, "model digest mismatch"):
            rr.run(self.protocol, self.out, resume=True,
                   transport=FakeTransport(self.protocol, digests=altered))
        path = rr.record_path(self.out, 0)
        record = rr.read_json(path)
        record["request"]["body"] = "{}"
        rr.atomic_json(path, record)
        with self.assertRaisesRegex(rr.CheckError, "blinded payload"):
            rr.checked_results(self.protocol, self.out)

    def test_resume_refuses_a_hole_in_reserved_call_sequence(self):
        rr.run(self.protocol, self.out, transport=FakeTransport(self.protocol))
        rr.record_path(self.out, 5).unlink()
        with self.assertRaisesRegex(rr.CheckError, "checkpoint has a gap"):
            rr.run(self.protocol, self.out, resume=True, transport=FakeTransport(self.protocol))

    def test_interrupted_control_is_not_retried_and_other_controls_still_run(self):
        first = FakeTransport(self.protocol, interrupt_at=0)
        with self.assertRaises(KeyboardInterrupt):
            rr.run(self.protocol, self.out, transport=first)
        second = FakeTransport(self.protocol)
        summary = rr.run(self.protocol, self.out, resume=True, transport=second)
        self.assertEqual(second.calls, [1, 2, 3] + list(range(52, 104)))
        self.assertEqual(summary["calibration"]["gpt-oss:120b"]["status"], "failed")
        self.assertFalse(summary["usable"])

    def test_offline_summary_recomputes_instead_of_trusting_cached_counts(self):
        rr.run(self.protocol, self.out, transport=FakeTransport(self.protocol))
        (self.out / "summary.json").write_text('{"made_up": 999}')
        output = io.StringIO()
        with patch.object(rr, "HTTPTransport", side_effect=AssertionError("network")), redirect_stdout(output):
            self.assertEqual(rr.main(["--plan", str(self.plan_path), "--out", str(self.out), "--summarize"]), 0)
        self.assertEqual(json.loads(output.getvalue())["cells"]["A"]["joint_acceptance"], 11)

    def test_item_hash_mismatch_is_rejected_offline(self):
        rr.run(self.protocol, self.out, transport=FakeTransport(self.protocol))
        path = self.out / "manifest.json"
        manifest = rr.read_json(path)
        self.assertEqual(len(manifest["items"]), 52)
        self.assertTrue(all("text" not in item and len(item["text_sha256"]) == 64
                            for item in manifest["items"]))
        manifest["items"][0]["text_sha256"] = "0" * 64
        rr.atomic_json(path, manifest)
        with self.assertRaisesRegex(rr.CheckError, "item identities or text hashes"):
            rr.checked_results(self.protocol, self.out)

    def test_unpublished_atomic_temp_does_not_block_resume_or_replace_evidence(self):
        first = FakeTransport(self.protocol, interrupt_at=5)
        with self.assertRaises(KeyboardInterrupt):
            rr.run(self.protocol, self.out, transport=first)
        leftover = self.out / "calls" / ".checkpoint-interrupted"
        leftover.write_text('{"partial":')
        transport = FakeTransport(self.protocol)
        result = rr.run(self.protocol, self.out, resume=True, transport=transport)
        self.assertNotIn(5, transport.calls)
        self.assertEqual(result["invalid_or_indeterminate_attempts"], 1)
        self.assertTrue(leftover.exists())
        self.assertEqual(len(rr.checked_results(self.protocol, self.out)), 104)

    def test_correct_verdict_from_wrong_model_is_missing(self):
        call = self.source_call(cell="C")
        transport = FakeTransport(self.protocol, {call["sequence"]: answer("B", "other-model")})
        summary = rr.run(self.protocol, self.out, transport=transport)
        self.assertEqual(summary["invalid_or_indeterminate_attempts"], 1)
        self.assertEqual(summary["cells"]["C"]["missing_any_rating"], 1)
        self.assertIsNone(summary["cells"]["C"]["joint_acceptance"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
