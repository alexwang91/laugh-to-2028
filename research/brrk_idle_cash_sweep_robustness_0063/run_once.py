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

from research.brrk_idle_cash_sweep_robustness_0063 import engine

RID = "BRRK-IDLE-CASH-SWEEP-ROBUSTNESS-0063"
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EQUITY = ROOT / "research/results/pit_disp_0015/daily_equity.csv"
WEIGHTS = ROOT / "research/results/pit_disp_0015/daily_weights.csv"
DTB3 = HERE / "DTB3_RAW.csv"
ATTEMPT = HERE / "RUN_ATTEMPT.marker"
RESULT = HERE / "PRIMARY_RESULT.json"
EVIDENCE = HERE / "EVIDENCE.json"
EXECUTION = HERE / "EXECUTION.json"
FINAL = HERE / "RUN_ONCE.marker"

PINNED_BLOBS = {
    "research/brrk_idle_cash_sweep_robustness_0063/PREREGISTRATION.json": "c69a228c3bfb4f6826e086fb0cd4525ce4717353",
    "research/brrk_idle_cash_sweep_robustness_0063/DATASET_DECLARATION.json": "3da466c328bb5fa0237f94d619d8d51c27d7bd3e",
    "research/brrk_idle_cash_sweep_robustness_0063/CAPTURE_REPORT.json": "37f52f0025285d3300cdbec487a2c5e75c7f2494",
    "research/brrk_idle_cash_sweep_robustness_0063/DTB3_RAW.csv": "71d50e26f8a9afb6bcb88401d20b97d5fb0a891a",
    "research/brrk_idle_cash_sweep_robustness_0063/IMPLEMENTATION_CONTRACT.json": "856378ed424afc2f265014ffce552c6e8cc4e330",
    "research/brrk_idle_cash_sweep_robustness_0063/engine.py": "94dec1f3071ce80b859c9558556cdb4f1ffd26c8",
    "research/results/pit_disp_0015/daily_equity.csv": "82c87f8cb0ff01c728ffd3b717fff17cf5a364f2",
    "research/results/pit_disp_0015/daily_weights.csv": "2f6c8d3a8c25d3cafeaa0128f1c425dac248370b",
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
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, text=True
    ).strip()


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
        baseline_returns = None
    else:
        baseline_returns = np.empty(len(values), dtype=float)
        baseline_returns[0] = values[0] / 10000.0 - 1.0
        baseline_returns[1:] = values[1:] / values[:-1] - 1.0
        if np.any(baseline_returns <= -1.0) or not np.isfinite(baseline_returns).all():
            reasons.append("invalid reconstructed baseline return")
        if len(idx) >= 2:
            multiple = float(np.prod(1.0 + baseline_returns))
            cagr = multiple ** (1.0 / (((idx[-1] - idx[0]).days) / 365.25)) - 1.0
            if abs(cagr - CAGR_ANCHOR) > CAGR_TOL:
                reasons.append(f"CAGR anchor mismatch {cagr}")
            terminal = 10000.0 * multiple
            if abs(terminal - FINAL_10K_ANCHOR) > FINAL_TOL:
                reasons.append(f"terminal anchor mismatch {terminal}")

    w = weights.astype(float).to_numpy()
    if not np.isfinite(w).all():
        reasons.append("weights contain nonfinite values")
        gross_max = None
    else:
        gross = np.abs(w).sum(axis=1)
        gross_max = float(np.max(gross))
        if gross_max > 1.000001:
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
        "terminal_10k_anchor_expected": FINAL_10K_ANCHOR,
    }
    return not reasons, details


def evaluate(boundary_sha: str) -> dict:
    if not ATTEMPT.exists():
        raise ControlledRunError("durable RUN_ATTEMPT.marker required before evaluation")
    if FINAL.exists():
        raise ControlledRunError("final marker exists; same-ID evaluation permanently closed")
    if any(p.exists() for p in (RESULT, EVIDENCE, EXECUTION)):
        raise ControlledRunError("partial result exists; automatic recomputation forbidden")
    _verify_pinned_blobs()

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
    if not g1_pass:
        primary = {
            "schema_version": 1,
            "research_id": RID,
            "classification": "MEASUREMENT_INCONCLUSIVE_DATA_IDENTITY",
            "gates": {"G0_CONTRACT_AND_DATA_IDENTITY": True, "G1_BASELINE_RECONSTRUCTION_AND_SUPPORT": False},
            "baseline": None,
            "primary_cell_key": "a050_f10bps",
            "primary": None,
            "positive_chronological_blocks": None,
            "chronological_block_sizes": None,
            "bootstrap": None,
            "core_stress_pass": None,
            "candidate_cell_count": 0,
            "actual_variants_evaluated": 0,
            "state_to_canonical_integration_eligible": False,
            "future_only_validation_eligible": False,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        }
        cells = {}
        core_keys = []
    else:
        engine_calls += 1
        out = engine.evaluate(
            equity.index,
            equity["BRRK0011_BASELINE"].astype(float).to_numpy(),
            weights.astype(float).to_numpy(),
            rates.index,
            rates["DTB3"].astype(float).to_numpy(),
            10000.0,
        )
        if out.get("candidate_cell_count") != 16:
            raise ControlledRunError("engine did not return all 16 frozen cells")
        classification = out["classification_after_G1"]
        gates = {"G0_CONTRACT_AND_DATA_IDENTITY": True, "G1_BASELINE_RECONSTRUCTION_AND_SUPPORT": True}
        gates.update(out["gates_after_G1"])
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
            "candidate_cell_count": 16,
            "actual_variants_evaluated": 16,
            "state_to_canonical_integration_eligible": False,
            "future_only_validation_eligible": classification == "PASS_IDLE_CASH_SWEEP_ROBUSTNESS",
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        }
        cells = out["cells"]
        core_keys = out["core_stress_cell_keys"]

    evidence = {
        "schema_version": 1,
        "research_id": RID,
        "data_identity": {
            "pinned_git_blobs_verified": True,
            "dtb3_payload_sha256": DTB3_SHA256,
            "dtb3_payload_sha256_verified": _sha256_bytes(dtb3_bytes) == DTB3_SHA256,
        },
        "support_validation": support,
        "cells": cells,
        "core_stress_cell_keys": core_keys,
        "input_read_counts": counts,
        "scientific_engine_calls": engine_calls,
    }

    _create_only(RESULT, _json_bytes(primary))
    _create_only(EVIDENCE, _json_bytes(evidence))
    execution = {
        "schema_version": 1,
        "research_id": RID,
        "boundary_merge_sha": boundary_sha,
        "attempt_marker_sha256": _sha256_file(ATTEMPT),
        "primary_result_sha256": _sha256_file(RESULT),
        "evidence_sha256": _sha256_file(EVIDENCE),
        "input_read_counts": counts,
        "scientific_engine_calls": engine_calls,
        "network_fetches": 0,
        "reruns": 0,
        "retunes": 0,
        "rescues": 0,
    }
    _create_only(EXECUTION, _json_bytes(execution))
    return primary


def finalize(boundary_sha: str) -> dict:
    if FINAL.exists():
        raise ControlledRunError("final marker already exists")
    for path in (ATTEMPT, RESULT, EVIDENCE, EXECUTION):
        if not path.exists():
            raise ControlledRunError(f"cannot finalize; missing {path.name}")
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    if execution.get("boundary_merge_sha") != boundary_sha:
        raise ControlledRunError("execution boundary mismatch")
    checks = {
        "attempt_marker_sha256": _sha256_file(ATTEMPT),
        "primary_result_sha256": _sha256_file(RESULT),
        "evidence_sha256": _sha256_file(EVIDENCE),
    }
    for key, value in checks.items():
        if execution.get(key) != value:
            raise ControlledRunError(f"persisted hash mismatch for {key}")
    marker = {
        "schema_version": 1,
        "research_id": RID,
        "status": "VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        "boundary_merge_sha": boundary_sha,
        **checks,
        "execution_sha256": _sha256_file(EXECUTION),
        "market_reads_during_finalize": 0,
        "scientific_engine_calls_during_finalize": 0,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
    }
    _create_only(FINAL, _json_bytes(marker))
    return marker


def _main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("preflight", "start", "evaluate", "finalize"):
        q = sub.add_parser(name)
        q.add_argument("--boundary-sha", required=True)
        if name == "start":
            q.add_argument("--workflow-run-id", required=True)
    args = p.parse_args()
    if args.cmd == "preflight":
        out = preflight(args.boundary_sha)
    elif args.cmd == "start":
        out = start_attempt(args.boundary_sha, args.workflow_run_id)
    elif args.cmd == "evaluate":
        out = evaluate(args.boundary_sha)
    else:
        out = finalize(args.boundary_sha)
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    _main()
