from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Literal

from .instrument_registry import InstrumentRegistry
from .route_cost import FeeSchedule, RouteCostEstimate, RouteObservation, estimate_route_cost


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROUTER_POLICY_PATH = REPO_ROOT / "config" / "router_policy.json"

Direction = Literal["long", "short"]
ExposureRole = Literal["base", "leverage_overlay"]
SelectedRoute = Literal["spot", "perp", "no_trade"]


class RouterDecisionError(ValueError):
    """Router inputs are incomplete, inconsistent, or violate canonical policy."""


@dataclass(frozen=True)
class RouterPolicy:
    schema_version: int
    policy_id: str
    cost_model_id: str
    base_long_spot_candidates: tuple[str, ...]
    perp_only_assets: dict[str, str]
    tie_break_route: Literal["spot", "perp"]
    tie_epsilon_bps: float
    max_capacity_ratio: float
    reason_codes: tuple[str, ...]
    authorization: str

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "RouterPolicy":
        tie = raw["tie_break"]
        capacity = raw["capacity_contract"]
        policy = cls(
            schema_version=int(raw["schema_version"]),
            policy_id=str(raw["policy_id"]),
            cost_model_id=str(raw["cost_model_id"]),
            base_long_spot_candidates=tuple(str(x).upper() for x in raw["base_long_spot_candidates"]),
            perp_only_assets={str(k).upper(): str(v) for k, v in raw["perp_only_assets"].items()},
            tie_break_route=str(tie["route"]),  # type: ignore[arg-type]
            tie_epsilon_bps=float(tie["epsilon_bps"]),
            max_capacity_ratio=float(capacity["max_notional_to_displayed_two_sided_depth_ratio"]),
            reason_codes=tuple(str(x) for x in raw["reason_codes"]),
            authorization=str(raw["authorization"]),
        )
        policy.validate()
        return policy

    def validate(self) -> None:
        if self.schema_version != 1:
            raise RouterDecisionError("Unsupported router policy schema_version")
        if self.tie_break_route not in {"spot", "perp"}:
            raise RouterDecisionError("Router tie-break route must be spot or perp")
        if not isfinite(self.tie_epsilon_bps) or self.tie_epsilon_bps < 0:
            raise RouterDecisionError("Router tie epsilon must be finite and nonnegative")
        if not isfinite(self.max_capacity_ratio) or self.max_capacity_ratio <= 0:
            raise RouterDecisionError("Router capacity ratio must be finite and positive")
        if set(self.base_long_spot_candidates) != {"BTC", "ETH", "SOL"}:
            raise RouterDecisionError("Canonical base-long spot candidates must be BTC/ETH/SOL")
        if self.perp_only_assets != {"BNB": "ROUTER-BNB-PERP-ONLY-2026-08-06"}:
            raise RouterDecisionError("Canonical BNB perp-only decision is missing")
        required = {
            "SPOT_VERIFIED_LOWER_COST",
            "SPOT_VERIFIED_COST_TIE",
            "SPOT_ONLY_VIABLE_ROUTE",
            "PERP_LOWER_COST",
            "PERP_SPOT_UNVERIFIED",
            "PERP_SPOT_COST_UNAVAILABLE",
            "PERP_SPOT_LIQUIDITY_FAIL",
            "PERP_PRODUCT_POLICY",
            "PERP_REQUIRED_FOR_SHORT",
            "PERP_REQUIRED_FOR_LEVERAGE_OVERLAY",
            "NO_TRADE_LIQUIDITY_FAIL",
            "NO_TRADE_COST_UNAVAILABLE",
            "NO_TRADE_ZERO_EXPOSURE",
        }
        if set(self.reason_codes) != required:
            raise RouterDecisionError("Router reason-code registry is incomplete or unexpected")
        if self.authorization != "IMPLEMENTATION_PLAN_ONLY_NO_PRODUCTION_AUTHORIZATION":
            raise RouterDecisionError("Router policy must not authorize production")


@dataclass(frozen=True)
class EconomicExposureRequest:
    decision_timestamp: str
    asset: str
    direction: Direction
    exposure_role: ExposureRole
    notional_usd: float
    holding_hours: float
    target_revision: str

    def validate(self) -> None:
        if not self.asset or self.asset.upper() != self.asset:
            raise RouterDecisionError("Economic asset must use canonical uppercase identity")
        if self.direction not in {"long", "short"}:
            raise RouterDecisionError("direction must be long or short")
        if self.exposure_role not in {"base", "leverage_overlay"}:
            raise RouterDecisionError("exposure_role must be base or leverage_overlay")
        if self.exposure_role == "leverage_overlay" and self.direction != "long":
            raise RouterDecisionError("Current leverage-overlay role is defined only for long exposure")
        if not isfinite(float(self.notional_usd)) or self.notional_usd < 0:
            raise RouterDecisionError("notional_usd must be finite and nonnegative")
        if not isfinite(float(self.holding_hours)) or self.holding_hours < 0:
            raise RouterDecisionError("holding_hours must be finite and nonnegative")
        if not self.target_revision:
            raise RouterDecisionError("target_revision is required")
        try:
            parsed = datetime.fromisoformat(self.decision_timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise RouterDecisionError("decision_timestamp must be ISO-8601") from exc
        if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
            raise RouterDecisionError("decision_timestamp must be timezone-aware UTC")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SpotRuntimeIdentity:
    asset: str
    expected_hypercore_token: str
    expected_hypercore_pair: str
    runtime_pair_label: str
    token_index: int
    pair_index: int
    coin_id: str
    sz_decimals: int
    wei_decimals: int
    token_id: str
    token_is_canonical: bool
    pair_is_canonical: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RouteCandidate:
    route: Literal["spot", "perp"]
    observation: RouteObservation
    estimate: RouteCostEstimate
    capacity_ok: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "route": self.route,
            "observation": asdict(self.observation),
            "estimate": self.estimate.to_dict(),
            "capacity_ok": self.capacity_ok,
        }


@dataclass(frozen=True)
class ImplementationPlan:
    asset: str
    route: Literal["spot", "perp"]
    instrument_id: str
    display_identity: str
    hypercore_identity: str
    expected_cost_bps: float
    expected_cost_usd: float
    cost_model_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RouterDecision:
    schema_version: int
    decision_id: str
    policy_id: str
    request: EconomicExposureRequest
    selected_route: SelectedRoute
    reason_code: str
    plan: ImplementationPlan | None
    spot_runtime_identity: SpotRuntimeIdentity | None
    spot_candidate: RouteCandidate | None
    perp_candidate: RouteCandidate | None
    fee_schedule: FeeSchedule

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "decision_id": self.decision_id,
            "policy_id": self.policy_id,
            "request": self.request.to_dict(),
            "selected_route": self.selected_route,
            "reason_code": self.reason_code,
            "plan": self.plan.to_dict() if self.plan else None,
            "spot_runtime_identity": self.spot_runtime_identity.to_dict() if self.spot_runtime_identity else None,
            "spot_candidate": self.spot_candidate.to_dict() if self.spot_candidate else None,
            "perp_candidate": self.perp_candidate.to_dict() if self.perp_candidate else None,
            "fee_schedule": asdict(self.fee_schedule),
        }


@dataclass(frozen=True)
class RealizedCostComparison:
    decision_id: str
    asset: str
    route: Literal["spot", "perp"]
    expected_cost_bps: float
    realized_cost_bps: float
    variance_bps: float
    expected_cost_usd: float
    realized_cost_usd: float
    variance_usd: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_router_policy(path: Path | None = None) -> RouterPolicy:
    source = path or DEFAULT_ROUTER_POLICY_PATH
    return RouterPolicy.from_mapping(json.loads(source.read_text(encoding="utf-8")))


def resolve_spot_runtime_identity(
    registry: InstrumentRegistry,
    asset: str,
    spot_meta: dict[str, Any],
) -> SpotRuntimeIdentity:
    key = asset.upper()
    row = registry.asset(key)
    if row.get("route_policy") != "SPOT_CANDIDATE_WITH_PERP_FALLBACK":
        raise RouterDecisionError(f"{key} is not a canonical spot candidate")
    spot = row["spot"]
    if spot.get("identity_status") not in {"VERIFIED_PRIOR_EVIDENCE", "VERIFIED_UNIT_NATIVE_ASSET"}:
        raise RouterDecisionError(f"{key} spot identity is not verified")
    expected_token = spot.get("hypercore_token_candidate")
    expected_pair = spot.get("hypercore_pair_candidate")
    if not isinstance(expected_token, str) or not isinstance(expected_pair, str):
        raise RouterDecisionError(f"{key} verified spot identity is incomplete")

    tokens = spot_meta.get("tokens") if isinstance(spot_meta, dict) else None
    universe = spot_meta.get("universe") if isinstance(spot_meta, dict) else None
    if not isinstance(tokens, list) or not isinstance(universe, list):
        raise RouterDecisionError("spotMeta must contain tokens and universe arrays")

    matching_base = [token for token in tokens if isinstance(token, dict) and token.get("name") == expected_token]
    matching_quote = [token for token in tokens if isinstance(token, dict) and token.get("name") == registry.quote_asset]
    if len(matching_base) != 1 or len(matching_quote) != 1:
        raise RouterDecisionError(f"spotMeta token identity is missing or ambiguous for {key}")
    base = matching_base[0]
    quote = matching_quote[0]
    try:
        base_index = int(base["index"])
        quote_index = int(quote["index"])
        sz_decimals = int(base["szDecimals"])
        wei_decimals = int(base["weiDecimals"])
        token_id = str(base["tokenId"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RouterDecisionError(f"spotMeta token metadata is malformed for {key}") from exc
    if base_index < 0 or quote_index < 0 or sz_decimals < 0 or wei_decimals < 0 or not token_id:
        raise RouterDecisionError(f"spotMeta token metadata is invalid for {key}")

    pairs: list[dict[str, Any]] = []
    for pair in universe:
        if not isinstance(pair, dict):
            continue
        pair_tokens = pair.get("tokens")
        if isinstance(pair_tokens, list) and len(pair_tokens) == 2:
            try:
                token_pair = [int(pair_tokens[0]), int(pair_tokens[1])]
            except (TypeError, ValueError):
                continue
            if token_pair == [base_index, quote_index]:
                pairs.append(pair)
    if len(pairs) != 1:
        raise RouterDecisionError(f"spotMeta pair identity is missing or ambiguous for {key}")
    pair = pairs[0]
    try:
        pair_index = int(pair["index"])
        pair_label = str(pair["name"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RouterDecisionError(f"spotMeta pair metadata is malformed for {key}") from exc
    if pair_index < 0 or not pair_label:
        raise RouterDecisionError(f"spotMeta pair metadata is invalid for {key}")

    # Hyperliquid's Info API uses PURR/USDC only for PURR. All BRRK spot
    # candidates are addressed as @<spot-pair-index> even if UI names are remapped.
    coin_id = f"@{pair_index}"
    return SpotRuntimeIdentity(
        asset=key,
        expected_hypercore_token=expected_token,
        expected_hypercore_pair=expected_pair,
        runtime_pair_label=pair_label,
        token_index=base_index,
        pair_index=pair_index,
        coin_id=coin_id,
        sz_decimals=sz_decimals,
        wei_decimals=wei_decimals,
        token_id=token_id,
        token_is_canonical=bool(base.get("isCanonical")),
        pair_is_canonical=bool(pair.get("isCanonical")),
    )


def decide_route(
    request: EconomicExposureRequest,
    *,
    registry: InstrumentRegistry,
    policy: RouterPolicy,
    spot_observation: RouteObservation | None,
    perp_observation: RouteObservation | None,
    spot_runtime_identity: SpotRuntimeIdentity | None,
    fees: FeeSchedule | None = None,
) -> RouterDecision:
    request.validate()
    row = registry.asset(request.asset)
    fee_schedule = fees or FeeSchedule()

    spot_candidate = _candidate_from_observation(
        request,
        "spot",
        spot_observation,
        policy=policy,
        fees=fee_schedule,
    )
    perp_candidate = _candidate_from_observation(
        request,
        "perp",
        perp_observation,
        policy=policy,
        fees=fee_schedule,
    )

    if request.notional_usd == 0:
        return _finalize(
            policy=policy,
            request=request,
            selected_route="no_trade",
            reason_code="NO_TRADE_ZERO_EXPOSURE",
            plan=None,
            spot_runtime_identity=spot_runtime_identity,
            spot_candidate=spot_candidate,
            perp_candidate=perp_candidate,
            fees=fee_schedule,
        )

    if request.direction == "short":
        return _forced_perp_or_no_trade(
            policy=policy,
            request=request,
            row=row,
            reason_code="PERP_REQUIRED_FOR_SHORT",
            spot_runtime_identity=spot_runtime_identity,
            spot_candidate=spot_candidate,
            perp_candidate=perp_candidate,
            fees=fee_schedule,
        )

    if request.exposure_role == "leverage_overlay":
        return _forced_perp_or_no_trade(
            policy=policy,
            request=request,
            row=row,
            reason_code="PERP_REQUIRED_FOR_LEVERAGE_OVERLAY",
            spot_runtime_identity=spot_runtime_identity,
            spot_candidate=spot_candidate,
            perp_candidate=perp_candidate,
            fees=fee_schedule,
        )

    if request.asset in policy.perp_only_assets:
        if spot_observation is not None or spot_runtime_identity is not None:
            raise RouterDecisionError(f"{request.asset} spot inputs violate canonical perp-only policy")
        return _forced_perp_or_no_trade(
            policy=policy,
            request=request,
            row=row,
            reason_code="PERP_PRODUCT_POLICY",
            spot_runtime_identity=None,
            spot_candidate=None,
            perp_candidate=perp_candidate,
            fees=fee_schedule,
        )

    if request.asset not in policy.base_long_spot_candidates:
        raise RouterDecisionError(f"No canonical base-long routing policy for {request.asset}")

    spot_verified = row.get("route_policy") == "SPOT_CANDIDATE_WITH_PERP_FALLBACK" and row["spot"].get(
        "identity_status"
    ) in {"VERIFIED_PRIOR_EVIDENCE", "VERIFIED_UNIT_NATIVE_ASSET"}
    if not spot_verified or spot_runtime_identity is None:
        if _viable(perp_candidate):
            return _select_perp(
                policy,
                request,
                row,
                "PERP_SPOT_UNVERIFIED",
                spot_runtime_identity,
                spot_candidate,
                perp_candidate,
                fee_schedule,
            )
        return _no_trade(
            policy,
            request,
            spot_runtime_identity,
            spot_candidate,
            perp_candidate,
            fee_schedule,
        )

    _validate_runtime_identity(request, row, spot_runtime_identity)

    if spot_candidate is None:
        if _viable(perp_candidate):
            return _select_perp(
                policy,
                request,
                row,
                "PERP_SPOT_COST_UNAVAILABLE",
                spot_runtime_identity,
                spot_candidate,
                perp_candidate,
                fee_schedule,
            )
        return _no_trade(policy, request, spot_runtime_identity, spot_candidate, perp_candidate, fee_schedule)

    if not spot_candidate.capacity_ok:
        if _viable(perp_candidate):
            return _select_perp(
                policy,
                request,
                row,
                "PERP_SPOT_LIQUIDITY_FAIL",
                spot_runtime_identity,
                spot_candidate,
                perp_candidate,
                fee_schedule,
            )
        return _no_trade(policy, request, spot_runtime_identity, spot_candidate, perp_candidate, fee_schedule)

    if not _viable(perp_candidate):
        return _select_spot(
            policy,
            request,
            row,
            "SPOT_ONLY_VIABLE_ROUTE",
            spot_runtime_identity,
            spot_candidate,
            perp_candidate,
            fee_schedule,
        )

    assert perp_candidate is not None
    difference = spot_candidate.estimate.total_cost_bps - perp_candidate.estimate.total_cost_bps
    if difference < -policy.tie_epsilon_bps:
        return _select_spot(
            policy,
            request,
            row,
            "SPOT_VERIFIED_LOWER_COST",
            spot_runtime_identity,
            spot_candidate,
            perp_candidate,
            fee_schedule,
        )
    if difference > policy.tie_epsilon_bps:
        return _select_perp(
            policy,
            request,
            row,
            "PERP_LOWER_COST",
            spot_runtime_identity,
            spot_candidate,
            perp_candidate,
            fee_schedule,
        )
    if policy.tie_break_route == "spot":
        return _select_spot(
            policy,
            request,
            row,
            "SPOT_VERIFIED_COST_TIE",
            spot_runtime_identity,
            spot_candidate,
            perp_candidate,
            fee_schedule,
        )
    return _select_perp(
        policy,
        request,
        row,
        "PERP_LOWER_COST",
        spot_runtime_identity,
        spot_candidate,
        perp_candidate,
        fee_schedule,
    )


def route_and_log(
    request: EconomicExposureRequest,
    *,
    registry: InstrumentRegistry,
    policy: RouterPolicy,
    spot_observation: RouteObservation | None,
    perp_observation: RouteObservation | None,
    spot_runtime_identity: SpotRuntimeIdentity | None,
    log_path: Path,
    fees: FeeSchedule | None = None,
) -> RouterDecision:
    decision = decide_route(
        request,
        registry=registry,
        policy=policy,
        spot_observation=spot_observation,
        perp_observation=perp_observation,
        spot_runtime_identity=spot_runtime_identity,
        fees=fees,
    )
    append_router_decision(log_path, decision)
    return decision


def append_router_decision(path: Path, decision: RouterDecision) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(decision.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        with os.fdopen(fd, "a", encoding="utf-8", closefd=False) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(fd)


def replay_logged_decision(
    record: dict[str, Any],
    *,
    registry: InstrumentRegistry,
    policy: RouterPolicy,
) -> RouterDecision:
    if record.get("policy_id") != policy.policy_id:
        raise RouterDecisionError("Logged router policy_id does not match replay policy")
    request = EconomicExposureRequest(**record["request"])
    runtime_raw = record.get("spot_runtime_identity")
    runtime_identity = SpotRuntimeIdentity(**runtime_raw) if isinstance(runtime_raw, dict) else None
    spot_raw = record.get("spot_candidate")
    perp_raw = record.get("perp_candidate")
    spot_observation = RouteObservation(**spot_raw["observation"]) if isinstance(spot_raw, dict) else None
    perp_observation = RouteObservation(**perp_raw["observation"]) if isinstance(perp_raw, dict) else None
    fees = FeeSchedule(**record["fee_schedule"])
    replayed = decide_route(
        request,
        registry=registry,
        policy=policy,
        spot_observation=spot_observation,
        perp_observation=perp_observation,
        spot_runtime_identity=runtime_identity,
        fees=fees,
    )
    if replayed.decision_id != record.get("decision_id"):
        raise RouterDecisionError("Logged router decision is not reproducible under the recorded assumptions")
    return replayed


def compare_expected_realized_cost(
    decision: RouterDecision,
    *,
    realized_cost_bps: float,
) -> RealizedCostComparison:
    if decision.plan is None or decision.selected_route == "no_trade":
        raise RouterDecisionError("Cannot compare realized cost for a no-trade decision")
    value = float(realized_cost_bps)
    if not isfinite(value):
        raise RouterDecisionError("realized_cost_bps must be finite")
    notional = decision.request.notional_usd
    realized_usd = notional * value / 10_000.0
    expected = decision.plan.expected_cost_bps
    expected_usd = decision.plan.expected_cost_usd
    return RealizedCostComparison(
        decision_id=decision.decision_id,
        asset=decision.request.asset,
        route=decision.plan.route,
        expected_cost_bps=expected,
        realized_cost_bps=value,
        variance_bps=value - expected,
        expected_cost_usd=expected_usd,
        realized_cost_usd=realized_usd,
        variance_usd=realized_usd - expected_usd,
    )


def _candidate_from_observation(
    request: EconomicExposureRequest,
    route: Literal["spot", "perp"],
    observation: RouteObservation | None,
    *,
    policy: RouterPolicy,
    fees: FeeSchedule,
) -> RouteCandidate | None:
    if observation is None:
        return None
    if observation.route != route:
        raise RouterDecisionError(f"Expected {route} observation")
    if observation.asset.upper() != request.asset:
        raise RouterDecisionError(f"{route} observation asset does not match economic request")
    if abs(observation.notional_usd - request.notional_usd) > max(1e-9, request.notional_usd * 1e-12):
        raise RouterDecisionError(f"{route} observation notional does not match economic request")
    if abs(observation.holding_hours - request.holding_hours) > 1e-9:
        raise RouterDecisionError(f"{route} observation holding horizon does not match economic request")
    estimate = estimate_route_cost(observation, fees=fees)
    ratio = estimate.notional_to_depth_ratio
    capacity_ok = ratio is not None and isfinite(ratio) and 0 <= ratio <= policy.max_capacity_ratio + 1e-12
    return RouteCandidate(route=route, observation=observation, estimate=estimate, capacity_ok=capacity_ok)


def _forced_perp_or_no_trade(
    *,
    policy: RouterPolicy,
    request: EconomicExposureRequest,
    row: dict[str, Any],
    reason_code: str,
    spot_runtime_identity: SpotRuntimeIdentity | None,
    spot_candidate: RouteCandidate | None,
    perp_candidate: RouteCandidate | None,
    fees: FeeSchedule,
) -> RouterDecision:
    if _viable(perp_candidate):
        return _select_perp(
            policy,
            request,
            row,
            reason_code,
            spot_runtime_identity,
            spot_candidate,
            perp_candidate,
            fees,
        )
    return _no_trade(policy, request, spot_runtime_identity, spot_candidate, perp_candidate, fees)


def _select_spot(
    policy: RouterPolicy,
    request: EconomicExposureRequest,
    row: dict[str, Any],
    reason_code: str,
    runtime: SpotRuntimeIdentity | None,
    spot_candidate: RouteCandidate | None,
    perp_candidate: RouteCandidate | None,
    fees: FeeSchedule,
) -> RouterDecision:
    if runtime is None or not _viable(spot_candidate):
        raise RouterDecisionError("Spot route selected without verified runtime identity and viable cost observation")
    assert spot_candidate is not None
    plan = ImplementationPlan(
        asset=request.asset,
        route="spot",
        instrument_id=runtime.coin_id,
        display_identity=str(row["spot"].get("ui_identity") or runtime.expected_hypercore_pair),
        hypercore_identity=runtime.expected_hypercore_pair,
        expected_cost_bps=spot_candidate.estimate.total_cost_bps,
        expected_cost_usd=spot_candidate.estimate.total_cost_usd,
        cost_model_id=policy.cost_model_id,
    )
    return _finalize(policy, request, "spot", reason_code, plan, runtime, spot_candidate, perp_candidate, fees)


def _select_perp(
    policy: RouterPolicy,
    request: EconomicExposureRequest,
    row: dict[str, Any],
    reason_code: str,
    runtime: SpotRuntimeIdentity | None,
    spot_candidate: RouteCandidate | None,
    perp_candidate: RouteCandidate | None,
    fees: FeeSchedule,
) -> RouterDecision:
    if not _viable(perp_candidate):
        raise RouterDecisionError("Perp route selected without viable cost observation")
    assert perp_candidate is not None
    identity = str(row["perp"]["identity"])
    plan = ImplementationPlan(
        asset=request.asset,
        route="perp",
        instrument_id=identity,
        display_identity=identity,
        hypercore_identity=identity,
        expected_cost_bps=perp_candidate.estimate.total_cost_bps,
        expected_cost_usd=perp_candidate.estimate.total_cost_usd,
        cost_model_id=policy.cost_model_id,
    )
    return _finalize(policy, request, "perp", reason_code, plan, runtime, spot_candidate, perp_candidate, fees)


def _no_trade(
    policy: RouterPolicy,
    request: EconomicExposureRequest,
    runtime: SpotRuntimeIdentity | None,
    spot_candidate: RouteCandidate | None,
    perp_candidate: RouteCandidate | None,
    fees: FeeSchedule,
) -> RouterDecision:
    candidates = [candidate for candidate in (spot_candidate, perp_candidate) if candidate is not None]
    reason = "NO_TRADE_LIQUIDITY_FAIL" if candidates and all(not c.capacity_ok for c in candidates) else "NO_TRADE_COST_UNAVAILABLE"
    return _finalize(policy, request, "no_trade", reason, None, runtime, spot_candidate, perp_candidate, fees)


def _validate_runtime_identity(
    request: EconomicExposureRequest,
    row: dict[str, Any],
    runtime: SpotRuntimeIdentity,
) -> None:
    expected_token = row["spot"].get("hypercore_token_candidate")
    expected_pair = row["spot"].get("hypercore_pair_candidate")
    if runtime.asset != request.asset:
        raise RouterDecisionError("Spot runtime identity asset mismatch")
    if runtime.expected_hypercore_token != expected_token or runtime.expected_hypercore_pair != expected_pair:
        raise RouterDecisionError("Spot runtime identity does not match canonical registry")
    if runtime.coin_id != f"@{runtime.pair_index}":
        raise RouterDecisionError("Spot runtime API identity must match pair index")


def _viable(candidate: RouteCandidate | None) -> bool:
    return candidate is not None and candidate.capacity_ok


def _finalize(
    policy: RouterPolicy,
    request: EconomicExposureRequest,
    selected_route: SelectedRoute,
    reason_code: str,
    plan: ImplementationPlan | None,
    spot_runtime_identity: SpotRuntimeIdentity | None,
    spot_candidate: RouteCandidate | None,
    perp_candidate: RouteCandidate | None,
    fees: FeeSchedule,
) -> RouterDecision:
    if reason_code not in policy.reason_codes:
        raise RouterDecisionError(f"Unregistered router reason code: {reason_code}")
    payload = {
        "schema_version": 1,
        "policy_id": policy.policy_id,
        "request": request.to_dict(),
        "selected_route": selected_route,
        "reason_code": reason_code,
        "plan": plan.to_dict() if plan else None,
        "spot_runtime_identity": spot_runtime_identity.to_dict() if spot_runtime_identity else None,
        "spot_candidate": spot_candidate.to_dict() if spot_candidate else None,
        "perp_candidate": perp_candidate.to_dict() if perp_candidate else None,
        "fee_schedule": asdict(fees),
    }
    decision_id = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()[:32]
    return RouterDecision(
        schema_version=1,
        decision_id=decision_id,
        policy_id=policy.policy_id,
        request=request,
        selected_route=selected_route,
        reason_code=reason_code,
        plan=plan,
        spot_runtime_identity=spot_runtime_identity,
        spot_candidate=spot_candidate,
        perp_candidate=perp_candidate,
        fee_schedule=fees,
    )
