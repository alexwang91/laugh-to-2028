from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from research.brrk_idle_cash_passive_accrual_robustness_0064 import run_once as r


def _write_synthetic_history(tmp_path: Path) -> tuple[Path, Path, Path]:
    n = r.EXPECTED_N
    dates = pd.date_range(r.EXPECTED_START, periods=n, freq="D")
    assert dates[-1] == r.EXPECTED_END
    multiple = r.FINAL_10K_ANCHOR / 10000.0
    daily = multiple ** (1.0 / n) - 1.0
    equity = 10000.0 * np.cumprod(np.full(n, 1.0 + daily))
    eq = pd.DataFrame({"date": dates, "BRRK0011_BASELINE": equity})
    wt = pd.DataFrame({
        "date": dates,
        "BRRK0011_BASELINE__BTC": np.full(n, 0.35),
        "BRRK0011_BASELINE__ETH": np.full(n, 0.35),
    })
    rate_dates = pd.date_range(r.EXPECTED_START - pd.Timedelta(days=1), r.EXPECTED_END, freq="D")
    rf = pd.DataFrame({"observation_date": rate_dates, "DTB3": np.full(len(rate_dates), 5.0)})
    eqp, wtp, rfp = tmp_path / "equity.csv", tmp_path / "weights.csv", tmp_path / "dtb3.csv"
    eq.to_csv(eqp, index=False)
    wt.to_csv(wtp, index=False)
    rf.to_csv(rfp, index=False)
    return eqp, wtp, rfp


def test_full_synthetic_exactly_once_lifecycle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    eqp, wtp, rfp = _write_synthetic_history(tmp_path)
    boundary = "synthetic-boundary-sha"
    monkeypatch.setattr(r, "EQUITY", eqp)
    monkeypatch.setattr(r, "WEIGHTS", wtp)
    monkeypatch.setattr(r, "DTB3", rfp)
    monkeypatch.setattr(r, "ATTEMPT", tmp_path / "RUN_ATTEMPT.marker")
    monkeypatch.setattr(r, "RESULT", tmp_path / "PRIMARY_RESULT.json")
    monkeypatch.setattr(r, "EVIDENCE", tmp_path / "EVIDENCE.json")
    monkeypatch.setattr(r, "EXECUTION", tmp_path / "EXECUTION.json")
    monkeypatch.setattr(r, "FINAL", tmp_path / "RUN_ONCE.marker")
    monkeypatch.setattr(r, "DTB3_SHA256", hashlib.sha256(rfp.read_bytes()).hexdigest())
    monkeypatch.setattr(r, "_git_head", lambda: boundary)
    monkeypatch.setattr(r, "_verify_pinned_blobs", lambda: None)

    pre = r.preflight(boundary)
    assert pre["historical_csv_content_reads"] == 0
    assert pre["scientific_engine_calls"] == 0

    r.start_attempt(boundary, "synthetic-run")
    primary = r.evaluate(boundary)
    assert primary["candidate_cell_count"] == 20
    assert primary["actual_variants_evaluated"] == 20
    assert primary["primary_cell_key"] == "a050_fee100bps"
    assert primary["classification"] == "PASS_PASSIVE_CASH_ACCRUAL_ROBUSTNESS"
    assert primary["chronological_block_sizes"] == [333, 333, 333, 333]
    assert primary["bootstrap"]["block_length"] == 60
    assert primary["bootstrap"]["replicates"] == 4000
    assert primary["bootstrap"]["seed"] == 640064
    assert all(primary["gates"].values())

    evidence = json.loads(r.EVIDENCE.read_text())
    execution = json.loads(r.EXECUTION.read_text())
    assert evidence["input_read_counts"] == {"equity": 1, "weights": 1, "dtb3": 1}
    assert evidence["scientific_engine_calls"] == 1
    assert len(evidence["cells"]) == 20
    assert execution["input_read_counts"] == {"equity": 1, "weights": 1, "dtb3": 1}
    assert execution["scientific_engine_calls"] == 1
    assert execution["candidate_cells_evaluated"] == 20

    marker = r.finalize(boundary)
    assert marker["classification"] == primary["classification"]
    assert marker["historical_input_reads_during_finalize"] == 0
    assert marker["scientific_engine_calls_during_finalize"] == 0
    assert r.FINAL.exists()

    with pytest.raises(r.ControlledRunError):
        r.start_attempt(boundary, "second-run")
    with pytest.raises(r.ControlledRunError):
        r.evaluate(boundary)
    with pytest.raises(r.ControlledRunError):
        r.finalize(boundary)
