from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

EXPERIMENT_ID = "CARRY-RF-0036R2-REVIEW-METRIC-PARITY"
HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
RESULTS = RESEARCH / "results"
R1_DIR = RESULTS / "carry_rf_0036r1"
OUTPUT = RESULTS / "carry_rf_0036r2"
R1_SUMMARY = R1_DIR / "summary.json"
R1_DAILY = R1_DIR / "daily_repricing.csv"
EXPECTED_FRED_SHA256 = "27b9d881b98ec90890a891c1080170fe6ade2a682ab01b6e66561479b113d0c3"


def annual_vol(ret: pd.Series) -> float:
    values = ret.dropna().astype(float)
    if len(values) < 2:
        raise ValueError("insufficient daily returns for annual volatility")
    return float(values.std(ddof=1) * math.sqrt(365.0))


def review_excess_sharpe(excess_cagr: float, strategy_return: pd.Series) -> float:
    vol = annual_vol(strategy_return)
    if vol <= 0:
        raise ValueError("strategy annualized volatility must be positive")
    return float(excess_cagr / vol)


def build_report(r1: dict[str, Any], daily: pd.DataFrame) -> dict[str, Any]:
    if r1.get("status") != "FIRST_VALID_REPRICING_COMPLETE":
        raise RuntimeError("R1 source is not the preserved first valid repricing")
    fred_sha = r1["carry_pnl_0031"]["risk_free_source"]["raw_csv_sha256"]
    if fred_sha != EXPECTED_FRED_SHA256:
        raise RuntimeError(f"unexpected R1 FRED source digest: {fred_sha}")

    required = {
        "date",
        "carry_0031_return",
        "rf_daily_return",
        "stack_0033_combined_return",
        "stack_0033_brrk_plus_idle_cash_return",
    }
    missing = sorted(required.difference(daily.columns))
    if missing:
        raise RuntimeError(f"R1 daily evidence missing columns: {missing}")

    carry = r1["carry_pnl_0031"]
    stack = r1["carry_stack_0033"]
    carry_excess_cagr = float(carry["risk_free_restatement"]["excess_cagr_over_rf"])
    stack_excess_cagr = float(stack["risk_free_restatement"]["excess_cagr_over_rf"])

    carry_vol = annual_vol(daily["carry_0031_return"])
    stack_vol = annual_vol(daily["stack_0033_combined_return"])
    carry_corrected = review_excess_sharpe(carry_excess_cagr, daily["carry_0031_return"])
    stack_corrected = review_excess_sharpe(stack_excess_cagr, daily["stack_0033_combined_return"])

    carry_old = float(carry["risk_free_restatement"]["excess_sharpe_over_rf"])
    stack_old = float(stack["risk_free_restatement"]["excess_sharpe_over_rf"])

    return {
        "experiment_id": EXPERIMENT_ID,
        "status": "FIRST_VALID_REPORTING_CORRECTION_COMPLETE",
        "promotion_evidence": False,
        "source_experiment": r1["experiment_id"],
        "source_daily_evidence": "research/results/carry_rf_0036r1/daily_repricing.csv",
        "source_fred_raw_sha256": fred_sha,
        "authorized_change": "named excess_sharpe_over_rf reporting convention only",
        "carry_pnl_0031": {
            "excess_cagr_over_rf": carry_excess_cagr,
            "strategy_ann_vol": carry_vol,
            "r1_excess_sharpe_over_rf_preserved": carry_old,
            "excess_sharpe_over_rf": carry_corrected,
            "pr30_reference_rounded": -0.223,
            "absolute_difference_to_pr30_rounded_reference": abs(carry_corrected - (-0.223)),
            "corrected_net_economics_pass": bool(carry["corrected_net_economics_pass"]),
            "decision": carry["decision"],
        },
        "carry_stack_0033": {
            "excess_cagr_over_rf": stack_excess_cagr,
            "strategy_ann_vol": stack_vol,
            "r1_excess_sharpe_over_rf_preserved": stack_old,
            "excess_sharpe_over_rf": stack_corrected,
            "corrected_net_economics_pass": bool(stack["corrected_net_economics_pass"]),
            "decision": stack["decision"],
        },
        "carry_line_stopped_under_discipline_7": bool(r1["carry_line_stopped_under_discipline_7"]),
        "carry_pm_0035_required": bool(r1["carry_pm_0035_required"]),
        "carry_pm_0037_required": bool(r1["carry_pm_0037_required"]),
        "decision": "REPORTING_METRIC_CORRECTED_R1_STOP_DECISION_UNCHANGED",
        "stopping_rule": "R2 cannot alter the R1 excess-CAGR gate or carry-line decision. No rescue or strategy rerun is authorized.",
    }


def main() -> None:
    r1 = json.loads(R1_SUMMARY.read_text(encoding="utf-8"))
    daily = pd.read_csv(R1_DAILY)
    report = build_report(r1, daily)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = (
        "# CARRY-RF-0036R2 result\n\n"
        f"- CARRY-PNL-0031 excess Sharpe over rf: **{report['carry_pnl_0031']['excess_sharpe_over_rf']:.6f}**\n"
        f"- PR #30 rounded reference: **-0.223**\n"
        f"- CARRY-STACK-0033 excess Sharpe over rf: **{report['carry_stack_0033']['excess_sharpe_over_rf']:.6f}**\n"
        "- Net-economics gate and carry-line STOP decision: **unchanged**.\n\n"
        "R1 is preserved unchanged; R2 corrects only the named reporting convention.\n"
    )
    (OUTPUT / "RESULT.md").write_text(md, encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
