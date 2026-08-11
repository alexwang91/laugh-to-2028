from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from research.brrk_leadership_intraday_support_0053 import support_funnel as sf


class TestSupportFunnel(unittest.TestCase):
    def test_trend_score_matches_direct_formula(self):
        idx = pd.date_range("2020-01-01", periods=1800, freq="4h", tz="UTC")
        x = np.arange(len(idx), dtype=float)
        price = pd.Series(np.exp(0.0002 * x + 0.02 * np.sin(x / 17.0)), index=idx)
        got = sf.trend_score_4h(price)
        t = 1700
        logp = np.log(price.to_numpy())
        lr = np.diff(logp)
        expected = 0.0
        for h, w in zip(sf.HORIZONS_4H, sf.FAST_WEIGHTS):
            momentum = logp[t] - logp[t - h]
            # pandas rolling(h).std at t uses the h log returns ending at t.
            returns = lr[t - h : t]
            scale = float(np.std(returns, ddof=1) * math.sqrt(h))
            expected += w * math.tanh(momentum / scale)
        self.assertAlmostEqual(float(got.iloc[t]), expected, places=12)
        self.assertTrue(got.iloc[: sf.MAX_FEATURE_HISTORY_BARS].isna().all())
        self.assertTrue(pd.notna(got.iloc[sf.MAX_FEATURE_HISTORY_BARS]))

    def test_measure_track_preserves_maturity_and_refit_clock(self):
        idx = pd.date_range("2020-01-01", periods=1400, freq="4h", tz="UTC")
        eligible = np.ones(len(idx), dtype=bool)
        spec = sf.TrackSpec("X", training_support=3, shadow_support=2, block_length=10, authority="TEST")
        result = sf.measure_track(idx, eligible, spec)
        # Training support: at t=338, origins 0,1,2 are matured by 336 bars.
        self.assertEqual(result.first_training_support_timestamp, sf._iso(idx[338]))
        # Two shadow origins 338,339 are both matured by t=675.
        self.assertEqual(result.first_shadow_support_satisfied_timestamp, sf._iso(idx[675]))
        # Frozen 168-bar refit grid is anchored at 338: 338,506,674,842,...
        # t=674 is one bar too early for the second shadow maturity; activation is 842.
        self.assertEqual(result.calibration_activation_refit_timestamp, sf._iso(idx[842]))
        # Formal rows must also retain a full 336-bar future maturity window.
        expected_positions = np.arange(842, len(idx) - sf.MAX_TARGET_MATURITY_BARS)
        self.assertEqual(result.formal_rows, len(expected_positions))
        self.assertEqual(result.complete_blocks, len(expected_positions) // 10)
        self.assertEqual(result.trailing_partial_rows, len(expected_positions) % 10)
        self.assertEqual(result.first_formal_origin_timestamp, sf._iso(idx[842]))
        self.assertEqual(result.last_formal_origin_timestamp, sf._iso(idx[len(idx) - 337]))

    def test_ineligible_rows_do_not_count_toward_burnin(self):
        idx = pd.date_range("2020-01-01", periods=1600, freq="4h", tz="UTC")
        eligible = np.zeros(len(idx), dtype=bool)
        eligible[::2] = True
        spec = sf.TrackSpec("X", training_support=3, shadow_support=2, block_length=10, authority="TEST")
        result = sf.measure_track(idx, eligible, spec)
        # By t=340 the matured cutoff is 4 and eligible matured rows are 0,2,4.
        self.assertEqual(result.first_training_support_timestamp, sf._iso(idx[340]))
        self.assertIsNotNone(result.calibration_activation_refit_timestamp)
        self.assertLess(result.formal_rows, len(idx))

    def test_no_training_support_returns_zero_formal_rows(self):
        idx = pd.date_range("2020-01-01", periods=800, freq="4h", tz="UTC")
        eligible = np.zeros(len(idx), dtype=bool)
        eligible[500:] = True
        spec = sf.TrackSpec("X", training_support=400, shadow_support=2, block_length=10, authority="TEST")
        result = sf.measure_track(idx, eligible, spec)
        self.assertIsNone(result.first_training_support_timestamp)
        self.assertEqual(result.formal_rows, 0)
        self.assertEqual(result.complete_blocks, 0)

    def test_primary_classification_uses_track_a_only(self):
        dummy = sf.FunnelMeasurement(
            research_id=sf.RESEARCH_ID,
            payload_sha256=sf.EXPECTED_PAYLOAD_SHA256,
            common_start="2020-01-01T00:00:00Z",
            common_end="2021-01-01T00:00:00Z",
            raw_common_bars=100,
            feature_valid_bars=50,
            eligible_feature_valid_bars=25,
            pre_formal_eligibility_rate=0.5,
            max_feature_history_bars=1440,
            max_target_maturity_bars=336,
            refit_bars=168,
            tracks={
                "A": sf.TrackSupportResult("A", "PRIMARY", 2190, 2190, 336, None, None, None, None, None, None, 4032, 12, 0, None, None),
                "B": sf.TrackSupportResult("B", "DIAG", 365, 365, 56, None, None, None, None, None, None, 0, 0, 0, None, None),
                "C": sf.TrackSupportResult("C", "DIAG", 365, 365, 336, None, None, None, None, None, None, 0, 0, 0, None, None),
            },
        )
        self.assertEqual(sf.classify_track_a(dummy), "PASS_4H_CALENDAR_EQUIVALENT_SUPPORT_FEASIBLE")
        failed = sf.FunnelMeasurement(**{**dummy.__dict__, "tracks": {**dummy.tracks, "A": sf.TrackSupportResult("A", "PRIMARY", 2190, 2190, 336, None, None, None, None, None, None, 3695, 10, 335, None, None)}})
        self.assertEqual(sf.classify_track_a(failed), "FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT")

    def test_loader_fails_closed_on_wrong_payload_hash(self):
        fake = {"interval": "4h", "start_ms": 0, "end_exclusive_ms": 1, "symbols": {s: [] for s in sf.SYMBOLS}}
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "payload.json"
            p.write_text(json.dumps(fake, sort_keys=True, separators=(",", ":")))
            with self.assertRaises(sf.SupportProtocolError):
                sf.load_frozen_payload(p)

    def test_no_result_artifacts_exist_at_implementation_stage(self):
        here = Path(__file__).resolve().parent
        for name in ["SUPPORT_RESULT.json", "PRIMARY_RESULT.json", "RESULT_SUMMARY.json", "EXECUTION.json", "RUN_ONCE.marker"]:
            self.assertFalse((here / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
