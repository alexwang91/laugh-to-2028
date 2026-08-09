from __future__ import annotations

"""Future-only Phase-6 live-shadow observation collector.

The collector is deliberately zero-authority. It performs public/read-only HTTP
reads, preserves raw response bytes before parsing, feeds those observations
through the already-frozen P3.1 -> P3.2 -> P3.3 -> P2.4 -> Phase-6 shadow chain,
and writes a hash-bound evidence bundle. It never imports the executor, signer,
private-key handling, transfer, withdrawal, or order-submission code.

Before the Phase-6 observation gate is armed this module may be run only as a
non-crediting preflight. A scheduled decision can become a credit candidate only
when the merged gate says collector_armed=true, schedule_configured=true and
elapsed_evidence_credit_authorized=true. Durable credit is determined only after
both the evidence artifact and its separate receipt artifact upload successfully.
"""

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import requests

from .phase6_live_account_identity import verify_identity_observation
from .phase6_live_valuation import derive_standard_account_valuation


ROOT = Path(__file__).resolve().parents[2]
BOT_ROOT = ROOT / "execution" / "plan-b-bot"
INTEGRATION_ROOT = ROOT / "research" / "integration"
if str(BOT_ROOT) not in sys.path:
    sys.path.insert(0, str(BOT_ROOT))
if str(INTEGRATION_ROOT) not in sys.path:
    sys.path.insert(0, str(INTEGRATION_ROOT))

from beta_bot.data_contract import (  # noqa: E402
    CANONICAL_ASSETS,
    STRATEGY_SIGNAL_ASSETS,
    DAY_MS,
    build_canonical_daily_dataset,
    canonicalize_funding_history,
    load_data_contract,
)
from beta_bot.instrument_registry import load_instrument_registry  # noqa: E402
from beta_bot.rebalance_control import calculate_rebalance_control  # noqa: E402
from beta_bot.route_cost import (  # noqa: E402
    RouteCostError,
    basis_bps,
    observation_from_l2_book,
)
from beta_bot.router import (  # noqa: E402
    EconomicExposureRequest,
    decide_route,
    load_router_policy,
    resolve_spot_runtime_identity,
)
from beta_bot.shadow_system import (  # noqa: E402
    ShadowRouteProjection,
    build_integrated_shadow_record,
)
from beta_bot.target_engine import calculate_target  # noqa: E402


IDENTITY_PATH = ROOT / "research" / "governance" / "phase6_live_account_identity_contract.json"
GATE_PATH = ROOT / "research" / "governance" / "phase6_live_observation_gate.json"
EVIDENCE_CONTRACT_PATH = ROOT / "research" / "governance" / "phase6_live_evidence_contract.json"
HL_INFO_URL = "https://api.hyperliquid.xyz/info"
BINANCE_RAW_START = datetime(2020, 8, 1, tzinfo=timezone.utc)
HOLDING_HOURS = 24.0
REQUEST_TIMEOUT_SECONDS = 30.0
BACKEND_ID = "GITHUB_ACTIONS_ARTIFACT_V4"
RETENTION_DAYS = 90


class Phase6LiveCollectorError(RuntimeError):
    pass


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_json(value: object) -> str:
    return _sha_bytes(_canonical_json(value).encode("utf-8"))


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Phase6LiveCollectorError(f"{path} must contain a JSON object")
    return value


def decision_timestamp_for_observation(observed_at: datetime) -> datetime:
    observed = observed_at.astimezone(timezone.utc)
    return observed.replace(hour=0, minute=0, second=0, microsecond=0)


def decision_slug(decision_timestamp: str) -> str:
    parsed = datetime.fromisoformat(decision_timestamp.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc).strftime("%Y%m%dT000000Z")


def _iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _book_mid(book: Mapping[str, Any]) -> float:
    levels = book.get("levels")
    if not isinstance(levels, list) or len(levels) != 2:
        raise Phase6LiveCollectorError("l2Book missing bid/ask levels")
    if not levels[0] or not levels[1]:
        raise Phase6LiveCollectorError("l2Book has empty side")
    try:
        bid = float(levels[0][0]["px"])
        ask = float(levels[1][0]["px"])
    except (KeyError, TypeError, ValueError) as exc:
        raise Phase6LiveCollectorError("malformed l2Book top of book") from exc
    if not math.isfinite(bid) or not math.isfinite(ask) or bid <= 0 or ask <= bid:
        raise Phase6LiveCollectorError("invalid l2Book top of book")
    return (bid + ask) / 2.0


class RawCapture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.entries: list[dict[str, Any]] = []

    def _write(
        self,
        *,
        category: str,
        name: str,
        method: str,
        url: str,
        request: Mapping[str, Any],
        raw: bytes,
    ) -> Any:
        folder = self.root / category
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{name}.json"
        path.write_bytes(raw)
        relative = str(path.relative_to(self.root))
        self.entries.append(
            {
                "category": category,
                "path": relative,
                "method": method,
                "url": url,
                "request": dict(request),
                "response_sha256": _sha_bytes(raw),
                "response_bytes": len(raw),
                "authorization_header_used": False,
            }
        )
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise Phase6LiveCollectorError(f"non-JSON response for {name}") from exc

    def get_json(
        self,
        *,
        category: str,
        name: str,
        url: str,
        params: Mapping[str, Any],
    ) -> Any:
        response = requests.get(url, params=dict(params), timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return self._write(
            category=category,
            name=name,
            method="GET",
            url=url,
            request=params,
            raw=response.content,
        )

    def post_info(
        self,
        *,
        category: str,
        name: str,
        payload: Mapping[str, Any],
    ) -> Any:
        response = requests.post(HL_INFO_URL, json=dict(payload), timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return self._write(
            category=category,
            name=name,
            method="POST",
            url=HL_INFO_URL,
            request=payload,
            raw=response.content,
        )


def _fetch_binance_history(
    capture: RawCapture,
    *,
    asset: str,
    symbol: str,
    endpoint: str,
    start_ms: int,
    end_exclusive_ms: int,
) -> list[list[Any]]:
    cursor = int(start_ms)
    rows: list[list[Any]] = []
    page = 0
    while cursor < end_exclusive_ms:
        params = {
            "symbol": symbol,
            "interval": "1d",
            "timeZone": "0",
            "startTime": cursor,
            "endTime": end_exclusive_ms - 1,
            "limit": 1000,
        }
        payload = capture.get_json(
            category="raw_market",
            name=f"binance_{asset.lower()}_{page:02d}",
            url=endpoint,
            params=params,
        )
        if not isinstance(payload, list):
            raise Phase6LiveCollectorError(f"unexpected Binance response for {asset}")
        if not payload:
            break
        rows.extend(payload)
        try:
            next_cursor = int(payload[-1][0]) + DAY_MS
        except (IndexError, TypeError, ValueError) as exc:
            raise Phase6LiveCollectorError(f"malformed Binance pagination for {asset}") from exc
        if next_cursor <= cursor:
            raise Phase6LiveCollectorError(f"non-advancing Binance pagination for {asset}")
        cursor = next_cursor
        page += 1
        time.sleep(0.04)
    if not rows:
        raise Phase6LiveCollectorError(f"no Binance history returned for {asset}")
    return rows


def _independent_reference(dataset: object) -> dict[str, Any]:
    module_path = INTEGRATION_ROOT / "p3_2_target_parity.py"
    spec = importlib.util.spec_from_file_location("phase6_p3_reference", module_path)
    if spec is None or spec.loader is None:
        raise Phase6LiveCollectorError("cannot load independent P3.2 reference adapter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    value = module.research_current_target(dataset)
    if not isinstance(value, dict):
        raise Phase6LiveCollectorError("independent P3.2 reference returned invalid payload")
    return value


def _reference_parity(product: object, reference: Mapping[str, Any]) -> dict[str, Any]:
    product_weights = getattr(product, "target_weights")
    reference_weights = reference.get("target_weights", {})
    differences = {
        asset: abs(float(product_weights[asset]) - float(reference_weights[asset]))
        for asset in CANONICAL_ASSETS
    }
    gross_difference = abs(float(getattr(product, "base_gross_target")) - float(reference["gross"]))
    max_weight_difference = max(differences.values())
    passed = max_weight_difference <= 2e-10 and gross_difference <= 2e-10
    return {
        "passed": passed,
        "max_weight_abs_difference": max_weight_difference,
        "gross_abs_difference": gross_difference,
        "weight_abs_differences": differences,
        "reference_refit_session": reference.get("refit"),
        "product_refit_session": getattr(product, "regime_refit_session"),
    }


def _funding_input(
    capture: RawCapture,
    *,
    asset: str,
    as_of: datetime,
    policy: object,
) -> object:
    end_ms = int(as_of.timestamp() * 1000)
    hours = int(getattr(policy, "funding_lookback_hours"))
    start_ms = end_ms - (hours + 3) * 3_600_000
    raw = capture.post_info(
        category="raw_route",
        name=f"funding_{asset.lower()}",
        payload={
            "type": "fundingHistory",
            "coin": asset,
            "startTime": start_ms,
            "endTime": end_ms,
        },
    )
    if not isinstance(raw, list):
        raise Phase6LiveCollectorError(f"unexpected fundingHistory for {asset}")
    return canonicalize_funding_history(
        asset=asset,
        records=raw,
        router_as_of=as_of,
        policy=policy,
    )


def collect(
    *,
    output_dir: Path,
    event_name: str,
    run_id: str,
    run_attempt: str,
    workflow_sha: str,
    emergency_drill: bool,
    observed_at: datetime | None = None,
) -> dict[str, Any]:
    observed = (observed_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    decision = decision_timestamp_for_observation(observed)
    decision_text = _iso_z(decision)
    output_dir.mkdir(parents=True, exist_ok=True)
    capture = RawCapture(output_dir)

    identity_contract = _load_json(IDENTITY_PATH)
    gate = _load_json(GATE_PATH)
    evidence_contract = _load_json(EVIDENCE_CONTRACT_PATH)
    address = identity_contract.get("account_address")
    if not isinstance(address, str):
        raise Phase6LiveCollectorError("Phase-6 identity is not bound")

    armed = gate.get("collector_armed") is True
    schedule_configured = gate.get("schedule_configured") is True
    elapsed_authorized = gate.get("elapsed_evidence_credit_authorized") is True
    if event_name == "schedule" and not (armed and schedule_configured and elapsed_authorized):
        raise Phase6LiveCollectorError("scheduled collector invoked while Phase-6 gate is not fully armed")
    if event_name not in {"schedule", "workflow_dispatch"}:
        raise Phase6LiveCollectorError(f"unsupported live collector event: {event_name}")

    role_response = capture.post_info(
        category="raw_account",
        name="user_role",
        payload={"type": "userRole", "user": address},
    )
    abstraction_response = capture.post_info(
        category="raw_account",
        name="user_abstraction",
        payload={"type": "userAbstraction", "user": address},
    )
    compatible = verify_identity_observation(
        account_address=address,
        user_role_response=role_response,
        user_abstraction_response=abstraction_response,
    )

    perp_state = capture.post_info(
        category="raw_account",
        name="clearinghouse_state",
        payload={"type": "clearinghouseState", "user": address},
    )
    spot_state = capture.post_info(
        category="raw_account",
        name="spot_clearinghouse_state",
        payload={"type": "spotClearinghouseState", "user": address},
    )
    if not isinstance(perp_state, dict) or not isinstance(spot_state, dict):
        raise Phase6LiveCollectorError("Hyperliquid account state response is malformed")

    data_policy = load_data_contract()
    start_ms = int(BINANCE_RAW_START.timestamp() * 1000)
    end_exclusive_ms = int(decision.timestamp() * 1000)
    source_batches: dict[str, Sequence[tuple[str, Sequence[Sequence[Any]]]]] = {}
    endpoint = data_policy.strategy_endpoints[0]
    for asset in STRATEGY_SIGNAL_ASSETS:
        symbol = data_policy.source_symbol(asset, start_ms)
        rows = _fetch_binance_history(
            capture,
            asset=asset,
            symbol=symbol,
            endpoint=endpoint,
            start_ms=start_ms,
            end_exclusive_ms=end_exclusive_ms,
        )
        source_batches[asset] = [(symbol, rows)]
    dataset = build_canonical_daily_dataset(
        source_batches=source_batches,
        decision_timestamp=decision,
        policy=data_policy,
    )

    registry = load_instrument_registry()
    router_policy = load_router_policy()
    spot_meta = capture.post_info(category="raw_route", name="spot_meta", payload={"type": "spotMeta"})
    if not isinstance(spot_meta, dict):
        raise Phase6LiveCollectorError("spotMeta response is malformed")

    spot_identity: dict[str, object] = {}
    spot_books: dict[str, dict[str, Any]] = {}
    spot_marks: dict[str, float] = {}
    for asset, token in (("BTC", "UBTC"), ("ETH", "UETH"), ("SOL", "USOL")):
        identity = resolve_spot_runtime_identity(registry, asset, spot_meta)
        spot_identity[asset] = identity
        book = capture.post_info(
            category="raw_route",
            name=f"spot_book_{asset.lower()}",
            payload={"type": "l2Book", "coin": identity.coin_id},
        )
        if not isinstance(book, dict):
            raise Phase6LiveCollectorError(f"spot l2Book response is malformed for {asset}")
        spot_books[asset] = book
        spot_marks[token] = _book_mid(book)

    valuation = derive_standard_account_valuation(
        user_abstraction=str(compatible["user_abstraction"]),
        spot_state=spot_state,
        perp_state=perp_state,
        spot_mark_by_token=spot_marks,
    )
    equity = float(valuation["account_equity_usd"])
    current_positions = dict(valuation["current_positions_notional_usd"])

    target = calculate_target(
        daily_dataset=dataset,
        account_equity_usd=equity,
        current_positions=current_positions,
    )
    reference = _independent_reference(dataset)
    parity = _reference_parity(target, reference)
    if not parity["passed"]:
        raise Phase6LiveCollectorError(f"independent P3.2 target reference mismatch: {parity}")

    plan = calculate_rebalance_control(
        target=target,
        account_equity_usd=equity,
        current_positions_notional_usd=current_positions,
    )

    perp_books: dict[str, dict[str, Any]] = {}
    funding_inputs: dict[str, object] = {}
    route_projections: dict[str, ShadowRouteProjection] = {}
    route_decisions: dict[str, dict[str, Any]] = {}
    for asset in CANONICAL_ASSETS:
        perp_book = capture.post_info(
            category="raw_route",
            name=f"perp_book_{asset.lower()}",
            payload={"type": "l2Book", "coin": asset},
        )
        if not isinstance(perp_book, dict):
            raise Phase6LiveCollectorError(f"perp l2Book response is malformed for {asset}")
        perp_books[asset] = perp_book
        funding = _funding_input(capture, asset=asset, as_of=observed, policy=data_policy)
        funding_inputs[asset] = funding

        notional = abs(float(plan.proposed_delta_notionals_usd[asset]))
        request = EconomicExposureRequest(
            decision_timestamp=target.decision_timestamp,
            asset=asset,
            direction="long",
            exposure_role="base",
            notional_usd=notional,
            holding_hours=HOLDING_HOURS,
            target_revision=target.digest(),
        )
        if notional <= 1e-9:
            decision_row = decide_route(
                request,
                registry=registry,
                policy=router_policy,
                spot_observation=None,
                perp_observation=None,
                spot_runtime_identity=None,
            )
        else:
            spot_observation = None
            runtime_identity = spot_identity.get(asset)
            if asset in spot_books:
                try:
                    spot_observation = observation_from_l2_book(
                        asset=asset,
                        route="spot",
                        book=spot_books[asset],
                        notional_usd=notional,
                        holding_hours=HOLDING_HOURS,
                    )
                except RouteCostError:
                    spot_observation = None
            funding_bps_per_hour = float(getattr(funding, "average_bps_per_hour"))
            entry_basis = 0.0
            if asset in spot_books:
                entry_basis = basis_bps(
                    perp_price=_book_mid(perp_book),
                    verified_spot_price=_book_mid(spot_books[asset]),
                )
            try:
                perp_observation = observation_from_l2_book(
                    asset=asset,
                    route="perp",
                    book=perp_book,
                    notional_usd=notional,
                    holding_hours=HOLDING_HOURS,
                    funding_bps_per_hour=funding_bps_per_hour,
                    entry_basis_bps=entry_basis,
                    expected_exit_basis_bps=0.0,
                )
            except RouteCostError:
                perp_observation = None
            decision_row = decide_route(
                request,
                registry=registry,
                policy=router_policy,
                spot_observation=spot_observation,
                perp_observation=perp_observation,
                spot_runtime_identity=runtime_identity,
            )
        route_decisions[asset] = decision_row.to_dict()
        route_projections[asset] = ShadowRouteProjection(
            asset=asset,
            selected_route=decision_row.selected_route,
            reason_code=decision_row.reason_code,
            instrument_id=decision_row.plan.instrument_id if decision_row.plan else None,
            expected_cost_bps=decision_row.plan.expected_cost_bps if decision_row.plan else None,
            capacity_ok=decision_row.plan is not None or decision_row.selected_route == "no_trade",
        )

    schedule_ok = event_name == "workflow_dispatch" or (
        event_name == "schedule" and decision.date() == observed.date()
    )
    emergency_active = bool(emergency_drill and event_name == "workflow_dispatch")
    shadow = build_integrated_shadow_record(
        plan=plan,
        route_projections=route_projections,
        offline_reference_target_weights=reference["target_weights"],
        feature_reference_ok=bool(parity["passed"]),
        data_complete=True,
        instrument_identity_ok=True,
        cost_model_ok=True,
        state_transition_explained=True,
        schedule_ok=schedule_ok,
        emergency_active=emergency_active,
    )

    raw_manifest = {
        "schema_version": 1,
        "decision_timestamp": decision_text,
        "observed_at": _iso_z(observed),
        "account_address": address,
        "raw_responses": capture.entries,
        "data_contract_id": dataset.contract_id,
        "data_digest": dataset.digest(),
        "valuation_contract_id": valuation["valuation_contract_id"],
        "target_digest": target.digest(),
        "rebalance_digest": plan.digest(),
        "target_reference_parity": parity,
        "route_decision_ids": {
            asset: route_decisions[asset]["decision_id"] for asset in CANONICAL_ASSETS
        },
        "secret_material_present": False,
        "authorization_headers_used_for_market_or_account_reads": False,
    }
    manifest_path = output_dir / "input_provenance_manifest.json"
    manifest_bytes = (_canonical_json(raw_manifest) + "\n").encode("utf-8")
    manifest_path.write_bytes(manifest_bytes)
    input_digest = _sha_bytes(manifest_bytes)

    shadow_path = output_dir / "shadow_record.json"
    shadow_bytes = (shadow.canonical_json() + "\n").encode("utf-8")
    shadow_path.write_bytes(shadow_bytes)
    shadow_digest = _sha_bytes(shadow_bytes)

    evidence_identity = {
        "decision_timestamp": decision_text,
        "observed_at": _iso_z(observed),
        "input_provenance_digest": input_digest,
        "shadow_record_digest": shadow_digest,
        "github_run_id": str(run_id),
        "github_run_attempt": str(run_attempt),
        "workflow_sha": str(workflow_sha),
    }
    evidence_object_digest = _sha_json(evidence_identity)
    credit_candidate = bool(
        armed
        and schedule_configured
        and elapsed_authorized
        and event_name == "schedule"
        and schedule_ok
        and not emergency_active
    )
    metadata = {
        **evidence_identity,
        "evidence_object_digest": evidence_object_digest,
        "decision_slug": decision_slug(decision_text),
        "collector_armed": armed,
        "schedule_configured": schedule_configured,
        "elapsed_evidence_credit_authorized": elapsed_authorized,
        "event_name": event_name,
        "scheduled_decision_credit_candidate": credit_candidate,
        "emergency_drill_candidate": emergency_active and armed,
        "preflight_only": not armed,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
        "account_equity_usd": equity,
        "shadow_status": shadow.status,
        "shadow_alerts": list(shadow.alerts),
        "evidence_contract_status": evidence_contract.get("status"),
    }
    (output_dir / "evidence_metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return metadata


def finalize_receipt(
    *,
    evidence_dir: Path,
    output_path: Path,
    artifact_id: str,
    artifact_url: str,
    artifact_digest: str,
) -> dict[str, Any]:
    metadata = _load_json(evidence_dir / "evidence_metadata.json")
    required = {
        "github_run_id",
        "github_run_attempt",
        "workflow_sha",
        "decision_timestamp",
        "observed_at",
        "shadow_record_digest",
        "input_provenance_digest",
        "evidence_object_digest",
    }
    missing = sorted(required - set(metadata))
    if missing:
        raise Phase6LiveCollectorError(f"evidence metadata missing receipt fields: {missing}")
    receipt = {key: metadata[key] for key in sorted(required)}
    receipt.update(
        {
            "evidence_artifact_id": str(artifact_id),
            "evidence_artifact_url": str(artifact_url),
            "evidence_artifact_digest": str(artifact_digest),
            "backend_id": BACKEND_ID,
            "retention_days": RETENTION_DAYS,
            "scheduled_decision_credit_candidate": bool(
                metadata.get("scheduled_decision_credit_candidate")
            ),
            "emergency_drill_candidate": bool(metadata.get("emergency_drill_candidate")),
            "credit_requires_this_receipt_artifact_upload_success": True,
            "production_authorized": False,
        }
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def _write_failure(path: Path, exc: Exception) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "status": "FAIL_CLOSED",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "production_authorized": False,
                "signature_authorized": False,
                "order_submission_authorized": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase-6 zero-authority live-shadow collector")
    sub = parser.add_subparsers(dest="command", required=True)

    collect_parser = sub.add_parser("collect")
    collect_parser.add_argument("--output-dir", type=Path, required=True)
    collect_parser.add_argument("--event-name", required=True)
    collect_parser.add_argument("--run-id", required=True)
    collect_parser.add_argument("--run-attempt", required=True)
    collect_parser.add_argument("--workflow-sha", required=True)
    collect_parser.add_argument("--emergency-drill", action="store_true")

    receipt_parser = sub.add_parser("finalize-receipt")
    receipt_parser.add_argument("--evidence-dir", type=Path, required=True)
    receipt_parser.add_argument("--output", type=Path, required=True)
    receipt_parser.add_argument("--artifact-id", required=True)
    receipt_parser.add_argument("--artifact-url", required=True)
    receipt_parser.add_argument("--artifact-digest", required=True)

    args = parser.parse_args(argv)
    if args.command == "finalize-receipt":
        finalize_receipt(
            evidence_dir=args.evidence_dir,
            output_path=args.output,
            artifact_id=args.artifact_id,
            artifact_url=args.artifact_url,
            artifact_digest=args.artifact_digest,
        )
        return 0

    try:
        metadata = collect(
            output_dir=args.output_dir,
            event_name=args.event_name,
            run_id=args.run_id,
            run_attempt=args.run_attempt,
            workflow_sha=args.workflow_sha,
            emergency_drill=args.emergency_drill,
        )
    except Exception as exc:
        _write_failure(args.output_dir / "collector_failure.json", exc)
        print(f"Phase-6 live collector: FAIL_CLOSED ({type(exc).__name__}: {exc})")
        return 1
    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
