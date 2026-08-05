from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ReversalSafetyError(RuntimeError):
    """Raised when a reversal cannot safely advance to the new direction."""


@dataclass(frozen=True)
class ReversalState:
    coin: str
    expected_old_sign: int
    observed_position_qty: float
    safe_to_open_new_direction: bool


def position_qty_from_user_state(state: dict[str, Any], coin: str) -> float:
    positions = state.get("assetPositions")
    if not isinstance(positions, list):
        raise ReversalSafetyError("clearinghouseState.assetPositions is missing or malformed")
    matches: list[float] = []
    for item in positions:
        if not isinstance(item, dict):
            continue
        position = item.get("position")
        if not isinstance(position, dict) or position.get("coin") != coin:
            continue
        try:
            matches.append(float(position.get("szi") or 0.0))
        except (TypeError, ValueError) as exc:
            raise ReversalSafetyError(f"Malformed position size for {coin}") from exc
    if len(matches) > 1:
        raise ReversalSafetyError(f"Multiple position rows returned for {coin}")
    return matches[0] if matches else 0.0


def verify_reversal_flat(
    state: dict[str, Any],
    *,
    coin: str,
    previous_position_qty: float,
    epsilon: float = 1e-8,
) -> ReversalState:
    if abs(previous_position_qty) <= epsilon:
        raise ReversalSafetyError("Reversal verification requires a non-flat previous position")
    observed = position_qty_from_user_state(state, coin)
    old_sign = 1 if previous_position_qty > 0 else -1
    if abs(observed) <= epsilon:
        return ReversalState(coin, old_sign, observed, True)
    if (observed > 0) != (previous_position_qty > 0):
        raise ReversalSafetyError(
            f"Unsafe reversal state: {coin} already crossed through flat to {observed} before the new-direction leg"
        )
    raise ReversalSafetyError(
        f"Reversal close is incomplete for {coin}: fresh exchange position is {observed}; new-direction opening is blocked"
    )
