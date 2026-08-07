from __future__ import annotations

"""Pre-result R2 correction for LEVERAGE-0040 one-time execution.

Run 31197608453 failed during the cap=1.00 comparator gap-stress pass before
any cap>1 candidate was constructed. The failure was an implementation edge
case: a zero cross-margin equity state with a non-zero routed perp notional
was passed into the liquidation model, whose contract requires positive cross
equity.

R2 preserves all frozen economic semantics. It only makes _gap_stress fail
closed in the same way already used by _minimum_liquidation_distance:
if routed perp notionals exist while cross equity is non-positive, classify
the state as liquidatable instead of calling the liquidation model.
"""

import hashlib
import json
from pathlib import Path

import run_leverage_0040_once_r1 as r1

base = r1.base

CORRECTION_PATH = Path(__file__).with_name(
    "LEVERAGE-0040-PRE-RESULT-CORRECTION-R2.json"
)


def _gap_stress_r2(cand, matched):
    snapshot = base.load_frozen_snapshot()
    out = {}
    for name, gaps in base.GAP_SCENARIOS.items():
        worst = {"return": float("inf"), "date": None, "liquidatable": False}
        for dt in cand.index.intersection(matched.index):
            c = cand.loc[dt].to_dict()
            m = matched.loc[dt].to_dict()
            ret = base.synthetic_gap_return(c, gaps)
            routed = base._route_exposures(c, m)
            spot = routed[("BTC", "spot")]
            notionals = {
                "BTC": routed[("BTC", "perp")] * base.REFERENCE_EQUITY,
                "ETH": routed[("ETH", "perp")] * base.REFERENCE_EQUITY,
                "SOL": routed[("SOL", "perp")] * base.REFERENCE_EQUITY,
                "BNB": routed[("BNB", "perp")] * base.REFERENCE_EQUITY,
            }
            notionals = {a: v for a, v in notionals.items() if v > 1e-15}
            liq = False
            if notionals:
                equity = base.REFERENCE_EQUITY * (1 - spot)
                if equity <= 0:
                    liq = True
                else:
                    state = base.evaluate_cross_margin_state(
                        current_cross_account_equity_usd=equity,
                        current_long_perp_notionals_usd=notionals,
                        relative_mark_returns={a: gaps[a] for a in notionals},
                        snapshot=snapshot,
                    )
                    liq = bool(state.liquidatable)
            if ret < worst["return"]:
                worst = {
                    "return": ret,
                    "date": dt.strftime("%Y-%m-%d"),
                    "liquidatable": liq,
                }
            elif liq:
                worst["liquidatable"] = True
        worst.update(
            {
                "catastrophe_pass": worst["return"] > -0.70,
                "liquidation_pass": not worst["liquidatable"],
            }
        )
        worst["pass"] = worst["catastrophe_pass"] and worst["liquidation_pass"]
        out[name] = worst
    return out


def _augment_r2_evidence() -> None:
    summary = base.RESULT_DIR / "summary.json"
    digest_file = base.RESULT_DIR / "summary.sha256"
    if not summary.exists():
        return
    payload = json.loads(summary.read_text(encoding="utf-8"))
    evidence = payload.setdefault("input_evidence", {})
    corrections = list(evidence.get("preflight_corrections", []))
    if "PREFLIGHT-GAP-CROSS-EQUITY-003" not in corrections:
        corrections.append("PREFLIGHT-GAP-CROSS-EQUITY-003")
    evidence["preflight_corrections"] = corrections
    evidence["runner_entrypoint"] = (
        "research/leverage_0040/run_leverage_0040_once_r2.py"
    )
    evidence["r2_correction_sha256"] = hashlib.sha256(
        CORRECTION_PATH.read_bytes()
    ).hexdigest()
    payload["execution_provenance"] = {
        "initial_run_id": 31197608453,
        "initial_run_head": "78e8530cbef614e42e274828068f45a1f3e7542a",
        "initial_failure_before_cap_gt_1_construction": True,
        "r2_recovery": True,
    }
    summary.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    digest = hashlib.sha256(summary.read_bytes()).hexdigest()
    digest_file.write_text(digest + "\n", encoding="utf-8")
    print(f"LEVERAGE-0040 R2 immutable summary_sha256={digest}")


def main() -> None:
    base._gap_stress = _gap_stress_r2
    r1.main()
    _augment_r2_evidence()


if __name__ == "__main__":
    main()
