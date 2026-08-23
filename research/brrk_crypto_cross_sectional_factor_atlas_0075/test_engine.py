import unittest

from research.brrk_crypto_cross_sectional_factor_atlas_0075.engine import (
    ExecutionAccounting,
    amihud_20,
    drawdown_60,
    forward_return,
    fractional_ranks,
    funding_7d,
    holm_adjust,
    invert_rank,
    perp_basis_1d,
    preprocess_rank,
    q1_q5_supported,
    replacement_fraction,
    terminal_classification,
    volume_surprise_20,
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

    def test_forward_return_uses_only_endpoint_prices(self):
        self.assertAlmostEqual(forward_return(100.0, 110.0), 0.10)
        with self.assertRaises(ValueError):
            forward_return(0.0, 110.0)

    def test_drawdown_60_requires_exact_positive_window(self):
        closes = [100.0 + i for i in range(59)] + [120.0]
        self.assertAlmostEqual(drawdown_60(closes), 120.0 / 158.0 - 1.0)
        with self.assertRaises(ValueError):
            drawdown_60(closes[:-1])

    def test_volume_surprise_requires_prior_19_only(self):
        prior = [100.0] * 19
        self.assertAlmostEqual(volume_surprise_20(200.0, prior), 0.6931471805599453)
        with self.assertRaises(ValueError):
            volume_surprise_20(200.0, prior[:-1])

    def test_amihud_20_fails_closed_on_incomplete_or_zero_volume(self):
        returns = [0.01] * 20
        volumes = [1000.0] * 20
        self.assertAlmostEqual(amihud_20(returns, volumes), 0.00001)
        with self.assertRaises(ValueError):
            amihud_20(returns, volumes[:-1])
        bad_volumes = volumes.copy()
        bad_volumes[-1] = 0.0
        with self.assertRaises(ValueError):
            amihud_20(returns, bad_volumes)

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
        bad_trials = ExecutionAccounting(63, 0, 0, True, True, True)
        bad_identity = ExecutionAccounting(64, 0, 0, False, True, True)
        bad_lookahead = ExecutionAccounting(64, 0, 0, True, False, True)
        bad_persistence = ExecutionAccounting(64, 0, 0, True, True, False)
        self.assertEqual(terminal_classification(accounting=bad_trials, any_qualified=False, support_possible=True, inference_defined=True), "INVALID_EXECUTION")
        self.assertEqual(terminal_classification(accounting=bad_identity, any_qualified=False, support_possible=True, inference_defined=True), "INVALID_EXECUTION")
        self.assertEqual(terminal_classification(accounting=bad_lookahead, any_qualified=False, support_possible=True, inference_defined=True), "INVALID_EXECUTION")
        self.assertEqual(terminal_classification(accounting=bad_persistence, any_qualified=False, support_possible=True, inference_defined=True), "INVALID_EXECUTION")
        self.assertEqual(terminal_classification(accounting=good, any_qualified=False, support_possible=False, inference_defined=True), "INCONCLUSIVE_INSUFFICIENT_SUPPORT")
        self.assertEqual(terminal_classification(accounting=good, any_qualified=False, support_possible=True, inference_defined=True), "FAIL_NO_QUALIFIED_FACTOR")
        self.assertEqual(terminal_classification(accounting=good, any_qualified=True, support_possible=True, inference_defined=True), "PASS")


if __name__ == "__main__":
    unittest.main()
