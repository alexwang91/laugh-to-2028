import unittest

from research.brrk_crypto_cross_sectional_factor_atlas_0075.engine import (
    fractional_ranks,
    preprocess_rank,
)
from research.brrk_crypto_cross_sectional_factor_atlas_0075.synthetic_qualification import (
    historical_membership,
    leave_size_bucket_robust,
    leave_year_robust,
    matured_forward_return,
    point_in_time_eligible,
    residualize_cross_section,
    spearman_from_ranks,
)


class Stage4FrozenObligationsTest(unittest.TestCase):
    def test_known_positive_negative_monotonic_and_null_factor(self):
        raw = {f"S{i:02d}": float(i) for i in range(20)}
        positive = fractional_ranks(raw)
        target = dict(positive)
        negative = {k: 1.0 - v for k, v in positive.items()}
        self.assertAlmostEqual(spearman_from_ranks(positive, target), 1.0)
        self.assertAlmostEqual(spearman_from_ranks(negative, target), -1.0)
        null = {f"S{i:02d}": float((i * 7) % 20) / 19.0 for i in range(20)}
        self.assertLess(abs(spearman_from_ranks(null, target)), 0.25)

    def test_insufficient_universe_stale_and_missing_rows_fail_closed(self):
        with self.assertRaises(ValueError):
            fractional_ranks({f"S{i}": float(i) for i in range(19)})
        valid_closes = [100.0] * 60
        quote = [2_000_000.0] * 30
        notional = [2_000_000.0] * 30
        self.assertFalse(point_in_time_eligible(
            listing_age_days=300,
            recent_closes=valid_closes,
            trailing_quote_volumes=quote,
            trailing_notional_volumes=notional,
            latest_close_is_t_minus_1=False,
        ))
        missing = valid_closes[:-1]
        self.assertFalse(point_in_time_eligible(
            listing_age_days=300,
            recent_closes=missing,
            trailing_quote_volumes=quote,
            trailing_notional_volumes=notional,
            latest_close_is_t_minus_1=True,
        ))

    def test_delisting_survival_is_not_future_conditioned(self):
        self.assertTrue(historical_membership(
            eligible_by_t_minus_1=True,
            has_valid_observation=True,
            future_survival=False,
        ))
        self.assertTrue(historical_membership(
            eligible_by_t_minus_1=True,
            has_valid_observation=True,
            future_survival=True,
        ))

    def test_maturity_exclusion_never_imputes_tail(self):
        self.assertIsNone(matured_forward_return([100.0] * 5, 5))
        self.assertAlmostEqual(matured_forward_return([100.0] * 5 + [110.0], 5), 0.10)
        self.assertIsNone(matured_forward_return([100.0] * 20, 20))

    def test_winsor_rank_determinism(self):
        values = {f"S{i:02d}": float(i) for i in range(20)}
        values["S19"] = 1_000_000.0
        first = preprocess_rank(values)
        second = preprocess_rank(dict(reversed(list(values.items()))))
        self.assertEqual(first, second)

    def test_residualization_requires_30_complete_and_removes_linear_controls(self):
        y = {f"S{i:02d}": 3.0 + 2.0 * i + (0.1 if i % 2 else -0.1) for i in range(30)}
        controls = {f"S{i:02d}": [float(i)] for i in range(30)}
        residuals = residualize_cross_section(y, controls)
        self.assertEqual(len(residuals), 30)
        self.assertAlmostEqual(sum(residuals.values()), 0.0, places=10)
        with self.assertRaises(ValueError):
            residualize_cross_section(dict(list(y.items())[:29]), dict(list(controls.items())[:29]))

    def test_leave_year_and_size_robustness(self):
        self.assertTrue(leave_year_robust(0.10, [0.06, 0.05, 0.08, 0.07]))
        self.assertFalse(leave_year_robust(0.10, [0.06, -0.05, 0.08, 0.07]))
        self.assertFalse(leave_year_robust(0.10, [0.02, 0.03, 0.04]))
        self.assertTrue(leave_size_bucket_robust(-0.10, [-0.08, -0.06, -0.09]))
        self.assertFalse(leave_size_bucket_robust(-0.10, [-0.08, 0.06, -0.09]))


if __name__ == "__main__":
    unittest.main()
