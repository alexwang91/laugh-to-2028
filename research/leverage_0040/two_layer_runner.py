from __future__ import annotations

"""Research-only P4 two-layer leverage composition.

This module deliberately does **not** choose a leverage multiplier.  It preserves
P3.2/P4.1 as the complete <=1 target authority and applies a separately supplied
research multiplier after that frozen defensive target has been produced.

No production runtime imports this module.  LEVERAGE-0040 must not evaluate any
multiplier above 1.0 until the dedicated cap=1 historical parity gate passes.
"""

from dataclasses import dataclass
import math
from typing import Mapping


TARGET_ASSETS = ("BTC", "ETH", "SOL", "BNB")
MAX_0040_RESEARCH_CAP = 1.30


class TwoLayerLeverageError(ValueError):
    pass


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise TwoLayerLeverageError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class TwoLayerTarget:
    base_target_weights: dict[str, float]
    base_gross_target: float
    frozen_defensive_scale: float
    leverage_multiplier: float
    research_cap: float
    final_target_weights: dict[str, float]
    final_gross_target: float
    cash_or_financing_share: float
    final_scale: float
    production_authorized: bool = False


def compose_two_layer_target(
    *,
    base_target_weights: Mapping[str, float],
    frozen_defensive_scale: float,
    leverage_multiplier: float,
    research_cap: float,
) -> TwoLayerTarget:
    """Apply a separate multiplier to an already-frozen P3.2 target.

    `base_target_weights` are the complete P3.2 target weights, meaning the
    frozen BRRK relative allocation and frozen 0-1 defensive scale have already
    been applied.  This function never calls or modifies the defensive selector.
    """

    if set(base_target_weights) != set(TARGET_ASSETS):
        raise TwoLayerLeverageError(
            f"base_target_weights must contain exactly {TARGET_ASSETS}"
        )

    defensive = _finite("frozen_defensive_scale", frozen_defensive_scale)
    multiplier = _finite("leverage_multiplier", leverage_multiplier)
    cap = _finite("research_cap", research_cap)

    if not 0.0 <= defensive <= 1.0:
        raise TwoLayerLeverageError("frozen_defensive_scale must remain in [0,1]")
    if not 1.0 <= cap <= MAX_0040_RESEARCH_CAP:
        raise TwoLayerLeverageError(
            f"research_cap must remain in [1,{MAX_0040_RESEARCH_CAP}] under LEVERAGE-0040"
        )
    if not 1.0 <= multiplier <= cap:
        raise TwoLayerLeverageError("leverage_multiplier must remain in [1,research_cap]")

    base: dict[str, float] = {}
    for asset in TARGET_ASSETS:
        value = _finite(f"base_target_weights[{asset}]", base_target_weights[asset])
        if value < 0.0:
            raise TwoLayerLeverageError("LEVERAGE-0040 cannot create or amplify short targets")
        base[asset] = value

    base_gross = float(sum(base.values()))
    if base_gross > 1.0 + 1e-12:
        raise TwoLayerLeverageError(
            "base P3.2 target gross must remain <=1 before the P4 leverage layer"
        )

    final_weights = {asset: float(base[asset] * multiplier) for asset in TARGET_ASSETS}
    final_gross = float(sum(final_weights.values()))
    final_scale = float(defensive * multiplier)

    return TwoLayerTarget(
        base_target_weights=base,
        base_gross_target=base_gross,
        frozen_defensive_scale=defensive,
        leverage_multiplier=multiplier,
        research_cap=cap,
        final_target_weights=final_weights,
        final_gross_target=final_gross,
        cash_or_financing_share=float(1.0 - final_gross),
        final_scale=final_scale,
        production_authorized=False,
    )
