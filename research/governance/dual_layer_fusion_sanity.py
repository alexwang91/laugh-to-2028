from __future__ import annotations

"""Pure, non-promotable dual-layer architecture sanity logic.

This module does not import or modify canonical BRRK runtime code.  It only
checks the composition rule frozen by DUAL-LAYER-FUSION-ARCH-SANITY-V1:
external information may cap total gross exposure, but may never change the
canonical BRRK relative asset ranking, add assets, introduce shorts, or increase
gross exposure.
"""

from dataclasses import dataclass
import math
from typing import Mapping


ASSETS = ("BTC", "ETH", "SOL", "BNB")
STATE_CAPS = {"SUPPORTIVE": 1.0, "NEUTRAL": 0.8, "RESTRICTIVE": 0.6}
_EPS = 1e-12


class DualLayerFusionError(ValueError):
    pass


@dataclass(frozen=True)
class ExternalState:
    state: str
    growth_20d: float
    growth_acceleration_20d: float
    gross_cap: float


def classify_external_state(growth_20d: object, growth_acceleration_20d: object) -> ExternalState:
    try:
        growth = float(growth_20d)
        acceleration = float(growth_acceleration_20d)
    except (TypeError, ValueError) as exc:
        raise DualLayerFusionError("external features must be numeric") from exc
    if not math.isfinite(growth) or not math.isfinite(acceleration):
        raise DualLayerFusionError("external features must be finite")
    if growth > 0.0 and acceleration > 0.0:
        state = "SUPPORTIVE"
    elif growth < 0.0 and acceleration < 0.0:
        state = "RESTRICTIVE"
    else:
        state = "NEUTRAL"
    return ExternalState(state, growth, acceleration, STATE_CAPS[state])


def _weights(values: Mapping[str, object]) -> dict[str, float]:
    normalized = {str(k).upper(): v for k, v in values.items()}
    if tuple(normalized) != ASSETS:
        if set(normalized) != set(ASSETS):
            raise DualLayerFusionError("target must contain exactly BTC/ETH/SOL/BNB")
    out: dict[str, float] = {}
    for asset in ASSETS:
        try:
            value = float(normalized[asset])
        except (TypeError, ValueError) as exc:
            raise DualLayerFusionError(f"target[{asset}] must be numeric") from exc
        if not math.isfinite(value) or value < -_EPS:
            raise DualLayerFusionError("fusion accepts finite long-only canonical targets")
        out[asset] = max(value, 0.0)
    gross = sum(out.values())
    if gross > 1.0 + _EPS:
        raise DualLayerFusionError("canonical target gross must be <= 1")
    return out


def apply_external_gross_cap(
    canonical_target: Mapping[str, object],
    external_state: ExternalState,
) -> dict[str, float]:
    target = _weights(canonical_target)
    if external_state.state not in STATE_CAPS:
        raise DualLayerFusionError("unknown external state")
    expected_cap = STATE_CAPS[external_state.state]
    if not math.isclose(float(external_state.gross_cap), expected_cap, rel_tol=0.0, abs_tol=1e-15):
        raise DualLayerFusionError("external state/cap mismatch")
    gross = float(sum(target.values()))
    if gross <= external_state.gross_cap + _EPS or gross <= _EPS:
        return dict(target)
    scale = external_state.gross_cap / gross
    fused = {asset: float(target[asset] * scale) for asset in ASSETS}
    if sum(fused.values()) > gross + _EPS:
        raise DualLayerFusionError("external layer may not increase internal gross")
    return fused


def relative_weights(weights: Mapping[str, object]) -> dict[str, float]:
    target = _weights(weights)
    gross = sum(target.values())
    if gross <= _EPS:
        return {asset: 0.0 for asset in ASSETS}
    return {asset: target[asset] / gross for asset in ASSETS}
