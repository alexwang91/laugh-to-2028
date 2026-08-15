from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from research.brrk_beta_handoff_0047.engine import frames_from_market_evidence
from research.brrk_idle_cash_passive_accrual_robustness_0064 import engine as cash_engine
from research.brrk_btc_sol_path_event_early_warning_runtime_qualified_0067 import engine

RID = "BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-RUNTIME-QUALIFIED-0067"
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MARKET = ROOT / "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json"
EQUITY = ROOT / "research/results/pit_disp_0015/daily_equity.csv"
WEIGHTS = ROOT / "research/results/pit_disp_0015/daily_weights.csv"
DTB3 = ROOT / "research/brrk_idle_cash_sweep_robustness_0063/DTB3_RAW.csv"
ATTEMPT = HERE / "RUN_ATTEMPT.marker"
RESULT = HERE / "PRIMARY_RESULT.json"
EVIDENCE = HERE / "EVIDENCE.json"
EXECUTION = HERE / "EXECUTION.json"
FINAL = HERE / "RUN_ONCE.marker"

RUN_INTERFACE_BLOB = "ff0e835468fef04e3a0b62ac5cc2fabfcfff1c38"
RESULT_SCHEMA_BLOB = "d9846be31acb7c894662555f50b1ebc74ceca699"
BOUNDARY_DECLARATION_BLOB = "0583584e4a7ec94e294109d69cbf839894f87689"
QUALIFICATION_RESULT_BLOB = "6409a558c0c800f363699c67fe28b39faf8f3bff"
PINNED_BLOBS = {
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/RUN_INTERFACE.json": RUN_INTERFACE_BLOB,
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/RESULT_SCHEMA.json": RESULT_SCHEMA_BLOB,
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/CONTROLLED_EXECUTION_BOUNDARY.json": BOUNDARY_DECLARATION_BLOB,
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/QUALIFICATION_RESULT.json": QUALIFICATION_RESULT_BLOB,
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/PREREGISTRATION.json": "398e4a238229282582bbdbe4eed944d779c51ab3",
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/DATASET_DECLARATION.json": "4cbf84841a07c97dbd62bb6639c198e7bbba6128",
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/QUALIFICATION_PREREGISTRATION.json": "4ec87ce4604ec526a0043d48882568bad102b3f3",
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/IMPLEMENTATION_CONTRACT.json": "34c858c1672149a2a89a6554348ba69f75234eeb",
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/engine.py": "482868d45ccdeaa5fbad8033f122a8fcfde79ca6",
    "research/brrk_btc_sol_path_event_early_warning_0066/engine.py": "79320c83d0ce89c2c952fd0a4f7a9b7452a8e0ae",
    "research/brrk_btc_sol_path_event_early_warning_0066/event_engine.py": "651ebb824b9dc1390ed0170a4eab07a3870786aa",
    "research/brrk_btc_sol_path_event_early_warning_0066/models.py": "6b255b887f2cd8f1741086a7bf27e6254288e836",
    "research/brrk_btc_risk_signal_atlas_0062/engine.py": "cac8e946998c836d10842b9388e1e3ef345a8c0b",
    "research/brrk_beta_handoff_0047/engine.py": "059b55961e279dab41ba29b5b017de0922e4f33c",
    "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json": "64ebf5c6deaf3f34dbeac715378f196ff0f4fafe",
    "research/results/pit_disp_0015/daily_equity.csv": "82c87f8cb0ff01c728ffd3b717fff17cf5a364f2",
    "research/results/pit_disp_0015/daily_weights.csv": "2f6c8d3a8c25d3cafeaa0128f1c425dac248370b",
    "research/brrk_idle_cash_sweep_robustness_0063/DTB3_RAW.csv": "71d50e26f8a9afb6bcb88401d20b97d5fb0a891a",
    "research/brrk_idle_cash_passive_accrual_robustness_0064/engine.py": "4060a307be2204c11952cb52e2fc718a5343d8e1",
    "execution/plan-b-bot/requirements.txt": "c48550e67350bdc1e640ac8eb5e2ea02986ad83a",
    "execution/plan-b-bot/requirements-dev.txt": "df60fe952f573fc6201b16b9de6b6043fbe7dbe2",
}
MARKET_PAYLOAD_SHA256 = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"
DTB3_SHA256 = "4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879"
EXPECTED_PORTFOLIO_START = pd.Timestamp("2022-12-10")
EXPECTED_PORTFOLIO_END = pd.Timestamp("2026-08-02")
EXPECTED_PORTFOLIO_N = 1332


class ControlledRunError(RuntimeError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def _create_only(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, text=True).strip()


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _verify_pinned_blobs() -> None:
    bad = []
    for path, expected in PINNED_BLOBS.items():
        actual = _git_blob(path)
        if actual != expected:
            bad.append({"path": path, "expected": expected, "actual": actual})
    if bad:
        raise ControlledRunError(f"pinned blob identity mismatch: {bad}")


def _load_schema() -> dict:
    schema = json.loads((HERE / "RESULT_SCHEMA.json").read_text(encoding="utf-8"))
    if schema.get("research_id") != RID:
        raise ControlledRunError("result schema identity mismatch")
    return schema


def _runtime_existing() -> list[str]:
    return [p.name for p in (ATTEMPT, RESULT, EVIDENCE, EXECUTION, FINAL) if p.exists()]


def preflight(boundary_sha: str) -> dict:
    if _git_head() != boundary_sha:
        raise ControlledRunError("preflight must run on exact merged boundary HEAD")
    _verify_pinned_blobs()
    existing = _runtime_existing()
    if existing:
        raise ControlledRunError(f"preflight requires zero-result state; found {existing}")
    return {
        "research_id": RID,
        "status": "PREFLIGHT_PASS_ZERO_RESULT_GIT_IDENTITY_ONLY",
        "boundary_sha": boundary_sha,
        "qualification_result_blob": QUALIFICATION_RESULT_BLOB,
        "historical_content_reads": {"market_evidence": 0, "equity": 0, "weights": 0, "dtb3": 0},
        "market_loader_calls": 0,
        "scientific_engine_calls": 0,
        "runtime_artifacts_present": [],
    }


def start_attempt(boundary_sha: str, workflow_run_id: str) -> dict:
    if _git_head() != boundary_sha:
        raise ControlledRunError("attempt must start from exact merged boundary HEAD")
    _verify_pinned_blobs()
    if _runtime_existing():
        raise ControlledRunError("attempt/result artifact already exists; same-ID start forbidden")
    marker = {
        "schema_version": 1,
        "research_id": RID,
        "attempt_number": 1,
        "boundary_merge_sha": boundary_sha,
        "workflow_run_id": str(workflow_run_id),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "qualification_result_blob": QUALIFICATION_RESULT_BLOB,
        "declared_indicator_atlas_hypothesis_cells": 8080,
        "declared_validation_tuning_configs": 1632,
        "declared_final_predictor_tracks": 64,
        "declared_final_controllers": 8,
        "declared_model_controller_variants": 1704,
        "declared_validation_estimator_fit_calls": 31008,
        "declared_economic_estimator_fit_calls": 11904,
        "declared_total_estimator_fit_calls": 42912,
        "declared_stacking_nnls_solves": 40,
        "declared_process_worker_count": 4,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
    }
    _create_only(ATTEMPT, _json_bytes(marker))
    return marker


def _read_input_once(path: Path, counts: dict[str, int], key: str) -> bytes:
    if counts[key] != 0:
        raise ControlledRunError(f"input {key} attempted more than once")
    data = path.read_bytes()
    counts[key] += 1
    return data


def _parse_market(data: bytes) -> dict[str, pd.DataFrame]:
    evidence = json.loads(data.decode("utf-8"))
    if evidence.get("payload_sha256") != MARKET_PAYLOAD_SHA256:
        raise ControlledRunError("market evidence payload SHA256 mismatch")
    return frames_from_market_evidence(evidence)


def _parse_equity(data: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(data), parse_dates=["date"])
    if "BRRK0011_BASELINE" not in df.columns:
        raise ControlledRunError("missing BRRK0011_BASELINE equity column")
    return df.set_index("date")


def _parse_weights(data: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(data), parse_dates=["date"]).set_index("date")
    cols = [c for c in df.columns if c.startswith("BRRK0011_BASELINE__")]
    if not cols:
        raise ControlledRunError("missing BRRK0011_BASELINE weight columns")
    return df[cols]


def _parse_dtb3(data: bytes) -> pd.DataFrame:
    if _sha256_bytes(data) != DTB3_SHA256:
        raise ControlledRunError("DTB3 payload SHA256 mismatch")
    df = pd.read_csv(io.BytesIO(data), parse_dates=["observation_date"])
    if list(df.columns) != ["observation_date", "DTB3"]:
        raise ControlledRunError("unexpected DTB3 schema")
    df["DTB3"] = pd.to_numeric(df["DTB3"], errors="coerce")
    return df.dropna(subset=["DTB3"]).set_index("observation_date")


def _prepare_portfolio_inputs(
    equity: pd.DataFrame,
    weights: pd.DataFrame,
    rates: pd.DataFrame,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    idx = equity.index
    if (
        len(idx) != EXPECTED_PORTFOLIO_N
        or idx[0] != EXPECTED_PORTFOLIO_START
        or idx[-1] != EXPECTED_PORTFOLIO_END
        or not weights.index.equals(idx)
    ):
        raise ControlledRunError("frozen BRRK portfolio support mismatch")
    eq = pd.to_numeric(equity["BRRK0011_BASELINE"], errors="coerce").to_numpy(dtype=float)
    w = weights.astype(float).to_numpy()
    if not np.isfinite(eq).all() or not np.isfinite(w).all():
        raise ControlledRunError("non-finite equity/weights")
    baseline_returns = cash_engine.reconstruct_returns(eq, 10000.0)
    gross = cash_engine.gross_from_weights(w)
    if float(np.max(gross)) > 1.000001:
        raise ControlledRunError("baseline gross exceeds frozen cap")
    aligned_percent = cash_engine.causal_align_rates(idx, rates.index, rates["DTB3"].to_numpy(dtype=float))
    rf_daily = cash_engine.dtb3_percent_to_daily_return(aligned_percent)
    return (
        pd.Series(baseline_returns, index=idx, name="baseline_return"),
        pd.Series(gross, index=idx, name="baseline_gross"),
        pd.Series(rf_daily, index=idx, name="rf_daily"),
    )


def _validate_primary(primary: dict, schema: dict) -> None:
    if primary.get("research_id") != RID:
        raise ControlledRunError("primary research identity mismatch")
    classification = primary.get("classification")
    if classification not in schema["classification_enum"]:
        raise ControlledRunError("classification outside frozen enum")
    missing = [x for x in schema["required_primary_fields"] if x not in primary]
    if missing:
        raise ControlledRunError(f"primary result missing fields: {missing}")
    if classification != "INVALID_EXECUTION":
        counts = schema["frozen_counts"]
        if primary.get("indicator_atlas_hypothesis_cells") != counts["indicator_atlas_hypothesis_cells"]:
            raise ControlledRunError("indicator-atlas count drift")
        if primary.get("actual_validation_tuning_configs_evaluated") != counts["validation_tuning_configs"]:
            raise ControlledRunError("validation tuning accounting drift")
        if primary.get("final_predictor_track_count") != counts["final_predictor_tracks"]:
            raise ControlledRunError("final predictor count drift")
        if primary.get("final_controller_count") != counts["final_controllers"]:
            raise ControlledRunError("controller count drift")
        if primary.get("actual_variants_evaluated") != counts["actual_variants_if_complete"]:
            raise ControlledRunError("variant accounting drift")
    if (
        primary.get("production_authorized") is not False
        or primary.get("signature_authorized") is not False
        or primary.get("order_submission_authorized") is not False
    ):
        raise ControlledRunError("illegal authority in primary result")


def _validate_runtime_evidence(evidence: dict, schema: dict) -> None:
    runtime = evidence.get("0067_runtime_accounting")
    if not isinstance(runtime, dict):
        raise ControlledRunError("missing 0067 runtime accounting evidence")
    frozen = schema["frozen_physical_compute"]
    checks = {
        "validation_fit_call_attempts": frozen["validation_estimator_fit_calls"],
        "economic_fit_call_attempts": frozen["economic_estimator_fit_calls"],
        "total_fit_call_attempts": frozen["total_estimator_fit_calls"],
        "stacking_nnls_solves": frozen["stacking_nnls_solves"],
        "worker_count": frozen["process_worker_count"],
    }
    bad = {k: {"expected": v, "actual": runtime.get(k)} for k, v in checks.items() if runtime.get(k) != v}
    if bad:
        raise ControlledRunError(f"physical compute accounting drift: {bad}")


def _invalid_result(
    stage: str,
    exc: Exception,
    counts: dict[str, int],
    loader_calls: int,
    engine_calls: int,
) -> tuple[dict, dict]:
    primary = {
        "schema_version": 1,
        "research_id": RID,
        "classification": "INVALID_EXECUTION",
        "event_onset_count": None,
        "event_counts_by_asset_type_grade": {},
        "indicator_atlas_hypothesis_cells": 8080,
        "indicator_atlas_supported_holm_family_size": 0,
        "indicator_atlas_holm_rejections": 0,
        "actual_validation_tuning_configs_evaluated": None,
        "final_predictor_track_count": 64,
        "final_controller_count": 8,
        "actual_variants_evaluated": None,
        "predictor_tracks": {},
        "predictive_winners": [],
        "predictor_simultaneous_bootstrap": {
            "block_length": 60,
            "replicates": 4000,
            "seed": 660066,
            "q95": None,
        },
        "benchmark_0064_same_window": {},
        "controllers": {},
        "economic_simultaneous_bootstrap": {
            "block_length": 60,
            "replicates": 4000,
            "seed": 660066,
            "q95": None,
        },
        "PBO_CSCV": {"status": "NOT_EVALUATED"},
        "controller_error": {
            "failure_stage": stage,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        },
        "validation_preferred_horizons": {},
        "validation_preferred_architectures": {},
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    evidence = {
        "failure_stage": stage,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "input_read_counts": dict(counts),
        "market_loader_calls": int(loader_calls),
        "scientific_engine_calls": int(engine_calls),
        "same_id_recomputation_allowed": False,
    }
    return primary, evidence


def evaluate(boundary_sha: str) -> dict:
    if _git_head() != boundary_sha:
        raise ControlledRunError("evaluation must run on exact merged boundary HEAD")
    if not ATTEMPT.exists():
        raise ControlledRunError("durable RUN_ATTEMPT.marker required before evaluation")
    if FINAL.exists():
        raise ControlledRunError("final marker exists; same-ID evaluation permanently closed")
    if any(p.exists() for p in (RESULT, EVIDENCE, EXECUTION)):
        raise ControlledRunError("partial result exists; automatic recomputation forbidden")
    _verify_pinned_blobs()
    marker = json.loads(ATTEMPT.read_text(encoding="utf-8"))
    if (
        marker.get("research_id") != RID
        or marker.get("attempt_number") != 1
        or marker.get("boundary_merge_sha") != boundary_sha
    ):
        raise ControlledRunError("attempt marker identity mismatch")

    counts = {"market_evidence": 0, "equity": 0, "weights": 0, "dtb3": 0}
    loader_calls = 0
    engine_calls = 0
    stage = "historical_input_loading"
    try:
        market_bytes = _read_input_once(MARKET, counts, "market_evidence")
        equity_bytes = _read_input_once(EQUITY, counts, "equity")
        weights_bytes = _read_input_once(WEIGHTS, counts, "weights")
        dtb3_bytes = _read_input_once(DTB3, counts, "dtb3")

        stage = "market_loader"
        frames = _parse_market(market_bytes)
        loader_calls = 1
        stage = "portfolio_input_preparation"
        equity = _parse_equity(equity_bytes)
        weights = _parse_weights(weights_bytes)
        rates = _parse_dtb3(dtb3_bytes)
        baseline_returns, baseline_gross, rf_daily = _prepare_portfolio_inputs(equity, weights, rates)

        stage = "scientific_engine"
        engine_calls = 1
        out = engine.evaluate_program(
            frames,
            baseline_returns,
            baseline_gross,
            rf_daily,
            bootstrap_replicates=4000,
        )
        primary = out["primary_result"]
        evidence = out["evidence"]
        stage = "result_validation"
        schema = _load_schema()
        _validate_primary(primary, schema)
        _validate_runtime_evidence(evidence, schema)
    except Exception as exc:
        primary, evidence = _invalid_result(stage, exc, counts, loader_calls, engine_calls)
        _validate_primary(primary, _load_schema())

    result_bytes = _json_bytes(primary)
    evidence_bytes = _json_bytes(evidence)
    _create_only(RESULT, result_bytes)
    _create_only(EVIDENCE, evidence_bytes)
    execution = {
        "schema_version": 1,
        "research_id": RID,
        "attempt_number": 1,
        "boundary_merge_sha": boundary_sha,
        "qualification_result_blob": QUALIFICATION_RESULT_BLOB,
        "attempt_sha256": _sha256_file(ATTEMPT),
        "primary_result_sha256": _sha256_bytes(result_bytes),
        "evidence_sha256": _sha256_bytes(evidence_bytes),
        "input_read_counts": dict(counts),
        "market_loader_calls": int(loader_calls),
        "scientific_engine_calls": int(engine_calls),
        "network_fetches": 0,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _create_only(EXECUTION, _json_bytes(execution))
    return {"primary_result": primary, "execution": execution}


def finalize(boundary_sha: str) -> dict:
    if _git_head() != boundary_sha:
        raise ControlledRunError("finalize must run on exact merged boundary HEAD")
    _verify_pinned_blobs()
    if FINAL.exists():
        raise ControlledRunError("RUN_ONCE.marker already exists")
    if not all(p.exists() for p in (ATTEMPT, RESULT, EVIDENCE, EXECUTION)):
        raise ControlledRunError("marker-only finalize requires complete attempt/result/evidence/execution bundle")
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    if execution.get("boundary_merge_sha") != boundary_sha:
        raise ControlledRunError("execution boundary identity mismatch")
    if execution.get("attempt_sha256") != _sha256_file(ATTEMPT):
        raise ControlledRunError("attempt hash mismatch")
    if execution.get("primary_result_sha256") != _sha256_file(RESULT):
        raise ControlledRunError("primary result hash mismatch")
    if execution.get("evidence_sha256") != _sha256_file(EVIDENCE):
        raise ControlledRunError("evidence hash mismatch")
    primary = json.loads(RESULT.read_text(encoding="utf-8"))
    _validate_primary(primary, _load_schema())
    marker = {
        "schema_version": 1,
        "research_id": RID,
        "attempt_number": 1,
        "boundary_merge_sha": boundary_sha,
        "status": "VALID_OR_INVALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        "classification": primary.get("classification"),
        "qualification_result_blob": QUALIFICATION_RESULT_BLOB,
        "attempt_sha256": _sha256_file(ATTEMPT),
        "primary_result_sha256": _sha256_file(RESULT),
        "evidence_sha256": _sha256_file(EVIDENCE),
        "execution_sha256": _sha256_file(EXECUTION),
        "historical_content_reads_during_finalize": 0,
        "market_loader_calls_during_finalize": 0,
        "scientific_engine_calls_during_finalize": 0,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _create_only(FINAL, _json_bytes(marker))
    return marker


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "evaluate", "finalize"):
        p = sub.add_parser(name)
        p.add_argument("--boundary-sha", required=True)
    p = sub.add_parser("start")
    p.add_argument("--boundary-sha", required=True)
    p.add_argument("--workflow-run-id", required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        out = preflight(args.boundary_sha)
    elif args.command == "start":
        out = start_attempt(args.boundary_sha, args.workflow_run_id)
    elif args.command == "evaluate":
        out = evaluate(args.boundary_sha)
    else:
        out = finalize(args.boundary_sha)
    print(json.dumps(out, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
