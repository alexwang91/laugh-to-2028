from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

RESEARCH_ID = "BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053"
EXPECTED_PAYLOAD_SHA256 = "471b54991ae648b79433285f073ea7bc813663319b6e2389c1682dad1a319135"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
BAR_INTERVAL_MS = 14_400_000
HORIZONS_4H = (120, 360, 720, 1440)
FAST_WEIGHTS = (0.15, 0.25, 0.30, 0.30)
MAX_FEATURE_HISTORY_BARS = 1440
MAX_TARGET_MATURITY_BARS = 336
REFIT_BARS = 168


class SupportProtocolError(RuntimeError):
    pass


@dataclass(frozen=True)
class TrackSpec:
    name: str
    training_support: int
    shadow_support: int
    block_length: int
    authority: str


TRACKS = (
    TrackSpec("A", 2190, 2190, 336, "PRIMARY_CALENDAR_EQUIVALENT"),
    TrackSpec("B", 365, 365, 56, "DIAGNOSTIC_RAW_ROW_MULTIPLICATION_ONLY"),
    TrackSpec("C", 365, 365, 336, "DIAGNOSTIC_HYBRID_EARLIER_BURNIN_ONLY"),
)


@dataclass(frozen=True)
class TrackSupportResult:
    name: str
    authority: str
    training_support_required: int
    shadow_support_required: int
    block_length: int
    first_training_support_timestamp: str | None
    first_shadow_origin_timestamp: str | None
    first_shadow_support_satisfied_timestamp: str | None
    calibration_activation_refit_timestamp: str | None
    first_formal_origin_timestamp: str | None
    last_formal_origin_timestamp: str | None
    formal_rows: int
    complete_blocks: int
    trailing_partial_rows: int
    formal_calendar_span_days: float | None
    formal_eligibility_rate: float | None


@dataclass(frozen=True)
class FunnelMeasurement:
    research_id: str
    payload_sha256: str
    common_start: str
    common_end: str
    raw_common_bars: int
    feature_valid_bars: int
    eligible_feature_valid_bars: int
    pre_formal_eligibility_rate: float
    max_feature_history_bars: int
    max_target_maturity_bars: int
    refit_bars: int
    tracks: dict[str, TrackSupportResult]

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tracks"] = {k: asdict(v) for k, v in self.tracks.items()}
        return d


def _iso(ts: pd.Timestamp) -> str:
    return pd.Timestamp(ts).tz_convert("UTC").isoformat().replace("+00:00", "Z")


def _validate_payload_bytes(raw: bytes) -> dict[str, Any]:
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_PAYLOAD_SHA256:
        raise SupportProtocolError(f"0053 payload SHA256 mismatch: {sha}")
    payload = json.loads(raw)
    if payload.get("interval") != "4h":
        raise SupportProtocolError("0053 payload interval must be 4h")
    if tuple(payload.get("symbols", {}).keys()) != SYMBOLS:
        raise SupportProtocolError("0053 payload symbol ordering/identity mismatch")
    return payload


def load_frozen_payload(path: str | Path) -> dict[str, pd.DataFrame]:
    payload = _validate_payload_bytes(Path(path).read_bytes())
    frames: dict[str, pd.DataFrame] = {}
    for symbol in SYMBOLS:
        rows = payload["symbols"][symbol]
        if not isinstance(rows, list) or not rows:
            raise SupportProtocolError(f"Empty 0053 payload rows for {symbol}")
        parsed: list[dict[str, Any]] = []
        previous: int | None = None
        for row in rows:
            if not isinstance(row, list) or len(row) < 12:
                raise SupportProtocolError(f"Malformed 0053 kline row for {symbol}")
            open_ms = int(row[0])
            if open_ms % BAR_INTERVAL_MS != 0:
                raise SupportProtocolError(f"Non-4h-aligned open_time for {symbol}")
            if previous is not None and open_ms - previous != BAR_INTERVAL_MS:
                raise SupportProtocolError(f"Internal 4h gap for {symbol}")
            previous = open_ms
            close = float(row[4])
            if not math.isfinite(close) or close <= 0.0:
                raise SupportProtocolError(f"Invalid close for {symbol}")
            parsed.append({"open_time": pd.to_datetime(open_ms, unit="ms", utc=True), "close": close})
        frame = pd.DataFrame(parsed).set_index("open_time")
        if frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
            raise SupportProtocolError(f"Invalid 0053 index for {symbol}")
        frames[symbol] = frame

    common = frames[SYMBOLS[0]].index
    for symbol in SYMBOLS[1:]:
        common = common.intersection(frames[symbol].index)
    common = common.sort_values()
    if len(common) == 0:
        raise SupportProtocolError("Empty 0053 common index")
    expected = pd.date_range(common[0], common[-1], freq="4h", tz="UTC")
    if not common.equals(expected):
        raise SupportProtocolError("0053 common BTC/ETH/SOL index is not contiguous 4h")
    return {symbol: frames[symbol].loc[common].copy() for symbol in SYMBOLS}


def trend_score_4h(price: pd.Series) -> pd.Series:
    price = pd.Series(price, copy=False).astype(float)
    if price.empty or (~np.isfinite(price.to_numpy())).any() or (price <= 0.0).any():
        raise SupportProtocolError("BTC price series must be finite and strictly positive")
    lr = np.log(price).diff()
    out = pd.Series(0.0, index=price.index, dtype=float)
    valid = pd.Series(True, index=price.index, dtype=bool)
    for horizon, weight in zip(HORIZONS_4H, FAST_WEIGHTS):
        momentum = np.log(price / price.shift(horizon))
        scale = lr.rolling(horizon, min_periods=horizon).std(ddof=1) * math.sqrt(horizon)
        component = np.tanh(momentum / scale)
        out = out + weight * component
        valid &= component.notna()
    return out.where(valid)


def build_support_state(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if tuple(frames.keys()) != SYMBOLS:
        raise SupportProtocolError("Support frames must contain exact frozen symbol order")
    index = frames[SYMBOLS[0]].index
    if not all(index.equals(frames[s].index) for s in SYMBOLS[1:]):
        raise SupportProtocolError("Support frames must share identical 4h index")
    btc_fast = trend_score_4h(frames["BTCUSDT"]["close"])
    state = pd.DataFrame(index=index)
    state["FEATURE_VALID"] = btc_fast.notna()
    state["BTC_FAST_4H"] = btc_fast
    state["ELIGIBLE"] = state["FEATURE_VALID"] & btc_fast.ge(0.0)
    positions = np.arange(len(index), dtype=int)
    state["TARGET_MATURITY_AVAILABLE"] = positions + MAX_TARGET_MATURITY_BARS < len(index)
    return state


def _matured_count(eligible: np.ndarray, t: int) -> int:
    cutoff = t - MAX_TARGET_MATURITY_BARS
    if cutoff < 0:
        return 0
    return int(np.count_nonzero(eligible[: cutoff + 1]))


def _first_index_or_none(mask: np.ndarray) -> int | None:
    found = np.flatnonzero(mask)
    return int(found[0]) if len(found) else None


def measure_track(index: pd.DatetimeIndex, eligible: np.ndarray, spec: TrackSpec) -> TrackSupportResult:
    if len(index) != len(eligible):
        raise SupportProtocolError("Index/eligibility length mismatch")
    n = len(index)
    if n == 0:
        raise SupportProtocolError("Empty support index")
    eligible = np.asarray(eligible, dtype=bool)

    anchor: int | None = None
    for t in np.flatnonzero(eligible):
        if _matured_count(eligible, int(t)) >= spec.training_support:
            anchor = int(t)
            break

    if anchor is None:
        return TrackSupportResult(
            name=spec.name,
            authority=spec.authority,
            training_support_required=spec.training_support,
            shadow_support_required=spec.shadow_support,
            block_length=spec.block_length,
            first_training_support_timestamp=None,
            first_shadow_origin_timestamp=None,
            first_shadow_support_satisfied_timestamp=None,
            calibration_activation_refit_timestamp=None,
            first_formal_origin_timestamp=None,
            last_formal_origin_timestamp=None,
            formal_rows=0,
            complete_blocks=0,
            trailing_partial_rows=0,
            formal_calendar_span_days=None,
            formal_eligibility_rate=None,
        )

    # Shadow forecasts are conceptually emitted on every eligible bar from the
    # first training-supported anchor. No model or target value is computed.
    shadow_mask = eligible.copy()
    shadow_mask[:anchor] = False

    support_satisfied: int | None = None
    for t in range(anchor, n):
        cutoff = t - MAX_TARGET_MATURITY_BARS
        if cutoff < anchor:
            continue
        matured_shadow = int(np.count_nonzero(shadow_mask[anchor : cutoff + 1]))
        if matured_shadow >= spec.shadow_support:
            support_satisfied = t
            break

    activation: int | None = None
    if support_satisfied is not None:
        k = max(0, math.ceil((support_satisfied - anchor) / REFIT_BARS))
        candidate = anchor + k * REFIT_BARS
        if candidate < n:
            # 0048 activates calibration at the first frozen refit where the
            # matured-shadow pool already satisfies the support threshold.
            cutoff = candidate - MAX_TARGET_MATURITY_BARS
            matured_shadow = 0 if cutoff < anchor else int(np.count_nonzero(shadow_mask[anchor : cutoff + 1]))
            if matured_shadow >= spec.shadow_support:
                activation = candidate
            else:
                candidate += REFIT_BARS
                if candidate < n:
                    cutoff = candidate - MAX_TARGET_MATURITY_BARS
                    matured_shadow = 0 if cutoff < anchor else int(np.count_nonzero(shadow_mask[anchor : cutoff + 1]))
                    if matured_shadow >= spec.shadow_support:
                        activation = candidate

    formal_positions: np.ndarray
    if activation is None:
        formal_positions = np.asarray([], dtype=int)
    else:
        positions = np.arange(n, dtype=int)
        formal_mask = eligible & (positions >= activation) & (positions + MAX_TARGET_MATURITY_BARS < n)
        formal_positions = np.flatnonzero(formal_mask)

    formal_rows = int(len(formal_positions))
    complete_blocks = formal_rows // spec.block_length
    trailing = formal_rows % spec.block_length
    if formal_rows:
        first = int(formal_positions[0])
        last = int(formal_positions[-1])
        span_days = float((index[last] - index[first]).total_seconds() / 86400.0)
        calendar_positions = np.arange(first, last + 1, dtype=int)
        eligibility_rate = float(np.mean(eligible[calendar_positions]))
        first_formal = _iso(index[first])
        last_formal = _iso(index[last])
    else:
        span_days = None
        eligibility_rate = None
        first_formal = None
        last_formal = None

    return TrackSupportResult(
        name=spec.name,
        authority=spec.authority,
        training_support_required=spec.training_support,
        shadow_support_required=spec.shadow_support,
        block_length=spec.block_length,
        first_training_support_timestamp=_iso(index[anchor]),
        first_shadow_origin_timestamp=_iso(index[anchor]),
        first_shadow_support_satisfied_timestamp=_iso(index[support_satisfied]) if support_satisfied is not None else None,
        calibration_activation_refit_timestamp=_iso(index[activation]) if activation is not None else None,
        first_formal_origin_timestamp=first_formal,
        last_formal_origin_timestamp=last_formal,
        formal_rows=formal_rows,
        complete_blocks=complete_blocks,
        trailing_partial_rows=trailing,
        formal_calendar_span_days=span_days,
        formal_eligibility_rate=eligibility_rate,
    )


def measure_support_funnel(payload_path: str | Path) -> FunnelMeasurement:
    frames = load_frozen_payload(payload_path)
    state = build_support_state(frames)
    eligible = state["ELIGIBLE"].to_numpy(dtype=bool)
    tracks = {spec.name: measure_track(state.index, eligible, spec) for spec in TRACKS}
    feature_valid = state["FEATURE_VALID"].to_numpy(dtype=bool)
    feature_count = int(np.count_nonzero(feature_valid))
    eligible_count = int(np.count_nonzero(eligible))
    eligibility_rate = float(eligible_count / feature_count) if feature_count else float("nan")
    return FunnelMeasurement(
        research_id=RESEARCH_ID,
        payload_sha256=EXPECTED_PAYLOAD_SHA256,
        common_start=_iso(state.index[0]),
        common_end=_iso(state.index[-1]),
        raw_common_bars=int(len(state)),
        feature_valid_bars=feature_count,
        eligible_feature_valid_bars=eligible_count,
        pre_formal_eligibility_rate=eligibility_rate,
        max_feature_history_bars=MAX_FEATURE_HISTORY_BARS,
        max_target_maturity_bars=MAX_TARGET_MATURITY_BARS,
        refit_bars=REFIT_BARS,
        tracks=tracks,
    )


def classify_track_a(measurement: FunnelMeasurement) -> str:
    blocks = measurement.tracks["A"].complete_blocks
    return (
        "PASS_4H_CALENDAR_EQUIVALENT_SUPPORT_FEASIBLE"
        if blocks >= 12
        else "FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT"
    )
