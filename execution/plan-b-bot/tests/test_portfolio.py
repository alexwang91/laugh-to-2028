from beta_bot.portfolio import build_portfolio_plan


def test_current_beta_example_from_design():
    plan = build_portfolio_plan(
        mark_price=100_000,
        target_beta=0.47,
        external_spot_btc_qty=0.5,
        external_cash_usd=0,
        hyperliquid_equity_usd=50_000,
        current_perp_qty=0,
        rebalance_band=0.01,
        min_trade_usd=100,
        max_platform_leverage=2,
    )
    assert round(plan.nav_usd) == 100_000
    assert round(plan.target_perp_notional_usd) == -3_000
    assert not plan.target_clamped_by_leverage
    assert plan.should_rebalance


def test_platform_leverage_cap_is_applied_and_reported():
    plan = build_portfolio_plan(
        mark_price=100_000,
        target_beta=1.5,
        external_spot_btc_qty=1.0,
        external_cash_usd=0,
        hyperliquid_equity_usd=10_000,
        current_perp_qty=0,
        rebalance_band=0.01,
        min_trade_usd=100,
        max_platform_leverage=2,
    )
    assert plan.requested_target_perp_notional_usd > 20_000
    assert plan.target_perp_notional_usd == 20_000
    assert plan.platform_effective_leverage == 2
    assert plan.target_clamped_by_leverage
    assert plan.should_rebalance
    assert plan.rebalance_reason == "rebalance_required_target_clamped_by_leverage"


def test_leverage_clamp_at_reachable_limit_is_not_misreported_as_below_min_trade():
    plan = build_portfolio_plan(
        mark_price=100_000,
        target_beta=1.5,
        external_spot_btc_qty=1.0,
        external_cash_usd=0,
        hyperliquid_equity_usd=10_000,
        current_perp_qty=0.2,
        rebalance_band=0.01,
        min_trade_usd=100,
        max_platform_leverage=2,
    )
    assert plan.target_clamped_by_leverage
    assert plan.delta_notional_usd == 0
    assert not plan.should_rebalance
    assert plan.rebalance_reason == "target_unreachable_leverage_cap"
