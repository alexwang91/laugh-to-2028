from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable

from .fill_transition import FillTransitionError, build_fill_transition
from .order_ledger import LedgerUncertainState, OrderLedger, reconcile_unresolved_orders
from .portfolio import parse_position_qty


TOLERANCE = 1e-8
ACTIVE_EXCHANGE_STATUSES = {"open", "triggered"}

OPEN_ORDER_RECOVERED = "COLD_OPEN_ORDER_RECOVERED"
PARTIAL_FILL_RECOVERED = "COLD_PARTIAL_FILL_RECOVERED"
UNKNOWN_SUBMIT_RECOVERED = "COLD_UNKNOWN_SUBMIT_RESULT_RECOVERED"
UNKNOWN_SUBMIT_BLOCKED = "COLD_UNKNOWN_SUBMIT_RESULT_BLOCKED"
STALE_POSITION_OVERRIDDEN = "COLD_STALE_POSITION_OVERRIDDEN_BY_EXCHANGE"


@dataclass(frozen=True)
class RestartRecoveryReport:
    coin: str
    actual_position_qty: float
    local_position_expectation_qty: float | None
    position_truth_source: str
    recovery_cases: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    blocking_unresolved_after: int
    persistent_reconciliation: dict[str, Any]
    risk_increase_allowed: bool

    @property
    def is_resolved(self) -> bool:
        return not self.blocking_reasons

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"is_resolved": self.is_resolved}


def _latest_fill_implied_position(
    ledger: OrderLedger, coin: str
) -> tuple[float | None, list[dict[str, Any]]]:
    transitions: list[dict[str, Any]] = []
    local_expectation: float | None = None
    for row in ledger.orders_for_asset(coin):
        try:
            transition = build_fill_transition(row).to_dict()
        except FillTransitionError:
            # An unresolved/malformed row remains visible through the blocking ledger
            # state. It must not be converted into a guessed position expectation.
            continue
        transitions.append(transition)
        if (
            local_expectation is None
            and transition.get("position_tracking_status") == "available"
            and transition.get("actual_position_qty_from_fills") is not None
        ):
            local_expectation = float(transition["actual_position_qty_from_fills"])
    return local_expectation, transitions


def recover_cold_start(
    *,
    ledger: OrderLedger,
    coin: str,
    user_state: dict[str, Any],
    query_order_status: Callable[[str], dict[str, Any]],
    fetch_fills_by_time: Callable[[int, int], list[dict[str, Any]]],
    now_ms: int | None = None,
) -> RestartRecoveryReport:
    """Recover durable execution truth before any new economic submission.

    This function never submits, cancels, or resizes an order. It only replays
    exchange/account truth into the durable ledger and classifies the cold-start
    condition. Therefore repeated calls are economically idempotent.

    A still-unknown prior submission is a safe *blocked* resolution: the function
    records that new risk cannot resume and never converts unknownOid into a retry.
    Fresh clearinghouse position always wins over stale fill-implied local position.
    """
    before = ledger.unresolved_orders()
    prior_unknown_attempt_cloids = {
        str(row["cloid"])
        for row in before
        if row.get("submission_attempt_timestamp_ms") is not None
        and row.get("exchange_oid") is None
    }

    reconciliation_error: str | None = None
    try:
        persistent = reconcile_unresolved_orders(
            ledger,
            query_order_status=query_order_status,
            fetch_fills_by_time=fetch_fills_by_time,
            now_ms=now_ms,
        )
    except LedgerUncertainState as exc:
        # P1.7 resolves uncertainty by making it explicit and blocking new risk;
        # it does not blind-retry. Non-uncertainty LedgerError failures propagate.
        reconciliation_error = str(exc)
        persistent = {
            "unresolved_before": len(before),
            "reconciled": 0,
            "unresolved_after": len(ledger.unresolved_orders()),
            "blocking_unresolved_after": len(ledger.blocking_unresolved_orders()),
            "reconciliation_uncertain": True,
            "error": reconciliation_error,
        }

    after = ledger.orders_for_asset(coin)
    cases: list[str] = []
    for row in after:
        status = row.get("last_exchange_status")
        submitted = float(row.get("submitted_quantity") or 0.0)
        filled = float(row.get("fill_quantity") or 0.0)
        if status in ACTIVE_EXCHANGE_STATUSES:
            if filled <= TOLERANCE:
                cases.append(OPEN_ORDER_RECOVERED)
            elif filled < submitted - TOLERANCE:
                cases.append(PARTIAL_FILL_RECOVERED)

    if prior_unknown_attempt_cloids:
        recovered_unknown = any(
            str(row.get("cloid")) in prior_unknown_attempt_cloids
            and row.get("exchange_oid") is not None
            for row in after
        )
        still_unknown = any(
            str(row.get("cloid")) in prior_unknown_attempt_cloids
            and row.get("exchange_oid") is None
            for row in after
        )
        if recovered_unknown:
            cases.append(UNKNOWN_SUBMIT_RECOVERED)
        if still_unknown:
            cases.append(UNKNOWN_SUBMIT_BLOCKED)

    actual_position = parse_position_qty(user_state, coin)
    local_expectation, _transitions = _latest_fill_implied_position(ledger, coin)
    if (
        local_expectation is not None
        and abs(local_expectation - actual_position) > TOLERANCE
    ):
        cases.append(STALE_POSITION_OVERRIDDEN)

    blockers = ledger.blocking_unresolved_orders()
    reasons: list[str] = []
    if blockers:
        reasons.append("RESTART_BLOCKING_UNRESOLVED_ORDER")
    if reconciliation_error is not None:
        reasons.append("RESTART_RECONCILIATION_UNCERTAIN")
    if UNKNOWN_SUBMIT_BLOCKED in cases:
        reasons.append("RESTART_UNKNOWN_SUBMIT_RESULT")

    normalized_cases = tuple(dict.fromkeys(cases))
    normalized_reasons = tuple(dict.fromkeys(reasons))
    return RestartRecoveryReport(
        coin=coin,
        actual_position_qty=actual_position,
        local_position_expectation_qty=local_expectation,
        position_truth_source="fresh_clearinghouse_state",
        recovery_cases=normalized_cases,
        blocking_reasons=normalized_reasons,
        blocking_unresolved_after=len(blockers),
        persistent_reconciliation=persistent,
        risk_increase_allowed=not normalized_reasons,
    )
