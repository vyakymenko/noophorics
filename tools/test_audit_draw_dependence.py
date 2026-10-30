#!/usr/bin/env python3
"""Checks on the draw-dependence audit, before it reads a real answer.

Each check is red on the defect it exists to find and green on the legitimate
case nearest to it: the repeat expectation is checked against every ordering,
the test is checked to stay quiet on independent draws and to fire on
persistent ones, and the record is checked to hold no answer text.
"""

import itertools
import json
import os
import random
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import audit_draw_dependence as ad  # noqa: E402


def dirichlet(rng, k, alpha=0.6):
    x = [rng.gammavariate(alpha, 1.0) for _ in range(k)]
    return [v / sum(x) for v in x]


def synthetic(rng, count, n, rho, k=3, family="m", source="E-1"):
    seqs = []
    for i in range(count):
        p = dirichlet(rng, k)
        cum, acc = [], 0.0
        for v in p:
            acc += v
            cum.append(acc)
        a = ad.persistent(rng, n, cum, rho)
        seqs.append(ad.Seq(source, family, "c", str(i), ad._encode(a)))
    return seqs


def null_excess(seqs, perms=200):
    keys = ad._groups(seqs)
    by_group = [[s.answers for s in seqs if (s.family, s.source) == k and ad.informative(s.answers)]
                for k in keys]
    rows = ad._perm_chunk((0, perms, by_group))
    base = sum(ad.expected_repeats(s.answers) for s in seqs if ad.informative(s.answers))
    return [sum(r[0] for r in row) - base for row in rows]


def excess(seqs):
    return sum(ad.repeats(s.answers) - ad.expected_repeats(s.answers)
               for s in seqs if ad.informative(s.answers))


class StatisticTests(unittest.TestCase):
    def test_expected_repeats_is_the_mean_over_every_ordering(self):
        for a in ((0, 0, 1, 2), (0, 0, 0, 1, 1), (0, 1, 2, 3), (0, 0, 1, 1, 1, 2)):
            with self.subTest(a=a):
                orders = list(itertools.permutations(a))
                mean = sum(ad.repeats(o) for o in orders) / len(orders)
                self.assertAlmostEqual(ad.expected_repeats(a), mean, places=12)
                # the nearest wrong formula, sum c^2 / n, is not it
                self.assertNotAlmostEqual(
                    sum(a.count(x) ** 2 for x in set(a)) / len(a), mean, places=6)

    def test_grouped_and_drift_on_known_sequences(self):
        self.assertTrue(ad.grouped((0, 0, 1, 1, 2)))
        self.assertFalse(ad.grouped((0, 1, 0, 1)))
        self.assertEqual(ad.drift((0, 0, 1, 1)), 8)
        self.assertEqual(ad.drift((0, 1, 0, 1)), 0)
        self.assertFalse(ad.informative((2, 2, 2)))

    def test_the_test_is_quiet_on_independent_draws_and_fires_on_persistent_ones(self):
        rng = random.Random(4)
        iid = synthetic(rng, 1500, 16, 0.0)
        sticky = synthetic(rng, 1500, 16, 0.3)
        for seqs, persistent in ((iid, False), (sticky, True)):
            with self.subTest(persistent=persistent):
                null = null_excess(seqs)
                sd = (sum(x * x for x in null) / len(null)) ** 0.5
                z = excess(seqs) / sd
                if persistent:
                    self.assertEqual(ad._upper_p(excess(seqs), null), 1 / 201)
                    self.assertGreater(z, 10)
                else:
                    self.assertLess(abs(z), 4)
                self.assertLess(abs(sum(null) / len(null)), 3 * sd / len(null) ** 0.5)

    def test_rho_hat_is_near_zero_without_persistence_and_grows_with_it(self):
        rng = random.Random(8)
        hats = []
        for rho in (0.0, 0.1, 0.3):
            seqs = synthetic(rng, 3000, 16, rho)
            room = sum(len(s.answers) - 1 - ad.expected_repeats(s.answers)
                       for s in seqs if ad.informative(s.answers))
            hats.append(excess(seqs) / room)
        self.assertLess(abs(hats[0]), 0.015)
        self.assertLess(hats[0], hats[1])
        self.assertLess(hats[1], hats[2])
        self.assertLess(hats[2], 0.3)          # biased toward zero, as the plan says

    def test_grouped_diagnostic_flags_rebuilt_sequences(self):
        rng = random.Random(2)
        seqs = synthetic(rng, 300, 16, 0.0)
        rebuilt = [s._replace(answers=tuple(sorted(s.answers))) for s in seqs]
        for data, flagged in ((seqs, False), (rebuilt, True)):
            keys = ad._groups(data)
            groups = [[s.answers for s in data if ad.informative(s.answers)]]
            rows = ad._perm_chunk((0, 500, groups))
            null = [row[0][2] for row in rows]
            observed = sum(ad.grouped(s.answers) for s in data if ad.informative(s.answers))
            p = ad._upper_p(observed, null)
            with self.subTest(flagged=flagged):
                self.assertEqual(len(keys), 1)
                if flagged:
                    self.assertLess(p, ad.GROUPED_FLAG * 5)
                else:
                    self.assertGreater(p, 0.01)


class ReadingTests(unittest.TestCase):
    def test_only_answer_draw_conditions_are_read(self):
        self.assertIsNone(ad.parse_condition("pred-sender@gpt-oss:120b#ab12"))
        self.assertIsNone(ad.parse_condition("claim-receiver@gpt-oss:120b#ab12"))
        self.assertIsNone(ad.parse_condition("no-model-here"))
        self.assertEqual(ad.parse_condition("r030_1@gpt-oss:120b#ab12"), ("r030_1", "gpt-oss:120b"))
        self.assertEqual(ad.parse_condition("prior@claude-opus-4-8/claude-opus-4-8"),
                         ("prior", "claude-opus-4-8"))

    def test_a_reused_prefix_is_counted_once_and_nothing_else_is_dropped(self):
        long = tuple("ABAB" * 7 + "AA")
        rows = [("E-1", "m", "CEILING@m", "p1", long),
                ("E-2", "m", "CEILING@m", "p1", long[:16]),      # imported prefix: dropped
                ("E-3", "m", "CEILING@m", "p1", long[:16]),      # and again
                ("E-2", "m", "CEILING@m", "p2", long[:16]),      # another probe: kept
                ("E-2", "m", "PRIOR@m", "p1", long[:16]),        # another condition: kept
                ("E-4", "m", "CEILING@m", "p1", tuple("BBAB" * 4))]  # not a prefix: kept
        kept, dropped = ad.dedupe(rows)
        self.assertEqual(dropped, 2)
        self.assertEqual(len(kept), 4)


class ScoringTests(unittest.TestCase):
    def test_holm(self):
        out = ad.holm({"a": 0.01, "b": 0.04, "c": 0.03})
        self.assertAlmostEqual(out["a"], 0.03)
        self.assertAlmostEqual(out["c"], 0.06)
        self.assertAlmostEqual(out["b"], 0.06)

    def test_rho_upper_reads_the_grid(self):
        n = len(ad.GRID)
        at = lambda k: [[0.0] * 100 if i <= k else [1.0] * 100 for i in range(n)]
        self.assertEqual(ad.rho_upper(0.5, at(7)), {"kind": "bound", "value": 0.07})
        self.assertEqual(ad.rho_upper(0.5, at(n - 1))["kind"], "above_grid")
        self.assertEqual(ad.rho_upper(-1.0, at(3))["kind"], "below_grid")

    def test_each_threshold_from_both_sides(self):
        def fams(p_holm=0.5, bound=0.05, drift=0.5):
            f = {"p_holm": p_holm, "rho_upper": {"kind": "bound", "value": bound}, "p_drift": drift}
            return {k: dict(f) for k in ad.FAMILIES}
        self.assertTrue(all(v["holds"] for v in ad.score(fams()).values()))
        self.assertFalse(ad.score(fams(p_holm=0.05))["P1"]["holds"])
        self.assertTrue(ad.score(fams(p_holm=0.0501))["P1"]["holds"])
        self.assertFalse(ad.score(fams(bound=0.10))["P1"]["holds"])
        self.assertTrue(ad.score(fams(bound=0.09))["P1"]["holds"])
        self.assertTrue(ad.score(fams(bound=0.29))["P2"]["holds"])
        self.assertFalse(ad.score(fams(bound=0.30))["P3"]["holds"])
        self.assertFalse(ad.score(fams(drift=0.0499))["P4"]["holds"])
        above = fams()
        above["qwen3.5:35b"]["rho_upper"] = {"kind": "above_grid", "value": None}
        self.assertFalse(ad.score(above)["P2"]["holds"])
        self.assertFalse(ad.score({})["P1"]["holds"])


class RecordTests(unittest.TestCase):
    def tree(self, root, extra=""):
        rng = random.Random(5)
        for exp, model in (("E-901-x", "gpt-oss:120b"), ("E-902-y", "qwen3.5:35b")):
            os.makedirs(os.path.join(root, "experiments", exp))
            cache = {}
            for c in range(3):
                rows = {}
                for i in range(20):
                    p = dirichlet(rng, 3)
                    rows["SECRETPROBE%d" % i] = ["SECRET_ANSWER_%d" % rng.choices(range(3), p)[0]
                                                 for _ in range(16)]
                cache["cond%d@%s#SECRETFP%s" % (c, model, extra)] = rows
            cache["pred-sender@%s#x" % model] = {"q": ["SECRET_PRED"] * 9}
            with open(os.path.join(root, "experiments", exp, "sample-cache.json"), "w") as fh:
                json.dump(cache, fh)

    def test_the_record_holds_no_answer_probe_or_condition_text(self):
        with tempfile.TemporaryDirectory() as root:
            self.tree(root)
            record = ad.audit(root, workers=1, permutations=200)
            text = json.dumps(record)
            self.assertNotIn("SECRET", text)
            self.assertEqual(record["dedupe"]["kept"], 120)
            self.assertEqual(set(record["families"]), {"gpt-oss:120b", "qwen3.5:35b"})

    def write(self, root, record, note_tables=None):
        os.makedirs(os.path.join(root, "research"), exist_ok=True)
        with open(os.path.join(root, ad.RECORD), "w") as fh:
            json.dump(record, fh)
        tables = ad.render(record) if note_tables is None else note_tables
        with open(os.path.join(root, ad.NOTE), "w") as fh:
            fh.write("prose\n" + ad.START + "\n" + tables + ad.END + "\n")

    def test_check_goes_red_on_each_observed_field_a_missing_model_and_the_note(self):
        with tempfile.TemporaryDirectory() as root:
            self.tree(root)
            record = ad.audit(root, workers=1, permutations=200)
            self.write(root, record)
            self.assertEqual(ad.check(root), [])
            edits = [lambda r: r["families"]["qwen3.5:35b"].__setitem__("sequences", 61),
                     lambda r: r["families"]["gpt-oss:120b"].__setitem__("draws", 1),
                     lambda r: r["families"]["gpt-oss:120b"].__setitem__("rho_hat", 0.3),
                     lambda r: r["families"]["gpt-oss:120b"].__setitem__("drift", -1),
                     lambda r: r["by_source"][0].__setitem__("rho_hat", 0.3),
                     lambda r: r["families"].pop("qwen3.5:35b")]
            for i, edit in enumerate(edits):
                tampered = json.loads(json.dumps(record))
                edit(tampered)
                tampered["predictions"] = json.loads(json.dumps(ad.score(tampered["families"])))
                self.write(root, tampered)
                with self.subTest(edit=i):
                    self.assertTrue(ad.check(root))
            self.write(root, record, note_tables=ad.render(record).replace("| **yes** |", "| **no** |", 1)
                       if "| **yes** |" in ad.render(record) else ad.render(record) + "x\n")
            self.assertIn("the note's tables differ from the record", ad.check(root))
            os.remove(os.path.join(root, ad.NOTE))
            self.assertIn("the results note is missing", ad.check(root))

    def test_a_seeded_rerun_reproduces_its_record_and_catches_an_edited_bound(self):
        with tempfile.TemporaryDirectory() as root:
            self.tree(root)
            record = ad.audit(root, workers=1, permutations=200)
            os.makedirs(os.path.join(root, "research"))
            with open(os.path.join(root, ad.RECORD), "w") as fh:
                fh.write(json.dumps(record, indent=1, sort_keys=True) + "\n")
            self.assertEqual(ad.check_full(root, workers=1, permutations=200), [])
            record["families"]["gpt-oss:120b"]["p_holm"] = 0.04
            with open(os.path.join(root, ad.RECORD), "w") as fh:
                fh.write(json.dumps(record, indent=1, sort_keys=True) + "\n")
            self.assertTrue(ad.check_full(root, workers=1, permutations=200))

    def test_check_is_green_on_its_record_and_red_on_a_change(self):
        with tempfile.TemporaryDirectory() as root:
            self.tree(root)
            record = ad.audit(root, workers=1, permutations=200)
            self.write(root, record)
            path = os.path.join(root, ad.RECORD)
            self.assertEqual(ad.check(root), [])
            tampered = json.loads(json.dumps(record))
            tampered["predictions"]["P4"]["holds"] = not tampered["predictions"]["P4"]["holds"]
            with open(path, "w") as fh:
                json.dump(tampered, fh)
            self.assertIn("predictions differ from score(families)", ad.check(root))
            with open(path, "w") as fh:
                json.dump(record, fh)
            cache = os.path.join(root, "experiments", "E-901-x", "sample-cache.json")
            with open(cache) as fh:
                data = json.load(fh)
            first = sorted(data)[0]
            probe = sorted(data[first])[0]
            data[first][probe] = data[first][probe][::-1][:15] + ["SECRET_ANSWER_9"]
            with open(cache, "w") as fh:
                json.dump(data, fh)
            self.assertTrue(ad.check(root))


class ProseTests(unittest.TestCase):
    """The numbers quoted in prose, on the repository's own files and record."""

    FILES = (ad.NOTE, "theory/open-problems.md", "research/README.md")

    def copy(self, root):
        for rel in self.FILES + (ad.RECORD,):
            os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
            shutil.copy(os.path.join(ad.ROOT, rel), os.path.join(root, rel))
        with open(os.path.join(root, ad.RECORD)) as fh:
            return json.load(fh)

    def test_quoted_numbers_are_green_as_written_and_red_when_changed_or_moved(self):
        with tempfile.TemporaryDirectory() as root:
            record = self.copy(root)
            self.assertEqual(ad.prose_problems(root, record), [])
            for rel, old, new in ((ad.NOTE, "raw p **0.033**", "raw p **0.003**"),
                                  (ad.NOTE, "All four predictions held", "Three of four predictions held"),
                                  ("theory/open-problems.md", "They rest on 537,", "They rest on 538,"),
                                  ("research/README.md", "raw p 0.033 before", "raw p 0.03 before"),
                                  (ad.NOTE, "Its power against `ρ = 0.05` is", "Its power at `ρ = 0.05` is")):
                path = os.path.join(root, rel)
                with open(path) as fh:
                    text = fh.read()
                self.assertIn(old, text)
                with open(path, "w") as fh:
                    fh.write(text.replace(old, new))
                with self.subTest(new=new):
                    self.assertTrue(ad.prose_problems(root, record))
                with open(path, "w") as fh:
                    fh.write(text)


if __name__ == "__main__":
    unittest.main()
