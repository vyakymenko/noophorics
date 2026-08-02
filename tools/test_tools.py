#!/usr/bin/env python3
"""Tests for the checks. The checks are not exempt from the rule they enforce.

`check_counts.py`, `check_retracted.py` and `check_links.py` are what stand
between this repository and the class of defect it has repeatedly shipped: a
number that disagrees with its source, a withdrawn claim restated as live, a
pointer that resolves to nothing. Until this file existed, all three were
themselves unchecked -- their only evidence of working was that they printed a
clean line on a repository their authors believed to be clean, which is exactly
the shape of a gate that cannot fail.

That is not hypothetical here. Three defects in this repository survived
careful reading and died the moment something was executed: a function called
but never defined, a gate that could not fail, a monitor whose pgrep matched
itself. Two more were found by writing the tests below -- `check_links` crashed
with a ValueError instead of reporting when a path straddled a symlink, and the
first stall detector's vocabulary suppressed the very defects it was written to
catch.

So each test here asserts the property that matters for a check: **that it goes
red on the specific defect it exists to find, and green on the legitimate case
that most resembles it.** A test that only proves the clean case passes would
be satisfied by a check that always returns zero.

    python3 tools/test_tools.py
"""

from __future__ import annotations

import io
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_counts  # noqa: E402
import check_links  # noqa: E402
import check_retracted  # noqa: E402


def fixture(files: dict) -> Path:
    """A throwaway repository containing exactly the given files."""
    root = Path(tempfile.mkdtemp())
    for rel, body in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return root


class ToolTest(unittest.TestCase):
    def tree(self, files: dict) -> Path:
        root = fixture(files)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root


# ---------------------------------------------------------------------------


class TestCheckLinks(ToolTest):
    def broken(self, files: dict):
        root = self.tree(files)
        old, check_links.ROOT = check_links.ROOT, root
        self.addCleanup(lambda: setattr(check_links, "ROOT", old))
        report = []
        check_links.check_markdown(report)
        check_links.check_html(report)
        return report

    def test_markdown_missing_file_is_reported(self):
        self.assertEqual(len(self.broken({"a.md": "see [x](nope.md)\n"})), 1)

    def test_markdown_missing_anchor_is_reported(self):
        r = self.broken({"a.md": "see [x](b.md#ghost)\n", "b.md": "## Real Heading\n"})
        self.assertEqual(len(r), 1)
        self.assertIn("no such anchor", r[0][3])

    def test_markdown_live_anchor_passes(self):
        """The legitimate case that most resembles the defect."""
        self.assertEqual(
            self.broken({"a.md": "see [x](b.md#real-heading)\n",
                         "b.md": "## Real Heading\n"}), [])

    def test_explicit_html_anchor_in_markdown_passes(self):
        """`## L2 — Law <a id="l2"></a>` is how this repository anchors laws."""
        self.assertEqual(
            self.broken({"a.md": "see [x](b.md#l2)\n",
                         "b.md": '## L2 — Law of asymmetry <a id="l2"></a>\n'}), [])

    def test_html_route_that_nothing_serves_is_reported(self):
        r = self.broken({"docs/index.html": '<a href="/journal/ghost/">x</a>'})
        self.assertEqual(len(r), 1)
        self.assertIn("no page serves", r[0][3])

    def test_html_route_that_exists_passes(self):
        self.assertEqual(
            self.broken({"docs/index.html": '<a href="/journal/real/">x</a>',
                         "docs/journal/real/index.html": "<p>ok</p>"}), [])

    def test_html_missing_fragment_is_reported(self):
        r = self.broken({"docs/index.html": '<a href="#ghost">x</a><h2 id="real">r</h2>'})
        self.assertEqual(len(r), 1)

    def test_external_links_are_never_fetched(self):
        """A check that reddens when a third-party host is slow gets disabled."""
        self.assertEqual(
            self.broken({"a.md": "[x](https://example.invalid/certainly-404)\n"}), [])

    def test_a_symlinked_checkout_reports_instead_of_crashing(self):
        """`Path.relative_to` raises across a symlink; a report must not."""
        root = self.tree({"a.md": "see [x](b.md#ghost)\n", "b.md": "# Real\n"})
        link = Path(tempfile.mkdtemp()) / "via-link"
        self.addCleanup(shutil.rmtree, link.parent, ignore_errors=True)
        link.symlink_to(root, target_is_directory=True)
        old, check_links.ROOT = check_links.ROOT, link
        self.addCleanup(lambda: setattr(check_links, "ROOT", old))
        report = []
        check_links.check_markdown(report)          # must not raise
        self.assertEqual(len(report), 1)


# ---------------------------------------------------------------------------


class TestCheckRetracted(ToolTest):
    SRC = "PRINCIPIA.md"

    def run_check(self, files: dict, ngram: int = 6):
        root = self.tree(files)
        saved = (check_retracted.ROOT, check_retracted.SOURCES,
                 check_retracted.TARGETS, check_retracted.TARGET_GLOBS)

        def restore():
            (check_retracted.ROOT, check_retracted.SOURCES,
             check_retracted.TARGETS, check_retracted.TARGET_GLOBS) = saved
        self.addCleanup(restore)
        check_retracted.ROOT = root
        check_retracted.SOURCES = [self.SRC]
        check_retracted.TARGETS = [f for f in files if f != self.SRC]
        check_retracted.TARGET_GLOBS = []
        out = io.StringIO()
        argv, sys.argv = sys.argv, ["check_retracted", "--ngram", str(ngram)]
        try:
            with redirect_stdout(out):
                code = check_retracted.main()
        finally:
            sys.argv = argv
        return code, out.getvalue()

    CLAIM = ("capacity between any two systems with non identical priors is "
             "strictly less than one")

    def test_a_withdrawn_claim_restated_as_live_is_caught(self):
        code, out = self.run_check({
            self.SRC: "## A3\n\n> ~~%s~~\n>\n> Refuted by a lookup table.\n" % self.CLAIM,
            "site.md": "Our third axiom: %s. It follows that transfer is hard.\n" % self.CLAIM,
        })
        self.assertEqual(code, 1)
        self.assertIn("stated as live", out)

    def test_the_same_claim_quoted_with_its_withdrawal_passes(self):
        """A findings page has to be able to say what it broke."""
        code, out = self.run_check({
            self.SRC: "## A3\n\n> ~~%s~~\n>\n> Refuted by a lookup table.\n" % self.CLAIM,
            "site.md": ("This was withdrawn in v0.3: %s. A lookup table reached "
                        "F* = 1.\n" % self.CLAIM),
        })
        self.assertEqual(code, 0)

    def test_struck_text_on_the_target_is_not_a_restatement(self):
        code, _ = self.run_check({
            self.SRC: "## A3\n\n> ~~%s~~\n>\n> Refuted.\n" % self.CLAIM,
            "site.html": "<p><s>%s</s> It was false.</p>" % self.CLAIM,
        })
        self.assertEqual(code, 0)

    def test_a_conditional_refutation_nearby_does_not_excuse_it(self):
        """Every law card ends "Refuted if:" -- that is a future condition."""
        code, _ = self.run_check({
            self.SRC: "## A3\n\n> ~~%s~~\n>\n> Refuted 2026-07-29.\n" % self.CLAIM,
            "site.md": ("L9. %s. Refuted if a bounded message closes the gap.\n"
                        % self.CLAIM),
        })
        self.assertEqual(code, 1)

    def test_british_and_american_spelling_are_one_claim(self):
        code, _ = self.run_check({
            self.SRC: "~~the quantity that engineering should optimize everywhere~~\n",
            "site.md": "It is the quantity that engineering should optimise everywhere.\n",
        })
        self.assertEqual(code, 1)


# ---------------------------------------------------------------------------


class TestCheckCounts(ToolTest):
    """A stated count against its source, where the source is computed."""

    def base(self, tests_n: int, readme_states: int) -> dict:
        return {
            "metrics/tests/test_metrics.py":
                "".join("def test_%d(): pass\n" % i for i in range(tests_n)),
            "theory/laws.md": "## L1 a\n## L2 b\n",
            # Nine, not two: check_counts only reads numerals it can compare,
            # and its vocabulary starts at "nine". A fixture that uses a word
            # outside it tests the vocabulary, not the count.
            "theory/open-problems.md":
                "".join("## %d. p\n" % i for i in range(1, 10)),
            "PRINCIPIA.md": "**A1 — x.**\n**A2 — y.**\n",
            "RETRACTIONS.md": "| # | Claim |\n|---|---|\n| 1 | a |\n",
            "README.md": ("python3 metrics/tests/test_metrics.py       # %d tests\n"
                          "nine open problems\n" % readme_states),
            "CITATION.cff": "nine open problems\n",
            "docs/index.html": ("<dt>Conjectural laws</dt><dd>2</dd>"
                                "<dt>Open problems</dt><dd>9</dd>"
                                "<dt>Own claims refuted</dt><dd><a href=x>1</a></dd>"
                                "<p>nine open problems, and two experiments "
                                "are void.</p>"),
            "docs/journal/one/index.html": "x",
            "docs/en/index.html": "x",
            # Two voided experiments and one that merely has a directory: the
            # count is files named VOID.md, not experiments that exist.
            "experiments/E-1/VOID.md": "void",
            "experiments/E-2/VOID.md": "void",
            "experiments/E-3/PREREGISTRATION.md": "alive",
        }

    def run_check(self, files: dict):
        root = self.tree(files)
        old, check_counts.ROOT = check_counts.ROOT, str(root)
        self.addCleanup(lambda: setattr(check_counts, "ROOT", old))
        out = io.StringIO()
        with redirect_stdout(out):
            code = check_counts.main()
        return code, out.getvalue()

    def test_a_matching_count_passes(self):
        code, out = self.run_check(self.base(tests_n=7, readme_states=7))
        self.assertEqual(code, 0, out)

    def test_a_stale_count_is_caught(self):
        """The defect that shipped: README said 86 after the suite reached 92."""
        code, out = self.run_check(self.base(tests_n=7, readme_states=6))
        self.assertEqual(code, 1)
        self.assertIn("MISMATCH", out)

    def test_a_spelled_out_numeral_counts_as_a_claim(self):
        """"ten open problems" is a claim exactly as much as "10" is."""
        files = self.base(tests_n=7, readme_states=7)
        files["README.md"] = files["README.md"].replace("nine open problems",
                                                        "twelve open problems")
        code, out = self.run_check(files)
        self.assertEqual(code, 1)
        self.assertIn("MISMATCH", out)


    def test_a_voided_run_is_not_a_voided_experiment(self):
        """The count is VOID.md files, and the site got this wrong.

        It said "three experiments are void" while two directories carried the
        file. The third was E-001's first live run, thrown away and then re-run
        to completion -- a voided run, not a voided experiment.
        """
        files = self.base(tests_n=7, readme_states=7)
        files["experiments/E-4/VOID.md"] = "void"          # now three
        code, out = self.run_check(files)
        self.assertEqual(code, 1)
        self.assertIn("MISMATCH", out)

    def test_the_void_count_survives_a_repository_with_no_experiments(self):
        """A counter that raises instead of reporting is an outage, not an audit."""
        files = {k: v for k, v in self.base(tests_n=7, readme_states=7).items()
                 if not k.startswith("experiments/")}
        files["docs/index.html"] = files["docs/index.html"].replace(
            "two experiments are void", "four experiments are void")
        code, out = self.run_check(files)          # must not raise
        self.assertEqual(code, 1)
        self.assertIn("voids", out)

    def test_a_claim_that_moved_is_a_failure_not_a_pass(self):
        """A pattern that stops matching means the claim was edited or removed.

        Treating that as "nothing to check" is how a check quietly stops
        checking: the file still passes, and the number it guarded is now
        unguarded. It has to be as loud as a wrong number.
        """
        files = self.base(tests_n=7, readme_states=7)
        files["README.md"] = files["README.md"].replace("nine open problems",
                                                        "several open problems")
        code, out = self.run_check(files)
        self.assertEqual(code, 1)
        self.assertIn("PATTERN NOT FOUND", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
