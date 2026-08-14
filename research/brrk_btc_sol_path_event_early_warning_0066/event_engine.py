from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

import numpy as np
import pandas as pd

SCAN_HORIZONS = (10, 15, 20, 30, 45, 60, 90, 120, 180, 240)
WARNING_HORIZONS = (1, 3, 5, 10, 20)
ASSETS = ("BTC", "SOL")
VALID_END = pd.Timestamp("2023-12-31")
FINAL_START = pd.Timestamp("2024-01-01")
FINAL_END = pd.Timestamp("2025-11-15")

DOWN_GRADE = {
    10: "D1_SHORT", 15: "D1_SHORT", 20: "D1_SHORT",
    30: "D2_MEDIUM", 45: "D2_MEDIUM", 60: "D2_MEDIUM",
    90: "D3_LONG", 120: "D3_LONG",
    180: "D4_SECULAR", 240: "D4_SECULAR",
}
SIDEWAYS_GRADE = {
    10: "S1_SHORT", 15: "S1_SHORT", 20: "S1_SHORT",
    30: "S2_MEDIUM", 45: "S2_MEDIUM", 60: "S2_MEDIUM",
    90: "S3_LONG", 120: "S3_LONG",
    180: "S4_SECULAR", 240: "S4_SECULAR",
}
DOWN_GRADE_RANK = {"D1_SHORT": 1, "D2_MEDIUM": 2, "D3_LONG": 3, "D4_SECULAR": 4}
SIDEWAYS_GRADE_RANK = {"S1_SHORT": 1, "S2_MEDIUM": 2, "S3_LONG": 3, "S4_SECULAR": 4}


def naive_index(index: pd.Index) -> pd.DatetimeIndex:
    out = pd.DatetimeIndex(pd.to_datetime(index))
    if out.tz is not None:
        out = out.tz_convert("UTC").tz_localize(None)
    return out


def with_naive_index(obj: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    out = obj.copy()
    out.index = naive_index(out.index)
    return out.sort_index()


def _path_slope_tstat(values: np.ndarray) -> float:
    y = np.asarray(values, dtype=float)
    if len(y) < 3 or not np.isfinite(y).all():
        return float("nan")
    x = np.arange(len(y), dtype=float)
    xc = x - x.mean()
    yc = y - y.mean()
    sxx = float(np.dot(xc, xc))
    if sxx <= 0:
        return float("nan")
    beta = float(np.dot(xc, yc) / sxx)
    resid = yc - beta * xc
    df = len(y) - 2
    s2 = float(np.dot(resid, resid) / df) if df > 0 else float("nan")
    if not np.isfinite(s2):
        return float("nan")
    if s2 <= 0:
        if beta > 0:
            return float("inf")
        if beta < 0:
            return float("-inf")
        return 0.0
    se = math.sqrt(s2 / sxx)
    return beta / se if se > 0 else float("nan")


def _severity(z_mae: float) -> str | None:
    if not np.isfinite(z_mae) or z_mae < 1.5:
        return None
    if z_mae < 2.5:
        return "S1"
    if z_mae < 4.0:
        return "S2"
    return "S3"


def _scan_asset(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    f = with_naive_index(frame)
    if "close" not in f.columns:
        raise ValueError(f"{asset} close missing")
    close = pd.to_numeric(f["close"], errors="coerce").astype(float)
    if (close <= 0).any() or not np.isfinite(close.to_numpy()).all():
        raise ValueError(f"{asset} invalid close")
    idx = close.index
    logc = np.log(close.to_numpy(dtype=float))
    logret = pd.Series(np.diff(logc, prepend=np.nan), index=idx)
    sigma60 = logret.rolling(60, min_periods=30).std(ddof=1).shift(1)

    rows: list[dict] = []
    max_h = max(SCAN_HORIZONS)
    for i in range(len(idx) - max_h):
        sig = float(sigma60.iloc[i]) if np.isfinite(sigma60.iloc[i]) else float("nan")
        if not np.isfinite(sig) or sig <= 0:
            continue
        stats: dict[int, dict[str, float]] = {}
        for h in SCAN_HORIZONS:
            y = logc[i:i + h + 1]
            tstat = _path_slope_tstat(y)
            r_h = float(y[-1] - y[0])
            mae = float(max(0.0, -(np.min(y - y[0]))))
            path_range = float(np.max(y) - np.min(y))
            stats[h] = {"tstat": tstat, "return": r_h, "mae": mae, "range": path_range}

        h_star = min(SCAN_HORIZONS, key=lambda h: (-abs(stats[h]["tstat"]), h))
        st = stats[h_star]
        scale = sig * math.sqrt(float(h_star))
        event_type: str | None = None
        grade: str | None = None
        sev: str | None = None
        chosen_h: int | None = None
        chosen = st
        z_mae = st["mae"] / scale if scale > 0 else float("nan")
        if st["tstat"] <= -2.5 and st["return"] <= -1.0 * scale and st["mae"] >= 1.5 * scale:
            event_type = "DOWN"
            grade = DOWN_GRADE[h_star]
            sev = _severity(z_mae)
            chosen_h = h_star
        else:
            qualified: list[int] = []
            for h in SCAN_HORIZONS:
                hs = stats[h]
                scl = sig * math.sqrt(float(h))
                if abs(hs["tstat"]) <= 1.25 and abs(hs["return"]) <= 0.50 * scl and hs["range"] <= 1.75 * scl:
                    qualified.append(h)
            if qualified:
                chosen_h = max(qualified)
                chosen = stats[chosen_h]
                event_type = "SIDEWAYS"
                grade = SIDEWAYS_GRADE[chosen_h]
                scale = sig * math.sqrt(float(chosen_h))
                z_mae = chosen["mae"] / scale if scale > 0 else float("nan")

        if event_type is not None and chosen_h is not None and grade is not None:
            rows.append({
                "asset": asset,
                "date": idx[i],
                "position": i,
                "event_type": event_type,
                "duration_grade": grade,
                "H_star": int(chosen_h),
                "severity": sev,
                "sigma60": sig,
                "slope_t_stat": float(chosen["tstat"]),
                "terminal_log_return": float(chosen["return"]),
                "mae_magnitude": float(chosen["mae"]),
                "z_mae": float(z_mae),
                "path_log_range": float(chosen["range"]),
            })
    if not rows:
        return pd.DataFrame(columns=["asset", "date", "position", "event_type", "duration_grade", "H_star", "severity", "sigma60", "slope_t_stat", "terminal_log_return", "mae_magnitude", "z_mae", "path_log_range"]).set_index("date")
    return pd.DataFrame(rows).set_index("date").sort_index()


def _grade_rank(event_type: str, grade: str) -> int:
    if event_type == "DOWN":
        return DOWN_GRADE_RANK[grade]
    return SIDEWAYS_GRADE_RANK[grade]


def _extract_asset_onsets(candidates: pd.DataFrame, index: pd.DatetimeIndex, asset: str) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    risk_masks = {
        "DOWN": pd.Series(True, index=index, dtype=bool),
        "SIDEWAYS": pd.Series(True, index=index, dtype=bool),
    }
    accepted: list[dict] = []
    if candidates.empty:
        return pd.DataFrame(columns=list(candidates.columns) + ["suppression_end_position", "suppression_end_date"]), risk_masks

    pos_to_row = {int(row.position): row for row in candidates.itertuples()}
    for event_type in ("DOWN", "SIDEWAYS"):
        proposals: list[int] = []
        prev_key: tuple[str, str] | None = None
        prev_pos: int | None = None
        for pos in sorted(pos_to_row):
            row = pos_to_row[pos]
            if row.event_type != event_type:
                prev_key = None
                prev_pos = None
                continue
            key = (row.event_type, row.duration_grade)
            contiguous_same = prev_pos is not None and pos == prev_pos + 1 and key == prev_key
            if not contiguous_same:
                proposals.append(pos)
            prev_key, prev_pos = key, pos

        last_onset: int | None = None
        last_rank = -1
        suppression_end = -1
        for pos in proposals:
            row = pos_to_row[pos]
            rank = _grade_rank(event_type, row.duration_grade)
            accept = False
            if last_onset is None or pos > suppression_end:
                accept = True
            elif rank > last_rank and pos - last_onset >= 10:
                accept = True
            if not accept:
                continue
            end_pos = min(len(index) - 1, pos + int(math.ceil(float(row.H_star) / 2.0)))
            risk_masks[event_type].iloc[pos:end_pos + 1] = False
            rec = row._asdict()
            rec.pop("Index", None)
            rec["date"] = index[pos]
            rec["suppression_end_position"] = int(end_pos)
            rec["suppression_end_date"] = index[end_pos]
            accepted.append(rec)
            last_onset = pos
            last_rank = rank
            suppression_end = end_pos

    if not accepted:
        events = pd.DataFrame(columns=list(candidates.columns) + ["suppression_end_position", "suppression_end_date"])
    else:
        events = pd.DataFrame(accepted).set_index("date").sort_index()
    return events, risk_masks


@dataclass
class EventBundle:
    events: pd.DataFrame
    candidates: pd.DataFrame
    risk_masks: dict[tuple[str, str], pd.Series]
    asset_indices: dict[str, pd.DatetimeIndex]


def build_event_atlas(frames: Mapping[str, pd.DataFrame]) -> EventBundle:
    all_candidates: list[pd.DataFrame] = []
    all_events: list[pd.DataFrame] = []
    risk_masks: dict[tuple[str, str], pd.Series] = {}
    asset_indices: dict[str, pd.DatetimeIndex] = {}
    for asset in ASSETS:
        if asset not in frames:
            raise ValueError(f"missing event asset {asset}")
        f = with_naive_index(frames[asset])
        idx = f.index
        asset_indices[asset] = idx
        candidates = _scan_asset(f, asset)
        events, masks = _extract_asset_onsets(candidates, idx, asset)
        all_candidates.append(candidates)
        all_events.append(events)
        for etype, mask in masks.items():
            risk_masks[(asset, etype)] = mask
    candidates_all = pd.concat(all_candidates, axis=0).sort_index() if all_candidates else pd.DataFrame()
    events_all = pd.concat(all_events, axis=0).sort_index() if all_events else pd.DataFrame()
    return EventBundle(events=events_all, candidates=candidates_all, risk_masks=risk_masks, asset_indices=asset_indices)


def event_matches_target(row: pd.Series | object, target: str) -> bool:
    event_type = getattr(row, "event_type", None) if not isinstance(row, pd.Series) else row.get("event_type")
    grade = getattr(row, "duration_grade", None) if not isinstance(row, pd.Series) else row.get("duration_grade")
    severity = getattr(row, "severity", None) if not isinstance(row, pd.Series) else row.get("severity")
    if target == "T1_ANY_DOWN":
        return event_type == "DOWN"
    if target == "T2_MAJOR_DOWN":
        return event_type == "DOWN" and (DOWN_GRADE_RANK.get(str(grade), 0) >= 2 or severity in {"S2", "S3"})
    if target == "T3_ANY_SIDEWAYS":
        return event_type == "SIDEWAYS"
    if target == "T4_LONG_SIDEWAYS":
        return event_type == "SIDEWAYS" and SIDEWAYS_GRADE_RANK.get(str(grade), 0) >= 2
    raise KeyError(target)


def target_event_type(target: str) -> str:
    if target in {"T1_ANY_DOWN", "T2_MAJOR_DOWN"}:
        return "DOWN"
    if target in {"T3_ANY_SIDEWAYS", "T4_LONG_SIDEWAYS"}:
        return "SIDEWAYS"
    raise KeyError(target)


def qualifying_events(bundle: EventBundle, asset: str, target: str) -> pd.DataFrame:
    if bundle.events.empty:
        return bundle.events.copy()
    e = bundle.events[bundle.events["asset"] == asset]
    keep = [event_matches_target(row, target) for row in e.itertuples()]
    return e.loc[np.asarray(keep, dtype=bool)].copy()


def build_warning_labels(bundle: EventBundle, asset: str, target: str, warning_horizon: int, prediction_index: pd.DatetimeIndex) -> pd.Series:
    if warning_horizon not in WARNING_HORIZONS:
        raise ValueError("warning horizon drift")
    aidx = bundle.asset_indices[asset]
    pos_map = {d: i for i, d in enumerate(aidx)}
    risk = bundle.risk_masks[(asset, target_event_type(target))]
    q = qualifying_events(bundle, asset, target)
    onset_positions = np.array(sorted(int(x) for x in q["position"].tolist()), dtype=int) if len(q) else np.array([], dtype=int)
    y = pd.Series(np.nan, index=prediction_index, dtype=float)
    for d in prediction_index:
        pos = pos_map.get(pd.Timestamp(d))
        if pos is None or not bool(risk.iloc[pos]):
            continue
        y.loc[d] = 0.0
        if len(onset_positions):
            j = int(np.searchsorted(onset_positions, pos, side="right"))
            if j < len(onset_positions) and int(onset_positions[j]) <= pos + warning_horizon:
                y.loc[d] = 1.0
    return y


def unique_onset_support(bundle: EventBundle, asset: str, target: str, warning_horizon: int, prediction_index: pd.DatetimeIndex) -> dict[str, int | bool]:
    q = qualifying_events(bundle, asset, target)
    if q.empty:
        return {"train_validation_unique_onsets": 0, "final_unique_onsets": 0, "support_pass": False}
    pset = set(pd.DatetimeIndex(prediction_index))
    aidx = bundle.asset_indices[asset]
    risk = bundle.risk_masks[(asset, target_event_type(target))]
    valid_onsets: list[pd.Timestamp] = []
    for row in q.itertuples():
        pos = int(row.position)
        has_precursor = False
        for k in range(1, warning_horizon + 1):
            j = pos - k
            if j >= 0 and aidx[j] in pset and bool(risk.iloc[j]):
                has_precursor = True
                break
        if has_precursor:
            valid_onsets.append(pd.Timestamp(row.Index))
    tv = sum(d <= VALID_END for d in valid_onsets)
    fe = sum(FINAL_START <= d <= FINAL_END for d in valid_onsets)
    return {
        "train_validation_unique_onsets": int(tv),
        "final_unique_onsets": int(fe),
        "support_pass": bool(tv >= 8 and fe >= 3),
    }


def event_records(bundle: EventBundle) -> list[dict]:
    if bundle.events.empty:
        return []
    out: list[dict] = []
    for idx, row in bundle.events.iterrows():
        rec = {"date": pd.Timestamp(idx).isoformat()}
        for k, v in row.items():
            if isinstance(v, pd.Timestamp):
                rec[k] = v.isoformat()
            elif isinstance(v, (np.integer,)):
                rec[k] = int(v)
            elif isinstance(v, (np.floating,)):
                rec[k] = None if not np.isfinite(v) else float(v)
            elif pd.isna(v):
                rec[k] = None
            else:
                rec[k] = v
        out.append(rec)
    return out
