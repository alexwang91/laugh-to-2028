from __future__ import annotations

import time
from datetime import datetime, timezone

from .account_reconciliation import (
    AccountReconciliationReport,
    build_account_reconciliation,
    transition_increases_directional_risk,
)
from .config import Settings
from .executor import execute_target_position, reconcile_persistent_orders
from .market import (
    fetch_market_snapshot,
    fetch_open_orders,
    fetch_user_fills_by_time,
    fetch_user_state,
)
from .model import build_signal
from .notify import send_telegram
from .order_ledger import LedgerUncertainState, OrderLedger
from .portfolio import build_portfolio_plan, parse_account_equity, parse_position_qty
from .product_config import load_product_config


DAY_MS = 86_400_000
ACCOUNT_RECONCILIATION_FILL_LOOKBACK_MS = DAY_MS


def _canonical_decision_timestamp_ms(last_completed_candle_start_ms: int) -> int:
    """Return the UTC decision boundary immediately after the completed daily candle."""
    if last_completed_candle_start_ms <= 0:
        raise ValueError("last_completed_candle_start_ms must be positive")
    return last_completed_candle_start_ms + DAY_MS


def _account_reconciliation(
    settings: Settings,
    *,
    target_position_qty: float,
    persistent_reconciliation: dict | None,
    user_state: dict | None = None,
) -> AccountReconciliationReport:
    if not settings.account_address:
        raise ValueError("Trading account address is missing")
    if not settings.order_ledger_path:
        raise ValueError("Account reconciliation requires ORDER_LEDGER_PATH")

    end_ms = int(time.time() * 1000)
    start_ms = end_ms - ACCOUNT_RECONCILIATION_FILL_LOOKBACK_MS
    state = user_state or fetch_user_state(
        settings.api_url,
        settings.account_address,
        settings.request_timeout_seconds,
    )
    open_orders = fetch_open_orders(
        settings.api_url,
        settings.account_address,
        settings.request_timeout_seconds,
    )
    fills = fetch_user_fills_by_time(
        settings.api_url,
        settings.account_address,
        start_ms,
        end_ms,
        settings.request_timeout_seconds,
    )
    return build_account_reconciliation(
        ledger=OrderLedger(settings.order_ledger_path),
        coin=settings.coin,
        target_position_qty=target_position_qty,
        open_orders=open_orders,
        fills=fills,
        user_state=state,
        persistent_blocking_unresolved=int(
            (persistent_reconciliation or {}).get("blocking_unresolved_after", 0)
        ),
    )


def run_strategy(settings: Settings) -> dict:
    product = load_product_config()
    snapshot = fetch_market_snapshot(
        api_url=settings.api_url,
        coin=settings.coin,
        lookback_days=settings.candle_lookback_days,
        timeout=settings.request_timeout_seconds,
    )
    decision_timestamp_ms = _canonical_decision_timestamp_ms(snapshot.last_candle_start_ms)
    decision_timestamp_utc = datetime.fromtimestamp(decision_timestamp_ms / 1000, tz=timezone.utc).isoformat()

    signal = build_signal(
        snapshot.closes,
        funding_apr=snapshot.funding_apr_24h,
        normal_cap=settings.normal_beta_cap,
        hard_cap=settings.hard_beta_cap,
        allow_strong_beta=settings.allow_strong_beta,
    )

    payload: dict = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "decision": {
            "timestamp_ms": decision_timestamp_ms,
            "timestamp_utc": decision_timestamp_utc,
            "strategy_release_id": product.strategy_release_id,
            "model_version": product.model_version,
            "data_version": product.data_version,
        },
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

    pre_persistent = None
    if settings.can_trade:
        try:
            pre_persistent = reconcile_persistent_orders(settings)
        except LedgerUncertainState as exc:
            # P1.2 uncertainty still forbids fresh risk. P1.6 deliberately turns
            # that uncertainty into a gate input instead of terminating the whole
            # cycle so a later same-direction reduction can remain available.
            pre_persistent = {
                "blocking_unresolved_after": 1,
                "reconciliation_uncertain": True,
                "error": str(exc),
            }
        payload["order_reconciliation"] = {"pre_trade": pre_persistent}

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

    pre_account = None
    if settings.can_trade:
        pre_account = _account_reconciliation(
            settings,
            target_position_qty=plan.target_perp_qty,
            persistent_reconciliation=pre_persistent,
            user_state=user_state,
        )
        payload.setdefault("account_reconciliation", {})["pre_trade"] = pre_account.to_dict()

    if not plan.should_rebalance:
        payload["result"] = plan.rebalance_reason
        payload["orders"] = []
    elif not settings.can_trade:
        payload["result"] = "shadow_rebalance_recommended"
        payload["orders"] = []
    else:
        increases_risk = transition_increases_directional_risk(
            current_qty,
            plan.target_perp_qty,
        )
        if pre_account and not pre_account.risk_increase_allowed and increases_risk:
            payload["result"] = "trade_blocked_account_reconciliation"
            payload["orders"] = []
            payload["risk_increase_blocked"] = True
        else:
            payload["risk_increase_blocked"] = False
            if pre_account and not pre_account.is_clean and not increases_risk:
                payload["reconciliation_override"] = "REDUCE_RISK_ACTION_ALLOWED"
            payload["orders"] = execute_target_position(
                settings,
                current_qty=current_qty,
                target_qty=plan.target_perp_qty,
                release_id=product.strategy_release_id,
                decision_timestamp_ms=decision_timestamp_ms,
            )
            try:
                post_persistent = reconcile_persistent_orders(settings)
            except LedgerUncertainState as exc:
                post_persistent = {
                    "blocking_unresolved_after": 1,
                    "reconciliation_uncertain": True,
                    "error": str(exc),
                }
            payload.setdefault("order_reconciliation", {})["post_trade"] = post_persistent
            post_account = _account_reconciliation(
                settings,
                target_position_qty=plan.target_perp_qty,
                persistent_reconciliation=post_persistent,
            )
            payload.setdefault("account_reconciliation", {})["post_trade"] = post_account.to_dict()
            payload["result"] = "trade_submitted_or_duplicate_suppressed"

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
