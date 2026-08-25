from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from io import BytesIO, StringIO
from math import isfinite, log, sqrt
from random import Random
from statistics import median, stdev
from typing import Any, Mapping, Sequence
import csv
import re
import zipfile

FACTOR_NAMES = ("MOM60_RAW", "RVOL20_RAW", "LIQ30_RAW")
BOOTSTRAP_SEED = 860086
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_BLOCK = 8
FWER_ALPHA = 0.05
MIN_ASSETS = 10
TOP_N = 30
MIN_HISTORY = 120
FWD = 5
REALISTIC_BPS = 10
STRESS_BPS = 20
CLASSIFICATIONS = {
    "PASS_VALIDATED_FACTOR_ATLAS",
    "FAIL_NO_ROBUST_FACTOR_FAMILY",
    "INCONCLUSIVE_INSUFFICIENT_SUPPORT",
}

_SOURCE_RE = re.compile(
    r"^(?:stage/)?payloads/data__futures__um__monthly__klines__"
    r"(?P<symbol>[A-Z0-9]+USDT)__1d__(?P=symbol)-1d-"
    r"(?P<year>20\d{2})-(?P<month>0[1-9]|1[0-2])\.zip$"
)


class FactorAtlasExecutionError(RuntimeError):
    pass


def validate_source_keys(source_keys: Sequence[str]) -> None:
    """Metadata-only qualification. Never opens payload bytes."""
    if not source_keys:
        raise FactorAtlasExecutionError("NO_SOURCE_KEYS")
    logical: set[tuple[str, str]] = set()
    symbols: set[str] = set()
    for key in source_keys:
        match = _SOURCE_RE.fullmatch(key)
        if match is None:
            raise FactorAtlasExecutionError(f"UNKNOWN_SOURCE_KEY:{key}")
        symbol = match.group("symbol")
        month = f"{match.group('year')}-{match.group('month')}"
        identity = (symbol, month)
        if identity in logical:
            raise FactorAtlasExecutionError(f"DUPLICATE_LOGICAL_OBJECT:{symbol}:{month}")
        logical.add(identity)
        symbols.add(symbol)
    if "BTCUSDT" not in symbols:
        raise FactorAtlasExecutionError("MISSING_BTCUSDT_SOURCE")


def _utc_date(raw: str) -> str:
    try:
        stamp = int(raw)
    except (TypeError, ValueError) as exc:
        raise FactorAtlasExecutionError("INVALID_KLINE_OPEN_TIME") from exc
    mag = abs(stamp)
    seconds = stamp / (1_000_000.0 if mag >= 10**14 else 1_000.0 if mag >= 10**11 else 1.0)
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc).date().isoformat()
    except (OverflowError, OSError, ValueError) as exc:
        raise FactorAtlasExecutionError("INVALID_KLINE_OPEN_TIME") from exc


def _parse_month(raw_zip: bytes, source_name: str, expected_month: str) -> list[dict[str, Any]]:
    try:
        with zipfile.ZipFile(BytesIO(raw_zip), "r") as archive:
            members = [info for info in archive.infolist() if not info.is_dir()]
            if len(members) != 1 or not members[0].filename.lower().endswith(".csv"):
                raise FactorAtlasExecutionError(f"INVALID_INNER_ZIP_MEMBERS:{source_name}")
            with archive.open(members[0], "r") as handle:
                raw_csv = handle.read()
    except FactorAtlasExecutionError:
        raise
    except (zipfile.BadZipFile, RuntimeError, OSError, EOFError) as exc:
        raise FactorAtlasExecutionError(f"INVALID_INNER_ZIP:{source_name}") from exc

    try:
        reader = csv.reader(StringIO(raw_csv.decode("utf-8-sig")))
    except UnicodeDecodeError as exc:
        raise FactorAtlasExecutionError(f"INVALID_KLINE_ENCODING:{source_name}") from exc

    out: list[dict[str, Any]] = []
    previous: str | None = None
    for fields in reader:
        if not fields or all(not item.strip() for item in fields):
            continue
        first = fields[0].strip()
        if not first.lstrip("-").isdigit():
            if not out and first.lower() in {"open_time", "opentime"}:
                continue
            raise FactorAtlasExecutionError(f"INVALID_KLINE_ROW:{source_name}")
        if len(fields) < 8:
            raise FactorAtlasExecutionError(f"SHORT_KLINE_ROW:{source_name}")
        day = _utc_date(first)
        if day[:7] != expected_month:
            raise FactorAtlasExecutionError(f"KLINE_MONTH_MISMATCH:{source_name}:{day}")
        try:
            close = float(fields[4])
            quote_volume = float(fields[7])
        except (TypeError, ValueError) as exc:
            raise FactorAtlasExecutionError(f"INVALID_KLINE_VALUE:{source_name}") from exc
        if not isfinite(close) or close <= 0 or not isfinite(quote_volume) or quote_volume < 0:
            raise FactorAtlasExecutionError(f"INVALID_KLINE_VALUE:{source_name}")
        if previous is not None and day <= previous:
            raise FactorAtlasExecutionError(f"NON_INCREASING_KLINE_DATE:{source_name}")
        previous = day
        out.append({"date": day, "close": close, "quote_volume": quote_volume})
    if not out:
        raise FactorAtlasExecutionError(f"EMPTY_KLINE_MONTH:{source_name}")
    return out


def normalize_controlled_sources(sources: Mapping[str, bytes]) -> dict[str, list[dict[str, Any]]]:
    validate_source_keys(tuple(sources))
    monthly: dict[str, list[tuple[str, str, bytes]]] = defaultdict(list)
    for key, payload in sources.items():
        match = _SOURCE_RE.fullmatch(key)
        assert match is not None
        month = f"{match.group('year')}-{match.group('month')}"
        monthly[match.group("symbol")].append((month, key, payload))

    panel: dict[str, list[dict[str, Any]]] = {}
    for symbol, objects in monthly.items():
        objects.sort(key=lambda item: item[0])
        rows: list[dict[str, Any]] = []
        previous: str | None = None
        for month, key, payload in objects:
            for row in _parse_month(payload, key, month):
                day = str(row["date"])
                if previous is not None and day <= previous:
                    raise FactorAtlasExecutionError(f"NON_INCREASING_SYMBOL_DATE:{symbol}:{day}")
                previous = day
                rows.append(row)
        panel[symbol] = rows
    return panel


def _average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    p = 0
    while p < len(order):
        q = p + 1
        while q < len(order) and values[order[q]] == values[order[p]]:
            q += 1
        rank = (p + 1 + q) / 2.0
        for j in range(p, q):
            ranks[order[j]] = rank
        p = q
    return ranks


def _pearson(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        raise FactorAtlasExecutionError("INVALID_CORRELATION_SUPPORT")
    ml = sum(left) / len(left)
    mr = sum(right) / len(right)
    dl = [x - ml for x in left]
    dr = [x - mr for x in right]
    vl = sum(x * x for x in dl)
    vr = sum(x * x for x in dr)
    if vl <= 0 or vr <= 0:
        raise FactorAtlasExecutionError("DEGENERATE_RANK_CORRELATION")
    value = sum(x * y for x, y in zip(dl, dr)) / sqrt(vl * vr)
    if not isfinite(value):
        raise FactorAtlasExecutionError("NONFINITE_RANK_CORRELATION")
    return value


def _spearman(left: list[float], right: list[float]) -> float:
    return _pearson(_average_ranks(left), _average_ranks(right))


def _factor_values(rows: list[dict[str, Any]], i: int) -> dict[str, float]:
    closes = [float(row["close"]) for row in rows]
    if i < 60:
        raise FactorAtlasExecutionError("INSUFFICIENT_FACTOR_HISTORY")
    mom = log(closes[i] / closes[i - 60])
    returns = [log(closes[j] / closes[j - 1]) for j in range(i - 19, i + 1)]
    rvol = stdev(returns)
    liq = log(median(float(rows[j]["quote_volume"]) for j in range(i - 29, i + 1)))
    values = {"MOM60_RAW": mom, "RVOL20_RAW": rvol, "LIQ30_RAW": liq}
    if any(not isfinite(value) for value in values.values()):
        raise FactorAtlasExecutionError("NONFINITE_FACTOR")
    return values


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        raise FactorAtlasExecutionError("EMPTY_BOOTSTRAP")
    pos = (len(sorted_values) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    weight = pos - lo
    return sorted_values[lo] * (1.0 - weight) + sorted_values[hi] * weight


def _moving_block_draw(values: list[float], rng: Random) -> list[float]:
    n = len(values)
    block = min(BOOTSTRAP_BLOCK, n)
    out: list[float] = []
    while len(out) < n:
        start = rng.randrange(0, n - block + 1)
        out.extend(values[start : start + block])
    return out[:n]


def _bootstrap_stats(values: list[float], rng: Random) -> tuple[float, tuple[float, float]]:
    observed = sum(values) / len(values)
    centered = [value - observed for value in values]
    null_means: list[float] = []
    sample_means: list[float] = []
    for _ in range(BOOTSTRAP_REPLICATES):
        null_sample = _moving_block_draw(centered, rng)
        sample = _moving_block_draw(values, rng)
        null_means.append(sum(null_sample) / len(null_sample))
        sample_means.append(sum(sample) / len(sample))
    p = (1 + sum(abs(value) >= abs(observed) for value in null_means)) / (BOOTSTRAP_REPLICATES + 1)
    sample_means.sort()
    return p, (_quantile(sample_means, 0.025), _quantile(sample_means, 0.975))


def _holm_adjust(raw: Mapping[str, float]) -> dict[str, float]:
    ordered = sorted(raw.items(), key=lambda item: (item[1], item[0]))
    m = len(ordered)
    adjusted: dict[str, float] = {}
    running = 0.0
    for i, (name, p) in enumerate(ordered):
        running = max(running, min(1.0, (m - i) * p))
        adjusted[name] = running
    return adjusted


def _hac_tstat(values: list[float], lag: int = 4) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    centered = [value - mean for value in values]
    gamma0 = sum(value * value for value in centered) / n
    long_run = gamma0
    for k in range(1, min(lag, n - 1) + 1):
        gamma = sum(centered[t] * centered[t - k] for t in range(k, n)) / n
        long_run += 2.0 * (1.0 - k / (lag + 1.0)) * gamma
    if long_run <= 0:
        return 0.0
    se = sqrt(long_run / n)
    return mean / se if se > 0 else 0.0


def _four_blocks(values: list[float]) -> list[list[float]]:
    n = len(values)
    bounds = [round(i * n / 4) for i in range(5)]
    return [values[bounds[i] : bounds[i + 1]] for i in range(4)]


def _sign(value: float) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def _aligned_weights(symbols: list[str], factor_values: list[float]) -> dict[str, float]:
    n = len(symbols)
    k = n // 3
    if k < 1:
        raise FactorAtlasExecutionError("INVALID_TERCILE_SUPPORT")
    ordered = sorted(zip(factor_values, symbols), key=lambda pair: (pair[0], pair[1]))
    bottom = [symbol for _, symbol in ordered[:k]]
    top = [symbol for _, symbol in ordered[-k:]]
    weights = {symbol: 0.0 for symbol in symbols}
    for symbol in top:
        weights[symbol] = 1.0 / k
    for symbol in bottom:
        weights[symbol] = -1.0 / k
    return weights


def _turnover(previous: Mapping[str, float], current: Mapping[str, float]) -> float:
    names = set(previous) | set(current)
    return sum(abs(current.get(name, 0.0) - previous.get(name, 0.0)) for name in names)


def analyze_panel(panel: Mapping[str, list[dict[str, Any]]]) -> Mapping[str, Any]:
    """Pure frozen 0086 scientific engine over already-decoded daily rows."""
    if "BTCUSDT" not in panel:
        raise FactorAtlasExecutionError("MISSING_BTCUSDT")
    normalized: dict[str, list[dict[str, Any]]] = {}
    indices: dict[str, dict[str, int]] = {}
    for symbol, rows in panel.items():
        previous: str | None = None
        clean: list[dict[str, Any]] = []
        for row in rows:
            try:
                day = str(row["date"])
                datetime.fromisoformat(day)
                close = float(row["close"])
                quote_volume = float(row["quote_volume"])
            except (KeyError, TypeError, ValueError) as exc:
                raise FactorAtlasExecutionError(f"SCHEMA_DRIFT:{symbol}") from exc
            if previous is not None and day <= previous:
                raise FactorAtlasExecutionError(f"NON_INCREASING_DATE:{symbol}")
            if not isfinite(close) or close <= 0 or not isfinite(quote_volume) or quote_volume < 0:
                raise FactorAtlasExecutionError(f"NONFINITE_OR_INVALID_VALUE:{symbol}:{day}")
            previous = day
            clean.append({"date": day, "close": close, "quote_volume": quote_volume})
        normalized[symbol] = clean
        indices[symbol] = {row["date"]: i for i, row in enumerate(clean)}

    btc_rows = normalized["BTCUSDT"]
    observations: dict[str, list[dict[str, Any]]] = {name: [] for name in FACTOR_NAMES}
    decision_dates = [row["date"] for row in btc_rows if datetime.fromisoformat(row["date"]).weekday() == 0]

    for day in decision_dates:
        btc_i = indices["BTCUSDT"].get(day)
        if btc_i is None or btc_i < MIN_HISTORY - 1 or btc_i + FWD >= len(btc_rows):
            continue
        eligible: list[tuple[float, str, int]] = []
        for symbol, rows in normalized.items():
            i = indices[symbol].get(day)
            if i is None or i < MIN_HISTORY - 1 or i + FWD >= len(rows):
                continue
            trailing_liq = median(float(rows[j]["quote_volume"]) for j in range(i - 29, i + 1))
            if isfinite(trailing_liq) and trailing_liq > 0:
                eligible.append((trailing_liq, symbol, i))
        eligible.sort(key=lambda item: (-item[0], item[1]))
        selected = eligible[:TOP_N]
        if len(selected) < MIN_ASSETS:
            continue

        symbols = [symbol for _, symbol, _ in selected]
        factors = {name: [] for name in FACTOR_NAMES}
        outcomes: list[float] = []
        for _, symbol, i in selected:
            rows = normalized[symbol]
            values = _factor_values(rows, i)
            for name in FACTOR_NAMES:
                factors[name].append(values[name])
            outcomes.append(log(float(rows[i + FWD]["close"]) / float(rows[i]["close"])))

        btc_state = "BTC_UP" if log(float(btc_rows[btc_i]["close"]) / float(btc_rows[btc_i - 60]["close"])) > 0 else "BTC_NONUP"
        year = day[:4]
        for name in FACTOR_NAMES:
            raw_ic = _spearman(factors[name], outcomes)
            weights = _aligned_weights(symbols, factors[name])
            raw_spread = sum(weights[symbol] * outcomes[symbols.index(symbol)] for symbol in symbols)
            observations[name].append(
                {"date": day, "year": year, "btc_state": btc_state, "ic": raw_ic, "raw_spread": raw_spread, "weights": weights}
            )

    support_ok = True
    support_detail: dict[str, Any] = {}
    for name in FACTOR_NAMES:
        obs = observations[name]
        years = defaultdict(int)
        states = defaultdict(int)
        for row in obs:
            years[row["year"]] += 1
            states[row["btc_state"]] += 1
        blocks = _four_blocks([row["ic"] for row in obs])
        checks = {
            "weekly_ic_ge_104": len(obs) >= 104,
            "four_blocks_ge_20": len(blocks) == 4 and all(len(block) >= 20 for block in blocks),
            "three_years_ge_20": sum(count >= 20 for count in years.values()) >= 3,
            "btc_up_ge_30": states["BTC_UP"] >= 30,
            "btc_nonup_ge_30": states["BTC_NONUP"] >= 30,
        }
        support_detail[name] = {"observations": len(obs), "year_counts": dict(years), "state_counts": dict(states), "checks": checks}
        support_ok = support_ok and all(checks.values())

    if not support_ok:
        return {
            "classification": "INCONCLUSIVE_INSUFFICIENT_SUPPORT",
            "execution_valid": True,
            "factor_candidates": 3,
            "support": support_detail,
            "passing_factors": [],
            "btc_state_rule": "BTC_UP iff BTCUSDT MOM60_RAW > 0 at decision close; otherwise BTC_NONUP",
        }

    rng = Random(BOOTSTRAP_SEED)
    raw_p: dict[str, float] = {}
    summaries: dict[str, Any] = {}
    for name in FACTOR_NAMES:
        obs = observations[name]
        ics = [float(row["ic"]) for row in obs]
        mean_ic = sum(ics) / len(ics)
        persisted_sign = _sign(mean_ic)
        if persisted_sign == 0:
            persisted_sign = 1
        p_value, ci = _bootstrap_stats(ics, rng)
        raw_p[name] = p_value

        block_means = [sum(block) / len(block) for block in _four_blocks(ics)]
        years: dict[str, list[float]] = defaultdict(list)
        states: dict[str, list[float]] = defaultdict(list)
        for row in obs:
            years[row["year"]].append(float(row["ic"]))
            states[row["btc_state"]].append(float(row["ic"]))
        year_means = {year: sum(vals) / len(vals) for year, vals in years.items() if len(vals) >= 20}
        state_means = {state: sum(vals) / len(vals) for state, vals in states.items() if len(vals) >= 30}
        loo = {}
        for year in sorted(year_means):
            vals = [float(row["ic"]) for row in obs if row["year"] != year]
            loo[year] = sum(vals) / len(vals)

        aligned_spreads = [persisted_sign * float(row["raw_spread"]) for row in obs]
        previous: dict[str, float] = {}
        turnovers: list[float] = []
        for row in obs:
            current = {symbol: persisted_sign * weight for symbol, weight in row["weights"].items()}
            turnovers.append(_turnover(previous, current))
            previous = current
        net10 = [spread - turn * REALISTIC_BPS / 10_000.0 for spread, turn in zip(aligned_spreads, turnovers)]
        net20 = [spread - turn * STRESS_BPS / 10_000.0 for spread, turn in zip(aligned_spreads, turnovers)]
        summaries[name] = {
            "mean_ic": mean_ic,
            "persisted_sign": persisted_sign,
            "raw_p_value": p_value,
            "hac_lag4_tstat_diagnostic": _hac_tstat(ics, 4),
            "bootstrap_95_ci": list(ci),
            "sign_fraction": sum(_sign(value) == persisted_sign for value in ics) / len(ics),
            "chronological_block_means": block_means,
            "calendar_year_means": year_means,
            "btc_state_means": state_means,
            "leave_one_year_out_means": loo,
            "gross_aligned_spread_mean": sum(aligned_spreads) / len(aligned_spreads),
            "net10_aligned_spread_mean": sum(net10) / len(net10),
            "net20_aligned_spread_mean": sum(net20) / len(net20),
            "mean_turnover_both_legs": sum(turnovers) / len(turnovers),
        }

    holm = _holm_adjust(raw_p)
    passing: list[str] = []
    for name in FACTOR_NAMES:
        s = summaries[name]
        sign = int(s["persisted_sign"])
        block_means = s["chronological_block_means"]
        year_means = s["calendar_year_means"]
        state_means = s["btc_state_means"]
        loo = s["leave_one_year_out_means"]
        ci = s["bootstrap_95_ci"]
        gates = {
            "G0_EXECUTION": True,
            "G1_SUPPORT": True,
            "G2_MULTIPLE_TESTING": holm[name] < FWER_ALPHA,
            "G3_BOOTSTRAP": (ci[0] > 0 and sign > 0) or (ci[1] < 0 and sign < 0),
            "G4_SIGN_FRACTION": s["sign_fraction"] >= 0.55,
            "G5_CHRONOLOGY": sum(_sign(value) == sign for value in block_means) >= 3
            and all(not (_sign(value) == -sign and abs(value) >= 0.025) for value in block_means),
            "G6_CALENDAR": sum(_sign(value) == sign for value in year_means.values()) >= 3,
            "G7_BTC_STATE": set(state_means) == {"BTC_UP", "BTC_NONUP"}
            and all(_sign(value) == sign for value in state_means.values()),
            "G8_LEAVE_ONE_YEAR_OUT": bool(loo) and all(_sign(value) == sign for value in loo.values()),
            "G9_ECONOMIC": s["net10_aligned_spread_mean"] > 0 and s["net20_aligned_spread_mean"] >= 0,
        }
        s["holm_adjusted_p_value"] = holm[name]
        s["gates"] = gates
        if all(gates.values()):
            passing.append(name)

    return {
        "classification": "PASS_VALIDATED_FACTOR_ATLAS" if passing else "FAIL_NO_ROBUST_FACTOR_FAMILY",
        "execution_valid": True,
        "factor_candidates": 3,
        "support": support_detail,
        "factors": summaries,
        "passing_factors": passing,
        "btc_state_rule": "BTC_UP iff BTCUSDT MOM60_RAW > 0 at decision close; otherwise BTC_NONUP",
        "bootstrap": {"method": "moving-block", "block_weeks": 8, "replicates": 10_000, "seed": 860086},
        "cost_accounting": "cost_bps * sum(abs(current_weight - previous_weight)) across both long and short legs",
    }


class CrossSectionalFactorAtlas0086Engine:
    """Source-qualified post-marker engine. Runner owns reads and persistence."""

    def validate_source_keys(self, source_keys: Sequence[str]) -> None:
        validate_source_keys(source_keys)

    def execute(self, context: Any) -> Mapping[str, Any]:
        return analyze_panel(normalize_controlled_sources(context.sources))
