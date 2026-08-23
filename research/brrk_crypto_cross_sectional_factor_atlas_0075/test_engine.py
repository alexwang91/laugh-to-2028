import unittest

from research.brrk_crypto_cross_sectional_factor_atlas_0075.engine import (
    ExecutionAccounting,
    fractional_ranks,
    funding_7d,
    holm_adjust,
    invert_rank,
    perp_basis_1d,
    preprocess_rank,
    q1_q5_supported,
    replacement_fraction,
    terminal_classification,
)


class Stage4SyntheticMechanicsTest(unittest.TestCase):
    def test_rank_ties_and_inversion(self):
        vals = {f"S{i:02d}": float(i // 2) for i in range(20)}
        ranks = fractional_ranks(vals)
        self.assertEqual(ranks["S00"], ranks["S01"])
        inv = invert_rank(ranks)
        for k in ranks:
            self.assertAlmostEqual(ranks[k] + inv[k], 1.0)

    def test_preprocess_and_quintile_support(self):
        vals = {f"S{i:02d}": float(i) for i in range(20)}
        ranks = preprocess_rank(vals)
        self.assertTrue(q1_q5_supported(ranks))

    def test_missing_derivatives_remain_missing(self):
        self.assertIsNone(perp_basis_1d(None, 100.0))
        self.assertIsNone(funding_7d([0.01, -0.01], complete_coverage=False))

    def test_holm_is_monotone_in_sorted_order(self):
        raw = [0.01, 0.04, 0.02, 0.50]
        adjusted = holm_adjust(raw)
        ordered = sorted(zip(raw, adjusted))
        self.assertEqual([x[1] for x in ordered], sorted(x[1] for x in ordered))

    def test_replacement_fraction(self):
        self.assertEqual(replacement_fraction({"A", "B"}, {"A", "B"}), 0.0)
        self.assertEqual(replacement_fraction({"A", "B"}, {"C", "D"}), 1.0)

    def test_terminal_classifications(self):
        good = ExecutionAccounting(64, 0, 0, True, True, True)
        bad = ExecutionAccounting(63, 0, 0, True, True, True)
        self.assertEqual(terminal_classification(accounting=bad, any_qualified=False, support_possible=True, inference_defined=True), "INVALID_EXECUTION")
        self.assertEqual(terminal_classification(accounting=good, any_qualified=False, support_possible=False, inference_defined=True), "INCONCLUSIVE_INSUFFICIENT_SUPPORT")
        self.assertEqual(terminal_classification(accounting=good, any_qualified=False, support_possible=True, inference_defined=True), "FAIL_NO_QUALIFIED_FACTOR")
        self.assertEqual(terminal_classification(accounting=good, any_qualified=True, support_possible=True, inference_defined=True), "PASS")


if __name__ == "__main__":
    unittest.main()
