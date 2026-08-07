from __future__ import annotations

"""R3 fail-closed recovery for LEVERAGE-0040 one-time execution.

Recovery run 31198649428 reached the liquidation-distance check and failed
because the frozen liquidation model intentionally rejects a starting state
that is already liquidatable.  That is a valid risk failure, not a reason to
abort the entire study.  R3 preserves the liquidation model and every frozen
economic parameter; it converts that model state into an explicit distance=0
failure in the study report.
"""

import hashlib
import json
from pathlib import Path

import run_leverage_0040_once_r2 as r2

base = r2.base

CORRECTION_PATH = Path(__file__).with_name(
    "LEVERAGE-0040-PRE-RESULT-CORRECTION-R3.json"
)


def _minimum_liquidation_distance_r3(cand, matched):
    snapshot = base.load_frozen_snapshot()
    minimum = float("inf")
    worst = None
    any_perp = False
    for dt in cand.index.intersection(matched.index):
        routed = base._route_exposures(cand.loc[dt], matched.loc[dt])
        spot = routed[("BTC", "spot")]
        perp = {
            "BTC": routed[("BTC", "perp")],
            "ETH": routed[("ETH", "perp")],
            "SOL": routed[("SOL", "perp")],
            "BNB": routed[("BNB", "perp")],
        }
        notionals = {
            a: w * base.REFERENCE_EQUITY for a, w in perp.items() if w > 1e-15
        }
        if not notionals:
            continue
        any_perp = True
        equity = base.REFERENCE_EQUITY * (1 - spot)
        if equity <= 0:
            return {
                "pass": False,
                "minimum_uniform_down_move": 0.0,
                "worst_date": dt.strftime("%Y-%m-%d"),
            }

        start = base.evaluate_cross_margin_state(
            current_cross_account_equity_usd=equity,
            current_long_perp_notionals_usd=notionals,
            relative_mark_returns={a: 0.0 for a in notionals},
            snapshot=snapshot,
        )
        if start.liquidatable:
            return {
                "pass": False,
                "minimum_uniform_down_move": 0.0,
                "worst_date": dt.strftime("%Y-%m-%d"),
            }

        dist = base.uniform_long_down_liquidation_distance(
            current_cross_account_equity_usd=equity,
            current_long_perp_notionals_usd=notionals,
            snapshot=snapshot,
        )
        d = (
            float("inf")
            if not dist.liquidates_within_domain
            else float(dist.uniform_down_move_fraction)
        )
        if d < minimum:
            minimum = d
            worst = dt

    if not any_perp:
        return {
            "pass": True,
            "minimum_uniform_down_move": None,
            "worst_date": None,
        }
    return {
        "pass": minimum > 0.50,
        "minimum_uniform_down_move": None
        if minimum == float("inf")
        else minimum,
        "worst_date": None if worst is None else worst.strftime("%Y-%m-%d"),
    }


def _augment_r3_evidence() -> None:
    summary = base.RESULT_DIR / "summary.json"
    digest_file = base.RESULT_DIR / "summary.sha256"
    if not summary.exists():
        return
    payload = json.loads(summary.read_text(encoding="utf-8"))
    evidence = payload.setdefault("input_evidence", {})
    corrections = list(evidence.get("preflight_corrections", []))
    if "PREFLIGHT-LIQUIDATION-START-004" not in corrections:
        corrections.append("PREFLIGHT-LIQUIDATION-START-004")
    evidence["preflight_corrections"] = corrections
    evidence["runner_entrypoint"] = (
        "research/leverage_0040/run_leverage_0040_once_r3.py"
    )
    evidence["r3_correction_sha256"] = hashlib.sha256(
        CORRECTION_PATH.read_bytes()
    ).hexdigest()
    provenance = payload.setdefault("execution_provenance", {})
    provenance["r3_recovery"] = {
        "failed_run_id": 31198649428,
        "failed_head": "c3ec4a747b68349ceb0c1d17fdd5b8593e0e9af5",
        "immutable_result_committed_before_failure": False,
        "cap_gt_1_metrics_emitted_before_failure": False,
    }
    summary.write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    digest = hashlib.sha256(summary.read_bytes()).hexdigest()
    digest_file.write_text(digest + "\n", encoding="utf-8")
    print(f"LEVERAGE-0040 R3 immutable summary_sha256={digest}")


def main() -> None:
    base._minimum_liquidation_distance = _minimum_liquidation_distance_r3
    r2.main()
    _augment_r3_evidence()


if __name__ == "__main__":
    main()
