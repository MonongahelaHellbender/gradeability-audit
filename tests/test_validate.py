import unittest

from gradeable.item import load_fixture
from gradeable.validate import validate


class TestValidateOnFixture(unittest.TestCase):
    def setUp(self):
        self.report = validate(load_fixture())

    def test_all_items_labeled(self):
        self.assertEqual(self.report.n_labeled, 14)

    def test_perfect_on_fixture(self):
        # The three rules catch all 4 gold-problematic items and false-flag none
        # of the 10 clean ones (including the two adversarial near-misses).
        # NOTE: this is a UNIT-TEST sanity check on a synthetic 14-item set, not
        # evidence of real precision/recall. The honest number requires GSM8K +
        # GSM8K-Platinum (see data/README.md).
        self.assertEqual((self.report.tp, self.report.fp, self.report.fn, self.report.tn),
                         (4, 0, 0, 10))
        self.assertAlmostEqual(self.report.precision, 1.0)
        self.assertAlmostEqual(self.report.recall, 1.0)


if __name__ == "__main__":
    unittest.main()
