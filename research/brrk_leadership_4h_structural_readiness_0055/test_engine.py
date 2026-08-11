from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from research.brrk_leadership_4h_structural_readiness_0055 import engine


class StructuralReadinessEngineContractTests(unittest.TestCase):
    @staticmethod
    def _synthetic_frames(n: int = 2400) -> dict[str, pd.DataFrame]:
        index = pd.date_range("2022-01-01T00:00:00Z", periods=n, freq="4h")
        t = np.arange(n, dtype=float)
        btc_log = 9.0 + 0.00020 * t + 0.010 * np.sin(t / 19.0) + 0.004 * np.cos(t / 7.0)
        eth_log = 4.0 + 0.00016 * t + 0.012 * np.sin(t / 23.0) + 0.003 * np.cos(t / 11.0)
        relative_step = 0.00004 + 0.00035 * np.sin(t / 13.0) + 0.00018 * np.cos(t / 29.0)
        z = 0.20 + np.cumsum(relative_step)
        sol_log = eth_log + z
        q_eth = 1_000_000.0 * np.exp(0.05 * np.sin(t / 31.0) + 0.01 * np.cos(t / 5.0))
        q_sol = 800_000.0 * np.exp(0.06 * np.cos(t / 37.0) + 0.015 * np.sin(t / 9.0))
        q_btc = 5_000_000.0 * np.exp(0.04 * np.sin(t / 41.0) + 0.01 * np.cos(t / 17.0))
        return {
            "BTCUSDT": pd.DataFrame({"close": np.exp(btc_log), "quote_volume": q_btc}, index=index),
            "ETHUSDT": pd.DataFrame({"close": np.exp(eth_log), "quote_volume": q_eth}, index=index),
            "SOLUSDT": pd.DataFrame({"close": np.exp(sol_log), "quote_volume": q_sol}, index=index),
        }

    @staticmethod
    def _direct_training_panel(n: int = 1500) -> pd.DataFrame:
        index = pd.date_range("2021-01-01T00:00:00Z", periods=n, freq="4h")
        i = np.arange(n, dtype=float)
        panel = pd.DataFrame(index=index)
        panel["TrendLevel"] = 0.55 * np.sin(i / 11.0) + 0.20 * np.cos(i / 23.0)
        panel["TrendAge"] = 0.45 * np.sin(i / 17.0) - 0.18 * np.cos(i / 31.0)
        panel["StateSupport"] = 0.50 * np.cos(i / 13.0) + 0.15 * np.sin(i / 29.0)
        panel["ELIGIBLE"] = True
        panel["FEATURE_VALID"] = True
        panel["TARGET_DEFINED"] = True
        panel["TARGET_ALLOWED"] = True
        panel["ORIGIN_POS"] = np.arange(n, dtype=int)
        panel["Y"] = (((np.arange(n) * 37 + 11) % 101) < 51).astype(float)
        return panel

    def test_structural_transform_exact_weights_and_antisymmetry(self) -> None:
        raw = np.asarray([0.8, 0.4, -0.2, -0.6, 0.9, 0.3, -0.3], dtype=float)
        actual = engine.structural_transform(raw)
        expected = np.asarray([
            (0.8 + 0.4 - 0.2 - 0.6) / 4.0,
            (3.0 * 0.8 + 0.4 - (-0.2) - 3.0 * (-0.6)) / 8.0,
            (0.9 + 0.3 - 0.3) / 3.0,
        ])
        np.testing.assert_allclose(actual, expected, rtol=0.0, atol=1e-15)
        np.testing.assert_allclose(engine.structural_transform(-raw), -actual, rtol=0.0, atol=1e-15)
        self.assertLessEqual(float(np.max(np.abs(actual))), 1.0)

    def test_structural_basis_weights_are_frozen_and_normalized(self) -> None:
        np.testing.assert_array_equal(engine.TREND_LEVEL_WEIGHTS, np.asarray([0.25] * 4))
        np.testing.assert_array_equal(engine.TREND_AGE_WEIGHTS, np.asarray([0.375, 0.125, -0.125, -0.375]))
        self.assertAlmostEqual(float(np.sum(engine.TREND_AGE_WEIGHTS)), 0.0, places=15)
        self.assertAlmostEqual(float(np.sum(np.abs(engine.TREND_AGE_WEIGHTS))), 1.0, places=15)
        np.testing.assert_allclose(engine.STATE_SUPPORT_WEIGHTS, np.asarray([1.0 / 3.0] * 3), rtol=0.0, atol=0.0)

    def test_training_probe_library_is_exact_13_by_3(self) -> None:
        q = engine.training_probe_library()
        self.assertEqual(q.shape, (13, 3))
        np.testing.assert_array_equal(q[0], np.zeros(3))
        self.assertEqual(len(np.unique(q, axis=0)), 13)
        self.assertTrue(np.all(np.count_nonzero(q[1:], axis=1) == 1))
        for j in range(3):
            values = sorted(float(x) for x in q[1:, j] if x != 0.0)
            self.assertEqual(values, [-1.0, -0.5, 0.5, 1.0])

    def test_type7_p90_is_exact_preregistered_interpolation(self) -> None:
        widths = np.arange(1.0, 14.0)
        actual = engine.type7_quantile(widths, 0.90)
        expected = 0.2 * 11.0 + 0.8 * 12.0
        self.assertAlmostEqual(actual, expected, places=15)
        self.assertAlmostEqual(actual, float(np.quantile(widths, 0.90, method="linear")), places=15)

    def test_bartlett_hac_matches_direct_manual_formula(self) -> None:
        scores = np.asarray([[1.0, 0.5, -0.2], [0.0, -0.5, 0.1], [2.0, 1.5, 0.7], [-1.0, 0.25, -0.4], [0.5, -1.25, 0.2], [1.5, 0.75, 0.8]], dtype=float)
        lag = 2
        centered = scores - scores.mean(axis=0, keepdims=True)
        manual = centered.T @ centered
        for k in range(1, lag + 1):
            weight = 1.0 - k / float(lag + 1)
            cross = centered[k:].T @ centered[:-k]
            manual += weight * (cross + cross.T)
        np.testing.assert_allclose(engine.bartlett_hac_sum(scores, lag), manual, rtol=0.0, atol=1e-12)

    def test_raw_panel_semantics_and_target_firewall_are_inherited(self) -> None:
        frames = self._synthetic_frames()
        panel = engine.build_methodology_panel(frames)
        raw = panel.loc[:, list(engine.RAW_FEATURE_COLUMNS)].to_numpy(dtype=float)
        struct = panel.loc[:, list(engine.FEATURE_COLUMNS)].to_numpy(dtype=float)
        mask = np.isfinite(raw).all(axis=1)
        np.testing.assert_allclose(struct[mask], engine.structural_transform(raw[mask]), rtol=0.0, atol=1e-14)
        forbidden = ~panel["TARGET_ALLOWED"].to_numpy(dtype=bool)
        self.assertFalse(panel.loc[forbidden, ["M", "Y"]].notna().to_numpy().any())
        reserved = panel.index >= engine.RESERVED_SUFFIX_START
        self.assertFalse(panel.loc[reserved, ["M", "Y"]].notna().to_numpy().any())
        self.assertFalse(panel.loc[reserved, "TARGET_ALLOWED"].any())

    def test_training_precision_refuses_samples_below_672(self) -> None:
        panel = self._direct_training_panel(900)
        record, model = engine.training_precision_at_refit(panel, 850)
        self.assertEqual(record.status, "INSUFFICIENT_FOR_HAC")
        self.assertFalse(record.passed)
        self.assertLess(record.matured_eligible_count, engine.NUMERICAL_FLOOR)
        self.assertIsNone(model)

    def test_training_precision_is_finite_above_floor_and_uses_13_probes(self) -> None:
        panel = self._direct_training_panel(1500)
        record, model = engine.training_precision_at_refit(panel, 1499)
        self.assertIsNotNone(model)
        self.assertGreaterEqual(record.matured_eligible_count, engine.NUMERICAL_FLOOR)
        self.assertIn(record.status, {"PASS", "PRECISION_TOO_WIDE"})
        self.assertEqual(len(record.probe_widths), 13)
        self.assertTrue(np.isfinite(np.asarray(record.probe_widths)).all())
        self.assertAlmostEqual(record.p90_width, engine.type7_quantile(record.probe_widths, 0.90), places=15)

    def test_calibration_semantics_are_identical_to_upstream(self) -> None:
        ts = pd.Timestamp("2022-10-01T00:00:00Z")
        n = 800
        eta = np.linspace(-2.0, 2.0, n)
        rng = np.random.default_rng(550055)
        p = 1.0 / (1.0 + np.exp(-0.65 * eta))
        y = rng.binomial(1, p).astype(float)
        a = engine.calibration_precision_from_pairs(ts, np.full(n, 0.5), eta, y)
        self.assertIsNotNone(a.gamma)
        self.assertEqual(len(a.probe_widths), 8)
        self.assertTrue(np.isfinite(np.asarray(a.probe_widths)).all())

    def test_readiness_requires_three_consecutive_passes(self) -> None:
        def rec(passed: bool) -> engine.TrainingPrecision:
            return engine.TrainingPrecision(
                "2022-01-01T00:00:00Z", 700, "PASS" if passed else "PRECISION_TOO_WIDE", passed,
                0.05 if passed else 0.15, 0.08 if passed else 0.25, tuple([0.05] * 13), 0.0, 1.0,
            )
        self.assertFalse(engine.consecutive_ready([rec(True), rec(True)]))
        self.assertTrue(engine.consecutive_ready([rec(True), rec(True), rec(True)]))
        self.assertFalse(engine.consecutive_ready([rec(True), rec(False), rec(True), rec(True)]))


if __name__ == "__main__":
    unittest.main()
