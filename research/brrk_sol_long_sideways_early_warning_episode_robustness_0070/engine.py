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
    PRIMARY: {
        "PR_AUC": 0.7974030713822858,
        "prevalence": 0.45544554455445546,
        "PR_AUC_LIFT": 0.34195752682783037,
        "ROC_AUC": 0.7913043478260869,
    },
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
    return {
        "ROC_AUC": float(roc_auc_score(yy, pp)),
        "PR_AUC": pr,
        "prevalence": prevalence,
        "PR_AUC_LIFT": lift,
        "retention": lift / float(frozen_lift),
    }


def _json_scalar(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def assign_positive_rows(
    times: Sequence[Any],
    y: Sequence[int],
    onsets: Sequence[Any],
    horizon: int = 10,
    session_axis: Sequence[Any] | None = None,
) -> list[Any | None]:
    """Assign positives by session position, never by calendar-day arithmetic."""
    if horizon != 10:
        raise ValueError("0070 horizon drift")
    if len(times) != len(y):
        raise ValueError("times/labels length mismatch")

    axis = list(times if session_axis is None else session_axis)
    if len(axis) != len(set(axis)):
        raise ValueError("session axis contains duplicates")
    pos = {value: i for i, value in enumerate(axis)}
    if any(t not in pos for t in times):
        raise ValueError("eligible row missing from session axis")
    if any(o not in pos for o in onsets):
        raise ValueError("onset missing from session axis")

    onset_positions = sorted((pos[o], o) for o in set(onsets))
    out: list[Any | None] = []
    for t, label in zip(times, y):
        if int(label) != 1:
            out.append(None)
            continue
        i = pos[t]
        future = [(j, o) for j, o in onset_positions if i < j <= i + horizon]
        out.append(min(future, key=lambda x: x[0])[1] if future else None)
    return out


def _close(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= TOL


def _validate_reproduction(
    reproduced: Mapping[str, Mapping[str, float]] | None,
) -> tuple[bool, str | None]:
    if reproduced is None:
        return False, "aggregate reproduction evidence missing"
    for track, refs in FROZEN.items():
        if track not in reproduced:
            return False, f"aggregate reproduction track missing {track}"
        for key, expected in refs.items():
            if key not in reproduced[track]:
                return False, f"aggregate reproduction metric missing {track} {key}"
            if not _close(reproduced[track][key], expected):
                return False, f"aggregate reproduction mismatch {track} {key}"
    return True, None


def evaluate_locked_predictions(
    *,
    times: Sequence[Any],
    y: Sequence[int],
    predictions: Mapping[str, Sequence[float]],
    onsets: Sequence[Any],
    reproduced: Mapping[str, Mapping[str, float]] | None,
    session_axis: Sequence[Any] | None = None,
) -> dict[str, Any]:
    required = (PRIMARY,) + CLUSTER
    n = len(times)
    if len(y) != n:
        return _result(INVALID, False, False, [], onsets, {}, "times/labels length mismatch")
    if any(k not in predictions for k in required):
        return _result(INVALID, False, False, [], onsets, {}, "required frozen prediction track missing")
    if any(len(predictions[k]) != n for k in required):
        return _result(INVALID, False, False, [], onsets, {}, "prediction length mismatch")

    reproduction_valid, reproduction_reason = _validate_reproduction(reproduced)
    if not reproduction_valid:
        return _result(INVALID, False, False, [], onsets, {}, reproduction_reason)

    unique_onsets = list(dict.fromkeys(onsets))
    if len(unique_onsets) != 7:
        return _result(
            INCONCLUSIVE,
            True,
            True,
            [],
            unique_onsets,
            {},
            "unique onset support is not exactly seven",
        )

    try:
        assignment = assign_positive_rows(
            times,
            y,
            unique_onsets,
            horizon=10,
            session_axis=session_axis,
        )
    except (TypeError, ValueError):
        return _result(
            INVALID,
            False,
            True,
            [],
            unique_onsets,
            {},
            "deterministic session-axis assignment invalid",
        )

    if any(int(label) == 1 and a is None for label, a in zip(y, assignment)):
        return _result(
            INVALID,
            False,
            True,
            assignment,
            unique_onsets,
            {},
            "positive row has no deterministic onset assignment",
        )

    assigned_positive_onsets = {
        a for label, a in zip(y, assignment) if int(label) == 1 and a is not None
    }
    if set(unique_onsets) != assigned_positive_onsets:
        return _result(
            INCONCLUSIVE,
            True,
            True,
            assignment,
            unique_onsets,
            {},
            "one or more unique onsets has no assigned positive warning row",
        )

    axis = list(times if session_axis is None else session_axis)
    axis_pos = {value: i for i, value in enumerate(axis)}
    folds: dict[str, list[dict[str, Any]]] = {k: [] for k in required}
    try:
        for onset in sorted(unique_onsets, key=lambda o: axis_pos[o]):
            keep = np.asarray(
                [not (int(label) == 1 and a == onset) for label, a in zip(y, assignment)],
                dtype=bool,
            )
            yy = np.asarray(y, dtype=int)[keep]
            for track in required:
                pp = np.asarray(predictions[track], dtype=float)[keep]
                m = metrics(yy, pp, FROZEN[track]["PR_AUC_LIFT"])
                folds[track].append(
                    {
                        "onset": _json_scalar(onset),
                        "n": int(len(yy)),
                        "positives": int(yy.sum()),
                        **m,
                    }
                )
    except (ValueError, IndexError):
        return _result(
            INCONCLUSIVE,
            True,
            True,
            assignment,
            unique_onsets,
            folds,
            "one or more required LOEO metrics undefined",
        )

    p02 = folds[PRIMARY]
    g2 = all(x["PR_AUC_LIFT"] > 0.0 and x["ROC_AUC"] > 0.50 for x in p02)
    median_retention = float(np.median([x["retention"] for x in p02]))
    retention_count = sum(x["retention"] >= 0.50 for x in p02)
    cluster_pass = any(
        all(x["PR_AUC_LIFT"] > 0.0 for x in folds[t])
        and float(np.median([x["retention"] for x in folds[t]])) >= 0.50
        for t in CLUSTER
    )
    passed = g2 and median_retention >= 0.75 and retention_count >= 6 and cluster_pass
    return _result(
        PASS if passed else FAIL,
        True,
        True,
        assignment,
        unique_onsets,
        folds,
        None,
        median_retention,
        retention_count,
        cluster_pass,
    )


def _result(
    classification: str,
    execution_valid: bool,
    reproduction_valid: bool,
    assignment: Sequence[Any | None],
    unique_onsets: Sequence[Any],
    folds: Mapping[str, Any],
    reason: str | None,
    median_retention: float | None = None,
    retention_count: int | None = None,
    cluster_pass: bool | None = None,
) -> dict[str, Any]:
    return {
        "research_id": RID,
        "classification": classification,
        "execution_valid": bool(execution_valid),
        "evidence_tier": "RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS",
        "full_window_reproduction": {
            "passed": bool(reproduction_valid),
            "absolute_tolerance": TOL,
        },
        "unique_onsets": [_json_scalar(x) for x in unique_onsets],
        "assignment": [_json_scalar(x) for x in assignment],
        "P02_folds": list(folds.get(PRIMARY, [])),
        "P02_median_retention": median_retention,
        "P02_retention_gte_0_50_count": retention_count,
        "corroborative_cluster": {t: list(folds.get(t, [])) for t in CLUSTER},
        "corroborative_cluster_pass": cluster_pass,
        "source_read_counts": None,
        "network_fetches": None,
        "reason": reason,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
