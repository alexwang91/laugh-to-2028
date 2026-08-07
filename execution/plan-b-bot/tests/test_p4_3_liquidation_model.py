from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "leverage_0040"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

from liquidation_model import (  # noqa: E402
    LiquidationModelError,
    active_margin_tier,
    evaluate_cross_margin_state,
    load_frozen_snapshot,
    maintenance_margin_usd,
    margin_tiers,
    uniform_long_down_liquidation_distance,
)


SPEC = ROOT / "research" / "leverage_0040" / "P4_3_LIQUIDATION_MODEL_V1.json"


def test_liquidation_contract_is_frozen_pre_result_and_cross_only():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    assert spec["model_id"] == "P4.3-HYPERLIQUID-CROSS-LIQUIDATION-V1"
    assert spec["status"] == "FROZEN_BEFORE_FIRST_LEVERAGE_0040_RUN"
    assert spec["margin_mode"] == "cross"
    assert spec["portfolio_margin_supported"] is False
    assert spec["isolated_margin_supported"] is False
    assert spec["production_authorized"] is False
    assert spec["leverage_search_run"] is False
    assert spec["frozen_margin_snapshot"]["relevant_margin_inputs_sha256"] == (
        "38060892f1976315084de4dc4ed1c9f3885d909ffccc47bce7ad589315d8b9dd"
    )


def test_frozen_snapshot_and_first_tier_mmr_match_official_rule():
    snapshot = load_frozen_snapshot()
    assert snapshot["captured_at_utc"] == "2026-08-07T09:11:25Z"
    expected = {"BTC": 40, "ETH": 25, "SOL": 20, "BNB": 10}
    for asset, max_leverage in expected.items():
        first = margin_tiers(asset, snapshot)[0]
        assert first.lower_bound_usd == 0.0
        assert first.max_leverage == max_leverage
        assert first.maintenance_margin_rate == pytest.approx(1.0 / (2.0 * max_leverage))
        assert first.maintenance_deduction_usd == 0.0


def test_tier_maintenance_margin_is_continuous_at_frozen_boundaries():
    snapshot = load_frozen_snapshot()
    boundaries = {"BTC": 150_000_000.0, "ETH": 100_000_000.0, "SOL": 70_000_000.0, "BNB": 3_000_000.0}
    for asset, boundary in boundaries.items():
        tiers = margin_tiers(asset, snapshot)
        assert len(tiers) == 2
        lower = tiers[0]
        upper = tiers[1]
        assert upper.lower_bound_usd == boundary
        left_formula = boundary * lower.maintenance_margin_rate - lower.maintenance_deduction_usd
        right_formula = boundary * upper.maintenance_margin_rate - upper.maintenance_deduction_usd
        assert right_formula == pytest.approx(left_formula, abs=1e-8)
        assert maintenance_margin_usd(asset, boundary, snapshot) == pytest.approx(left_formula, abs=1e-8)
        assert active_margin_tier(asset, boundary, snapshot) == upper


def test_single_position_uniform_distance_matches_official_liquidation_price_formula():
    # BTC stays in the first 40x-max-leverage tier. Official Hyperliquid formula:
    # liq_price = price - margin_available / size / (1 - l) for a long,
    # l = maintenance margin rate = 1/(2*maxLeverage).
    notional = 10_000.0
    equity = 1_000.0
    mmr = 1.0 / 80.0
    current_mm = notional * mmr
    margin_available = equity - current_mm
    expected_liq_price_ratio = 1.0 - (margin_available / notional) / (1.0 - mmr)
    expected_drop = 1.0 - expected_liq_price_ratio

    result = uniform_long_down_liquidation_distance(
        current_cross_account_equity_usd=equity,
        current_long_perp_notionals_usd={"BTC": notional},
    )
    assert result.liquidates_within_domain is True
    assert result.uniform_down_move_fraction == pytest.approx(expected_drop, abs=1e-12)
    assert result.state_at_boundary is not None
    assert abs(result.state_at_boundary.margin_buffer_usd) < 1e-7


def test_cross_margin_stress_sums_per_asset_maintenance_and_pnl():
    state = evaluate_cross_margin_state(
        current_cross_account_equity_usd=2_000.0,
        current_long_perp_notionals_usd={"BTC": 800.0, "ETH": 400.0, "BNB": 200.0},
        relative_mark_returns={"BTC": -0.10, "ETH": -0.20, "BNB": -0.30},
    )
    expected_equity = 2_000.0 - 80.0 - 80.0 - 60.0
    assert state.account_equity_usd == pytest.approx(expected_equity)
    assert state.stressed_abs_notionals_usd == {
        "BTC": pytest.approx(720.0),
        "ETH": pytest.approx(320.0),
        "BNB": pytest.approx(140.0),
    }
    expected_mm = 720.0 / 80.0 + 320.0 / 50.0 + 140.0 / 20.0
    assert state.maintenance_margin_usd == pytest.approx(expected_mm)
    assert state.margin_buffer_usd == pytest.approx(expected_equity - expected_mm)
    assert state.liquidatable is False


def test_no_perp_position_has_no_liquidation_distance():
    result = uniform_long_down_liquidation_distance(
        current_cross_account_equity_usd=2_000.0,
        current_long_perp_notionals_usd={},
    )
    assert result.liquidates_within_domain is False
    assert result.stress_scale is None
    assert result.uniform_down_move_fraction is None


def test_liquidation_model_fails_closed_on_unsupported_or_ambiguous_inputs():
    with pytest.raises(LiquidationModelError, match="positive"):
        evaluate_cross_margin_state(
            current_cross_account_equity_usd=0.0,
            current_long_perp_notionals_usd={"BTC": 100.0},
            relative_mark_returns={"BTC": 0.0},
        )
    with pytest.raises(LiquidationModelError, match="short"):
        evaluate_cross_margin_state(
            current_cross_account_equity_usd=1_000.0,
            current_long_perp_notionals_usd={"BTC": -100.0},
            relative_mark_returns={"BTC": 0.0},
        )
    with pytest.raises(LiquidationModelError, match="exactly match"):
        evaluate_cross_margin_state(
            current_cross_account_equity_usd=1_000.0,
            current_long_perp_notionals_usd={"BTC": 100.0, "ETH": 100.0},
            relative_mark_returns={"BTC": -0.1},
        )
    with pytest.raises(LiquidationModelError, match="Unsupported asset"):
        maintenance_margin_usd("XRP", 100.0)


def test_uniform_distance_is_monotone_with_more_perp_notional_at_same_equity():
    low = uniform_long_down_liquidation_distance(
        current_cross_account_equity_usd=2_000.0,
        current_long_perp_notionals_usd={"BTC": 1_000.0},
    )
    high = uniform_long_down_liquidation_distance(
        current_cross_account_equity_usd=2_000.0,
        current_long_perp_notionals_usd={"BTC": 2_000.0},
    )
    assert low.uniform_down_move_fraction is not None
    assert high.uniform_down_move_fraction is not None
    assert high.uniform_down_move_fraction < low.uniform_down_move_fraction
