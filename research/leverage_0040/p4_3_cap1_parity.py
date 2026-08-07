from __future__ import annotations

"""P4.3 cap=1 historical parity gate.

This is intentionally the only executable LEVERAGE-0040 path before >1 research
is unlocked.  It regenerates the frozen P3.2 targets on the committed golden
historical dates, composes them through the new two-layer boundary with an
identity multiplier, and verifies that no P4 wiring changes the frozen baseline.
"""

import json
import math
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
EXECUTION_ROOT = REPO_ROOT / "execution" / "plan-b-bot"
INTEGRATION_ROOT = REPO_ROOT / "research" / "integration"
for path in (EXECUTION_ROOT, INTEGRATION_ROOT, Path(__file__).resolve().parent):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from beta_bot.product_config import load_product_config  # noqa: E402
from beta_bot.target_engine import calculate_target  # noqa: E402
from p3_1_data_contract_adapter import canonicalize_research_daily_history  # noqa: E402
from p3_2_golden_compare import verify_coverage, verify_evidence_metadata  # noqa: E402
from p3_2_target_parity import TARGET_ASSETS, fetch_source_batches  # noqa: E402
from two_layer_runner import compose_two_layer_target  # noqa: E402


GOLDEN_PATH = REPO_ROOT / "research" / "results" / "p3_2_target_parity" / "golden_v1.json"
ABS_TOL = 2e-10


def assert_close(label: str, actual: float, expected: float, *, atol: float = ABS_TOL) -> None:
    if not math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=atol):
        raise AssertionError(f"{label}: actual={actual!r}, expected={expected!r}")


def run_cap1_parity() -> dict[str, object]:
    golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    verify_evidence_metadata(golden)
    verify_coverage(golden)
    source_batches = fetch_source_batches()
    config = load_product_config()

    expected_rows = golden["full_brrk_multi_date"]
    if not isinstance(expected_rows, list) or len(expected_rows) < 6:
        raise AssertionError("Committed full-BRRK golden coverage is incomplete")

    rows: list[dict[str, object]] = []
    for expected in expected_rows:
        if not isinstance(expected, dict):
            raise AssertionError("Malformed committed full-BRRK golden row")
        decision = str(expected["decision"])
        print(f"P4 cap=1 parity decision {decision}", flush=True)
        dataset = canonicalize_research_daily_history(
            source_batches=source_batches,
            decision_timestamp=decision,
        )
        base = calculate_target(
            daily_dataset=dataset,
            account_equity_usd=10_000.0,
            current_positions={},
            approved_config=config,
        )

        two_layer = compose_two_layer_target(
            base_target_weights=base.target_weights,
            frozen_defensive_scale=base.defensive_scale,
            leverage_multiplier=1.0,
            research_cap=1.0,
        )

        # The new P4 boundary must be a literal identity at cap=1.
        if two_layer.final_target_weights != base.target_weights:
            raise AssertionError(f"cap=1 changed target weight bits at {decision}")
        assert_close(
            f"cap=1 gross identity {decision}",
            two_layer.final_gross_target,
            base.base_gross_target,
            atol=1e-15,
        )
        assert_close(
            f"cap=1 cash identity {decision}",
            two_layer.cash_or_financing_share,
            base.cash_share,
            atol=1e-15,
        )
        assert_close(
            f"cap=1 defensive identity {decision}",
            two_layer.final_scale,
            base.defensive_scale,
            atol=1e-15,
        )

        # Then independently anchor the unchanged base to committed historical evidence.
        for field, actual in {
            "gross": base.base_gross_target,
            "cash": base.cash_share,
            "riskoff_probability": base.riskoff_probability,
            "meta_scale": base.meta_scale,
            "defensive_scale": base.defensive_scale,
        }.items():
            assert_close(f"golden {field} {decision}", actual, float(expected[field]))

        expected_weights = expected["weights"]
        if not isinstance(expected_weights, dict):
            raise AssertionError("Malformed committed golden weights")
        for asset in TARGET_ASSETS:
            assert_close(
                f"golden weight {decision} {asset}",
                two_layer.final_target_weights[asset],
                float(expected_weights[asset]),
            )

        for field, actual in {
            "target_session": base.target_session,
            "regime_refit_session": base.regime_refit_session,
            "risk_state": base.risk_state,
            "data_digest": base.data_digest,
        }.items():
            if actual != expected[field]:
                raise AssertionError(
                    f"golden {field} {decision}: actual={actual!r} expected={expected[field]!r}"
                )

        rows.append(
            {
                "decision": decision,
                "target_session": base.target_session,
                "risk_state": base.risk_state,
                "defensive_scale": base.defensive_scale,
                "leverage_multiplier": 1.0,
                "final_scale": two_layer.final_scale,
                "base_gross": base.base_gross_target,
                "final_gross": two_layer.final_gross_target,
                "weights": two_layer.final_target_weights,
                "data_digest": base.data_digest,
            }
        )

    return {
        "status": "P4_3_CAP1_EXACT_HISTORICAL_PARITY_PASS",
        "experiment": "LEVERAGE-0040",
        "research_cap": 1.0,
        "leverage_multiplier": 1.0,
        "decision_count": len(rows),
        "rows": rows,
        "production_authorized": False,
        "leverage_search_run": False,
    }


def main() -> None:
    report = run_cap1_parity()
    print("=== P4_3_CAP1_PARITY ===")
    print(json.dumps(report, indent=2, sort_keys=True))
    print("=== END_P4_3_CAP1_PARITY ===")


if __name__ == "__main__":
    main()
