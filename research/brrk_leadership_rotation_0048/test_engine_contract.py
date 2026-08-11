from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from research.brrk_leadership_rotation_0048 import engine


HERE = Path(__file__).resolve().parent


def synthetic_frames(n: int = 1400) -> dict[str, pd.DataFrame]:
    index = pd.date_range("2020-01-01", periods=n, freq="D")
    t = np.arange(n, dtype=float)
    btc = np.exp(4.0 + 0.0012 * t + 0.025 * np.sin(t / 17.0) + 0.01 * np.sin(t / 5.0))
    eth = np.exp(3.0 + 0.00125 * t + 0.08 * np.sin(t / 31.0) + 0.025 * np.sin(t / 8.0))
    sol = np.exp(1.0 + 0.00135 * t + 0.11 * np.sin(t / 23.0 + 0.8) + 0.03 * np.sin(t / 7.0))
    closes = {"BTC": btc, "ETH": eth, "SOL": sol}
    out: dict[str, pd.DataFrame] = {}
    for j, asset in enumerate(engine.ASSETS):
        close = closes[asset]
        quote_volume = 1_000_000.0 * (1.5 + 0.25 * np.sin(t / (19.0 + j * 3.0) + j) + 0.0001 * t)
        out[asset] = pd.DataFrame({"close": close, "quote_volume": quote_volume}, index=index)
    return out


def swap_eth_sol(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {"BTC": frames["BTC"].copy(), "ETH": frames["SOL"].copy(), "SOL": frames["ETH"].copy()}


class EngineContractTest(unittest.TestCase):
    def test_frozen_constants_match_preregistration(self):
        prereg = json.loads((HERE / "PREREGISTRATION.json").read_text(encoding="utf-8"))
        text = "\n".join(prereg["researcher_decisions"])
        self.assertEqual(engine.TARGET_HORIZONS, (14, 28, 56))
        self.assertEqual(engine.FEATURE_COLUMNS, ("K1", "K2", "K3", "K4", "Persistence60", "Position120", "Participation"))
        self.assertEqual(engine.RIDGE_LAMBDA, 1.0)
        self.assertEqual(engine.REFIT_CALENDAR_DAYS, 28)
        self.assertEqual(engine.MAX_TARGET_HORIZON_DAYS, 56)
        self.assertEqual(engine.INITIAL_TRAIN_SUPPORT, 365)
        self.assertEqual(engine.INITIAL_CALIBRATION_SUPPORT, 365)
        self.assertEqual(engine.BOOTSTRAP_BLOCK_LENGTH, 56)
        self.assertEqual(engine.BOOTSTRAP_REPLICATES, 10_000)
        self.assertEqual(engine.BOOTSTRAP_SEED, 4_292_549_012)
        self.assertEqual(engine.SPLINE_INTERNAL_KNOTS, (0.25, 0.50, 0.75))
        self.assertEqual(engine.BREAKPOINT_RANGE, (0.20, 0.80))
        self.assertIn("T*=max_b(mean(d_b*)-mean(d_b))", text)
        self.assertIn("deterministic global SSE minimizer", text)

    def test_target_formula_matches_direct_definition(self):
        frames = synthetic_frames(400)
        panel = engine.build_feature_target_panel(frames)
        dt = panel.index[300]
        for asset in ("ETH", "SOL"):
            close = frames[asset]["close"]
            values = []
            for h in engine.TARGET_HORIZONS:
                direct = 2.0 / (h * (h + 1.0)) * sum(math.log(float(close.loc[dt + pd.Timedelta(days=u)]) / float(close.loc[dt])) for u in range(1, h + 1))
                self.assertAlmostEqual(float(panel.loc[dt, f"FUTURE_A_{asset}_{h}"]), direct, places=12)
                values.append(direct)
            self.assertAlmostEqual(float(panel.loc[dt, f"FUTURE_L_{asset}"]), float(np.mean(values)), places=12)

    def test_eth_sol_exchange_is_antisymmetric(self):
        frames = synthetic_frames(500)
        original = engine.build_feature_target_panel(frames)
        swapped = engine.build_feature_target_panel(swap_eth_sol(frames))
        mask = original["FEATURE_VALID"] & swapped["FEATURE_VALID"] & original["TARGET_DEFINED"] & swapped["TARGET_DEFINED"]
        self.assertGreater(int(mask.sum()), 100)
        np.testing.assert_allclose(
            original.loc[mask, list(engine.FEATURE_COLUMNS)].to_numpy(dtype=float),
            -swapped.loc[mask, list(engine.FEATURE_COLUMNS)].to_numpy(dtype=float),
            atol=1e-10,
            rtol=1e-10,
        )
        np.testing.assert_allclose(original.loc[mask, "M"].to_numpy(dtype=float), -swapped.loc[mask, "M"].to_numpy(dtype=float), atol=1e-12, rtol=1e-12)
        np.testing.assert_array_equal(original.loc[mask, "Y"].to_numpy(dtype=int), 1 - swapped.loc[mask, "Y"].to_numpy(dtype=int))
        np.testing.assert_allclose(original.loc[mask, "H_LAGGED_LEADER"], -swapped.loc[mask, "H_LAGGED_LEADER"], atol=1e-12)
        np.testing.assert_allclose(original.loc[mask, "RM60"], -swapped.loc[mask, "RM60"], atol=1e-12)

    def test_offset_ridge_exchange_probability_complements(self):
        rng = np.random.default_rng(10048)
        X = rng.normal(size=(300, 7))
        y = (0.7 * X[:, 0] - 0.4 * X[:, 3] + 0.2 * X[:, 6] > 0.1).astype(float)
        pi = engine.prevalence_from_labels(y)
        fitted = engine.fit_offset_ridge(X, y, pi)
        swapped = engine.fit_offset_ridge(-X, 1.0 - y, 1.0 - pi)
        np.testing.assert_allclose(fitted.beta, swapped.beta, atol=1e-8, rtol=1e-8)
        p, _ = engine.raw_probability(fitted, X[:20])
        ps, _ = engine.raw_probability(swapped, -X[:20])
        np.testing.assert_allclose(p + ps, np.ones_like(p), atol=1e-10, rtol=1e-10)

    def test_label_maturity_is_exactly_56_calendar_days(self):
        frames = synthetic_frames(700)
        panel = engine.build_feature_target_panel(frames)
        prediction_date = panel.index[600]
        mask = engine.matured_training_mask(panel, prediction_date)
        selected = panel.index[mask]
        self.assertGreater(len(selected), 0)
        self.assertTrue((selected <= prediction_date - pd.Timedelta(days=56)).all())
        future_mask = panel.index.to_series() > prediction_date - pd.Timedelta(days=56)
        self.assertFalse(bool((mask & future_mask).any()))

    def test_temperature_is_prior_preserving_and_exchange_symmetric(self):
        priors = np.asarray([0.55, 0.58, 0.60, 0.57, 0.62, 0.59, 0.61, 0.56], dtype=float)
        etas = np.asarray([-1.1, 0.8, 1.4, -0.7, 0.9, -1.3, 1.7, -0.4], dtype=float)
        y = np.asarray([0, 1, 1, 0, 0, 0, 1, 1], dtype=float)
        fit = engine.fit_temperature(priors, etas, y)
        self.assertTrue(fit.identified)
        self.assertIsNotNone(fit.gamma)
        p = engine.calibrated_probability(priors, etas, float(fit.gamma))
        ps = engine.calibrated_probability(1.0 - priors, -etas, float(fit.gamma))
        np.testing.assert_allclose(p + ps, np.ones_like(p), atol=1e-12, rtol=1e-12)
        zero = engine.fit_temperature(priors, np.zeros_like(etas), y)
        self.assertFalse(zero.identified)

    def test_segmented_breakpoint_recovers_known_kink(self):
        c = np.linspace(0.01, 0.99, 840)
        z = 0.01 + 0.02 * c + 0.30 * np.maximum(c - 0.55, 0.0)
        block_ids = engine.sequential_full_block_ids(len(c))
        fit = engine.fit_segmented_breakpoint(c, z, block_ids)
        self.assertIsNotNone(fit)
        assert fit is not None
        self.assertAlmostEqual(fit.kappa, 0.55, places=6)
        self.assertGreater(fit.delta, 0.25)
        self.assertLess(fit.sse, 1e-12)

    def test_natural_spline_is_finite_and_derivatives_are_defined(self):
        c = np.linspace(0.0, 1.0, 300)
        z = 0.02 + 0.1 * c + 0.05 * c**2
        coef = engine.fit_natural_spline(c, z)
        grid = np.linspace(0.0, 1.0, 101)
        for derivative in (0, 1, 2):
            values = engine.evaluate_natural_spline(coef, grid, derivative=derivative)
            self.assertTrue(np.isfinite(values).all())

    def test_moving_block_indices_are_deterministic_and_contiguous_by_piece(self):
        rng1 = np.random.default_rng(engine.BOOTSTRAP_SEED)
        rng2 = np.random.default_rng(engine.BOOTSTRAP_SEED)
        idx1 = engine.moving_block_indices(173, rng1)
        idx2 = engine.moving_block_indices(173, rng2)
        np.testing.assert_array_equal(idx1, idx2)
        self.assertEqual(len(idx1), 173)
        for start in range(0, 168, 56):
            piece = idx1[start : min(start + 56, 173)]
            if len(piece) > 1:
                np.testing.assert_array_equal(np.diff(piece), np.ones(len(piece) - 1, dtype=int))

    def test_synthetic_walk_forward_is_prequential(self):
        frames = synthetic_frames(1450)
        panel = engine.build_feature_target_panel(frames)
        predictions = engine.walk_forward_predictions(panel)
        self.assertGreater(len(predictions), 10)
        self.assertTrue((predictions["training_size"] >= 365).all())
        self.assertTrue((predictions["calibration_pool_size"] >= 365).all())
        delta = (predictions.index.to_series() - pd.to_datetime(predictions["refit_date"])).dt.days
        self.assertTrue(((delta >= 0) & (delta < 28)).all())
        for col in ("p_candidate", "p_B0", "p_B1", "p_B2", "p_B3"):
            self.assertTrue(((predictions[col] > 0.0) & (predictions[col] < 1.0)).all())
        first = predictions.index.min()
        self.assertGreaterEqual(first, panel.index.min() + pd.Timedelta(days=365 + 56 + 365))

    def test_bootstrap_math_uses_common_indices_without_retraining(self):
        n = 224
        y = np.tile(np.asarray([0, 1], dtype=int), n // 2)
        p_candidate = np.where(y == 1, 0.68, 0.32)
        eval_rows = pd.DataFrame(
            {
                "Y": y,
                "confidence": np.linspace(0.2, 0.8, n),
                "Z": 0.01 + 0.04 * np.linspace(0.2, 0.8, n),
                "p_candidate": p_candidate,
                "EPISODE_ID": np.repeat(np.arange(1, 17), 14),
                "EPISODE_STATE": np.where(np.repeat(np.arange(1, 17), 14) % 2, "SOL", "ETH"),
                "EPISODE_DURATION": 14,
            },
            index=pd.date_range("2024-01-01", periods=n, freq="D"),
        )
        for name, prob in {
            "candidate": p_candidate,
            "B0": np.full(n, 0.5),
            "B1": np.full(n, 0.53),
            "B2": np.where(y == 1, 0.58, 0.42),
            "B3": np.where(y == 1, 0.60, 0.40),
        }.items():
            eval_rows[f"p_{name}"] = prob
            eval_rows[f"loss_{name}"] = engine.nll_losses(y, prob)
        stats1 = engine.bootstrap_statistics(eval_rows, replicates=20, seed=123)
        stats2 = engine.bootstrap_statistics(eval_rows, replicates=20, seed=123)
        self.assertEqual(stats1, stats2)
        self.assertEqual(set(stats1["simultaneous_ucl"]), {"B0", "B1", "B2", "B3"})

    def test_loader_rejects_nonfrozen_payload_before_parsing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_text(json.dumps({"payload": {}, "payload_sha256": "wrong"}), encoding="utf-8")
            with self.assertRaises(engine.FrozenProtocolError):
                engine.load_frozen_market_evidence(path)

    def test_controlled_run_boundary_has_no_scientific_result_artifacts(self):
        forbidden = {
            "PRIMARY_RESULT.json",
            "RESULT_SUMMARY.json",
            "EXECUTION.json",
            "RUN_ATTEMPT.marker",
            "RUN_ONCE.marker",
            "RESULT.md",
            "portfolio.py",
            "portfolio_result.json",
        }
        present = {p.name for p in HERE.iterdir() if p.is_file()}
        self.assertTrue(forbidden.isdisjoint(present))
        self.assertTrue({"run_once.py", "RUN_INTERFACE.json", "RESULT_SCHEMA.json"}.issubset(present))


if __name__ == "__main__":
    unittest.main()
