from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from research.brrk_idle_cash_passive_accrual_robustness_0064 import engine as e


def test_frozen_geometry_and_statistics() -> None:
    assert e.YIELD_REALIZATIONS == (0.25, 0.50, 0.75, 1.00)
    assert e.ANNUAL_SPREAD_FEE_BPS == (0, 50, 100, 150, 200)
    assert e.PRIMARY == (0.50, 100)
    assert e.CORE_YIELDS == (0.50, 0.75, 1.00)
    assert e.CORE_FEES == (50, 100, 150)
    assert e.MBB_BLOCK_LENGTH == 60
    assert e.MBB_REPS == 4000
    assert e.MBB_SEED == 640064
    assert e.FROZEN_CELL_COUNT == 20


def test_passive_accrual_formula_and_no_floor() -> None:
    baseline = np.zeros(3)
    cash = np.array([0.5, 0.4, 0.6])
    rf = np.array([0.001, 0.001, 0.00001])
    candidate, net_cash, gross_carry, fee = e.candidate_returns(baseline, cash, rf, 0.5, 100)
    fee_daily = 0.01 / 365.25
    assert np.allclose(gross_carry, cash * 0.5 * rf)
    assert np.allclose(fee, cash * fee_daily)
    assert np.allclose(net_cash, gross_carry - fee)
    assert np.allclose(candidate, net_cash)
    assert net_cash[-1] < 0.0


def test_no_sweep_turnover_path_dependency() -> None:
    baseline = np.zeros(4)
    rf = np.full(4, 0.001)
    cash_a = np.array([0.2, 0.8, 0.2, 0.8])
    cash_b = np.array([0.2, 0.2, 0.8, 0.8])
    a, *_ = e.candidate_returns(baseline, cash_a, rf, 0.5, 100)
    b, *_ = e.candidate_returns(baseline, cash_b, rf, 0.5, 100)
    assert np.isclose(a.sum(), b.sum())


def test_outside_frozen_grid_rejected() -> None:
    with pytest.raises(e.MeasurementError, match="outside frozen grid"):
        e.candidate_returns([0.0], [0.5], [0.001], 0.6, 100)
    with pytest.raises(e.MeasurementError, match="outside frozen grid"):
        e.candidate_returns([0.0], [0.5], [0.001], 0.5, 125)


def test_rate_formula() -> None:
    got = e.dtb3_percent_to_daily_return([5.0])[0]
    d = 0.05
    expected = (365.0 * d / (360.0 - 91.0 * d)) / 365.0
    assert abs(got - expected) < 1e-15


def test_causal_ffill_and_no_backfill() -> None:
    strategy_dates = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    source_dates = pd.to_datetime(["2024-01-01", "2024-01-04"])
    got = e.causal_align_rates(strategy_dates, source_dates, [4.0, 5.0])
    assert np.array_equal(got, np.array([4.0, 4.0, 5.0]))
    with pytest.raises(e.MeasurementError, match="missing preceding"):
        e.causal_align_rates(strategy_dates, pd.to_datetime(["2024-01-03"]), [4.0])


def test_full_grid_dimensions_and_no_winner_selection() -> None:
    n = 240
    dates = pd.date_range("2023-01-01", periods=n, freq="D")
    returns = np.tile(np.array([0.002, -0.001, 0.001, 0.0]), n // 4)
    equity = 10000.0 * np.cumprod(1.0 + returns)
    weights = np.zeros((n, 2))
    weights[:, 0] = 0.35
    weights[:, 1] = 0.35
    rate_dates = pd.date_range("2022-12-30", periods=40, freq="7D")
    rate_values = np.full(len(rate_dates), 5.0)
    result = e.evaluate(dates, equity, weights, rate_dates, rate_values)
    assert result["candidate_cell_count"] == 20
    assert len(result["cells"]) == 20
    assert result["primary_cell_key"] == "a050_fee100bps"
    assert len(result["core_stress_cell_keys"]) == 9
    assert result["chronological_block_sizes"] == [60, 60, 60, 60]
    assert "argmax" not in result and "winner" not in result


def test_count_balanced_blocks_expected_full_support() -> None:
    ids = e.count_balanced_blocks(1332, 4)
    assert [int(np.sum(ids == i)) for i in range(4)] == [333, 333, 333, 333]


def test_type7_and_mbb_determinism() -> None:
    x = np.arange(10.0)
    assert e.type7_quantile(x, 0.95) == pytest.approx(8.55)
    d = np.sin(np.arange(240) / 7.0) * 0.001 + 0.0002
    a = e.mbb_lcb(d, block_length=60, reps=100, seed=640064)
    b = e.mbb_lcb(d, block_length=60, reps=100, seed=640064)
    assert a == b


def test_engine_source_contains_no_file_or_network_io() -> None:
    source = inspect.getsource(e)
    for token in ("requests", "urllib", "read_csv", "read_text", "read_bytes", "subprocess", "socket", "open("):
        assert token not in source
