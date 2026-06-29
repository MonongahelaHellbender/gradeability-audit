import unittest

from gradeable.item import load_fixture
from gradeable.validate import validate


class TestValidateOnFixture(unittest.TestCase):
    def setUp(self):
        self.report = validate(load_fixture())

    def test_all_items_labeled(self):
        self.assertEqual(self.report.n_labeled, 14)

    def test_fixture_after_retraction(self):
        # Two SOUND rules catch p1/p3/p4 with no false flags; p2 is missed since
        # the unsound underspecified rule was retracted -> precision 1.0, recall
        # 0.75. This is a UNIT-TEST sanity check on a synthetic 14-item set, NOT
        # evidence of real precision/recall. The real numbers (from GSM8K +
        # GSM8K-Platinum) are far harsher: recall 0/33. See scripts/report.py.
        self.assertEqual((self.report.tp, self.report.fp, self.report.fn, self.report.tn),
                         (3, 0, 1, 10))
        self.assertAlmostEqual(self.report.precision, 1.0)
        self.assertAlmostEqual(self.report.recall, 0.75)


if __name__ == "__main__":
    unittest.main()
