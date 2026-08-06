from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PortfolioPlan:
    nav_usd: float
    mark_price: float
    external_spot_notional_usd: float
    external_cash_usd: float
    hyperliquid_equity_usd: float
    current_perp_qty: float
    current_perp_notional_usd: float
    current_beta: float
    target_beta: float
    requested_target_perp_notional_usd: float
    target_perp_qty: float
    target_perp_notional_usd: float
    delta_perp_qty: float
    delta_notional_usd: float
    platform_effective_leverage: float
    target_clamped_by_leverage: bool
    should_rebalance: bool
    rebalance_reason: str

    def to_dict(self) -> dict:
        return asdict(self)


def parse_account_equity(user_state: dict[str, Any]) -> float:
    margin_summary = user_state.get("marginSummary") or user_state.get("crossMarginSummary") or {}
    return float(margin_summary.get("accountValue") or 0.0)


def parse_position_qty(user_state: dict[str, Any], coin: str) -> float:
    for item in user_state.get("assetPositions", []):
        position = item.get("position", {})
        if position.get("coin") == coin:
            return float(position.get("szi") or 0.0)
    return 0.0


def build_portfolio_plan(
    *,
    mark_price: float,
    target_beta: float,
    external_spot_btc_qty: float,
    external_cash_usd: float,
    hyperliquid_equity_usd: float,
    current_perp_qty: float,
    rebalance_band: float,
    min_trade_usd: float,
    max_platform_leverage: float,
) -> PortfolioPlan:
    if mark_price <= 0:
        raise ValueError("mark_price must be positive")

    spot_notional = external_spot_btc_qty * mark_price
    current_perp_notional = current_perp_qty * mark_price
    nav = spot_notional + external_cash_usd + hyperliquid_equity_usd
    if nav <= 0:
        raise ValueError("Total strategy NAV must be positive")

    target_total_notional = target_beta * nav
    requested_target_perp_notional = target_total_notional - spot_notional
    target_perp_notional = requested_target_perp_notional
    target_clamped_by_leverage = False

    max_perp_notional = max_platform_leverage * hyperliquid_equity_usd
    if hyperliquid_equity_usd <= 0 and abs(target_perp_notional) > 0:
        target_perp_notional = 0.0
        target_clamped_by_leverage = True
    elif abs(target_perp_notional) > max_perp_notional:
        target_perp_notional = max_perp_notional if target_perp_notional > 0 else -max_perp_notional
        target_clamped_by_leverage = True

    target_perp_qty = target_perp_notional / mark_price
    delta_qty = target_perp_qty - current_perp_qty
    delta_notional = delta_qty * mark_price
    current_beta = (spot_notional + current_perp_notional) / nav
    platform_leverage = abs(target_perp_notional) / hyperliquid_equity_usd if hyperliquid_equity_usd > 0 else 0.0

    beta_gap = abs(target_beta - current_beta)
    if target_clamped_by_leverage and abs(delta_notional) < min_trade_usd:
        should_rebalance = False
        reason = "target_unreachable_leverage_cap"
    elif beta_gap < rebalance_band:
        should_rebalance = False
        reason = "inside_beta_band"
    elif abs(delta_notional) < min_trade_usd:
        should_rebalance = False
        reason = "below_min_trade"
    elif target_clamped_by_leverage:
        should_rebalance = True
        reason = "rebalance_required_target_clamped_by_leverage"
    else:
        should_rebalance = True
        reason = "rebalance_required"

    return PortfolioPlan(
        nav_usd=nav,
        mark_price=mark_price,
        external_spot_notional_usd=spot_notional,
        external_cash_usd=external_cash_usd,
        hyperliquid_equity_usd=hyperliquid_equity_usd,
        current_perp_qty=current_perp_qty,
        current_perp_notional_usd=current_perp_notional,
        current_beta=current_beta,
        target_beta=target_beta,
        requested_target_perp_notional_usd=requested_target_perp_notional,
        target_perp_qty=target_perp_qty,
        target_perp_notional_usd=target_perp_notional,
        delta_perp_qty=delta_qty,
        delta_notional_usd=delta_notional,
        platform_effective_leverage=platform_leverage,
        target_clamped_by_leverage=target_clamped_by_leverage,
        should_rebalance=should_rebalance,
        rebalance_reason=reason,
    )
