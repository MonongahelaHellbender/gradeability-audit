import unittest

from gradeable.audit import audit
from gradeable.item import load_fixture
from gradeable.verdict import Verdict


class TestAuditOnFixture(unittest.TestCase):
    def setUp(self):
        self.items = load_fixture()
        self.report = audit(self.items)
        self.verdict_by_id = {c.item.id: c.verdict for c in self.report.classified}

    def test_fixture_size(self):
        self.assertEqual(self.report.n_total, 14)  # 10 clean + 4 problematic

    def test_trust_denominator(self):
        # Two SOUND rules are live (answer_not_clean_number, internal_contradiction).
        # underspecified_non_derivable was retracted (unsound on real data), so p2
        # ("Jenny has some marbles ...") is an HONEST miss and stays exact-checkable.
        self.assertEqual(self.report.counts[Verdict.EXACT_CHECKABLE], 11)
        self.assertEqual(self.report.counts[Verdict.JUDGE_DEPENDENT], 0)
        self.assertEqual(self.report.counts[Verdict.ILL_POSED], 3)
        self.assertAlmostEqual(self.report.soundly_gradeable_fraction, 11 / 14)

    def test_flagged_are_the_sound_catches(self):
        # p1/p4 (non-numeric key) + p3 (age contradiction). p2 is the known miss.
        flagged_ids = {c.item.id for c in self.report.flagged}
        self.assertEqual(flagged_ids, {"p1", "p3", "p4"})

    def test_near_misses_not_flagged(self):
        # Precision guard: c9 ("some of the 20 ...") and c10 ("two years ago ...
        # Ben was 8") look like the patterns the new rules hunt for but are
        # well-posed. They MUST stay exact-checkable.
        self.assertEqual(self.verdict_by_id["c9"], Verdict.EXACT_CHECKABLE)
        self.assertEqual(self.verdict_by_id["c10"], Verdict.EXACT_CHECKABLE)


if __name__ == "__main__":
    unittest.main()
