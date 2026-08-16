from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

RID = "BRRK-SOL-LONG-SIDEWAYS-EARLY-WARNING-EPISODE-ROBUSTNESS-0070"
PASS = "PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION"
FAIL = "FAIL_LOCKED_EPISODE_ROBUSTNESS_REPLICATION"
INCONCLUSIVE = "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_EPISODE_SUPPORT"
INVALID = "INVALID_EXECUTION"

PRIMARY = "P02_RAW_ELASTIC_NET_LOGIT|SOL|T4_LONG_SIDEWAYS"
CLUSTER = (
    "P03_VALIDATION_SCREENED_SIGNAL_LOGIT|SOL|T4_LONG_SIDEWAYS",
    "P08_STACKED_PROBABILITY_ENSEMBLE|SOL|T4_LONG_SIDEWAYS",
)
FROZEN = {
    PRIMARY: {"PR_AUC": 0.7974030713822858, "prevalence": 0.45544554455445546, "PR_AUC_LIFT": 0.34195752682783037, "ROC_AUC": 0.7913043478260869},
    CLUSTER[0]: {"PR_AUC_LIFT": 0.28384632505003554, "ROC_AUC": 0.8027667984189722},
    CLUSTER[1]: {"PR_AUC_LIFT": 0.28384632505003554, "ROC_AUC": 0.8027667984189722},
}
TOL = 1e-12

@dataclass(frozen=True)
class FoldMetric:
    onset: Any
    n: int
    positives: int
    roc_auc: float
    pr_auc: float
    prevalence: float
    pr_auc_lift: float
    retention: float


def metrics(y: Sequence[int], p: Sequence[float], frozen_lift: float) -> dict[str, float]:
    yy = np.asarray(y, dtype=int)
    pp = np.asarray(p, dtype=float)
    if len(yy) == 0 or len(yy) != len(pp) or len(np.unique(yy)) != 2:
        raise ValueError("metric undefined")
    prevalence = float(np.mean(yy))
    pr = float(average_precision_score(yy, pp))
    lift = pr - prevalence
    return {"ROC_AUC": float(roc_auc_score(yy, pp)), "PR_AUC": pr, "prevalence": prevalence, "PR_AUC_LIFT": lift, "retention": lift / float(frozen_lift)}


def assign_positive_rows(times: Sequence[Any], y: Sequence[int], onsets: Sequence[Any], horizon: int = 10) -> list[Any | None]:
    if horizon != 10:
        raise ValueError("0070 horizon drift")
    onset_list = sorted(onsets)
    out: list[Any | None] = []
    for t, label in zip(times, y):
        if int(label) != 1:
            out.append(None)
            continue
        future = [o for o in onset_list if t < o <= t + horizon]
        out.append(future[0] if future else None)
    return out


def _close(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= TOL


def evaluate_locked_predictions(*, times: Sequence[Any], y: Sequence[int], predictions: Mapping[str, Sequence[float]], onsets: Sequence[Any], reproduced: Mapping[str, Mapping[str, float]] | None = None) -> dict[str, Any]:
    if len(set(onsets)) != 7:
        return _result(INCONCLUSIVE, False, [], {}, "unique onset support is not exactly seven")
    required = (PRIMARY,) + CLUSTER
    if any(k not in predictions for k in required):
        return _result(INVALID, False, [], {}, "required frozen prediction track missing")
    if reproduced is not None:
        for track, refs in FROZEN.items():
            if track not in reproduced:
                return _result(INVALID, False, [], {}, "aggregate reproduction track missing")
            for key, expected in refs.items():
                if key in reproduced[track] and not _close(reproduced[track][key], expected):
                    return _result(INVALID, False, [], {}, f"aggregate reproduction mismatch {track} {key}")
    assignment = assign_positive_rows(times, y, onsets)
    if any(int(label) == 1 and a is None for label, a in zip(y, assignment)):
        return _result(INVALID, False, [], {}, "positive row has no deterministic onset assignment")
    folds: dict[str, list[dict[str, Any]]] = {k: [] for k in required}
    try:
        for onset in sorted(set(onsets)):
            keep = np.asarray([not (int(label) == 1 and a == onset) for label, a in zip(y, assignment)], dtype=bool)
            yy = np.asarray(y, dtype=int)[keep]
            for track in required:
                pp = np.asarray(predictions[track], dtype=float)[keep]
                m = metrics(yy, pp, FROZEN[track]["PR_AUC_LIFT"])
                folds[track].append({"onset": onset, "n": int(len(yy)), "positives": int(yy.sum()), **m})
    except (ValueError, IndexError):
        return _result(INCONCLUSIVE, False, assignment, folds, "one or more required LOEO metrics undefined")
    p02 = folds[PRIMARY]
    g2 = all(x["PR_AUC_LIFT"] > 0.0 and x["ROC_AUC"] > 0.50 for x in p02)
    median_retention = float(np.median([x["retention"] for x in p02]))
    retention_count = sum(x["retention"] >= 0.50 for x in p02)
    cluster_pass = any(all(x["PR_AUC_LIFT"] > 0.0 for x in folds[t]) and float(np.median([x["retention"] for x in folds[t]])) >= 0.50 for t in CLUSTER)
    passed = g2 and median_retention >= 0.75 and retention_count >= 6 and cluster_pass
    return _result(PASS if passed else FAIL, True, assignment, folds, None, median_retention, retention_count, cluster_pass)


def _result(classification: str, execution_valid: bool, assignment: Sequence[Any | None], folds: Mapping[str, Any], reason: str | None, median_retention: float | None = None, retention_count: int | None = None, cluster_pass: bool | None = None) -> dict[str, Any]:
    return {
        "research_id": RID,
        "classification": classification,
        "execution_valid": bool(execution_valid),
        "evidence_tier": "RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS",
        "assignment": list(assignment),
        "P02_folds": list(folds.get(PRIMARY, [])),
        "P02_median_retention": median_retention,
        "P02_retention_gte_0_50_count": retention_count,
        "corroborative_cluster": {t: list(folds.get(t, [])) for t in CLUSTER},
        "corroborative_cluster_pass": cluster_pass,
        "reason": reason,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
