from __future__ import annotations

"""Serialization boundary containing only timestamps and frozen S1-S4 values."""

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

RESEARCH_ID = "BRRK-EXHAUSTION-PULSE-0046"
PRIMARY_AXES = (
    "S1_MOMENTUM_DECELERATION",
    "S2_TREND_DISAGREEMENT",
    "S3_PRICE_STRUCTURE",
    "S4_VOL_DOWNSIDE",
)


class PredictorArtifactInvalid(RuntimeError):
    pass


@dataclass(frozen=True)
class PredictorArtifact:
    axes: pd.DataFrame
    predictor_digest: str
    artifact_payload_sha256: str


def _json_sha(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def rows_from_state(state: pd.DataFrame) -> list[list[object]]:
    rows: list[list[object]] = []
    for idx, row in state[list(PRIMARY_AXES)].iterrows():
        rows.append([str(pd.Timestamp(idx).date()), *[float(row[a]) for a in PRIMARY_AXES]])
    return rows


def predictor_digest_from_rows(rows: list[list[object]]) -> str:
    return _json_sha(rows)


def build_payload(state: pd.DataFrame) -> dict[str, object]:
    if list(state.columns) != list(PRIMARY_AXES):
        raise PredictorArtifactInvalid("predictor columns must be exactly frozen S1-S4 in order")
    values = state.to_numpy(dtype=float)
    if not len(state) or not np.isfinite(values).all():
        raise PredictorArtifactInvalid("predictor path must be nonempty and finite")
    rows = rows_from_state(state)
    payload: dict[str, object] = {
        "schema_version": 1,
        "research_id": RESEARCH_ID,
        "artifact_type": "LABEL_BLIND_PREDICTOR_PATH",
        "primary_axes": list(PRIMARY_AXES),
        "start": rows[0][0],
        "end": rows[-1][0],
        "sessions": len(rows),
        "rows": rows,
        "predictor_digest": predictor_digest_from_rows(rows),
        "contains_only_timestamps_and_s1_s4": True,
        "label_data_accessed": False,
        "event_taxonomy_loaded": False,
        "portfolio_economics_executed": False,
        "production_authorized": False,
    }
    payload["artifact_payload_sha256_without_self_hash"] = _json_sha(payload)
    return payload


def _atomic_write(path: Path, payload: dict[str, object]) -> None:
    if path.exists():
        raise PredictorArtifactInvalid(f"predictor artifact is create-only: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def write_predictor_artifact(path: Path, state: pd.DataFrame) -> dict[str, object]:
    payload = build_payload(state)
    _atomic_write(path, payload)
    return payload


def read_predictor_artifact(path: Path) -> PredictorArtifact:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected_hash = payload.pop("artifact_payload_sha256_without_self_hash", None)
    observed_hash = _json_sha(payload)
    payload["artifact_payload_sha256_without_self_hash"] = expected_hash
    if expected_hash != observed_hash:
        raise PredictorArtifactInvalid("predictor artifact payload hash mismatch")
    if payload.get("research_id") != RESEARCH_ID or payload.get("artifact_type") != "LABEL_BLIND_PREDICTOR_PATH":
        raise PredictorArtifactInvalid("predictor artifact identity mismatch")
    if payload.get("primary_axes") != list(PRIMARY_AXES):
        raise PredictorArtifactInvalid("predictor artifact axes drifted")
    if payload.get("contains_only_timestamps_and_s1_s4") is not True:
        raise PredictorArtifactInvalid("predictor artifact contains unapproved information")
    if payload.get("label_data_accessed") is not False or payload.get("event_taxonomy_loaded") is not False:
        raise PredictorArtifactInvalid("predictor artifact does not prove label-blind construction")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise PredictorArtifactInvalid("predictor rows missing")
    if any(not isinstance(row, list) or len(row) != 5 for row in rows):
        raise PredictorArtifactInvalid("each predictor row must contain date plus exactly four axes")
    dates = pd.to_datetime([row[0] for row in rows])
    values = np.asarray([row[1:] for row in rows], dtype=np.float64)
    if not np.isfinite(values).all():
        raise PredictorArtifactInvalid("non-finite predictor value")
    if not pd.Index(dates).is_monotonic_increasing or pd.Index(dates).duplicated().any():
        raise PredictorArtifactInvalid("predictor timestamps must be unique and increasing")
    if predictor_digest_from_rows(rows) != payload.get("predictor_digest"):
        raise PredictorArtifactInvalid("predictor digest mismatch")
    frame = pd.DataFrame(values, index=dates, columns=PRIMARY_AXES)
    return PredictorArtifact(
        axes=frame,
        predictor_digest=str(payload["predictor_digest"]),
        artifact_payload_sha256=str(expected_hash),
    )
