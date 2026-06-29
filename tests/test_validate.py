import unittest

from gradeable.item import load_fixture
from gradeable.validate import validate


class TestValidateOnFixture(unittest.TestCase):
    def setUp(self):
        self.report = validate(load_fixture())

    def test_all_items_labeled(self):
        self.assertEqual(self.report.n_labeled, 12)

    def test_precision_perfect_recall_half(self):
        # Example rule catches p1, p4 (true positives), never false-flags a clean
        # item (precision 1.0), and misses p2, p3 (recall 0.5). The whole point
        # of the tool: precision must stay high; recall is what you grow.
        self.assertEqual((self.report.tp, self.report.fp, self.report.fn, self.report.tn),
                         (2, 0, 2, 8))
        self.assertAlmostEqual(self.report.precision, 1.0)
        self.assertAlmostEqual(self.report.recall, 0.5)


if __name__ == "__main__":
    unittest.main()
