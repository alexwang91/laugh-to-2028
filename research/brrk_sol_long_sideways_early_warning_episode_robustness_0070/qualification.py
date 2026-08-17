from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np

from research.brrk_sol_long_sideways_early_warning_episode_robustness_0070 import engine


def _fixture(kind: str) -> dict[str, Any]:
    onsets = [20, 40, 60, 80, 100, 120, 140]
    times = list(range(10, 151))
    y = np.zeros(len(times), dtype=int)
    for o in onsets:
        for t in range(o - 3, o):
            y[times.index(t)] = 1
    base = np.linspace(0.05, 0.35, len(times))
    p = base.copy()
    p[y == 1] = 0.90
    p03 = p * 0.96 + 0.02
    p08 = p03.copy()
    if kind == "SINGLE_EPISODE_DOMINANT":
        p[:] = 0.45
        first = onsets[0]
        for t in range(first - 3, first):
            p[times.index(t)] = 0.99
    if kind == "CLUSTER_FAIL":
        p03 = 1.0 - p03
        p08 = 1.0 - p08
    if kind == "INSUFFICIENT_EPISODES":
        onsets = onsets[:6]
        y[:] = 0
        for o in onsets:
            for t in range(o - 3, o):
                y[times.index(t)] = 1
    if kind == "UNDEFINED_FOLD":
        onsets = [20, 21, 22, 23, 24, 25, 26]
        y[:] = 0
        for t in range(10, 20):
            y[times.index(t)] = 1
    return {
        "times": times,
        "y": y.tolist(),
        "onsets": onsets,
        "predictions": {
            engine.PRIMARY: p.tolist(),
            engine.CLUSTER[0]: p03.tolist(),
            engine.CLUSTER[1]: p08.tolist(),
        },
    }


def _exact_reproduction() -> dict[str, dict[str, float]]:
    return {k: dict(v) for k, v in engine.FROZEN.items()}


def _datetime_session_axis_check() -> bool:
    f = _fixture("EXACT_PASS")
    start = date(2025, 1, 1)
    dated_times = [start + timedelta(days=i) for i in range(len(f["times"]))]
    remap = dict(zip(f["times"], dated_times))
    got = engine.evaluate_locked_predictions(
        times=dated_times,
        session_axis=dated_times,
        y=f["y"],
        onsets=[remap[o] for o in f["onsets"]],
        predictions=f["predictions"],
        reproduced=_exact_reproduction(),
    )
    return got["classification"] == engine.PASS and got["execution_valid"] is True


def _strict_reproduction_checks() -> dict[str, bool]:
    f = _fixture("EXACT_PASS")
    missing_all = engine.evaluate_locked_predictions(**f, reproduced=None)

    missing_metric = _exact_reproduction()
    del missing_metric[engine.PRIMARY]["ROC_AUC"]
    missing_one = engine.evaluate_locked_predictions(**f, reproduced=missing_metric)

    bad_length = dict(f)
    bad_predictions = {k: list(v) for k, v in f["predictions"].items()}
    bad_predictions[engine.PRIMARY] = bad_predictions[engine.PRIMARY][:-1]
    bad_length["predictions"] = bad_predictions
    bad_len_result = engine.evaluate_locked_predictions(**bad_length, reproduced=_exact_reproduction())

    return {
        "missing_reproduction_rejected": missing_all["classification"] == engine.INVALID,
        "missing_reproduction_metric_rejected": missing_one["classification"] == engine.INVALID,
        "prediction_length_mismatch_rejected": bad_len_result["classification"] == engine.INVALID,
    }


def qualify() -> dict[str, Any]:
    expected = {
        "EXACT_PASS": engine.PASS,
        "SINGLE_EPISODE_DOMINANT": engine.FAIL,
        "CLUSTER_FAIL": engine.FAIL,
        "INSUFFICIENT_EPISODES": engine.INCONCLUSIVE,
        "UNDEFINED_FOLD": engine.INCONCLUSIVE,
        "IDENTITY_OR_REPRODUCTION_MISMATCH": engine.INVALID,
    }
    rows = []
    for name, wanted in expected.items():
        f = _fixture("EXACT_PASS" if name == "IDENTITY_OR_REPRODUCTION_MISMATCH" else name)
        reproduced = _exact_reproduction()
        if name == "IDENTITY_OR_REPRODUCTION_MISMATCH":
            reproduced[engine.PRIMARY]["PR_AUC_LIFT"] += 1e-6
        got = engine.evaluate_locked_predictions(**f, reproduced=reproduced)
        expected_execution_valid = wanted != engine.INVALID
        rows.append(
            {
                "regime": name,
                "expected": wanted,
                "observed": got["classification"],
                "execution_valid": got["execution_valid"],
                "expected_execution_valid": expected_execution_valid,
                "pass": got["classification"] == wanted
                and got["execution_valid"] is expected_execution_valid,
            }
        )

    implementation_checks = {
        "session_horizon_uses_ordered_sessions_not_calendar_arithmetic": _datetime_session_axis_check(),
        **_strict_reproduction_checks(),
    }
    verdict = "PASS" if all(x["pass"] for x in rows) and all(implementation_checks.values()) else "QUALIFICATION_FAIL"
    return {
        "research_id": engine.RID,
        "qualification_verdict": verdict,
        "regimes": rows,
        "implementation_checks": implementation_checks,
        "historical_or_0069_evidence_reads": 0,
        "network_fetches": 0,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def main(output: str | None = None) -> int:
    result = qualify()
    text = json.dumps(result, indent=2, sort_keys=True)
    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if result["qualification_verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
