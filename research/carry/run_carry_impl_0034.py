from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
ROUTER = RESEARCH / "funding_router"
for path in (RESEARCH, ROUTER, HERE):
    sys.path.insert(0, str(path))

from run_router_data_audit import (
    NOTIONALS,
    TARGETS,
    as_float,
    book_summary,
    context_fields,
    discover_candidates,
    marketable_vwap,
    perp_inventory,
    post_info,
    safe_json,
    split_meta_and_contexts,
)

AUDIT_ID = "CARRY-IMPL-0034-HYPERLIQUID-PORTFOLIO-MARGIN"
OUTPUT = RESEARCH / "results" / "carry_impl_0034"
INFO_URL = "https://api.hyperliquid.xyz/info"
VERIFIED_SPOT_CLASSES = {"verified_exact", "verified_official_ui_remap"}


def reserve_rows(payload: Any, token_by_index: dict[int, dict]) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    if not isinstance(payload, list):
        raise RuntimeError(f"allBorrowLendReserveStates unexpected shape: {type(payload)}")
    rows: list[dict[str, Any]] = []
    by_token: dict[int, dict[str, Any]] = {}
    for item in payload:
        if not isinstance(item, list) or len(item) != 2:
            raise RuntimeError(f"unexpected reserve row: {item!r}")
        token_index = int(item[0])
        state = item[1]
        if not isinstance(state, dict):
            raise RuntimeError(f"reserve state not dict for token {token_index}")
        token = token_by_index.get(token_index, {})
        row = {
            "token_index": token_index,
            "token_name": token.get("name"),
            "token_fullName": token.get("fullName"),
            "token_isCanonical": token.get("isCanonical"),
            "token_tokenId": token.get("tokenId"),
            "ltv": as_float(state.get("ltv")),
            "oraclePx": as_float(state.get("oraclePx")),
            "totalSupplied": as_float(state.get("totalSupplied")),
            "totalBorrowed": as_float(state.get("totalBorrowed")),
            "balance": as_float(state.get("balance")),
            "utilization": as_float(state.get("utilization")),
            "borrowYearlyRate": as_float(state.get("borrowYearlyRate")),
            "supplyYearlyRate": as_float(state.get("supplyYearlyRate")),
            "raw_state": safe_json(state),
        }
        row["collateral_capable_by_ltv"] = bool(row["ltv"] is not None and row["ltv"] > 0.0)
        row["observable_borrow_liquidity"] = bool(
            row["balance"] is not None and row["balance"] > 0.0
        )
        rows.append(row)
        by_token[token_index] = row
    rows.sort(key=lambda row: row["token_index"])
    return rows, by_token


def reserve_for_candidate(candidate: dict | None, by_token: dict[int, dict[str, Any]]) -> dict[str, Any] | None:
    if candidate is None:
        return None
    token_index = int(candidate["base_token_index"])
    return by_token.get(token_index)


def target_market_snapshot(
    target: str,
    candidates: dict[str, list[dict]],
    perps: dict[str, dict | None],
    reserve_by_token: dict[int, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    candidate = candidates[target][0] if candidates[target] else None
    perp = perps[target]
    rows: list[dict[str, Any]] = []

    spot_book = None
    spot_summary = None
    spot_vwap: list[dict[str, Any]] = []
    if candidate is not None:
        spot_book = post_info({"type": "l2Book", "coin": candidate["api_coin"]})
        spot_summary = book_summary(spot_book)
        for side in ("buy", "sell"):
            for notional in NOTIONALS:
                row = marketable_vwap(spot_book, side, notional)
                row.update({"target": target, "leg": "spot", "api_coin": candidate["api_coin"]})
                spot_vwap.append(row)
                rows.append(row)

    perp_book = None
    perp_summary = None
    perp_vwap: list[dict[str, Any]] = []
    if perp is not None:
        perp_book = post_info({"type": "l2Book", "coin": perp["api_coin"]})
        perp_summary = book_summary(perp_book)
        for side in ("buy", "sell"):
            for notional in NOTIONALS:
                row = marketable_vwap(perp_book, side, notional)
                row.update({"target": target, "leg": "perp", "api_coin": perp["api_coin"]})
                perp_vwap.append(row)
                rows.append(row)

    reserve = reserve_for_candidate(candidate, reserve_by_token)
    classification = candidate["classification"] if candidate is not None else "no_direct_spot_candidate"
    verified_identity = classification in VERIFIED_SPOT_CLASSES
    collateral_capable = bool(reserve and reserve.get("collateral_capable_by_ltv"))
    spot_book_live = bool(spot_summary and spot_summary.get("bid_levels", 0) > 0 and spot_summary.get("ask_levels", 0) > 0)
    perp_book_live = bool(perp_summary and perp_summary.get("bid_levels", 0) > 0 and perp_summary.get("ask_levels", 0) > 0)

    perp_ctx = perp["asset_context"] if perp else {}
    current_funding = as_float(perp_ctx.get("funding"))
    simple_annualized_funding = current_funding * 24.0 * 365.0 if current_funding is not None else None
    spot_mid = spot_summary.get("mid") if spot_summary else None
    perp_mid = perp_summary.get("mid") if perp_summary else None
    mid_basis_bps = ((perp_mid / spot_mid - 1.0) * 10_000.0) if spot_mid and perp_mid else None

    target_pass = bool(
        target == "BTC"
        and verified_identity
        and collateral_capable
        and perp is not None
        and spot_book_live
        and perp_book_live
    )
    return {
        "target": target,
        "perp_present": perp is not None,
        "perp_metadata": safe_json(perp.get("metadata") if perp else None),
        "perp_context": safe_json(context_fields(perp_ctx)),
        "current_funding_rate_context": current_funding,
        "simple_current_funding_annualized_diagnostic": simple_annualized_funding,
        "primary_spot_present": candidate is not None,
        "primary_spot_classification": classification,
        "primary_spot_verified_identity": verified_identity,
        "primary_spot": safe_json({
            key: value for key, value in (candidate or {}).items()
            if key not in ("base_token", "quote_token", "asset_context")
        }) if candidate else None,
        "primary_spot_token": safe_json(candidate.get("base_token") if candidate else None),
        "primary_spot_reserve": safe_json(reserve),
        "primary_spot_collateral_capable_by_ltv": collateral_capable,
        "spot_book": safe_json(spot_summary),
        "perp_book": safe_json(perp_summary),
        "spot_perp_mid_basis_bps": mid_basis_bps,
        "btc_public_pm_feasibility_pass": target_pass if target == "BTC" else None,
        "implementation_class": (
            "verified_pm_collateral_spot_plus_perp"
            if verified_identity and collateral_capable and perp is not None
            else "verified_spot_but_not_pm_collateral"
            if verified_identity and not collateral_capable and perp is not None
            else "unverified_or_wrapped_spot_candidate"
            if candidate is not None and perp is not None
            else "perp_only_or_unavailable"
        ),
        "vwap": safe_json(spot_vwap + perp_vwap),
    }, rows


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    observed_at = datetime.now(timezone.utc).isoformat()

    raw_spot = post_info({"type": "spotMetaAndAssetCtxs"})
    raw_perp = post_info({"type": "metaAndAssetCtxs"})
    raw_mids = post_info({"type": "allMids"})
    raw_reserves = post_info({"type": "allBorrowLendReserveStates"})

    spot_meta, spot_contexts = split_meta_and_contexts(raw_spot, "spotMetaAndAssetCtxs")
    perp_meta, perp_contexts = split_meta_and_contexts(raw_perp, "metaAndAssetCtxs")
    if not isinstance(raw_mids, dict):
        raise RuntimeError("allMids did not return dictionary")

    candidates, token_by_index, _ = discover_candidates(spot_meta, spot_contexts)
    perps = perp_inventory(perp_meta, perp_contexts)
    reserves, reserve_by_token = reserve_rows(raw_reserves, token_by_index)

    collateral_reserves = [row for row in reserves if row["collateral_capable_by_ltv"]]
    borrowable_reserves = [row for row in reserves if row["observable_borrow_liquidity"]]
    usdc_reserves = [row for row in reserves if row.get("token_name") == "USDC"]
    usdc_reserve = usdc_reserves[0] if usdc_reserves else None

    targets: dict[str, Any] = {}
    vwap_rows: list[dict[str, Any]] = []
    for target in TARGETS:
        snapshot, rows = target_market_snapshot(target, candidates, perps, reserve_by_token)
        targets[target] = snapshot
        vwap_rows.extend(rows)

    btc = targets["BTC"]
    btc_pass = bool(btc.get("btc_public_pm_feasibility_pass"))
    report = {
        "audit_id": AUDIT_ID,
        "status": "PASS_BTC_PUBLIC_FEASIBILITY" if btc_pass else "FAIL_BTC_PUBLIC_FEASIBILITY",
        "trading_changes": False,
        "strategy_pnl": False,
        "private_account_used": False,
        "observed_at_utc": observed_at,
        "info_endpoint": INFO_URL,
        "runtime_counts": {
            "spot_tokens": len(spot_meta.get("tokens", [])),
            "spot_pairs": len(spot_meta.get("universe", [])),
            "perp_assets": len(perp_meta.get("universe", [])),
            "borrow_lend_reserves": len(reserves),
            "collateral_ltv_positive_reserves": len(collateral_reserves),
            "observable_borrow_liquidity_reserves": len(borrowable_reserves),
        },
        "reserves": safe_json(reserves),
        "collateral_reserves": safe_json(collateral_reserves),
        "borrowable_reserves": safe_json(borrowable_reserves),
        "usdc_reserve": safe_json(usdc_reserve),
        "targets": safe_json(targets),
        "qualification": {
            "btc_verified_spot_identity": bool(btc.get("primary_spot_verified_identity")),
            "btc_selected_spot_ltv_positive": bool(btc.get("primary_spot_collateral_capable_by_ltv")),
            "btc_perp_present": bool(btc.get("perp_present")),
            "btc_spot_book_live": bool((btc.get("spot_book") or {}).get("bid_levels", 0) > 0 and (btc.get("spot_book") or {}).get("ask_levels", 0) > 0),
            "btc_perp_book_live": bool((btc.get("perp_book") or {}).get("bid_levels", 0) > 0 and (btc.get("perp_book") or {}).get("ask_levels", 0) > 0),
            "btc_public_pm_feasibility": btc_pass,
        },
        "external_official_context_not_machine_verified_by_this_run": {
            "portfolio_margin_carry_use_case": "Hyperliquid docs describe spot balance offsetting a short perp with the spot balance serving as collateral.",
            "beta_context": "Hyperliquid 2026 announcements state Portfolio Margin is in beta and BTC/HYPE are supported collateral subject to account/cap requirements.",
            "limit": "Current reserve state verifies LTV/rates/liquidity but does not reveal exact matched-position margin release for this hypothetical account."
        },
        "decision": (
            "BTC PASS authorizes only a separately preregistered no-trade/small-subaccount Portfolio Margin probe that measures actual margin usage and health-factor behavior. "
            "No target whose selected spot token lacks positive-LTV reserve state is promoted to capital-efficient carry by this audit."
        ),
    }

    pd.DataFrame(vwap_rows).to_csv(OUTPUT / "vwap_snapshot.csv", index=False)
    pd.DataFrame([{key: value for key, value in row.items() if key != "raw_state"} for row in reserves]).to_csv(
        OUTPUT / "reserve_snapshot.csv", index=False
    )
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (OUTPUT / "raw_all_borrow_lend_reserves.json").write_text(json.dumps(safe_json(raw_reserves), indent=2), encoding="utf-8")
    (OUTPUT / "raw_spot_meta_and_contexts.json").write_text(json.dumps(safe_json(raw_spot), indent=2), encoding="utf-8")
    (OUTPUT / "raw_perp_meta_and_contexts.json").write_text(json.dumps(safe_json(raw_perp), indent=2), encoding="utf-8")
    (OUTPUT / "raw_all_mids.json").write_text(json.dumps(safe_json(raw_mids), indent=2), encoding="utf-8")

    print("=== CARRY_IMPL_0034_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")
    if not btc_pass:
        raise RuntimeError("BTC public Portfolio Margin feasibility gate failed")


if __name__ == "__main__":
    main()
