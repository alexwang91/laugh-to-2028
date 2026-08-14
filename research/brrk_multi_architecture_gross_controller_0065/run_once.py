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
from research.brrk_multi_architecture_gross_controller_0065 import engine

RID = "BRRK-MULTI-ARCHITECTURE-GROSS-CONTROLLER-0065"
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

RUN_INTERFACE_BLOB = "0e13a536ca4ee2bc9de4cdf2bcbfe8cd1392b18b"
RESULT_SCHEMA_BLOB = "05dd87cd6f820a8573ff434d8cda21656fa164fd"
PINNED_BLOBS = {
    "research/brrk_multi_architecture_gross_controller_0065/RUN_INTERFACE.json": RUN_INTERFACE_BLOB,
    "research/brrk_multi_architecture_gross_controller_0065/RESULT_SCHEMA.json": RESULT_SCHEMA_BLOB,
    "research/brrk_multi_architecture_gross_controller_0065/PREREGISTRATION.json": "5e98ae3c384d75a970b87f5ceb9fb893e3967acd",
    "research/brrk_multi_architecture_gross_controller_0065/DATASET_DECLARATION.json": "031ed9a5d00526029825ad82b0183a09db8e6149",
    "research/brrk_multi_architecture_gross_controller_0065/IMPLEMENTATION_CONTRACT.json": "508c909eedeff79796fec05fbbb125d1015fe962",
    "research/brrk_multi_architecture_gross_controller_0065/engine.py": "762b608dd9eb5feedc06867ce07f02d0de8ea928",
    "research/brrk_btc_risk_signal_atlas_0062/engine.py": "cac8e946998c836d10842b9388e1e3ef345a8c0b",
    "research/brrk_beta_handoff_0047/engine.py": "059b55961e279dab41ba29b5b017de0922e4f33c",
    "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json": "64ebf5c6deaf3f34dbeac715378f196ff0f4fafe",
    "research/results/pit_disp_0015/daily_equity.csv": "82c87f8cb0ff01c728ffd3b717fff17cf5a364f2",
    "research/results/pit_disp_0015/daily_weights.csv": "2f6c8d3a8c25d3cafeaa0128f1c425dac248370b",
    "research/brrk_idle_cash_sweep_robustness_0063/DTB3_RAW.csv": "71d50e26f8a9afb6bcb88401d20b97d5fb0a891a",
    "research/brrk_idle_cash_passive_accrual_robustness_0064/engine.py": "4060a307be2204c11952cb52e2fc718a5343d8e1",
}
MARKET_PAYLOAD_SHA256 = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"
DTB3_SHA256 = "4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879"
EXPECTED_START = pd.Timestamp("2022-12-10")
EXPECTED_END = pd.Timestamp("2026-08-02")
EXPECTED_N = 1332
EXPECTED_BENCHMARK = {
    "terminal_wealth": 62813.41563922909,
    "cagr": 0.6557689400699214,
    "max_drawdown": -0.3366471268083583,
}


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


def preflight(boundary_sha: str) -> dict:
    if _git_head() != boundary_sha:
        raise ControlledRunError("preflight must run on exact merged boundary HEAD")
    _verify_pinned_blobs()
    existing = [p.name for p in (ATTEMPT, RESULT, EVIDENCE, EXECUTION, FINAL) if p.exists()]
    if existing:
        raise ControlledRunError(f"preflight requires zero-result state; found {existing}")
    return {
        "research_id": RID,
        "status": "PREFLIGHT_PASS_ZERO_RESULT_GIT_IDENTITY_ONLY",
        "boundary_sha": boundary_sha,
        "historical_content_reads": {"market_evidence": 0, "equity": 0, "weights": 0, "dtb3": 0},
        "market_loader_calls": 0,
        "scientific_engine_calls": 0,
        "runtime_artifacts_present": [],
    }


def start_attempt(boundary_sha: str, workflow_run_id: str) -> dict:
    if _git_head() != boundary_sha:
        raise ControlledRunError("attempt must start from exact merged boundary HEAD")
    _verify_pinned_blobs()
    if any(p.exists() for p in (ATTEMPT, RESULT, EVIDENCE, EXECUTION, FINAL)):
        raise ControlledRunError("attempt/result artifact already exists; same-ID start forbidden")
    marker = {
        "schema_version": 1,
        "research_id": RID,
        "attempt_number": 1,
        "boundary_merge_sha": boundary_sha,
        "workflow_run_id": str(workflow_run_id),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "declared_validation_tuning_configs": 63,
        "declared_final_architectures": 8,
        "declared_total_variants": 71,
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


def _prepare_portfolio_inputs(equity: pd.DataFrame, weights: pd.DataFrame, rates: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    idx = equity.index
    if len(idx) != EXPECTED_N or idx[0] != EXPECTED_START or idx[-1] != EXPECTED_END or not weights.index.equals(idx):
        raise ControlledRunError("frozen 0065 portfolio support mismatch")
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


def _validate_complete_primary(primary: dict, schema: dict) -> None:
    classification = primary.get("classification")
    if classification not in schema["classification_enum"]:
        raise ControlledRunError("classification outside frozen enum")
    if classification in {"PASS_MULTI_ARCHITECTURE_GROSS_CONTROLLER", "FAIL_NO_ROBUST_MULTI_ARCHITECTURE_IMPROVEMENT"}:
        missing = [x for x in schema["required_primary_fields"] if x not in primary]
        if missing:
            raise ControlledRunError(f"complete result missing fields: {missing}")
        if primary.get("actual_validation_configs_evaluated") != 63 or primary.get("final_architecture_count") != 8 or primary.get("actual_variants_evaluated") != 71:
            raise ControlledRunError("complete result variant accounting mismatch")
        methods = primary.get("methods", {})
        if list(methods) != schema["method_enum"]:
            raise ControlledRunError("method set/order mismatch")
        for name, m in methods.items():
            miss = [x for x in schema["required_method_fields"] if x not in m]
            if miss:
                raise ControlledRunError(f"method {name} missing fields {miss}")
        bench = primary.get("benchmark_0064", {})
        for key, expected in schema["frozen_benchmark"].items():
            if not np.isclose(float(bench[key]), float(expected), rtol=0.0, atol=1e-12):
                raise ControlledRunError(f"0064 benchmark drift {key}")
        boot = primary.get("simultaneous_bootstrap", {})
        if boot.get("block_length") != 60 or boot.get("replicates") != 4000 or boot.get("seed") != 650065:
            raise ControlledRunError("simultaneous bootstrap identity mismatch")
        pbo = primary.get("PBO_CSCV", {})
        if pbo.get("status") == "OK" and pbo.get("split_count") != 70:
            raise ControlledRunError("PBO split-count mismatch")
    if primary.get("production_authorized") is not False or primary.get("signature_authorized") is not False or primary.get("order_submission_authorized") is not False:
        raise ControlledRunError("illegal authority in primary result")


def _failure_result(classification: str, stage: str, exc: Exception, counts: dict[str, int], loader_calls: int, engine_calls: int) -> tuple[dict, dict]:
    primary = {
        "schema_version": 1,
        "research_id": RID,
        "classification": classification,
        "failure_stage": stage,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "actual_validation_configs_evaluated": 0,
        "final_architecture_count": 8,
        "actual_variants_evaluated": 0,
        "benchmark_0064": EXPECTED_BENCHMARK,
        "methods": {},
        "descriptive_best_CAGR_method": None,
        "scientific_winners": [],
        "simultaneous_bootstrap": {"block_length": 60, "replicates": 4000, "seed": 650065, "q95": None},
        "PBO_CSCV": {"status": "NOT_EVALUATED"},
        "stack_weights": {},
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
    schema = _load_schema()
    marker = json.loads(ATTEMPT.read_text(encoding="utf-8"))
    if marker.get("boundary_merge_sha") != boundary_sha or marker.get("attempt_number") != 1:
        raise ControlledRunError("attempt marker does not bind requested boundary")

    counts = {"market_evidence": 0, "equity": 0, "weights": 0, "dtb3": 0}
    loader_calls = 0
    engine_calls = 0
    try:
        market_bytes = _read_input_once(MARKET, counts, "market_evidence")
        equity_bytes = _read_input_once(EQUITY, counts, "equity")
        weights_bytes = _read_input_once(WEIGHTS, counts, "weights")
        dtb3_bytes = _read_input_once(DTB3, counts, "dtb3")
        frames = _parse_market(market_bytes)
        loader_calls += 1
        equity = _parse_equity(equity_bytes)
        weights = _parse_weights(weights_bytes)
        rates = _parse_dtb3(dtb3_bytes)
        baseline_returns, baseline_gross, rf_daily = _prepare_portfolio_inputs(equity, weights, rates)
        engine_calls += 1
        out = engine.evaluate_tournament(frames, baseline_returns, baseline_gross, rf_daily, enforce_historical_anchors=True)
        primary = out["primary_result"]
        evidence = out["evidence"]
        _validate_complete_primary(primary, schema)
    except Exception as exc:
        # One-attempt fail-closed result. Never re-enter the engine under this ID.
        primary, evidence = _failure_result("INVALID_EXECUTION", "UNIQUE_HISTORICAL_ATTEMPT", exc, counts, loader_calls, engine_calls)

    if any(v != 1 for v in counts.values()):
        # Identity/parse failure can occur after an attempted read; preserve exact counts in the immutable failure result.
        pass
    execution = {
        "schema_version": 1,
        "research_id": RID,
        "attempt_number": 1,
        "boundary_merge_sha": boundary_sha,
        "input_read_counts": dict(counts),
        "market_loader_calls": int(loader_calls),
        "scientific_engine_calls": int(engine_calls),
        "network_fetches": 0,
        "declared_validation_tuning_configs": 63,
        "declared_final_architectures": 8,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
        "attempt_marker_sha256": _sha256_file(ATTEMPT),
    }
    _create_only(RESULT, _json_bytes(primary))
    _create_only(EVIDENCE, _json_bytes(evidence))
    execution["result_sha256"] = _sha256_file(RESULT)
    execution["evidence_sha256"] = _sha256_file(EVIDENCE)
    _create_only(EXECUTION, _json_bytes(execution))
    return {
        "classification": primary["classification"],
        "result_sha256": execution["result_sha256"],
        "evidence_sha256": execution["evidence_sha256"],
        "execution_sha256": _sha256_file(EXECUTION),
        "input_read_counts": counts,
        "market_loader_calls": loader_calls,
        "scientific_engine_calls": engine_calls,
    }


def finalize(boundary_sha: str) -> dict:
    if FINAL.exists():
        raise ControlledRunError("RUN_ONCE.marker already exists; finalization closed")
    if not ATTEMPT.exists() or not RESULT.exists() or not EVIDENCE.exists() or not EXECUTION.exists():
        raise ControlledRunError("finalize requires complete persisted attempt/result/evidence/execution")
    _verify_pinned_blobs()
    marker = json.loads(ATTEMPT.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    if marker.get("boundary_merge_sha") != boundary_sha or execution.get("boundary_merge_sha") != boundary_sha:
        raise ControlledRunError("boundary hash mismatch during finalize")
    if execution.get("result_sha256") != _sha256_file(RESULT) or execution.get("evidence_sha256") != _sha256_file(EVIDENCE):
        raise ControlledRunError("persisted result/evidence hash mismatch")
    final = {
        "schema_version": 1,
        "research_id": RID,
        "status": "VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN" if result.get("classification") != "INVALID_EXECUTION" else "INVALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        "classification": result.get("classification"),
        "boundary_merge_sha": boundary_sha,
        "attempt_sha256": _sha256_file(ATTEMPT),
        "result_sha256": _sha256_file(RESULT),
        "evidence_sha256": _sha256_file(EVIDENCE),
        "execution_sha256": _sha256_file(EXECUTION),
        "historical_input_reads_during_finalize": 0,
        "market_loader_calls_during_finalize": 0,
        "scientific_engine_calls_during_finalize": 0,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    _create_only(FINAL, _json_bytes(final))
    return final


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("preflight")
    p.add_argument("--boundary-sha", required=True)
    s = sub.add_parser("start")
    s.add_argument("--boundary-sha", required=True)
    s.add_argument("--workflow-run-id", required=True)
    e = sub.add_parser("evaluate")
    e.add_argument("--boundary-sha", required=True)
    f = sub.add_parser("finalize")
    f.add_argument("--boundary-sha", required=True)
    args = ap.parse_args()
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
