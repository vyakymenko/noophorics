#!/usr/bin/env python3
"""Offline checks that the Markdown readout preserves counts and missingness."""
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import rate_register as rr
import report_register as report
from test_rate_register import FakeTransport


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.out = self.directory / "results"
        self.report = self.directory / "readout.md"
        self.protocol = rr.load_protocol(report.PLAN)

    def test_counts_ignore_cached_summary_and_check_detects_stale_report(self):
        rr.run(self.protocol, self.out, transport=FakeTransport(self.protocol))
        with patch.object(rr, "HTTPTransport", side_effect=AssertionError("network")):
            content = report.render(self.out, self.report)
            self.assertIn("| A | connected prose | 12 | 11 | 12 | 12 | 12 | 0 | 11 |", content)
            self.assertIn("**104 / 104**", content)
            self.assertIn("Direct joint acceptance across the archived corpus: **46 / 48**", content)
            self.assertNotIn("lower bound", content)
            self.assertTrue(all(row["text"] not in content for row in self.protocol["rows"]))
            (self.out / "summary.json").write_text('{"made_up": 999}')
            self.assertEqual(content, report.render(self.out, self.report))
            arguments = ["--out", str(self.out), "--report", str(self.report), "--check"]
            self.report.write_text(content, encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(report.main(arguments), 0)
            self.report.write_text(content.replace("**104 / 104**", "**103 / 104**"), encoding="utf-8")
            with redirect_stderr(io.StringIO()):
                self.assertEqual(report.main(arguments), 1)

    def test_missing_rating_is_unavailable_with_only_labelled_lower_bound(self):
        call = next(c for c in self.protocol["schedule"]
                    if c["item"]["kind"] == "source" and c["item"]["cell"] == "C")
        rr.run(self.protocol, self.out, transport=FakeTransport(
            self.protocol, {call["sequence"]: TimeoutError("missing response")}))
        content = report.render(self.out, self.report)
        self.assertIn("| C | list | 12 | 12 | 11 | 12 | 11 | 0 | unavailable |", content)
        self.assertIn("Corpus messages missing at least one valid rating: **1 / 48**", content)
        self.assertIn("observed joint acceptances are C: 11", content)
        self.assertIn("only a lower bound", content)
        self.assertNotIn("Partial collection", content)

    def test_failed_calibration_does_not_become_zero_acceptance(self):
        rr.run(self.protocol, self.out, transport=FakeTransport(self.protocol, {0: "B"}))
        content = report.render(self.out, self.report)
        self.assertIn("| C | list | 12 | 12 | unavailable | 12 | unavailable | unavailable | unavailable |", content)
        self.assertIn("**56 / 104**", content)
        self.assertNotIn("lower bound", content)

    def test_interrupted_run_is_identified_as_partial(self):
        with self.assertRaises(KeyboardInterrupt):
            rr.run(self.protocol, self.out, transport=FakeTransport(self.protocol, interrupt_at=5))
        content = report.render(self.out, self.report)
        self.assertIn("Partial collection — unfinished snapshot", content)
        self.assertIn("**6 / 104**", content)
        self.assertIn("complete two-judge corpus result is **unavailable**", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
