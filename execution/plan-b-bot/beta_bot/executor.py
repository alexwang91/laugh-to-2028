from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.utils.types import Cloid

from .config import Settings
from .order_identity import OrderIdentity, build_order_identity, canonical_target_revision


def _round_size(size: float, decimals: int = 5) -> float:
    rounded = round(abs(size), decimals)
    if rounded <= 0:
        raise ValueError("Rounded order size is zero")
    return rounded


def _extract_status(response: dict[str, Any]) -> str:
    if response.get("status") != "ok":
        raise RuntimeError(f"Hyperliquid order failed: {response}")
    statuses = response.get("response", {}).get("data", {}).get("statuses", [])
    if not statuses:
        return "ok"
    status = statuses[0]
    if "error" in status:
        raise RuntimeError(f"Hyperliquid order rejected: {status['error']}")
    if "filled" in status:
        return "filled"
    if "resting" in status:
        return "resting"
    return str(status)


def _existing_order_status(exchange: Exchange, account_address: str, cloid: Cloid) -> str | None:
    """Return a prior order status for this cloid, or None when it has never existed.

    Hyperliquid's orderStatus endpoint returns unknownOid for a missing oid/cloid and
    status=order for any known order, including terminal states. Any unexpected response
    fails closed so a transient/malformed lookup cannot cause an accidental duplicate.
    """
    response = exchange.info.query_order_by_cloid(account_address, cloid)
    response_status = response.get("status") if isinstance(response, dict) else None
    if response_status == "unknownOid":
        return None
    if response_status == "order":
        order = response.get("order") or {}
        return str(order.get("status") or "order")
    raise RuntimeError(f"Unexpected Hyperliquid orderStatus response for cloid {cloid}: {response}")


def _submit_once(
    *,
    exchange: Exchange,
    account_address: str,
    identity: OrderIdentity,
    submit: Callable[[Cloid], dict[str, Any]],
) -> tuple[str, str | None]:
    """Submit one economic order at most once for sequential replay/restart attempts.

    The exchange-visible cloid is the durable idempotency key. A restart reconstructs
    the same cloid from the same economic decision, queries exchange history, and skips
    submission if that cloid already exists. Cross-process concurrent submission races
    are intentionally not claimed here; persistent coordination belongs to later Phase 1.
    """
    cloid = Cloid.from_str(identity.cloid)
    existing = _existing_order_status(exchange, account_address, cloid)
    if existing is not None:
        return "duplicate_suppressed", existing
    response = submit(cloid)
    return _extract_status(response), None


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


def execute_target_position(
    settings: Settings,
    current_qty: float,
    target_qty: float,
    *,
    release_id: str,
    decision_timestamp_ms: int,
) -> list[dict[str, Any]]:
    """Move a BTC perp position to the target with deterministic exchange order IDs."""
    if not settings.api_private_key or not settings.master_address:
        raise ValueError("Trading credentials are missing")
    if not settings.account_address:
        raise ValueError("Trading account address is missing")

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
        intent = "reduce" if reducing else "increase"
        identity = _identity(
            release_id=release_id,
            decision_timestamp_ms=decision_timestamp_ms,
            asset=settings.coin,
            side=side,
            intent=intent,
            target_revision=target_revision,
        )

        if reducing:
            status, existing_status = _submit_once(
                exchange=exchange,
                account_address=settings.account_address,
                identity=identity,
                submit=lambda cloid: exchange.market_close(
                    settings.coin,
                    sz=_round_size(abs(delta)),
                    slippage=slippage,
                    cloid=cloid,
                ),
            )
        else:
            status, existing_status = _submit_once(
                exchange=exchange,
                account_address=settings.account_address,
                identity=identity,
                submit=lambda cloid: exchange.market_open(
                    settings.coin,
                    is_buy=delta > 0,
                    sz=_round_size(delta),
                    slippage=slippage,
                    cloid=cloid,
                ),
            )
        action = {
            "action": intent,
            "size": abs(delta),
            "status": status,
            "order_identity": identity.to_dict(),
        }
        if existing_status is not None:
            action["existing_order_status"] = existing_status
        actions.append(action)
        return actions

    # Reversal route labels remain observable, but identity uses route-independent
    # economic intents. This lets a restart after the close leg reconstruct the same
    # increase cloid that the original reversal would have used for the open leg.
    close_side = "sell" if current_qty > 0 else "buy"
    close_identity = _identity(
        release_id=release_id,
        decision_timestamp_ms=decision_timestamp_ms,
        asset=settings.coin,
        side=close_side,
        intent="reduce",
        target_revision=target_revision,
    )
    close_status, close_existing_status = _submit_once(
        exchange=exchange,
        account_address=settings.account_address,
        identity=close_identity,
        submit=lambda cloid: exchange.market_close(
            settings.coin,
            sz=_round_size(current_qty),
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
    open_status, open_existing_status = _submit_once(
        exchange=exchange,
        account_address=settings.account_address,
        identity=open_identity,
        submit=lambda cloid: exchange.market_open(
            settings.coin,
            is_buy=target_qty > 0,
            sz=_round_size(target_qty),
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
