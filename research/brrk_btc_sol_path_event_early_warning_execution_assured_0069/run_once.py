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
from research.brrk_btc_sol_path_event_early_warning_execution_assured_0069 import engine

RID = "BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-EXECUTION-ASSURED-0069"
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

RUN_INTERFACE_BLOB = "fc4f8daa73c59ceda14c94109ae073a027c9fa68"
RESULT_SCHEMA_BLOB = "fb140a06bbf63bf9a543faa51d3d6907ffc5cb62"
BOUNDARY_DECLARATION_BLOB = "a0327af4549bc1823364fd0f64726a61ac60dc0e"
QUALIFICATION_RESULT_BLOB = "6a652faf66db4ef96edae4e3857e285816ca61da"
PINNED_BLOBS = {
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/RUN_INTERFACE.json": RUN_INTERFACE_BLOB,
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/RESULT_SCHEMA.json": RESULT_SCHEMA_BLOB,
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/CONTROLLED_EXECUTION_BOUNDARY.json": BOUNDARY_DECLARATION_BLOB,
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/QUALIFICATION_RESULT.json": QUALIFICATION_RESULT_BLOB,
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/PREREGISTRATION.json": "0aa4153f2058a556760001d1e80c0487432c47a2",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/DATASET_DECLARATION.json": "6d07f9e9b4c001fa4f65a9b9fbd919f4199c9a7a",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/QUALIFICATION_PREREGISTRATION.json": "eb6d731a1d652befba534d7210c8f4d188a16dd6",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/IMPLEMENTATION_CONTRACT.md": "326c03b6fa1ca46b6ad7b2c5edb941a81a6aea21",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/engine.py": "a5b85b386775b02fc8ad4ed3fd598f97d2284011",
    "research/brrk_btc_sol_path_event_execution_equivalence_0068/execution_graph.py": "56e910f787d96d572c570661359fc7005529925f",
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/PREREGISTRATION.json": "398e4a238229282582bbdbe4eed944d779c51ab3",
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
        raise ControlledRunError("attempt must start on exact merged boundary HEAD")
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
        "validation_estimator_fit_calls_structural": 31008,
        "economic_estimator_fit_calls": "manifest-derived",
        "p08_nnls_solves": "manifest-derived",
        "declared_process_worker_count": 4,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
    }
    _create_only(ATTEMPT, _json_bytes(marker))
    return marker


def _read_once(path: Path, counts: dict[str, int], key: str) -> bytes:
    if counts[key] != 0:
        raise ControlledRunError(f"historical input {key} attempted more than once")
    data = path.read_bytes()
    counts[key] += 1
    return data


def _parse_market(data: bytes, counts: dict[str, int]) -> dict[str, pd.DataFrame]:
    evidence = json.loads(data.decode("utf-8"))
    if evidence.get("payload_sha256") != MARKET_PAYLOAD_SHA256:
        raise ControlledRunError("market evidence payload SHA256 mismatch")
    if counts["market_loader_calls"] != 0:
        raise ControlledRunError("market loader attempted more than once")
    frames = frames_from_market_evidence(evidence)
    counts["market_loader_calls"] += 1
    return frames


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


def _portfolio_inputs(equity: pd.DataFrame, weights: pd.DataFrame, rates: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    idx = equity.index
    if len(idx) != EXPECTED_PORTFOLIO_N or idx[0] != EXPECTED_PORTFOLIO_START or idx[-1] != EXPECTED_PORTFOLIO_END or not weights.index.equals(idx):
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
    return pd.Series(baseline_returns, index=idx), pd.Series(gross, index=idx), pd.Series(rf_daily, index=idx)


def _invalid_primary(exc: Exception) -> dict:
    return {
        "schema_version": 1,
        "research_id": RID,
        "classification": "INVALID_EXECUTION",
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "predictive_summary": {},
        "controller_summary": {},
        "economic_summary": {},
        "selection_risk": {},
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def evaluate(boundary_sha: str) -> dict:
    if _git_head() != boundary_sha:
        raise ControlledRunError("evaluate must run on exact merged boundary HEAD")
    _verify_pinned_blobs()
    if not ATTEMPT.exists():
        raise ControlledRunError("durable RUN_ATTEMPT.marker required before historical read")
    if any(p.exists() for p in (RESULT, EVIDENCE, EXECUTION, FINAL)):
        raise ControlledRunError("result/final artifact already exists; same-ID evaluation forbidden")
    marker = json.loads(ATTEMPT.read_text(encoding="utf-8"))
    if marker.get("research_id") != RID or marker.get("boundary_merge_sha") != boundary_sha or marker.get("attempt_number") != 1:
        raise ControlledRunError("RUN_ATTEMPT identity mismatch")

    counts = {"market_evidence": 0, "equity": 0, "weights": 0, "dtb3": 0, "market_loader_calls": 0, "scientific_engine_calls": 0, "network_fetches": 0}
    primary = None
    evidence = None
    failure = None
    try:
        market_b = _read_once(MARKET, counts, "market_evidence")
        equity_b = _read_once(EQUITY, counts, "equity")
        weights_b = _read_once(WEIGHTS, counts, "weights")
        dtb3_b = _read_once(DTB3, counts, "dtb3")
        frames = _parse_market(market_b, counts)
        equity = _parse_equity(equity_b)
        weights = _parse_weights(weights_b)
        rates = _parse_dtb3(dtb3_b)
        baseline_returns, baseline_gross, rf_daily = _portfolio_inputs(equity, weights, rates)
        if counts["scientific_engine_calls"] != 0:
            raise ControlledRunError("scientific engine attempted more than once")
        counts["scientific_engine_calls"] += 1
        out = engine.evaluate_program(frames, baseline_returns, baseline_gross, rf_daily, bootstrap_replicates=4000)
        primary = out["primary_result"]
        evidence = out["evidence"]
        if primary.get("research_id") != RID:
            raise ControlledRunError("primary research identity mismatch")
        assurance = evidence.get("0069_execution_assurance")
        if not isinstance(assurance, dict):
            raise ControlledRunError("missing 0069 execution assurance")
        if assurance.get("validation_fit_calls_expected") != 31008 or assurance.get("validation_fit_calls_observed") != 31008:
            raise ControlledRunError("validation physical accounting mismatch")
        if assurance.get("economic_fit_calls_expected_manifest_derived") != assurance.get("economic_fit_calls_observed"):
            raise ControlledRunError("economic physical accounting mismatch")
        if assurance.get("p08_nnls_expected_manifest_derived") != assurance.get("p08_nnls_observed"):
            raise ControlledRunError("P08 NNLS physical accounting mismatch")
        if assurance.get("terminal_trace_count") != assurance.get("manifest_unit_count") or assurance.get("terminal_trace_complete") is not True:
            raise ControlledRunError("terminal trace mismatch")
        if assurance.get("inference_barrier_released") is not True or assurance.get("process_worker_count") != 4:
            raise ControlledRunError("execution assurance barrier/worker mismatch")
    except Exception as exc:
        failure = exc
        primary = _invalid_primary(exc)
        evidence = {
            "research_id": RID,
            "invalid_execution": {"error_type": type(exc).__name__, "error_message": str(exc)},
            "0069_execution_assurance": {"inference_barrier_released": False},
        }

    execution = {
        "schema_version": 1,
        "research_id": RID,
        "boundary_merge_sha": boundary_sha,
        "attempt_sha256": _sha256_file(ATTEMPT),
        "historical_input_read_counters": {"market_evidence": counts["market_evidence"], "equity": counts["equity"], "weights": counts["weights"], "dtb3": counts["dtb3"]},
        "market_loader_calls": counts["market_loader_calls"],
        "scientific_engine_calls": counts["scientific_engine_calls"],
        "network_fetches": counts["network_fetches"],
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    assurance = evidence.get("0069_execution_assurance", {}) if isinstance(evidence, dict) else {}
    for key in ("manifest_sha256", "manifest_unit_count", "terminal_trace_count", "terminal_trace_complete", "validation_fit_calls_expected", "validation_fit_calls_observed", "economic_fit_calls_expected_manifest_derived", "economic_fit_calls_observed", "p08_nnls_expected_manifest_derived", "p08_nnls_observed", "process_worker_count", "inference_barrier_released"):
        if key in assurance:
            execution[key] = assurance[key]
    execution["classification"] = primary["classification"]
    execution["execution_valid"] = primary["classification"] != "INVALID_EXECUTION"

    _create_only(RESULT, _json_bytes(primary))
    _create_only(EVIDENCE, _json_bytes(evidence))
    execution["primary_result_sha256"] = _sha256_file(RESULT)
    execution["evidence_sha256"] = _sha256_file(EVIDENCE)
    _create_only(EXECUTION, _json_bytes(execution))
    if failure is not None:
        return {"classification": "INVALID_EXECUTION", "error_type": type(failure).__name__, "error_message": str(failure), "execution": execution}
    return {"classification": primary["classification"], "execution": execution}


def finalize(boundary_sha: str) -> dict:
    if _git_head() != boundary_sha:
        raise ControlledRunError("finalize must run on exact merged boundary HEAD")
    _verify_pinned_blobs()
    if FINAL.exists():
        raise ControlledRunError("RUN_ONCE.marker already exists; finalize cannot repeat")
    missing = [p.name for p in (ATTEMPT, RESULT, EVIDENCE, EXECUTION) if not p.exists()]
    if missing:
        raise ControlledRunError(f"cannot finalize incomplete durable bundle: {missing}")
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    if execution.get("attempt_sha256") != _sha256_file(ATTEMPT) or execution.get("primary_result_sha256") != _sha256_file(RESULT) or execution.get("evidence_sha256") != _sha256_file(EVIDENCE):
        raise ControlledRunError("durable result hash chain mismatch")
    marker = {
        "schema_version": 1,
        "research_id": RID,
        "attempt_number": 1,
        "boundary_merge_sha": boundary_sha,
        "classification": json.loads(RESULT.read_text(encoding="utf-8"))["classification"],
        "attempt_sha256": _sha256_file(ATTEMPT),
        "primary_result_sha256": _sha256_file(RESULT),
        "evidence_sha256": _sha256_file(EVIDENCE),
        "execution_sha256": _sha256_file(EXECUTION),
        "finalize_historical_content_reads": 0,
        "finalize_market_loader_calls": 0,
        "finalize_scientific_engine_calls": 0,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _create_only(FINAL, _json_bytes(marker))
    return marker


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "evaluate", "finalize"):
        p = sub.add_parser(name)
        p.add_argument("--boundary-sha", required=True)
    p = sub.add_parser("start")
    p.add_argument("--boundary-sha", required=True)
    p.add_argument("--workflow-run-id", required=True)
    args = parser.parse_args(argv)
    if args.command == "preflight":
        out = preflight(args.boundary_sha)
    elif args.command == "start":
        out = start_attempt(args.boundary_sha, args.workflow_run_id)
    elif args.command == "evaluate":
        out = evaluate(args.boundary_sha)
    else:
        out = finalize(args.boundary_sha)
    print(json.dumps(out, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
