from __future__ import annotations

import math
import unittest

import numpy as np
import pandas as pd

from research.brrk_beta_deterioration_btc_takeover_diagnostic_0059 import engine


def frozen_synthetic_frames() -> dict[str, pd.DataFrame]:
    idx = pd.date_range("2020-08-11", "2026-08-02", freq="D")
    x = np.arange(len(idx), dtype=np.float64)
    return {
        "BTC": pd.DataFrame(
            {"close": 100.0 * np.exp(0.0004 * x + 0.04 * np.sin(x / 17.0) + 0.02 * np.sin(x / 53.0))},
            index=idx,
        ),
        "ETH": pd.DataFrame(
            {"close": 80.0 * np.exp(0.0006 * x + 0.06 * np.sin(x / 13.0 + 0.4) + 0.03 * np.sin(x / 47.0))},
            index=idx,
        ),
        "SOL": pd.DataFrame(
            {"close": 20.0 * np.exp(0.0008 * x + 0.08 * np.sin(x / 11.0 + 0.7) + 0.04 * np.sin(x / 41.0))},
            index=idx,
        ),
    }


class Test0059Engine(unittest.TestCase):
    def test_constants_match_preregistration(self) -> None:
        self.assertEqual(engine.HORIZONS, (20, 60, 120, 240))
        self.assertEqual(engine.FAST_WEIGHTS, (0.15, 0.25, 0.30, 0.30))
        self.assertEqual(engine.SLOW_WEIGHTS, (0.10, 0.20, 0.30, 0.40))
        self.assertEqual(engine.D2_HIGH_WINDOW, 60)
        self.assertEqual(engine.CAUSAL_Z_WINDOW, 252)
        self.assertEqual(engine.CAUSAL_Z_MIN_PERIODS, 60)
        self.assertEqual(engine.MIN_SHARED_ORIGINS, 1440)
        self.assertEqual(engine.BOOTSTRAP_BLOCK_LENGTH, 240)
        self.assertEqual(engine.BOOTSTRAP_REPLICATES, 10_000)
        self.assertEqual(engine.BOOTSTRAP_SEED, 1_844_716_895)

    def test_payload_identity_guard(self) -> None:
        engine.validate_payload_identity(engine.EXPECTED_PAYLOAD_SHA256)
        with self.assertRaises(engine.DiagnosticProtocolError):
            engine.validate_payload_identity("0" * 64)

    def test_frozen_calendar_accepts_tz_naive_and_rejects_tz_aware(self) -> None:
        frames = frozen_synthetic_frames()
        prices = engine.validate_price_frames(frames, require_frozen_calendar=True)
        self.assertEqual(len(prices), 2183)
        self.assertIsNone(prices.index.tz)
        aware = {asset: frame.copy() for asset, frame in frames.items()}
        for frame in aware.values():
            frame.index = frame.index.tz_localize("UTC")
        with self.assertRaises(engine.DiagnosticProtocolError):
            engine.validate_price_frames(aware, require_frozen_calendar=True)

    def test_price_validation_rejects_alignment_and_nonpositive_mutations(self) -> None:
        frames = frozen_synthetic_frames()
        bad = {asset: frame.copy() for asset, frame in frames.items()}
        bad["SOL"] = bad["SOL"].iloc[:-1]
        with self.assertRaises(engine.DiagnosticProtocolError):
            engine.validate_price_frames(bad, require_frozen_calendar=True)
        bad2 = {asset: frame.copy() for asset, frame in frames.items()}
        bad2["ETH"].iloc[20, 0] = 0.0
        with self.assertRaises(engine.DiagnosticProtocolError):
            engine.validate_price_frames(bad2, require_frozen_calendar=True)

    def test_trend_score_matches_hash_bound_0047_semantics(self) -> None:
        idx = pd.date_range("2020-01-01", periods=400, freq="D")
        x = np.arange(len(idx), dtype=float)
        price = pd.Series(100.0 * np.exp(0.001 * x + 0.05 * np.sin(x / 19.0)), index=idx)
        actual = engine.trend_score(price, engine.FAST_WEIGHTS)
        lr = np.log(price).diff()
        expected = pd.Series(0.0, index=idx, dtype=float)
        valid = pd.Series(True, index=idx)
        for h, w in zip(engine.HORIZONS, engine.FAST_WEIGHTS):
            momentum = np.log(price / price.shift(h))
            scale = lr.rolling(h).std() * math.sqrt(h)
            component = np.tanh(momentum / scale)
            expected = expected + w * component
            valid &= component.notna()
        expected = expected.where(valid)
        np.testing.assert_allclose(
            actual.to_numpy(),
            expected.to_numpy(),
            rtol=0.0,
            atol=1e-15,
            equal_nan=True,
        )

    def test_causal_z_matches_hash_bound_0043_semantics(self) -> None:
        idx = pd.date_range("2020-01-01", periods=500, freq="D")
        x = pd.Series(np.sin(np.arange(500) / 23.0) + np.arange(500) / 700.0, index=idx)
        actual = engine.causal_z(x)
        mean = x.rolling(252, min_periods=60).mean()
        std = x.rolling(252, min_periods=60).std().replace(0.0, np.nan)
        expected = ((x - mean) / std).clip(-3.0, 3.0)
        np.testing.assert_allclose(
            actual.to_numpy(),
            expected.to_numpy(),
            rtol=0.0,
            atol=1e-15,
            equal_nan=True,
        )

    def test_state_representation_is_exact_equal_weight_beta_and_relative(self) -> None:
        frames = frozen_synthetic_frames()
        prices = engine.validate_price_frames(frames, require_frozen_calendar=True)
        panel = engine.build_state_panel(prices)
        b = 0.5 * np.log(prices["ETH"]) + 0.5 * np.log(prices["SOL"])
        z = b - np.log(prices["BTC"])
        np.testing.assert_allclose(panel["b_log_beta"], b, rtol=0.0, atol=1e-15)
        np.testing.assert_allclose(panel["z_log_beta_over_btc"], z, rtol=0.0, atol=1e-15)
        np.testing.assert_allclose(
            panel["S"],
            panel[["D1_z", "D2_z", "D3_z"]].mean(axis=1, skipna=False),
            rtol=0.0,
            atol=1e-15,
            equal_nan=True,
        )

    def test_d2_is_positive_log_distance_below_trailing_60_high(self) -> None:
        frames = frozen_synthetic_frames()
        prices = engine.validate_price_frames(frames, require_frozen_calendar=True)
        panel = engine.build_state_panel(prices)
        B = np.exp(0.5 * np.log(prices["ETH"]) + 0.5 * np.log(prices["SOL"]))
        expected = np.log(B.rolling(60, min_periods=60).max() / B)
        np.testing.assert_allclose(panel["D2_raw"], expected, rtol=0.0, atol=1e-15, equal_nan=True)
        self.assertGreaterEqual(float(panel["D2_raw"].dropna().min()), -1e-15)

    def test_target_is_origin_reset_arithmetic_50_50_beta_not_geometric(self) -> None:
        idx = pd.date_range("2020-01-01", periods=300, freq="D")
        x = np.arange(300, dtype=float)
        prices = pd.DataFrame(
            {
                "BTC": 10.0 * np.exp(0.001 * x),
                "ETH": 20.0 * np.exp(0.002 * x),
                "SOL": 30.0 * np.exp(-0.0005 * x),
            },
            index=idx,
        )
        target = engine.build_target_panel(prices)
        h = 20
        expected_beta = 0.5 * (prices["ETH"].iloc[h] / prices["ETH"].iloc[0]) + 0.5 * (
            prices["SOL"].iloc[h] / prices["SOL"].iloc[0]
        )
        geometric_substitute = math.sqrt(
            (prices["ETH"].iloc[h] / prices["ETH"].iloc[0])
            * (prices["SOL"].iloc[h] / prices["SOL"].iloc[0])
        )
        self.assertAlmostEqual(float(target["WBETA_20"].iloc[0]), float(expected_beta))
        self.assertNotAlmostEqual(float(expected_beta), float(geometric_substitute), places=12)

    def test_shared_origin_calendar_is_exact_nominal_1644(self) -> None:
        frames = frozen_synthetic_frames()
        prices = engine.validate_price_frames(frames, require_frozen_calendar=True)
        panel = engine.build_shared_origin_panel(prices)
        self.assertEqual(len(panel), 1644)
        self.assertEqual(panel.iloc[0]["origin_date"], "2021-06-06T00:00:00Z")
        self.assertEqual(panel.iloc[-1]["origin_date"], "2025-12-05T00:00:00Z")
        self.assertEqual(tuple(panel.columns), engine.ORIGIN_PANEL_FIELDS)

    def test_chronological_partition_is_four_equal_as_possible_blocks(self) -> None:
        ids = engine._block_ids(1644)
        self.assertEqual([int(np.sum(ids == i)) for i in range(1, 5)], [411, 411, 411, 411])
        ids2 = engine._block_ids(1646)
        self.assertEqual([int(np.sum(ids2 == i)) for i in range(1, 5)], [412, 412, 411, 411])

    def test_spearman_uses_average_ties_and_constant_is_undefined(self) -> None:
        x = [1.0, 1.0, 2.0, 3.0]
        self.assertAlmostEqual(engine.spearman_rho(x, x), 1.0)
        self.assertAlmostEqual(engine.spearman_rho(x, [-1.0, -1.0, -2.0, -3.0]), -1.0)
        self.assertTrue(math.isnan(engine.spearman_rho([1.0, 1.0, 1.0], [1.0, 2.0, 3.0])))

    def test_component_redundancy_effective_rank_is_descriptive(self) -> None:
        n = 100
        base = np.arange(n, dtype=float)
        panel = pd.DataFrame(
            {
                "D1_z": base,
                "D2_z": base,
                "D3_z": -base,
            }
        )
        matrix, eigenvalues, effective_rank = engine.component_redundancy(panel)
        self.assertEqual(matrix[0][1], 1.0)
        self.assertEqual(matrix[0][2], -1.0)
        self.assertIsNotNone(eigenvalues)
        self.assertAlmostEqual(float(effective_rank), 1.0, places=12)

    def test_moving_block_bootstrap_is_seed_deterministic(self) -> None:
        s = np.arange(80, dtype=float)
        targets = np.column_stack([s, s**2, -s, np.sin(s / 9.0)])
        a = engine._bootstrap_rhos(s, targets, block_length=20, replicates=25, seed=123)
        b = engine._bootstrap_rhos(s, targets, block_length=20, replicates=25, seed=123)
        c = engine._bootstrap_rhos(s, targets, block_length=20, replicates=25, seed=124)
        np.testing.assert_allclose(a, b, rtol=0.0, atol=0.0)
        self.assertFalse(np.array_equal(a, c))

    def test_classification_precedence_is_frozen(self) -> None:
        self.assertEqual(
            engine.classification_from_gates(g1=False, g2=True, g3=True, g4=True),
            "FAIL_INSUFFICIENT_CAUSAL_SUPPORT",
        )
        self.assertEqual(
            engine.classification_from_gates(g1=True, g2=False, g3=True, g4=True),
            "FAIL_NO_MONOTONE_CONTINUATION_INFORMATION",
        )
        self.assertEqual(
            engine.classification_from_gates(g1=True, g2=True, g3=False, g4=True),
            "FAIL_TEMPORAL_INSTABILITY",
        )
        self.assertEqual(
            engine.classification_from_gates(g1=True, g2=True, g3=True, g4=False),
            "FAIL_DEPENDENCE_AWARE_ROBUSTNESS",
        )
        self.assertEqual(
            engine.classification_from_gates(g1=True, g2=True, g3=True, g4=True),
            "PASS_MECHANISM_INFORMATION_STAGE_ELIGIBLE",
        )

    def test_full_frozen_calendar_synthetic_contract_is_lossless(self) -> None:
        result = engine.evaluate_frozen_contract(
            frozen_synthetic_frames(),
            engine.EXPECTED_PAYLOAD_SHA256,
        )
        self.assertEqual(result["shared_origin_count"], 1644)
        self.assertEqual(result["shared_origin_start"], "2021-06-06T00:00:00Z")
        self.assertEqual(result["shared_origin_end"], "2025-12-05T00:00:00Z")
        self.assertEqual(len(result["origin_panel"]), 1644)
        self.assertEqual(set(result["full_sample_rho_by_horizon"]), {"20", "60", "120", "240"})
        self.assertEqual(len(result["temporal_block_rho_by_horizon"]), 4)
        self.assertIsNotNone(result["bootstrap_q95"])
        self.assertEqual(set(result["simultaneous_lcb_by_horizon"]), {"20", "60", "120", "240"})
        self.assertEqual(result["actual_variants_evaluated"], 1)
        self.assertEqual(result["classification"], "FAIL_NO_MONOTONE_CONTINUATION_INFORMATION")
        self.assertFalse(result["authority"]["production_authorized"])

    def test_no_market_loader_network_or_portfolio_surface_is_present(self) -> None:
        forbidden = (
            "requests",
            "urllib",
            "open(",
            "read_text(",
            "read_bytes(",
            "frames_from_market_evidence",
            "fetch_daily",
            "transaction_cost",
            "turnover",
            "cagr",
            "mdd",
            "hysteresis",
            "allocation_weight",
        )
        with open(engine.__file__, "r", encoding="utf-8") as handle:
            source = handle.read().lower()
        for token in forbidden:
            self.assertNotIn(token.lower(), source)


if __name__ == "__main__":
    unittest.main()
