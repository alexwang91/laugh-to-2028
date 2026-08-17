from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from research.brrk_beta_handoff_0047.engine import frames_from_market_evidence
from research.brrk_btc_sol_path_event_early_warning_0066 import engine as ref
from research.brrk_btc_sol_path_event_early_warning_runtime_qualified_0067 import engine as opt
from research.brrk_idle_cash_passive_accrual_robustness_0064 import engine as cash_engine
from research.brrk_sol_long_sideways_early_warning_episode_robustness_0070 import engine as robustness
from research.brrk_sol_long_sideways_controller_integration_0071 import engine

RID = "BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-0071"
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE_PRIMARY = ROOT / "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/PRIMARY_RESULT.json"
SOURCE_EVIDENCE = ROOT / "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/EVIDENCE.json"
MARKET = ROOT / "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json"
DTB3 = ROOT / "research/brrk_idle_cash_sweep_robustness_0063/DTB3_RAW.csv"
ATTEMPT = HERE / "RUN_ATTEMPT.marker"
RESULT = HERE / "PRIMARY_RESULT.json"
EVIDENCE = HERE / "EVIDENCE.json"
EXECUTION = HERE / "EXECUTION.json"
FINAL = HERE / "RUN_ONCE.marker"

MARKET_PAYLOAD_SHA256 = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"
DTB3_SHA256 = "4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879"
P02 = "P02_RAW_ELASTIC_NET_LOGIT|SOL|T4_LONG_SIDEWAYS"
P02_KEY = ("P02_RAW_ELASTIC_NET_LOGIT", "SOL", "T4_LONG_SIDEWAYS", 10)

PINNED_BLOBS = {
    "research/brrk_sol_long_sideways_controller_integration_0071/RUN_INTERFACE.json": "35c14920f854a0526080ad41c527b61732f342e1",
    "research/brrk_sol_long_sideways_controller_integration_0071/CONTROLLED_EXECUTION_BOUNDARY.json": "9a06e1180b9329e429f40a57d30dcb78c13a8b6f",
    "research/brrk_sol_long_sideways_controller_integration_0071/PREREGISTRATION.json": "f7810fcf1db723c0b84c71a5d74d4f74573c3830",
    "research/brrk_sol_long_sideways_controller_integration_0071/ECONOMIC_ANALYSIS_CONTRACT.json": "5f4577dfa2e54a37b79c671ed271e20a19515778",
    "research/brrk_sol_long_sideways_controller_integration_0071/QUALIFICATION_PREREGISTRATION.json": "15ec542b67f8f27f00d208e7f65ddafc32ed8880",
    "research/brrk_sol_long_sideways_controller_integration_0071/RESULT_SCHEMA.json": "c1d98c743deb4e93876624e23f057a7a96375000",
    "research/brrk_sol_long_sideways_controller_integration_0071/IMPLEMENTATION_CONTRACT.json": "f20564293dce526546e119681c7eba4e261da3d3",
    "research/brrk_sol_long_sideways_controller_integration_0071/engine.py": "26cac1ecd2e93b6954bed23737e8416893376c4d",
    "research/brrk_sol_long_sideways_controller_integration_0071/QUALIFICATION_RESULT.json": "9a782797b32430e36fd20316f5aa3030fa04e72d",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/PRIMARY_RESULT.json": "df00901c77d8d334d61c7c65a14b8d127e9ca8b6",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/EVIDENCE.json": "6266e6a11205e21592766546342ca5bca1dd97f0",
    "research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/PRIMARY_RESULT.json": "e5226963c6bebfae4341889da1b17025152eec51",
    "research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/EVIDENCE.json": "47d5f2ac5704ae2f89773d8d0c29ccce9ee2da0c",
    "research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/EXECUTION.json": "ff264f5ef1bf3d5096301f3e31a0f136c7e3b0f8",
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/engine.py": "482868d45ccdeaa5fbad8033f122a8fcfde79ca6",
    "research/brrk_btc_sol_path_event_early_warning_0066/engine.py": "79320c83d0ce89c2c952fd0a4f7a9b7452a8e0ae",
    "research/brrk_btc_sol_path_event_early_warning_0066/event_engine.py": "651ebb824b9dc1390ed0170a4eab07a3870786aa",
    "research/brrk_btc_sol_path_event_early_warning_0066/models.py": "6b255b887f2cd8f1741086a7bf27e6254288e836",
    "research/brrk_btc_risk_signal_atlas_0062/engine.py": "cac8e946998c836d10842b9388e1e3ef345a8c0b",
    "research/brrk_beta_handoff_0047/engine.py": "059b55961e279dab41ba29b5b017de0922e4f33c",
    "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json": "64ebf5c6deaf3f34dbeac715378f196ff0f4fafe",
    "research/brrk_idle_cash_passive_accrual_robustness_0064/engine.py": "4060a307be2204c11952cb52e2fc718a5343d8e1",
    "research/brrk_idle_cash_sweep_robustness_0063/DTB3_RAW.csv": "71d50e26f8a9afb6bcb88401d20b97d5fb0a891a",
}


class ControlledRunError(RuntimeError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def preflight(boundary_sha: str) -> dict[str, Any]:
    if _git_head() != boundary_sha:
        raise ControlledRunError("preflight must run on exact merged boundary HEAD")
    _verify_pinned_blobs()
    existing = _runtime_existing()
    if existing:
        raise ControlledRunError(f"preflight requires zero-result state; found {existing}")
    branch_exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", "refs/heads/research/0071-result-v1"],
        cwd=ROOT,
        check=False,
    ).returncode == 0
    if branch_exists:
        raise ControlledRunError("result branch already exists")
    return {
        "research_id": RID,
        "status": "PREFLIGHT_PASS_ZERO_RESULT_GIT_IDENTITY_ONLY",
        "boundary_sha": boundary_sha,
        "controlled_reads": {"0069_PRIMARY_RESULT": 0, "0069_EVIDENCE": 0, "MARKET_EVIDENCE": 0, "DTB3": 0, "0070_RESULT_CONTENT": 0},
        "call_counts": {"market_loader": 0, "frozen_P02_prediction_reconstruction": 0, "cash_engine": 0, "validation_tuning": 0, "model_reselection": 0, "P02_retraining": 0},
        "network_fetches": 0,
        "controlled_attempt_consumed": 0,
        "runtime_artifacts_present": [],
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def start_attempt(boundary_sha: str, workflow_run_id: str) -> dict[str, Any]:
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
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
    }
    _create_only(ATTEMPT, _json_bytes(marker))
    return marker


def _read_once(path: Path, counts: dict[str, int], key: str) -> bytes:
    if counts[key] != 0:
        raise ControlledRunError(f"controlled input {key} attempted more than once")
    data = path.read_bytes()
    counts[key] += 1
    return data


def _parse_market(data: bytes, counts: dict[str, int]) -> dict[str, pd.DataFrame]:
    obj = json.loads(data.decode("utf-8"))
    if obj.get("payload_sha256") != MARKET_PAYLOAD_SHA256:
        raise ControlledRunError("market evidence payload SHA256 mismatch")
    if counts["market_loader"] != 0:
        raise ControlledRunError("market loader attempted more than once")
    frames = frames_from_market_evidence(obj)
    counts["market_loader"] += 1
    return frames


def _parse_dtb3(data: bytes) -> pd.DataFrame:
    if _sha256_bytes(data) != DTB3_SHA256:
        raise ControlledRunError("DTB3 payload SHA256 mismatch")
    df = pd.read_csv(io.BytesIO(data), parse_dates=["observation_date"])
    if list(df.columns) != ["observation_date", "DTB3"]:
        raise ControlledRunError("unexpected DTB3 schema")
    df["DTB3"] = pd.to_numeric(df["DTB3"], errors="coerce")
    return df.dropna(subset=["DTB3"]).set_index("observation_date")


def _parse_atrack(key: str) -> tuple[str, str, str, int]:
    parts = key.split("|")
    if len(parts) != 4 or not parts[3].startswith("L"):
        raise ControlledRunError(f"invalid selected-hyperparameter key {key}")
    return parts[0], parts[1], parts[2], int(parts[3][1:])


def _locked_p02_params(evidence: Mapping[str, Any]) -> dict[str, Any]:
    raw = evidence.get("validation_selected_hyperparameters")
    if not isinstance(raw, Mapping):
        raise ControlledRunError("0069 evidence missing frozen validation selection")
    for key, value in raw.items():
        if _parse_atrack(str(key)) == P02_KEY and isinstance(value, Mapping):
            return dict(value)
    raise ControlledRunError("frozen P02 selection missing")


def _source_reference(primary: Mapping[str, Any]) -> dict[str, float]:
    tracks = primary.get("predictor_tracks")
    if not isinstance(tracks, Mapping):
        raise ControlledRunError("0069 PRIMARY_RESULT predictor_tracks missing")
    row = tracks.get(P02)
    if not isinstance(row, Mapping) or row.get("status") != "EVALUATED" or int(row.get("preferred_warning_horizon", -1)) != 10:
        raise ControlledRunError("0069 frozen P02 source unavailable")
    fm = row.get("final_metrics")
    if not isinstance(fm, Mapping) or fm.get("status") != "OK":
        raise ControlledRunError("0069 frozen P02 metrics unavailable")
    needed = robustness.FROZEN[P02]
    vals = {k: float(fm[k]) for k in needed}
    for key, expected in needed.items():
        if abs(vals[key] - float(expected)) > robustness.TOL:
            raise ControlledRunError(f"0069 P02 reference mismatch {key}")
    return vals


def _reconstruct_p02(frames: Mapping[str, pd.DataFrame], source_evidence: Mapping[str, Any], counts: dict[str, int]) -> dict[str, Any]:
    if counts["frozen_P02_prediction_reconstruction"] != 0:
        raise ControlledRunError("P02 reconstruction attempted more than once")
    counts["frozen_P02_prediction_reconstruction"] += 1
    naive = ref._naive_frames(frames)
    cells, families, _, signals = ref._common_feature_objects(naive)
    bundle = ref.ee.build_event_atlas(naive)
    labels, _ = ref._labels_and_support(bundle, cells.index)
    params = _locked_p02_params(source_evidence)
    predictions, replay_audit = opt._evaluate_selected_parallel(
        cells,
        families,
        signals,
        labels,
        {a: bundle.asset_indices[a] for a in ref.ee.ASSETS},
        {},
        {P02_KEY: params},
        {},
    )
    if P02_KEY not in predictions:
        raise ControlledRunError("frozen P02 reconstruction unavailable")
    fidx = ref._period_index(cells.index, ref.FINAL_START, ref.FINAL_END)
    pred = predictions[P02_KEY].reindex(fidx).astype(float)
    label = labels[("SOL", "T4_LONG_SIDEWAYS", 10)].reindex(fidx).astype(float)
    metric_mask = pred.notna() & label.notna()
    if int(metric_mask.sum()) == 0 or label.loc[metric_mask].nunique() != 2:
        raise ControlledRunError("P02 reproduction support undefined")
    y = label.loc[metric_mask].to_numpy(dtype=int)
    p = pred.loc[metric_mask].to_numpy(dtype=float)
    reproduced = robustness.metrics(y, p, robustness.FROZEN[P02]["PR_AUC_LIFT"])
    return {"scores": pred, "reproduced": reproduced, "replay_audit": replay_audit}


def _validate_reproduction(reproduced: Mapping[str, float], source: Mapping[str, float]) -> None:
    for key, expected in source.items():
        observed = float(reproduced[key])
        if abs(observed - float(expected)) > robustness.TOL:
            raise ControlledRunError(f"P02 reproduction mismatch {key}: observed={observed} expected={expected}")


def _build_economic_support(scores: pd.Series, frames: Mapping[str, pd.DataFrame], rates: pd.DataFrame, counts: dict[str, int]) -> dict[str, Any]:
    sol = frames["SOL"].sort_index()
    close = pd.to_numeric(sol["close"], errors="raise").astype(float)
    daily = close.pct_change()
    running_max = close.cummax()
    drawdown = close / running_max - 1.0
    rows: list[pd.Timestamp] = []
    next_dates: list[pd.Timestamp] = []
    lag20: list[list[float]] = []
    sol_returns: list[float] = []
    lagged_dd: list[float] = []
    score_values: list[float] = []
    index_pos = {pd.Timestamp(d): i for i, d in enumerate(close.index)}
    for d, score in scores.items():
        d = pd.Timestamp(d)
        if not np.isfinite(float(score)) or d not in index_pos:
            continue
        pos = index_pos[d]
        if pos < 20 or pos + 1 >= len(close):
            continue
        hist = daily.iloc[pos - 19:pos + 1].to_numpy(dtype=float)
        if len(hist) != 20 or not np.isfinite(hist).all():
            continue
        nxt = pd.Timestamp(close.index[pos + 1])
        rnext = float(close.iloc[pos + 1] / close.iloc[pos] - 1.0)
        if not np.isfinite(rnext):
            continue
        rows.append(d)
        next_dates.append(nxt)
        lag20.append(hist.tolist())
        sol_returns.append(rnext)
        lagged_dd.append(float(drawdown.iloc[pos]))
        score_values.append(float(score))
    if len(rows) == 0:
        raise ControlledRunError("no common economic support")
    if counts["cash_engine"] != 0:
        raise ControlledRunError("cash engine attempted more than once")
    aligned_percent = cash_engine.causal_align_rates(rows, rates.index, rates["DTB3"].to_numpy(dtype=float))
    rf_daily = cash_engine.dtb3_percent_to_daily_return(aligned_percent)
    fee_daily = (100.0 / 10000.0) / cash_engine.YEAR_DAYS
    cash_returns = 0.50 * rf_daily - fee_daily
    counts["cash_engine"] += 1
    if not np.isfinite(cash_returns).all():
        raise ControlledRunError("nonfinite frozen cash returns")
    return {
        "decision_dates": pd.DatetimeIndex(rows),
        "return_dates": pd.DatetimeIndex(next_dates),
        "scores": np.asarray(score_values, dtype=float),
        "sol_returns": np.asarray(sol_returns, dtype=float),
        "cash_returns": np.asarray(cash_returns, dtype=float),
        "lag20": lag20,
        "lagged_drawdown": np.asarray(lagged_dd, dtype=float),
    }


def _pbo_diagnostic(support: Mapping[str, Any]) -> dict[str, Any]:
    n = len(support["scores"])
    if n // 8 < 20:
        return {"status": "NOT_SUPPORTED", "reason": "fewer than 20 common rows per CSCV slice", "slices": 8, "splits": 70}
    return {"status": "SUPPORTED_BY_CONTRACT_BUT_NON_GATE", "method": "CSCV", "slices": 8, "splits": 70, "ranking": "C1 Sharpe", "role": "diagnostic_not_PASS_gate"}


def _invalid_primary(exc: Exception) -> dict[str, Any]:
    return {
        "research_id": RID,
        "classification": engine.INVALID,
        "execution_valid": False,
        "evidence_tier": "RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS",
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def _result_payload(core: Mapping[str, Any], source: Mapping[str, float], reproduced: Mapping[str, float], support: Mapping[str, Any], counts: Mapping[str, int]) -> dict[str, Any]:
    candidates = core.get("candidates", {})
    controls = core.get("controls", {})
    return {
        "research_id": RID,
        "classification": core.get("classification"),
        "execution_valid": bool(core.get("execution_valid")),
        "evidence_tier": "RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS",
        "common_support": {"rows": int(len(support["scores"])), "decision_start": str(support["decision_dates"][0].date()), "decision_end": str(support["decision_dates"][-1].date()), "first_applied_return": "t_to_t_plus_1"},
        "full_window_P02_reproduction": {"status": "PASS", "absolute_tolerance": 1e-12, "source": dict(source), "reproduced": {k: float(v) for k, v in reproduced.items()}},
        "benchmark": core.get("benchmark", {}),
        "candidates": candidates,
        "matched_controls": controls,
        "passing_candidates": core.get("passing_candidates", []),
        "representative_candidate": core.get("representative_candidate"),
        "bootstrap": {"replicates": engine.BOOTSTRAP_REPS, "block_length": engine.BOOTSTRAP_BLOCK, "seed": engine.BOOTSTRAP_SEED},
        "DSR": {"trials": engine.DSR_TRIALS, "gate": engine.DSR_GATE},
        "PBO": _pbo_diagnostic(support),
        "concentration": {cid: {"best_month_removed": row.get("best_month_removed")} for cid, row in candidates.items()},
        "cost_break_even": {cid: row.get("cost_break_even_bps") for cid, row in candidates.items()},
        "source_read_counts": {"0069_PRIMARY_RESULT": counts["0069_PRIMARY_RESULT"], "0069_EVIDENCE": counts["0069_EVIDENCE"], "MARKET_EVIDENCE": counts["MARKET_EVIDENCE"], "DTB3": counts["DTB3"], "0070_RESULT_CONTENT": 0},
        "call_counts": {"market_loader": counts["market_loader"], "frozen_P02_prediction_reconstruction": counts["frozen_P02_prediction_reconstruction"], "cash_engine": counts["cash_engine"], "validation_tuning": 0, "model_reselection": 0, "P02_retraining": 0},
        "candidate_accounting": {"selectable_candidates": int(core.get("candidate_count", 0)), "matched_controls": int(core.get("matched_control_count", 0)), "benchmark": 1},
        "network_fetches": 0,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def evaluate(boundary_sha: str) -> dict[str, Any]:
    if _git_head() != boundary_sha:
        raise ControlledRunError("evaluate must run on exact merged boundary HEAD")
    _verify_pinned_blobs()
    if not ATTEMPT.exists():
        raise ControlledRunError("durable RUN_ATTEMPT.marker required before controlled read")
    if any(p.exists() for p in (RESULT, EVIDENCE, EXECUTION, FINAL)):
        raise ControlledRunError("result/final artifact already exists; same-ID evaluation forbidden")
    marker = json.loads(ATTEMPT.read_text(encoding="utf-8"))
    if marker.get("research_id") != RID or marker.get("boundary_merge_sha") != boundary_sha or marker.get("attempt_number") != 1:
        raise ControlledRunError("RUN_ATTEMPT identity mismatch")

    counts = {"0069_PRIMARY_RESULT": 0, "0069_EVIDENCE": 0, "MARKET_EVIDENCE": 0, "DTB3": 0, "market_loader": 0, "frozen_P02_prediction_reconstruction": 0, "cash_engine": 0}
    failure: Exception | None = None
    try:
        primary_b = _read_once(SOURCE_PRIMARY, counts, "0069_PRIMARY_RESULT")
        evidence_b = _read_once(SOURCE_EVIDENCE, counts, "0069_EVIDENCE")
        market_b = _read_once(MARKET, counts, "MARKET_EVIDENCE")
        dtb3_b = _read_once(DTB3, counts, "DTB3")
        source_primary = json.loads(primary_b.decode("utf-8"))
        source_evidence = json.loads(evidence_b.decode("utf-8"))
        source_reference = _source_reference(source_primary)
        frames = _parse_market(market_b, counts)
        rates = _parse_dtb3(dtb3_b)
        rec = _reconstruct_p02(frames, source_evidence, counts)
        _validate_reproduction(rec["reproduced"], source_reference)
        support = _build_economic_support(rec["scores"], frames, rates, counts)
        core = engine.evaluate(
            scores=support["scores"],
            sol_returns=support["sol_returns"],
            cash_returns=support["cash_returns"],
            lag20=support["lag20"],
            lagged_drawdown=support["lagged_drawdown"],
            dates=support["return_dates"],
            identity_ok=True,
            reproduction_ok=True,
            read_counts_ok=all((counts["0069_PRIMARY_RESULT"] == 1, counts["0069_EVIDENCE"] == 1, counts["MARKET_EVIDENCE"] == 1, counts["DTB3"] == 1, counts["market_loader"] == 1, counts["frozen_P02_prediction_reconstruction"] == 1, counts["cash_engine"] == 1)),
            cash_accounting_ok=True,
        )
        primary = _result_payload(core, source_reference, rec["reproduced"], support, counts)
        evidence = {
            "research_id": RID,
            "boundary_sha": boundary_sha,
            "P02_replay_audit": rec["replay_audit"],
            "full_window_P02_reproduction": primary["full_window_P02_reproduction"],
            "common_support": primary["common_support"],
            "candidate_accounting": primary["candidate_accounting"],
            "source_read_counts": primary["source_read_counts"],
            "call_counts": primary["call_counts"],
            "network_fetches": 0,
            "production_authorized": False,
        }
    except Exception as exc:
        failure = exc
        primary = _invalid_primary(exc)
        evidence = {"research_id": RID, "boundary_sha": boundary_sha, "failure": {"type": type(exc).__name__, "message": str(exc)}, "source_read_counts": {"0069_PRIMARY_RESULT": counts["0069_PRIMARY_RESULT"], "0069_EVIDENCE": counts["0069_EVIDENCE"], "MARKET_EVIDENCE": counts["MARKET_EVIDENCE"], "DTB3": counts["DTB3"], "0070_RESULT_CONTENT": 0}, "call_counts": {"market_loader": counts["market_loader"], "frozen_P02_prediction_reconstruction": counts["frozen_P02_prediction_reconstruction"], "cash_engine": counts["cash_engine"], "validation_tuning": 0, "model_reselection": 0, "P02_retraining": 0}, "network_fetches": 0, "production_authorized": False}

    result_b = _json_bytes(primary)
    evidence_b = _json_bytes(evidence)
    execution = {
        "research_id": RID,
        "boundary_sha": boundary_sha,
        "attempt_sha256": _sha256_bytes(ATTEMPT.read_bytes()),
        "PRIMARY_RESULT_sha256": _sha256_bytes(result_b),
        "EVIDENCE_sha256": _sha256_bytes(evidence_b),
        "source_read_counts": evidence["source_read_counts"],
        "call_counts": evidence["call_counts"],
        "network_fetches": 0,
        "attempt_consumed": "1/1",
        "failure_after_marker": failure is not None,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    execution_b = _json_bytes(execution)
    _create_only(RESULT, result_b)
    _create_only(EVIDENCE, evidence_b)
    _create_only(EXECUTION, execution_b)
    return {"primary": primary, "evidence": evidence, "execution": execution}


def finalize(boundary_sha: str) -> dict[str, Any]:
    if _git_head() != boundary_sha:
        raise ControlledRunError("finalize must run on exact merged boundary HEAD")
    _verify_pinned_blobs()
    if FINAL.exists():
        raise ControlledRunError("RUN_ONCE.marker already exists")
    if not ATTEMPT.exists() or not RESULT.exists() or not EVIDENCE.exists() or not EXECUTION.exists():
        raise ControlledRunError("marker-only finalize requires complete durable result bundle")
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    if execution.get("boundary_sha") != boundary_sha or execution.get("attempt_consumed") != "1/1":
        raise ControlledRunError("execution identity mismatch")
    if execution.get("PRIMARY_RESULT_sha256") != _sha256_bytes(RESULT.read_bytes()) or execution.get("EVIDENCE_sha256") != _sha256_bytes(EVIDENCE.read_bytes()):
        raise ControlledRunError("durable result hash mismatch")
    marker = {
        "schema_version": 1,
        "research_id": RID,
        "boundary_sha": boundary_sha,
        "attempt_consumed": "1/1",
        "PRIMARY_RESULT_sha256": _sha256_bytes(RESULT.read_bytes()),
        "EVIDENCE_sha256": _sha256_bytes(EVIDENCE.read_bytes()),
        "EXECUTION_sha256": _sha256_bytes(EXECUTION.read_bytes()),
        "finalization_controlled_source_rereads": 0,
        "finalized_at_utc": datetime.now(timezone.utc).isoformat(),
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
    }
    _create_only(FINAL, _json_bytes(marker))
    return marker


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("preflight", "start", "evaluate", "finalize", "run"))
    parser.add_argument("--boundary-sha", required=True)
    parser.add_argument("--workflow-run-id", default="manual-standing-authorization")
    args = parser.parse_args()
    if args.command == "preflight":
        out = preflight(args.boundary_sha)
    elif args.command == "start":
        out = start_attempt(args.boundary_sha, args.workflow_run_id)
    elif args.command == "evaluate":
        out = evaluate(args.boundary_sha)
    elif args.command == "finalize":
        out = finalize(args.boundary_sha)
    else:
        start_attempt(args.boundary_sha, args.workflow_run_id)
        evaluate(args.boundary_sha)
        out = finalize(args.boundary_sha)
    print(json.dumps(out, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
