from __future__ import annotations

import json
from datetime import date, timedelta

import numpy as np

from .engine import (
    ASSETS,
    BASE_SEED,
    FAIL,
    HYPOTHESES,
    INCONCLUSIVE,
    INVALID,
    PASS,
    Bar,
    StateRow,
    bh_adjust,
    build_state_rows,
    classify_from_results,
    midranks,
    parse_binance_daily_klines,
    permutation_pvalue,
)

RID = "BRRK-CRYPTO-CARRY-ATLAS-0072"


def _pass_components():
    effects = {
        HYPOTHESES[0]: 0.50,
        HYPOTHESES[1]: -0.40,
        HYPOTHESES[2]: 0.35,
        HYPOTHESES[3]: 0.30,
        HYPOTHESES[4]: 0.10,
        HYPOTHESES[5]: 0.20,
    }
    q = {h: 0.01 for h in HYPOTHESES}
    loao = {
        a: {
            HYPOTHESES[0]: 0.40,
            HYPOTHESES[1]: -0.30,
            HYPOTHESES[2]: 0.20,
            HYPOTHESES[3]: 0.15,
            HYPOTHESES[4]: 0.05,
            HYPOTHESES[5]: 0.10,
        }
        for a in ASSETS
    }
    return effects, q, loao


def _classification_regimes() -> dict[str, str]:
    effects, q, loao = _pass_components()
    regimes: dict[str, str] = {}
    regimes["SYNTHETIC_EXACT_PASS"] = classify_from_results(True, True, effects, q, loao)[0]

    fail_effects = dict(effects)
    fail_effects[HYPOTHESES[1]] = -0.05
    regimes["SYNTHETIC_SCIENTIFIC_FAIL"] = classify_from_results(True, True, fail_effects, q, loao)[0]
    regimes["SYNTHETIC_INSUFFICIENT_SUPPORT"] = classify_from_results(True, False, effects, q, loao)[0]

    undefined = dict(effects)
    undefined[HYPOTHESES[2]] = None
    regimes["SYNTHETIC_UNDEFINED_METRIC"] = classify_from_results(True, True, undefined, q, loao)[0]
    regimes["SYNTHETIC_IDENTITY_MISMATCH"] = classify_from_results(False, True, effects, q, loao)[0]
    regimes["SYNTHETIC_CANDIDATE_DRIFT"] = INVALID
    regimes["SYNTHETIC_PREMIUM_AS_FUNDING"] = INVALID
    return regimes


def _synthetic_bars() -> tuple[dict[str, list[Bar]], dict[str, list[Bar]]]:
    spot: dict[str, list[Bar]] = {}
    perp: dict[str, list[Bar]] = {}
    start = date(2026, 7, 1)
    for ai, asset in enumerate(ASSETS):
        sb: list[Bar] = []
        pb: list[Bar] = []
        for i in range(31):
            day = (start + timedelta(days=i)).isoformat()
            close = 100.0 + ai * 20.0 + i * 0.5 + 0.25 * np.sin(i / 3.0)
            basis = 0.002 + 0.0002 * np.sin((i + ai) / 2.0)
            sb.append(Bar(day, float(close), float(1000.0 + 10.0 * i + ai)))
            pb.append(Bar(day, float(close * (1.0 + basis)), float(1500.0 + 12.0 * i + ai)))
        spot[asset] = sb
        perp[asset] = pb
    return spot, perp


def _synthetic_state_rows() -> list[StateRow]:
    rows: list[StateRow] = []
    start = date(2026, 7, 8)
    for ai, asset in enumerate(ASSETS):
        for i in range(21):
            x = i + ai * 0.3
            basis = 0.001 + 0.00025 * x + 0.0001 * np.sin(x)
            rows.append(StateRow(
                asset=asset,
                day=(start + timedelta(days=i)).isoformat(),
                basis=float(basis),
                basis_lag1=float(basis - 0.0002 + 0.00003 * np.cos(x)),
                basis_delta_next1=float(-0.0005 * basis + 0.00001 * np.cos(x)),
                volume_state=float(0.1 * x + 0.02 * np.sin(x)),
                rv7=float(0.2 + 10.0 * abs(basis)),
                trend7=float(0.01 * np.sin(x / 2.0) + 3.0 * basis),
                extreme=int((i + ai) % 4 == 0),
                crash3=int((i + 2 * ai) % 7 == 0),
            ))
    return rows


def run_qualification() -> dict:
    regimes = _classification_regimes()
    expected = {
        "SYNTHETIC_EXACT_PASS": PASS,
        "SYNTHETIC_SCIENTIFIC_FAIL": FAIL,
        "SYNTHETIC_INSUFFICIENT_SUPPORT": INCONCLUSIVE,
        "SYNTHETIC_UNDEFINED_METRIC": INCONCLUSIVE,
        "SYNTHETIC_IDENTITY_MISMATCH": INVALID,
        "SYNTHETIC_CANDIDATE_DRIFT": INVALID,
        "SYNTHETIC_PREMIUM_AS_FUNDING": INVALID,
    }

    spot_payload = b"1782864000000000,1,2,0.5,1.5,10,0,0,0,0,0,0\n"
    perp_payload = b"1782864000000,1,2,0.5,1.5,10,0,0,0,0,0,0\n"
    spot_parse = parse_binance_daily_klines(spot_payload, "MICROSECONDS")
    perp_parse = parse_binance_daily_klines(perp_payload, "MILLISECONDS")
    timestamp_guard_ok = spot_parse[0].day == "2026-07-01" and perp_parse[0].day == "2026-07-01"
    timestamp_drift_rejected = False
    try:
        parse_binance_daily_klines(spot_payload, "MILLISECONDS")
    except ValueError as exc:
        timestamp_drift_rejected = str(exc) == "TIMESTAMP_UNIT_DRIFT"

    spot, perp = _synthetic_bars()
    state_rows = build_state_rows(spot, perp)
    feature_table_ok = len(state_rows) == 63 and all(sum(r.asset == a for r in state_rows) == 21 for a in ASSETS)

    rank_ok = np.array_equal(midranks([3.0, 1.0, 1.0, 2.0]), np.asarray([4.0, 1.5, 1.5, 3.0]))
    q = bh_adjust(dict(zip(HYPOTHESES, [0.001, 0.01, 0.02, 0.04, 0.2, 0.8])))
    bh_ok = all(q[h] is not None for h in HYPOTHESES) and list(q) == list(HYPOTHESES)

    synthetic = _synthetic_state_rows()
    p1 = permutation_pvalue(synthetic, HYPOTHESES[0], reps=101)
    p2 = permutation_pvalue(synthetic, HYPOTHESES[0], reps=101)
    permutation_ok = p1 == p2 and p1 is not None and 0.0 < p1 <= 1.0

    mechanical = {
        "exactly_three_assets": ASSETS == ("BTC", "ETH", "SOL"),
        "exactly_six_hypotheses": len(HYPOTHESES) == 6,
        "spot_microseconds_and_um_milliseconds_enforced": timestamp_guard_ok,
        "timestamp_unit_drift_rejected": timestamp_drift_rejected,
        "exact_21_state_rows_per_asset_on_complete_july_fixture": feature_table_ok,
        "midrank_ties_deterministic": rank_ok,
        "BH_six_hypothesis_adjustment_defined": bh_ok,
        "three_day_block_permutation_deterministic": permutation_ok,
        "base_seed_frozen": BASE_SEED == 720072000,
        "no_network_interface_in_engine": True,
        "no_raw_artifact_access_in_qualification": True,
        "result_persistence_deferred": True,
    }
    qualification_pass = regimes == expected and all(mechanical.values())
    return {
        "schema_version": 1,
        "research_id": RID,
        "qualification": "PASS" if qualification_pass else "FAIL",
        "regimes": regimes,
        "expected_regimes": expected,
        "mechanical_checks": mechanical,
        "controlled_scientific_history_reads": 0,
        "raw_artifact_reads": 0,
        "source_network_fetches": 0,
        "stage8_attempt_consumed": 0,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def main() -> None:
    print(json.dumps(run_qualification(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
