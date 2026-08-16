from __future__ import annotations

import json
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
        y[:] = 0
        for o in onsets:
            y[times.index(o - 1)] = 1
        # All positives belong to the first onset so its removal leaves one class.
        onsets = [20, 21, 22, 23, 24, 25, 26]
        y[:] = 0
        for t in range(10, 20):
            y[times.index(t)] = 1
    return {"times": times, "y": y.tolist(), "onsets": onsets, "predictions": {engine.PRIMARY: p.tolist(), engine.CLUSTER[0]: p03.tolist(), engine.CLUSTER[1]: p08.tolist()}}


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
        reproduced = None
        if name == "IDENTITY_OR_REPRODUCTION_MISMATCH":
            reproduced = {k: dict(v) for k, v in engine.FROZEN.items()}
            reproduced[engine.PRIMARY]["PR_AUC_LIFT"] += 1e-6
        got = engine.evaluate_locked_predictions(**f, reproduced=reproduced)
        rows.append({"regime": name, "expected": wanted, "observed": got["classification"], "pass": got["classification"] == wanted})
    verdict = "PASS" if all(x["pass"] for x in rows) else "QUALIFICATION_FAIL"
    return {
        "research_id": engine.RID,
        "qualification_verdict": verdict,
        "regimes": rows,
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
