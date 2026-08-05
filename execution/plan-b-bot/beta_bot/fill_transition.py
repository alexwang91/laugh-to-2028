from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any


QUANTITY_TOLERANCE = 1e-8
WORKING_EXCHANGE_STATUSES = {"open", "triggered"}


class FillTransitionError(RuntimeError):
    """Persisted order truth cannot produce a trustworthy fill-driven transition."""


def _number(value: Any, *, name: str, allow_none: bool = False) -> float | None:
    if value is None and allow_none:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise FillTransitionError(f"{name} is not numeric: {value!r}") from exc
    if not isfinite(number):
        raise FillTransitionError(f"{name} is not finite: {value!r}")
    return number


def _parameters(order: dict[str, Any]) -> dict[str, Any]:
    raw = order.get("submitted_order_parameters_json")
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        raise FillTransitionError("submitted_order_parameters_json is missing")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FillTransitionError("submitted_order_parameters_json is malformed") from exc
    if not isinstance(parsed, dict):
        raise FillTransitionError("submitted_order_parameters_json must decode to an object")
    return parsed


@dataclass(frozen=True)
class FillTransition:
    cloid: str
    asset: str
    side: str
    economic_intent: str
    route_action: str
    submitted_quantity: float
    fill_quantity: float
    signed_fill_quantity: float
    unfilled_quantity: float
    exchange_remaining_quantity: float
    resting_remaining_quantity: float
    fill_state: str
    position_tracking_status: str
    position_tracking_source: str | None
    position_before_qty: float | None
    target_position_qty: float | None
    actual_position_qty_from_fills: float | None
    target_gap_qty: float | None
    last_exchange_status: str | None
    terminal_status: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_fill_transition(order: dict[str, Any]) -> FillTransition:
    """Derive position progress from actual fills, never from requested notional.

    P1.3 deliberately separates two questions:
    - fill lifecycle truth is always derived from reconciled fill_quantity / remaining_quantity;
    - target-vs-actual position is only emitted when the persisted pre-trade position baseline is known.

    This prevents the P1.4 reversal problem from being hidden: an open-reversal leg may have
    fill truth while its position baseline remains unavailable until the close leg is freshly
    reconciled against account state.
    """
    submitted = _number(order.get("submitted_quantity"), name="submitted_quantity")
    fill = _number(order.get("fill_quantity"), name="fill_quantity")
    remaining = _number(order.get("remaining_quantity"), name="remaining_quantity")
    assert submitted is not None and fill is not None and remaining is not None

    if submitted <= 0:
        raise FillTransitionError("submitted_quantity must be positive")
    if fill < -QUANTITY_TOLERANCE:
        raise FillTransitionError("fill_quantity cannot be negative")
    if remaining < -QUANTITY_TOLERANCE:
        raise FillTransitionError("remaining_quantity cannot be negative")
    if fill > submitted + QUANTITY_TOLERANCE:
        raise FillTransitionError(
            f"fill_quantity {fill} exceeds submitted_quantity {submitted}"
        )

    fill = max(fill, 0.0)
    remaining = max(remaining, 0.0)
    unfilled = max(submitted - fill, 0.0)

    if fill <= QUANTITY_TOLERANCE:
        fill_state = "zero_fill"
    elif abs(fill - submitted) <= QUANTITY_TOLERANCE:
        fill_state = "full_fill"
    else:
        fill_state = "partial_fill"

    side = str(order.get("side") or "").lower()
    if side == "buy":
        signed_fill = fill
    elif side == "sell":
        signed_fill = -fill
    else:
        raise FillTransitionError(f"Unsupported order side for position transition: {side!r}")

    last_exchange_status = order.get("last_exchange_status")
    last_exchange_status = str(last_exchange_status) if last_exchange_status is not None else None
    resting_remaining = remaining if last_exchange_status in WORKING_EXCHANGE_STATUSES else 0.0

    params = _parameters(order)
    tracking_source = params.get("position_tracking_source")
    tracking_source = str(tracking_source) if tracking_source is not None else None
    before = _number(params.get("position_before_qty"), name="position_before_qty", allow_none=True)
    target = _number(params.get("target_position_qty"), name="target_position_qty", allow_none=True)

    if before is None or target is None:
        tracking_status = "baseline_unavailable"
        actual = None
        gap = None
    else:
        tracking_status = "available"
        actual = before + signed_fill
        gap = target - actual
        if abs(actual) <= QUANTITY_TOLERANCE:
            actual = 0.0
        if abs(gap) <= QUANTITY_TOLERANCE:
            gap = 0.0

    return FillTransition(
        cloid=str(order.get("cloid") or ""),
        asset=str(order.get("asset") or ""),
        side=side,
        economic_intent=str(order.get("economic_intent") or ""),
        route_action=str(order.get("route_action") or ""),
        submitted_quantity=submitted,
        fill_quantity=fill,
        signed_fill_quantity=signed_fill,
        unfilled_quantity=unfilled,
        exchange_remaining_quantity=remaining,
        resting_remaining_quantity=resting_remaining,
        fill_state=fill_state,
        position_tracking_status=tracking_status,
        position_tracking_source=tracking_source,
        position_before_qty=before,
        target_position_qty=target,
        actual_position_qty_from_fills=actual,
        target_gap_qty=gap,
        last_exchange_status=last_exchange_status,
        terminal_status=(
            str(order.get("terminal_status")) if order.get("terminal_status") is not None else None
        ),
    )
