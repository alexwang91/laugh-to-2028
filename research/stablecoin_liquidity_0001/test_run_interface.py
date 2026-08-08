from __future__ import annotations

import math
import random
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from research.stablecoin_liquidity_0001.data_contract import SourcePoint
from research.stablecoin_liquidity_0001.run_interface import (
    BASELINE_FEATURE_ORDER,
    FIRST_RELEASE_FIELDS,
    MIN_PASS_OOS,
    PRIMARY_HAC_LAG,
    RESEARCH_ID,
    RUN_INTERFACE_ID,
    RunInterfaceError,
    canonical_daily_net_return,
    claim_run_once,
    classify_primary_result,
    eligible_training_decisions,
    flatten_canonical_brrk_state,
    forward_20d_label,
    hac_newey_west_one_sided,
    stablecoin_feature_for_decision,
    validate_first_release,
    validate_run_interface_contract,
)


def _dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


def _synthetic_brrk_state() -> dict[str, object]:
    return {
        "target_weights": {"BTC": 0.4, "ETH": 0.2, "SOL": 0.1, "BNB": 0.0},
        "cash_share": 0.3,
        "base_gross_target": 0.7,
        "risk_state_probabilities": {
            "RISK_OFF": 0.1,
            "BTC_LEAD": 0.2,
            "MAJOR_ROTATION": 0.3,
            "ALT_EXPANSION": 0.4,
        },
        "meta_scale": 0.8,
        "defensive_scale": 0.9,
        "feature_snapshot": {
            "regime_features": {
                "btc_trend": 0.11,
                "log_btc_rv30": -0.7,
                "btc_drawdown_252": -0.2,
                "major_breadth": 0.5,
                "alt_breadth": 0.4,
                "rel_strength_mean": 0.03,
                "rel_strength_dispersion": 0.08,
                "avg_corr30_btc": 0.65,
            },
            "v1": {
                "raw_gross_before_defense": 0.78,
                "raw_weights": {"BTC": 0.45, "ETH": 0.22, "SOL": 0.11, "BNB": 0.0},
                "btc_beta": 0.88,
                "btc_trend": 0.12,
                "btc_vol": 0.55,
                "scores": {"ETH": 0.2, "SOL": 0.3, "BNB": -0.1},
                "asset_trends": {"BTC": 0.12, "ETH": 0.2, "SOL": 0.25, "BNB": -0.05},
            },
        },
        "account_equity_usd": 10000.0,
        "current_positions_notional_usd": {"BTC": 123.0},
        "risk_state": "ALT_EXPANSION",
        "data_digest": "ignored",
    }


class RunInterfaceTests(unittest.TestCase):
    def test_contract_identity(self) -> None:
        validate_run_interface_contract()
        self.assertEqual(len(BASELINE_FEATURE_ORDER), 35)

    def test_baseline_state_extraction_has_exact_frozen_order(self) -> None:
        vector = flatten_canonical_brrk_state(_synthetic_brrk_state())
        self.assertEqual(len(vector), len(BASELINE_FEATURE_ORDER))
        self.assertEqual(vector[0:4], (0.4, 0.2, 0.1, 0.0))
        self.assertEqual(vector[4], 0.3)
        self.assertEqual(vector[6:10], (0.1, 0.2, 0.3, 0.4))
        self.assertAlmostEqual(vector[-1], -0.05)
        self.assertNotIn(10000.0, vector)
        self.assertNotIn(123.0, vector)

    def test_stablecoin_decision_alignment_is_exact_lag2_and_exact_20_40_day_lags(self) -> None:
        decision = _dt(2026, 8, 1)
        metric = decision - timedelta(days=2)
        points = [
            SourcePoint(metric - timedelta(days=40), 100.0),
            SourcePoint(metric - timedelta(days=20), 110.0),
            SourcePoint(metric, 121.0),
        ]
        feature = stablecoin_feature_for_decision(points, decision)
        self.assertIsNotNone(feature)
        assert feature is not None
        self.assertEqual(feature.metric_timestamp, metric)
        expected_growth = math.log(121.0) - math.log(110.0)
        expected_prior = math.log(110.0) - math.log(100.0)
        self.assertAlmostEqual(feature.growth_20d, expected_growth)
        self.assertAlmostEqual(feature.acceleration_20d, expected_growth - expected_prior)

        missing_exact = [points[0], SourcePoint(metric - timedelta(days=19), 110.0), points[2]]
        self.assertIsNone(stablecoin_feature_for_decision(missing_exact, decision))

    def test_daily_net_return_uses_target_for_same_decision_day_and_l1_turnover_cost(self) -> None:
        target = {"BTC": 0.5, "ETH": 0.2, "SOL": 0.0, "BNB": 0.0}
        previous = {"BTC": 0.4, "ETH": 0.1, "SOL": 0.0, "BNB": 0.0}
        returns = {"BTC": 0.02, "ETH": -0.01, "SOL": 0.03, "BNB": 0.0}
        actual = canonical_daily_net_return(target, previous, returns)
        gross_component = 0.5 * 0.02 + 0.2 * -0.01
        turnover = 0.1 + 0.1
        expected = gross_component - turnover * 5.0 / 10000.0
        self.assertAlmostEqual(actual, expected)

    def test_forward_label_requires_exact_twenty_calendar_days(self) -> None:
        decision = _dt(2026, 1, 1)
        daily = {decision + timedelta(days=i): 0.001 for i in range(20)}
        self.assertAlmostEqual(forward_20d_label(daily, decision), (1.001**20) - 1.0)
        del daily[decision + timedelta(days=11)]
        self.assertIsNone(forward_20d_label(daily, decision))

    def test_label_purge_requires_full_realization_before_training_use(self) -> None:
        prediction = _dt(2026, 3, 1)
        prior = [prediction - timedelta(days=19), prediction - timedelta(days=20), prediction - timedelta(days=21)]
        eligible = eligible_training_decisions(prior, prediction)
        self.assertEqual(eligible, (prediction - timedelta(days=21), prediction - timedelta(days=20)))

    def test_hac_and_primary_classification_pass_on_strong_positive_synthetic_differentials(self) -> None:
        rng = random.Random(20260808)
        values = [0.01 + rng.gauss(0.0, 0.004) for _ in range(MIN_PASS_OOS)]
        hac = hac_newey_west_one_sided(values)
        self.assertEqual(hac.n, MIN_PASS_OOS)
        self.assertGreater(hac.mean, 0.0)
        self.assertIsNotNone(hac.one_sided_p_value)
        assert hac.one_sided_p_value is not None
        self.assertLess(hac.one_sided_p_value, 0.05)
        self.assertEqual(classify_primary_result(hac), "PASS_INCREMENTAL_INFORMATION")

    def test_nonpositive_mean_is_fail_even_if_hac_is_degenerate(self) -> None:
        hac = hac_newey_west_one_sided([-0.01] * MIN_PASS_OOS)
        self.assertLessEqual(hac.mean, 0.0)
        self.assertEqual(classify_primary_result(hac), "FAIL_NO_INCREMENTAL_INFORMATION")

    def test_positive_but_underpowered_is_inconclusive(self) -> None:
        values = [0.01 + (0.001 if i % 2 else -0.001) for i in range(100)]
        hac = hac_newey_west_one_sided(values)
        self.assertEqual(classify_primary_result(hac), "INCONCLUSIVE")

    def test_first_release_rejects_extra_secondary_or_prediction_fields(self) -> None:
        payload = {
            "research_id": RESEARCH_ID,
            "run_interface_id": RUN_INTERFACE_ID,
            "classification": "INCONCLUSIVE",
            "valid_oos_prediction_count": 700,
            "mean_primary_loss_differential": 0.001,
            "hac_max_lag": PRIMARY_HAC_LAG,
            "hac_test_statistic": 1.2,
            "hac_one_sided_p_value": 0.11,
            "primary_result_digest": "a" * 64,
        }
        self.assertEqual(set(payload), set(FIRST_RELEASE_FIELDS))
        validate_first_release(payload)
        payload["predictions_table"] = []
        with self.assertRaisesRegex(RunInterfaceError, "exactly the frozen primary fields"):
            validate_first_release(payload)

    def test_stage1_claim_is_create_only_and_token_gated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "RUN_ONCE_STAGE1.marker"
            with self.assertRaisesRegex(RunInterfaceError, "invalid Stage-1 execution token"):
                claim_run_once(marker, "wrong")
            self.assertFalse(marker.exists())
            claim_run_once(marker, "[STABLECOIN_STAGE1_EXECUTE_V1]")
            self.assertTrue(marker.exists())
            with self.assertRaises(FileExistsError):
                claim_run_once(marker, "[STABLECOIN_STAGE1_EXECUTE_V1]")


if __name__ == "__main__":
    unittest.main()
