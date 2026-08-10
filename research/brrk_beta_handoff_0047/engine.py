from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd
import requests
from scipy.stats import chi2

RESEARCH_ID = "BRRK-BETA-HANDOFF-EVENT-STUDY-0047"
DATASET_SLICE_ID = "BRRK-BETA-HANDOFF-0047-EXPOSED-HIST-V1"
ASSETS = ("BTC", "ETH", "SOL")
SYMBOLS = {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT"}
RAW_START = pd.Timestamp("2020-08-01")
FROZEN_END = pd.Timestamp("2026-08-02")
REQUEST_END_EXCLUSIVE = pd.Timestamp("2026-08-03")
HORIZONS = (20, 60, 120, 240)
FAST_WEIGHTS = (0.15, 0.25, 0.30, 0.30)
SLOW_WEIGHTS = (0.10, 0.20, 0.30, 0.40)
TARGET_HORIZONS = (20, 60)
XCF_LAGS = tuple(range(-14, 15))
VAR_LAGS = 7
IRF_MAX_HORIZON = 14
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 470_047
TRADE_SURPRISE_WINDOW = 60
ORACLE_COST_BPS_PER_ABS_WEIGHT_CHANGE = 5.0
ORACLE_FULL_SWITCH_L1 = 2.0
ORACLE_FULL_SWITCH_COST = ORACLE_FULL_SWITCH_L1 * ORACLE_COST_BPS_PER_ABS_WEIGHT_CHANGE / 10_000.0
API_BASES = (
    "https://data-api.binance.vision/api/v3/klines",
    "https://api.binance.com/api/v3/klines",
)
REQUIRED_FIELDS = ("open", "high", "low", "close", "volume", "quote_volume", "trades")


class FrozenProtocolError(RuntimeError):
    pass


def _ms(ts: pd.Timestamp) -> int:
    return int(pd.Timestamp(ts, tz="UTC").timestamp() * 1000)


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def fetch_daily_frame(asset: str) -> pd.DataFrame:
    if asset not in ASSETS:
        raise FrozenProtocolError(f"Unexpected asset: {asset}")
    start_ms = _ms(RAW_START)
    end_exclusive_ms = _ms(REQUEST_END_EXCLUSIVE)
    rows: list[list[Any]] = []
    last_error: Exception | None = None
    while start_ms < end_exclusive_ms:
        payload = None
        for base in API_BASES:
            try:
                response = requests.get(
                    base,
                    params={
                        "symbol": SYMBOLS[asset],
                        "interval": "1d",
                        "startTime": start_ms,
                        "endTime": end_exclusive_ms - 1,
                        "limit": 1000,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                payload = response.json()
                break
            except Exception as exc:  # pragma: no cover - network path
                last_error = exc
                time.sleep(1.0)
        if payload is None:
            raise FrozenProtocolError(f"Could not fetch {asset}: {last_error}")
        if not payload:
            break
        rows.extend(payload)
        next_start = int(payload[-1][0]) + 86_400_000
        if next_start <= start_ms:
            raise FrozenProtocolError(f"Non-advancing Binance pagination for {asset}")
        start_ms = next_start
        time.sleep(0.08)
    if not rows:
        raise FrozenProtocolError(f"No Binance rows for {asset}")

    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_volume",
        "trades",
        "taker_base",
        "taker_quote",
        "ignore",
    ]
    frame = pd.DataFrame(rows, columns=columns)
    frame["date"] = pd.to_datetime(frame["open_time"], unit="ms", utc=True).dt.tz_localize(None)
    for col in ("open", "high", "low", "close", "volume", "quote_volume"):
        frame[col] = pd.to_numeric(frame[col], errors="raise").astype(float)
    frame["trades"] = pd.to_numeric(frame["trades"], errors="raise").astype(np.int64)
    frame = frame[["date", *REQUIRED_FIELDS]].set_index("date").sort_index()
    frame = frame.loc[(frame.index >= RAW_START) & (frame.index <= FROZEN_END)]
    validate_asset_frame(asset, frame)
    return frame


def validate_asset_frame(asset: str, frame: pd.DataFrame) -> None:
    if asset not in ASSETS:
        raise FrozenProtocolError(f"Unexpected asset: {asset}")
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise FrozenProtocolError(f"{asset} index must be DatetimeIndex")
    if frame.index.tz is not None:
        raise FrozenProtocolError(f"{asset} index must be UTC-normalized tz-naive dates")
    if frame.empty:
        raise FrozenProtocolError(f"{asset} frame is empty")
    if frame.index.has_duplicates:
        raise FrozenProtocolError(f"Duplicate dates for {asset}")
    if not frame.index.is_monotonic_increasing:
        raise FrozenProtocolError(f"Unsorted dates for {asset}")
    missing_columns = [c for c in REQUIRED_FIELDS if c not in frame.columns]
    if missing_columns:
        raise FrozenProtocolError(f"Missing columns for {asset}: {missing_columns}")
    if (frame.index.normalize() != frame.index).any():
        raise FrozenProtocolError(f"Non-midnight daily index for {asset}")
    numeric = frame.loc[:, REQUIRED_FIELDS].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise FrozenProtocolError(f"Nonfinite required value for {asset}")
    if (frame["close"] <= 0).any():
        raise FrozenProtocolError(f"Nonpositive close for {asset}")
    if (frame["trades"] < 0).any():
        raise FrozenProtocolError(f"Negative trade count for {asset}")
    if (frame["volume"] < 0).any() or (frame["quote_volume"] < 0).any():
        raise FrozenProtocolError(f"Negative volume for {asset}")


def assemble_common_frames(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    if tuple(sorted(frames)) != tuple(sorted(ASSETS)):
        raise FrozenProtocolError(f"Frames must contain exactly {ASSETS}")
    for asset in ASSETS:
        validate_asset_frame(asset, frames[asset])
    common_start = max(frames[a].index.min() for a in ASSETS)
    if common_start < RAW_START:
        common_start = RAW_START
    if common_start > FROZEN_END:
        raise FrozenProtocolError("No common history through frozen end")
    expected = pd.date_range(common_start, FROZEN_END, freq="D")
    aligned: dict[str, pd.DataFrame] = {}
    for asset in ASSETS:
        missing = expected.difference(frames[asset].index)
        if len(missing):
            sample = [d.strftime("%Y-%m-%d") for d in missing[:5]]
            raise FrozenProtocolError(f"Internal common-history gap for {asset}: {sample}")
        out = frames[asset].loc[expected, REQUIRED_FIELDS].copy()
        if not out.index.equals(expected):
            raise FrozenProtocolError(f"Common index mismatch for {asset}")
        aligned[asset] = out
    return aligned


def build_market_evidence_payload(frames: dict[str, pd.DataFrame]) -> dict[str, Any]:
    aligned = assemble_common_frames(frames)
    common_index = aligned["BTC"].index
    rows: list[dict[str, Any]] = []
    for dt in common_index:
        date_text = dt.strftime("%Y-%m-%d")
        for asset in ASSETS:
            row = aligned[asset].loc[dt]
            rows.append(
                {
                    "date": date_text,
                    "asset": asset,
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                    "quote_volume": float(row["quote_volume"]),
                    "trades": int(row["trades"]),
                }
            )
    payload = {
        "research_id": RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "raw_request_start": RAW_START.strftime("%Y-%m-%d"),
        "frozen_end": FROZEN_END.strftime("%Y-%m-%d"),
        "common_start": common_index.min().strftime("%Y-%m-%d"),
        "common_end": common_index.max().strftime("%Y-%m-%d"),
        "assets": list(ASSETS),
        "fields": list(REQUIRED_FIELDS),
        "rows": rows,
    }
    return {"payload": payload, "payload_sha256": sha256_json(payload)}


def frames_from_market_evidence(evidence: dict[str, Any]) -> dict[str, pd.DataFrame]:
    if set(evidence) != {"payload", "payload_sha256"}:
        raise FrozenProtocolError("Unexpected market evidence wrapper")
    payload = evidence["payload"]
    if evidence["payload_sha256"] != sha256_json(payload):
        raise FrozenProtocolError("Market evidence SHA256 mismatch")
    if payload.get("research_id") != RESEARCH_ID or payload.get("dataset_slice_id") != DATASET_SLICE_ID:
        raise FrozenProtocolError("Wrong market evidence identity")
    if payload.get("frozen_end") != FROZEN_END.strftime("%Y-%m-%d"):
        raise FrozenProtocolError("Wrong frozen history end")
    rows = pd.DataFrame(payload.get("rows", []))
    if rows.empty:
        raise FrozenProtocolError("Empty market evidence rows")
    if list(payload.get("assets", [])) != list(ASSETS):
        raise FrozenProtocolError("Wrong asset universe in market evidence")
    frames: dict[str, pd.DataFrame] = {}
    for asset in ASSETS:
        part = rows.loc[rows["asset"] == asset, ["date", *REQUIRED_FIELDS]].copy()
        part["date"] = pd.to_datetime(part["date"], format="%Y-%m-%d")
        part = part.set_index("date").sort_index()
        for col in ("open", "high", "low", "close", "volume", "quote_volume"):
            part[col] = pd.to_numeric(part[col], errors="raise").astype(float)
        part["trades"] = pd.to_numeric(part["trades"], errors="raise").astype(np.int64)
        frames[asset] = part
    aligned = assemble_common_frames(frames)
    if aligned["BTC"].index.min().strftime("%Y-%m-%d") != payload.get("common_start"):
        raise FrozenProtocolError("Common-start mismatch in market evidence")
    return aligned


def trend_score(price: pd.Series, weights: Iterable[float]) -> pd.Series:
    weights = tuple(float(x) for x in weights)
    if len(weights) != len(HORIZONS):
        raise FrozenProtocolError("Trend weight length mismatch")
    lr = np.log(price).diff()
    out = pd.Series(0.0, index=price.index, dtype=float)
    valid = pd.Series(True, index=price.index)
    for horizon, weight in zip(HORIZONS, weights):
        momentum = np.log(price / price.shift(horizon))
        scale = lr.rolling(horizon).std() * math.sqrt(horizon)
        component = np.tanh(momentum / scale)
        out = out + weight * component
        valid &= component.notna()
    return out.where(valid)


def _episode_columns(btc_fast: pd.Series) -> tuple[pd.Series, pd.Series]:
    active = btc_fast.notna() & btc_fast.ge(0.0)
    starts = active & ~active.shift(1, fill_value=False)
    ids = starts.cumsum().where(active).astype("Int64")
    age = pd.Series(pd.NA, index=btc_fast.index, dtype="Int64")
    if active.any():
        age.loc[active] = active.loc[active].groupby(ids.loc[active]).cumcount().to_numpy() + 1
    return ids, age


def build_causal_panel(frames: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    aligned = assemble_common_frames(frames)
    prices = pd.DataFrame({asset: aligned[asset]["close"] for asset in ASSETS})
    panel = pd.DataFrame(index=prices.index)
    for asset in ASSETS:
        panel[f"{asset}_ABS_FAST"] = trend_score(prices[asset], FAST_WEIGHTS)
        panel[f"{asset}_ABS_SLOW"] = trend_score(prices[asset], SLOW_WEIGHTS)
    for asset in ("ETH", "SOL"):
        ratio = prices[asset] / prices["BTC"]
        panel[f"{asset}_REL_FAST"] = trend_score(ratio, FAST_WEIGHTS)
        panel[f"{asset}_REL_SLOW"] = trend_score(ratio, SLOW_WEIGHTS)
        panel[f"{asset}_REL_ACCEL"] = panel[f"{asset}_REL_FAST"] - panel[f"{asset}_REL_SLOW"]
        panel[f"{asset}_PARTICIPATING"] = (
            panel[f"{asset}_ABS_FAST"].gt(0.0) & panel[f"{asset}_REL_FAST"].gt(0.0)
        ).astype(int)
        log_trades = np.log1p(aligned[asset]["trades"].astype(float))
        med60 = log_trades.rolling(TRADE_SURPRISE_WINDOW, min_periods=TRADE_SURPRISE_WINDOW).median()
        panel[f"{asset}_TRADE_SURPRISE"] = log_trades - med60
        if asset == "ETH":
            score = 0.60 * panel["ETH_ABS_FAST"] + 0.40 * panel["ETH_REL_FAST"]
        else:
            score = 0.50 * panel["SOL_ABS_FAST"] + 0.50 * panel["SOL_REL_FAST"]
        panel[f"{asset}_V1_ELIGIBLE"] = (
            score.gt(0.0) & panel[f"{asset}_ABS_FAST"].gt(0.0) & panel[f"{asset}_REL_FAST"].gt(0.0)
        ).astype(int)
    panel["BETA_BREADTH"] = (
        panel["ETH_PARTICIPATING"].astype(float) + panel["SOL_PARTICIPATING"].astype(float)
    ) / 2.0
    episode_id, state_age = _episode_columns(panel["BTC_ABS_FAST"])
    panel["EPISODE_ID"] = episode_id
    panel["STATE_AGE"] = state_age
    return prices, panel


def build_durable_target(prices: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    if not prices.index.equals(panel.index):
        raise FrozenProtocolError("Prices/panel index mismatch")
    target = pd.DataFrame(index=prices.index)
    for horizon in TARGET_HORIZONS:
        for asset in ASSETS:
            target[f"F{horizon}_{asset}"] = np.log(prices[asset].shift(-horizon) / prices[asset])
    target["TARGET_AVAILABLE"] = prices.shift(-max(TARGET_HORIZONS)).notna().all(axis=1)
    inside_episode = panel["EPISODE_ID"].notna()
    eth = (
        inside_episode
        & target["TARGET_AVAILABLE"]
        & target["F20_BTC"].gt(0.0)
        & target["F60_BTC"].gt(0.0)
        & target["F20_ETH"].gt(target["F20_BTC"])
        & target["F60_ETH"].gt(target["F60_BTC"])
        & target["F20_ETH"].gt(target["F20_SOL"])
        & target["F60_ETH"].gt(target["F60_SOL"])
    )
    sol = (
        inside_episode
        & target["TARGET_AVAILABLE"]
        & target["F20_BTC"].gt(0.0)
        & target["F60_BTC"].gt(0.0)
        & target["F20_SOL"].gt(target["F20_BTC"])
        & target["F60_SOL"].gt(target["F60_BTC"])
        & target["F20_SOL"].gt(target["F20_ETH"])
        & target["F60_SOL"].gt(target["F60_ETH"])
    )
    if (eth & sol).any():
        raise FrozenProtocolError("Durable target cannot have two primary causes")
    target["ETH_DURABLE"] = eth
    target["SOL_DURABLE"] = sol
    cause = pd.Series(pd.NA, index=prices.index, dtype="string")
    cause.loc[eth] = "ETH"
    cause.loc[sol] = "SOL"
    target["DURABLE_CAUSE"] = cause
    return target


def _first_age(panel: pd.DataFrame, episode_id: int, flag_col: str) -> int | None:
    group = panel.loc[panel["EPISODE_ID"] == episode_id]
    hits = group.loc[group[flag_col].astype(bool), "STATE_AGE"].dropna()
    return int(hits.iloc[0]) if len(hits) else None


def _first_positive_age(panel: pd.DataFrame, episode_id: int, value_col: str) -> int | None:
    group = panel.loc[panel["EPISODE_ID"] == episode_id]
    hits = group.loc[group[value_col].gt(0.0), "STATE_AGE"].dropna()
    return int(hits.iloc[0]) if len(hits) else None


def one_switch_oracle(prices: pd.DataFrame, episode_dates: pd.DatetimeIndex) -> dict[str, Any]:
    if len(episode_dates) == 0:
        raise FrozenProtocolError("Empty oracle episode")
    start = episode_dates[0]
    end = episode_dates[-1]
    btc_log_wealth = float(np.log(prices.loc[end, "BTC"] / prices.loc[start, "BTC"]))
    best = {
        "oracle_choice": "NO_SWITCH",
        "oracle_switch_date": None,
        "oracle_log_wealth": btc_log_wealth,
        "oracle_log_wealth_uplift_vs_BTC": 0.0,
    }
    # Deterministic tie order is NO_SWITCH, then ETH, then SOL; ties do not matter for any gate.
    for asset in ("ETH", "SOL"):
        for switch_date in episode_dates[1:]:
            log_wealth = (
                float(np.log(prices.loc[switch_date, "BTC"] / prices.loc[start, "BTC"]))
                + float(np.log(prices.loc[end, asset] / prices.loc[switch_date, asset]))
                + float(np.log1p(-ORACLE_FULL_SWITCH_COST))
            )
            if log_wealth > float(best["oracle_log_wealth"]):
                best = {
                    "oracle_choice": asset,
                    "oracle_switch_date": switch_date.strftime("%Y-%m-%d"),
                    "oracle_log_wealth": log_wealth,
                    "oracle_log_wealth_uplift_vs_BTC": log_wealth - btc_log_wealth,
                }
    return best


def build_episode_table(prices: pd.DataFrame, panel: pd.DataFrame, target: pd.DataFrame) -> list[dict[str, Any]]:
    episodes: list[dict[str, Any]] = []
    ids = [int(x) for x in panel["EPISODE_ID"].dropna().unique()]
    for episode_id in ids:
        mask = panel["EPISODE_ID"].eq(episode_id).fillna(False)
        dates = panel.index[mask]
        available_dates = target.index[mask & target["TARGET_AVAILABLE"]]
        cause_series = target.loc[dates, "DURABLE_CAUSE"]
        handoff_dates = cause_series.dropna().index
        primary_date = handoff_dates[0] if len(handoff_dates) else None
        primary_cause = str(cause_series.loc[primary_date]) if primary_date is not None else None
        primary_age = int(panel.loc[primary_date, "STATE_AGE"]) if primary_date is not None else None
        spell_length = None
        if primary_date is not None:
            spell_length = 0
            started = False
            for dt in dates:
                if dt < primary_date:
                    continue
                started = True
                if bool(target.loc[dt, "TARGET_AVAILABLE"]) and target.loc[dt, "DURABLE_CAUSE"] == primary_cause:
                    spell_length += 1
                else:
                    break
            if not started:
                raise FrozenProtocolError("Primary date absent from episode")
        oracle = one_switch_oracle(prices, dates)
        row = {
            "episode_id": episode_id,
            "episode_start": dates[0].strftime("%Y-%m-%d"),
            "episode_end": dates[-1].strftime("%Y-%m-%d"),
            "episode_length": int(len(dates)),
            "first_target_available_date": available_dates[0].strftime("%Y-%m-%d") if len(available_dates) else None,
            "last_target_available_date": available_dates[-1].strftime("%Y-%m-%d") if len(available_dates) else None,
            "primary_handoff_date": primary_date.strftime("%Y-%m-%d") if primary_date is not None else None,
            "primary_handoff_cause": primary_cause,
            "handoff_state_age": primary_age,
            "handoff_opportunity_spell_length": int(spell_length) if spell_length is not None else None,
            "first_ETH_abs_fast_positive_age": _first_positive_age(panel, episode_id, "ETH_ABS_FAST"),
            "first_SOL_abs_fast_positive_age": _first_positive_age(panel, episode_id, "SOL_ABS_FAST"),
            "first_ETH_rel_fast_positive_age": _first_positive_age(panel, episode_id, "ETH_REL_FAST"),
            "first_SOL_rel_fast_positive_age": _first_positive_age(panel, episode_id, "SOL_REL_FAST"),
            "first_ETH_existing_V1_eligible_age": _first_age(panel, episode_id, "ETH_V1_ELIGIBLE"),
            "first_SOL_existing_V1_eligible_age": _first_age(panel, episode_id, "SOL_V1_ELIGIBLE"),
            **oracle,
        }
        episodes.append(row)
    return episodes


def _returns_inside_episode(prices: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    returns = np.log(prices).diff()
    same_episode_as_previous = panel["EPISODE_ID"].notna() & panel["EPISODE_ID"].eq(panel["EPISODE_ID"].shift(1))
    return returns.where(same_episode_as_previous, np.nan)


def _pearson_from_sufficient(n: float, sx: float, sy: float, sxx: float, syy: float, sxy: float) -> float | None:
    if n < 2:
        return None
    vx = sxx - sx * sx / n
    vy = syy - sy * sy / n
    if vx <= 0.0 or vy <= 0.0:
        return None
    cov = sxy - sx * sy / n
    return float(cov / math.sqrt(vx * vy))


def cross_correlation_diagnostics(prices: pd.DataFrame, panel: pd.DataFrame) -> dict[str, Any]:
    returns = _returns_inside_episode(prices, panel)
    episode_ids = [int(x) for x in panel["EPISODE_ID"].dropna().unique()]
    per_episode: list[dict[str, Any]] = []
    sufficient: dict[str, dict[int, list[dict[str, float]]]] = {"ETH": {}, "SOL": {}}
    for alt in ("ETH", "SOL"):
        for lag in XCF_LAGS:
            sufficient[alt][lag] = []
    for episode_id in episode_ids:
        mask = panel["EPISODE_ID"].eq(episode_id).fillna(False)
        group = returns.loc[mask]
        for alt in ("ETH", "SOL"):
            for lag in XCF_LAGS:
                x = group["BTC"]
                # Positive lag means BTC_t is compared with ALT_{t+lag}; positive lag therefore means BTC leads.
                y = group[alt].shift(-lag)
                pair = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
                n = int(len(pair))
                stats = {
                    "n": float(n),
                    "sx": float(pair["x"].sum()) if n else 0.0,
                    "sy": float(pair["y"].sum()) if n else 0.0,
                    "sxx": float((pair["x"] ** 2).sum()) if n else 0.0,
                    "syy": float((pair["y"] ** 2).sum()) if n else 0.0,
                    "sxy": float((pair["x"] * pair["y"]).sum()) if n else 0.0,
                }
                sufficient[alt][lag].append(stats)
                corr = _pearson_from_sufficient(**stats)
                per_episode.append(
                    {
                        "episode_id": episode_id,
                        "pair": f"BTC_{alt}",
                        "lag": lag,
                        "lag_semantics": "corr(BTC_t, ALT_t_plus_lag); positive lag means BTC leads",
                        "n_pairs": n,
                        "correlation": corr,
                    }
                )
    pooled: list[dict[str, Any]] = []
    for alt in ("ETH", "SOL"):
        for lag in XCF_LAGS:
            items = sufficient[alt][lag]
            total = {key: sum(x[key] for x in items) for key in ("n", "sx", "sy", "sxx", "syy", "sxy")}
            pooled.append(
                {
                    "pair": f"BTC_{alt}",
                    "lag": lag,
                    "lag_semantics": "corr(BTC_t, ALT_t_plus_lag); positive lag means BTC leads",
                    "n_pairs": int(total["n"]),
                    "correlation": _pearson_from_sufficient(**total),
                }
            )
    return {"per_episode": per_episode, "pooled": pooled, "_sufficient": sufficient, "episode_ids": episode_ids}


@dataclass
class VarPrepared:
    episode_ids: list[int]
    x_by_episode: dict[int, np.ndarray]
    y_by_episode: dict[int, np.ndarray]
    x_centered_by_episode: dict[int, np.ndarray]
    y_centered_by_episode: dict[int, np.ndarray]


def prepare_episode_var(prices: pd.DataFrame, panel: pd.DataFrame) -> VarPrepared:
    returns = _returns_inside_episode(prices, panel)
    x_by: dict[int, np.ndarray] = {}
    y_by: dict[int, np.ndarray] = {}
    episode_ids: list[int] = []
    for episode_id in [int(x) for x in panel["EPISODE_ID"].dropna().unique()]:
        mask = panel["EPISODE_ID"].eq(episode_id).fillna(False)
        group = returns.loc[mask, list(ASSETS)]
        xs: list[np.ndarray] = []
        ys: list[np.ndarray] = []
        values = group.to_numpy(dtype=float)
        for pos in range(VAR_LAGS, len(group)):
            y = values[pos]
            lag_blocks = [values[pos - lag] for lag in range(1, VAR_LAGS + 1)]
            x = np.concatenate(lag_blocks)
            if np.isfinite(y).all() and np.isfinite(x).all():
                xs.append(x)
                ys.append(y)
        if xs:
            x_arr = np.vstack(xs)
            y_arr = np.vstack(ys)
            x_by[episode_id] = x_arr
            y_by[episode_id] = y_arr
            episode_ids.append(episode_id)
    xc = {eid: x_by[eid] - x_by[eid].mean(axis=0, keepdims=True) for eid in episode_ids}
    yc = {eid: y_by[eid] - y_by[eid].mean(axis=0, keepdims=True) for eid in episode_ids}
    return VarPrepared(episode_ids, x_by, y_by, xc, yc)


def _var_matrices_from_beta(beta: np.ndarray) -> list[np.ndarray]:
    if beta.shape != (VAR_LAGS * len(ASSETS), len(ASSETS)):
        raise FrozenProtocolError(f"Unexpected VAR beta shape: {beta.shape}")
    matrices: list[np.ndarray] = []
    for lag in range(VAR_LAGS):
        block = beta[lag * len(ASSETS) : (lag + 1) * len(ASSETS), :]
        matrices.append(block.T.copy())
    return matrices


def _companion_radius(matrices: list[np.ndarray]) -> float:
    k = len(ASSETS)
    p = VAR_LAGS
    companion = np.zeros((k * p, k * p), dtype=float)
    companion[:k, : k * p] = np.hstack(matrices)
    if p > 1:
        companion[k:, :-k] = np.eye(k * (p - 1))
    return float(np.max(np.abs(np.linalg.eigvals(companion))))


def _generalized_btc_irf(matrices: list[np.ndarray], sigma: np.ndarray) -> np.ndarray:
    k = len(ASSETS)
    if sigma.shape != (k, k) or sigma[0, 0] <= 0.0:
        raise FrozenProtocolError("Invalid residual covariance for generalized IRF")
    psi = [np.eye(k)]
    for horizon in range(1, IRF_MAX_HORIZON + 1):
        value = np.zeros((k, k), dtype=float)
        for lag in range(1, min(VAR_LAGS, horizon) + 1):
            value += matrices[lag - 1] @ psi[horizon - lag]
        psi.append(value)
    impact = sigma[:, 0] / math.sqrt(float(sigma[0, 0]))
    return np.vstack([m @ impact for m in psi])


def fit_episode_var7(prepared: VarPrepared) -> dict[str, Any]:
    if not prepared.episode_ids:
        return {"status": "INSUFFICIENT_VAR_ROWS", "lag_order": VAR_LAGS}
    x = np.vstack([prepared.x_centered_by_episode[eid] for eid in prepared.episode_ids])
    y = np.vstack([prepared.y_centered_by_episode[eid] for eid in prepared.episode_ids])
    n, p = x.shape
    rank = int(np.linalg.matrix_rank(x))
    if rank < p:
        return {
            "status": "INSUFFICIENT_VAR_RANK",
            "lag_order": VAR_LAGS,
            "rows": int(n),
            "design_columns": int(p),
            "rank": rank,
        }
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    matrices = _var_matrices_from_beta(beta)
    residual_by: dict[int, np.ndarray] = {}
    intercepts: dict[int, list[float]] = {}
    sse = np.zeros((len(ASSETS), len(ASSETS)), dtype=float)
    for eid in prepared.episode_ids:
        xg = prepared.x_by_episode[eid]
        yg = prepared.y_by_episode[eid]
        intercept = yg.mean(axis=0) - xg.mean(axis=0) @ beta
        resid = yg - intercept - xg @ beta
        residual_by[eid] = resid
        intercepts[eid] = [float(v) for v in intercept]
        sse += resid.T @ resid
    df_resid = n - rank - len(prepared.episode_ids)
    if df_resid <= 0:
        return {
            "status": "INSUFFICIENT_VAR_RESIDUAL_DF",
            "lag_order": VAR_LAGS,
            "rows": int(n),
            "rank": rank,
            "episode_count": len(prepared.episode_ids),
        }
    sigma = sse / float(df_resid)
    radius = _companion_radius(matrices)
    irf = _generalized_btc_irf(matrices, sigma)

    xtx_inv = np.linalg.inv(x.T @ x)
    granger: list[dict[str, Any]] = []
    asset_to_idx = {asset: idx for idx, asset in enumerate(ASSETS)}
    for source in ASSETS:
        source_idx = asset_to_idx[source]
        coef_indices = np.array([lag * len(ASSETS) + source_idx for lag in range(VAR_LAGS)], dtype=int)
        for target_asset in ASSETS:
            if source == target_asset:
                continue
            target_idx = asset_to_idx[target_asset]
            scores = np.zeros((p, p), dtype=float)
            for eid in prepared.episode_ids:
                xg = prepared.x_centered_by_episode[eid]
                ug = residual_by[eid][:, target_idx]
                sg = xg.T @ ug
                scores += np.outer(sg, sg)
            covariance = xtx_inv @ scores @ xtx_inv
            sub_cov = covariance[np.ix_(coef_indices, coef_indices)]
            b = beta[coef_indices, target_idx]
            cov_rank = int(np.linalg.matrix_rank(sub_cov))
            if cov_rank < VAR_LAGS:
                wald = None
                pvalue = None
                status = "CLUSTER_COVARIANCE_SINGULAR"
            else:
                wald_value = float(b.T @ np.linalg.inv(sub_cov) @ b)
                wald = wald_value
                pvalue = float(chi2.sf(wald_value, df=VAR_LAGS))
                status = "OK"
            granger.append(
                {
                    "source": source,
                    "target": target_asset,
                    "lags_tested": VAR_LAGS,
                    "cluster_unit": "BTC_POSITIVE_EPISODE",
                    "cluster_covariance": "CR0_WITHIN_EPISODE_FIXED_EFFECTS",
                    "status": status,
                    "wald_chi2": wald,
                    "df": VAR_LAGS,
                    "p_value": pvalue,
                }
            )
    return {
        "status": "OK",
        "lag_order": VAR_LAGS,
        "rows": int(n),
        "design_columns": int(p),
        "rank": rank,
        "episode_count": len(prepared.episode_ids),
        "episode_ids": list(prepared.episode_ids),
        "episode_intercepts": intercepts,
        "A_matrices": [[[float(v) for v in row] for row in matrix] for matrix in matrices],
        "residual_covariance": [[float(v) for v in row] for row in sigma],
        "spectral_radius": radius,
        "stable_companion": bool(radius < 1.0),
        "granger_wald": granger,
        "generalized_btc_irf": [
            {
                "horizon": h,
                "BTC": float(irf[h, 0]),
                "ETH": float(irf[h, 1]),
                "SOL": float(irf[h, 2]),
            }
            for h in range(IRF_MAX_HORIZON + 1)
        ],
        "_beta": beta,
        "_sigma": sigma,
        "_residual_by_episode": residual_by,
    }


def _percentile_summary(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"p2_5": None, "median": None, "p97_5": None}
    arr = np.asarray(values, dtype=float)
    return {
        "p2_5": float(np.percentile(arr, 2.5)),
        "median": float(np.percentile(arr, 50.0)),
        "p97_5": float(np.percentile(arr, 97.5)),
    }


def _bootstrap_draws(episode_count: int) -> np.ndarray:
    if episode_count <= 0:
        return np.empty((BOOTSTRAP_REPLICATES, 0), dtype=int)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    return rng.integers(0, episode_count, size=(BOOTSTRAP_REPLICATES, episode_count), endpoint=False)


def bootstrap_episode_uncertainty(
    episode_table: list[dict[str, Any]],
    xcf: dict[str, Any],
    prepared_var: VarPrepared,
) -> dict[str, Any]:
    episode_ids = [int(row["episode_id"]) for row in episode_table]
    draws = _bootstrap_draws(len(episode_ids))
    prevalence_values: list[float] = []
    eth_share_values: list[float] = []
    sol_share_values: list[float] = []
    age_medians: list[float] = []
    spell_medians: list[float] = []
    for draw in draws:
        sampled = [episode_table[int(i)] for i in draw]
        eligible = [r for r in sampled if r["first_target_available_date"] is not None]
        handoffs = [r for r in eligible if r["primary_handoff_date"] is not None]
        if eligible:
            prevalence_values.append(len(handoffs) / len(eligible))
        if handoffs:
            eth_share_values.append(sum(r["primary_handoff_cause"] == "ETH" for r in handoffs) / len(handoffs))
            sol_share_values.append(sum(r["primary_handoff_cause"] == "SOL" for r in handoffs) / len(handoffs))
            age_medians.append(float(np.median([r["handoff_state_age"] for r in handoffs])))
            spell_medians.append(float(np.median([r["handoff_opportunity_spell_length"] for r in handoffs])))

    xcf_ci: list[dict[str, Any]] = []
    xcf_eids = list(xcf["episode_ids"])
    eid_to_pos = {eid: pos for pos, eid in enumerate(episode_ids)}
    for alt in ("ETH", "SOL"):
        for lag in XCF_LAGS:
            items = xcf["_sufficient"][alt][lag]
            item_by_eid = {eid: items[pos] for pos, eid in enumerate(xcf_eids)}
            corr_values: list[float] = []
            for draw in draws:
                totals = {key: 0.0 for key in ("n", "sx", "sy", "sxx", "syy", "sxy")}
                for pos in draw:
                    eid = episode_ids[int(pos)]
                    stats = item_by_eid.get(eid)
                    if stats is None:
                        continue
                    for key in totals:
                        totals[key] += stats[key]
                corr = _pearson_from_sufficient(**totals)
                if corr is not None:
                    corr_values.append(corr)
            xcf_ci.append({"pair": f"BTC_{alt}", "lag": lag, **_percentile_summary(corr_values)})

    irf_ci: dict[str, Any]
    var_episode_ids = prepared_var.episode_ids
    if not var_episode_ids:
        irf_ci = {"status": "INSUFFICIENT_VAR_ROWS", "valid_replicates": 0, "attempted_replicates": BOOTSTRAP_REPLICATES}
    else:
        k = len(ASSETS)
        p = VAR_LAGS * k
        sufficient: dict[int, dict[str, Any]] = {}
        for eid in var_episode_ids:
            x = prepared_var.x_centered_by_episode[eid]
            y = prepared_var.y_centered_by_episode[eid]
            sufficient[eid] = {
                "n": int(len(x)),
                "sxx": x.T @ x,
                "sxy": x.T @ y,
                "syy": y.T @ y,
            }
        eth_values: list[list[float]] = [[] for _ in range(IRF_MAX_HORIZON + 1)]
        sol_values: list[list[float]] = [[] for _ in range(IRF_MAX_HORIZON + 1)]
        valid = 0
        for draw in draws:
            counts: dict[int, int] = {}
            for pos in draw:
                eid = episode_ids[int(pos)]
                counts[eid] = counts.get(eid, 0) + 1
            sxx = np.zeros((p, p), dtype=float)
            sxy = np.zeros((p, k), dtype=float)
            syy = np.zeros((k, k), dtype=float)
            n = 0
            contributing_draws = 0
            for eid, count in counts.items():
                if eid not in sufficient:
                    continue
                stats = sufficient[eid]
                sxx += count * stats["sxx"]
                sxy += count * stats["sxy"]
                syy += count * stats["syy"]
                n += count * stats["n"]
                contributing_draws += count
            if contributing_draws == 0 or np.linalg.matrix_rank(sxx) < p:
                continue
            beta = np.linalg.solve(sxx, sxy)
            sse = syy - beta.T @ sxy - sxy.T @ beta + beta.T @ sxx @ beta
            df_resid = n - p - contributing_draws
            if df_resid <= 0:
                continue
            sigma = sse / float(df_resid)
            if not np.isfinite(sigma).all() or sigma[0, 0] <= 0.0:
                continue
            matrices = _var_matrices_from_beta(beta)
            try:
                irf = _generalized_btc_irf(matrices, sigma)
            except FrozenProtocolError:
                continue
            valid += 1
            for h in range(IRF_MAX_HORIZON + 1):
                eth_values[h].append(float(irf[h, 1]))
                sol_values[h].append(float(irf[h, 2]))
        irf_ci = {
            "status": "OK" if valid else "NO_VALID_BOOTSTRAP_REFITS",
            "attempted_replicates": BOOTSTRAP_REPLICATES,
            "valid_replicates": valid,
            "rows": [
                {
                    "horizon": h,
                    "ETH": _percentile_summary(eth_values[h]),
                    "SOL": _percentile_summary(sol_values[h]),
                }
                for h in range(IRF_MAX_HORIZON + 1)
            ],
        }

    return {
        "resampling_unit": "COMPLETE_BTC_POSITIVE_EPISODE",
        "replicates": BOOTSTRAP_REPLICATES,
        "seed": BOOTSTRAP_SEED,
        "episode_level_durable_handoff_prevalence": _percentile_summary(prevalence_values),
        "ETH_share_among_handoff_episodes": _percentile_summary(eth_share_values),
        "SOL_share_among_handoff_episodes": _percentile_summary(sol_share_values),
        "handoff_state_age_median": _percentile_summary(age_medians),
        "handoff_spell_median": _percentile_summary(spell_medians),
        "cross_correlation": xcf_ci,
        "generalized_btc_irf": irf_ci,
    }


def build_event_time_rows(panel: pd.DataFrame, episode_table: list[dict[str, Any]]) -> list[dict[str, Any]]:
    feature_cols = [
        "BTC_ABS_FAST",
        "BTC_ABS_SLOW",
        "ETH_ABS_FAST",
        "ETH_ABS_SLOW",
        "SOL_ABS_FAST",
        "SOL_ABS_SLOW",
        "ETH_REL_FAST",
        "ETH_REL_SLOW",
        "SOL_REL_FAST",
        "SOL_REL_SLOW",
        "ETH_REL_ACCEL",
        "SOL_REL_ACCEL",
        "BETA_BREADTH",
        "ETH_TRADE_SURPRISE",
        "SOL_TRADE_SURPRISE",
        "STATE_AGE",
    ]
    rows: list[dict[str, Any]] = []
    index = panel.index
    pos_by_date = {dt: i for i, dt in enumerate(index)}
    for episode in episode_table:
        if episode["primary_handoff_date"] is None:
            continue
        event_date = pd.Timestamp(episode["primary_handoff_date"])
        event_pos = pos_by_date[event_date]
        for event_time in range(-60, 21):
            pos = event_pos + event_time
            if pos < 0 or pos >= len(index):
                continue
            dt = index[pos]
            row: dict[str, Any] = {
                "episode_id": episode["episode_id"],
                "cause": episode["primary_handoff_cause"],
                "event_date": episode["primary_handoff_date"],
                "event_time": event_time,
                "date": dt.strftime("%Y-%m-%d"),
                "same_episode": bool(panel.loc[dt, "EPISODE_ID"] == episode["episode_id"]),
            }
            for col in feature_cols:
                value = panel.loc[dt, col]
                row[col] = None if pd.isna(value) else (int(value) if col == "STATE_AGE" else float(value))
            rows.append(row)
    return rows


def _distribution(values: list[int]) -> dict[str, Any]:
    if not values:
        return {"n": 0, "min": None, "q25": None, "median": None, "q75": None, "max": None}
    arr = np.asarray(values, dtype=float)
    return {
        "n": len(values),
        "min": int(np.min(arr)),
        "q25": float(np.percentile(arr, 25)),
        "median": float(np.median(arr)),
        "q75": float(np.percentile(arr, 75)),
        "max": int(np.max(arr)),
    }


def stage_classification(episode_table: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [r for r in episode_table if r["first_target_available_date"] is not None]
    handoffs = [r for r in eligible if r["primary_handoff_date"] is not None]
    eth_count = sum(r["primary_handoff_cause"] == "ETH" for r in handoffs)
    sol_count = sum(r["primary_handoff_cause"] == "SOL" for r in handoffs)
    prevalence = len(handoffs) / len(eligible) if eligible else None
    gates = {
        "target_eligible_episode_count_ge_5": len(eligible) >= 5,
        "handoff_episode_count_ge_3": len(handoffs) >= 3,
        "episode_level_prevalence_ge_0_50": prevalence is not None and prevalence >= 0.50,
        "ETH_cause_episode_count_ge_1": eth_count >= 1,
        "SOL_cause_episode_count_ge_1": sol_count >= 1,
    }
    if len(eligible) < 5:
        status = "INSUFFICIENT_EPISODE_DIVERSITY"
    elif len(handoffs) < 3 or prevalence is None or prevalence < 0.50:
        status = "FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE"
    elif eth_count < 1 or sol_count < 1:
        status = "INSUFFICIENT_COMPETING_RISK_DIVERSITY"
    else:
        status = "PASS_DURATION_AWARE_HANDOFF_MODEL_STAGE_ELIGIBLE"
    return {
        "result_status": status,
        "total_BTC_positive_episodes": len(episode_table),
        "target_eligible_BTC_positive_episodes": len(eligible),
        "primary_handoff_episodes": len(handoffs),
        "episode_level_durable_handoff_prevalence": prevalence,
        "ETH_primary_handoff_episodes": eth_count,
        "SOL_primary_handoff_episodes": sol_count,
        "gates": gates,
    }


def evaluate_frozen_protocol(frames: dict[str, pd.DataFrame], market_payload_sha256: str) -> dict[str, Any]:
    prices, panel = build_causal_panel(frames)
    target = build_durable_target(prices, panel)
    episodes = build_episode_table(prices, panel, target)
    event_time = build_event_time_rows(panel, episodes)
    xcf_internal = cross_correlation_diagnostics(prices, panel)
    prepared_var = prepare_episode_var(prices, panel)
    var = fit_episode_var7(prepared_var)
    uncertainty = bootstrap_episode_uncertainty(episodes, xcf_internal, prepared_var)
    classification = stage_classification(episodes)

    handoff_episodes = [r for r in episodes if r["primary_handoff_date"] is not None]
    ages = [int(r["handoff_state_age"]) for r in handoff_episodes]
    spells = [int(r["handoff_opportunity_spell_length"]) for r in handoff_episodes]
    follow_lags = {
        key: _distribution([int(r[key]) for r in episodes if r[key] is not None])
        for key in (
            "first_ETH_abs_fast_positive_age",
            "first_SOL_abs_fast_positive_age",
            "first_ETH_rel_fast_positive_age",
            "first_SOL_rel_fast_positive_age",
            "first_ETH_existing_V1_eligible_age",
            "first_SOL_existing_V1_eligible_age",
        )
    }
    xcf = {"per_episode": xcf_internal["per_episode"], "pooled": xcf_internal["pooled"]}
    if var.get("status") == "OK":
        var = {k: v for k, v in var.items() if not k.startswith("_")}

    return {
        "research_id": RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "evidence_class": "RESEARCHER_EXPOSED_DEVELOPMENT_HISTORY_NOT_INDEPENDENT_OOS",
        "market_payload_sha256": market_payload_sha256,
        "actual_variants_evaluated": 1,
        "primary_metric": "EPISODE_LEVEL_DURABLE_HANDOFF_PREVALENCE",
        "classification": classification,
        "handoff_state_age_distribution": _distribution(ages),
        "handoff_opportunity_spell_distribution": _distribution(spells),
        "observable_follow_age_distributions": follow_lags,
        "episodes": episodes,
        "event_time_grid": {"min": -60, "max": 20, "rows": event_time},
        "transmission_diagnostics": {
            "cross_correlation": xcf,
            "VAR7": var,
        },
        "uncertainty": uncertainty,
        "method_compliance": {
            "leader_follower_new_leader_question_preserved": True,
            "canonical_BTC_positive_episode_reused": True,
            "fast_slow_absolute_trend_present": True,
            "fast_slow_ETH_BTC_SOL_BTC_relative_trend_present": True,
            "relative_fast_minus_slow_acceleration_present": True,
            "beta_breadth_present": True,
            "trade_count_participation_present": True,
            "state_age_present": True,
            "cross_correlation_minus14_plus14_present": True,
            "pooled_episode_preserving_VAR7_present": True,
            "six_direction_Granger_Wald_present": True,
            "generalized_BTC_shock_IRF_0_14_present": True,
            "complete_episode_bootstrap_10000_seed_470047_present": True,
            "one_switch_oracle_is_hindsight_bound_only": True,
            "BOCPD_not_used": True,
            "portfolio_allocation_not_tested": True,
            "portfolio_economics_not_tested": True,
            "history_after_2026_08_02_not_used": True,
        },
        "authority": {
            "duration_aware_handoff_model_fitted": False,
            "portfolio_allocation_tested": False,
            "portfolio_economics_executed": False,
            "canonical_strategy_changed": False,
            "phase6_observation_changed": False,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        },
    }
