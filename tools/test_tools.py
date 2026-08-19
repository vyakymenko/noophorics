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
import json
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

    def test_experiment_documents_are_discovered_as_sources(self):
        """The glob, not the seven names. A new experiment must not need an edit.

        Three withdrawn claims were living in findings and void documents with
        nothing indexing them, because SOURCES was a hand-maintained list and a
        new experiment produces a new file that nobody remembers to add.
        """
        root = self.tree({
            "PRINCIPIA.md": "x\n",
            "experiments/E-9/FINDINGS.md": "y\n",
            "experiments/E-9/VOID.md": "z\n",
            "experiments/E-9/PREREGISTRATION.md": "not a source\n",
        })
        old, check_retracted.ROOT = check_retracted.ROOT, root
        self.addCleanup(lambda: setattr(check_retracted, "ROOT", old))
        found = check_retracted._sources()
        self.assertIn("experiments/E-9/FINDINGS.md", found)
        self.assertIn("experiments/E-9/VOID.md", found)
        self.assertNotIn("experiments/E-9/PREREGISTRATION.md", found)

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
            # The tally line is part of the fixture because check_counts now
            # reads it. Two, to match the two VOID.md files below. Nine rows
            # rather than one because the retraction count is now also claimed
            # in prose, and prose numerals start at "nine" in the vocabulary.
            "RETRACTIONS.md": ("**Standing tally: nine claims withdrawn, two "
                               "experiments void.**\n"
                               "| # | Claim |\n|---|---|\n"
                               + "".join("| %d | a |\n" % i for i in range(1, 10))),
            "README.md": ("python3 metrics/tests/test_metrics.py       # %d tests\n"
                          "nine open problems\n" % readme_states),
            "CITATION.cff": "nine open problems\n",
            "docs/index.html": ("<dt>Conjectural laws</dt><dd>2</dd>"
                                "<dt>Open problems</dt><dd>9</dd>"
                                "<dt>Own claims refuted</dt><dd><a href=x>9</a></dd>"
                                "<p>nine open problems, and two experiments "
                                "are void. Nine of our own claims are "
                                "withdrawn.</p>"),
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

    def test_the_retraction_count_in_prose_is_a_claim(self):
        """The stat card was checked and the sentence beside it was not.

        That sentence is the one carried into nineteen translations, so an
        unchecked numeral in it is wrong in twenty places at once. The card is
        left correct here, so only the prose can produce the mismatch.
        """
        files = self.base(tests_n=7, readme_states=7)
        files["docs/index.html"] = files["docs/index.html"].replace(
            "Nine of our own claims", "Twelve of our own claims")
        code, out = self.run_check(files)
        self.assertEqual(code, 1)
        self.assertIn("MISMATCH", out)

    def test_a_stale_tally_in_the_retractions_file_is_caught(self):
        """The file that exists so a count can be audited had an unaudited one.

        Its standing tally said three experiments void while two directories
        carried VOID.md, and went on saying zero findings established after one
        was. The void half is now read here as well as on the site; this is the
        test that it is actually read, on the defect it exists to find.
        """
        files = self.base(tests_n=7, readme_states=7)
        files["RETRACTIONS.md"] = files["RETRACTIONS.md"].replace(
            "two experiments void", "three experiments void")
        code, out = self.run_check(files)
        self.assertEqual(code, 1)
        self.assertIn("MISMATCH", out)

    def test_a_correct_tally_in_the_retractions_file_passes(self):
        """The legitimate case that most resembles the defect above."""
        code, out = self.run_check(self.base(tests_n=7, readme_states=7))
        self.assertEqual(code, 0)
        self.assertNotIn("MISMATCH", out)

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


class TestReuseSender(ToolTest):
    """`headroom_check.reuse_sender` asserted a model it never read.

    The reuse path printed "same model, spec, measure and n" while comparing
    only `draws` and `probe_measure`. A sender drawn on one model was therefore
    accepted verbatim under `--model` naming another, and the run affirmed the
    match in its own log. The measurement that results is a cross-model
    sender/receiver pair labelled as same-model, which no later reader could
    detect from the output file.

    What these tests cover, stated exactly rather than generously: that the
    model is now SURFACED, that raw draws survive when the file has them, and
    that the two silent-failure paths raise instead of returning None. The
    comparison itself lives in `main()` behind an ollama connection and a
    650-line argument path, and is NOT exercised here. So this is the necessary
    half, not the sufficient one -- a reader should know that the guard is
    covered only as far as its inputs.
    """

    def setUp(self):
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(
            os.path.dirname(here), "experiments",
            "E-001c-fluency-length-controlled"))
        import headroom_check  # noqa: E402
        self.hc = headroom_check

    def record(self, model="gpt-oss:120b", draws=10, raw=True):
        rec = {"model": model, "draws": draws,
               "probe_measure": "MERIDIAN-IX32@f058de0f906e",
               "parties": {"sender": {"modes": ["HANDLED"], "margins": [10]}}}
        if raw:
            rec["parties"]["sender"]["raw"] = [["HANDLED"] * 10]
        return rec

    def write(self, rec) -> str:
        root = self.tree({"prev.json": json.dumps(rec)})
        return str(root / "prev.json")

    def test_model_is_returned_so_it_can_be_checked(self):
        """The defect was an omission: the field was never surfaced."""
        got = self.hc.reuse_sender(self.write(self.record(model="qwen3.5:35b")))
        self.assertEqual(got["model"], "qwen3.5:35b")

    def test_raw_draws_survive_when_present(self):
        """Refusing a statistic the file can support is a self-inflicted gap."""
        got = self.hc.reuse_sender(self.write(self.record(raw=True)))
        self.assertEqual(got["raw"], [["HANDLED"] * 10])

    def test_modes_only_file_reports_no_raw(self):
        """The legitimate case that most resembles it: an early file."""
        got = self.hc.reuse_sender(self.write(self.record(raw=False)))
        self.assertIsNone(got["raw"])

    def test_missing_file_is_an_error_not_a_silent_fresh_draw(self):
        """A mistyped path used to return None and fall through to `else`,
        where the run drew a fresh sender and reported nothing unusual."""
        with self.assertRaises(SystemExit):
            self.hc.reuse_sender("/nonexistent/prev.json")

    def test_file_without_sender_party_is_an_error(self):
        rec = self.record()
        rec["parties"] = {}
        with self.assertRaises(SystemExit):
            self.hc.reuse_sender(self.write(rec))


class TestJournalCompleteness(ToolTest):
    """`build_journal.check_sources_complete` covered only half its inputs.

    SOURCES is hand-maintained and draws from two directories. The guard that
    catches an unlisted document was written after E-001c's VOID.md sat
    unpublished, and it walked `experiments/` alone -- so a new file in
    `journal/` was dropped silently, with the build printing a success line and
    exiting 0. The guard against a hand-maintained list drifting was itself a
    hand-maintained list.
    """

    def setUp(self):
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, here)
        import build_journal  # noqa: E402
        self.bj = build_journal
        self._root = build_journal.ROOT
        self.addCleanup(setattr, build_journal, "ROOT", self._root)

    def point_at(self, files: dict):
        root = self.tree(files)
        self.bj.ROOT = str(root)
        return root

    def test_unlisted_journal_entry_is_reported(self):
        """Red on the defect: a journal file in neither list."""
        self.point_at({"journal/2026-01-01-unlisted.md": "# x\n",
                       "experiments/.keep": ""})
        self.assertIn("journal/2026-01-01-unlisted.md",
                      self.bj.check_sources_complete())

    def test_listed_journal_entry_is_not_reported(self):
        """Green on the case that most resembles it: the same file, listed."""
        listed = {path for _, path, _ in self.bj.SOURCES}
        self.assertTrue(any(p.startswith("journal/") for p in listed),
                        "SOURCES should carry journal entries")
        self.point_at({"journal/2026-07-28-founding.md": "# x\n",
                       "experiments/.keep": ""})
        self.assertEqual(self.bj.check_sources_complete(), [])

    def test_non_markdown_in_journal_is_ignored(self):
        """A stray non-.md file is not a missing entry."""
        self.point_at({"journal/notes.txt": "x", "experiments/.keep": ""})
        self.assertEqual(self.bj.check_sources_complete(), [])


class TestCheckExperiments(ToolTest):
    """The site said E-002 was a Planned ablation ladder for weeks.

    `experiments/E-002-phantom-agreement/` held a VOID.md the whole time. The
    founding roadmap had given that id to the ladder and the repository later
    reused it, so a reader following L1's pointer landed on a voided experiment
    about something else. `check_links` could not see it -- the ids in laws.md
    are prose, not links -- and `check_counts` compared "four experiments are
    void" against four VOID.md files and was right.
    """

    def setUp(self):
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, here)
        import check_experiments
        self.ce = check_experiments

    def site(self, rows) -> str:
        body = "".join(
            '<div class="exp"><div class="hd">'
            '<span class="id">%s</span><span class="nm">n</span>'
            '<span class="tag">%s</span></div><p>x</p></div>' % r for r in rows)
        return '<div class="ledger">%s</div>' % body

    def tree_with(self, dirs: dict, rows) -> str:
        files = {"docs/index.html": self.site(rows)}
        for name, marker in dirs.items():
            files["experiments/%s/%s" % (name, marker)] = "x\n"
        return str(self.tree(files))

    def test_void_experiment_shown_as_planned_is_caught(self):
        """Red on the exact defect: the id exists and the site calls it Planned."""
        root = self.tree_with({"E-002-phantom-agreement": "VOID.md"},
                              [("E-002", "Planned")])
        bad = self.ce.check(root)
        self.assertEqual(len(bad), 1)
        self.assertIn("exists", bad[0][1])

    def test_void_experiment_shown_as_void_passes(self):
        """Green on the case that most resembles it."""
        root = self.tree_with({"E-002-phantom-agreement": "VOID.md"},
                              [("E-002", "Void")])
        self.assertEqual(self.ce.check(root), [])

    def test_experiment_missing_from_the_site_is_caught(self):
        root = self.tree_with({"E-002c-calibration-slope": "FINDINGS.md"}, [])
        bad = self.ce.check(root)
        self.assertEqual(len(bad), 1)
        self.assertIn("absent from the site", bad[0][1])

    def test_planned_row_with_no_directory_passes(self):
        """A genuinely unbuilt experiment is the legitimate use of Planned."""
        root = self.tree_with({}, [("E-006", "Planned")])
        self.assertEqual(self.ce.check(root), [])

    def test_findings_row_with_no_directory_is_caught(self):
        root = self.tree_with({}, [("E-009", "Findings")])
        bad = self.ce.check(root)
        self.assertEqual(len(bad), 1)
        self.assertIn("no experiments", bad[0][1])

    def test_compound_tag_is_normalised_not_treated_as_absent(self):
        """`Void &middot; informative` is a Void with a gloss.

        The first version of the regex required class="tag" exactly and missed
        E-001's class="tag tag-alert", then reported the row as ABSENT -- a
        louder and quite different defect from the one present.
        """
        self.assertEqual(self.ce.normalise("Void &middot; informative"), "Void")


if __name__ == "__main__":
    unittest.main(verbosity=2)
