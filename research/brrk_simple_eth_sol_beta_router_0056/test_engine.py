from __future__ import annotations

import math
import unittest

import numpy as np
import pandas as pd

from research.brrk_simple_eth_sol_beta_router_0056 import engine


class SimpleBetaRouterEngineContractTests(unittest.TestCase):
    @staticmethod
    def _frames_from_arrays(eth: np.ndarray, sol: np.ndarray, start: str = "2020-01-01T00:00:00Z") -> dict[str, pd.DataFrame]:
        index = pd.date_range(start, periods=len(eth), freq="D", tz="UTC")
        return {
            "ETH": pd.DataFrame({"close": np.asarray(eth, dtype=float)}, index=index),
            "SOL": pd.DataFrame({"close": np.asarray(sol, dtype=float)}, index=index),
        }

    @staticmethod
    def _frozen_synthetic_frames() -> dict[str, pd.DataFrame]:
        index = pd.date_range(engine.FROZEN_START, engine.TERMINAL_CLOSE, freq="D")
        t = np.arange(len(index), dtype=float)
        eth_log = 4.5 + 0.00045 * t + 0.025 * np.sin(t / 47.0) + 0.011 * np.cos(t / 13.0)
        rel_step = 0.00006 + 0.0012 * np.sin(t / 37.0) + 0.00055 * np.cos(t / 19.0)
        z = 0.4 + np.cumsum(rel_step)
        sol_log = eth_log + z
        return {
            "ETH": pd.DataFrame({"close": np.exp(eth_log)}, index=index),
            "SOL": pd.DataFrame({"close": np.exp(sol_log)}, index=index),
        }

    def test_frozen_calendar_and_counts_are_exact(self) -> None:
        prices = engine.validate_price_frames(self._frozen_synthetic_frames(), require_frozen_calendar=True)
        self.assertEqual(len(prices), 2183)
        self.assertEqual(prices.index[60], engine.FIRST_ORIGIN)
        self.assertEqual(prices.index[-2], engine.LAST_ORIGIN)
        self.assertEqual(prices.index[-1], engine.TERMINAL_CLOSE)
        rm, targets = engine.router_targets_from_prices(prices)
        self.assertEqual(len(rm), 2122)
        self.assertEqual(len(targets), 2122)
        self.assertEqual(sum(engine.TEMPORAL_BLOCK_SIZES), 2122)
        self.assertEqual(math.ceil(2122 / 60), engine.BOOTSTRAP_BLOCKS_PER_REPLICATE)

    def test_payload_identity_is_exact_and_has_no_loader_side_effect(self) -> None:
        engine.validate_payload_identity(engine.EXPECTED_PAYLOAD_SHA256)
        with self.assertRaises(engine.RouterProtocolError):
            engine.validate_payload_identity("0" * 64)

    def test_validator_rejects_bad_calendar_and_nonpositive_prices(self) -> None:
        frames = self._frames_from_arrays(np.ones(63), np.ones(63))
        with self.assertRaises(engine.RouterProtocolError):
            engine.validate_price_frames(frames, require_frozen_calendar=True)
        bad = self._frames_from_arrays(np.ones(63), np.ones(63))
        bad["SOL"].iloc[3, 0] = 0.0
        with self.assertRaises(engine.RouterProtocolError):
            engine.validate_price_frames(bad, require_frozen_calendar=False)

    def test_exact_zero_fallback_and_retain_prior_are_frozen(self) -> None:
        n = 64
        eth = np.ones(n)
        z = np.zeros(n)
        z[61] = 1.0
        z[62] = 0.0
        sol = np.exp(z)
        prices = engine.validate_price_frames(self._frames_from_arrays(eth, sol), require_frozen_calendar=False)
        rm, targets = engine.router_targets_from_prices(prices)
        np.testing.assert_allclose(rm, np.asarray([0.0, 1.0, 0.0]), rtol=0.0, atol=0.0)
        self.assertEqual(targets, ("ETH", "SOL", "SOL"))

    def test_signal_move_is_not_same_period_return_capture(self) -> None:
        n = 62
        eth = np.ones(n)
        sol = np.ones(n)
        sol[60] = 10.0
        sol[61] = 10.0
        prices = engine.validate_price_frames(self._frames_from_arrays(eth, sol), require_frozen_calendar=False)
        _, targets = engine.router_targets_from_prices(prices)
        self.assertEqual(targets, ("SOL",))
        path = engine.simulate_router(prices, targets, 5.0)
        self.assertAlmostEqual(path.terminal_wealth, 1.0 - 5.0 / 10000.0, places=15)

    def test_router_l1_turnover_is_1_then_2_only_on_full_switch(self) -> None:
        n = engine.LOOKBACK_DAYS + 5
        prices = engine.validate_price_frames(self._frames_from_arrays(np.ones(n), np.ones(n)), require_frozen_calendar=False)
        targets = ("ETH", "ETH", "SOL", "SOL")
        path = engine.simulate_router(prices, targets, 5.0)
        np.testing.assert_array_equal(path.executed_l1_turnover, np.asarray([1.0, 0.0, 2.0, 0.0]))
        expected = (1.0 - 0.0005) * (1.0 - 0.0010)
        self.assertAlmostEqual(path.terminal_wealth, expected, places=15)
        self.assertEqual(int(np.sum(path.executed_l1_turnover[1:] == 2.0)), 1)

    def test_static_50_50_is_initial_split_then_drifting_buy_and_hold(self) -> None:
        n = engine.LOOKBACK_DAYS + 3
        eth = np.ones(n)
        sol = np.ones(n)
        eth[61:] = 2.0
        sol[62:] = 2.0
        prices = engine.validate_price_frames(self._frames_from_arrays(eth, sol), require_frozen_calendar=False)
        path = engine.simulate_static_50_50(prices, 5.0)
        post = 1.0 - 0.0005
        expected = 0.5 * post * (eth[62] / eth[60]) + 0.5 * post * (sol[62] / sol[60])
        self.assertAlmostEqual(path.terminal_wealth, expected, places=15)
        np.testing.assert_array_equal(path.executed_l1_turnover, np.asarray([1.0, 0.0]))

    def test_static_arms_pay_only_initial_entry_cost(self) -> None:
        n = engine.LOOKBACK_DAYS + 5
        prices = engine.validate_price_frames(self._frames_from_arrays(np.ones(n), np.ones(n)), require_frozen_calendar=False)
        e = engine.simulate_static_single(prices, "ETH", 20.0)
        s = engine.simulate_static_single(prices, "SOL", 20.0)
        b2 = engine.simulate_static_50_50(prices, 20.0)
        for path in (e, s, b2):
            np.testing.assert_array_equal(path.executed_l1_turnover, np.asarray([1.0, 0.0, 0.0, 0.0]))
            self.assertAlmostEqual(path.terminal_wealth, 1.0 - 0.0020, places=15)

    def test_higher_costs_reduce_router_wealth_with_same_targets(self) -> None:
        n = engine.LOOKBACK_DAYS + 7
        prices = engine.validate_price_frames(self._frames_from_arrays(np.ones(n), np.ones(n)), require_frozen_calendar=False)
        targets = ("ETH", "SOL", "ETH", "SOL", "ETH", "SOL")
        panel = engine.evaluate_cost_panel(prices, targets)
        wealths = [panel[bps]["ROUTER"].terminal_wealth for bps in engine.COST_BPS]
        self.assertGreater(wealths[0], wealths[1])
        self.assertGreater(wealths[1], wealths[2])
        for bps in engine.COST_BPS:
            self.assertEqual(panel[bps]["ROUTER"].targets, targets)

    def test_best_static_exact_tie_break_is_b0_then_b1_then_b2(self) -> None:
        def path(name: str, w: float) -> engine.ArmPath:
            return engine.ArmPath(name, 5.0, np.asarray([1.0, w]), np.asarray([w]), np.asarray([1.0]), None)
        arms = {
            "B0_STATIC_ETH": path("B0_STATIC_ETH", 2.0),
            "B1_STATIC_SOL": path("B1_STATIC_SOL", 2.0),
            "B2_STATIC_50_50": path("B2_STATIC_50_50", 2.0),
        }
        self.assertEqual(engine.select_best_static(arms), "B0_STATIC_ETH")
        arms["B1_STATIC_SOL"] = path("B1_STATIC_SOL", 2.1)
        self.assertEqual(engine.select_best_static(arms), "B1_STATIC_SOL")

    def test_temporal_blocks_use_global_no_reset_nav_paths(self) -> None:
        rf = np.full(engine.HELD_PERIODS, 1.001, dtype=float)
        bf = np.full(engine.HELD_PERIODS, 1.0005, dtype=float)
        rnav = np.concatenate([[1.0], np.cumprod(rf)])
        bnav = np.concatenate([[1.0], np.cumprod(bf)])
        zero = np.zeros(engine.HELD_PERIODS)
        router = engine.ArmPath("ROUTER", 5.0, rnav, rf, zero, tuple(["ETH"] * engine.HELD_PERIODS))
        bench = engine.ArmPath("B0_STATIC_ETH", 5.0, bnav, bf, zero, tuple(["ETH"] * engine.HELD_PERIODS))
        stats = engine.temporal_block_relative_log_growth(router, bench)
        self.assertEqual(len(stats), 4)
        expected = [size * math.log(1.001 / 1.0005) for size in engine.TEMPORAL_BLOCK_SIZES]
        np.testing.assert_allclose(stats, expected, rtol=0.0, atol=1e-12)

    def test_moving_block_bootstrap_is_seeded_paired_and_type7(self) -> None:
        n = 180
        x = np.arange(n, dtype=float)
        d = np.column_stack([0.001 + x * 1e-7, 0.002 - x * 2e-7, 0.0005 + np.sin(x / 7.0) * 1e-4])
        a = engine._bootstrap_from_differentials(d, replicates=50, seed=12345)
        b = engine._bootstrap_from_differentials(d, replicates=50, seed=12345)
        self.assertEqual(a, b)
        self.assertEqual(len(a["means"]), 3)
        self.assertEqual(len(a["lcbs"]), 3)
        self.assertTrue(math.isfinite(a["q95"]))
        rng = np.random.default_rng(12345)
        idx = engine.moving_block_indices(2122, rng)
        self.assertEqual(len(idx), 2122)
        self.assertTrue(np.all(np.diff(idx[:60]) == 1))
        self.assertGreaterEqual(int(idx.min()), 0)
        self.assertLessEqual(int(idx.max()), 2121)

    def test_classification_precedence_is_exact(self) -> None:
        self.assertEqual(engine.classification_from_gates(False, True, True, True, True), "INVALID_EXECUTION")
        self.assertEqual(engine.classification_from_gates(True, False, True, True, True), "FAIL_NO_SIMPLE_BETA_ROUTER_ECONOMIC_UPLIFT")
        self.assertEqual(engine.classification_from_gates(True, True, False, True, True), "FAIL_SIMPLE_BETA_ROUTER_COST_FRAGILE")
        self.assertEqual(engine.classification_from_gates(True, True, True, False, True), "FAIL_SIMPLE_BETA_ROUTER_TEMPORALLY_CONCENTRATED")
        self.assertEqual(engine.classification_from_gates(True, True, True, True, False), "FAIL_SIMPLE_BETA_ROUTER_ECONOMIC_UPLIFT_NOT_DEPENDENCE_ROBUST")
        self.assertEqual(engine.classification_from_gates(True, True, True, True, True), "PASS_SIMPLE_BETA_ROUTER_ECONOMIC_ELIGIBILITY")

    def test_full_frozen_contract_runs_only_on_synthetic_frames(self) -> None:
        out = engine.evaluate_frozen_contract(self._frozen_synthetic_frames(), engine.EXPECTED_PAYLOAD_SHA256)
        self.assertIn(out["classification"], engine.ALLOWED_CLASSIFICATIONS)
        self.assertEqual(out["target_count"], 2122)
        self.assertEqual(out["bootstrap_5bps"]["replicates"], 10000)
        self.assertEqual(out["bootstrap_5bps"]["block_length"], 60)
        self.assertEqual(out["bootstrap_5bps"]["seed"], 1844716895)
        self.assertEqual(out["actual_variants_evaluated"], 1)
        self.assertFalse(out["authority"]["production_authorized"])

    def test_holding_spell_and_calendar_return_diagnostics_are_mechanical(self) -> None:
        self.assertEqual(engine.holding_spells(("ETH", "ETH", "SOL", "SOL", "SOL", "ETH")), (2, 3, 1))
        factors = np.asarray([1.10, 0.90, 1.20])
        nav = np.concatenate([[1.0], np.cumprod(factors)])
        path = engine.ArmPath("ROUTER", 5.0, nav, factors, np.asarray([1.0, 0.0, 0.0]), ("ETH", "ETH", "ETH"))
        idx = pd.DatetimeIndex([pd.Timestamp("2020-12-31T00:00:00Z"), pd.Timestamp("2021-01-01T00:00:00Z"), pd.Timestamp("2021-01-02T00:00:00Z")])
        out = engine.calendar_year_returns(path, idx)
        self.assertAlmostEqual(out["2020"], 0.10, places=15)
        self.assertAlmostEqual(out["2021"], 0.90 * 1.20 - 1.0, places=15)


if __name__ == "__main__":
    unittest.main()
