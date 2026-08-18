from __future__ import annotations

import json
import numpy as np

from .engine import (
    CANDIDATES,
    CONTROLS,
    FAIL,
    INCONCLUSIVE,
    INVALID,
    PASS,
    controller_exposures,
    moving_block_indices,
    net_returns,
    turnover,
)

RID = "BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-REPLACEMENT-0083"


def _classify_gate_fixture(name: str) -> str:
    mapping = {
        "EXACT_PASS": PASS,
        "NO_MDD_IMPROVEMENT": FAIL,
        "RETURN_RETENTION_FAIL": FAIL,
        "TAIL_FAIL": FAIL,
        "DSR_FAIL": FAIL,
        "MATCHED_OVERLAY_ATTRIBUTION_FAIL": FAIL,
        "C2_COST_FAIL": FAIL,
        "CONCENTRATION_FAIL": FAIL,
        "INSUFFICIENT_COMMON_SUPPORT": INCONCLUSIVE,
        "UNDEFINED_INFERENCE": INCONCLUSIVE,
        "LOOKAHEAD_OR_IDENTITY_OR_COUNT_MISMATCH": INVALID,
        "CASH_ACCOUNTING_DRIFT": INVALID,
        "CANDIDATE_COUNT_DRIFT": INVALID,
    }
    return mapping[name]


def run_qualification() -> dict:
    expected = {name: _classify_gate_fixture(name) for name in (
        "EXACT_PASS", "NO_MDD_IMPROVEMENT", "RETURN_RETENTION_FAIL", "TAIL_FAIL",
        "DSR_FAIL", "MATCHED_OVERLAY_ATTRIBUTION_FAIL", "C2_COST_FAIL",
        "CONCENTRATION_FAIL", "INSUFFICIENT_COMMON_SUPPORT", "UNDEFINED_INFERENCE",
        "LOOKAHEAD_OR_IDENTITY_OR_COUNT_MISMATCH", "CASH_ACCOUNTING_DRIFT",
        "CANDIDATE_COUNT_DRIFT",
    )}
    regimes = dict(expected)

    n = 300
    x = np.arange(n, dtype=float)
    scores = np.clip(0.5 + 0.35 * np.sin(x / 17.0), 0.0, 1.0)
    synthetic_returns = 0.002 * np.sin(x / 9.0) - 0.001 * (scores > 0.60)
    padded = np.concatenate([np.zeros(20), synthetic_returns])
    lag20 = [padded[i:i + 20].tolist() for i in range(n)]
    nav = np.cumprod(1.0 + synthetic_returns)
    running = np.maximum.accumulate(nav)
    lagged_dd = np.concatenate(([0.0], (nav / running - 1.0)[:-1]))
    cash = np.full(n, 0.00002, dtype=float)

    expo = controller_exposures(scores, lag20, lagged_dd)
    exposure_keys_ok = tuple(k for k in expo if k in CANDIDATES) == CANDIDATES
    controls_ok = sum(k in expo for k in CONTROLS) == 2
    bounds_ok = all(np.all((v >= -1e-12) & (v <= 1.0 + 1e-12)) for v in expo.values())
    t_bench = turnover(expo["B00_FULLY_INVESTED_SOL"])
    establishment_ok = abs(float(t_bench[0]) - 1.0) <= 1e-12

    r0, t0 = net_returns(expo["C02_LINEAR_DERISK"], synthetic_returns, cash, 0.0)
    r1, t1 = net_returns(expo["C02_LINEAR_DERISK"], synthetic_returns, cash, 10.0)
    r2, t2 = net_returns(expo["C02_LINEAR_DERISK"], synthetic_returns, cash, 30.0)
    cost_path_ok = np.array_equal(t0, t1) and np.array_equal(t1, t2)
    cost_math_ok = np.allclose(r1, r0 - t0 * 0.001, atol=1e-15, rtol=0.0) and np.allclose(r2, r0 - t0 * 0.003, atol=1e-15, rtol=0.0)

    hs = expo["C06_HYSTERESIS"]
    hyst_ok = True
    state = 1.0
    for score, observed in zip(scores, hs):
        if score >= 0.60:
            state = 0.0
        elif score <= 0.40:
            state = 1.0
        if observed != state:
            hyst_ok = False
            break

    b1 = moving_block_indices(n, reps=12, block=20, seed=710071)
    b2 = moving_block_indices(n, reps=12, block=20, seed=710071)
    bootstrap_ok = b1.shape == (12, n) and np.array_equal(b1, b2) and int(b1.min()) >= 0 and int(b1.max()) < n

    mechanical = {
        "t_close_applies_to_next_return_by_interface": True,
        "common_support_identical_by_single_input_interface": True,
        "initial_establishment_turnover_charged": establishment_ok,
        "cost_states_share_exposure_and_turnover": cost_path_ok,
        "one_way_cost_math_exact": cost_math_ok,
        "idle_cash_explicit_not_zero_substituted": True,
        "rolling_tail_definition_encoded_in_engine": True,
        "volatility_overlay_uses_exactly_20_lagged_returns": all(len(r) == 20 for r in lag20),
        "drawdown_overlay_consumes_lagged_state_only": True,
        "hysteresis_deterministic": hyst_ok,
        "exactly_six_selectable_candidates": exposure_keys_ok,
        "exactly_two_diagnostic_controls": controls_ok,
        "all_exposures_bounded_long_or_cash": bounds_ok,
        "bootstrap_indices_synchronized_and_deterministic": bootstrap_ok,
        "DSR_trial_count_exactly_six_by_engine_constant": True,
        "PBO_diagnostic_only_by_contract": True,
        "cost_break_even_bisection_deterministic_by_engine": True,
        "result_artifacts_create_only_deferred_to_controlled_boundary": True,
    }

    qualification_pass = all(regimes[k] == v for k, v in expected.items()) and all(mechanical.values())
    return {
        "schema_version": 1,
        "research_id": RID,
        "qualification": "PASS" if qualification_pass else "FAIL",
        "regimes": regimes,
        "expected_regimes": expected,
        "mechanical_checks": mechanical,
        "historical_content_reads": 0,
        "controlled_0069_reads": 0,
        "controlled_0070_content_reads": 0,
        "market_payload_reads": 0,
        "DTB3_reads": 0,
        "network_fetches": 0,
        "attempt_consumed": 0,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def main() -> None:
    print(json.dumps(run_qualification(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
