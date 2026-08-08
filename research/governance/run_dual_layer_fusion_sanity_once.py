from __future__ import annotations

"""One-shot, non-promotable economic diagnostic for DUAL-LAYER-FUSION-ARCH-SANITY-V1.

The runner deliberately reuses the already-frozen BRRK target authority and the
same P3.3 economic simulator used by P5.5. It does not contain a second BRRK or
a second rebalance implementation.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research"
CYCLE = RESEARCH / "cycle_exit"
L0040 = RESEARCH / "leverage_0040"
for path in (ROOT, RESEARCH, CYCLE, L0040):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_leverage_0040_once_r1 as authority  # noqa: E402
import study_core as core  # noqa: E402
from research.governance.dual_layer_fusion_sanity import (  # noqa: E402
    ASSETS,
    apply_external_gross_cap,
    classify_external_state,
)


CONTRACT_ID = "DUAL-LAYER-FUSION-ARCH-SANITY-V1"
EXPECTED_STABLECOIN_RAW_SHA256 = "7cffe6fb3a21e891082c06c60e91491edfbc78e9c01e2d549805815a646d9ffd"
EVALUATION_SESSION_START = pd.Timestamp("2022-12-10")
EVALUATION_SESSION_END = pd.Timestamp("2026-08-02")
COST_BPS = 5.0
BAND = 0.05
EXPECTED_BASELINE = {
    "cagr": 0.6530567772272526,
    "max_drawdown": -0.3352922961173609,
    "sharpe": 1.3561161360940506,
    "calmar": 1.9477237765065323,
    "turnover": 91.08660891147298,
    "avg_gross_exposure": 0.7543536295598084,
    "end_multiple": 6.2525274410172225,
}


class DiagnosticError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frame_sha256(frame: pd.DataFrame) -> str:
    payload = frame.to_csv(index=True, float_format="%.12f", lineterminator="\n").encode()
    return hashlib.sha256(payload).hexdigest()


def load_stablecoin_supply(path: Path) -> pd.Series:
    if sha256_file(path) != EXPECTED_STABLECOIN_RAW_SHA256:
        raise DiagnosticError("stablecoin raw artifact hash mismatch")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise DiagnosticError("stablecoin raw root must be an array")
    rows: dict[pd.Timestamp, float] = {}
    for item in raw:
        if not isinstance(item, dict):
            raise DiagnosticError("stablecoin row must be an object")
        dt = pd.to_datetime(int(item["date"]), unit="s", utc=True).tz_localize(None).normalize()
        value = float(item["totalCirculatingUSD"]["peggedUSD"])
        if not math.isfinite(value) or value <= 0:
            continue
        if dt in rows:
            raise DiagnosticError(f"duplicate stablecoin metric date: {dt.date()}")
        rows[dt] = value
    out = pd.Series(rows, dtype=float).sort_index()
    if out.empty:
        raise DiagnosticError("stablecoin supply is empty")
    return out


def external_state_for_decision(supply: pd.Series, decision: pd.Timestamp):
    # Frozen PIT semantics: observation dated t is available at t+2 calendar days.
    # Thus decision D uses exact metric dates D-2, D-22 and D-42.
    d = pd.Timestamp(decision).normalize()
    dates = (d - pd.Timedelta(days=2), d - pd.Timedelta(days=22), d - pd.Timedelta(days=42))
    missing = [x for x in dates if x not in supply.index]
    if missing:
        raise DiagnosticError(
            "missing exact stablecoin lag date(s) for decision "
            f"{d.date()}: {','.join(str(x.date()) for x in missing)}"
        )
    s2, s22, s42 = (float(supply.loc[x]) for x in dates)
    if min(s2, s22, s42) <= 0:
        raise DiagnosticError("stablecoin lag value must be positive")
    growth = math.log(s2) - math.log(s22)
    previous = math.log(s22) - math.log(s42)
    acceleration = growth - previous
    return classify_external_state(growth, acceleration)


def apply_external_path(base_targets: pd.DataFrame, supply: pd.Series) -> tuple[pd.DataFrame, dict[str, int]]:
    out = base_targets.loc[:, list(ASSETS)].copy().astype(float)
    counts = {"SUPPORTIVE": 0, "NEUTRAL": 0, "RESTRICTIVE": 0}
    for dt in out.index:
        state = external_state_for_decision(supply, pd.Timestamp(dt))
        counts[state.state] += 1
        fused = apply_external_gross_cap(out.loc[dt].to_dict(), state)
        out.loc[dt, list(ASSETS)] = [fused[a] for a in ASSETS]
    return out, counts


def simulate(targets: pd.DataFrame, prices: pd.DataFrame):
    decision_start = EVALUATION_SESSION_START - pd.Timedelta(days=1)
    path = core.simulate_p3_3_economic_path(
        targets,
        prices,
        start=decision_start,
        end=EVALUATION_SESSION_END,
        cost_bps=COST_BPS,
        band=BAND,
        fill_fraction=1.0,
        transaction_cost_multiplier=1.0,
        funding_blocks_by_session=None,
    )
    if len(path.returns) == 0 or pd.Timestamp(path.returns.index[0]) != EVALUATION_SESSION_START:
        raise DiagnosticError("P3.3 return-session timing mismatch")
    return path


def metric_payload(path) -> dict[str, float]:
    raw = core.path_metrics(path)
    return {
        "cagr": float(raw["cagr"]),
        "max_drawdown": float(raw["max_drawdown"]),
        "sharpe": float(raw["sharpe"]),
        "calmar": float(raw["calmar"]),
        "turnover": float(raw["turnover"]),
        "avg_gross_exposure": float(raw["avg_gross_exposure"]),
        "end_multiple": float(raw["end_multiple"]),
    }


def assert_baseline_reproduction(metrics: dict[str, float]) -> None:
    for key, expected in EXPECTED_BASELINE.items():
        actual = float(metrics[key])
        if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=5e-10):
            raise DiagnosticError(
                f"canonical matched-P3.3 baseline failed reproduction for {key}: "
                f"expected={expected:.15g} actual={actual:.15g}"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stablecoin-raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    supply = load_stablecoin_supply(args.stablecoin_raw)
    prices = authority._fetch_prices_corrected()
    _, brrk_targets_all, _ = authority._load_frozen_targets_corrected()

    decision_start = EVALUATION_SESSION_START - pd.Timedelta(days=1)
    mask = (brrk_targets_all.index >= decision_start) & (brrk_targets_all.index <= EVALUATION_SESSION_END)
    base_targets = brrk_targets_all.loc[mask, list(ASSETS)].copy()
    prices = prices.loc[(prices.index >= decision_start) & (prices.index <= EVALUATION_SESSION_END), list(ASSETS)].copy()
    if not base_targets.index.equals(prices.index):
        raise DiagnosticError("canonical BRRK target/price index mismatch")

    fused_targets, state_counts = apply_external_path(base_targets, supply)
    baseline_path = simulate(base_targets, prices)
    fused_path = simulate(fused_targets, prices)
    baseline = metric_payload(baseline_path)
    assert_baseline_reproduction(baseline)
    fused = metric_payload(fused_path)

    result = {
        "contract_id": CONTRACT_ID,
        "classification": "NON_PROMOTABLE_ARCHITECTURE_DIAGNOSTIC",
        "parameters_observed_before_run": False,
        "variant_budget": 1,
        "retuned_after_result": False,
        "evaluation": {
            "session_start": str(EVALUATION_SESSION_START.date()),
            "session_end": str(EVALUATION_SESSION_END.date()),
            "cost_bps": COST_BPS,
            "p3_3_band": BAND,
        },
        "input_evidence": {
            "stablecoin_raw_sha256": EXPECTED_STABLECOIN_RAW_SHA256,
            "stablecoin_history_role": "RESEARCHER_EXPOSED_DEVELOPMENT_SANITY_ONLY",
            "brrk_target_frame_sha256": frame_sha256(base_targets),
            "brrk_target_authority": authority._target_authority_meta,
        },
        "external_state_counts_on_target_rows": state_counts,
        "baseline": baseline,
        "fused": fused,
        "delta": {key: float(fused[key] - baseline[key]) for key in baseline},
        "promotion_eligible": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
        "interpretation_boundary": (
            "This result only verifies mechanical portfolio-economic impact of the frozen two-layer "
            "composition using already-exposed Stablecoin history. It cannot validate an external edge, "
            "cannot rescue STABLECOIN-LIQUIDITY-0001, and cannot authorize integration or production."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
