import unittest

from gradeable.audit import audit
from gradeable.item import load_fixture
from gradeable.verdict import Verdict


class TestAuditOnFixture(unittest.TestCase):
    def setUp(self):
        self.items = load_fixture()
        self.report = audit(self.items)

    def test_fixture_size(self):
        self.assertEqual(self.report.n_total, 12)

    def test_current_trust_denominator(self):
        # With only the example rule implemented, p2 ("20") and p3 ("8") are
        # gold-problematic but slip through as EXACT_CHECKABLE -> the classifier
        # currently OVER-counts soundly gradeable. This is the honest baseline
        # the validation step exposes; it should rise toward 8/12 as the stub
        # rules get written.
        self.assertEqual(self.report.counts[Verdict.EXACT_CHECKABLE], 10)
        self.assertAlmostEqual(self.report.soundly_gradeable_fraction, 10 / 12)

    def test_two_items_flagged_ill_posed(self):
        self.assertEqual(self.report.counts[Verdict.ILL_POSED], 2)
        flagged_ids = {c.item.id for c in self.report.flagged}
        self.assertEqual(flagged_ids, {"p1", "p4"})


if __name__ == "__main__":
    unittest.main()
