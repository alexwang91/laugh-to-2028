from __future__ import annotations

"""Compare the product P3.2 engine to committed historical golden vectors.

Unlike ``p3_2_target_parity.py``, this check does not calculate a fresh research
reference.  The expected values are committed evidence from the first successful
independent research-vs-product parity run, so future coordinated changes to both
implementations cannot silently move the frozen BRRK-0011 target baseline.
"""

import importlib.metadata
import json
import math
from pathlib import Path

from beta_bot.product_config import load_product_config
from beta_bot.target_engine import MODEL_AUTHORITY, TARGET_ENGINE_VERSION, calculate_target
from beta_bot.target_math import build_v1_raw
from p3_1_data_contract_adapter import canonicalize_research_daily_history
from p3_2_target_parity import TARGET_ASSETS, dataset_prices, fetch_source_batches


REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_PATH = REPO_ROOT / "research" / "results" / "p3_2_target_parity" / "golden_v1.json"
ABS_TOL = 2e-10


def assert_close(label: str, actual: float, expected: float, *, atol: float = ABS_TOL) -> None:
    if not math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=atol):
        raise AssertionError(f"{label}: actual={actual!r}, golden={expected!r}")


def verify_evidence_metadata(golden: dict[str, object]) -> None:
    source = golden["evidence_source"]
    if not isinstance(source, dict):
        raise AssertionError("Golden evidence_source must be a mapping")
    if source["target_engine_version"] != TARGET_ENGINE_VERSION:
        raise AssertionError(
            f"target engine version drift: runtime={TARGET_ENGINE_VERSION} golden={source['target_engine_version']}"
        )
    if source["model_authority"] != MODEL_AUTHORITY:
        raise AssertionError(
            f"model authority drift: runtime={MODEL_AUTHORITY} golden={source['model_authority']}"
        )

    dependency_lock = source["dependency_lock"]
    if not isinstance(dependency_lock, dict):
        raise AssertionError("Golden dependency_lock must be a mapping")
    package_names = {
        "numpy": "numpy",
        "pandas": "pandas",
        "scipy": "scipy",
        "scikit-learn": "scikit-learn",
        "hmmlearn": "hmmlearn",
    }
    for key, package_name in package_names.items():
        installed = importlib.metadata.version(package_name)
        expected = str(dependency_lock[key])
        if installed != expected:
            raise AssertionError(
                f"dependency drift for {package_name}: installed={installed} golden={expected}"
            )


def verify_early_v1(source_batches, golden: dict[str, object]) -> None:
    rows = golden["v1_only_early_history"]
    if not isinstance(rows, list):
        raise AssertionError("Golden v1_only_early_history must be a list")
    for expected in rows:
        if not isinstance(expected, dict):
            raise AssertionError("Malformed early V1 golden row")
        decision = str(expected["decision"])
        dataset = canonicalize_research_daily_history(
            source_batches=source_batches,
            decision_timestamp=decision,
        )
        prices = dataset_prices(dataset)
        product_v1, _ = build_v1_raw(prices)
        latest = prices.index[-1]
        actual_session = latest.strftime("%Y-%m-%d")
        if actual_session != expected["session"]:
            raise AssertionError(
                f"early V1 session {decision}: actual={actual_session} golden={expected['session']}"
            )
        actual_weights = {
            asset: float(product_v1.loc[latest, asset]) for asset in TARGET_ASSETS
        }
        expected_weights = expected["weights"]
        if not isinstance(expected_weights, dict):
            raise AssertionError("Malformed early V1 golden weights")
        for asset in TARGET_ASSETS:
            assert_close(
                f"early V1 {decision} {asset}",
                actual_weights[asset],
                float(expected_weights[asset]),
                atol=1e-12,
            )
        assert_close(
            f"early V1 gross {decision}",
            sum(actual_weights.values()),
            float(expected["gross"]),
            atol=1e-12,
        )


def verify_full_brrk(source_batches, golden: dict[str, object]) -> None:
    rows = golden["full_brrk_multi_date"]
    if not isinstance(rows, list):
        raise AssertionError("Golden full_brrk_multi_date must be a list")
    config = load_product_config()
    for expected in rows:
        if not isinstance(expected, dict):
            raise AssertionError("Malformed full BRRK golden row")
        decision = str(expected["decision"])
        print(f"golden decision {decision}", flush=True)
        dataset = canonicalize_research_daily_history(
            source_batches=source_batches,
            decision_timestamp=decision,
        )
        product = calculate_target(
            daily_dataset=dataset,
            account_equity_usd=10_000.0,
            current_positions={},
            approved_config=config,
        )

        exact_fields = {
            "target_session": product.target_session,
            "regime_refit_session": product.regime_refit_session,
            "risk_state": product.risk_state,
            "data_digest": product.data_digest,
        }
        for field, actual in exact_fields.items():
            if actual != expected[field]:
                raise AssertionError(
                    f"{field} {decision}: actual={actual!r} golden={expected[field]!r}"
                )

        numeric_fields = {
            "gross": product.base_gross_target,
            "cash": product.cash_share,
            "riskoff_probability": product.riskoff_probability,
            "meta_scale": product.meta_scale,
            "defensive_scale": product.defensive_scale,
        }
        for field, actual in numeric_fields.items():
            assert_close(f"{field} {decision}", actual, float(expected[field]))

        expected_weights = expected["weights"]
        if not isinstance(expected_weights, dict):
            raise AssertionError("Malformed full BRRK golden weights")
        for asset in TARGET_ASSETS:
            assert_close(
                f"weight {decision} {asset}",
                product.target_weights[asset],
                float(expected_weights[asset]),
            )


def verify_coverage(golden: dict[str, object]) -> None:
    coverage = golden["coverage"]
    if not isinstance(coverage, dict):
        raise AssertionError("Golden coverage must be a mapping")
    expected_states = {"RISK_OFF", "BTC_LEAD", "MAJOR_ROTATION", "ALT_EXPANSION"}
    observed = set(coverage["risk_states_observed"])
    if observed != expected_states:
        raise AssertionError(f"Golden state coverage incomplete: {sorted(observed)}")
    if int(coverage["full_brrk_decision_count"]) < 6:
        raise AssertionError("Golden full BRRK coverage unexpectedly shrank")
    if int(coverage["early_v1_decision_count"]) < 2:
        raise AssertionError("Golden early V1 coverage unexpectedly shrank")
    if float(coverage["min_defensive_scale"]) >= 0.01:
        raise AssertionError("Golden set no longer proves near-flat defensive exposure")
    if float(coverage["max_defensive_scale"]) <= 0.99:
        raise AssertionError("Golden set no longer proves near-full defensive exposure")


def main() -> None:
    golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    verify_evidence_metadata(golden)
    verify_coverage(golden)
    source_batches = fetch_source_batches()
    verify_early_v1(source_batches, golden)
    verify_full_brrk(source_batches, golden)
    print("P3_2_COMMITTED_GOLDEN_PASS")


if __name__ == "__main__":
    main()
