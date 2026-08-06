from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from eth_account import Account
from hyperliquid.exchange import Exchange

from .config import Settings
from .instrument_metadata import InstrumentMetadataError, format_size, parse_perp_metadata
from .market import fetch_open_orders, fetch_perp_metadata, fetch_user_state


class EmergencyPathError(RuntimeError):
    """Emergency action could not be completed safely."""


@dataclass(frozen=True)
class EmergencyAction:
    action: str
    coin: str | None
    status: str
    detail: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class NewRiskKillSwitch:
    """Durable local switch that blocks only risk-increasing normal execution."""

    def __init__(self, path: str):
        if not path or path == ":memory:":
            raise EmergencyPathError("A persistent kill-switch path is required")
        self.path = Path(path)

    def disable(self, *, reason: str) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "disabled": True,
            "reason": reason,
            "timestamp_ms": int(time.time() * 1000),
        }
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        os.replace(tmp, self.path)
        return payload

    def status(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"disabled": False, "reason": None, "timestamp_ms": None}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise EmergencyPathError(f"Kill-switch state is unreadable: {exc}") from exc
        if not isinstance(payload, dict) or payload.get("disabled") is not True:
            raise EmergencyPathError("Kill-switch state is malformed; fail closed")
        return {
            "disabled": True,
            "reason": str(payload.get("reason") or "unspecified"),
            "timestamp_ms": int(payload.get("timestamp_ms") or 0),
        }

    @property
    def new_risk_disabled(self) -> bool:
        return bool(self.status()["disabled"])


def kill_switch_path(settings: Settings) -> str:
    explicit = getattr(settings, "new_risk_kill_switch_path", None)
    if explicit:
        return str(explicit)
    if settings.order_ledger_path:
        return f"{settings.order_ledger_path}.new-risk-disabled"
    raise EmergencyPathError("NEW_RISK_KILL_SWITCH_PATH or ORDER_LEDGER_PATH is required")


def normal_new_risk_disabled(settings: Settings) -> bool:
    """Fail closed if the durable switch exists but cannot be parsed."""
    try:
        return NewRiskKillSwitch(kill_switch_path(settings)).new_risk_disabled
    except EmergencyPathError:
        if settings.can_trade:
            raise
        return False


def _positions(user_state: dict[str, Any]) -> list[tuple[str, float]]:
    raw = user_state.get("assetPositions")
    if not isinstance(raw, list):
        raise EmergencyPathError("clearinghouseState assetPositions is missing")
    positions: list[tuple[str, float]] = []
    for entry in raw:
        if not isinstance(entry, dict) or not isinstance(entry.get("position"), dict):
            raise EmergencyPathError("Malformed clearinghouseState position entry")
        position = entry["position"]
        coin = position.get("coin")
        size = position.get("szi")
        if not isinstance(coin, str):
            raise EmergencyPathError("Position coin is missing")
        try:
            qty = float(size)
        except (TypeError, ValueError) as exc:
            raise EmergencyPathError(f"Position size for {coin} is malformed: {size}") from exc
        if abs(qty) > 1e-12:
            positions.append((coin, qty))
    return positions


def build_exchange(settings: Settings) -> Exchange:
    if not settings.api_private_key or not settings.master_address:
        raise EmergencyPathError("Trading Agent/API credentials are required")
    wallet = Account.from_key(settings.api_private_key)
    exchange = Exchange(
        wallet,
        settings.api_url,
        vault_address=settings.vault_address,
        account_address=settings.master_address,
        timeout=settings.request_timeout_seconds,
    )
    exchange.set_expires_after(int(time.time() * 1000) + 30_000)
    return exchange


class EmergencyController:
    """Direct risk-reduction control plane independent of the normal target engine."""

    def __init__(
        self,
        settings: Settings,
        *,
        exchange: Exchange | Any | None = None,
        fetch_open_orders_fn: Callable[[str, str, float], list[dict[str, Any]]] = fetch_open_orders,
        fetch_user_state_fn: Callable[[str, str, float], dict[str, Any]] = fetch_user_state,
        fetch_perp_metadata_fn: Callable[[str, float], dict[str, Any]] = fetch_perp_metadata,
    ):
        if not settings.account_address:
            raise EmergencyPathError("Trading account address is required")
        self.settings = settings
        self.exchange = exchange or build_exchange(settings)
        self.fetch_open_orders_fn = fetch_open_orders_fn
        self.fetch_user_state_fn = fetch_user_state_fn
        self.fetch_perp_metadata_fn = fetch_perp_metadata_fn

    def cancel_all(self) -> list[EmergencyAction]:
        orders = self.fetch_open_orders_fn(
            self.settings.api_url,
            self.settings.account_address or "",
            self.settings.request_timeout_seconds,
        )
        actions: list[EmergencyAction] = []
        for order in orders:
            if not isinstance(order, dict):
                raise EmergencyPathError(f"Malformed open order: {order}")
            coin = order.get("coin")
            oid = order.get("oid")
            if not isinstance(coin, str) or oid is None:
                raise EmergencyPathError(f"Open order lacks coin/oid: {order}")
            response = self.exchange.cancel(coin, int(oid))
            actions.append(
                EmergencyAction(
                    action="cancel_all",
                    coin=coin,
                    status="submitted",
                    detail={"oid": str(oid), "response": response},
                )
            )
        return actions

    def reduce_only_close(self, coin: str | None = None) -> list[EmergencyAction]:
        target_coin = (coin or self.settings.coin).upper()
        state = self.fetch_user_state_fn(
            self.settings.api_url,
            self.settings.account_address or "",
            self.settings.request_timeout_seconds,
        )
        positions = dict(_positions(state))
        qty = float(positions.get(target_coin, 0.0))
        if abs(qty) <= 1e-12:
            return []
        metadata = parse_perp_metadata(
            self.fetch_perp_metadata_fn(
                self.settings.api_url, self.settings.request_timeout_seconds
            )
        )
        try:
            size = format_size(abs(qty), metadata[target_coin])
        except KeyError as exc:
            raise InstrumentMetadataError(f"No perp metadata for emergency close {target_coin}") from exc
        response = self.exchange.market_close(
            target_coin,
            sz=size,
            slippage=self.settings.max_slippage_bps / 10_000,
        )
        return [
            EmergencyAction(
                action="reduce_only_close",
                coin=target_coin,
                status="submitted",
                detail={
                    "pre_close_position_qty": qty,
                    "size": size,
                    "reduce_only_semantics": True,
                    "response": response,
                },
            )
        ]

    def emergency_flat(self) -> list[EmergencyAction]:
        actions = self.cancel_all()
        state = self.fetch_user_state_fn(
            self.settings.api_url,
            self.settings.account_address or "",
            self.settings.request_timeout_seconds,
        )
        positions = _positions(state)
        if not positions:
            return actions
        metadata = parse_perp_metadata(
            self.fetch_perp_metadata_fn(
                self.settings.api_url, self.settings.request_timeout_seconds
            )
        )
        for coin, qty in positions:
            try:
                size = format_size(abs(qty), metadata[coin])
            except KeyError as exc:
                raise InstrumentMetadataError(f"No perp metadata for emergency FLAT {coin}") from exc
            response = self.exchange.market_close(
                coin,
                sz=size,
                slippage=self.settings.max_slippage_bps / 10_000,
            )
            actions.append(
                EmergencyAction(
                    action="emergency_flat",
                    coin=coin,
                    status="submitted",
                    detail={
                        "pre_close_position_qty": qty,
                        "size": size,
                        "reduce_only_semantics": True,
                        "response": response,
                    },
                )
            )
        return actions

    def disable_new_risk(self, *, reason: str = "operator_emergency_switch") -> EmergencyAction:
        state = NewRiskKillSwitch(kill_switch_path(self.settings)).disable(reason=reason)
        return EmergencyAction(
            action="disable_new_risk",
            coin=None,
            status="active",
            detail=state,
        )
