from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from beta_bot.data_contract import CanonicalDailyDataset, DailyClose
from beta_bot.product_config import load_product_config
from beta_bot.target_engine import (
    MODEL_AUTHORITY,
    TARGET_ENGINE_VERSION,
    TargetCalculationError,
    calculate_target,
)


ASSETS = ("BTC", "ETH", "SOL", "BNB", "XRP")


def _synthetic_dataset(days: int = 1120) -> CanonicalDailyDataset:
    start = pd.Timestamp("2022-01-01", tz="UTC")
    t = np.arange(days, dtype=float)
    log_returns = {
        "BTC": 0.00055 + 0.0100 * np.sin(t / 31.0) + 0.0030 * np.cos(t / 97.0),
        "ETH": 0.00065 + 0.0120 * np.sin(t / 27.0 + 0.4) + 0.0040 * np.cos(t / 83.0),
        "SOL": 0.00075 + 0.0160 * np.sin(t / 23.0 + 0.8) + 0.0050 * np.cos(t / 71.0),
        "BNB": 0.00045 + 0.0080 * np.sin(t / 37.0 + 0.2) + 0.0025 * np.cos(t / 101.0),
        "XRP": 0.00035 + 0.0140 * np.sin(t / 29.0 + 1.1) + 0.0045 * np.cos(t / 67.0),
    }
    bases = {"BTC": 20000.0, "ETH": 1200.0, "SOL": 20.0, "BNB": 250.0, "XRP": 0.4}
    symbols = {asset: f"{asset}USDT" for asset in ASSETS}
    closes_by_asset: dict[str, tuple[DailyClose, ...]] = {}

    for asset in ASSETS:
        prices = bases[asset] * np.exp(np.cumsum(log_returns[asset]))
        rows = []
        for offset, close in enumerate(prices):
            session = start + pd.Timedelta(days=offset)
            session_ms = int(session.timestamp() * 1000)
            rows.append(
                DailyClose(
                    asset=asset,
                    source_symbol=symbols[asset],
                    session_open_ms=session_ms,
                    close_time_ms=session_ms + 86_400_000 - 1,
                    close=float(close),
                )
            )
        closes_by_asset[asset] = tuple(rows)

    last = start + pd.Timedelta(days=days - 1)
    decision = last + pd.Timedelta(days=1)
    return CanonicalDailyDataset(
        schema_version=2,
        contract_id="BRRK-DATA-CONTRACT-P3.1-R1-2026-08-06",
        decision_timestamp=decision.isoformat().replace("+00:00", "Z"),
        common_start_ms=int(start.timestamp() * 1000),
        latest_session_open_ms=int(last.timestamp() * 1000),
        closes_by_asset=closes_by_asset,
    )


@pytest.fixture(scope="module")
def synthetic_dataset() -> CanonicalDailyDataset:
    return _synthetic_dataset()


@pytest.fixture(scope="module")
def zero_position_result(synthetic_dataset: CanonicalDailyDataset):
    return calculate_target(
        daily_dataset=synthetic_dataset,
        account_equity_usd=10_000.0,
        current_positions={},
        approved_config=load_product_config(),
    )


def test_p3_2_target_is_long_only_gross_capped_and_auditable(zero_position_result):
    result = zero_position_result
    assert result.model_authority == MODEL_AUTHORITY == "BRRK-0011"
    assert result.target_engine_version == TARGET_ENGINE_VERSION
    assert result.production_authorized is False
    assert tuple(result.target_weights) == ("BTC", "ETH", "SOL", "BNB")
    assert all(value >= 0.0 for value in result.target_weights.values())
    assert 0.0 <= result.base_gross_target <= 1.0
    assert result.base_gross_target == pytest.approx(sum(result.target_weights.values()), abs=1e-12)
    assert result.cash_share == pytest.approx(1.0 - result.base_gross_target, abs=1e-12)
    assert 0.0 <= result.defensive_scale <= 1.0
    assert 0.0 <= result.meta_scale <= 1.0
    assert 0.0 <= result.riskoff_probability <= 1.0
    assert sum(result.risk_state_probabilities.values()) == pytest.approx(1.0, abs=1e-8)
    if result.base_gross_target > 0:
        assert sum(result.relative_weights.values()) == pytest.approx(1.0, abs=1e-10)
    assert result.feature_snapshot["internal_band_is_not_p3_3_execution_control"] is True


def test_current_positions_are_context_only_not_p3_2_rebalance_logic(
    synthetic_dataset: CanonicalDailyDataset,
    zero_position_result,
):
    changed_positions = {"BTC": 5000.0, "ETH": -250.0, "SOL": 125.0, "BNB": 75.0}
    second = calculate_target(
        daily_dataset=synthetic_dataset,
        account_equity_usd=10_000.0,
        current_positions=changed_positions,
        approved_config=load_product_config(),
    )
    assert second.target_weights == pytest.approx(zero_position_result.target_weights, abs=1e-12)
    assert second.base_gross_target == pytest.approx(zero_position_result.base_gross_target, abs=1e-12)
    assert second.defensive_scale == pytest.approx(zero_position_result.defensive_scale, abs=1e-12)
    assert second.risk_state_probabilities == pytest.approx(
        zero_position_result.risk_state_probabilities, abs=1e-12
    )
    assert second.current_positions_notional_usd == changed_positions


def test_p3_2_rejects_feature_only_asset_as_position_input(synthetic_dataset: CanonicalDailyDataset):
    with pytest.raises(TargetCalculationError, match="outside the approved target universe"):
        calculate_target(
            daily_dataset=synthetic_dataset,
            account_equity_usd=10_000.0,
            current_positions={"XRP": 10.0},
            approved_config=load_product_config(),
        )


def test_p3_2_requires_exact_d_minus_one_session(synthetic_dataset: CanonicalDailyDataset):
    invalid = replace(
        synthetic_dataset,
        latest_session_open_ms=synthetic_dataset.latest_session_open_ms - 86_400_000,
    )
    with pytest.raises(TargetCalculationError, match="latest_session_open_ms"):
        calculate_target(
            daily_dataset=invalid,
            account_equity_usd=10_000.0,
            current_positions={},
            approved_config=load_product_config(),
        )


def test_p3_2_rejects_nonpositive_equity_before_model_work(synthetic_dataset: CanonicalDailyDataset):
    with pytest.raises(TargetCalculationError, match="must be positive"):
        calculate_target(
            daily_dataset=synthetic_dataset,
            account_equity_usd=0.0,
            current_positions={},
            approved_config=load_product_config(),
        )
