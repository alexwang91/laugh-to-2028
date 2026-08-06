from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .order_ledger import OrderLedger
from .portfolio import parse_position_qty


TOLERANCE = 1e-8
ACTIVE_EXCHANGE_STATUSES = {"open", "triggered"}


class AccountReconciliationError(RuntimeError):
    """Account/exchange/local truth could not be parsed safely."""


@dataclass(frozen=True)
class AccountReconciliationReport:
    coin: str
    actual_position_qty: float
    target_position_qty: float
    target_gap_qty: float
    account_equity_usd: float
    total_margin_used_usd: float
    exchange_open_order_cloids: tuple[str, ...]
    local_active_order_cloids: tuple[str, ...]
    recent_fill_count: int
    blocking_reasons: tuple[str, ...]
    risk_increase_allowed: bool

    @property
    def is_clean(self) -> bool:
        return not self.blocking_reasons

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"is_clean": self.is_clean}


def transition_increases_directional_risk(current_qty: float, target_qty: float) -> bool:
    """True when reaching target requires opening/increasing directional exposure."""
    if abs(target_qty) <= TOLERANCE:
        return False
    if abs(current_qty) <= TOLERANCE:
        return True
    if (current_qty > 0) != (target_qty > 0):
        return True
    return abs(target_qty) > abs(current_qty) + TOLERANCE


def _parse_margin(user_state: dict[str, Any]) -> tuple[float, float]:
    summary = user_state.get("marginSummary") or user_state.get("crossMarginSummary")
    if not isinstance(summary, dict):
        raise AccountReconciliationError("clearinghouseState has no margin summary")
    try:
        equity = float(summary["accountValue"])
        margin_used = float(summary["totalMarginUsed"])
    except (KeyError, TypeError, ValueError) as exc:
        raise AccountReconciliationError(
            "clearinghouseState margin summary lacks valid accountValue/totalMarginUsed"
        ) from exc
    if equity < 0 or margin_used < 0:
        raise AccountReconciliationError("negative account equity/margin is not trusted")
    return equity, margin_used


def _exchange_open_cloids(open_orders: list[dict[str, Any]], coin: str) -> set[str]:
    result: set[str] = set()
    for row in open_orders:
        if not isinstance(row, dict):
            raise AccountReconciliationError("openOrders contains malformed row")
        if row.get("coin") != coin:
            continue
        cloid = row.get("cloid")
        if not isinstance(cloid, str) or not cloid:
            raise AccountReconciliationError(
                f"open {coin} order has no CLOID and cannot be correlated to local truth"
            )
        result.add(cloid.lower())
    return result


def _local_active_cloids(ledger: OrderLedger, coin: str) -> set[str]:
    result: set[str] = set()
    for row in ledger.unresolved_orders():
        if row.get("asset") != coin:
            continue
        if row.get("last_exchange_status") in ACTIVE_EXCHANGE_STATUSES:
            result.add(str(row["cloid"]).lower())
    return result


def build_account_reconciliation(
    *,
    ledger: OrderLedger,
    coin: str,
    target_position_qty: float,
    open_orders: list[dict[str, Any]],
    fills: list[dict[str, Any]],
    user_state: dict[str, Any],
    persistent_blocking_unresolved: int = 0,
) -> AccountReconciliationReport:
    """Cross-check exchange account truth against ledger and current target.

    Recent fills are already persisted/cross-checked by the P1.2 reconciliation pass.
    Here they are fetched again as account-level evidence and structurally validated;
    open-order correlation and position/equity/margin truth determine the risk gate.
    """
    equity, margin_used = _parse_margin(user_state)
    actual_qty = parse_position_qty(user_state, coin)
    exchange_open = _exchange_open_cloids(open_orders, coin)
    local_active = _local_active_cloids(ledger, coin)

    relevant_fills = []
    for fill in fills:
        if not isinstance(fill, dict):
            raise AccountReconciliationError("user fills contain malformed row")
        if fill.get("coin") == coin:
            if fill.get("oid") is None or fill.get("tid") is None:
                raise AccountReconciliationError(
                    f"{coin} fill lacks oid/tid and cannot be audited"
                )
            relevant_fills.append(fill)

    reasons: list[str] = []
    unknown_exchange = sorted(exchange_open - local_active)
    missing_exchange = sorted(local_active - exchange_open)
    if unknown_exchange:
        reasons.append("EXCHANGE_OPEN_ORDER_NOT_IN_LOCAL_ACTIVE_LEDGER")
    if missing_exchange:
        reasons.append("LOCAL_ACTIVE_ORDER_NOT_OPEN_AT_EXCHANGE")
    if persistent_blocking_unresolved > 0:
        reasons.append("PERSISTENT_ORDER_RECONCILIATION_UNRESOLVED")

    risk_increase_allowed = not reasons
    return AccountReconciliationReport(
        coin=coin,
        actual_position_qty=actual_qty,
        target_position_qty=float(target_position_qty),
        target_gap_qty=float(target_position_qty) - actual_qty,
        account_equity_usd=equity,
        total_margin_used_usd=margin_used,
        exchange_open_order_cloids=tuple(sorted(exchange_open)),
        local_active_order_cloids=tuple(sorted(local_active)),
        recent_fill_count=len(relevant_fills),
        blocking_reasons=tuple(reasons),
        risk_increase_allowed=risk_increase_allowed,
    )
