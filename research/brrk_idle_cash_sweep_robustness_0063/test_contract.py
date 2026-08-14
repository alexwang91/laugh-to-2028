from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from research.brrk_idle_cash_sweep_robustness_0063 import engine as e


def test_frozen_dimensions_constants() -> None:
    assert e.YIELD_REALIZATIONS == (0.25, 0.50, 0.75, 1.00)
    assert e.SWEEP_FRICTION_BPS == (0, 5, 10, 20)
    assert e.PRIMARY == (0.50, 10)
    assert e.MBB_BLOCK_LENGTH == 60
    assert e.MBB_REPS == 4000
    assert e.MBB_SEED == 630063
    assert e.FROZEN_CELL_COUNT == 16


def test_rate_formula() -> None:
    got = e.dtb3_percent_to_daily_return([5.0])[0]
    d = 0.05
    expected = (365.0 * d / (360.0 - 91.0 * d)) / 365.0
    assert abs(got - expected) < 1e-15


def test_first_turnover_zero_and_candidate_formula() -> None:
    baseline = np.zeros(4)
    cash = np.array([0.5, 0.4, 0.6, 0.6])
    rf = np.full(4, 0.001)
    out, turnover, carry, friction = e.candidate_returns(baseline, cash, rf, 0.5, 10)
    assert np.allclose(turnover, [0.0, 0.1, 0.2, 0.0])
    assert np.allclose(carry, [0.00025, 0.0002, 0.0003, 0.0003])
    assert np.allclose(friction, [0.0, 0.0001, 0.0002, 0.0])
    assert abs(out[0] - 0.00025) < 1e-15
    assert abs(out[1] - 0.0001) < 1e-15


def test_outside_frozen_grid_rejected() -> None:
    with pytest.raises(e.MeasurementError, match="outside frozen grid"):
        e.candidate_returns([0.0], [0.5], [0.001], 0.6, 10)
    with pytest.raises(e.MeasurementError, match="outside frozen grid"):
        e.candidate_returns([0.0], [0.5], [0.001], 0.5, 11)


def test_identity_when_no_idle_cash() -> None:
    baseline = np.array([0.01, -0.02, 0.03])
    out, turnover, carry, friction = e.candidate_returns(
        baseline, np.zeros(3), np.full(3, 0.001), 1.0, 20
    )
    assert np.array_equal(out, baseline)
    assert np.array_equal(turnover, np.zeros(3))
    assert np.array_equal(carry, np.zeros(3))
    assert np.array_equal(friction, np.zeros(3))


def test_grid_dimensions_primary_and_no_winner_selection() -> None:
    n = 240
    dates = pd.date_range("2023-01-01", periods=n, freq="D")
    returns = np.tile(np.array([0.002, -0.001, 0.001, 0.0]), n // 4)
    equity = 10000.0 * np.cumprod(1.0 + returns)
    weights = np.zeros((n, 2))
    weights[:, 0] = 0.35
    weights[:, 1] = 0.35
    weights[::10, 0] = 0.30
    rate_dates = pd.date_range("2022-12-30", periods=40, freq="7D")
    rate_values = np.full(len(rate_dates), 5.0)
    result = e.evaluate(dates, equity, weights, rate_dates, rate_values)
    assert result["candidate_cell_count"] == 16
    assert len(result["cells"]) == 16
    assert result["primary_cell_key"] == "a050_f10bps"
    assert len(result["core_stress_cell_keys"]) == 9
    assert result["chronological_block_sizes"] == [60, 60, 60, 60]
    assert "argmax" not in result
    assert "winner" not in result


def test_engine_source_contains_no_file_or_network_io() -> None:
    source = inspect.getsource(e)
    forbidden = ["requests", "urllib", "read_csv", "read_text", "read_bytes", "subprocess", "socket"]
    for token in forbidden:
        assert token not in source
