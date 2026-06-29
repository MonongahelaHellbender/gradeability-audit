import unittest

from gradeable.item import BenchmarkItem
from gradeable.classify import classify
from gradeable.rules import answer_not_clean_number
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


class TestClassifyDefault(unittest.TestCase):
    def test_default_is_exact_checkable(self):
        self.assertEqual(classify(item("42")).verdict, Verdict.EXACT_CHECKABLE)

    def test_reports_most_restrictive(self):
        c = classify(item("many"))
        self.assertEqual(c.verdict, Verdict.ILL_POSED)
        self.assertTrue(c.fired)


if __name__ == "__main__":
    unittest.main()
