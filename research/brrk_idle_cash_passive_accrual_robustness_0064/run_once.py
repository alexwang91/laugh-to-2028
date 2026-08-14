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

from research.brrk_idle_cash_passive_accrual_robustness_0064 import engine

RID = "BRRK-IDLE-CASH-PASSIVE-ACCRUAL-ROBUSTNESS-0064"
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EQUITY = ROOT / "research/results/pit_disp_0015/daily_equity.csv"
WEIGHTS = ROOT / "research/results/pit_disp_0015/daily_weights.csv"
DTB3 = ROOT / "research/brrk_idle_cash_sweep_robustness_0063/DTB3_RAW.csv"
ATTEMPT = HERE / "RUN_ATTEMPT.marker"
RESULT = HERE / "PRIMARY_RESULT.json"
EVIDENCE = HERE / "EVIDENCE.json"
EXECUTION = HERE / "EXECUTION.json"
FINAL = HERE / "RUN_ONCE.marker"

RUN_INTERFACE_BLOB = "1289d808bd5da99dd4de295f70360f4673536cee"
RESULT_SCHEMA_BLOB = "3dd860f51b96f769db75a50e50acf850db35bf19"
PINNED_BLOBS = {
    "research/brrk_idle_cash_passive_accrual_robustness_0064/RUN_INTERFACE.json": RUN_INTERFACE_BLOB,
    "research/brrk_idle_cash_passive_accrual_robustness_0064/RESULT_SCHEMA.json": RESULT_SCHEMA_BLOB,
    "research/brrk_idle_cash_passive_accrual_robustness_0064/PREREGISTRATION.json": "86e01383e284921b5c870509854ee62d11d8bba9",
    "research/brrk_idle_cash_passive_accrual_robustness_0064/DATASET_DECLARATION.json": "2eb154f1c034ab247a75eef61e6ce818777a6b45",
    "research/brrk_idle_cash_passive_accrual_robustness_0064/IMPLEMENTATION_CONTRACT.json": "cc4ed9a251d06bf9dfdcd331923fe69bf41fedb1",
    "research/brrk_idle_cash_passive_accrual_robustness_0064/engine.py": "4060a307be2204c11952cb52e2fc718a5343d8e1",
    "research/results/pit_disp_0015/daily_equity.csv": "82c87f8cb0ff01c728ffd3b717fff17cf5a364f2",
    "research/results/pit_disp_0015/daily_weights.csv": "2f6c8d3a8c25d3cafeaa0128f1c425dac248370b",
    "research/brrk_idle_cash_sweep_robustness_0063/DTB3_RAW.csv": "71d50e26f8a9afb6bcb88401d20b97d5fb0a891a",
    "research/brrk_idle_cash_sweep_robustness_0063/CAPTURE_REPORT.json": "37f52f0025285d3300cdbec487a2c5e75c7f2494",
}
DTB3_SHA256 = "4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879"
EXPECTED_START = pd.Timestamp("2022-12-10")
EXPECTED_END = pd.Timestamp("2026-08-02")
EXPECTED_N = 1332
EXPECTED_SPAN_DAYS = 1331
CAGR_ANCHOR = 0.6516609785339953
CAGR_TOL = 1e-6
FINAL_10K_ANCHOR = 62247.38231294191
FINAL_TOL = 1e-6
GROSS_MAX = 1.000001
PRIMARY_KEY = "a050_fee100bps"
PASS_CLASS = "PASS_PASSIVE_CASH_ACCRUAL_ROBUSTNESS"
CLASSIFICATIONS = {
    "MEASUREMENT_INCONCLUSIVE_DATA_IDENTITY",
    "FAIL_PASSIVE_CASH_PRIMARY_ECONOMICS",
    "FAIL_PASSIVE_CASH_DRAWDOWN",
    "FAIL_PASSIVE_CASH_TEMPORAL_ROBUSTNESS",
    "FAIL_PASSIVE_CASH_DEPENDENCE_ROBUSTNESS",
    "FAIL_PASSIVE_CASH_STRESS_ROBUSTNESS",
    PASS_CLASS,
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
        "historical_csv_content_reads": 0,
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


def _g1_support(equity: pd.DataFrame, weights: pd.DataFrame, rates: pd.DataFrame) -> tuple[bool, dict]:
    reasons: list[str] = []
    idx = equity.index
    cagr_actual = None
    terminal_actual = None
    gross_max = None
    if len(equity) != EXPECTED_N:
        reasons.append(f"equity rows {len(equity)} != {EXPECTED_N}")
    if idx.has_duplicates or not idx.is_monotonic_increasing:
        reasons.append("equity dates not unique/increasing")
    if len(idx) and (idx[0] != EXPECTED_START or idx[-1] != EXPECTED_END):
        reasons.append(f"window {idx[0] if len(idx) else None}..{idx[-1] if len(idx) else None} mismatch")
    if len(idx) >= 2 and int((idx[-1] - idx[0]).days) != EXPECTED_SPAN_DAYS:
        reasons.append("calendar span mismatch")
    if not weights.index.equals(idx):
        reasons.append("weights dates do not exactly match equity dates")

    values = equity["BRRK0011_BASELINE"].astype(float).to_numpy()
    if not np.isfinite(values).all() or np.any(values <= 0):
        reasons.append("equity contains invalid values")
    else:
        baseline_returns = np.empty(len(values), dtype=float)
        baseline_returns[0] = values[0] / 10000.0 - 1.0
        baseline_returns[1:] = values[1:] / values[:-1] - 1.0
        if np.any(baseline_returns <= -1.0) or not np.isfinite(baseline_returns).all():
            reasons.append("invalid reconstructed baseline return")
        elif len(idx) >= 2:
            multiple = float(np.prod(1.0 + baseline_returns))
            cagr_actual = multiple ** (1.0 / (((idx[-1] - idx[0]).days) / 365.25)) - 1.0
            terminal_actual = 10000.0 * multiple
            if abs(cagr_actual - CAGR_ANCHOR) > CAGR_TOL:
                reasons.append(f"CAGR anchor mismatch {cagr_actual}")
            if abs(terminal_actual - FINAL_10K_ANCHOR) > FINAL_TOL:
                reasons.append(f"terminal anchor mismatch {terminal_actual}")

    w = weights.astype(float).to_numpy()
    if not np.isfinite(w).all():
        reasons.append("weights contain nonfinite values")
    else:
        gross = np.abs(w).sum(axis=1)
        gross_max = float(np.max(gross))
        if gross_max > GROSS_MAX:
            reasons.append(f"gross max {gross_max} exceeds frozen cap")

    ridx = rates.index
    if ridx.has_duplicates or not ridx.is_monotonic_increasing or len(ridx) == 0:
        reasons.append("valid DTB3 dates not unique/increasing")
    elif ridx[0] > EXPECTED_START:
        reasons.append("no pre/on-window DTB3 seed")
    else:
        aligned = rates["DTB3"].reindex(ridx.union(idx).sort_values()).ffill().reindex(idx)
        if aligned.isna().any():
            reasons.append("DTB3 causal support missing on strategy dates")

    details = {
        "passed": not reasons,
        "reasons": reasons,
        "observations": int(len(equity)),
        "start": str(idx[0].date()) if len(idx) else None,
        "end": str(idx[-1].date()) if len(idx) else None,
        "gross_max": gross_max,
        "cagr_anchor_expected": CAGR_ANCHOR,
        "cagr_actual": cagr_actual,
        "terminal_10k_anchor_expected": FINAL_10K_ANCHOR,
        "terminal_10k_actual": terminal_actual,
    }
    return not reasons, details


def _validate_engine_output(out: dict, schema: dict) -> None:
    if out.get("candidate_cell_count") != 20 or len(out.get("cells", {})) != 20:
        raise ControlledRunError("engine did not return all 20 frozen cells")
    if out.get("primary_cell_key") != PRIMARY_KEY:
        raise ControlledRunError("primary cell key mismatch")
    if out.get("chronological_block_sizes") != [333, 333, 333, 333]:
        raise ControlledRunError("chronological block geometry mismatch")
    boot = out.get("bootstrap", {})
    if boot.get("block_length") != 60 or boot.get("replicates") != 4000 or boot.get("seed") != 640064:
        raise ControlledRunError("bootstrap identity mismatch")
    if len(out.get("core_stress_cell_keys", [])) != 9:
        raise ControlledRunError("core stress cell count mismatch")
    classification = out.get("classification_after_G1")
    if classification not in CLASSIFICATIONS or classification not in schema["classification_enum"]:
        raise ControlledRunError("classification outside frozen enum")
    gates = out.get("gates_after_G1", {})
    expected = {
        "G2_PRIMARY_NET_TERMINAL_WEALTH_AND_CAGR",
        "G3_PRIMARY_MAX_DRAWDOWN_NONINFERIORITY",
        "G4_TEMPORAL_RECURRENCE",
        "G5_DEPENDENCE_AWARE_MBB_LCB",
        "G6_CORE_STRESS_ROBUSTNESS",
    }
    if set(gates) != expected or any(type(v) is not bool for v in gates.values()):
        raise ControlledRunError("engine gate contract mismatch")


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

    counts = {"equity": 0, "weights": 0, "dtb3": 0}
    equity_bytes = _read_input_once(EQUITY, counts, "equity")
    weights_bytes = _read_input_once(WEIGHTS, counts, "weights")
    dtb3_bytes = _read_input_once(DTB3, counts, "dtb3")
    equity = _parse_equity(equity_bytes)
    weights = _parse_weights(weights_bytes)
    rates = _parse_dtb3(dtb3_bytes)

    g1_pass, support = _g1_support(equity, weights, rates)
    engine_calls = 0
    cells: dict = {}
    core_keys: list[str] = []
    if not g1_pass:
        gates = {
            "G0_CONTRACT_AND_DATA_IDENTITY": True,
            "G1_BASELINE_RECONSTRUCTION_AND_SUPPORT": False,
            "G2_PRIMARY_NET_TERMINAL_WEALTH_AND_CAGR": False,
            "G3_PRIMARY_MAX_DRAWDOWN_NONINFERIORITY": False,
            "G4_TEMPORAL_RECURRENCE": False,
            "G5_DEPENDENCE_AWARE_MBB_LCB": False,
            "G6_CORE_STRESS_ROBUSTNESS": False,
        }
        primary = {
            "schema_version": 1,
            "research_id": RID,
            "classification": "MEASUREMENT_INCONCLUSIVE_DATA_IDENTITY",
            "gates": gates,
            "baseline": None,
            "primary_cell_key": PRIMARY_KEY,
            "primary": None,
            "positive_chronological_blocks": None,
            "chronological_block_sizes": None,
            "bootstrap": None,
            "core_stress_pass": None,
            "candidate_cell_count": 0,
            "actual_variants_evaluated": 0,
            "future_only_validation_eligible": False,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        }
    else:
        engine_calls = 1
        out = engine.evaluate(
            equity.index,
            equity["BRRK0011_BASELINE"].astype(float).to_numpy(),
            weights.astype(float).to_numpy(),
            rates.index,
            rates["DTB3"].astype(float).to_numpy(),
            10000.0,
        )
        _validate_engine_output(out, schema)
        classification = out["classification_after_G1"]
        gates = {
            "G0_CONTRACT_AND_DATA_IDENTITY": True,
            "G1_BASELINE_RECONSTRUCTION_AND_SUPPORT": True,
            **out["gates_after_G1"],
        }
        primary = {
            "schema_version": 1,
            "research_id": RID,
            "classification": classification,
            "gates": gates,
            "baseline": out["baseline"],
            "primary_cell_key": out["primary_cell_key"],
            "primary": out["primary"],
            "positive_chronological_blocks": out["positive_chronological_blocks"],
            "chronological_block_sizes": out["chronological_block_sizes"],
            "bootstrap": out["bootstrap"],
            "core_stress_pass": bool(out["gates_after_G1"]["G6_CORE_STRESS_ROBUSTNESS"]),
            "candidate_cell_count": 20,
            "actual_variants_evaluated": 20,
            "future_only_validation_eligible": classification == PASS_CLASS,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        }
        cells = out["cells"]
        core_keys = out["core_stress_cell_keys"]

    if set(primary) != set(schema["required_primary_keys"]):
        raise ControlledRunError("PRIMARY_RESULT keys mismatch frozen schema")
    if primary["classification"] not in schema["classification_enum"]:
        raise ControlledRunError("PRIMARY_RESULT classification mismatch frozen schema")
    if primary["production_authorized"] or primary["signature_authorized"] or primary["order_submission_authorized"]:
        raise ControlledRunError("authority must remain false")

    evidence = {
        "schema_version": 1,
        "research_id": RID,
        "data_identity": {
            "pinned_git_blobs_verified": True,
            "dtb3_payload_sha256": DTB3_SHA256,
            "dtb3_payload_sha256_verified": _sha256_bytes(dtb3_bytes) == DTB3_SHA256,
        },
        "G1_support": support,
        "input_read_counts": counts,
        "scientific_engine_calls": engine_calls,
        "core_stress_cell_keys": core_keys,
        "cells": cells,
    }
    execution = {
        "schema_version": 1,
        "research_id": RID,
        "boundary_merge_sha": boundary_sha,
        "attempt_number": 1,
        "attempt_marker_sha256": _sha256_file(ATTEMPT),
        "input_read_counts": counts,
        "scientific_engine_calls": engine_calls,
        "candidate_cells_evaluated": primary["actual_variants_evaluated"],
        "network_fetches": 0,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    _create_only(RESULT, _json_bytes(primary))
    _create_only(EVIDENCE, _json_bytes(evidence))
    execution["result_sha256"] = _sha256_file(RESULT)
    execution["evidence_sha256"] = _sha256_file(EVIDENCE)
    _create_only(EXECUTION, _json_bytes(execution))
    return primary


def finalize(boundary_sha: str) -> dict:
    if _git_head() != boundary_sha:
        raise ControlledRunError("finalize must run on exact merged boundary HEAD")
    if FINAL.exists():
        raise ControlledRunError("final marker already exists")
    for path in (ATTEMPT, RESULT, EVIDENCE, EXECUTION):
        if not path.exists():
            raise ControlledRunError(f"cannot finalize; missing {path.name}")
    _verify_pinned_blobs()
    attempt = json.loads(ATTEMPT.read_text(encoding="utf-8"))
    primary = json.loads(RESULT.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    if attempt.get("boundary_merge_sha") != boundary_sha or execution.get("boundary_merge_sha") != boundary_sha:
        raise ControlledRunError("persisted boundary mismatch")
    checks = {
        "attempt_sha256": _sha256_file(ATTEMPT),
        "result_sha256": _sha256_file(RESULT),
        "evidence_sha256": _sha256_file(EVIDENCE),
        "execution_sha256": _sha256_file(EXECUTION),
    }
    if execution.get("attempt_marker_sha256") != checks["attempt_sha256"]:
        raise ControlledRunError("persisted attempt hash mismatch")
    if execution.get("result_sha256") != checks["result_sha256"]:
        raise ControlledRunError("persisted result hash mismatch")
    if execution.get("evidence_sha256") != checks["evidence_sha256"]:
        raise ControlledRunError("persisted evidence hash mismatch")
    marker = {
        "schema_version": 1,
        "research_id": RID,
        "status": "VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        "boundary_merge_sha": boundary_sha,
        "classification": primary["classification"],
        **checks,
        "historical_input_reads_during_finalize": 0,
        "scientific_engine_calls_during_finalize": 0,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    _create_only(FINAL, _json_bytes(marker))
    return marker


def _print(obj: dict) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False))


def cli() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "evaluate", "finalize"):
        p = sub.add_parser(name)
        p.add_argument("--boundary-sha", required=True)
    start = sub.add_parser("start-attempt")
    start.add_argument("--boundary-sha", required=True)
    start.add_argument("--workflow-run-id", required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        _print(preflight(args.boundary_sha))
    elif args.command == "start-attempt":
        _print(start_attempt(args.boundary_sha, args.workflow_run_id))
    elif args.command == "evaluate":
        _print(evaluate(args.boundary_sha))
    elif args.command == "finalize":
        _print(finalize(args.boundary_sha))
    else:
        raise AssertionError(args.command)


if __name__ == "__main__":
    cli()
