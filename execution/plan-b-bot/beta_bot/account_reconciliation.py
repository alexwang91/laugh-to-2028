from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .order_ledger import OrderLedger
from .portfolio import parse_position_qty


TOLERANCE = 1e-8
ACTIVE_EXCHANGE_STATUSES = {"open", "triggered"}


class AccountReconciliationError(RuntimeError):
    """Core account truth could not be parsed safely enough to classify risk."""


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


def _exchange_open_cloids(
    open_orders: list[dict[str, Any]], coin: str
) -> tuple[set[str], list[str]]:
    result: set[str] = set()
    reasons: list[str] = []
    for row in open_orders:
        if not isinstance(row, dict):
            reasons.append("EXCHANGE_OPEN_ORDER_UNAUDITABLE")
            continue
        if row.get("coin") != coin:
            continue
        cloid = row.get("cloid")
        if not isinstance(cloid, str) or not cloid:
            reasons.append("EXCHANGE_OPEN_ORDER_UNCORRELATABLE")
            continue
        result.add(cloid.lower())
    return result, reasons


def _local_active_cloids(ledger: OrderLedger, coin: str) -> set[str]:
    result: set[str] = set()
    for row in ledger.unresolved_orders():
        if row.get("asset") != coin:
            continue
        if row.get("last_exchange_status") in ACTIVE_EXCHANGE_STATUSES:
            result.add(str(row["cloid"]).lower())
    return result


def _audit_recent_fills(fills: list[dict[str, Any]], coin: str) -> tuple[int, list[str]]:
    count = 0
    reasons: list[str] = []
    for fill in fills:
        if not isinstance(fill, dict):
            reasons.append("RECENT_FILL_UNAUDITABLE")
            continue
        if fill.get("coin") != coin:
            continue
        count += 1
        if fill.get("oid") is None or fill.get("tid") is None:
            reasons.append("RECENT_FILL_UNCORRELATABLE")
    return count, reasons


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
    """Cross-check account truth against local execution truth and current target.

    P1.2 remains responsible for detailed order/fill persistence and OID/TID
    reconstruction. This account-level pass independently fetches the cycle evidence
    required by P1.6 and converts unexplained exchange discrepancies into reason codes.
    Reason codes block risk-increasing transitions, but they are deliberately not raised
    as global exceptions so same-direction reduce-risk actions remain available.

    Core account state (position/equity/margin) is different: if it cannot be parsed,
    directional-risk classification itself is not trustworthy and the cycle fails closed.
    """
    equity, margin_used = _parse_margin(user_state)
    actual_qty = parse_position_qty(user_state, coin)
    exchange_open, open_reasons = _exchange_open_cloids(open_orders, coin)
    local_active = _local_active_cloids(ledger, coin)
    recent_fill_count, fill_reasons = _audit_recent_fills(fills, coin)

    reasons: list[str] = [*open_reasons, *fill_reasons]
    unknown_exchange = sorted(exchange_open - local_active)
    missing_exchange = sorted(local_active - exchange_open)
    if unknown_exchange:
        reasons.append("EXCHANGE_OPEN_ORDER_NOT_IN_LOCAL_ACTIVE_LEDGER")
    if missing_exchange:
        reasons.append("LOCAL_ACTIVE_ORDER_NOT_OPEN_AT_EXCHANGE")
    if persistent_blocking_unresolved > 0:
        reasons.append("PERSISTENT_ORDER_RECONCILIATION_UNRESOLVED")

    # Stable unique reason ordering keeps reports deterministic and audit-friendly.
    normalized_reasons = tuple(dict.fromkeys(reasons))
    return AccountReconciliationReport(
        coin=coin,
        actual_position_qty=actual_qty,
        target_position_qty=float(target_position_qty),
        target_gap_qty=float(target_position_qty) - actual_qty,
        account_equity_usd=equity,
        total_margin_used_usd=margin_used,
        exchange_open_order_cloids=tuple(sorted(exchange_open)),
        local_active_order_cloids=tuple(sorted(local_active)),
        recent_fill_count=recent_fill_count,
        blocking_reasons=normalized_reasons,
        risk_increase_allowed=not normalized_reasons,
    )
