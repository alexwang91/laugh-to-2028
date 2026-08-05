from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
RESULTS = RESEARCH / "results"
for path in (HERE, RESEARCH, RESEARCH / "asym_beta"):
    sys.path.insert(0, str(path))

from common.risk_free import (
    annual_carry_vs_cash,
    compare_to_cash,
    load_fred_daily_risk_free,
)
from run_carry_stack_0033 import (
    brrk_strict_return,
    combine_idle_stack,
    held_brrk_gross,
    reconstruct_frozen_carry,
)

EXPERIMENT_ID = "CARRY-RF-0036R1-RISK-FREE-HURDLE"
OUTPUT = RESULTS / "carry_rf_0036r1"
PUBLISHED_0031 = RESULTS / "carry_pnl_0031" / "summary.json"
PUBLISHED_0033 = RESULTS / "carry_stack_0033" / "summary.json"
FRED_SERIES = "DTB3"
REFERENCE_CARRY_CAGR = 0.027404258463378905
REFERENCE_CASH_CAGR_ROUNDED = 0.03165
REFERENCE_EXCESS_SHARPE_ROUNDED = -0.223
REFERENCE_CUMULATIVE = 0.1719827766646282
REFERENCE_2021 = 0.16803690598573118
STACK_PARITY_DOLLARS = 0.05


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def cumulative_return(ret: pd.Series) -> float:
    return float((1.0 + ret.dropna().astype(float)).prod() - 1.0)


def annualized_vol(ret: pd.Series) -> float:
    return float(ret.dropna().astype(float).std(ddof=1) * math.sqrt(365.0))


def stack_parity(frame: pd.DataFrame, published: dict[str, Any]) -> dict[str, Any]:
    actual_combined = float((1.0 + frame["combined_return"]).prod() * 10000.0)
    actual_brrk = float((1.0 + frame["brrk_return"]).prod() * 10000.0)
    expected_combined = float(published["combined_idle_capital_stack"]["final_10k"])
    expected_brrk = float(published["baseline_strict_router_brrk"]["final_10k"])
    combined_delta = abs(actual_combined - expected_combined)
    brrk_delta = abs(actual_brrk - expected_brrk)
    return {
        "expected_combined_final_10k": expected_combined,
        "reconstructed_combined_final_10k": actual_combined,
        "combined_abs_difference_dollars": combined_delta,
        "expected_brrk_final_10k": expected_brrk,
        "reconstructed_brrk_final_10k": actual_brrk,
        "brrk_abs_difference_dollars": brrk_delta,
        "tolerance_dollars": STACK_PARITY_DOLLARS,
        "pass": bool(combined_delta <= STACK_PARITY_DOLLARS and brrk_delta <= STACK_PARITY_DOLLARS),
    }


def corrected_0031_qualification(
    published: dict[str, Any], net_economics: bool
) -> dict[str, Any]:
    old = published["qualification"]
    out = {
        "net_economics": bool(net_economics),
        "funding_mechanism": bool(old["funding_mechanism"]),
        "daily_correlation_below_0_50": bool(old["daily_correlation_below_0_50"]),
        "nonnegative_brrk_worst_decile_day_alpha": bool(old["nonnegative_brrk_worst_decile_day_alpha"]),
    }
    out["qualified_for_stack_test"] = bool(all(out.values()))
    return out


def corrected_0033_qualification(
    published: dict[str, Any], net_economics: bool
) -> dict[str, Any]:
    old = published["qualification"]
    out = {
        "net_economics_vs_idle_cash": bool(net_economics),
        "return_improvement": bool(old["return_improvement"]),
        "sharpe_improvement": bool(old["sharpe_improvement"]),
        "drawdown_nonworsening": bool(old["drawdown_nonworsening"]),
        "calmar_improvement": bool(old["calmar_improvement"]),
        "gross_discipline": bool(old["gross_discipline"]),
    }
    out["qualified_idle_capital_stack_corrected"] = bool(all(out.values()))
    return out


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    published_0031 = load_json(PUBLISHED_0031)
    published_0033 = load_json(PUBLISHED_0033)

    carry, carry_source_parity = reconstruct_frozen_carry()
    brrk = brrk_strict_return()
    gross = held_brrk_gross()
    stack = combine_idle_stack(brrk, carry, gross)
    stack_source_parity = stack_parity(stack, published_0033)
    if not stack_source_parity["pass"]:
        raise RuntimeError(f"CARRY-STACK-0033 reconstruction parity failed: {stack_source_parity}")

    start = carry.index.min()
    end = carry.index.max()
    rf_load = load_fred_daily_risk_free(start, end, series_id=FRED_SERIES)
    rf_full = rf_load.daily["rf_daily_return"].astype(float)
    rf_carry = rf_full.reindex(carry.index)
    if rf_carry.isna().any():
        raise RuntimeError("risk-free series missing a CARRY-PNL-0031 evaluation day")

    carry_compare = compare_to_cash(carry, rf_carry)
    carry_annual = annual_carry_vs_cash(carry, rf_carry)
    carry_net_economics = bool(carry_compare["excess_cagr_over_rf"] > 0.0)
    qualification_0031 = corrected_0031_qualification(published_0031, carry_net_economics)

    stack = stack.copy()
    stack["rf_daily_return"] = rf_full.reindex(stack.index)
    if stack["rf_daily_return"].isna().any():
        raise RuntimeError("risk-free series missing a CARRY-STACK-0033 evaluation day")
    stack["scaled_idle_cash_return"] = stack["carry_scale"] * stack["rf_daily_return"]
    stack["brrk_plus_idle_cash_return"] = stack["brrk_return"] + stack["scaled_idle_cash_return"]
    stack["incremental_sleeve_excess_return"] = (
        stack["scaled_carry_net"] - stack["scaled_idle_cash_return"]
    )
    stack_compare = compare_to_cash(
        stack["combined_return"], stack["brrk_plus_idle_cash_return"]
    )
    stack_net_economics = bool(stack_compare["excess_cagr_over_rf"] > 0.0)
    qualification_0033 = corrected_0033_qualification(published_0033, stack_net_economics)
    stack_annual_combined = annual_carry_vs_cash(
        stack["combined_return"], stack["brrk_plus_idle_cash_return"]
    )
    stack_annual_sleeve = annual_carry_vs_cash(
        stack["scaled_carry_net"], stack["scaled_idle_cash_return"]
    )

    carry_total = cumulative_return(carry)
    carry_2021 = cumulative_return(carry.loc[carry.index.year == 2021])
    reference_parity = {
        "carry_cagr_reference": REFERENCE_CARRY_CAGR,
        "carry_cagr_actual": carry_compare["strategy"]["cagr"],
        "carry_cagr_abs_difference": abs(carry_compare["strategy"]["cagr"] - REFERENCE_CARRY_CAGR),
        "cash_cagr_reference_rounded": REFERENCE_CASH_CAGR_ROUNDED,
        "cash_cagr_actual": carry_compare["cash_benchmark"]["cagr"],
        "cash_cagr_abs_difference_to_rounded_reference": abs(
            carry_compare["cash_benchmark"]["cagr"] - REFERENCE_CASH_CAGR_ROUNDED
        ),
        "excess_sharpe_reference_rounded": REFERENCE_EXCESS_SHARPE_ROUNDED,
        "excess_sharpe_actual": carry_compare["excess_sharpe_over_rf"],
        "excess_sharpe_abs_difference_to_rounded_reference": abs(
            float(carry_compare["excess_sharpe_over_rf"]) - REFERENCE_EXCESS_SHARPE_ROUNDED
        ),
        "cumulative_reference": REFERENCE_CUMULATIVE,
        "cumulative_actual": carry_total,
        "return_2021_reference": REFERENCE_2021,
        "return_2021_actual": carry_2021,
        "review_numbers_reproduced_with_rounding": bool(
            abs(carry_compare["strategy"]["cagr"] - REFERENCE_CARRY_CAGR) <= 5e-6
            and abs(carry_compare["cash_benchmark"]["cagr"] - REFERENCE_CASH_CAGR_ROUNDED) <= 5e-5
            and abs(float(carry_compare["excess_sharpe_over_rf"]) - REFERENCE_EXCESS_SHARPE_ROUNDED) <= 0.005
            and abs(carry_total - REFERENCE_CUMULATIVE) <= 5e-6
            and abs(carry_2021 - REFERENCE_2021) <= 5e-6
        ),
    }

    report_0031 = {
        "restatement_experiment_id": EXPERIMENT_ID,
        "source_experiment_id": "CARRY-PNL-0031",
        "published_report_preserved": str(PUBLISHED_0031.relative_to(RESEARCH.parent)),
        "published_decision": published_0031.get("decision"),
        "published_canonical_5bps": published_0031["canonical_5bps"],
        "published_qualification": published_0031["qualification"],
        "risk_free_source": rf_load.metadata,
        "risk_free_restatement": carry_compare,
        "annual_carry_vs_cash": carry_annual,
        "corrected_qualification": qualification_0031,
        "corrected_net_economics_pass": carry_net_economics,
        "decision": (
            "FAIL_CORRECTED_NET_ECONOMICS_STOP_CARRY_LINE"
            if not carry_net_economics
            else "PASS_CORRECTED_NET_ECONOMICS"
        ),
        "source_reconstruction_parity": carry_source_parity,
        "review_reference_parity": reference_parity,
    }

    report_0033 = {
        "restatement_experiment_id": EXPERIMENT_ID,
        "source_experiment_id": "CARRY-STACK-0033-IDLE-CAPITAL",
        "published_report_preserved": str(PUBLISHED_0033.relative_to(RESEARCH.parent)),
        "published_decision": published_0033.get("decision"),
        "published_baseline_strict_router_brrk": published_0033["baseline_strict_router_brrk"],
        "published_combined_idle_capital_stack": published_0033["combined_idle_capital_stack"],
        "published_qualification": published_0033["qualification"],
        "risk_free_restatement": stack_compare,
        "annual_combined_vs_brrk_plus_idle_cash": stack_annual_combined,
        "annual_carry_vs_cash": stack_annual_sleeve,
        "incremental_sleeve": {
            "scaled_carry_net_cumulative": cumulative_return(stack["scaled_carry_net"]),
            "scaled_idle_cash_cumulative": cumulative_return(stack["scaled_idle_cash_return"]),
            "incremental_excess_cumulative": cumulative_return(stack["incremental_sleeve_excess_return"]),
            "incremental_excess_ann_vol": annualized_vol(stack["incremental_sleeve_excess_return"]),
        },
        "corrected_qualification": qualification_0033,
        "corrected_net_economics_pass": stack_net_economics,
        "decision": (
            "FAIL_CORRECTED_NET_ECONOMICS_AND_REMAIN_REJECTED"
            if not stack_net_economics
            else "CORRECTED_NET_ECONOMICS_PASS_BUT_ORIGINAL_0033_GATES_STILL_CONTROL"
        ),
        "source_reconstruction_parity": stack_source_parity,
    }

    carry_line_stopped = not carry_net_economics
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "status": "FIRST_VALID_REPRICING_COMPLETE",
        "promotion_evidence": False,
        "authorized_change": "risk-free accounting benchmark only",
        "carry_pnl_0031": report_0031,
        "carry_stack_0033": report_0033,
        "carry_line_stopped_under_discipline_7": carry_line_stopped,
        "carry_pm_0035_required": not carry_line_stopped,
        "carry_pm_0037_required": not carry_line_stopped,
        "decision": (
            "STOP_CARRY_LINE_AND_DO_NOT_RUN_PM_PROBE"
            if carry_line_stopped
            else "CARRY_LINE_REMAINS_ELIGIBLE_FOR_PREVIOUSLY_AUTHORIZED_NEXT_GATE"
        ),
        "stopping_rule": (
            "If 0031 fails corrected net economics, retain 0031/0033 and this restatement as negative evidence. "
            "Do not rescue by changing assets, funding sign, basis threshold, weights, leverage, costs or window."
        ),
    }

    rf_out = rf_load.daily.copy()
    rf_out.to_csv(OUTPUT / "risk_free_daily.csv", index_label="date")
    (OUTPUT / "fred_dtb3_raw.csv").write_text(rf_load.raw_csv, encoding="utf-8")

    daily = pd.DataFrame(index=carry.index)
    daily["carry_0031_return"] = carry
    daily["rf_daily_return"] = rf_carry
    daily["carry_0031_excess_return"] = carry - rf_carry
    for column in (
        "brrk_return",
        "carry_scale",
        "scaled_carry_net",
        "scaled_idle_cash_return",
        "combined_return",
        "brrk_plus_idle_cash_return",
        "incremental_sleeve_excess_return",
    ):
        daily[f"stack_0033_{column}"] = stack[column].reindex(daily.index)
    daily.to_csv(OUTPUT / "daily_repricing.csv", index_label="date")

    (OUTPUT / "CARRY-PNL-0031-RF-RESTATEMENT.json").write_text(
        json.dumps(report_0031, indent=2), encoding="utf-8"
    )
    (OUTPUT / "CARRY-STACK-0033-RF-RESTATEMENT.json").write_text(
        json.dumps(report_0033, indent=2), encoding="utf-8"
    )
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    result_md = f"""# CARRY-RF-0036R1 result\n\n"
    result_md += f"- CARRY-PNL-0031 CAGR: **{carry_compare['strategy']['cagr'] * 100:.3f}%**\n"
    result_md += f"- DTB3 cash CAGR: **{carry_compare['cash_benchmark']['cagr'] * 100:.3f}%**\n"
    result_md += f"- excess CAGR over cash: **{carry_compare['excess_cagr_over_rf'] * 100:+.3f} pp/yr**\n"
    result_md += f"- excess Sharpe over cash: **{carry_compare['excess_sharpe_over_rf']:.3f}**\n"
    result_md += f"- corrected 0031 net_economics: **{'PASS' if carry_net_economics else 'FAIL'}**\n"
    result_md += f"- corrected 0033 net_economics: **{'PASS' if stack_net_economics else 'FAIL'}**\n"
    result_md += f"- carry line stopped under discipline #7: **{str(carry_line_stopped).lower()}**\n\n"
    result_md += "Old published 0031/0033 reports are preserved unchanged. This directory is an accounting restatement only.\n"
    (OUTPUT / "RESULT.md").write_text(result_md, encoding="utf-8")

    print("=== CARRY_RF_0036R1_REPORT ===")
    print(json.dumps(summary, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
