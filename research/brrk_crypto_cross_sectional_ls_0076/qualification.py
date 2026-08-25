"""Synthetic-only Stage5 qualification for BRRK-CRYPTO-CROSS-SECTIONAL-LS-0076.

This module must never open repository files, controlled historical payloads, or
network resources. It exercises frozen Stage4 mechanics using in-memory synthetic
objects only. It does not consume the Stage8 attempt or controlled-read budget.
"""
from __future__ import annotations

import hashlib
import io
import zipfile
from datetime import date, datetime, timezone

from research.brrk_crypto_cross_sectional_ls_0076.engine import (
    EconomicMetrics,
    ExecutionContext,
    ExecutionInvalid,
    PathState,
    ReadLedger,
    create_only_result_objects,
    evaluate_gates,
    run_scientific_engine,
)

PASS = "PASS_CROSS_SECTIONAL_MOMENTUM_LS_BASELINE"
FAIL = "FAIL_NO_ROBUST_CROSS_SECTIONAL_MOMENTUM_LS_ECONOMICS"
INCONCLUSIVE = "INCONCLUSIVE_INSUFFICIENT_SUPPORT"
INVALID = "INVALID_EXECUTION"


def _zip(name: str, text: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(name, text)
    return buf.getvalue()


def _minimal_payloads() -> tuple[dict[str, bytes], dict[str, str]]:
    ts = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    kpath = "data/futures/um/monthly/klines/AAAUSDT/1d/AAAUSDT-1d-2026-01.zip"
    fpath = "data/futures/um/monthly/fundingRate/AAAUSDT/AAAUSDT-fundingRate-2026-01.zip"
    k = _zip(
        "AAAUSDT-1d-2026-01.csv",
        f"{ts},1,2,0.5,1.5,10,{ts + 86399999},2000000,1,1,1,0\n",
    )
    f = _zip(
        "AAAUSDT-fundingRate-2026-01.csv",
        f"calc_time,funding_interval_hours,last_funding_rate\n{ts},8,0.0001\n",
    )
    payloads = {kpath: k, fpath: f}
    hashes = {path: hashlib.sha256(payload).hexdigest() for path, payload in payloads.items()}
    return payloads, hashes


def _metrics(*, cagr: float, sharpe: float, max_drawdown: float = -0.10, worst_7d: float = -0.05) -> EconomicMetrics:
    return EconomicMetrics(
        observations=800,
        cumulative_return=0.50 if cagr > 0 else -0.20,
        cagr=cagr,
        annualized_volatility=0.20,
        sharpe=sharpe,
        sortino=max(sharpe, 0.0),
        max_drawdown=max_drawdown,
        calmar=(cagr / abs(max_drawdown)) if max_drawdown < 0 else 0.0,
        worst_1d=-0.02,
        worst_5d=-0.04,
        worst_7d=worst_7d,
        worst_10d=-0.08,
        worst_20d=-0.10,
        expected_shortfall_5pct=-0.02,
    )


def _gate_fixture(*, pass_case: bool) -> dict[str, bool]:
    c1m = _metrics(cagr=0.30 if pass_case else -0.05, sharpe=1.25 if pass_case else -0.25)
    c2m = _metrics(cagr=0.20 if pass_case else -0.10, sharpe=0.80 if pass_case else -0.40)
    inference = {
        "bootstrap": {"one_sided_b": 0.001 if pass_case else 0.50, "mean_ci_low": 0.001 if pass_case else -0.01},
        "psr": 0.99 if pass_case else 0.50,
        "dsr_one_trial": 0.99 if pass_case else 0.50,
    }
    years = {
        "2023": {"weeks": 20, "cumulative_return": 0.10 if pass_case else -0.05, "sharpe": 1.0},
        "2024": {"weeks": 20, "cumulative_return": 0.12 if pass_case else -0.03, "sharpe": 1.1},
        "2025": {"weeks": 20, "cumulative_return": 0.15 if pass_case else -0.02, "sharpe": 1.2},
    }
    robustness = {
        "years": years,
        "bull": {"weeks": 30, "cumulative_return": 0.10 if pass_case else -0.01},
        "bear": {"weeks": 30, "cumulative_return": 0.08 if pass_case else -0.02},
        "leave_one_year_out": {
            "2023": {"cumulative_return": 0.20 if pass_case else -0.10, "sharpe": 1.0},
            "2024": {"cumulative_return": 0.18 if pass_case else -0.10, "sharpe": 1.0},
            "2025": {"cumulative_return": 0.16 if pass_case else -0.10, "sharpe": 1.0},
        },
    }
    capacity = {
        "participation_p95": 0.005 if pass_case else 0.02,
        "participation_max": 0.01 if pass_case else 0.10,
        "max_abs_asset_contribution_share": 0.20 if pass_case else 0.60,
        "remove_largest_contributor_cumulative_return": 0.15 if pass_case else -0.05,
    }
    state = PathState(
        gross_exposure=[1.0, 1.0],
        net_exposure=[0.0, 0.0],
        residual_beta=[0.0, 0.0],
    )
    weekly_meta = [
        {
            "date": date(2026, 1, 5),
            "supported": True,
            "target_net": 0.0,
            "target_beta": 0.0,
            "target_max_abs_weight": 0.10,
        }
    ]
    return evaluate_gates(
        c1m,
        c2m,
        inference,
        robustness,
        capacity,
        state,
        weekly_meta,
        3.0 if pass_case else 0.5,
        True,
    )


def run_qualification() -> None:
    # Terminal gate mechanics: an all-green frozen G0-G11 vector maps to PASS;
    # any failed gate maps to the frozen FAIL terminal vocabulary.
    pass_gates = _gate_fixture(pass_case=True)
    assert set(pass_gates) == {f"G{i}" for i in range(12)}
    assert all(pass_gates.values())
    assert (PASS if all(pass_gates.values()) else FAIL) == PASS

    fail_gates = _gate_fixture(pass_case=False)
    assert not all(fail_gates.values())
    assert (PASS if all(fail_gates.values()) else FAIL) == FAIL

    # Full frozen entrypoint on deliberately insufficient in-memory support.
    payloads, hashes = _minimal_payloads()
    ctx = ExecutionContext()
    inconclusive = run_scientific_engine(payloads, hashes, context=ctx)
    assert inconclusive.classification == INCONCLUSIVE
    assert inconclusive.execution_valid is True
    assert inconclusive.execution["scientific_engine_calls"] == 1
    assert inconclusive.execution["controlled_object_reads"] == 2
    assert inconclusive.execution["max_reads_per_object"] == 1
    assert inconclusive.execution["scientific_source_network_fetches"] == 0

    # Canonical serialization is deterministic and create-only.
    first = create_only_result_objects(inconclusive, ())
    second = create_only_result_objects(inconclusive, ())
    assert first == second
    assert set(first) == {"PRIMARY_RESULT.json", "EVIDENCE.json", "EXECUTION.json"}
    assert all(blob.endswith(b"\n") for blob in first.values())
    try:
        create_only_result_objects(inconclusive, ("PRIMARY_RESULT.json",))
    except FileExistsError:
        pass
    else:
        raise AssertionError("create-only collision must fail closed")

    # Hash mismatch reaches INVALID through the full frozen entrypoint.
    bad_ctx = ExecutionContext()
    bad_hashes = dict(hashes)
    first_path = sorted(bad_hashes)[0]
    bad_hashes[first_path] = "0" * 64
    invalid = run_scientific_engine(payloads, bad_hashes, context=bad_ctx)
    assert invalid.classification == INVALID
    assert invalid.execution_valid is False
    assert invalid.execution["scientific_engine_calls"] == 1
    assert invalid.execution["scientific_source_network_fetches"] == 0

    # Ledger rejects unauthorized and duplicate identities without external I/O.
    sample_path = sorted(payloads)[0]
    sample = payloads[sample_path]
    ledger = ReadLedger({sample_path: hashlib.sha256(sample).hexdigest()})
    ledger.consume(sample_path, sample)
    try:
        ledger.consume(sample_path, sample)
    except ExecutionInvalid:
        pass
    else:
        raise AssertionError("duplicate object consumption must fail closed")
    try:
        ReadLedger({}).consume(sample_path, sample)
    except ExecutionInvalid:
        pass
    else:
        raise AssertionError("unauthorized object consumption must fail closed")

    # A second engine call on one context must fail closed and cannot become a rescue.
    try:
        run_scientific_engine({}, {}, context=ctx)
    except ExecutionInvalid:
        pass
    else:
        raise AssertionError("second scientific engine call must be rejected")


if __name__ == "__main__":
    run_qualification()
    print("0076_STAGE5_NONHISTORICAL_QUALIFICATION_PASS")
