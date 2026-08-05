from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from run_carry_pm_0035 import (
    ADDRESS_RE,
    BTC_PERP_API_COIN,
    BTC_SPOT_API_COIN,
    MATCH_TOLERANCE,
    MAX_CLOSED_UBTC_RESIDUAL_USD,
    MAX_INCREMENTAL_MAINTENANCE_FRACTION,
    MAX_PORTFOLIO_MARGIN_RATIO,
    MAX_PROBE_NOTIONAL_USD,
    MAX_SPOT_QTY_CHANGE_FRACTION,
    USDC_TOKEN_INDEX,
    account_fingerprint,
    as_float,
    book_mid,
    is_portfolio_margin_stage,
    stage_clean,
    summarize_borrow_state,
    summarize_clearinghouse,
    summarize_spot_state,
)

AUDIT_ID = "CARRY-PM-0037-MEASUREMENT-INTEGRITY"
INFO_URL = "https://api.hyperliquid.xyz/info"
MAX_SNAPSHOT_GAP_SECONDS = 300.0
MAX_MID_DRIFT_FRACTION = 0.0025
MAX_ATTEMPTS_TOTAL = 4
RETRY_BACKOFF_SECONDS = (0.5, 1.0, 2.0)
RETRYABLE_HTTP_STATUSES = {408, 429, 500, 502, 503, 504}
OUTCOME_RELEASES = "PM_RELEASES_MARGIN"
OUTCOME_CONSUMES = "PM_CONSUMES_MARGIN"
OUTCOME_INCONCLUSIVE = "MEASUREMENT_INCONCLUSIVE"


def post_info(payload: dict[str, Any]) -> Any:
    """Read Hyperliquid /info with the preregistered bounded retry policy."""

    last_error: Exception | None = None
    for attempt in range(MAX_ATTEMPTS_TOTAL):
        try:
            response = requests.post(INFO_URL, json=payload, timeout=30)
        except requests.RequestException as exc:
            last_error = exc
            if attempt == MAX_ATTEMPTS_TOTAL - 1:
                raise
        else:
            if response.status_code not in RETRYABLE_HTTP_STATUSES:
                response.raise_for_status()
                return response.json()
            last_error = requests.HTTPError(
                f"retryable HTTP {response.status_code} from Hyperliquid /info",
                response=response,
            )
            if attempt == MAX_ATTEMPTS_TOTAL - 1:
                raise last_error
        time.sleep(RETRY_BACKOFF_SECONDS[attempt])
    if last_error is not None:
        raise last_error
    raise RuntimeError("bounded retry loop ended without response or exception")


def collect_snapshot(user: str, label: str) -> dict[str, Any]:
    if not ADDRESS_RE.fullmatch(user):
        raise ValueError("HL_PM_PROBE_USER must be a 42-character 0x address")

    abstraction = post_info({"type": "userAbstraction", "user": user})
    spot_raw = post_info({"type": "spotClearinghouseState", "user": user})
    borrow_raw = post_info({"type": "borrowLendUserState", "user": user})
    perp_raw = post_info({"type": "clearinghouseState", "user": user})
    spot_book = post_info({"type": "l2Book", "coin": BTC_SPOT_API_COIN})
    perp_book = post_info({"type": "l2Book", "coin": BTC_PERP_API_COIN})

    spot = summarize_spot_state(spot_raw)
    perp = summarize_clearinghouse(perp_raw)
    borrow = summarize_borrow_state(borrow_raw)
    spot_mid = book_mid(spot_book)
    perp_mid = book_mid(perp_book)
    ubtc_total = as_float(spot.get("ubtc", {}).get("total")) or 0.0
    btc_szi = as_float(perp.get("btc_position", {}).get("szi")) or 0.0
    spot_notional = ubtc_total * spot_mid if spot_mid is not None else None
    short_notional = abs(btc_szi) * perp_mid if perp_mid is not None and btc_szi < 0 else 0.0
    match_mismatch = None
    if spot_notional and short_notional:
        match_mismatch = abs(spot_notional - short_notional) / max(spot_notional, short_notional)

    return {
        "audit_id": AUDIT_ID,
        "label": label,
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "account_fingerprint": account_fingerprint(user),
        "user_abstraction": abstraction,
        "spot": spot,
        "borrow_lend": borrow,
        "perp": perp,
        "market": {"ubtc_spot_mid": spot_mid, "btc_perp_mid": perp_mid},
        "derived": {
            "ubtc_spot_notional": spot_notional,
            "btc_short_notional": short_notional,
            "matched_notional": min(spot_notional, short_notional) if spot_notional is not None else None,
            "match_mismatch_fraction": match_mismatch,
            "has_ubtc_spot": bool(ubtc_total > 0),
            "has_btc_short": bool(btc_szi < 0),
            "has_other_perp_positions": bool(perp.get("other_positions")),
        },
    }


def available_usdc(snapshot: dict[str, Any]) -> float | None:
    return as_float(
        snapshot.get("spot", {})
        .get("tokenToAvailableAfterMaintenance", {})
        .get(str(USDC_TOKEN_INDEX))
    )


def parse_observed_at(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(timezone.utc)


def midpoint_drift(spot_snapshot: dict[str, Any], matched_snapshot: dict[str, Any], key: str) -> float | None:
    before = as_float(spot_snapshot.get("market", {}).get(key))
    after = as_float(matched_snapshot.get("market", {}).get(key))
    if before is None or after is None or before <= 0 or after <= 0:
        return None
    return abs(after / before - 1.0)


def measurement_integrity(spot: dict[str, Any], matched: dict[str, Any]) -> dict[str, Any]:
    spot_time = parse_observed_at(spot.get("observed_at_utc"))
    matched_time = parse_observed_at(matched.get("observed_at_utc"))
    gap_seconds = None
    if spot_time is not None and matched_time is not None:
        gap_seconds = (matched_time - spot_time).total_seconds()

    spot_drift = midpoint_drift(spot, matched, "ubtc_spot_mid")
    perp_drift = midpoint_drift(spot, matched, "btc_perp_mid")
    gap_ok = bool(
        gap_seconds is not None
        and gap_seconds >= 0.0
        and gap_seconds <= MAX_SNAPSHOT_GAP_SECONDS
    )
    drift_ok = bool(
        spot_drift is not None
        and perp_drift is not None
        and spot_drift <= MAX_MID_DRIFT_FRACTION
        and perp_drift <= MAX_MID_DRIFT_FRACTION
    )
    return {
        "snapshot_gap_seconds": gap_seconds,
        "snapshot_gap_within_bound": gap_ok,
        "spot_mid_drift_fraction": spot_drift,
        "perp_mid_drift_fraction": perp_drift,
        "max_observed_mid_drift_fraction": (
            max(spot_drift, perp_drift)
            if spot_drift is not None and perp_drift is not None
            else None
        ),
        "mid_drift_within_bound": drift_ok,
    }


def classify_margin_outcome(
    raw_available_change: float | None,
    integrity: dict[str, Any],
    short_notional: float,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if not integrity["snapshot_gap_within_bound"]:
        reasons.append("snapshot_gap_out_of_bound_or_missing")
    if not integrity["mid_drift_within_bound"]:
        reasons.append("mid_drift_out_of_bound_or_missing")
    if raw_available_change is None:
        reasons.append("available_after_maintenance_missing")
    if short_notional <= 0:
        reasons.append("matched_short_notional_nonpositive")
    if reasons:
        return OUTCOME_INCONCLUSIVE, reasons
    if raw_available_change < 0:
        return OUTCOME_RELEASES, reasons
    if raw_available_change > 0:
        return OUTCOME_CONSUMES, reasons
    return OUTCOME_INCONCLUSIVE, ["raw_available_change_exactly_zero"]


def compare_snapshots(
    cash: dict[str, Any],
    spot: dict[str, Any],
    matched: dict[str, Any],
    closed: dict[str, Any],
) -> dict[str, Any]:
    snapshots = (cash, spot, matched, closed)
    fingerprints = {snapshot.get("account_fingerprint") for snapshot in snapshots}
    same_account = len(fingerprints) == 1 and None not in fingerprints

    cash_ubtc_notional = as_float(cash.get("derived", {}).get("ubtc_spot_notional"))
    spot_notional = as_float(spot.get("derived", {}).get("ubtc_spot_notional")) or 0.0
    matched_spot_notional = as_float(matched.get("derived", {}).get("ubtc_spot_notional")) or 0.0
    short_notional = as_float(matched.get("derived", {}).get("btc_short_notional")) or 0.0
    mismatch = as_float(matched.get("derived", {}).get("match_mismatch_fraction"))
    pm_ratio = as_float(matched.get("spot", {}).get("portfolioMarginRatio"))

    spot_ubtc_qty = abs(as_float(spot.get("spot", {}).get("ubtc", {}).get("total")) or 0.0)
    matched_ubtc_qty = abs(as_float(matched.get("spot", {}).get("ubtc", {}).get("total")) or 0.0)
    spot_qty_change_fraction = None
    if spot_ubtc_qty > 0:
        spot_qty_change_fraction = abs(matched_ubtc_qty - spot_ubtc_qty) / spot_ubtc_qty

    available_spot = available_usdc(spot)
    available_matched = available_usdc(matched)
    raw_available_change = None
    if available_spot is not None and available_matched is not None and short_notional > 0:
        raw_available_change = available_spot - available_matched

    integrity = measurement_integrity(spot, matched)
    outcome_state, inconclusive_reasons = classify_margin_outcome(
        raw_available_change, integrity, short_notional
    )
    consumed_margin_usdc = (
        float(raw_available_change)
        if outcome_state == OUTCOME_CONSUMES and raw_available_change is not None
        else 0.0
    )
    released_margin_usdc = (
        float(-raw_available_change)
        if outcome_state == OUTCOME_RELEASES and raw_available_change is not None
        else 0.0
    )
    consumed_fraction = (
        consumed_margin_usdc / short_notional
        if outcome_state == OUTCOME_CONSUMES and short_notional > 0
        else None
    )
    released_fraction = (
        released_margin_usdc / short_notional
        if outcome_state == OUTCOME_RELEASES and short_notional > 0
        else None
    )
    if outcome_state == OUTCOME_RELEASES:
        capital_efficiency_pass = True
    elif outcome_state == OUTCOME_CONSUMES:
        capital_efficiency_pass = bool(
            consumed_fraction is not None
            and consumed_fraction <= MAX_INCREMENTAL_MAINTENANCE_FRACTION
        )
    else:
        capital_efficiency_pass = False

    closed_ubtc_notional = as_float(closed.get("derived", {}).get("ubtc_spot_notional"))
    closed_btc_szi = as_float(closed.get("perp", {}).get("btc_position", {}).get("szi")) or 0.0

    checks = {
        "same_account": same_account,
        "portfolio_margin_mode_all_stages": all(is_portfolio_margin_stage(snapshot) for snapshot in snapshots),
        "dedicated_account_no_other_perps": all(stage_clean(snapshot) for snapshot in snapshots),
        "cash_stage_has_no_btc_short": not bool(cash.get("derived", {}).get("has_btc_short")),
        "cash_stage_ubtc_residual_below_1_usd": (
            cash_ubtc_notional is not None
            and abs(cash_ubtc_notional) <= MAX_CLOSED_UBTC_RESIDUAL_USD
        ),
        "spot_stage_has_ubtc": bool(spot.get("derived", {}).get("has_ubtc_spot")),
        "spot_stage_has_no_btc_short": not bool(spot.get("derived", {}).get("has_btc_short")),
        "probe_notional_within_cap_plus_5pct_execution_tolerance": (
            0 < spot_notional <= MAX_PROBE_NOTIONAL_USD * 1.05
        ),
        "matched_stage_has_ubtc": bool(matched.get("derived", {}).get("has_ubtc_spot")),
        "matched_stage_has_btc_short": bool(matched.get("derived", {}).get("has_btc_short")),
        "spot_quantity_preserved_to_matched": (
            spot_qty_change_fraction is not None
            and spot_qty_change_fraction <= MAX_SPOT_QTY_CHANGE_FRACTION
        ),
        "matched_base_notional_within_2pct": mismatch is not None and mismatch <= MATCH_TOLERANCE,
        "portfolio_margin_ratio_below_0_50": pm_ratio is not None and pm_ratio < MAX_PORTFOLIO_MARGIN_RATIO,
        "snapshot_gap_within_bound": bool(integrity["snapshot_gap_within_bound"]),
        "mid_drift_within_bound": bool(integrity["mid_drift_within_bound"]),
        "measurement_outcome_conclusive": outcome_state != OUTCOME_INCONCLUSIVE,
        "capital_efficiency_gate": capital_efficiency_pass,
        "closed_stage_flat_btc": abs(closed_btc_szi) <= 1e-12,
        "closed_stage_ubtc_residual_below_1_usd": (
            closed_ubtc_notional is not None
            and abs(closed_ubtc_notional) <= MAX_CLOSED_UBTC_RESIDUAL_USD
        ),
    }
    passed = bool(all(checks.values()))

    return {
        "audit_id": AUDIT_ID,
        "status": "PASS_PM_ACCOUNT_BEHAVIOR" if passed else "FAIL_OR_INCONCLUSIVE_PM_ACCOUNT_BEHAVIOR",
        "outcome_state": outcome_state,
        "measurement_inconclusive_reasons": inconclusive_reasons,
        "account_fingerprint": cash.get("account_fingerprint") if same_account else None,
        "read_only": True,
        "frozen_limits": {
            "max_probe_notional_usd": MAX_PROBE_NOTIONAL_USD,
            "probe_execution_tolerance_fraction": 0.05,
            "match_tolerance_fraction": MATCH_TOLERANCE,
            "max_spot_qty_change_fraction": MAX_SPOT_QTY_CHANGE_FRACTION,
            "max_portfolio_margin_ratio": MAX_PORTFOLIO_MARGIN_RATIO,
            "max_incremental_maintenance_fraction": MAX_INCREMENTAL_MAINTENANCE_FRACTION,
            "max_closed_ubtc_residual_notional_usd": MAX_CLOSED_UBTC_RESIDUAL_USD,
            "max_snapshot_gap_seconds": MAX_SNAPSHOT_GAP_SECONDS,
            "max_mid_drift_fraction": MAX_MID_DRIFT_FRACTION,
        },
        "measurement_integrity": integrity,
        "measurements": {
            "cash_stage_ubtc_notional": cash_ubtc_notional,
            "spot_stage_ubtc_quantity": spot_ubtc_qty,
            "matched_stage_ubtc_quantity": matched_ubtc_qty,
            "spot_to_matched_ubtc_quantity_change_fraction": spot_qty_change_fraction,
            "spot_stage_ubtc_notional": spot_notional,
            "matched_stage_ubtc_notional": matched_spot_notional,
            "matched_stage_btc_short_notional": short_notional,
            "matched_stage_mismatch_fraction": mismatch,
            "matched_stage_portfolio_margin_ratio": pm_ratio,
            "spot_stage_available_after_maintenance_usdc": available_spot,
            "matched_stage_available_after_maintenance_usdc": available_matched,
            "raw_available_after_maintenance_change_usdc": raw_available_change,
            "consumed_margin_usdc": consumed_margin_usdc,
            "released_margin_usdc": released_margin_usdc,
            "consumed_margin_fraction_of_short_notional": consumed_fraction,
            "released_margin_fraction_of_short_notional": released_fraction,
            "closed_stage_ubtc_notional": closed_ubtc_notional,
            "matched_stage_borrow_value": as_float(matched.get("borrow_lend", {}).get("total_borrow_value")),
            "matched_stage_health": matched.get("borrow_lend", {}).get("health"),
            "matched_stage_health_factor": as_float(matched.get("borrow_lend", {}).get("healthFactor")),
        },
        "checks": checks,
        "decision": (
            "PASS is only a measurement result. It may authorize a later stack experiment only if the independent CARRY-RF-0036R1 upstream carry gate remains qualified; no production, leverage search, size optimization or strategy change is authorized."
            if passed
            else "Do not authorize a PM-aware stack from this probe. Preserve fail/inconclusive evidence and do not tune timing, drift, size, match, PM-ratio or capital thresholds from the observed outcome."
        ),
    }


def load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="CARRY-PM-0037 read-only measurement-integrity probe")
    sub = parser.add_subparsers(dest="command", required=True)

    snap = sub.add_parser("snapshot")
    snap.add_argument("--user", required=True)
    snap.add_argument(
        "--label",
        required=True,
        choices=["cash", "spot", "matched", "closed", "readiness"],
    )
    snap.add_argument("--output", required=True)

    comp = sub.add_parser("compare")
    comp.add_argument("--cash", required=True)
    comp.add_argument("--spot", required=True)
    comp.add_argument("--matched", required=True)
    comp.add_argument("--closed", required=True)
    comp.add_argument("--output", required=True)

    args = parser.parse_args()
    if args.command == "snapshot":
        report = collect_snapshot(args.user, args.label)
    else:
        report = compare_snapshots(
            load_json(args.cash),
            load_json(args.spot),
            load_json(args.matched),
            load_json(args.closed),
        )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
