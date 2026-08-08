from __future__ import annotations

"""Phase 6 canonical integrated shadow orchestration.

This module is intentionally incapable of signing or submitting orders.  It
consumes an already-calculated P3.3 rebalance plan plus read-only route
projections and produces a deterministic audit record containing hypothetical
orders only.  P5.6 is blocked, so the cycle layer is explicitly NONE and the
upstream BRRK long target remains capped at gross 1.0.
"""

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Mapping, Protocol

from .data_contract import CANONICAL_ASSETS
from .rebalance_control import REBALANCE_CONTROL_VERSION


SHADOW_SYSTEM_VERSION = "P6-INTEGRATED-SHADOW-V1"
SHADOW_MODE = "SHADOW_ZERO_AUTHORITY"
CYCLE_LAYER_STATUS = "NONE_P5_6_BLOCKED"
_EPS = 1e-10


class ShadowSystemError(RuntimeError):
    pass


class RebalancePlanLike(Protocol):
    decision_timestamp: str
    control_version: str
    production_authorized: bool
    model_target_weights: Mapping[str, float]
    current_position_weights: Mapping[str, float]
    current_position_notionals_usd: Mapping[str, float]
    post_control_desired_weights: Mapping[str, float]
    proposed_delta_notionals_usd: Mapping[str, float]
    l1_target_gap: float

    def digest(self) -> str: ...


@dataclass(frozen=True)
class ShadowRouteProjection:
    asset: str
    selected_route: str
    reason_code: str
    instrument_id: str | None
    expected_cost_bps: float | None
    capacity_ok: bool

    def validate(self) -> None:
        if self.asset not in CANONICAL_ASSETS:
            raise ShadowSystemError(f"unknown shadow route asset: {self.asset}")
        if self.selected_route not in {"spot", "perp", "no_trade"}:
            raise ShadowSystemError(f"unsupported shadow route: {self.selected_route}")
        if not self.reason_code:
            raise ShadowSystemError("route reason_code is required")
        if self.selected_route == "no_trade":
            if self.instrument_id is not None:
                raise ShadowSystemError("no_trade route must not carry an instrument_id")
            return
        if not self.instrument_id:
            raise ShadowSystemError("tradable route requires instrument_id")
        if self.expected_cost_bps is None or not math.isfinite(float(self.expected_cost_bps)):
            raise ShadowSystemError("tradable route requires finite expected_cost_bps")
        if float(self.expected_cost_bps) < 0:
            raise ShadowSystemError("expected_cost_bps must be nonnegative")


@dataclass(frozen=True)
class HypotheticalOrder:
    asset: str
    side: str
    route: str
    instrument_id: str
    notional_usd: float
    expected_cost_bps: float
    expected_cost_usd: float
    reason_code: str
    hypothetical_only: bool = True


@dataclass(frozen=True)
class ShadowDecisionRecord:
    schema_version: int
    shadow_system_version: str
    mode: str
    decision_timestamp: str
    control_digest: str
    cycle_layer_status: str
    model_target_weights: dict[str, float]
    current_position_weights: dict[str, float]
    post_control_desired_weights: dict[str, float]
    target_gross_weight: float
    desired_gross_weight: float
    leverage_target: float
    l1_target_gap: float
    offline_reference_l1_drift: float
    route_projections: dict[str, dict[str, Any]]
    hypothetical_orders: tuple[HypotheticalOrder, ...]
    emergency_hypothetical_action: str
    alerts: tuple[str, ...]
    status: str
    production_authorized: bool = False
    signature_authorized: bool = False
    order_submission_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["hypothetical_orders"] = [asdict(row) for row in self.hypothetical_orders]
        return payload

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def _weights(values: Mapping[str, object], *, field: str) -> dict[str, float]:
    normalized = {str(k).upper(): v for k, v in values.items()}
    if set(normalized) != set(CANONICAL_ASSETS):
        raise ShadowSystemError(f"{field} must contain exactly BTC/ETH/SOL/BNB")
    result: dict[str, float] = {}
    for asset in CANONICAL_ASSETS:
        try:
            value = float(normalized[asset])
        except (TypeError, ValueError) as exc:
            raise ShadowSystemError(f"{field}[{asset}] must be numeric") from exc
        if not math.isfinite(value):
            raise ShadowSystemError(f"{field}[{asset}] must be finite")
        result[asset] = value
    return result


def _notionals(values: Mapping[str, object], *, field: str) -> dict[str, float]:
    return _weights(values, field=field)


def _validate_plan(plan: RebalancePlanLike) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    if plan.control_version != REBALANCE_CONTROL_VERSION:
        raise ShadowSystemError("Phase 6 requires the canonical P3.3 rebalance control version")
    if bool(plan.production_authorized):
        raise ShadowSystemError("shadow system rejects production-authorized upstream mutations")
    target = _weights(plan.model_target_weights, field="model_target_weights")
    current = _weights(plan.current_position_weights, field="current_position_weights")
    desired = _weights(plan.post_control_desired_weights, field="post_control_desired_weights")
    if any(value < -_EPS for value in target.values()):
        raise ShadowSystemError("canonical Phase 6 BRRK target must remain long-only")
    target_gross = sum(abs(value) for value in target.values())
    desired_gross = sum(abs(value) for value in desired.values())
    if target_gross > 1.0 + _EPS or desired_gross > 1.0 + _EPS:
        raise ShadowSystemError("Phase 6 gross must remain <= 1.0")
    observed_gap = sum(abs(target[a] - current[a]) for a in CANONICAL_ASSETS)
    if not math.isclose(observed_gap, float(plan.l1_target_gap), rel_tol=0.0, abs_tol=1e-8):
        raise ShadowSystemError("P3.3 l1_target_gap does not reconcile with target/current weights")
    return target, current, desired


def build_integrated_shadow_record(
    *,
    plan: RebalancePlanLike,
    route_projections: Mapping[str, ShadowRouteProjection],
    offline_reference_target_weights: Mapping[str, object],
    feature_reference_ok: bool,
    data_complete: bool,
    instrument_identity_ok: bool,
    cost_model_ok: bool,
    state_transition_explained: bool,
    schedule_ok: bool,
    emergency_active: bool = False,
) -> ShadowDecisionRecord:
    """Build one zero-authority integrated shadow decision.

    Any missing/failed reference check blocks hypothetical routing.  Emergency
    mode computes a hypothetical flattening intent from observed positions but
    still cannot authorize a signature or submission.
    """
    target, current, desired = _validate_plan(plan)
    current_notionals = _notionals(
        plan.current_position_notionals_usd,
        field="current_position_notionals_usd",
    )
    proposal = _notionals(plan.proposed_delta_notionals_usd, field="proposed_delta_notionals_usd")
    reference = _weights(offline_reference_target_weights, field="offline_reference_target_weights")
    reference_drift = float(sum(abs(target[a] - reference[a]) for a in CANONICAL_ASSETS))

    alerts: list[str] = []
    if not feature_reference_ok:
        alerts.append("FEATURE_REFERENCE_MISMATCH")
    if reference_drift > _EPS:
        alerts.append("TARGET_REFERENCE_MISMATCH")
    if not data_complete:
        alerts.append("MISSING_OR_INCOMPLETE_DATA")
    if not instrument_identity_ok:
        alerts.append("INSTRUMENT_IDENTITY_MISMATCH")
    if not cost_model_ok:
        alerts.append("COST_MODEL_ERROR")
    if not state_transition_explained:
        alerts.append("UNEXPLAINED_STATE_TRANSITION")
    if not schedule_ok:
        alerts.append("DAILY_SCHEDULE_DRIFT")

    effective_delta = (
        {asset: -current_notionals[asset] for asset in CANONICAL_ASSETS}
        if emergency_active
        else proposal
    )
    route_map = {str(asset).upper(): route for asset, route in route_projections.items()}
    unknown_routes = sorted(set(route_map) - set(CANONICAL_ASSETS))
    if unknown_routes:
        raise ShadowSystemError("route projections contain unknown assets: " + ",".join(unknown_routes))
    for asset, route in route_map.items():
        if route.asset != asset:
            raise ShadowSystemError("route projection key/asset mismatch")
        route.validate()

    orders: list[HypotheticalOrder] = []
    invariant_alerts = bool(alerts)
    if not invariant_alerts:
        for asset in CANONICAL_ASSETS:
            delta = float(effective_delta[asset])
            if abs(delta) <= 1e-9:
                continue
            route = route_map.get(asset)
            if route is None:
                alerts.append(f"ROUTE_MISSING:{asset}")
                continue
            if route.selected_route == "no_trade" or not route.capacity_ok:
                alerts.append(f"ROUTE_UNAVAILABLE:{asset}")
                continue
            assert route.instrument_id is not None
            assert route.expected_cost_bps is not None
            notional = abs(delta)
            cost_bps = float(route.expected_cost_bps)
            orders.append(
                HypotheticalOrder(
                    asset=asset,
                    side="BUY" if delta > 0 else "SELL",
                    route=route.selected_route,
                    instrument_id=route.instrument_id,
                    notional_usd=notional,
                    expected_cost_bps=cost_bps,
                    expected_cost_usd=notional * cost_bps / 10_000.0,
                    reason_code=route.reason_code,
                )
            )

    if alerts:
        # Fail closed: a partially routable shadow decision must not masquerade as
        # a complete executable plan.  Keep diagnostics but discard order intents.
        orders = []
        status = "BLOCKED_FAIL_CLOSED"
    else:
        status = "SHADOW_COMPUTED_NO_AUTHORITY"

    target_gross = float(sum(abs(v) for v in target.values()))
    desired_gross = float(sum(abs(v) for v in desired.values()))
    route_payload = {asset: asdict(route_map[asset]) for asset in sorted(route_map)}
    return ShadowDecisionRecord(
        schema_version=1,
        shadow_system_version=SHADOW_SYSTEM_VERSION,
        mode=SHADOW_MODE,
        decision_timestamp=str(plan.decision_timestamp),
        control_digest=str(plan.digest()),
        cycle_layer_status=CYCLE_LAYER_STATUS,
        model_target_weights=target,
        current_position_weights=current,
        post_control_desired_weights=desired,
        target_gross_weight=target_gross,
        desired_gross_weight=desired_gross,
        leverage_target=target_gross,
        l1_target_gap=float(plan.l1_target_gap),
        offline_reference_l1_drift=reference_drift,
        route_projections=route_payload,
        hypothetical_orders=tuple(orders),
        emergency_hypothetical_action="FLATTEN" if emergency_active else "NONE",
        alerts=tuple(alerts),
        status=status,
    )
