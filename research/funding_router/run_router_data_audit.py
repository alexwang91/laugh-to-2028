from __future__ import annotations

import json
import math
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "router_data_0004_outputs"
INFO_URL = "https://api.hyperliquid.xyz/info"
AUDIT_ID = "ROUTER-DATA-0004-SPOT-AVAILABILITY"
TARGETS = ("BTC", "ETH", "SOL", "BNB", "XRP")
ALIASES = {
    "BTC": ("BTC", "UBTC", "WBTC"),
    "ETH": ("ETH", "UETH", "WETH"),
    "SOL": ("SOL", "USOL", "WSOL"),
    "BNB": ("BNB", "UBNB", "WBNB"),
    "XRP": ("XRP", "UXRP", "WXRP"),
}
NOTIONALS = (1_000.0, 10_000.0, 50_000.0, 100_000.0)
BASE_FEES = {
    "spot": {"taker": 0.00070, "maker": 0.00040},
    "perp": {"taker": 0.00045, "maker": 0.00015},
}
CLASS_PRIORITY = {
    "verified_exact": 0,
    "verified_official_ui_remap": 1,
    "candidate_canonical": 2,
    "candidate_wrapped_or_bridged": 3,
    "no_direct_spot_candidate": 9,
}


def post_info(body: dict[str, Any], attempts: int = 7) -> Any:
    last_error = None
    for attempt in range(attempts):
        try:
            response = requests.post(INFO_URL, json=body, timeout=45)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else min(90.0, 5.0 * (2 ** attempt))
                last_error = f"HTTP 429: {response.text[:200]}"
                time.sleep(wait)
                continue
            if response.status_code >= 500:
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                time.sleep(min(45.0, 2.0 * (2 ** attempt)))
                continue
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            last_error = repr(exc)
            time.sleep(min(45.0, 2.0 * (2 ** attempt)))
    raise RuntimeError(f"Hyperliquid info request failed for {body}: {last_error}")


def as_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def safe_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): safe_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [safe_json(item) for item in value]
    if isinstance(value, tuple):
        return [safe_json(item) for item in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def split_meta_and_contexts(payload: Any, label: str) -> tuple[dict, list]:
    if not isinstance(payload, list) or len(payload) != 2:
        raise RuntimeError(f"Unexpected {label} response shape: {type(payload)} {payload}")
    meta, contexts = payload
    if not isinstance(meta, dict) or not isinstance(contexts, list):
        raise RuntimeError(f"Unexpected {label} components")
    return meta, contexts


def standalone_match(text: str | None, target: str) -> bool:
    if not text:
        return False
    return bool(re.search(rf"(?<![A-Z0-9]){re.escape(target)}(?![A-Z0-9])", text.upper()))


def spot_api_coin(pair: dict) -> str:
    name = str(pair.get("name", ""))
    if name == "PURR/USDC":
        return name
    return f"@{int(pair['index'])}"


def classify_candidate(target: str, token: dict, pair: dict) -> tuple[str, str]:
    name = str(token.get("name", ""))
    canonical = bool(token.get("isCanonical")) and bool(pair.get("isCanonical"))
    bridged = token.get("evmContract") not in (None, "", "0x0000000000000000000000000000000000000000")
    if name == target and canonical and not bridged:
        return "verified_exact", "Exact target ticker with canonical token and canonical direct-USDC pair."
    if target == "BTC" and name == "UBTC":
        return (
            "verified_official_ui_remap",
            "Official Hyperliquid API documentation states UI BTC/USDC maps to UBTC/USDC on mainnet HyperCore.",
        )
    if not canonical or bridged:
        return (
            "candidate_wrapped_or_bridged",
            "Candidate name/fullName match, but token/pair is noncanonical or has an EVM contract; economic equivalence is not auto-approved.",
        )
    return (
        "candidate_canonical",
        "Canonical direct-USDC candidate, but economic identity is not established by exact ticker or the preregistered official BTC remap.",
    )


def candidate_matches(target: str, token: dict) -> bool:
    name = str(token.get("name", "")).upper()
    full_name = str(token.get("fullName") or "")
    return name in ALIASES[target] or standalone_match(name, target) or standalone_match(full_name, target)


def normalize_levels(book: dict, side_index: int) -> list[dict]:
    levels = book.get("levels") if isinstance(book, dict) else None
    if not isinstance(levels, list) or len(levels) != 2:
        return []
    side = levels[side_index]
    normalized = []
    for level in side if isinstance(side, list) else []:
        if not isinstance(level, dict):
            continue
        px = as_float(level.get("px"))
        sz = as_float(level.get("sz"))
        if px is None or sz is None or px <= 0 or sz <= 0:
            continue
        normalized.append({
            "px": px,
            "sz": sz,
            "n": level.get("n"),
            "quote_notional": px * sz,
        })
    return normalized


def book_summary(book: dict) -> dict:
    bids = normalize_levels(book, 0)
    asks = normalize_levels(book, 1)
    best_bid = max((row["px"] for row in bids), default=None)
    best_ask = min((row["px"] for row in asks), default=None)
    mid = (best_bid + best_ask) / 2.0 if best_bid and best_ask else None
    spread_bps = ((best_ask - best_bid) / mid * 10_000.0) if mid else None
    return {
        "coin": book.get("coin") if isinstance(book, dict) else None,
        "time": book.get("time") if isinstance(book, dict) else None,
        "bid_levels": len(bids),
        "ask_levels": len(asks),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid": mid,
        "spread_bps": spread_bps,
        "returned_bid_notional": float(sum(row["quote_notional"] for row in bids)),
        "returned_ask_notional": float(sum(row["quote_notional"] for row in asks)),
    }


def marketable_vwap(book: dict, side: str, target_notional: float) -> dict:
    if side not in ("buy", "sell"):
        raise ValueError(f"Invalid side {side}")
    summary = book_summary(book)
    levels = normalize_levels(book, 1 if side == "buy" else 0)
    levels = sorted(levels, key=lambda row: row["px"], reverse=(side == "sell"))
    remaining = float(target_notional)
    quote_filled = 0.0
    base_filled = 0.0
    used = 0
    for level in levels:
        if remaining <= 1e-12:
            break
        quote_available = level["quote_notional"]
        quote_take = min(remaining, quote_available)
        base_take = quote_take / level["px"]
        quote_filled += quote_take
        base_filled += base_take
        remaining -= quote_take
        used += 1
    vwap = quote_filled / base_filled if base_filled > 0 else None
    mid = summary["mid"]
    if vwap is None or mid is None:
        slippage_bps = None
    elif side == "buy":
        slippage_bps = (vwap / mid - 1.0) * 10_000.0
    else:
        slippage_bps = (1.0 - vwap / mid) * 10_000.0
    return {
        "side": side,
        "target_notional": float(target_notional),
        "filled_notional": float(quote_filled),
        "unfilled_notional": float(max(0.0, target_notional - quote_filled)),
        "fill_fraction": float(quote_filled / target_notional) if target_notional > 0 else None,
        "base_filled": float(base_filled),
        "vwap": vwap,
        "reference_mid": mid,
        "slippage_bps": slippage_bps,
        "levels_used": used,
        "fully_fillable_in_returned_book": bool(remaining <= 1e-8),
    }


def fee_rows(market_type: str) -> list[dict]:
    rows = []
    for notional in NOTIONALS:
        for role in ("taker", "maker"):
            rate = BASE_FEES[market_type][role]
            rows.append({
                "market_type": market_type,
                "role": role,
                "notional": notional,
                "rate": rate,
                "fee_amount": notional * rate,
            })
    return rows


def select_context(contexts: list, index: int) -> dict:
    if 0 <= index < len(contexts) and isinstance(contexts[index], dict):
        return contexts[index]
    return {}


def discover_candidates(spot_meta: dict, spot_contexts: list) -> tuple[dict[str, list[dict]], dict[int, dict], dict[int, dict]]:
    tokens = spot_meta.get("tokens", [])
    universe = spot_meta.get("universe", [])
    token_by_index = {int(token["index"]): token for token in tokens if isinstance(token, dict) and "index" in token}
    usdc_indices = [index for index, token in token_by_index.items() if str(token.get("name")) == "USDC"]
    if not usdc_indices:
        raise RuntimeError("USDC token not found in spot metadata")
    usdc_index = usdc_indices[0]
    pair_by_index = {int(pair["index"]): pair for pair in universe if isinstance(pair, dict) and "index" in pair}
    candidates: dict[str, list[dict]] = {target: [] for target in TARGETS}

    for pair_index, pair in pair_by_index.items():
        pair_tokens = pair.get("tokens")
        if not isinstance(pair_tokens, list) or len(pair_tokens) != 2:
            continue
        base_index, quote_index = map(int, pair_tokens)
        if quote_index != usdc_index or base_index not in token_by_index:
            continue
        token = token_by_index[base_index]
        for target in TARGETS:
            if not candidate_matches(target, token):
                continue
            classification, reason = classify_candidate(target, token, pair)
            candidates[target].append({
                "target": target,
                "classification": classification,
                "classification_reason": reason,
                "pair_index": pair_index,
                "spot_order_asset_id": 10_000 + pair_index,
                "pair_name": pair.get("name"),
                "api_coin": spot_api_coin(pair),
                "pair_is_canonical": pair.get("isCanonical"),
                "base_token_index": base_index,
                "quote_token_index": quote_index,
                "base_token": token,
                "quote_token": token_by_index[quote_index],
                "asset_context": select_context(spot_contexts, pair_index),
            })
    for target in TARGETS:
        candidates[target].sort(
            key=lambda row: (
                CLASS_PRIORITY[row["classification"]],
                -float(as_float(row["asset_context"].get("dayNtlVlm")) or 0.0),
                row["pair_index"],
            )
        )
    return candidates, token_by_index, pair_by_index


def perp_inventory(perp_meta: dict, perp_contexts: list) -> dict[str, dict | None]:
    universe = perp_meta.get("universe", [])
    result: dict[str, dict | None] = {}
    for target in TARGETS:
        matches = []
        for index, item in enumerate(universe):
            if not isinstance(item, dict) or str(item.get("name")) != target:
                continue
            matches.append({
                "target": target,
                "perp_universe_index": index,
                "perp_order_asset_id": index,
                "api_coin": target,
                "metadata": item,
                "asset_context": select_context(perp_contexts, index),
            })
        result[target] = matches[0] if matches else None
    return result


def context_fields(context: dict) -> dict:
    wanted = (
        "midPx", "markPx", "oraclePx", "funding", "openInterest", "dayNtlVlm",
        "prevDayPx", "premium", "impactPxs", "circulatingSupply",
    )
    return {field: context.get(field) for field in wanted if field in context}


def basis_metrics(spot_mid: float | None, perp_context: dict, perp_book_mid: float | None) -> dict:
    mark = as_float(perp_context.get("markPx"))
    oracle = as_float(perp_context.get("oraclePx"))
    mid_context = as_float(perp_context.get("midPx"))
    perp_mid = perp_book_mid if perp_book_mid is not None else mid_context
    def bps(value):
        return (value / spot_mid - 1.0) * 10_000.0 if value is not None and spot_mid else None
    return {
        "spot_mid": spot_mid,
        "perp_book_or_context_mid": perp_mid,
        "perp_mark": mark,
        "perp_oracle": oracle,
        "perp_mid_vs_spot_bps": bps(perp_mid),
        "perp_mark_vs_spot_bps": bps(mark),
        "perp_oracle_vs_spot_bps": bps(oracle),
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    observed_at = datetime.now(timezone.utc).isoformat()

    raw_spot = post_info({"type": "spotMetaAndAssetCtxs"})
    raw_perp = post_info({"type": "metaAndAssetCtxs"})
    raw_mids = post_info({"type": "allMids"})
    spot_meta, spot_contexts = split_meta_and_contexts(raw_spot, "spotMetaAndAssetCtxs")
    perp_meta, perp_contexts = split_meta_and_contexts(raw_perp, "metaAndAssetCtxs")
    if not isinstance(raw_mids, dict):
        raise RuntimeError("allMids did not return a dictionary")

    candidates, token_by_index, pair_by_index = discover_candidates(spot_meta, spot_contexts)
    perps = perp_inventory(perp_meta, perp_contexts)

    token_details: dict[str, Any] = {}
    raw_books: dict[str, Any] = {}
    book_rows = []
    market_rows = []
    target_summary = {}

    for target in TARGETS:
        perp = perps[target]
        perp_book = None
        if perp is not None:
            perp_book = post_info({"type": "l2Book", "coin": perp["api_coin"]})
            raw_books[f"perp:{target}"] = perp_book
            perp_summary = book_summary(perp_book)
            for side in ("buy", "sell"):
                for notional in NOTIONALS:
                    row = marketable_vwap(perp_book, side, notional)
                    row.update({"target": target, "market_type": "perp", "api_coin": perp["api_coin"]})
                    book_rows.append(row)
            market_rows.append({
                "target": target,
                "market_type": "perp",
                "classification": "target_perp" if perp else "absent",
                "api_coin": perp["api_coin"],
                "pair_name": target,
                "order_asset_id": perp["perp_order_asset_id"],
                "universe_index": perp["perp_universe_index"],
                "szDecimals": perp["metadata"].get("szDecimals"),
                "maxLeverage": perp["metadata"].get("maxLeverage"),
                "isDelisted": perp["metadata"].get("isDelisted"),
                "onlyIsolated": perp["metadata"].get("onlyIsolated"),
                **perp_summary,
                **{f"ctx_{key}": value for key, value in context_fields(perp["asset_context"]).items()},
            })

        candidate_summaries = []
        for candidate in candidates[target]:
            token = candidate["base_token"]
            token_id = str(token.get("tokenId"))
            if token_id not in token_details:
                try:
                    token_details[token_id] = post_info({"type": "tokenDetails", "tokenId": token_id})
                except Exception as exc:
                    token_details[token_id] = {"error": repr(exc)}
            spot_book = post_info({"type": "l2Book", "coin": candidate["api_coin"]})
            raw_books[f"spot:{target}:{candidate['api_coin']}"] = spot_book
            spot_summary = book_summary(spot_book)
            for side in ("buy", "sell"):
                for notional in NOTIONALS:
                    row = marketable_vwap(spot_book, side, notional)
                    row.update({
                        "target": target,
                        "market_type": "spot",
                        "api_coin": candidate["api_coin"],
                        "classification": candidate["classification"],
                    })
                    book_rows.append(row)
            token_record = candidate["base_token"]
            market_rows.append({
                "target": target,
                "market_type": "spot",
                "classification": candidate["classification"],
                "classification_reason": candidate["classification_reason"],
                "api_coin": candidate["api_coin"],
                "pair_name": candidate["pair_name"],
                "order_asset_id": candidate["spot_order_asset_id"],
                "universe_index": candidate["pair_index"],
                "base_token_index": candidate["base_token_index"],
                "base_token_name": token_record.get("name"),
                "base_token_fullName": token_record.get("fullName"),
                "base_token_tokenId": token_record.get("tokenId"),
                "base_token_isCanonical": token_record.get("isCanonical"),
                "pair_isCanonical": candidate.get("pair_is_canonical"),
                "base_token_evmContract": token_record.get("evmContract"),
                "szDecimals": token_record.get("szDecimals"),
                "weiDecimals": token_record.get("weiDecimals"),
                **spot_summary,
                **{f"ctx_{key}": value for key, value in context_fields(candidate["asset_context"]).items()},
            })
            candidate_summaries.append({
                **{key: value for key, value in candidate.items() if key not in ("base_token", "quote_token", "asset_context")},
                "base_token": candidate["base_token"],
                "quote_token": candidate["quote_token"],
                "asset_context": context_fields(candidate["asset_context"]),
                "token_details": token_details[token_id],
                "book": spot_summary,
                "basis": basis_metrics(
                    spot_summary["mid"],
                    perp["asset_context"] if perp else {},
                    book_summary(perp_book)["mid"] if perp_book else None,
                ),
            })

        if candidate_summaries:
            primary = candidate_summaries[0]
            classification = primary["classification"]
            reason = primary["classification_reason"]
        else:
            primary = None
            classification = "no_direct_spot_candidate"
            reason = "No deterministic direct-USDC spot candidate discovered in current spot metadata."
        target_summary[target] = {
            "perp_present": perp is not None,
            "perp": safe_json(perp),
            "spot_candidate_count": len(candidate_summaries),
            "primary_spot_classification": classification,
            "primary_spot_reason": reason,
            "primary_spot_candidate": safe_json(primary),
            "all_spot_candidates": safe_json(candidate_summaries),
        }

    fee_frame = pd.DataFrame(fee_rows("spot") + fee_rows("perp"))
    book_frame = pd.DataFrame(book_rows)
    market_frame = pd.DataFrame(market_rows)

    fill_summary = {}
    for target in TARGETS:
        fill_summary[target] = {}
        for market_type in ("spot", "perp"):
            subset = book_frame[(book_frame["target"] == target) & (book_frame["market_type"] == market_type)]
            if subset.empty:
                fill_summary[target][market_type] = {"available": False}
                continue
            fill_summary[target][market_type] = {
                "available": True,
                "all_100k_sides_fillable": bool(
                    subset[subset["target_notional"] == 100_000.0]["fully_fillable_in_returned_book"].all()
                ),
                "maximum_buy_slippage_bps": as_float(subset[subset["side"] == "buy"]["slippage_bps"].max()),
                "maximum_sell_slippage_bps": as_float(subset[subset["side"] == "sell"]["slippage_bps"].max()),
            }

    report = {
        "audit_id": AUDIT_ID,
        "trading_changes": False,
        "strategy_pnl": False,
        "observed_at_utc": observed_at,
        "official_endpoint": INFO_URL,
        "fixed_notional_usd": list(NOTIONALS),
        "fees": {
            "source_role": "public base-tier current fee diagnostic",
            "spot": BASE_FEES["spot"],
            "perp": BASE_FEES["perp"],
        },
        "metadata_counts": {
            "spot_tokens": len(spot_meta.get("tokens", [])),
            "spot_pairs": len(spot_meta.get("universe", [])),
            "spot_contexts": len(spot_contexts),
            "perp_assets": len(perp_meta.get("universe", [])),
            "perp_contexts": len(perp_contexts),
            "all_mids_entries": len(raw_mids),
        },
        "targets": safe_json(target_summary),
        "fill_summary": safe_json(fill_summary),
        "decision_rule": "This is a single current data/execution snapshot. Only exact or officially documented remaps are verified spot candidates. A later shadow router may use only explicit classifications and must retain unavailable/unverified assets as perp-only or unavailable without inventing an external fallback.",
    }

    market_frame.to_csv(OUTPUT / "market_inventory.csv", index=False)
    book_frame.to_csv(OUTPUT / "vwap_slippage.csv", index=False, float_format="%.12f")
    fee_frame.to_csv(OUTPUT / "base_fee_scenarios.csv", index=False, float_format="%.12f")
    (OUTPUT / "router_data_0004_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    (OUTPUT / "raw_spot_meta_and_contexts.json").write_text(json.dumps(safe_json(raw_spot), indent=2), encoding="utf-8")
    (OUTPUT / "raw_perp_meta_and_contexts.json").write_text(json.dumps(safe_json(raw_perp), indent=2), encoding="utf-8")
    (OUTPUT / "raw_all_mids.json").write_text(json.dumps(safe_json(raw_mids), indent=2), encoding="utf-8")
    (OUTPUT / "raw_token_details.json").write_text(json.dumps(safe_json(token_details), indent=2), encoding="utf-8")
    (OUTPUT / "raw_l2_books.json").write_text(json.dumps(safe_json(raw_books), indent=2), encoding="utf-8")

    print("=== ROUTER_DATA_0004_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
