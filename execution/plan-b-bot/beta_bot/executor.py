from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.utils.types import Cloid

from .config import Settings
from .fill_transition import FillTransitionError, build_fill_transition
from .market import fetch_order_status, fetch_user_fills_by_time
from .order_identity import OrderIdentity, build_order_identity, canonical_target_revision
from .order_ledger import LedgerIntent, LedgerUncertainState, OrderLedger, reconcile_unresolved_orders


def _round_size(size: float, decimals: int = 5) -> float:
    rounded = round(abs(size), decimals)
    if rounded <= 0:
        raise ValueError("Rounded order size is zero")
    return rounded


def _parse_submission_response(response: dict[str, Any]) -> tuple[str, str | None, str | None]:
    if not isinstance(response, dict):
        raise LedgerUncertainState(f"Malformed Hyperliquid submission response: {response}")
    if response.get("status") != "ok":
        return "rejected", None, f"hyperliquid_response:{response}"
    statuses = response.get("response", {}).get("data", {}).get("statuses", [])
    if not statuses:
        return "ok", None, None
    status = statuses[0]
    if not isinstance(status, dict):
        raise LedgerUncertainState(f"Malformed Hyperliquid order status: {status}")
    if "error" in status:
        return "rejected", None, str(status["error"])
    if "filled" in status:
        filled = status["filled"] or {}
        oid = filled.get("oid") if isinstance(filled, dict) else None
        return "filled", str(oid) if oid is not None else None, None
    if "resting" in status:
        resting = status["resting"] or {}
        oid = resting.get("oid") if isinstance(resting, dict) else None
        return "resting", str(oid) if oid is not None else None, None
    raise LedgerUncertainState(f"Unrecognized Hyperliquid order status: {status}")


def _extract_status(response: dict[str, Any]) -> str:
    status, _oid, reject_reason = _parse_submission_response(response)
    if status == "rejected":
        raise RuntimeError(f"Hyperliquid order rejected: {reject_reason}")
    return status


def _query_existing_order(exchange: Exchange, account_address: str, cloid: Cloid) -> dict[str, Any] | None:
    """Return exact Hyperliquid orderStatus truth, or None when the CLOID is unknown."""
    response = exchange.info.query_order_by_cloid(account_address, cloid)
    response_status = response.get("status") if isinstance(response, dict) else None
    if response_status == "unknownOid":
        return None
    if response_status == "order":
        envelope = response.get("order") or {}
        if not isinstance(envelope, dict) or not isinstance(envelope.get("order"), dict):
            raise RuntimeError(f"Malformed Hyperliquid orderStatus response for cloid {cloid}: {response}")
        if not isinstance(envelope.get("status"), str):
            raise RuntimeError(f"Malformed Hyperliquid orderStatus response for cloid {cloid}: {response}")
        return response
    raise RuntimeError(f"Unexpected Hyperliquid orderStatus response for cloid {cloid}: {response}")


def _existing_order_status(exchange: Exchange, account_address: str, cloid: Cloid) -> str | None:
    """Compatibility helper used by tests and diagnostics."""
    response = _query_existing_order(exchange, account_address, cloid)
    if response is None:
        return None
    return str(response["order"]["status"])


def _submit_once(
    *,
    exchange: Exchange,
    account_address: str,
    ledger: OrderLedger,
    intent: LedgerIntent,
    submit: Callable[[Cloid], dict[str, Any]],
) -> tuple[str, str | None]:
    """Persist-before-submit and suppress/recover one deterministic economic order.

    Durable ordering is intentional:
      intent -> exchange CLOID lookup -> durable submission-attempt marker -> network submit.
    If a prior attempt exists and the exchange later says unknownOid, P1.2 does not retry.
    That retry policy belongs to a later lifecycle task; this path fails closed instead.
    """
    identity = intent.identity
    local = ledger.record_intent(intent)
    cloid = Cloid.from_str(identity.cloid)
    try:
        existing = _query_existing_order(exchange, account_address, cloid)
    except Exception as exc:
        ledger.record_reconciliation_uncertainty(
            identity.cloid, "pre_submit_order_status_lookup_failed", str(exc)
        )
        raise

    if existing is not None:
        existing_status = ledger.record_exchange_discovery(identity.cloid, existing)
        return "duplicate_suppressed", existing_status

    if local["submission_attempt_timestamp_ms"] is not None:
        ledger.record_reconciliation_uncertainty(
            identity.cloid,
            "unknown_oid_after_durable_submission_attempt",
            {"submission_attempt_timestamp_ms": local["submission_attempt_timestamp_ms"]},
        )
        raise LedgerUncertainState(
            f"CLOID {identity.cloid} is unknown at exchange after a prior submission attempt; blind retry is forbidden"
        )

    ledger.record_submission_attempt(identity.cloid)
    try:
        response = submit(cloid)
    except Exception as exc:
        ledger.record_submission_unknown(identity.cloid, exc)
        raise

    try:
        status, exchange_oid, reject_reason = _parse_submission_response(response)
    except Exception as exc:
        ledger.record_submission_response(
            identity.cloid,
            response if isinstance(response, dict) else {"raw": str(response)},
            "unrecognized",
        )
        ledger.record_reconciliation_uncertainty(
            identity.cloid, "unrecognized_submission_response", str(exc)
        )
        raise

    ledger.record_submission_response(
        identity.cloid,
        response,
        status,
        exchange_oid=exchange_oid,
        reject_reason=reject_reason,
    )
    if status == "rejected":
        raise RuntimeError(f"Hyperliquid order rejected: {reject_reason}")
    return status, None


def _identity(
    *,
    release_id: str,
    decision_timestamp_ms: int,
    asset: str,
    side: str,
    intent: str,
    target_revision: str,
) -> OrderIdentity:
    return build_order_identity(
        release_id=release_id,
        decision_timestamp_ms=decision_timestamp_ms,
        asset=asset,
        side=side,
        intent=intent,
        target_revision=target_revision,
    )


def _open_ledger(settings: Settings) -> OrderLedger:
    if not settings.order_ledger_path:
        raise LedgerUncertainState("Trade execution requires a configured persistent order ledger")
    return OrderLedger(settings.order_ledger_path)


def reconcile_persistent_orders(settings: Settings) -> dict[str, Any]:
    """Reconstruct unresolved rows and expose actual-fill-driven position progress."""
    if not settings.account_address:
        raise ValueError("Trading account address is missing")
    ledger = _open_ledger(settings)
    tracked_cloids = [row["cloid"] for row in ledger.unresolved_orders()]
    result = reconcile_unresolved_orders(
        ledger,
        query_order_status=lambda cloid: fetch_order_status(
            settings.api_url,
            settings.account_address or "",
            cloid,
            settings.request_timeout_seconds,
        ),
        fetch_fills_by_time=lambda start_ms, end_ms: fetch_user_fills_by_time(
            settings.api_url,
            settings.account_address or "",
            start_ms,
            end_ms,
            settings.request_timeout_seconds,
        ),
    )

    transitions: list[dict[str, Any]] = []
    for cloid in tracked_cloids:
        row = ledger.get_order(cloid)
        if row is None:
            continue
        try:
            transitions.append(build_fill_transition(row).to_dict())
        except FillTransitionError as exc:
            ledger.record_reconciliation_uncertainty(
                cloid, "fill_transition_failed", str(exc)
            )
            raise LedgerUncertainState(
                f"CLOID {cloid} cannot produce trustworthy actual-fill position progress: {exc}"
            ) from exc
    result["fill_transitions"] = transitions
    return result


def _ledger_intent(
    *,
    identity: OrderIdentity,
    route_action: str,
    quantity: float,
    parameters: dict[str, Any],
) -> LedgerIntent:
    return LedgerIntent(
        identity=identity,
        route_action=route_action,
        submitted_quantity=quantity,
        submitted_order_parameters=parameters,
    )


def execute_target_position(
    settings: Settings,
    current_qty: float,
    target_qty: float,
    *,
    release_id: str,
    decision_timestamp_ms: int,
) -> list[dict[str, Any]]:
    """Move a BTC perp position to the target with durable deterministic order truth."""
    if not settings.api_private_key or not settings.master_address:
        raise ValueError("Trading credentials are missing")
    if not settings.account_address:
        raise ValueError("Trading account address is missing")

    # Open and integrity-check durable state before any exchange write action.
    ledger = _open_ledger(settings)

    wallet = Account.from_key(settings.api_private_key)
    exchange = Exchange(
        wallet,
        settings.api_url,
        vault_address=settings.vault_address,
        account_address=settings.master_address,
        timeout=settings.request_timeout_seconds,
    )
    exchange.set_expires_after(int(time.time() * 1000) + 30_000)
    exchange.update_leverage(settings.max_platform_leverage, settings.coin, True)
    slippage = settings.max_slippage_bps / 10_000
    actions: list[dict[str, Any]] = []
    target_revision = canonical_target_revision(target_qty)

    epsilon = 1e-8
    if abs(target_qty - current_qty) <= epsilon:
        return actions

    same_direction = current_qty == 0 or target_qty == 0 or (current_qty > 0) == (target_qty > 0)

    if same_direction:
        delta = target_qty - current_qty
        side = "buy" if delta > 0 else "sell"
        reducing = current_qty != 0 and abs(target_qty) < abs(current_qty)
        intent_name = "reduce" if reducing else "increase"
        identity = _identity(
            release_id=release_id,
            decision_timestamp_ms=decision_timestamp_ms,
            asset=settings.coin,
            side=side,
            intent=intent_name,
            target_revision=target_revision,
        )
        quantity = _round_size(abs(delta))

        transition_metadata = {
            "position_before_qty": current_qty,
            "target_position_qty": target_qty,
            "position_tracking_source": "pre_trade_exchange_position",
        }
        if reducing:
            ledger_intent = _ledger_intent(
                identity=identity,
                route_action="reduce",
                quantity=quantity,
                parameters={
                    "method": "market_close",
                    "coin": settings.coin,
                    "size": quantity,
                    "slippage": slippage,
                    "reduce_only_semantics": True,
                    **transition_metadata,
                },
            )
            status, existing_status = _submit_once(
                exchange=exchange,
                account_address=settings.account_address,
                ledger=ledger,
                intent=ledger_intent,
                submit=lambda cloid: exchange.market_close(
                    settings.coin,
                    sz=quantity,
                    slippage=slippage,
                    cloid=cloid,
                ),
            )
        else:
            ledger_intent = _ledger_intent(
                identity=identity,
                route_action="increase",
                quantity=quantity,
                parameters={
                    "method": "market_open",
                    "coin": settings.coin,
                    "is_buy": delta > 0,
                    "size": quantity,
                    "slippage": slippage,
                    **transition_metadata,
                },
            )
            status, existing_status = _submit_once(
                exchange=exchange,
                account_address=settings.account_address,
                ledger=ledger,
                intent=ledger_intent,
                submit=lambda cloid: exchange.market_open(
                    settings.coin,
                    is_buy=delta > 0,
                    sz=quantity,
                    slippage=slippage,
                    cloid=cloid,
                ),
            )
        action = {
            "action": intent_name,
            "size": abs(delta),
            "status": status,
            "order_identity": identity.to_dict(),
        }
        if existing_status is not None:
            action["existing_order_status"] = existing_status
        actions.append(action)
        return actions

    # P1.3 records actual-fill position progress for each leg but deliberately does not
    # solve P1.4 reversal safety. The close leg has a known pre-trade baseline. The open
    # leg's baseline is intentionally unavailable until a future fresh reconciliation
    # proves the close leg's actual result; P1.3 therefore never assumes it is zero.
    close_side = "sell" if current_qty > 0 else "buy"
    close_identity = _identity(
        release_id=release_id,
        decision_timestamp_ms=decision_timestamp_ms,
        asset=settings.coin,
        side=close_side,
        intent="reduce",
        target_revision=target_revision,
    )
    close_quantity = _round_size(current_qty)
    close_ledger_intent = _ledger_intent(
        identity=close_identity,
        route_action="close_for_reversal",
        quantity=close_quantity,
        parameters={
            "method": "market_close",
            "coin": settings.coin,
            "size": close_quantity,
            "slippage": slippage,
            "reduce_only_semantics": True,
            "position_before_qty": current_qty,
            "target_position_qty": 0.0,
            "position_tracking_source": "pre_trade_exchange_position",
        },
    )
    close_status, close_existing_status = _submit_once(
        exchange=exchange,
        account_address=settings.account_address,
        ledger=ledger,
        intent=close_ledger_intent,
        submit=lambda cloid: exchange.market_close(
            settings.coin,
            sz=close_quantity,
            slippage=slippage,
            cloid=cloid,
        ),
    )
    close_action = {
        "action": "close_for_reversal",
        "size": abs(current_qty),
        "status": close_status,
        "order_identity": close_identity.to_dict(),
    }
    if close_existing_status is not None:
        close_action["existing_order_status"] = close_existing_status
    actions.append(close_action)

    open_side = "buy" if target_qty > 0 else "sell"
    open_identity = _identity(
        release_id=release_id,
        decision_timestamp_ms=decision_timestamp_ms,
        asset=settings.coin,
        side=open_side,
        intent="increase",
        target_revision=target_revision,
    )
    open_quantity = _round_size(target_qty)
    open_ledger_intent = _ledger_intent(
        identity=open_identity,
        route_action="open_reversal",
        quantity=open_quantity,
        parameters={
            "method": "market_open",
            "coin": settings.coin,
            "is_buy": target_qty > 0,
            "size": open_quantity,
            "slippage": slippage,
            "position_before_qty": None,
            "target_position_qty": target_qty,
            "position_tracking_source": "requires_p1_4_reversal_reconciliation",
        },
    )
    open_status, open_existing_status = _submit_once(
        exchange=exchange,
        account_address=settings.account_address,
        ledger=ledger,
        intent=open_ledger_intent,
        submit=lambda cloid: exchange.market_open(
            settings.coin,
            is_buy=target_qty > 0,
            sz=open_quantity,
            slippage=slippage,
            cloid=cloid,
        ),
    )
    open_action = {
        "action": "open_reversal",
        "size": abs(target_qty),
        "status": open_status,
        "order_identity": open_identity.to_dict(),
    }
    if open_existing_status is not None:
        open_action["existing_order_status"] = open_existing_status
    actions.append(open_action)
    return actions
