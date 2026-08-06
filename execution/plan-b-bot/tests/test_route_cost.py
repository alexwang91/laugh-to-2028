import pytest

from beta_bot.route_cost import (
    FeeSchedule,
    RouteCostError,
    RouteObservation,
    compare_spot_perp,
    estimate_route_cost,
    funding_break_even_hours,
)


def obs(route, **overrides):
    values = dict(
        asset="BTC",
        route=route,
        notional_usd=1000.0,
        holding_hours=24.0,
        order_style="taker",
        spread_bps=1.0,
        entry_slippage_bps=0.5,
        exit_slippage_bps=0.5,
        live_depth_usd=100_000.0,
        vwap_impact_bps=0.2,
        funding_bps_per_hour=0.0,
        entry_basis_bps=0.0,
        expected_exit_basis_bps=0.0,
        custody_redemption_bps=0.0,
    )
    values.update(overrides)
    return RouteObservation(**values)


def test_default_fee_schedule_matches_hyperliquid_tier0_base_rates():
    fees = FeeSchedule()
    assert fees.perp_taker_bps == 4.5
    assert fees.perp_maker_bps == 1.5
    assert fees.spot_taker_bps == 7.0
    assert fees.spot_maker_bps == 4.0


def test_spot_round_trip_cost_has_no_funding_or_basis():
    estimate = estimate_route_cost(obs("spot", custody_redemption_bps=0.4))
    assert estimate.execution_fee_bps == 14.0
    assert estimate.funding_cost_bps == 0.0
    assert estimate.basis_cost_bps == 0.0
    assert estimate.total_cost_bps == pytest.approx(16.6)
    assert estimate.total_cost_usd == pytest.approx(1.66)
    assert estimate.notional_to_depth_ratio == pytest.approx(0.01)


def test_perp_positive_funding_accumulates_with_holding_horizon():
    short = estimate_route_cost(obs("perp", holding_hours=24, funding_bps_per_hour=0.10))
    long = estimate_route_cost(obs("perp", holding_hours=240, funding_bps_per_hour=0.10))
    assert short.funding_cost_bps == pytest.approx(2.4)
    assert long.funding_cost_bps == pytest.approx(24.0)
    assert long.total_cost_bps - short.total_cost_bps == pytest.approx(21.6)


def test_negative_funding_is_a_long_benefit():
    estimate = estimate_route_cost(obs("perp", funding_bps_per_hour=-0.10))
    assert estimate.funding_cost_bps == pytest.approx(-2.4)


def test_basis_compression_is_a_cost_to_perp_long():
    estimate = estimate_route_cost(
        obs("perp", entry_basis_bps=8.0, expected_exit_basis_bps=2.0)
    )
    assert estimate.basis_cost_bps == pytest.approx(6.0)


def test_same_exposure_comparison_can_flip_with_holding_horizon():
    fees = FeeSchedule()
    spot_1h = obs("spot", holding_hours=1, spread_bps=1.0)
    perp_1h = obs("perp", holding_hours=1, spread_bps=1.0, funding_bps_per_hour=0.2)
    short = compare_spot_perp(spot_1h, perp_1h, fees=fees)
    assert short.lower_cost_route == "perp"

    spot_100h = obs("spot", holding_hours=100, spread_bps=1.0)
    perp_100h = obs("perp", holding_hours=100, spread_bps=1.0, funding_bps_per_hour=0.2)
    long = compare_spot_perp(spot_100h, perp_100h, fees=fees)
    assert long.lower_cost_route == "spot"


def test_break_even_horizon_is_explicit():
    # Tier-0 taker fees alone give spot a 5 bps round-trip disadvantage.
    assert funding_break_even_hours(
        spot_nonfunding_cost_bps=14.0,
        perp_nonfunding_cost_bps=9.0,
        positive_funding_bps_per_hour=0.125,
    ) == pytest.approx(40.0)
    assert funding_break_even_hours(
        spot_nonfunding_cost_bps=9.0,
        perp_nonfunding_cost_bps=10.0,
        positive_funding_bps_per_hour=0.125,
    ) == 0.0
    assert funding_break_even_hours(
        spot_nonfunding_cost_bps=14.0,
        perp_nonfunding_cost_bps=9.0,
        positive_funding_bps_per_hour=0.0,
    ) is None


def test_comparison_requires_same_asset_notional_and_horizon():
    with pytest.raises(RouteCostError, match="same asset"):
        compare_spot_perp(obs("spot"), obs("perp", asset="ETH"))
    with pytest.raises(RouteCostError, match="equal economic notional"):
        compare_spot_perp(obs("spot"), obs("perp", notional_usd=900))
    with pytest.raises(RouteCostError, match="equal holding horizon"):
        compare_spot_perp(obs("spot"), obs("perp", holding_hours=12))


def test_spot_cannot_smuggle_in_funding():
    with pytest.raises(RouteCostError, match="spot route cannot carry perp funding"):
        estimate_route_cost(obs("spot", funding_bps_per_hour=0.1))
