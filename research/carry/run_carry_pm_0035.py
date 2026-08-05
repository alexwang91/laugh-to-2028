from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

AUDIT_ID = "CARRY-PM-0035-ACCOUNT-BEHAVIOR"
INFO_URL = "https://api.hyperliquid.xyz/info"
UBTC_TOKEN_INDEX = 197
USDC_TOKEN_INDEX = 0
BTC_SPOT_API_COIN = "@142"
BTC_PERP_API_COIN = "BTC"
MATCH_TOLERANCE = 0.02
MAX_PROBE_NOTIONAL_USD = 500.0
MAX_PORTFOLIO_MARGIN_RATIO = 0.50
MAX_INCREMENTAL_MAINTENANCE_FRACTION = 0.25
MAX_CLOSED_UBTC_RESIDUAL_USD = 1.0
ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def post_info(payload: dict[str, Any]) -> Any:
    response = requests.post(INFO_URL, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def account_fingerprint(user: str) -> str:
    return hashlib.sha256(user.lower().encode("utf-8")).hexdigest()[:16]


def tuple_map(rows: Any) -> dict[int, Any]:
    out: dict[int, Any] = {}
    if not isinstance(rows, list):
        return out
    for row in rows:
        if isinstance(row, list) and len(row) == 2:
            try:
                out[int(row[0])] = row[1]
            except (TypeError, ValueError):
                continue
    return out


def spot_balance(spot_state: dict[str, Any], token_index: int) -> dict[str, Any]:
    for row in spot_state.get("balances", []) if isinstance(spot_state, dict) else []:
        if isinstance(row, dict) and row.get("token") == token_index:
            return {
                "coin": row.get("coin"),
                "token": token_index,
                "total": as_float(row.get("total")) or 0.0,
                "hold": as_float(row.get("hold")) or 0.0,
                "entryNtl": as_float(row.get("entryNtl")) or 0.0,
                "spotHold": as_float(row.get("spotHold")),
                "ltv": as_float(row.get("ltv")),
                "borrowed": as_float(row.get("borrowed")),
                "supplied": as_float(row.get("supplied")),
            }
    return {
        "coin": None,
        "token": token_index,
        "total": 0.0,
        "hold": 0.0,
        "entryNtl": 0.0,
        "spotHold": None,
        "ltv": None,
        "borrowed": None,
        "supplied": None,
    }


def btc_position(clearinghouse_state: dict[str, Any]) -> dict[str, Any]:
    for row in clearinghouse_state.get("assetPositions", []) if isinstance(clearinghouse_state, dict) else []:
        position = row.get("position", {}) if isinstance(row, dict) else {}
        if position.get("coin") == "BTC":
            leverage = position.get("leverage") if isinstance(position.get("leverage"), dict) else {}
            return {
                "szi": as_float(position.get("szi")) or 0.0,
                "positionValue": abs(as_float(position.get("positionValue")) or 0.0),
                "entryPx": as_float(position.get("entryPx")),
                "marginUsed": as_float(position.get("marginUsed")),
                "unrealizedPnl": as_float(position.get("unrealizedPnl")),
                "liquidationPx": as_float(position.get("liquidationPx")),
                "leverage_type": leverage.get("type"),
                "leverage_value": as_float(leverage.get("value")),
            }
    return {
        "szi": 0.0,
        "positionValue": 0.0,
        "entryPx": None,
        "marginUsed": None,
        "unrealizedPnl": None,
        "liquidationPx": None,
        "leverage_type": None,
        "leverage_value": None,
    }


def other_positions(clearinghouse_state: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in clearinghouse_state.get("assetPositions", []) if isinstance(clearinghouse_state, dict) else []:
        position = row.get("position", {}) if isinstance(row, dict) else {}
        coin = position.get("coin")
        szi = as_float(position.get("szi")) or 0.0
        if coin and coin != "BTC" and abs(szi) > 0:
            out.append(
                {
                    "coin": coin,
                    "szi": szi,
                    "positionValue": abs(as_float(position.get("positionValue")) or 0.0),
                }
            )
    return out


def book_mid(book: Any) -> float | None:
    if not isinstance(book, dict):
        return None
    levels = book.get("levels")
    if not isinstance(levels, list) or len(levels) < 2 or not levels[0] or not levels[1]:
        return None
    try:
        bid = float(levels[0][0]["px"])
        ask = float(levels[1][0]["px"])
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    return (bid + ask) / 2.0


def summarize_borrow_state(state: Any) -> dict[str, Any]:
    state = state if isinstance(state, dict) else {}
    rows = []
    total_borrow_value = 0.0
    total_supply_value = 0.0
    for token, token_state in tuple_map(state.get("tokenToState")).items():
        token_state = token_state if isinstance(token_state, dict) else {}
        borrow = token_state.get("borrow", {}) if isinstance(token_state.get("borrow"), dict) else {}
        supply = token_state.get("supply", {}) if isinstance(token_state.get("supply"), dict) else {}
        borrow_value = as_float(borrow.get("value")) or 0.0
        supply_value = as_float(supply.get("value")) or 0.0
        total_borrow_value += abs(borrow_value)
        total_supply_value += abs(supply_value)
        rows.append(
            {
                "token": token,
                "borrow_basis": as_float(borrow.get("basis")),
                "borrow_value": borrow_value,
                "supply_basis": as_float(supply.get("basis")),
                "supply_value": supply_value,
            }
        )
    return {
        "health": state.get("health"),
        "healthFactor": as_float(state.get("healthFactor")),
        "total_borrow_value": total_borrow_value,
        "total_supply_value": total_supply_value,
        "token_states": rows,
    }


def summarize_clearinghouse(state: Any) -> dict[str, Any]:
    state = state if isinstance(state, dict) else {}
    margin = state.get("marginSummary", {}) if isinstance(state.get("marginSummary"), dict) else {}
    cross = state.get("crossMarginSummary", {}) if isinstance(state.get("crossMarginSummary"), dict) else {}
    return {
        "marginSummary": {
            key: as_float(margin.get(key))
            for key in ("accountValue", "totalNtlPos", "totalRawUsd", "totalMarginUsed")
        },
        "crossMarginSummary": {
            key: as_float(cross.get(key))
            for key in ("accountValue", "totalNtlPos", "totalRawUsd", "totalMarginUsed")
        },
        "crossMaintenanceMarginUsed": as_float(state.get("crossMaintenanceMarginUsed")),
        "withdrawable": as_float(state.get("withdrawable")),
        "btc_position": btc_position(state),
        "other_positions": other_positions(state),
        "time": state.get("time"),
    }


def summarize_spot_state(state: Any) -> dict[str, Any]:
    state = state if isinstance(state, dict) else {}
    return {
        "portfolioMarginEnabled": bool(state.get("portfolioMarginEnabled")),
        "portfolioMarginRatio": as_float(state.get("portfolioMarginRatio")),
        "tokenToPortfolioBorrowRatio": {
            str(key): as_float(value)
            for key, value in tuple_map(state.get("tokenToPortfolioBorrowRatio")).items()
        },
        "tokenToAvailableAfterMaintenance": {
            str(key): as_float(value)
            for key, value in tuple_map(state.get("tokenToAvailableAfterMaintenance")).items()
        },
        "usdc": spot_balance(state, USDC_TOKEN_INDEX),
        "ubtc": spot_balance(state, UBTC_TOKEN_INDEX),
    }


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
    ubtc_total = spot["ubtc"]["total"]
    btc_szi = perp["btc_position"]["szi"]
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
            "has_other_perp_positions": bool(perp["other_positions"]),
        },
    }


def available_usdc(snapshot: dict[str, Any]) -> float | None:
    return as_float(
        snapshot.get("spot", {})
        .get("tokenToAvailableAfterMaintenance", {})
        .get(str(USDC_TOKEN_INDEX))
    )


def stage_clean(snapshot: dict[str, Any]) -> bool:
    return not snapshot.get("derived", {}).get("has_other_perp_positions", False)


def compare_snapshots(
    cash: dict[str, Any],
    spot: dict[str, Any],
    matched: dict[str, Any],
    closed: dict[str, Any],
) -> dict[str, Any]:
    fingerprints = {snapshot.get("account_fingerprint") for snapshot in (cash, spot, matched, closed)}
    same_account = len(fingerprints) == 1 and None not in fingerprints

    spot_notional = as_float(spot.get("derived", {}).get("ubtc_spot_notional")) or 0.0
    matched_spot_notional = as_float(matched.get("derived", {}).get("ubtc_spot_notional")) or 0.0
    short_notional = as_float(matched.get("derived", {}).get("btc_short_notional")) or 0.0
    mismatch = as_float(matched.get("derived", {}).get("match_mismatch_fraction"))
    pm_ratio = as_float(matched.get("spot", {}).get("portfolioMarginRatio"))

    available_spot = available_usdc(spot)
    available_matched = available_usdc(matched)
    incremental_maintenance = None
    incremental_fraction = None
    if available_spot is not None and available_matched is not None and short_notional > 0:
        incremental_maintenance = max(0.0, available_spot - available_matched)
        incremental_fraction = incremental_maintenance / short_notional

    closed_ubtc_notional = as_float(closed.get("derived", {}).get("ubtc_spot_notional"))
    closed_btc_szi = as_float(closed.get("perp", {}).get("btc_position", {}).get("szi")) or 0.0

    checks = {
        "same_account": same_account,
        "portfolio_margin_mode": matched.get("user_abstraction") == "portfolioMargin",
        "portfolio_margin_enabled": bool(matched.get("spot", {}).get("portfolioMarginEnabled")),
        "dedicated_account_no_other_perps": all(stage_clean(snapshot) for snapshot in (cash, spot, matched, closed)),
        "cash_stage_has_no_btc_short": not bool(cash.get("derived", {}).get("has_btc_short")),
        "spot_stage_has_ubtc": bool(spot.get("derived", {}).get("has_ubtc_spot")),
        "spot_stage_has_no_btc_short": not bool(spot.get("derived", {}).get("has_btc_short")),
        "probe_notional_within_cap": 0 < spot_notional <= MAX_PROBE_NOTIONAL_USD * 1.05,
        "matched_stage_has_ubtc": bool(matched.get("derived", {}).get("has_ubtc_spot")),
        "matched_stage_has_btc_short": bool(matched.get("derived", {}).get("has_btc_short")),
        "matched_base_notional_within_2pct": mismatch is not None and mismatch <= MATCH_TOLERANCE,
        "portfolio_margin_ratio_below_0_50": pm_ratio is not None and pm_ratio < MAX_PORTFOLIO_MARGIN_RATIO,
        "incremental_maintenance_measurement_available": incremental_fraction is not None,
        "incremental_maintenance_below_25pct_of_short_notional": (
            incremental_fraction is not None
            and incremental_fraction <= MAX_INCREMENTAL_MAINTENANCE_FRACTION
        ),
        "closed_stage_flat_btc": abs(closed_btc_szi) <= 1e-12,
        "closed_stage_ubtc_residual_below_1_usd": (
            closed_ubtc_notional is not None
            and abs(closed_ubtc_notional) <= MAX_CLOSED_UBTC_RESIDUAL_USD
        ),
    }
    passed = all(checks.values())

    return {
        "audit_id": AUDIT_ID,
        "status": (
            "PASS_PM_ACCOUNT_BEHAVIOR"
            if passed
            else "FAIL_OR_INCONCLUSIVE_PM_ACCOUNT_BEHAVIOR"
        ),
        "account_fingerprint": cash.get("account_fingerprint") if same_account else None,
        "frozen_limits": {
            "max_probe_notional_usd": MAX_PROBE_NOTIONAL_USD,
            "match_tolerance_fraction": MATCH_TOLERANCE,
            "max_portfolio_margin_ratio": MAX_PORTFOLIO_MARGIN_RATIO,
            "max_incremental_maintenance_fraction": MAX_INCREMENTAL_MAINTENANCE_FRACTION,
            "max_closed_ubtc_residual_notional_usd": MAX_CLOSED_UBTC_RESIDUAL_USD,
        },
        "measurements": {
            "spot_stage_ubtc_notional": spot_notional,
            "matched_stage_ubtc_notional": matched_spot_notional,
            "matched_stage_btc_short_notional": short_notional,
            "matched_stage_mismatch_fraction": mismatch,
            "matched_stage_portfolio_margin_ratio": pm_ratio,
            "spot_stage_available_after_maintenance_usdc": available_spot,
            "matched_stage_available_after_maintenance_usdc": available_matched,
            "incremental_maintenance_consumption_usdc": incremental_maintenance,
            "incremental_maintenance_fraction_of_short_notional": incremental_fraction,
            "closed_stage_ubtc_notional": closed_ubtc_notional,
            "matched_stage_borrow_value": as_float(
                matched.get("borrow_lend", {}).get("total_borrow_value")
            ),
            "matched_stage_health": matched.get("borrow_lend", {}).get("health"),
            "matched_stage_health_factor": as_float(
                matched.get("borrow_lend", {}).get("healthFactor")
            ),
        },
        "checks": checks,
        "decision": (
            "PASS authorizes only a separately preregistered PM-aware BRRK+carry stack accounting experiment using the observed capital factor; it does not authorize production, leverage search, size optimization, or changes to CARRY-PNL-0031."
            if passed
            else "Do not run a PM-aware stack experiment. Diagnose only data/implementation gaps; do not tune probe thresholds on this account outcome."
        ),
    }


def load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CARRY-PM-0035 read-only account-state probe"
    )
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
