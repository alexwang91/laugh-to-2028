from __future__ import annotations

import time
from typing import Any

from eth_account import Account
from hyperliquid.exchange import Exchange

from .config import Settings


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


def execute_target_position(
    settings: Settings,
    current_qty: float,
    target_qty: float,
) -> list[dict[str, Any]]:
    """Move a BTC perp position to the target with reduce-only closes where possible."""
    if not settings.api_private_key or not settings.master_address:
        raise ValueError("Trading credentials are missing")

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

    epsilon = 1e-8
    if abs(target_qty - current_qty) <= epsilon:
        return actions

    same_direction = current_qty == 0 or target_qty == 0 or (current_qty > 0) == (target_qty > 0)

    if same_direction:
        delta = target_qty - current_qty
        reducing = current_qty != 0 and abs(target_qty) < abs(current_qty)
        if reducing:
            response = exchange.market_close(
                settings.coin,
                sz=_round_size(abs(delta)),
                slippage=slippage,
            )
            actions.append({"action": "reduce", "size": abs(delta), "status": _extract_status(response)})
        else:
            response = exchange.market_open(
                settings.coin,
                is_buy=delta > 0,
                sz=_round_size(delta),
                slippage=slippage,
            )
            actions.append({"action": "increase", "size": abs(delta), "status": _extract_status(response)})
        return actions

    # Reversal: close the existing position first, then open the target direction.
    close_response = exchange.market_close(
        settings.coin,
        sz=_round_size(current_qty),
        slippage=slippage,
    )
    actions.append({"action": "close_for_reversal", "size": abs(current_qty), "status": _extract_status(close_response)})

    open_response = exchange.market_open(
        settings.coin,
        is_buy=target_qty > 0,
        sz=_round_size(target_qty),
        slippage=slippage,
    )
    actions.append({"action": "open_reversal", "size": abs(target_qty), "status": _extract_status(open_response)})
    return actions
