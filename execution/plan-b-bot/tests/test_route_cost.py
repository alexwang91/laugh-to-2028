import pytest

from beta_bot.route_cost import (
    FeeSchedule,
    RouteCostError,
    RouteObservation,
    analyze_l2_book,
    average_funding_bps_per_hour,
    basis_bps,
    compare_spot_perp,
    estimate_route_cost,
    funding_break_even_hours,
    funding_decimal_to_bps_per_hour,
    observation_from_l2_book,
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


def book(*, bid_levels=None, ask_levels=None):
    return {
        "coin": "BTC",
        "time": 1,
        "levels": [
            bid_levels or [{"px": "99.9", "sz": "5"}, {"px": "99.7", "sz": "5"}],
            ask_levels or [{"px": "100.1", "sz": "5"}, {"px": "100.3", "sz": "5"}],
        ],
    }


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
    assert estimate.total_cost_bps == pytest.approx(16.4)
    assert estimate.total_cost_usd == pytest.approx(1.64)
    assert estimate.notional_to_depth_ratio == pytest.approx(0.01)


def test_spot_rejects_perp_basis_or_funding():
    with pytest.raises(RouteCostError, match="spot route cannot carry perp funding"):
        estimate_route_cost(obs("spot", funding_bps_per_hour=0.1))
    with pytest.raises(RouteCostError, match="spot route cannot carry perp basis"):
        estimate_route_cost(obs("spot", entry_basis_bps=1.0))


def test_vwap_impact_is_diagnostic_not_double_counted():
    low = estimate_route_cost(obs("spot", vwap_impact_bps=0.2))
    high = estimate_route_cost(obs("spot", vwap_impact_bps=9.0))
    assert low.total_cost_bps == high.total_cost_bps
    assert low.observed_vwap_impact_bps == pytest.approx(0.2)
    assert high.observed_vwap_impact_bps == pytest.approx(9.0)


def test_perp_positive_funding_accumulates_with_holding_horizon():
    short = estimate_route_cost(obs("perp", holding_hours=24, funding_bps_per_hour=0.10))
    long = estimate_route_cost(obs("perp", holding_hours=240, funding_bps_per_hour=0.10))
    assert short.funding_cost_bps == pytest.approx(2.4)
    assert long.funding_cost_bps == pytest.approx(24.0)
    assert long.total_cost_bps - short.total_cost_bps == pytest.approx(21.6)


def test_negative_funding_is_a_long_benefit():
    estimate = estimate_route_cost(obs("perp", funding_bps_per_hour=-0.10))
    assert estimate.funding_cost_bps == pytest.approx(-2.4)


def test_hyperliquid_funding_decimal_is_explicitly_converted_to_bps_per_hour():
    assert funding_decimal_to_bps_per_hour(0.0000125) == pytest.approx(0.125)
    assert average_funding_bps_per_hour([0.00001, 0.00002]) == pytest.approx(0.15)
    with pytest.raises(RouteCostError, match="at least one"):
        average_funding_bps_per_hour([])


def test_basis_is_measured_perp_relative_to_verified_spot():
    assert basis_bps(perp_price=100.10, verified_spot_price=100.0) == pytest.approx(10.0)
    assert basis_bps(perp_price=99.90, verified_spot_price=100.0) == pytest.approx(-10.0)


def test_basis_compression_is_a_cost_to_perp_long():
    estimate = estimate_route_cost(obs("perp", entry_basis_bps=8.0, expected_exit_basis_bps=2.0))
    assert estimate.basis_cost_bps == pytest.approx(6.0)


def test_same_exposure_comparison_can_flip_with_holding_horizon():
    fees = FeeSchedule()
    short = compare_spot_perp(
        obs("spot", holding_hours=1),
        obs("perp", holding_hours=1, funding_bps_per_hour=0.2),
        fees=fees,
    )
    assert short.lower_cost_route == "perp"
    long = compare_spot_perp(
        obs("spot", holding_hours=100),
        obs("perp", holding_hours=100, funding_bps_per_hour=0.2),
        fees=fees,
    )
    assert long.lower_cost_route == "spot"


def test_break_even_horizon_is_explicit():
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


def test_l2_book_top_level_execution_equals_spread_only():
    diagnostics = analyze_l2_book(book(), notional_usd=100.0)
    assert diagnostics.mid_price == pytest.approx(100.0)
    assert diagnostics.spread_bps == pytest.approx(20.0)
    assert diagnostics.buy_vwap == pytest.approx(100.1)
    assert diagnostics.sell_vwap == pytest.approx(99.9)
    assert diagnostics.entry_slippage_beyond_half_spread_bps == pytest.approx(0.0)
    assert diagnostics.exit_slippage_beyond_half_spread_bps == pytest.approx(0.0)
    assert diagnostics.round_trip_vwap_impact_bps == pytest.approx(20.0)


def test_l2_book_vwap_consumption_measures_beyond_spread_slippage():
    snapshot = book(
        bid_levels=[{"px": "99.9", "sz": "0.5"}, {"px": "99.7", "sz": "3"}],
        ask_levels=[{"px": "100.1", "sz": "0.5"}, {"px": "100.3", "sz": "3"}],
    )
    diagnostics = analyze_l2_book(snapshot, notional_usd=200.0)
    assert diagnostics.target_quantity == pytest.approx(2.0)
    assert diagnostics.buy_vwap == pytest.approx(100.25)
    assert diagnostics.sell_vwap == pytest.approx(99.75)
    assert diagnostics.entry_slippage_beyond_half_spread_bps == pytest.approx(15.0)
    assert diagnostics.exit_slippage_beyond_half_spread_bps == pytest.approx(15.0)
    assert diagnostics.two_sided_depth_usd > 300.0

    observation = observation_from_l2_book(
        asset="BTC",
        route="perp",
        book=snapshot,
        notional_usd=200.0,
        holding_hours=24,
        funding_bps_per_hour=0.125,
        entry_basis_bps=3.0,
        expected_exit_basis_bps=1.0,
    )
    estimate = estimate_route_cost(observation)
    assert observation.spread_bps == pytest.approx(20.0)
    assert observation.entry_slippage_bps == pytest.approx(15.0)
    assert observation.exit_slippage_bps == pytest.approx(15.0)
    assert estimate.funding_cost_bps == pytest.approx(3.0)
    assert estimate.basis_cost_bps == pytest.approx(2.0)


def test_l2_book_fails_closed_when_returned_depth_cannot_fill_target():
    shallow = book(
        bid_levels=[{"px": "99.9", "sz": "0.1"}],
        ask_levels=[{"px": "100.1", "sz": "0.1"}],
    )
    with pytest.raises(RouteCostError, match="exceeds returned l2Book depth"):
        analyze_l2_book(shallow, notional_usd=1000.0)


def test_l2_book_rejects_crossed_or_malformed_snapshot():
    with pytest.raises(RouteCostError, match="crossed or locked"):
        analyze_l2_book(
            book(
                bid_levels=[{"px": "100.1", "sz": "1"}],
                ask_levels=[{"px": "100.0", "sz": "1"}],
            ),
            notional_usd=100.0,
        )
    with pytest.raises(RouteCostError, match="bid and ask"):
        analyze_l2_book({"levels": []}, notional_usd=100.0)
