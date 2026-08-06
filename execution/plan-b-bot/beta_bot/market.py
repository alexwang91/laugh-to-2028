from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import requests


@dataclass(frozen=True)
class MarketSnapshot:
    closes: list[float]
    mark_price: float
    current_hourly_funding: float
    funding_apr_24h: float
    last_candle_start_ms: int


def _post(api_url: str, payload: dict[str, Any], timeout: float) -> Any:
    response = requests.post(f"{api_url}/info", json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fetch_perp_metadata(api_url: str, timeout: float) -> dict[str, Any]:
    result = _post(api_url, {"type": "meta"}, timeout)
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected Hyperliquid meta response: {result}")
    return result


def fetch_spot_metadata(api_url: str, timeout: float) -> dict[str, Any]:
    """Fetch Hyperliquid spotMeta used to resolve token and pair indexes at runtime."""
    result = _post(api_url, {"type": "spotMeta"}, timeout)
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected spotMeta response: {result}")
    tokens = result.get("tokens")
    universe = result.get("universe")
    if not isinstance(tokens, list) or not isinstance(universe, list):
        raise RuntimeError(f"Unexpected spotMeta shape: {result}")
    return result


def fetch_l2_book(api_url: str, coin: str, timeout: float) -> dict[str, Any]:
    """Fetch one canonical Hyperliquid L2 snapshot for a perp or spot asset ID.

    Perp callers pass the canonical coin name. Spot callers pass the runtime
    `@{spot_pair_index}` identity resolved from `spotMeta`; UI display names are
    not substituted here because HyperCore spot names may be remapped.
    """
    result = _post(api_url, {"type": "l2Book", "coin": coin}, timeout)
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected l2Book response: {result}")
    levels = result.get("levels")
    if not isinstance(levels, list) or len(levels) != 2:
        raise RuntimeError(f"Unexpected l2Book levels: {result}")
    if not all(isinstance(side, list) for side in levels):
        raise RuntimeError(f"Unexpected l2Book side shape: {result}")
    return result


def fetch_open_orders(api_url: str, account_address: str, timeout: float) -> list[dict[str, Any]]:
    result = _post(api_url, {"type": "openOrders", "user": account_address}, timeout)
    if not isinstance(result, list):
        raise RuntimeError(f"Unexpected openOrders response: {result}")
    return result


def fetch_completed_daily_closes(
    api_url: str,
    coin: str,
    lookback_days: int,
    timeout: float,
) -> tuple[list[float], int]:
    now_ms = int(time.time() * 1000)
    start_ms = now_ms - lookback_days * 86_400_000
    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": coin,
            "interval": "1d",
            "startTime": start_ms,
            "endTime": now_ms,
        },
    }
    candles = _post(api_url, payload, timeout)
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_start_ms = int(today_start.timestamp() * 1000)

    completed = [c for c in candles if int(c["T"]) < today_start_ms]
    completed.sort(key=lambda item: int(item["t"]))
    if len(completed) < 242:
        raise RuntimeError(f"Only {len(completed)} completed daily candles were returned")
    closes = [float(c["c"]) for c in completed]
    return closes, int(completed[-1]["t"])


def fetch_asset_context(api_url: str, coin: str, timeout: float) -> tuple[float, float]:
    meta, contexts = _post(api_url, {"type": "metaAndAssetCtxs"}, timeout)
    universe = meta["universe"]
    for index, asset in enumerate(universe):
        if asset["name"] == coin:
            context = contexts[index]
            return float(context["markPx"]), float(context.get("funding") or 0.0)
    raise RuntimeError(f"Asset context not found for {coin}")


def fetch_funding_apr_24h(api_url: str, coin: str, timeout: float) -> float:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - 25 * 60 * 60 * 1000
    records = _post(
        api_url,
        {"type": "fundingHistory", "coin": coin, "startTime": start_ms, "endTime": end_ms},
        timeout,
    )
    rates = [float(item["fundingRate"]) for item in records[-24:] if item.get("fundingRate") is not None]
    if not rates:
        return 0.0
    average_hourly = sum(rates) / len(rates)
    return average_hourly * 24 * 365


def fetch_user_state(api_url: str, account_address: str, timeout: float) -> dict[str, Any]:
    result = _post(
        api_url,
        {"type": "clearinghouseState", "user": account_address},
        timeout,
    )
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected clearinghouseState response: {result}")
    return result


def fetch_order_status(
    api_url: str,
    account_address: str,
    cloid: str,
    timeout: float,
) -> dict[str, Any]:
    return _post(
        api_url,
        {"type": "orderStatus", "user": account_address, "oid": cloid},
        timeout,
    )


def fetch_user_fills_by_time(
    api_url: str,
    account_address: str,
    start_time_ms: int,
    end_time_ms: int,
    timeout: float,
) -> list[dict[str, Any]]:
    result = _post(
        api_url,
        {
            "type": "userFillsByTime",
            "user": account_address,
            "startTime": int(start_time_ms),
            "endTime": int(end_time_ms),
            "aggregateByTime": False,
        },
        timeout,
    )
    if not isinstance(result, list):
        raise RuntimeError(f"Unexpected userFillsByTime response: {result}")
    return result


def fetch_market_snapshot(
    api_url: str,
    coin: str,
    lookback_days: int,
    timeout: float,
) -> MarketSnapshot:
    closes, last_candle_start_ms = fetch_completed_daily_closes(
        api_url, coin, lookback_days, timeout
    )
    mark_price, current_hourly_funding = fetch_asset_context(api_url, coin, timeout)
    funding_apr_24h = fetch_funding_apr_24h(api_url, coin, timeout)
    return MarketSnapshot(
        closes=closes,
        mark_price=mark_price,
        current_hourly_funding=current_hourly_funding,
        funding_apr_24h=funding_apr_24h,
        last_candle_start_ms=last_candle_start_ms,
    )
