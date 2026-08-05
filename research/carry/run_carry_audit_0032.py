from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
RESULTS = RESEARCH / "results"
for path in (HERE, RESEARCH):
    sys.path.insert(0, str(path))

from run_carry_data_0030 import SPOT_ROOT, PERP_ROOT, download_key, parse_kline_payload
from run_carry_pnl_0031 import (
    WEIGHT,
    daily_key,
    load_monthly_kline_history,
    repair_internal_daily_gaps,
)

AUDIT_ID = "CARRY-AUDIT-0032-BASIS-OUTLIERS"
ASSETS = ("SOLUSDT", "XRPUSDT")
START = pd.Timestamp("2020-09-15")
END = pd.Timestamp("2026-07-30")
TOP_N = 20
ABS_FLAG = 0.02
TOL = 1e-10
OUTPUT = RESULTS / "carry_audit_0032"


def exact_daily_close(root: str, symbol: str, date: pd.Timestamp) -> dict[str, Any]:
    key = daily_key(root, symbol, date)
    try:
        frame = parse_kline_payload(download_key(key))
        exact = frame.loc[frame.index == pd.Timestamp(date)]
        if len(exact) != 1:
            return {"available": False, "key": key, "error": f"requested date rows={len(exact)}"}
        return {
            "available": True,
            "key": key,
            "date": str(pd.Timestamp(exact.index[0]).date()),
            "close": float(exact.iloc[0]["close"]),
        }
    except Exception as exc:
        return {"available": False, "key": key, "error": repr(exc)}


def relative_error(a: float, b: float) -> float:
    scale = max(abs(float(a)), abs(float(b)), 1e-12)
    return float(abs(float(a) - float(b)) / scale)


def ranked_dates(basis: pd.Series, n: int = TOP_N) -> list[pd.Timestamp]:
    clean = basis.dropna().abs().sort_values(ascending=False)
    return [pd.Timestamp(x) for x in clean.head(n).index]


def audit_asset(symbol: str) -> tuple[dict[str, Any], pd.DataFrame]:
    monthly_spot = load_monthly_kline_history(SPOT_ROOT, symbol, "spot")
    monthly_perp = load_monthly_kline_history(PERP_ROOT, symbol, "perp")
    spot, spot_repair = repair_internal_daily_gaps(SPOT_ROOT, symbol, monthly_spot)
    perp, perp_repair = repair_internal_daily_gaps(PERP_ROOT, symbol, monthly_perp)

    index = pd.date_range(START, END, freq="D")
    missing_spot = index.difference(spot.index)
    missing_perp = index.difference(perp.index)
    if len(missing_spot) or len(missing_perp):
        raise RuntimeError(
            f"{symbol}: unresolved 0031-window leg dates spot={list(missing_spot[:10])} perp={list(missing_perp[:10])}"
        )

    s = spot.reindex(index)["close"].astype(float)
    p = perp.reindex(index)["close"].astype(float)
    basis = p / s - 1.0
    spot_ret = s.pct_change(fill_method=None)
    perp_ret = p.pct_change(fill_method=None)
    price_contribution = WEIGHT * spot_ret - WEIGHT * perp_ret
    basis_change = basis.diff()

    selected = ranked_dates(basis)
    flagged = [pd.Timestamp(x) for x in basis.index[basis.abs() >= ABS_FLAG]]
    dates_to_check = sorted(set(selected + [d - pd.Timedelta(days=1) for d in selected if d > index.min()]))

    repair_spot_dates = set(spot_repair.get("repaired_dates", []))
    repair_perp_dates = set(perp_repair.get("repaired_dates", []))
    crosschecks: dict[tuple[str, pd.Timestamp], dict[str, Any]] = {}
    mismatches: list[dict[str, Any]] = []
    unavailable: list[dict[str, Any]] = []

    for date in dates_to_check:
        if date < index.min() or date > index.max():
            continue
        for leg, root, monthly, repaired, repaired_dates in (
            ("spot", SPOT_ROOT, monthly_spot, spot, repair_spot_dates),
            ("perp", PERP_ROOT, monthly_perp, perp, repair_perp_dates),
        ):
            daily = exact_daily_close(root, symbol, date)
            date_text = str(date.date())
            monthly_present = date in monthly.index
            value_used = float(repaired.at[date, "close"])
            row = {
                "symbol": symbol,
                "date": date_text,
                "leg": leg,
                "monthly_present": bool(monthly_present),
                "value_used_by_0031": value_used,
                "source_used_by_0031": "official_daily_fallback" if date_text in repaired_dates else "official_monthly",
                "daily_available": bool(daily.get("available")),
                "daily_key": daily.get("key"),
                "daily_close": daily.get("close"),
            }
            if monthly_present:
                monthly_close = float(monthly.at[date, "close"])
                row["monthly_close"] = monthly_close
                if daily.get("available"):
                    err = relative_error(monthly_close, float(daily["close"]))
                    row["monthly_vs_daily_relative_error"] = err
                    if err > TOL:
                        mismatches.append(dict(row))
            elif daily.get("available"):
                err = relative_error(value_used, float(daily["close"]))
                row["fallback_value_vs_daily_relative_error"] = err
                if err > TOL:
                    mismatches.append(dict(row))
            if not daily.get("available"):
                unavailable.append(dict(row))
            crosschecks[(leg, date)] = row

    rows: list[dict[str, Any]] = []
    for rank, date in enumerate(selected, start=1):
        prev_date = date - pd.Timedelta(days=1)
        next_date = date + pd.Timedelta(days=1)
        rows.append({
            "symbol": symbol,
            "rank_abs_basis": rank,
            "date": str(date.date()),
            "spot_close": float(s.loc[date]),
            "perp_close": float(p.loc[date]),
            "basis": float(basis.loc[date]),
            "abs_basis": float(abs(basis.loc[date])),
            "basis_prior_day": float(basis.loc[prev_date]) if prev_date in basis.index else None,
            "basis_next_day": float(basis.loc[next_date]) if next_date in basis.index else None,
            "basis_change": float(basis_change.loc[date]) if pd.notna(basis_change.loc[date]) else None,
            "spot_return": float(spot_ret.loc[date]) if pd.notna(spot_ret.loc[date]) else None,
            "perp_return": float(perp_ret.loc[date]) if pd.notna(perp_ret.loc[date]) else None,
            "frozen_0031_asset_price_spread_contribution": float(price_contribution.loc[date]) if pd.notna(price_contribution.loc[date]) else None,
            "spot_monthly_vs_daily_relative_error": crosschecks.get(("spot", date), {}).get("monthly_vs_daily_relative_error", crosschecks.get(("spot", date), {}).get("fallback_value_vs_daily_relative_error")),
            "perp_monthly_vs_daily_relative_error": crosschecks.get(("perp", date), {}).get("monthly_vs_daily_relative_error", crosschecks.get(("perp", date), {}).get("fallback_value_vs_daily_relative_error")),
            "spot_source_used_by_0031": crosschecks.get(("spot", date), {}).get("source_used_by_0031"),
            "perp_source_used_by_0031": crosschecks.get(("perp", date), {}).get("source_used_by_0031"),
        })
    ranked = pd.DataFrame(rows)

    total_price = float(price_contribution.loc[START:END].dropna().sum())
    selected_price = float(price_contribution.reindex(selected).dropna().sum())
    flagged_price = float(price_contribution.reindex(flagged).dropna().sum()) if flagged else 0.0
    report = {
        "symbol": symbol,
        "window": [str(START.date()), str(END.date())],
        "largest_abs_basis": float(basis.abs().max()),
        "largest_basis_date": str(basis.abs().idxmax().date()),
        "largest_basis_signed": float(basis.loc[basis.abs().idxmax()]),
        "dates_abs_basis_ge_2pct_count": int(len(flagged)),
        "dates_abs_basis_ge_2pct": [str(d.date()) for d in flagged],
        "monthly_gap_repair": {"spot": spot_repair, "perp": perp_repair},
        "daily_crosscheck_dates": int(len(dates_to_check)),
        "daily_crosscheck_unavailable_count": int(len(unavailable)),
        "daily_crosscheck_unavailable": unavailable[:100],
        "source_mismatch_count": int(len(mismatches)),
        "source_mismatches": mismatches[:100],
        "price_spread_attribution": {
            "full_window_cumulative_additive": total_price,
            "top20_abs_basis_dates_cumulative_additive": selected_price,
            "top20_share_of_full_signed": float(selected_price / total_price) if abs(total_price) > 1e-12 else None,
            "abs_basis_ge_2pct_dates_cumulative_additive": flagged_price,
            "abs_basis_ge_2pct_share_of_full_signed": float(flagged_price / total_price) if abs(total_price) > 1e-12 else None,
        },
        "pass": bool(len(mismatches) == 0),
    }
    return report, ranked


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    reports = []
    tables = []
    for symbol in ASSETS:
        report, ranked = audit_asset(symbol)
        reports.append(report)
        tables.append(ranked)
        print(f"resolved {symbol} pass={report['pass']} largest={report['largest_basis_signed']:.6f} date={report['largest_basis_date']}", flush=True)
    ranked_all = pd.concat(tables, ignore_index=True)
    ranked_all.to_csv(OUTPUT / "ranked_basis_outliers.csv", index=False)
    overall_pass = bool(all(row["pass"] for row in reports))
    summary = {
        "audit_id": AUDIT_ID,
        "status": "PASS" if overall_pass else "FAIL",
        "trading_changes": False,
        "recomputed_filtered_strategy": False,
        "assets": reports,
        "pass_rule": {
            "relative_tolerance": TOL,
            "all_compared_source_rows_consistent": overall_pass,
            "decision": "PASS authorizes proceeding to a separately preregistered BRRK+carry stack test; FAIL blocks stacking pending source resolution",
        },
        "interpretation": "Post-hoc data/source attribution only. The frozen CARRY-PNL-0031 result is not altered by this audit and no outlier is removed or winsorized."
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("=== CARRY_AUDIT_0032_REPORT ===")
    print(json.dumps(summary, indent=2))
    print("=== END ===")
    if not overall_pass:
        raise RuntimeError("CARRY-AUDIT-0032 failed source consistency")


if __name__ == "__main__":
    main()
