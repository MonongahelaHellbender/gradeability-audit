import unittest

from gradeable.item import BenchmarkItem
from gradeable.classify import classify
from gradeable.rules import (
    answer_not_clean_number,
    internal_contradiction,
    underspecified_non_derivable,
)
from gradeable.verdict import Verdict


def item(ans, q="q?"):
    return BenchmarkItem(id="x", question=q, reference_answer=ans)


class TestExampleRule(unittest.TestCase):
    def test_clean_numbers_not_flagged(self):
        for ans in ["18", "-7", "$1,200", "0.5", "30%", "72"]:
            self.assertIsNone(answer_not_clean_number(item(ans)), ans)

    def test_non_numbers_flagged_ill_posed(self):
        for ans in ["12 or 15", "many", "about 7", "twelve"]:
            res = answer_not_clean_number(item(ans))
            self.assertIsNotNone(res, ans)
            self.assertEqual(res.verdict, Verdict.ILL_POSED)

    def test_strips_gsm8k_wrapping(self):
        self.assertIsNone(answer_not_clean_number(item("reasoning...\n#### 42")))


class TestUnderspecified(unittest.TestCase):
    def test_flags_has_some(self):
        res = underspecified_non_derivable(item("42", "Jenny has some marbles and gives away 5. How many left?"))
        self.assertIsNotNone(res)
        self.assertEqual(res.verdict, Verdict.ILL_POSED)

    def test_abstains_when_base_is_bound(self):
        # "some of the 20" — the base quantity IS given; must not flag.
        self.assertIsNone(underspecified_non_derivable(
            item("15", "Some of the 20 marbles are red. Jenny gives away 5. How many left?")))


class TestInternalContradiction(unittest.TestCase):
    def test_flags_conflicting_ages(self):
        res = internal_contradiction(item("8", "Ben is 10 years old. Ben is also 8 years old. How old is Ben?"))
        self.assertIsNotNone(res)
        self.assertEqual(res.verdict, Verdict.ILL_POSED)

    def test_abstains_with_temporal_cue(self):
        # Two ages but temporally qualified -> consistent, must not flag.
        self.assertIsNone(internal_contradiction(
            item("10", "Ben is 10 years old. Two years ago Ben was 8 years old. How old is Ben now?")))


class TestClassifyDefault(unittest.TestCase):
    def test_default_is_exact_checkable(self):
        self.assertEqual(classify(item("42")).verdict, Verdict.EXACT_CHECKABLE)

    def test_reports_most_restrictive(self):
        c = classify(item("many"))
        self.assertEqual(c.verdict, Verdict.ILL_POSED)
        self.assertTrue(c.fired)


if __name__ == "__main__":
    unittest.main()
