from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Mapping, Sequence

import numpy as np

RID = "BRRK-CRYPTO-CARRY-ATLAS-0072"
ASSETS = ("BTC", "ETH", "SOL")
HYPOTHESES = (
    "H01_BASIS_PERSISTENCE",
    "H02_BASIS_MEAN_REVERSION",
    "H03_BASIS_VOLATILITY_ASSOCIATION",
    "H04_BASIS_VOLUME_ASSOCIATION",
    "H05_BASIS_TREND_ASSOCIATION",
    "H06_EXTREME_CARRY_CRASH_ASSOCIATION",
)
PASS = "PASS_STRUCTURAL_CARRY_MECHANISM"
FAIL = "FAIL_NO_ROBUST_STRUCTURAL_CARRY_MECHANISM"
INCONCLUSIVE = "INCONCLUSIVE_INSUFFICIENT_SUPPORT"
INVALID = "INVALID_EXECUTION"

EXTREME_BASIS = 0.005
CRASH_RETURN = -0.10
ANCHOR_START = "2026-07-08"
ANCHOR_END = "2026-07-28"
MIN_ROWS_PER_ASSET = 19
MIN_TOTAL_ROWS = 57
MIN_EXTREME_ROWS = 8
MIN_NONEXTREME_ROWS = 8
MIN_CRASH_POSITIVES = 3
PERMUTATION_BLOCK = 3
PERMUTATION_REPS = 20_000
BASE_SEED = 720_072_000
BH_Q = 0.10


@dataclass(frozen=True)
class Bar:
    day: str
    close: float
    base_volume: float


@dataclass(frozen=True)
class StateRow:
    asset: str
    day: str
    basis: float
    basis_lag1: float
    basis_delta_next1: float
    volume_state: float
    rv7: float
    trend7: float
    extreme: int
    crash3: int


def _timestamp_to_day(value: int, unit: str) -> str:
    if unit == "MICROSECONDS":
        if not 10**15 <= value < 10**17:
            raise ValueError("TIMESTAMP_UNIT_DRIFT")
        seconds = value / 1_000_000.0
    elif unit == "MILLISECONDS":
        if not 10**12 <= value < 10**14:
            raise ValueError("TIMESTAMP_UNIT_DRIFT")
        seconds = value / 1_000.0
    else:
        raise ValueError("UNSUPPORTED_TIMESTAMP_UNIT")
    return datetime.fromtimestamp(seconds, tz=timezone.utc).date().isoformat()


def parse_binance_daily_klines(payload: bytes, timestamp_unit: str) -> list[Bar]:
    """Parse already-captured Binance daily kline CSV bytes. Never performs I/O or network access."""
    text = payload.decode("utf-8-sig")
    out: list[Bar] = []
    for row in csv.reader(io.StringIO(text)):
        if not row:
            continue
        try:
            open_time = int(row[0])
        except ValueError:
            # Binance archives can include a header in some families/periods.
            if row[0].strip().lower() in {"open_time", "open time"}:
                continue
            raise
        if len(row) < 6:
            raise ValueError("KLINE_SCHEMA_DRIFT")
        day = _timestamp_to_day(open_time, timestamp_unit)
        close = float(row[4])
        volume = float(row[5])
        if not np.isfinite(close) or close <= 0.0:
            raise ValueError("INVALID_CLOSE")
        if not np.isfinite(volume) or volume < 0.0:
            raise ValueError("INVALID_VOLUME")
        out.append(Bar(day=day, close=close, base_volume=volume))
    if len({b.day for b in out}) != len(out):
        raise ValueError("DUPLICATE_UTC_DAY")
    return sorted(out, key=lambda b: b.day)


def _by_day(bars: Sequence[Bar]) -> dict[str, Bar]:
    return {b.day: b for b in bars}


def _date_range(start: str, end: str) -> list[str]:
    a = np.datetime64(start, "D")
    b = np.datetime64(end, "D")
    return [str(x) for x in np.arange(a, b + np.timedelta64(1, "D"), dtype="datetime64[D]")]


def _shift_day(day: str, delta: int) -> str:
    return str(np.datetime64(day, "D") + np.timedelta64(delta, "D"))


def build_state_rows(
    spot_by_asset: Mapping[str, Sequence[Bar]],
    perp_by_asset: Mapping[str, Sequence[Bar]],
) -> list[StateRow]:
    """Build the exact preregistered July-2026 PIT feature/outcome table."""
    rows: list[StateRow] = []
    for asset in ASSETS:
        spot = _by_day(spot_by_asset.get(asset, ()))
        perp = _by_day(perp_by_asset.get(asset, ()))
        basis_by_day = {
            day: perp[day].close / spot[day].close - 1.0
            for day in spot.keys() & perp.keys()
        }
        for day in _date_range(ANCHOR_START, ANCHOR_END):
            needed_spot = [_shift_day(day, d) for d in range(-7, 4)]
            needed_perp = [_shift_day(day, d) for d in range(-6, 2)]
            if any(d not in spot for d in needed_spot) or any(d not in perp for d in needed_perp):
                continue
            if day not in basis_by_day or _shift_day(day, -1) not in basis_by_day or _shift_day(day, 1) not in basis_by_day:
                continue
            vols = np.asarray([perp[_shift_day(day, d)].base_volume for d in range(-6, 1)], dtype=float)
            if np.any(vols <= 0.0):
                continue
            closes = np.asarray([spot[_shift_day(day, d)].close for d in range(-7, 1)], dtype=float)
            logret = np.diff(np.log(closes))
            basis = float(basis_by_day[day])
            crash = min(spot[_shift_day(day, h)].close / spot[day].close - 1.0 for h in (1, 2, 3)) <= CRASH_RETURN
            rows.append(StateRow(
                asset=asset,
                day=day,
                basis=basis,
                basis_lag1=float(basis_by_day[_shift_day(day, -1)]),
                basis_delta_next1=float(basis_by_day[_shift_day(day, 1)] - basis),
                volume_state=float(np.log(perp[day].base_volume / np.median(vols))),
                rv7=float(np.sqrt((365.0 / 7.0) * np.sum(logret * logret))),
                trend7=float(np.log(spot[day].close / spot[_shift_day(day, -7)].close)),
                extreme=int(abs(basis) >= EXTREME_BASIS),
                crash3=int(crash),
            ))
    return rows


def midranks(values: Sequence[float]) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1:
        raise ValueError("RANK_INPUT_NOT_1D")
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=float)
    i = 0
    while i < len(x):
        j = i + 1
        while j < len(x) and x[order[j]] == x[order[i]]:
            j += 1
        ranks[order[i:j]] = (i + 1 + j) / 2.0
        i = j
    return ranks


def _corr(x: Sequence[float], y: Sequence[float]) -> float | None:
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    if len(a) < 2 or len(a) != len(b) or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        return None
    if float(np.ptp(a)) == 0.0 or float(np.ptp(b)) == 0.0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def pooled_within_asset_spearman(asset: Sequence[str], x: Sequence[float], y: Sequence[float]) -> float | None:
    if not (len(asset) == len(x) == len(y)):
        raise ValueError("LENGTH_MISMATCH")
    rx: list[float] = []
    ry: list[float] = []
    for name in ASSETS:
        idx = [i for i, a in enumerate(asset) if a == name]
        if not idx:
            continue
        rx.extend(midranks([x[i] for i in idx]))
        ry.extend(midranks([y[i] for i in idx]))
    return _corr(rx, ry)


def hypothesis_vectors(rows: Sequence[StateRow], hypothesis: str) -> tuple[list[str], np.ndarray, np.ndarray]:
    asset = [r.asset for r in rows]
    if hypothesis == HYPOTHESES[0]:
        return asset, np.asarray([r.basis_lag1 for r in rows]), np.asarray([r.basis for r in rows])
    if hypothesis == HYPOTHESES[1]:
        return asset, np.asarray([r.basis for r in rows]), np.asarray([r.basis_delta_next1 for r in rows])
    if hypothesis == HYPOTHESES[2]:
        return asset, np.asarray([abs(r.basis) for r in rows]), np.asarray([r.rv7 for r in rows])
    if hypothesis == HYPOTHESES[3]:
        return asset, np.asarray([abs(r.basis) for r in rows]), np.asarray([r.volume_state for r in rows])
    if hypothesis == HYPOTHESES[4]:
        return asset, np.asarray([abs(r.basis) for r in rows]), np.asarray([abs(r.trend7) for r in rows])
    if hypothesis == HYPOTHESES[5]:
        return asset, np.asarray([r.extreme for r in rows], dtype=float), np.asarray([r.crash3 for r in rows], dtype=float)
    raise KeyError(hypothesis)


def effect(rows: Sequence[StateRow], hypothesis: str) -> float | None:
    asset, x, y = hypothesis_vectors(rows, hypothesis)
    if hypothesis == HYPOTHESES[5]:
        yes = y[x == 1.0]
        no = y[x == 0.0]
        if len(yes) == 0 or len(no) == 0:
            return None
        return float(np.mean(yes) - np.mean(no))
    return pooled_within_asset_spearman(asset, x, y)


def _block_permuted_response(asset: Sequence[str], y: np.ndarray, rng: np.random.Generator, block: int) -> np.ndarray:
    out = y.copy()
    for name in ASSETS:
        idx = np.asarray([i for i, a in enumerate(asset) if a == name], dtype=int)
        if len(idx) == 0:
            continue
        local = y[idx]
        blocks = [local[i:i + block] for i in range(0, len(local), block)]
        order = rng.permutation(len(blocks))
        out[idx] = np.concatenate([blocks[i] for i in order])
    return out


def permutation_pvalue(rows: Sequence[StateRow], hypothesis: str, reps: int = PERMUTATION_REPS) -> float | None:
    ordinal = HYPOTHESES.index(hypothesis) + 1
    observed = effect(rows, hypothesis)
    if observed is None:
        return None
    asset, x, y = hypothesis_vectors(rows, hypothesis)
    rng = np.random.Generator(np.random.PCG64(BASE_SEED + ordinal))
    extreme_count = 0
    for _ in range(reps):
        yp = _block_permuted_response(asset, y, rng, PERMUTATION_BLOCK)
        if hypothesis == HYPOTHESES[5]:
            yes = yp[x == 1.0]
            no = yp[x == 0.0]
            null = None if len(yes) == 0 or len(no) == 0 else float(np.mean(yes) - np.mean(no))
        else:
            null = pooled_within_asset_spearman(asset, x, yp)
        if null is None:
            return None
        if hypothesis == HYPOTHESES[1]:
            extreme_count += int(null <= observed)
        else:
            extreme_count += int(null >= observed)
    return float((1 + extreme_count) / (reps + 1))


def bh_adjust(pvalues: Mapping[str, float | None]) -> dict[str, float | None]:
    if set(pvalues) != set(HYPOTHESES):
        raise ValueError("CANDIDATE_COUNT_DRIFT")
    if any(pvalues[h] is None for h in HYPOTHESES):
        return {h: None for h in HYPOTHESES}
    ordered = sorted(((float(pvalues[h]), h) for h in HYPOTHESES), key=lambda z: (z[0], z[1]))
    m = len(ordered)
    q = [0.0] * m
    running = 1.0
    for i in range(m - 1, -1, -1):
        raw = ordered[i][0] * m / (i + 1)
        running = min(running, raw)
        q[i] = min(1.0, running)
    out = {h: None for h in HYPOTHESES}
    for (_, h), qi in zip(ordered, q):
        out[h] = float(qi)
    return out


def support(rows: Sequence[StateRow]) -> dict:
    per_asset = {a: sum(r.asset == a for r in rows) for a in ASSETS}
    extreme = sum(r.extreme == 1 for r in rows)
    nonextreme = sum(r.extreme == 0 for r in rows)
    crashes = sum(r.crash3 == 1 for r in rows)
    sufficient = (
        all(per_asset[a] >= MIN_ROWS_PER_ASSET for a in ASSETS)
        and len(rows) >= MIN_TOTAL_ROWS
        and extreme >= MIN_EXTREME_ROWS
        and nonextreme >= MIN_NONEXTREME_ROWS
        and crashes >= MIN_CRASH_POSITIVES
    )
    return {
        "per_asset": per_asset,
        "total": len(rows),
        "extreme": extreme,
        "nonextreme": nonextreme,
        "crash_positive": crashes,
        "sufficient": bool(sufficient),
    }


def leave_one_asset_out(rows: Sequence[StateRow]) -> dict[str, dict[str, float | None]]:
    return {
        omitted: {h: effect([r for r in rows if r.asset != omitted], h) for h in HYPOTHESES}
        for omitted in ASSETS
    }


def classify_from_results(
    execution_valid: bool,
    support_sufficient: bool,
    effects: Mapping[str, float | None],
    qvalues: Mapping[str, float | None],
    loao: Mapping[str, Mapping[str, float | None]],
) -> tuple[str, dict[str, bool | None]]:
    if not execution_valid:
        return INVALID, {"G0_EXECUTION_VALID": False}
    if not support_sufficient:
        return INCONCLUSIVE, {"G0_EXECUTION_VALID": True, "G1_SUPPORT_SUFFICIENT": False}
    if any(effects.get(h) is None or qvalues.get(h) is None for h in HYPOTHESES):
        return INCONCLUSIVE, {"G0_EXECUTION_VALID": True, "G1_SUPPORT_SUFFICIENT": True}

    g2 = float(effects[HYPOTHESES[0]]) >= 0.25 and float(qvalues[HYPOTHESES[0]]) <= BH_Q
    g3 = float(effects[HYPOTHESES[1]]) <= -0.20 and float(qvalues[HYPOTHESES[1]]) <= BH_Q
    crowd = sum(float(effects[h]) >= 0.20 and float(qvalues[h]) <= BH_Q for h in HYPOTHESES[2:5])
    g4 = crowd >= 2
    g5 = float(effects[HYPOTHESES[5]]) >= 0.05 and float(qvalues[HYPOTHESES[5]]) <= BH_Q

    required_loao = all(set(loao.get(a, {})) >= set(HYPOTHESES) for a in ASSETS)
    if not required_loao:
        return INCONCLUSIVE, {"G0_EXECUTION_VALID": True, "G1_SUPPORT_SUFFICIENT": True}
    h1_ok = all(loao[a][HYPOTHESES[0]] is not None and float(loao[a][HYPOTHESES[0]]) > 0.0 for a in ASSETS)
    h2_ok = all(loao[a][HYPOTHESES[1]] is not None and float(loao[a][HYPOTHESES[1]]) < 0.0 for a in ASSETS)
    crowd_robust = sum(all(loao[a][h] is not None and float(loao[a][h]) > 0.0 for a in ASSETS) for h in HYPOTHESES[2:5]) >= 2
    h6_defined = [float(loao[a][HYPOTHESES[5]]) for a in ASSETS if loao[a][HYPOTHESES[5]] is not None]
    h6_ok = len(h6_defined) >= 2 and sum(v > 0.0 for v in h6_defined) >= 2
    g6 = h1_ok and h2_ok and crowd_robust and h6_ok

    gates = {
        "G0_EXECUTION_VALID": True,
        "G1_SUPPORT_SUFFICIENT": True,
        "G2_PERSISTENCE": g2,
        "G3_MEAN_REVERSION": g3,
        "G4_CROWDING_STATE_ASSOCIATION": g4,
        "G5_CRASH_RISK_ASSOCIATION": g5,
        "G6_LEAVE_ONE_ASSET_ROBUSTNESS": g6,
    }
    return (PASS if all(gates.values()) else FAIL), gates


def evaluate(rows: Sequence[StateRow], reps: int = PERMUTATION_REPS) -> dict:
    if reps != PERMUTATION_REPS:
        raise ValueError("SCIENTIFIC_REPLICATE_COUNT_DRIFT")
    sup = support(rows)
    effects = {h: effect(rows, h) for h in HYPOTHESES}
    pvalues = {h: permutation_pvalue(rows, h, reps=reps) for h in HYPOTHESES}
    qvalues = bh_adjust(pvalues)
    loao = leave_one_asset_out(rows)
    classification, gates = classify_from_results(True, sup["sufficient"], effects, qvalues, loao)
    return {
        "research_id": RID,
        "classification": classification,
        "execution_valid": True,
        "support_counts": sup,
        "effects": effects,
        "pvalues": pvalues,
        "bh_adjusted_q": qvalues,
        "leave_one_asset_results": loao,
        "terminal_gates": gates,
        "candidate_count": len(HYPOTHESES),
        "permutation_replicates": reps,
        "permutation_block": PERMUTATION_BLOCK,
        "base_seed": BASE_SEED,
    }
