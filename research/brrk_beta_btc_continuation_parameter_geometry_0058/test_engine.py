from __future__ import annotations

import math
import unittest

import numpy as np
import pandas as pd

from research.brrk_beta_btc_continuation_parameter_geometry_0058 import engine


def frozen_flat_frames(value: float = 100.0) -> dict[str, pd.DataFrame]:
    idx = pd.date_range("2020-08-11", "2026-08-02", freq="D")
    return {
        asset: pd.DataFrame({"close": np.full(len(idx), value, dtype=np.float64)}, index=idx)
        for asset in engine.ASSETS
    }


def small_prices(rows: int = 300) -> pd.DataFrame:
    idx = pd.date_range("2020-01-01", periods=rows, freq="D")
    x = np.arange(rows, dtype=np.float64)
    return pd.DataFrame(
        {
            "BTC": 100.0 * np.exp(0.0005 * x),
            "ETH": 80.0 * np.exp(0.0007 * x),
            "SOL": 20.0 * np.exp(0.0009 * x),
        },
        index=idx,
    )


class Test0058Engine(unittest.TestCase):
    def test_constants_match_preregistration(self) -> None:
        self.assertEqual(engine.L_VALUES, tuple(range(20, 241, 20)))
        self.assertEqual(len(engine.KAPPA_VALUES), 9)
        self.assertEqual(len(engine.L_VALUES) * len(engine.KAPPA_VALUES), 108)
        self.assertEqual(engine.COST_BPS, (5.0, 10.0, 20.0))
        self.assertEqual(engine.HELD_PERIODS, 1942)
        self.assertEqual(engine.TEMPORAL_BLOCK_SIZES, (486, 486, 485, 485))
        self.assertEqual(sum(engine.TEMPORAL_BLOCK_SIZES), 1942)
        self.assertAlmostEqual(engine.GRADIENT_THRESHOLD, math.log(1.05))
        self.assertAlmostEqual(engine.HESSIAN_THRESHOLD, math.log(1.10))

    def test_payload_identity_guard(self) -> None:
        engine.validate_payload_identity(engine.EXPECTED_PAYLOAD_SHA256)
        with self.assertRaises(engine.ParameterGeometryProtocolError):
            engine.validate_payload_identity("0" * 64)

    def test_frozen_calendar_contract_accepts_tz_naive_only(self) -> None:
        frames = frozen_flat_frames()
        prices = engine.validate_price_frames(frames, require_frozen_calendar=True)
        self.assertEqual(len(prices), 2183)
        self.assertIsNone(prices.index.tz)
        self.assertEqual(prices.index[240], pd.Timestamp("2021-04-08"))
        self.assertEqual(prices.index[-2], pd.Timestamp("2026-08-01"))
        self.assertEqual(prices.index[-1], pd.Timestamp("2026-08-02"))

        aware = {k: v.copy() for k, v in frames.items()}
        for frame in aware.values():
            frame.index = frame.index.tz_localize("UTC")
        with self.assertRaises(engine.ParameterGeometryProtocolError):
            engine.validate_price_frames(aware, require_frozen_calendar=True)

    def test_index_and_close_validation_rejects_mutations(self) -> None:
        frames = frozen_flat_frames()
        bad = {k: v.copy() for k, v in frames.items()}
        bad["SOL"] = bad["SOL"].iloc[:-1].copy()
        with self.assertRaises(engine.ParameterGeometryProtocolError):
            engine.validate_price_frames(bad, require_frozen_calendar=True)

        bad2 = {k: v.copy() for k, v in frames.items()}
        bad2["ETH"].iloc[10, 0] = 0.0
        with self.assertRaises(engine.ParameterGeometryProtocolError):
            engine.validate_price_frames(bad2, require_frozen_calendar=True)

    def test_relative_log_state_formula(self) -> None:
        idx = pd.date_range("2020-01-01", periods=3, freq="D")
        prices = pd.DataFrame(
            {
                "BTC": [10.0, 10.0, 10.0],
                "ETH": [20.0, 40.0, 80.0],
                "SOL": [40.0, 40.0, 40.0],
            },
            index=idx,
        )
        z = engine.relative_log_state(prices)
        expected = 0.5 * np.log(prices["ETH"].to_numpy() / 10.0) + 0.5 * np.log(
            prices["SOL"].to_numpy() / 10.0
        )
        np.testing.assert_allclose(z, expected, rtol=0.0, atol=1e-15)

    def test_sigma240_uses_exact_recent_240_changes(self) -> None:
        z = np.arange(302, dtype=np.float64)
        sigma = engine.sigma240_from_z(z)
        self.assertTrue(np.isnan(sigma[:240]).all())
        self.assertAlmostEqual(float(sigma[240]), 0.0)
        z2 = np.concatenate([[0.0], np.cumsum(np.arange(1.0, 302.0))])
        sigma2 = engine.sigma240_from_z(z2)
        expected = float(np.std(np.arange(1.0, 241.0), ddof=1))
        self.assertAlmostEqual(float(sigma2[240]), expected)

    def test_exact_threshold_equality_routes_to_btc(self) -> None:
        states = engine.states_from_scores([0.0, 0.25, 0.2500000001], 0.25)
        self.assertEqual(states, ("BTC", "BTC", "BETA"))

    def test_candidate_turnover_and_beta_drift(self) -> None:
        prices = small_prices(245)
        states = ("BETA", "BETA", "BTC", "BETA")
        path = engine.simulate_candidate(prices, states, 5.0)
        np.testing.assert_allclose(path.executed_l1_turnover, [1.0, 0.0, 2.0, 2.0])
        self.assertEqual(path.switch_count, 2)
        self.assertAlmostEqual(path.beta_holding_fraction, 0.75)
        self.assertTrue(np.all(path.transaction_cost >= 0.0))
        self.assertEqual(len(path.nav), 5)
        self.assertTrue(np.all(path.nav > 0.0))

    def test_static_benchmarks_pay_one_entry_and_never_rebalance(self) -> None:
        prices = small_prices(245)
        benches = engine.simulate_benchmarks(prices, 10.0)
        self.assertEqual(set(benches), set(engine.BENCHMARKS))
        for path in benches.values():
            self.assertEqual(path.executed_l1_turnover[0], 1.0)
            self.assertTrue(np.all(path.executed_l1_turnover[1:] == 0.0))
            self.assertAlmostEqual(path.total_turnover, 1.0)

    def test_connected_component_support_and_medoid_are_geometric(self) -> None:
        mask = np.zeros((12, 9), dtype=bool)
        mask[2:5, 2:5] = True
        comps = engine.admissible_components(mask)
        self.assertEqual(len(comps), 1)
        self.assertEqual(len(comps[0]), 9)
        medoid, distance_sum = engine.medoid_of_component(comps[0])
        self.assertEqual(medoid, (3, 3))
        self.assertEqual(distance_sum, 12.0)

    def test_ridge_without_three_by_three_span_is_not_admissible(self) -> None:
        mask = np.zeros((12, 9), dtype=bool)
        mask[2:11, 3] = True
        self.assertEqual(engine.admissible_components(mask), [])

    def test_geometry_constant_surface_marks_all_interior_stable(self) -> None:
        dummy = engine.PortfolioPath(
            name="CANDIDATE",
            cost_bps=5.0,
            nav=np.array([1.0, 1.0]),
            period_factors=np.array([1.0]),
            executed_l1_turnover=np.array([0.0]),
            states=("BTC",),
            pre_trade_nav=np.array([1.0]),
            transaction_cost=np.array([0.0]),
            post_trade_nav=np.array([1.0]),
        )
        cell_paths = {(L, k): dummy for L in engine.L_VALUES for k in engine.KAPPA_VALUES}
        rows, mask = engine.geometry_for_cost(cell_paths, 5.0)
        self.assertEqual(len(rows), 70)
        self.assertEqual(int(mask.sum()), 70)
        self.assertTrue(all(row["gradient_norm"] == 0.0 for row in rows))
        self.assertTrue(all(row["hessian_spectral_norm"] == 0.0 for row in rows))

    def test_component_ranking_ignores_terminal_wealth(self) -> None:
        a = tuple((i, j) for i in range(2, 5) for j in range(2, 5))
        b = tuple((i, j) for i in range(6, 9) for j in range(2, 5))
        selected = engine.select_component([b, a])
        self.assertEqual(selected, a)

    def test_classification_precedence(self) -> None:
        self.assertEqual(
            engine.classification_from_gates(g1=False, g2=None, g3=None, g4=None, g5=None),
            "FAIL_NO_STABLE_PARAMETER_PLATEAU",
        )
        self.assertEqual(
            engine.classification_from_gates(g1=True, g2=False, g3=None, g4=None, g5=None),
            "FAIL_STABLE_PLATEAU_NOT_COST_ROBUST",
        )
        self.assertEqual(
            engine.classification_from_gates(g1=True, g2=True, g3=False, g4=True, g5=True),
            "FAIL_STABLE_PLATEAU_NOT_ECONOMICALLY_RELEVANT",
        )
        self.assertEqual(
            engine.classification_from_gates(g1=True, g2=True, g3=True, g4=False, g5=True),
            "FAIL_STABLE_PLATEAU_NOT_TEMPORALLY_OR_DEPENDENCE_ROBUST",
        )
        self.assertEqual(
            engine.classification_from_gates(g1=True, g2=True, g3=True, g4=True, g5=True),
            "PASS_PARAMETER_FREEZE_ELIGIBLE",
        )

    def test_bootstrap_helper_is_seed_deterministic(self) -> None:
        rng = np.random.default_rng(1)
        d = rng.normal(0.001, 0.01, size=(240, 3))
        a = engine._bootstrap_from_differentials(d, replicates=50, seed=123)
        b = engine._bootstrap_from_differentials(d, replicates=50, seed=123)
        self.assertEqual(a, b)

    def test_full_frozen_synthetic_contract_produces_lossless_shapes(self) -> None:
        result = engine.evaluate_frozen_contract(
            frozen_flat_frames(),
            engine.EXPECTED_PAYLOAD_SHA256,
        )
        self.assertEqual(result["classification"], "FAIL_STABLE_PLATEAU_NOT_COST_ROBUST")
        self.assertTrue(result["gates"]["G0_INTEGRITY"])
        self.assertTrue(result["gates"]["G1_PRIMARY_PLATEAU"])
        self.assertFalse(result["gates"]["G2_COST_ROBUSTNESS"])
        self.assertIsNone(result["gates"]["G3_ECONOMIC_RELEVANCE"])
        self.assertIsNone(result["gates"]["G4_TEMPORAL_ROBUSTNESS"])
        self.assertIsNone(result["gates"]["G5_DEPENDENCE_AWARE_ROBUSTNESS"])
        self.assertEqual(len(result["surface_table_every_cell_every_cost"]), 324)
        self.assertEqual(len(result["geometry_every_interior_cell_every_cost"]), 210)
        self.assertEqual(len(result["selected_representative_daily_path"]), 1942)
        self.assertEqual(len(result["benchmark_daily_paths"]), 3 * 1942)
        self.assertEqual(result["plateau_trace"]["selected_representative"], {"L": 120, "kappa": 1.0})
        self.assertEqual(result["diagnostics"]["selected_component_size"], 70)
        self.assertEqual(result["actual_variants_evaluated"], 108)
        self.assertEqual(result["robustness"]["bootstrap_means"], None)

    def test_no_loader_or_network_surface_is_present(self) -> None:
        forbidden = (
            "requests.",
            "urllib.",
            "open(",
            "read_text(",
            "read_bytes(",
            "frames_from_market_evidence",
        )
        with open(engine.__file__, "r", encoding="utf-8") as handle:
            source = handle.read()
        for token in forbidden:
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
