from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from research.brrk_btc_sol_path_event_early_warning_runtime_qualified_0067 import engine as opt


def test_frozen_runtime_shape_and_authority() -> None:
    root = Path(__file__).resolve().parents[2]
    d = Path(__file__).resolve().parent
    p = json.loads((d / "PREREGISTRATION.json").read_text())
    q = json.loads((d / "QUALIFICATION_PREREGISTRATION.json").read_text())
    assert opt.RID == "BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-RUNTIME-QUALIFIED-0067"
    assert opt.WORKERS == 4
    assert p["trial_accounting"]["validation_tuning_executions"] == 1632
    assert p["physical_compute_accounting"]["total_estimator_fit_calls_declared"] == 42912
    assert p["simultaneous_inference"]["seed"] == 660066
    assert q["synthetic_generator"]["seed"] == 670067
    assert q["environment"]["runner_label"] == "ubuntu-24.04"
    assert q["environment"]["process_worker_count"] == 4
    assert q["shape_contract"]["total_estimator_fit_calls"] == 42912
    assert q["resource_acceptance"]["total_wall_clock_pass_max_seconds"] == 10800
    for name in ("RUN_ATTEMPT.marker", "PRIMARY_RESULT.json", "EVIDENCE.json", "EXECUTION.json", "RUN_ONCE.marker"):
        assert not (d / name).exists()
    assert root.exists()


def test_predictive_bootstrap_parallel_matches_reference_small_fixture() -> None:
    rng = np.random.default_rng(670067)
    tracks = {}
    n = 180
    for i in range(3):
        y = ((np.arange(n) + i) % (5 + i) == 0).astype(float)
        p = np.clip(0.15 + 0.7 * y + 0.08 * rng.normal(size=n), 0.0, 1.0)
        tracks[str(i)] = (y, p)
    a = opt.ref._bootstrap_predictive_lcbs(tracks, block_length=30, reps=40, seed=660066)
    b = opt._bootstrap_predictive_parallel(tracks, block_length=30, reps=40, seed=660066)
    assert np.isclose(a[0], b[0], atol=1e-12, rtol=1e-10)
    assert a[2] == b[2]
    for k in a[1]:
        assert np.isclose(a[1][k], b[1][k], atol=1e-12, rtol=1e-10)


def test_economic_bootstrap_vectorization_matches_reference() -> None:
    x = np.arange(240, dtype=float)
    relative = {
        "A": 0.0002 + 0.0010 * np.sin(x / 9.0),
        "B": 0.0001 + 0.0012 * np.cos(x / 13.0),
    }
    a = opt.ref._economic_mbb(relative)
    b = opt._economic_mbb_vectorized(relative)
    assert np.isclose(a[0], b[0], atol=1e-12, rtol=1e-10)
    for k in a[1]:
        assert np.isclose(a[1][k], b[1][k], atol=1e-12, rtol=1e-10)
