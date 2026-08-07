from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
RESEARCH_0040 = ROOT / "research" / "leverage_0040"
if str(RESEARCH_0040) not in sys.path:
    sys.path.insert(0, str(RESEARCH_0040))

from two_layer_runner import (  # noqa: E402
    TwoLayerLeverageError,
    compose_two_layer_target,
)


BASE = {"BTC": 0.40, "ETH": 0.20, "SOL": 0.10, "BNB": 0.05}


def test_cap_one_is_exact_identity_on_frozen_p3_2_target():
    result = compose_two_layer_target(
        base_target_weights=BASE,
        frozen_defensive_scale=0.75,
        leverage_multiplier=1.0,
        research_cap=1.0,
    )
    assert result.final_target_weights == BASE
    assert result.final_gross_target == sum(BASE.values())
    assert result.cash_or_financing_share == 1.0 - sum(BASE.values())
    assert result.final_scale == 0.75
    assert result.production_authorized is False


def test_multiplier_is_separate_and_proportional_after_defensive_target():
    result = compose_two_layer_target(
        base_target_weights=BASE,
        frozen_defensive_scale=0.75,
        leverage_multiplier=1.2,
        research_cap=1.2,
    )
    assert result.final_target_weights == {
        asset: value * 1.2 for asset, value in BASE.items()
    }
    assert result.final_gross_target == pytest.approx(sum(BASE.values()) * 1.2)
    assert result.final_scale == pytest.approx(0.75 * 1.2)


def test_fixed_multiplier_preserves_defensive_monotonicity():
    high_risk = compose_two_layer_target(
        base_target_weights={asset: value * 0.4 for asset, value in BASE.items()},
        frozen_defensive_scale=0.4,
        leverage_multiplier=1.2,
        research_cap=1.2,
    )
    low_risk = compose_two_layer_target(
        base_target_weights={asset: value * 0.8 for asset, value in BASE.items()},
        frozen_defensive_scale=0.8,
        leverage_multiplier=1.2,
        research_cap=1.2,
    )
    assert high_risk.final_scale < low_risk.final_scale
    assert high_risk.final_gross_target < low_risk.final_gross_target


def test_rejects_attempt_to_extend_frozen_defensive_scale_above_one():
    with pytest.raises(TwoLayerLeverageError, match="defensive_scale"):
        compose_two_layer_target(
            base_target_weights=BASE,
            frozen_defensive_scale=1.01,
            leverage_multiplier=1.0,
            research_cap=1.0,
        )


def test_rejects_multiplier_outside_preregistered_cap():
    with pytest.raises(TwoLayerLeverageError, match="leverage_multiplier"):
        compose_two_layer_target(
            base_target_weights=BASE,
            frozen_defensive_scale=0.75,
            leverage_multiplier=1.21,
            research_cap=1.20,
        )


def test_rejects_search_cap_above_0040_domain():
    with pytest.raises(TwoLayerLeverageError, match="research_cap"):
        compose_two_layer_target(
            base_target_weights=BASE,
            frozen_defensive_scale=0.75,
            leverage_multiplier=1.0,
            research_cap=1.31,
        )


def test_rejects_short_or_noncanonical_target_input():
    with pytest.raises(TwoLayerLeverageError, match="short"):
        compose_two_layer_target(
            base_target_weights={"BTC": -0.1, "ETH": 0.2, "SOL": 0.1, "BNB": 0.0},
            frozen_defensive_scale=0.5,
            leverage_multiplier=1.0,
            research_cap=1.0,
        )

    with pytest.raises(TwoLayerLeverageError, match="exactly"):
        compose_two_layer_target(
            base_target_weights={"BTC": 0.5, "ETH": 0.2, "SOL": 0.1},
            frozen_defensive_scale=0.5,
            leverage_multiplier=1.0,
            research_cap=1.0,
        )


def test_rejects_non_p3_2_base_gross_above_one():
    with pytest.raises(TwoLayerLeverageError, match="base P3.2 target gross"):
        compose_two_layer_target(
            base_target_weights={"BTC": 0.6, "ETH": 0.3, "SOL": 0.2, "BNB": 0.0},
            frozen_defensive_scale=1.0,
            leverage_multiplier=1.0,
            research_cap=1.0,
        )
