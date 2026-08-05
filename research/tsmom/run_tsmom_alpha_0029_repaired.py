from __future__ import annotations

import json
from pathlib import Path

import run_tsmom_alpha_0029 as base
from funding_event_semantics_0029b import funding_accounting_event_semantics
from kline_gap_repair_0029a import repair_internal_gaps

REPAIR_ROWS: list[dict] = []
_ORIGINAL_LOAD_PRICE_HISTORY = base.load_price_history


def repaired_load_price_history(symbol: str) -> dict:
    row = _ORIGINAL_LOAD_PRICE_HISTORY(symbol)
    history = row.get("history")
    if history is None or history.empty:
        return row
    repaired, diagnostic = repair_internal_gaps(symbol, history, base.parse_kline_zip)
    row["history"] = repaired
    row["gap_repair"] = diagnostic
    REPAIR_ROWS.append(diagnostic)
    return row


def repair_summary() -> dict:
    rows = list(REPAIR_ROWS)
    detected = sum(int(row["internal_monthly_gap_count"]) for row in rows)
    repaired = sum(int(row["daily_fallback_repaired_count"]) for row in rows)
    unresolved = sum(int(row["daily_fallback_unresolved_count"]) for row in rows)
    repaired_examples = [
        {"symbol": row["symbol"], "dates": row["repaired_dates"][:10]}
        for row in rows if row["repaired_dates"]
    ][:50]
    unresolved_examples = [
        {"symbol": row["symbol"], "dates": row["unresolved_dates"][:10]}
        for row in rows if row["unresolved_dates"]
    ][:50]
    return {
        "audit_id": "TSMOM-DATA-0029A-MONTHLY-GAP-REPAIR",
        "symbols_checked": len(rows),
        "internal_monthly_gaps_detected": detected,
        "official_daily_1d_gaps_repaired": repaired,
        "unresolved_internal_gaps": unresolved,
        "symbols_with_repaired_gaps": sum(bool(row["repaired_dates"]) for row in rows),
        "symbols_with_unresolved_gaps": sum(bool(row["unresolved_dates"]) for row in rows),
        "repaired_examples": repaired_examples,
        "unresolved_examples": unresolved_examples,
        "rule": "monthly 1d primary; exact missing internal UTC date may be filled only from official Binance daily 1d archive; no interpolation/ffill/spot substitution/zero return",
    }


def main() -> None:
    base.load_price_history = repaired_load_price_history
    base.funding_accounting = funding_accounting_event_semantics
    base.main()

    diagnostic = repair_summary()
    output = Path(base.OUTPUT)
    (output / "monthly_gap_repair.json").write_text(json.dumps(diagnostic, indent=2), encoding="utf-8")

    summary_path = output / "summary.json"
    report = json.loads(summary_path.read_text(encoding="utf-8"))
    report["monthly_kline_gap_repair"] = diagnostic
    report["funding_event_semantics"] = {
        "audit_id": "TSMOM-DATA-0029B-FUNDING-EVENT-SEMANTICS",
        "rule": "only official recorded settlement events create funding cashflow; active symbol-days without an event contribute zero cashflow and remain explicit coverage diagnostics",
    }
    summary_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=== TSMOM_DATA_0029A_REPAIR ===")
    print(json.dumps(diagnostic, indent=2))
    print("=== END_REPAIR ===")


if __name__ == "__main__":
    main()
