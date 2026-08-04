from __future__ import annotations

from datetime import datetime, timezone

from .config import Settings
from .executor import execute_target_position
from .market import fetch_market_snapshot, fetch_user_state
from .model import build_signal
from .notify import send_telegram
from .portfolio import build_portfolio_plan, parse_account_equity, parse_position_qty


def run_strategy(settings: Settings) -> dict:
    snapshot = fetch_market_snapshot(
        api_url=settings.api_url,
        coin=settings.coin,
        lookback_days=settings.candle_lookback_days,
        timeout=settings.request_timeout_seconds,
    )
    signal = build_signal(
        snapshot.closes,
        funding_apr=snapshot.funding_apr_24h,
        normal_cap=settings.normal_beta_cap,
        hard_cap=settings.hard_beta_cap,
        allow_strong_beta=settings.allow_strong_beta,
    )

    payload: dict = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "network": settings.network,
        "mode": settings.trading_mode,
        "coin": settings.coin,
        "market": {
            "mark_price": snapshot.mark_price,
            "current_hourly_funding": snapshot.current_hourly_funding,
            "funding_apr_24h": snapshot.funding_apr_24h,
            "last_completed_candle_start_ms": snapshot.last_candle_start_ms,
        },
        "signal": signal.to_dict(),
    }

    if not settings.account_address:
        payload["result"] = "market_only_no_account_configured"
        payload["plan"] = None
        send_telegram(settings, payload)
        return payload

    user_state = fetch_user_state(
        settings.api_url,
        settings.account_address,
        settings.request_timeout_seconds,
    )
    equity = parse_account_equity(user_state)
    current_qty = parse_position_qty(user_state, settings.coin)

    plan = build_portfolio_plan(
        mark_price=snapshot.mark_price,
        target_beta=signal.target_beta,
        external_spot_btc_qty=settings.external_spot_btc_qty,
        external_cash_usd=settings.external_cash_usd,
        hyperliquid_equity_usd=equity,
        current_perp_qty=current_qty,
        rebalance_band=settings.rebalance_band,
        min_trade_usd=settings.min_trade_usd,
        max_platform_leverage=settings.max_platform_leverage,
    )
    payload["plan"] = plan.to_dict()

    if not plan.should_rebalance:
        payload["result"] = plan.rebalance_reason
        payload["orders"] = []
    elif not settings.can_trade:
        payload["result"] = "shadow_rebalance_recommended"
        payload["orders"] = []
    else:
        payload["orders"] = execute_target_position(
            settings,
            current_qty=current_qty,
            target_qty=plan.target_perp_qty,
        )
        payload["result"] = "trade_submitted"

    send_telegram(settings, payload)
    return payload


def run_public_market_status(settings: Settings) -> dict:
    snapshot = fetch_market_snapshot(
        api_url=settings.api_url,
        coin=settings.coin,
        lookback_days=settings.candle_lookback_days,
        timeout=settings.request_timeout_seconds,
    )
    signal = build_signal(
        snapshot.closes,
        funding_apr=snapshot.funding_apr_24h,
        normal_cap=settings.normal_beta_cap,
        hard_cap=settings.hard_beta_cap,
        allow_strong_beta=settings.allow_strong_beta,
    )
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "network": settings.network,
        "coin": settings.coin,
        "mark_price": snapshot.mark_price,
        "signal": signal.to_dict(),
    }
