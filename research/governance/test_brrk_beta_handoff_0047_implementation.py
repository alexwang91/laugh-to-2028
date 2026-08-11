from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from research.brrk_beta_handoff_0047 import engine
from research.core.crypto_rotation_backtest import trend_score as canonical_v1_trend_score

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "research" / "brrk_beta_handoff_0047"


def _frame(close: np.ndarray, start: pd.Timestamp) -> pd.DataFrame:
    close = np.asarray(close, dtype=float)
    idx = pd.date_range(start, periods=len(close), freq="D")
    return pd.DataFrame(
        {
            "open": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": np.linspace(1000.0, 2000.0, len(close)),
            "quote_volume": np.linspace(100_000.0, 200_000.0, len(close)),
            "trades": np.arange(len(close), dtype=int) + 100,
        },
        index=idx,
    )


def _ending_frames(days: int = 320) -> dict[str, pd.DataFrame]:
    start = engine.FROZEN_END - pd.Timedelta(days=days - 1)
    x = np.arange(days, dtype=float)
    return {
        "BTC": _frame(100.0 * np.exp(0.0010 * x), start),
        "ETH": _frame(100.0 * np.exp(0.0013 * x), start),
        "SOL": _frame(100.0 * np.exp(0.0016 * x), start),
    }


class TestBrrkBetaHandoff0047Implementation(unittest.TestCase):
    def test_frozen_trend_math_matches_canonical_v1_exactly(self):
        rng = np.random.default_rng(47)
        idx = pd.date_range("2022-01-01", periods=500, freq="D")
        price = pd.Series(100.0 * np.exp(np.cumsum(rng.normal(0.001, 0.02, len(idx)))), index=idx)
        for weights in (engine.FAST_WEIGHTS, engine.SLOW_WEIGHTS):
            got = engine.trend_score(price, weights)
            expected = canonical_v1_trend_score(price, list(weights))
            np.testing.assert_allclose(got.to_numpy(), expected.to_numpy(), rtol=0.0, atol=0.0, equal_nan=True)
        self.assertEqual(engine.HORIZONS, (20, 60, 120, 240))
        self.assertEqual(engine.FAST_WEIGHTS, (0.15, 0.25, 0.30, 0.30))
        self.assertEqual(engine.SLOW_WEIGHTS, (0.10, 0.20, 0.30, 0.40))

    def test_common_history_uses_latest_first_available_then_requires_every_day(self):
        frames = _ending_frames(120)
        sol = frames["SOL"].iloc[5:].copy()
        aligned = engine.assemble_common_frames({"BTC": frames["BTC"], "ETH": frames["ETH"], "SOL": sol})
        self.assertEqual(aligned["BTC"].index[0], sol.index[0])
        self.assertEqual(aligned["BTC"].index[-1], engine.FROZEN_END)
        broken = sol.drop(sol.index[20])
        with self.assertRaises(engine.FrozenProtocolError):
            engine.assemble_common_frames({"BTC": frames["BTC"], "ETH": frames["ETH"], "SOL": broken})

    def test_data_contract_fails_closed_on_duplicate_nonpositive_close_and_negative_trades(self):
        frame = _ending_frames(80)["BTC"]
        duplicate = pd.concat([frame, frame.iloc[[10]]]).sort_index()
        with self.assertRaises(engine.FrozenProtocolError):
            engine.validate_asset_frame("BTC", duplicate)
        bad_close = frame.copy()
        bad_close.iloc[5, bad_close.columns.get_loc("close")] = 0.0
        with self.assertRaises(engine.FrozenProtocolError):
            engine.validate_asset_frame("BTC", bad_close)
        bad_trades = frame.copy()
        bad_trades.iloc[5, bad_trades.columns.get_loc("trades")] = -1
        with self.assertRaises(engine.FrozenProtocolError):
            engine.validate_asset_frame("BTC", bad_trades)

    def test_market_evidence_round_trip_is_hash_bound(self):
        frames = _ending_frames(90)
        evidence = engine.build_market_evidence_payload(frames)
        rebuilt = engine.frames_from_market_evidence(evidence)
        self.assertEqual(evidence["payload"]["common_end"], "2026-08-02")
        for asset in engine.ASSETS:
            pd.testing.assert_frame_equal(rebuilt[asset], frames[asset], check_freq=False)
        tampered = json.loads(json.dumps(evidence))
        tampered["payload"]["rows"][0]["close"] *= 1.01
        with self.assertRaises(engine.FrozenProtocolError):
            engine.frames_from_market_evidence(tampered)

    def test_episode_boundaries_are_maximal_contiguous_nonnegative_btc_fast_runs(self):
        idx = pd.date_range("2024-01-01", periods=9, freq="D")
        score = pd.Series([np.nan, 0.0, 0.2, -0.1, 0.0, 0.1, np.nan, 0.3, -0.2], index=idx)
        ids, age = engine._episode_columns(score)
        got_ids = [None if pd.isna(v) else int(v) for v in ids]
        got_age = [None if pd.isna(v) else int(v) for v in age]
        self.assertEqual(got_ids, [None, 1, 1, None, 2, 2, None, 3, None])
        self.assertEqual(got_age, [None, 1, 2, None, 1, 2, None, 1, None])

    def test_durable_target_requires_same_unique_beta_at_20_and_60_and_positive_btc(self):
        idx = pd.date_range("2024-01-01", periods=100, freq="D")
        t = np.arange(len(idx), dtype=float)
        prices = pd.DataFrame(
            {
                "BTC": 100.0 * np.exp(0.0010 * t),
                "ETH": 100.0 * np.exp(0.0020 * t),
                "SOL": 100.0 * np.exp(0.0015 * t),
            },
            index=idx,
        )
        panel = pd.DataFrame({"EPISODE_ID": pd.Series(1, index=idx, dtype="Int64")}, index=idx)
        target = engine.build_durable_target(prices, panel)
        self.assertEqual(target.loc[idx[0], "DURABLE_CAUSE"], "ETH")
        self.assertTrue(bool(target.loc[idx[39], "TARGET_AVAILABLE"]))
        self.assertFalse(bool(target.loc[idx[40], "TARGET_AVAILABLE"]))
        self.assertTrue(pd.isna(target.loc[idx[40], "DURABLE_CAUSE"]))

        falling = pd.DataFrame(
            {
                "BTC": 100.0 * np.exp(-0.0020 * t),
                "ETH": 100.0 * np.exp(-0.0010 * t),
                "SOL": 100.0 * np.exp(-0.0015 * t),
            },
            index=idx,
        )
        falling_target = engine.build_durable_target(falling, panel)
        self.assertTrue(pd.isna(falling_target.loc[idx[0], "DURABLE_CAUSE"]))
        self.assertLess(falling_target.loc[idx[0], "F20_BTC"], 0.0)

    def test_durable_target_can_assign_SOL_when_SOL_is_unique_dual_horizon_winner(self):
        idx = pd.date_range("2024-01-01", periods=100, freq="D")
        t = np.arange(len(idx), dtype=float)
        prices = pd.DataFrame(
            {
                "BTC": 100.0 * np.exp(0.0010 * t),
                "ETH": 100.0 * np.exp(0.0015 * t),
                "SOL": 100.0 * np.exp(0.0025 * t),
            },
            index=idx,
        )
        panel = pd.DataFrame({"EPISODE_ID": pd.Series(1, index=idx, dtype="Int64")}, index=idx)
        target = engine.build_durable_target(prices, panel)
        self.assertEqual(target.loc[idx[0], "DURABLE_CAUSE"], "SOL")

    def test_primary_event_is_earliest_handoff_and_spell_stops_at_first_nonmatching_session(self):
        idx = pd.date_range("2024-01-01", periods=100, freq="D")
        t = np.arange(len(idx), dtype=float)
        prices = pd.DataFrame(
            {
                "BTC": 100.0 * np.exp(0.0010 * t),
                "ETH": 100.0 * np.exp(0.0020 * t),
                "SOL": 100.0 * np.exp(0.0015 * t),
            },
            index=idx,
        )
        panel = pd.DataFrame(index=idx)
        panel["EPISODE_ID"] = pd.Series(1, index=idx, dtype="Int64")
        panel["STATE_AGE"] = pd.Series(np.arange(1, 101), index=idx, dtype="Int64")
        for col in ("ETH_ABS_FAST", "SOL_ABS_FAST", "ETH_REL_FAST", "SOL_REL_FAST"):
            panel[col] = 1.0
        panel["ETH_V1_ELIGIBLE"] = 1
        panel["SOL_V1_ELIGIBLE"] = 1
        target = engine.build_durable_target(prices, panel)
        target.loc[idx[5], "DURABLE_CAUSE"] = pd.NA
        target.loc[idx[5], "ETH_DURABLE"] = False
        episodes = engine.build_episode_table(prices, panel, target)
        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0]["primary_handoff_date"], "2024-01-01")
        self.assertEqual(episodes[0]["primary_handoff_cause"], "ETH")
        self.assertEqual(episodes[0]["handoff_state_age"], 1)
        self.assertEqual(episodes[0]["handoff_opportunity_spell_length"], 5)

    def test_cross_correlation_never_pairs_across_episode_boundary_and_positive_lag_means_btc_leads(self):
        rng = np.random.default_rng(470)
        n = 140
        idx = pd.date_range("2024-01-01", periods=n, freq="D")
        btc_ret = rng.normal(0.0, 0.02, n)
        eth_ret = rng.normal(0.0, 0.002, n)
        eth_ret[2:] = btc_ret[:-2]
        sol_ret = rng.normal(0.0, 0.02, n)
        prices = pd.DataFrame(
            {
                "BTC": np.exp(np.cumsum(btc_ret)),
                "ETH": np.exp(np.cumsum(eth_ret)),
                "SOL": np.exp(np.cumsum(sol_ret)),
            },
            index=idx,
        )
        panel = pd.DataFrame(index=idx)
        panel["EPISODE_ID"] = pd.Series([1] * 70 + [2] * 70, index=idx, dtype="Int64")
        diag = engine.cross_correlation_diagnostics(prices, panel)
        eth_rows = [x for x in diag["pooled"] if x["pair"] == "BTC_ETH"]
        best = max((x for x in eth_rows if x["correlation"] is not None), key=lambda x: x["correlation"])
        self.assertEqual(best["lag"], 2)
        lag0 = next(x for x in eth_rows if x["lag"] == 0)
        self.assertEqual(lag0["n_pairs"], 138)
        self.assertIn("positive lag means BTC leads", lag0["lag_semantics"])

    def test_VAR7_within_estimator_matches_explicit_episode_dummy_intercept_OLS(self):
        rng = np.random.default_rng(471)
        lengths = [220, 230]
        all_returns = []
        ids = []
        a1 = np.array([[0.20, 0.03, 0.00], [0.08, 0.15, 0.02], [0.05, 0.04, 0.10]])
        intercepts = [np.array([0.002, 0.001, -0.001]), np.array([-0.001, 0.002, 0.001])]
        for episode_id, (length, intercept) in enumerate(zip(lengths, intercepts), start=1):
            r = np.zeros((length, 3), dtype=float)
            for i in range(1, length):
                r[i] = intercept + a1 @ r[i - 1] + rng.normal(0.0, 0.01, 3)
            all_returns.append(r)
            ids.extend([episode_id] * length)
        returns = np.vstack(all_returns)
        idx = pd.date_range("2023-01-01", periods=len(returns), freq="D")
        prices = pd.DataFrame(np.exp(np.cumsum(returns, axis=0)), index=idx, columns=list(engine.ASSETS))
        panel = pd.DataFrame({"EPISODE_ID": pd.Series(ids, index=idx, dtype="Int64")}, index=idx)
        prepared = engine.prepare_episode_var(prices, panel)
        fit = engine.fit_episode_var7(prepared)
        self.assertEqual(fit["status"], "OK")
        self.assertEqual(len(fit["granger_wald"]), 6)
        self.assertTrue(all(len(row["lag_coefficients"]) == 7 for row in fit["granger_wald"]))
        self.assertEqual(len(fit["generalized_btc_irf"]), 15)

        x = np.vstack([prepared.x_by_episode[eid] for eid in prepared.episode_ids])
        y = np.vstack([prepared.y_by_episode[eid] for eid in prepared.episode_ids])
        dummy_blocks = []
        for j, eid in enumerate(prepared.episode_ids):
            d = np.zeros((len(prepared.x_by_episode[eid]), len(prepared.episode_ids)))
            d[:, j] = 1.0
            dummy_blocks.append(d)
        dummies = np.vstack(dummy_blocks)
        full_x = np.hstack([dummies, x])
        explicit = np.linalg.lstsq(full_x, y, rcond=None)[0][len(prepared.episode_ids) :, :]
        np.testing.assert_allclose(fit["_beta"], explicit, rtol=1e-10, atol=1e-12)

    def test_one_switch_oracle_is_descriptive_and_charges_exact_full_switch_cost(self):
        idx = pd.date_range("2024-01-01", periods=20, freq="D")
        t = np.arange(len(idx), dtype=float)
        prices = pd.DataFrame(
            {
                "BTC": 100.0 * np.exp(0.01 * t),
                "ETH": 100.0 * np.exp(0.04 * t),
                "SOL": 100.0 * np.exp(0.015 * t),
            },
            index=idx,
        )
        oracle = engine.one_switch_oracle(prices, idx)
        self.assertEqual(oracle["oracle_choice"], "ETH")
        self.assertGreater(oracle["oracle_log_wealth_uplift_vs_BTC"], 0.0)
        self.assertAlmostEqual(engine.ORACLE_FULL_SWITCH_COST, 0.001, places=15)

    def test_stage_classification_depends_only_on_frozen_episode_recurrence_and_cause_diversity(self):
        def row(i, eligible=True, cause=None):
            return {
                "episode_id": i,
                "first_target_available_date": "2024-01-01" if eligible else None,
                "primary_handoff_date": "2024-01-05" if cause else None,
                "primary_handoff_cause": cause,
            }

        insufficient = engine.stage_classification([row(i) for i in range(4)])
        self.assertEqual(insufficient["result_status"], "INSUFFICIENT_EPISODE_DIVERSITY")

        fail = engine.stage_classification([row(1, cause="ETH"), row(2), row(3), row(4), row(5)])
        self.assertEqual(fail["result_status"], "FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE")

        one_cause = engine.stage_classification(
            [row(1, cause="ETH"), row(2, cause="ETH"), row(3, cause="ETH"), row(4), row(5)]
        )
        self.assertEqual(one_cause["result_status"], "INSUFFICIENT_COMPETING_RISK_DIVERSITY")

        passed = engine.stage_classification(
            [row(1, cause="ETH"), row(2, cause="SOL"), row(3, cause="ETH"), row(4), row(5)]
        )
        self.assertEqual(passed["result_status"], "PASS_DURATION_AWARE_HANDOFF_MODEL_STAGE_ELIGIBLE")
        self.assertEqual(passed["episode_level_durable_handoff_prevalence"], 0.6)

    def test_run_interface_freezes_zero_result_zero_model_zero_portfolio_authority(self):
        interface = json.loads((HERE / "RUN_INTERFACE.json").read_text())
        self.assertEqual(interface["status"], "IMPLEMENTED_PRE_RESULT_NOT_RUN")
        self.assertEqual(interface["actual_variants_evaluated"], 0)
        self.assertEqual(interface["frozen_causal_trend"]["horizons"], [20, 60, 120, 240])
        self.assertEqual(interface["frozen_realized_target"]["forward_horizons"], [20, 60])
        self.assertEqual(interface["frozen_transmission"]["VAR"], "POOLED_EPISODE_PRESERVING_VAR7_WITH_EPISODE_FIXED_INTERCEPTS")
        self.assertEqual(interface["frozen_uncertainty"]["replicates"], 10000)
        self.assertEqual(interface["frozen_uncertainty"]["seed"], 470047)
        self.assertFalse(interface["authority"]["historical_result_released"])
        self.assertFalse(interface["authority"]["duration_aware_handoff_model_fitted"])
        self.assertFalse(interface["authority"]["portfolio_allocation_tested"])
        self.assertFalse(interface["authority"]["portfolio_economics_executed"])
        self.assertFalse(interface["authority"]["production_authorized"])
        for forbidden in ("PRIMARY_RESULT.json", "EXECUTION.json", "RUN_ONCE.marker", "RESULT.md"):
            self.assertFalse((HERE / forbidden).exists())

    def test_implementation_source_has_no_portfolio_or_hazard_model_translation(self):
        source = (HERE / "engine.py").read_text() + "\n" + (HERE / "run_once.py").read_text()
        for forbidden in ("run_portfolio(", "load_fred_daily_risk_free", "hazard_model", "SemiMarkov", "LightGBM"):
            self.assertNotIn(forbidden, source)
        self.assertIn('"portfolio_economics_executed": False', source)
        self.assertIn('"duration_aware_handoff_model_fitted": False', source)


if __name__ == "__main__":
    unittest.main()
