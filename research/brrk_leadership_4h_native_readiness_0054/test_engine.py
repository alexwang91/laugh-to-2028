from __future__ import annotations

import math
import unittest

import numpy as np
import pandas as pd

from research.brrk_leadership_4h_native_readiness_0054 import engine


class ReadinessEngineContractTests(unittest.TestCase):
    @staticmethod
    def _synthetic_frames(n: int = 2400) -> dict[str, pd.DataFrame]:
        index = pd.date_range("2022-01-01T00:00:00Z", periods=n, freq="4h")
        t = np.arange(n, dtype=float)

        btc_log = 9.0 + 0.00020 * t + 0.010 * np.sin(t / 19.0) + 0.004 * np.cos(t / 7.0)
        eth_log = 4.0 + 0.00016 * t + 0.012 * np.sin(t / 23.0) + 0.003 * np.cos(t / 11.0)
        # Deliberately make SOL/ETH relative returns non-constant so the 1440-bar
        # relative-volatility denominator is identified.
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
        for j, name in enumerate(engine.FEATURE_COLUMNS, start=1):
            panel[name] = 0.60 * np.sin(i / (7.0 + j)) + 0.25 * np.cos(i / (13.0 + 2.0 * j))
        panel["ELIGIBLE"] = True
        panel["FEATURE_VALID"] = True
        panel["TARGET_DEFINED"] = True
        panel["TARGET_ALLOWED"] = True
        panel["ORIGIN_POS"] = np.arange(n, dtype=int)
        # Deterministic non-separable binary labels with both classes recurring.
        panel["Y"] = (((np.arange(n) * 37 + 11) % 101) < 51).astype(float)
        return panel

    def test_training_probe_library_is_exact_29_by_7(self) -> None:
        q = engine.training_probe_library()
        self.assertEqual(q.shape, (29, 7))
        np.testing.assert_array_equal(q[0], np.zeros(7))
        self.assertEqual(len(np.unique(q, axis=0)), 29)
        nonzero = q[1:]
        self.assertTrue(np.all(np.count_nonzero(nonzero, axis=1) == 1))
        self.assertEqual(set(np.unique(np.abs(nonzero))), {0.0, 0.5, 1.0})
        for j in range(7):
            values = sorted(float(x) for x in nonzero[:, j] if x != 0.0)
            self.assertEqual(values, [-1.0, -0.5, 0.5, 1.0])

    def test_calibration_probe_library_is_exact(self) -> None:
        np.testing.assert_array_equal(
            engine.calibration_probe_library(),
            np.asarray([-2.0, -1.0, -0.5, -0.2, 0.2, 0.5, 1.0, 2.0]),
        )

    def test_bartlett_hac_matches_direct_manual_formula(self) -> None:
        scores = np.asarray(
            [
                [1.0, 0.5],
                [0.0, -0.5],
                [2.0, 1.5],
                [-1.0, 0.25],
                [0.5, -1.25],
                [1.5, 0.75],
            ],
            dtype=float,
        )
        lag = 2
        centered = scores - scores.mean(axis=0, keepdims=True)
        manual = centered.T @ centered
        for k in range(1, lag + 1):
            weight = 1.0 - k / float(lag + 1)
            cross = centered[k:].T @ centered[:-k]
            manual = manual + weight * (cross + cross.T)
        actual = engine.bartlett_hac_sum(scores, lag=lag)
        np.testing.assert_allclose(actual, manual, rtol=0.0, atol=1e-12)
        np.testing.assert_allclose(actual, actual.T, rtol=0.0, atol=1e-12)

    def test_wrong_payload_hash_fails_closed_without_market_read(self) -> None:
        with self.assertRaises(engine.ReadinessProtocolError):
            engine._validate_payload_bytes(b"{}")

    def test_feature_bucket_indexing_matches_preregistered_direct_sums(self) -> None:
        frames = self._synthetic_frames()
        panel = engine.build_methodology_panel(frames)
        pos = 1800
        z = np.log(frames["SOLUSDT"]["close"].to_numpy()) - np.log(frames["ETHUSDT"]["close"].to_numpy())
        d = np.empty_like(z)
        d[0] = np.nan
        d[1:] = np.diff(z)
        sigma = float(np.std(d[pos - 1439 : pos + 1], ddof=1))
        denom = sigma + engine.EPSILON
        expected = {
            "K1": math.tanh(float(np.sum(d[pos - 119 : pos + 1])) / (denom * math.sqrt(120.0))),
            "K2": math.tanh(float(np.sum(d[pos - 359 : pos - 119])) / (denom * math.sqrt(240.0))),
            "K3": math.tanh(float(np.sum(d[pos - 719 : pos - 359])) / (denom * math.sqrt(360.0))),
            "K4": math.tanh(float(np.sum(d[pos - 1439 : pos - 719])) / (denom * math.sqrt(720.0))),
        }
        for name, value in expected.items():
            self.assertAlmostEqual(float(panel.iloc[pos][name]), value, places=12)

    def test_target_firewall_never_materializes_post_cutoff_labels(self) -> None:
        frames = self._synthetic_frames()
        panel = engine.build_methodology_panel(frames)
        forbidden = ~panel["TARGET_ALLOWED"].to_numpy(dtype=bool)
        self.assertFalse(panel.loc[forbidden, ["M", "Y"]].notna().to_numpy().any())
        reserved = panel.index >= engine.RESERVED_SUFFIX_START
        self.assertFalse(panel.loc[reserved, ["M", "Y"]].notna().to_numpy().any())
        self.assertFalse(panel.loc[reserved, "TARGET_ALLOWED"].any())

        allowed_pos = np.flatnonzero(panel["TARGET_ALLOWED"].to_numpy(dtype=bool))
        self.assertGreater(len(allowed_pos), 0)
        last = int(allowed_pos[-1])
        self.assertLessEqual(pd.Timestamp(panel.index[last + engine.MAX_TARGET_BARS]), engine.METHOD_TARGET_END)
        if last + 1 + engine.MAX_TARGET_BARS < len(panel):
            self.assertGreater(pd.Timestamp(panel.index[last + 1 + engine.MAX_TARGET_BARS]), engine.METHOD_TARGET_END)

    def test_training_precision_refuses_samples_below_672(self) -> None:
        panel = self._direct_training_panel(900)
        record, model = engine.training_precision_at_refit(panel, 850)
        self.assertEqual(record.status, "INSUFFICIENT_FOR_HAC")
        self.assertFalse(record.passed)
        self.assertLess(record.matured_eligible_count, engine.NUMERICAL_FLOOR)
        self.assertIsNone(model)

    def test_training_precision_is_finite_above_floor(self) -> None:
        panel = self._direct_training_panel(1500)
        record, model = engine.training_precision_at_refit(panel, 1499)
        self.assertIsNotNone(model)
        self.assertGreaterEqual(record.matured_eligible_count, engine.NUMERICAL_FLOOR)
        self.assertIn(record.status, {"PASS", "PRECISION_TOO_WIDE"})
        self.assertEqual(len(record.probe_widths), 29)
        self.assertTrue(np.isfinite(np.asarray(record.probe_widths)).all())
        self.assertIsNotNone(record.p90_width)
        self.assertIsNotNone(record.max_width)

    def test_calibration_precision_floor_and_finite_above_floor(self) -> None:
        ts = pd.Timestamp("2022-10-01T00:00:00Z")
        short = engine.calibration_precision_from_pairs(
            ts,
            np.full(500, 0.5),
            np.linspace(-1.5, 1.5, 500),
            (np.arange(500) % 2).astype(float),
        )
        self.assertEqual(short.status, "INSUFFICIENT_FOR_HAC")
        self.assertFalse(short.passed)

        n = 800
        eta = np.linspace(-2.0, 2.0, n)
        rng = np.random.default_rng(540054)
        p = 1.0 / (1.0 + np.exp(-0.65 * eta))
        y = rng.binomial(1, p).astype(float)
        full = engine.calibration_precision_from_pairs(ts, np.full(n, 0.5), eta, y)
        self.assertNotEqual(full.status.split(":", 1)[0], "UNIDENTIFIED")
        self.assertIsNotNone(full.gamma)
        self.assertEqual(len(full.probe_widths), 8)
        self.assertTrue(np.isfinite(np.asarray(full.probe_widths)).all())
        self.assertIsNotNone(full.max_width)

    def test_readiness_requires_exactly_three_consecutive_passes(self) -> None:
        def rec(passed: bool) -> engine.TrainingPrecision:
            return engine.TrainingPrecision(
                "2022-01-01T00:00:00Z",
                700,
                "PASS" if passed else "PRECISION_TOO_WIDE",
                passed,
                0.05 if passed else 0.15,
                0.08 if passed else 0.25,
                tuple([0.05] * 29),
                0.0,
                1.0,
            )

        self.assertFalse(engine.consecutive_ready([rec(True), rec(True)]))
        self.assertTrue(engine.consecutive_ready([rec(True), rec(True), rec(True)]))
        self.assertFalse(engine.consecutive_ready([rec(True), rec(False), rec(True), rec(True)]))
        self.assertTrue(engine.consecutive_ready([rec(False), rec(True), rec(True), rec(True)]))


if __name__ == "__main__":
    unittest.main()
