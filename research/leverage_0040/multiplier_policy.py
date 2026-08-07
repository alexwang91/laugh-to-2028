from __future__ import annotations

"""Frozen pre-result multiplier policy for LEVERAGE-0040.

This module is deterministic and deliberately tiny.  It consumes only the
already-frozen P3/P4 defensive scale and one preregistered candidate cap.
It does not inspect historical candidate performance or choose the cap.
"""

import math


ALLOWED_CAPS = (1.0, 1.10, 1.20, 1.30)


class MultiplierPolicyError(ValueError):
    pass


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise MultiplierPolicyError(f"{name} must be finite")
    return value


def _canonical_cap(value: float) -> float:
    cap = _finite("candidate_research_cap", value)
    for allowed in ALLOWED_CAPS:
        if math.isclose(cap, allowed, rel_tol=0.0, abs_tol=1e-12):
            return allowed
    raise MultiplierPolicyError(
        f"candidate_research_cap must be one of {ALLOWED_CAPS} under LEVERAGE-0040"
    )


def leverage_multiplier(*, frozen_defensive_scale: float, candidate_research_cap: float) -> float:
    defensive = _finite("frozen_defensive_scale", frozen_defensive_scale)
    if not 0.0 <= defensive <= 1.0:
        raise MultiplierPolicyError("frozen_defensive_scale must remain in [0,1]")
    cap = _canonical_cap(candidate_research_cap)
    return float(1.0 + (cap - 1.0) * defensive)


def final_scale(*, frozen_defensive_scale: float, candidate_research_cap: float) -> float:
    defensive = _finite("frozen_defensive_scale", frozen_defensive_scale)
    multiplier = leverage_multiplier(
        frozen_defensive_scale=defensive,
        candidate_research_cap=candidate_research_cap,
    )
    return float(defensive * multiplier)
