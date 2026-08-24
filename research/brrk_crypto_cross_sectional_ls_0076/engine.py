"""Frozen Stage4 implementation for BRRK-CRYPTO-CROSS-SECTIONAL-LS-0076.

Pure stdlib. No filesystem/network access. The single scientific entrypoint accepts
already-authorized staged ZIP bytes, verifies identity/hash once, parses Binance
USD-M daily klines and monthly fundingRate files, and executes the complete frozen
Stage3 contract through terminal classification and canonical result serialization.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import statistics
import zipfile
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta, timezone
from random import Random
from typing import Iterable, Mapping, MutableMapping, Sequence

RESEARCH_ID = "BRRK-CRYPTO-CROSS-SECTIONAL-LS-0076"
CANDIDATE = "CROSS_SECTIONAL_MOMENTUM_SINGLE_BASELINE"
BLOCK_LENGTH = 20
BOOTSTRAP_REPLICATES = 4000
BOOTSTRAP_SEED = 760076
C1_COST = 0.0010
C2_COST = 0.0030
MIN_LISTING_DAYS = 180
MIN_UNIVERSE = 30
MIN_LEG = 6
TAIL_FRAC = 0.20
MAX_ABS_WEIGHT = 0.10
NEUTRAL_TOL = 1e-10
MIN_BETA_PAIRS = 45
MIN_DAILY_SUPPORT = 730
MIN_WEEKLY_SUPPORT = 104
MIN_YEAR_WEEKS = 13
MIN_PARTITION_WEEKS = 26
CAPACITY_NAV_USD = 1_000_000.0

# Static, identity-only exclusions frozen at implementation. These are not selected
# from scientific returns. Base-symbol matching is exact after stripping trailing USDT.
DENY_BASES = frozenset({
    # stablecoins / fiat proxies
    "USDC", "BUSD", "TUSD", "FDUSD", "USDP", "DAI", "USDE", "USDS", "EUR", "EURI",
    "GBP", "AUD", "BRL", "TRY", "BIDR", "IDRT", "RUB", "UAH", "NGN", "ZAR", "JPY",
    # common wrapped/pegged duplicates
    "WBTC", "WETH", "STETH", "WSTETH", "BTCB", "ETHW",
    # tokenized non-crypto equity/commodity identifiers observed in the identity universe class
    "AAPL", "AAPL B", "AMZN", "AMZN B", "AMD", "AMD B", "AMAT", "AMAT B", "AVGO", "AVGO B",
    "MSFT", "META", "NVDA", "TSLA", "GOOGL", "GOOG", "NFLX", "COIN", "MSTR", "XAU", "XAG",
})

KLINE_RE = re.compile(
    r"(?:^|/)data/futures/um/monthly/klines/(?P<symbol>[A-Z0-9]+)/1d/"
    r"(?P=symbol)-1d-(?P<month>20\d\d-(?:0[1-9]|1[0-2]))\.zip$"
)
FUNDING_RE = re.compile(
    r"(?:^|/)data/futures/um/monthly/fundingRate/(?P<symbol>[A-Z0-9]+)/"
    r"(?P=symbol)-fundingRate-(?P<month>20\d\d-(?:0[1-9]|1[0-2]))\.zip$"
)


class ExecutionInvalid(RuntimeError):
    pass


@dataclass(frozen=True)
class DailyBar:
    session: date
    symbol: str
    close: float
    quote_volume: float


@dataclass(frozen=True)
class FundingEvent:
    timestamp_ms: int
    symbol: str
    rate: float

    @property
    def session(self) -> date:
        return datetime.fromtimestamp(self.timestamp_ms / 1000.0, tz=timezone.utc).date()


@dataclass
class ReadLedger:
    authorized_hashes: Mapping[str, str]
    context: "ExecutionContext | None" = None
    read_counts: MutableMapping[str, int] = field(default_factory=dict)

    def consume(self, path: str, payload: bytes) -> None:
        if path not in self.authorized_hashes:
            raise ExecutionInvalid(f"unauthorized object: {path}")
        count = int(self.read_counts.get(path, 0))
        if count != 0:
            raise ExecutionInvalid(f"duplicate controlled read: {path}")
        # Opening/hashing the payload is itself the single controlled content read.
        self.read_counts[path] = 1
        if self.context is not None:
            self.context.controlled_object_reads += 1
            self.context.max_reads_per_object = max(self.context.max_reads_per_object, 1)
        expected = str(self.authorized_hashes[path]).lower()
        actual = hashlib.sha256(payload).hexdigest()
        if actual != expected:
            raise ExecutionInvalid(f"sha256 mismatch: {path}")

    def validate(self) -> bool:
        return set(self.read_counts).issubset(set(self.authorized_hashes)) and all(v == 1 for v in self.read_counts.values())


@dataclass
class ExecutionContext:
    scientific_engine_calls: int = 0
    scientific_source_network_fetches: int = 0
    controlled_object_reads: int = 0
    max_reads_per_object: int = 0

    def enter_engine(self) -> None:
        if self.scientific_engine_calls != 0:
            raise ExecutionInvalid("scientific engine called more than once")
        self.scientific_engine_calls = 1
        if self.scientific_source_network_fetches != 0:
            raise ExecutionInvalid("scientific source-network fetch budget drift")


@dataclass(frozen=True)
class Target:
    rebalance: date
    weights: Mapping[str, float]
    betas: Mapping[str, float]
    eligible_n: int
    long_n: int
    short_n: int
    median_quote_volume: Mapping[str, float]
    market_trend_60: float | None
    market_rvol_20: float | None
    market_liquidity: float | None


@dataclass
class PathState:
    dates: list[date] = field(default_factory=list)
    returns: list[float] = field(default_factory=list)
    nav: list[float] = field(default_factory=lambda: [1.0])
    weekly_returns: list[tuple[date, float]] = field(default_factory=list)
    turnovers: list[float] = field(default_factory=list)
    total_abs_traded: float = 0.0
    funding_pnl: float = 0.0
    trading_cost_pnl: float = 0.0
    asset_contrib: dict[str, float] = field(default_factory=dict)
    participation: list[float] = field(default_factory=list)
    gross_exposure: list[float] = field(default_factory=list)
    net_exposure: list[float] = field(default_factory=list)
    residual_beta: list[float] = field(default_factory=list)


@dataclass(frozen=True)
class EconomicMetrics:
    observations: int
    cumulative_return: float
    cagr: float
    annualized_volatility: float
    sharpe: float
    sortino: float
    max_drawdown: float
    calmar: float
    worst_1d: float
    worst_5d: float
    worst_7d: float
    worst_10d: float
    worst_20d: float
    expected_shortfall_5pct: float


@dataclass(frozen=True)
class ResultBundle:
    research_id: str
    classification: str
    execution_valid: bool
    support_valid: bool
    gates: Mapping[str, bool]
    c0: Mapping[str, object]
    c1: Mapping[str, object]
    c2: Mapping[str, object]
    inference: Mapping[str, object]
    robustness: Mapping[str, object]
    capacity_concentration: Mapping[str, object]
    execution: Mapping[str, object]

    def canonical_json_objects(self) -> Mapping[str, bytes]:
        primary = {
            "research_id": self.research_id,
            "classification": self.classification,
            "execution_valid": self.execution_valid,
            "support_valid": self.support_valid,
            "gates": dict(self.gates),
            "c1": dict(self.c1),
            "c2": dict(self.c2),
        }
        evidence = {
            "research_id": self.research_id,
            "inference": dict(self.inference),
            "robustness": dict(self.robustness),
            "capacity_concentration": dict(self.capacity_concentration),
            "c0": dict(self.c0),
        }
        execution = {"research_id": self.research_id, **dict(self.execution)}
        return {
            "PRIMARY_RESULT.json": _canonical_bytes(primary),
            "EVIDENCE.json": _canonical_bytes(evidence),
            "EXECUTION.json": _canonical_bytes(execution),
        }


def _json_safe(value: object) -> object:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(_json_safe(value), sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _safe_float(value: object, label: str) -> float:
    try:
        x = float(value)
    except Exception as exc:
        raise ExecutionInvalid(f"non-numeric {label}") from exc
    if not math.isfinite(x):
        raise ExecutionInvalid(f"non-finite {label}")
    return x


def _timestamp_ms(value: object, label: str) -> int:
    try:
        x = int(float(str(value).strip()))
    except Exception as exc:
        raise ExecutionInvalid(f"invalid {label}") from exc
    if x < 10**11 or x > 10**14:
        raise ExecutionInvalid(f"unexpected millisecond timestamp range: {label}")
    return x


def _csv_rows_from_zip(payload: bytes) -> list[list[str]]:
    try:
        with zipfile.ZipFile(io.BytesIO(payload), "r") as zf:
            members = [n for n in zf.namelist() if not n.endswith("/") and n.lower().endswith(".csv")]
            if len(members) != 1:
                raise ExecutionInvalid("authorized ZIP must contain exactly one CSV member")
            raw = zf.read(members[0])
    except ExecutionInvalid:
        raise
    except Exception as exc:
        raise ExecutionInvalid("unreadable ZIP/CSV payload") from exc
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ExecutionInvalid("CSV is not UTF-8") from exc
    return [row for row in csv.reader(io.StringIO(text)) if row and any(cell.strip() for cell in row)]


def _looks_header(row: Sequence[str]) -> bool:
    if not row:
        return False
    first = row[0].strip().lower()
    return any(ch.isalpha() for ch in first) or first in {"open_time", "calc_time", "fundingtime", "funding_time"}


def _parse_kline(path: str, symbol: str, expected_month: str, payload: bytes) -> list[DailyBar]:
    rows = _csv_rows_from_zip(payload)
    if not rows:
        raise ExecutionInvalid(f"empty kline CSV: {path}")
    header: list[str] | None = None
    if _looks_header(rows[0]):
        header = [c.strip().lower() for c in rows.pop(0)]
    out: list[DailyBar] = []
    for row in rows:
        if header is None:
            if len(row) < 8:
                raise ExecutionInvalid(f"short kline row: {path}")
            open_time, close, quote_volume = row[0], row[4], row[7]
        else:
            index = {name: i for i, name in enumerate(header)}
            def get(*names: str) -> str:
                for name in names:
                    if name in index and index[name] < len(row):
                        return row[index[name]]
                raise ExecutionInvalid(f"missing kline column {names}: {path}")
            open_time = get("open_time", "open time")
            close = get("close")
            quote_volume = get("quote_volume", "quote asset volume", "quote_asset_volume")
        ts = _timestamp_ms(open_time, "kline open_time")
        session = datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc).date()
        if session.strftime("%Y-%m") != expected_month:
            raise ExecutionInvalid(f"kline row month/path mismatch: {path}")
        c = _safe_float(close, "close")
        qv = _safe_float(quote_volume, "quote_volume")
        if c <= 0 or qv < 0:
            raise ExecutionInvalid("non-positive close or negative quote volume")
        out.append(DailyBar(session=session, symbol=symbol, close=c, quote_volume=qv))
    return out


def _parse_funding(path: str, symbol: str, expected_month: str, payload: bytes) -> list[FundingEvent]:
    rows = _csv_rows_from_zip(payload)
    if not rows:
        return []
    header: list[str] | None = None
    if _looks_header(rows[0]):
        header = [c.strip().lower() for c in rows.pop(0)]
    out: list[FundingEvent] = []
    for row in rows:
        if header is None:
            if len(row) < 3:
                raise ExecutionInvalid(f"short funding row: {path}")
            # Binance Vision monthly fundingRate archive positional schema:
            # calc_time, funding_interval_hours, last_funding_rate
            ts_raw, rate_raw = row[0], row[2]
        else:
            index = {name: i for i, name in enumerate(header)}
            def get(*names: str) -> str:
                for name in names:
                    if name in index and index[name] < len(row):
                        return row[index[name]]
                raise ExecutionInvalid(f"missing funding column {names}: {path}")
            ts_raw = get("calc_time", "fundingtime", "funding_time")
            rate_raw = get("last_funding_rate", "fundingrate", "funding_rate")
        ts = _timestamp_ms(ts_raw, "funding timestamp")
        if datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc).strftime("%Y-%m") != expected_month:
            raise ExecutionInvalid(f"funding row month/path mismatch: {path}")
        rate = _safe_float(rate_raw, "funding rate")
        out.append(FundingEvent(timestamp_ms=ts, symbol=symbol, rate=rate))
    return out


def decode_authorized_payloads(
    payloads: Mapping[str, bytes], authorized_hashes: Mapping[str, str], context: ExecutionContext | None = None
) -> tuple[list[DailyBar], list[FundingEvent], ReadLedger]:
    if set(payloads) != set(authorized_hashes):
        missing = sorted(set(authorized_hashes) - set(payloads))
        extra = sorted(set(payloads) - set(authorized_hashes))
        raise ExecutionInvalid(f"authorized payload set mismatch missing={missing[:3]} extra={extra[:3]}")
    ledger = ReadLedger(authorized_hashes=dict(authorized_hashes), context=context)
    bars: list[DailyBar] = []
    funding: list[FundingEvent] = []
    seen_bar_keys: set[tuple[str, date]] = set()
    seen_funding_keys: set[tuple[str, int]] = set()
    for path in sorted(payloads):
        payload = payloads[path]
        ledger.consume(path, payload)
        km = KLINE_RE.search(path)
        fm = FUNDING_RE.search(path)
        if bool(km) == bool(fm):
            raise ExecutionInvalid(f"object path outside frozen 0076 families: {path}")
        if km:
            symbol = km.group("symbol")
            for bar in _parse_kline(path, symbol, km.group("month"), payload):
                key = (bar.symbol, bar.session)
                if key in seen_bar_keys:
                    raise ExecutionInvalid(f"duplicate bar identity: {key}")
                seen_bar_keys.add(key)
                bars.append(bar)
        else:
            assert fm is not None
            symbol = fm.group("symbol")
            for event in _parse_funding(path, symbol, fm.group("month"), payload):
                key = (event.symbol, event.timestamp_ms)
                if key in seen_funding_keys:
                    raise ExecutionInvalid(f"duplicate funding identity: {key}")
                seen_funding_keys.add(key)
                funding.append(event)
    if not ledger.validate():
        raise ExecutionInvalid("read ledger invalid")
    bars.sort(key=lambda x: (x.session, x.symbol))
    funding.sort(key=lambda x: (x.timestamp_ms, x.symbol))
    return bars, funding, ledger


def _base_symbol(symbol: str) -> str:
    if not symbol.endswith("USDT"):
        return symbol
    return symbol[:-4]


def identity_allowed(symbol: str) -> bool:
    base = _base_symbol(symbol)
    normalized = base.replace("-", "").replace("_", "").upper()
    deny_norm = {x.replace(" ", "").replace("-", "").replace("_", "").upper() for x in DENY_BASES}
    if normalized in deny_norm:
        return False
    if normalized.endswith(("UP", "DOWN", "BULL", "BEAR")):
        return False
    return symbol.endswith("USDT")


def _date_range(start: date, end: date) -> list[date]:
    if end < start:
        return []
    return [start + timedelta(days=i) for i in range((end - start).days + 1)]


def _median(xs: Sequence[float]) -> float:
    if not xs:
        raise ExecutionInvalid("empty median")
    return float(statistics.median(xs))


def _sample_std(xs: Sequence[float]) -> float:
    if len(xs) < 2:
        return 0.0
    return float(statistics.stdev(xs))


class MarketState:
    def __init__(self, bars: Sequence[DailyBar], funding: Sequence[FundingEvent]):
        self.bars: dict[str, dict[date, DailyBar]] = {}
        for b in bars:
            self.bars.setdefault(b.symbol, {})[b.session] = b
        self.funding: dict[str, list[FundingEvent]] = {}
        for f in funding:
            self.funding.setdefault(f.symbol, []).append(f)
        self.first_date = {s: min(d) for s, d in self.bars.items() if d}
        self.all_dates = sorted({d for by_date in self.bars.values() for d in by_date})
        self._eligible_cache: dict[date, tuple[str, ...]] = {}
        self._benchmark_cache: dict[date, float] = {}

    def bar(self, symbol: str, d: date) -> DailyBar | None:
        return self.bars.get(symbol, {}).get(d)

    def close(self, symbol: str, d: date) -> float | None:
        b = self.bar(symbol, d)
        return None if b is None else b.close

    def eligible(self, decision_date: date) -> tuple[str, ...]:
        if decision_date in self._eligible_cache:
            return self._eligible_cache[decision_date]
        asof = decision_date - timedelta(days=1)
        out: list[str] = []
        for symbol in sorted(self.bars):
            if not identity_allowed(symbol):
                continue
            first = self.first_date[symbol]
            if (asof - first).days < MIN_LISTING_DAYS:
                continue
            required = [asof - timedelta(days=i) for i in range(61)]
            seq = [self.bar(symbol, d) for d in required]
            if any(b is None or b.close <= 0 for b in seq):
                continue
            beta_days = [asof - timedelta(days=i) for i in range(60)]
            pair_count = 0
            for d in beta_days:
                if self.close(symbol, d) is not None and self.close(symbol, d - timedelta(days=1)) is not None:
                    pair_count += 1
            if pair_count < MIN_BETA_PAIRS:
                continue
            qvs = [self.bar(symbol, asof - timedelta(days=i)).quote_volume for i in range(30)]
            if any((not math.isfinite(v) or v < 0) for v in qvs):
                continue
            if _median(qvs) < 1_000_000.0:
                continue
            if self.bar(symbol, asof) is None:
                continue
            out.append(symbol)
        result = tuple(out)
        self._eligible_cache[decision_date] = result
        return result

    def benchmark_daily_return(self, d: date) -> float:
        if d in self._benchmark_cache:
            return self._benchmark_cache[d]
        # Membership for return d-1 -> d is frozen from information through d-1.
        eligible = self.eligible(d)
        vals: list[float] = []
        for symbol in eligible:
            p0 = self.close(symbol, d - timedelta(days=1))
            p1 = self.close(symbol, d)
            if p0 is not None and p1 is not None and p0 > 0 and p1 > 0:
                vals.append(math.log(p1 / p0))
        if not vals:
            raise ExecutionInvalid(f"undefined benchmark return on {d}")
        value = sum(vals) / len(vals)
        self._benchmark_cache[d] = value
        return value

    def asset_beta(self, symbol: str, t: date) -> float:
        end = t - timedelta(days=1)
        pairs: list[tuple[float, float]] = []
        for offset in range(59, -1, -1):
            d = end - timedelta(days=offset)
            p0 = self.close(symbol, d - timedelta(days=1))
            p1 = self.close(symbol, d)
            if p0 is None or p1 is None or p0 <= 0 or p1 <= 0:
                continue
            try:
                b = self.benchmark_daily_return(d)
            except ExecutionInvalid:
                continue
            pairs.append((math.log(p1 / p0), b))
        if len(pairs) < MIN_BETA_PAIRS:
            raise ExecutionInvalid("insufficient beta pairs")
        am = sum(a for a, _ in pairs) / len(pairs)
        bm = sum(b for _, b in pairs) / len(pairs)
        denom = sum((b - bm) ** 2 for _, b in pairs)
        if denom <= 1e-18:
            raise ExecutionInvalid("singular benchmark beta")
        return sum((a - am) * (b - bm) for a, b in pairs) / denom

    def mom60(self, symbol: str, t: date) -> float:
        p1 = self.close(symbol, t - timedelta(days=1))
        p0 = self.close(symbol, t - timedelta(days=61))
        if p0 is None or p1 is None or p0 <= 0 or p1 <= 0:
            raise ExecutionInvalid("MOM60 missing close")
        return math.log(p1 / p0)

    def median_quote_volume_30(self, symbol: str, t: date) -> float:
        asof = t - timedelta(days=1)
        vals = []
        for i in range(30):
            b = self.bar(symbol, asof - timedelta(days=i))
            if b is None:
                raise ExecutionInvalid("missing quote volume")
            vals.append(b.quote_volume)
        return _median(vals)

    def funding_sum(self, symbol: str, start_exclusive: datetime, end_inclusive: datetime) -> float:
        lo = int(start_exclusive.timestamp() * 1000)
        hi = int(end_inclusive.timestamp() * 1000)
        return sum(f.rate for f in self.funding.get(symbol, ()) if lo < f.timestamp_ms <= hi)


def _project_neutral(raw: Mapping[str, float], betas: Mapping[str, float]) -> dict[str, float]:
    keys = sorted(raw)
    n = float(len(keys))
    sb = sum(betas[k] for k in keys)
    sb2 = sum(betas[k] ** 2 for k in keys)
    su = sum(raw[k] for k in keys)
    sbu = sum(betas[k] * raw[k] for k in keys)
    det = n * sb2 - sb * sb
    if not math.isfinite(det) or abs(det) <= 1e-14:
        raise ExecutionInvalid("singular beta-neutral projection")
    # inv([[n,sb],[sb,sb2]]) @ [su,sbu]
    lam0 = (sb2 * su - sb * sbu) / det
    lam1 = (-sb * su + n * sbu) / det
    w = {k: raw[k] - lam0 - lam1 * betas[k] for k in keys}
    gross = sum(abs(v) for v in w.values())
    if gross <= 0 or not math.isfinite(gross):
        raise ExecutionInvalid("zero/nonfinite projected gross")
    w = {k: v / gross for k, v in w.items()}
    for k in keys:
        if raw[k] > 0 and w[k] <= 0:
            raise ExecutionInvalid("long sign flip after neutralization")
        if raw[k] < 0 and w[k] >= 0:
            raise ExecutionInvalid("short sign flip after neutralization")
        if abs(w[k]) > MAX_ABS_WEIGHT + 1e-12:
            raise ExecutionInvalid("asset weight cap breach")
    net = sum(w.values())
    beta = sum(w[k] * betas[k] for k in keys)
    if abs(net) > NEUTRAL_TOL or abs(beta) > NEUTRAL_TOL:
        raise ExecutionInvalid("neutrality tolerance breach")
    return w


def build_target(mkt: MarketState, t: date) -> Target | None:
    eligible = list(mkt.eligible(t))
    if len(eligible) < MIN_UNIVERSE:
        return None
    scores = {s: mkt.mom60(s, t) for s in eligible}
    ranked = sorted(eligible, key=lambda s: (-scores[s], s))
    nleg = math.floor(TAIL_FRAC * len(ranked))
    if nleg < MIN_LEG:
        return None
    longs = ranked[:nleg]
    shorts = ranked[-nleg:]
    if set(longs) & set(shorts):
        raise ExecutionInvalid("long/short overlap")
    raw = {s: 0.5 / nleg for s in longs}
    raw.update({s: -0.5 / nleg for s in shorts})
    betas = {s: mkt.asset_beta(s, t) for s in raw}
    weights = _project_neutral(raw, betas)
    volumes = {s: mkt.median_quote_volume_30(s, t) for s in raw}
    trend = _market_trend(mkt, t)
    rvol = _market_rvol(mkt, t)
    liquidity = _market_liquidity(mkt, t)
    return Target(t, weights, betas, len(eligible), len(longs), len(shorts), volumes, trend, rvol, liquidity)


def _market_trend(mkt: MarketState, t: date) -> float | None:
    try:
        vals = [mkt.benchmark_daily_return(t - timedelta(days=i)) for i in range(1, 61)]
    except ExecutionInvalid:
        return None
    return math.exp(sum(vals)) - 1.0


def _market_rvol(mkt: MarketState, t: date) -> float | None:
    try:
        vals = [mkt.benchmark_daily_return(t - timedelta(days=i)) for i in range(1, 21)]
    except ExecutionInvalid:
        return None
    return _sample_std(vals) * math.sqrt(365.0)


def _market_liquidity(mkt: MarketState, t: date) -> float | None:
    vals = []
    for s in mkt.eligible(t):
        try:
            vals.append(mkt.median_quote_volume_30(s, t))
        except ExecutionInvalid:
            continue
    return _median(vals) if vals else None


def _mondays(start: date, end: date) -> list[date]:
    d = start
    while d.weekday() != 0:
        d += timedelta(days=1)
    out = []
    while d <= end:
        out.append(d)
        d += timedelta(days=7)
    return out


def build_targets(mkt: MarketState) -> dict[date, Target | None]:
    if not mkt.all_dates:
        return {}
    start = min(mkt.all_dates) + timedelta(days=MIN_LISTING_DAYS + 62)
    end = max(mkt.all_dates)
    return {t: build_target(mkt, t) for t in _mondays(start, end)}


def _drifted_weights(
    quantities: Mapping[str, float], mkt: MarketState, d: date, nav: float
) -> dict[str, float]:
    if nav <= 0:
        raise ExecutionInvalid("non-positive NAV")
    out = {}
    for s, q in quantities.items():
        p = mkt.close(s, d)
        if p is None or p <= 0:
            raise ExecutionInvalid(f"missing held-asset close {s} {d}")
        out[s] = q * p / nav
    return out


def _trade_delta(pre: Mapping[str, float], target: Mapping[str, float]) -> dict[str, float]:
    keys = set(pre) | set(target)
    return {s: float(target.get(s, 0.0)) - float(pre.get(s, 0.0)) for s in keys}


def simulate_paths(mkt: MarketState, targets: Mapping[date, Target | None]) -> tuple[PathState, PathState, PathState, list[dict[str, object]]]:
    mondays = sorted(targets)
    if len(mondays) < 2:
        return PathState(), PathState(), PathState(), []
    c0, c1, c2 = PathState(), PathState(), PathState()
    navs = {"C0": 1.0, "C1": 1.0, "C2": 1.0}
    quantities: dict[str, dict[str, float]] = {"C0": {}, "C1": {}, "C2": {}}
    weekly_meta: list[dict[str, object]] = []

    for wi in range(len(mondays) - 1):
        t, next_t = mondays[wi], mondays[wi + 1]
        target_obj = targets[t]
        target = {} if target_obj is None else dict(target_obj.weights)
        # Full interval requires a close on every calendar day for every target constituent.
        if target_obj is not None:
            for s in target:
                for d in _date_range(t, next_t):
                    if mkt.close(s, d) is None:
                        raise ExecutionInvalid(f"required realized close missing for held asset {s} {d}")
        week_start_nav = dict(navs)
        participation_week: list[float] = []

        # Rebalance at Monday close. Pretrade weights are marked from previous quantities.
        for label, state, cost_rate in (("C0", c0, 0.0), ("C1", c1, C1_COST), ("C2", c2, C2_COST)):
            pre = _drifted_weights(quantities[label], mkt, t, navs[label]) if quantities[label] else {}
            delta = _trade_delta(pre, target)
            abs_trade = sum(abs(v) for v in delta.values())
            state.turnovers.append(0.5 * abs_trade)
            state.total_abs_traded += abs_trade
            trading_cost = cost_rate * abs_trade * navs[label]
            navs[label] -= trading_cost
            state.trading_cost_pnl -= trading_cost
            if navs[label] <= 0:
                raise ExecutionInvalid("NAV exhausted by trading cost")
            quantities[label] = {}
            for s, w in target.items():
                p = mkt.close(s, t)
                if p is None or p <= 0:
                    raise ExecutionInvalid(f"missing execution close {s} {t}")
                quantities[label][s] = w * navs[label] / p
                if target_obj is not None:
                    vol = target_obj.median_quote_volume[s]
                    part = abs(delta.get(s, 0.0)) * CAPACITY_NAV_USD / vol if vol > 0 else math.inf
                    participation_week.append(part)
                    state.participation.append(part)
                if cost_rate:
                    state.asset_contrib[s] = state.asset_contrib.get(s, 0.0) - cost_rate * abs(delta.get(s, 0.0)) * navs[label]

        # Daily PnL from Monday close through next Monday close.
        day = t + timedelta(days=1)
        while day <= next_t:
            prev = day - timedelta(days=1)
            start_dt = datetime(prev.year, prev.month, prev.day, 23, 59, 59, 999000, tzinfo=timezone.utc)
            end_dt = datetime(day.year, day.month, day.day, 23, 59, 59, 999000, tzinfo=timezone.utc)
            for label, state in (("C0", c0), ("C1", c1), ("C2", c2)):
                nav_before = navs[label]
                price_pnl_total = 0.0
                funding_pnl_total = 0.0
                for s, q in quantities[label].items():
                    p0 = mkt.close(s, prev)
                    p1 = mkt.close(s, day)
                    if p0 is None or p1 is None or p0 <= 0 or p1 <= 0:
                        raise ExecutionInvalid(f"held asset mark missing {s} {day}")
                    price_pnl = q * (p1 - p0)
                    price_pnl_total += price_pnl
                    state.asset_contrib[s] = state.asset_contrib.get(s, 0.0) + price_pnl
                    if label != "C0":
                        rate = mkt.funding_sum(s, start_dt, end_dt)
                        mark_notional = q * p1
                        fpnl = -mark_notional * rate
                        if label == "C2":
                            fpnl = fpnl * (2.0 if fpnl < 0 else 0.5)
                        funding_pnl_total += fpnl
                        state.asset_contrib[s] += fpnl
                navs[label] += price_pnl_total + funding_pnl_total
                state.funding_pnl += funding_pnl_total
                if navs[label] <= 0 or not math.isfinite(navs[label]):
                    raise ExecutionInvalid("non-positive/nonfinite NAV")
                r = navs[label] / nav_before - 1.0
                state.dates.append(day)
                state.returns.append(r)
                state.nav.append(navs[label])
                if quantities[label]:
                    weights = _drifted_weights(quantities[label], mkt, day, navs[label])
                    state.gross_exposure.append(sum(abs(v) for v in weights.values()))
                    state.net_exposure.append(sum(weights.values()))
                    betas = target_obj.betas if target_obj is not None else {}
                    state.residual_beta.append(sum(weights.get(s, 0.0) * betas.get(s, 0.0) for s in weights))
                else:
                    state.gross_exposure.append(0.0)
                    state.net_exposure.append(0.0)
                    state.residual_beta.append(0.0)
            day += timedelta(days=1)

        for label, state in (("C0", c0), ("C1", c1), ("C2", c2)):
            state.weekly_returns.append((t, navs[label] / week_start_nav[label] - 1.0))
        target_net = sum(target.values()) if target else 0.0
        target_beta = (sum(target[s] * target_obj.betas[s] for s in target) if target_obj is not None else 0.0)
        target_max_weight = max((abs(v) for v in target.values()), default=0.0)
        weekly_meta.append({
            "date": t,
            "supported": target_obj is not None,
            "eligible_n": 0 if target_obj is None else target_obj.eligible_n,
            "long_n": 0 if target_obj is None else target_obj.long_n,
            "short_n": 0 if target_obj is None else target_obj.short_n,
            "trend60": None if target_obj is None else target_obj.market_trend_60,
            "rvol20": None if target_obj is None else target_obj.market_rvol_20,
            "liquidity": None if target_obj is None else target_obj.market_liquidity,
            "participation_max": max(participation_week) if participation_week else 0.0,
            "target_net": target_net,
            "target_beta": target_beta,
            "target_max_abs_weight": target_max_weight,
        })

    # Terminal exit at final Monday close, charged to C1/C2 and included in turnover/cost.
    exit_date = mondays[-1]
    for label, state, cost_rate in (("C0", c0, 0.0), ("C1", c1, C1_COST), ("C2", c2, C2_COST)):
        if quantities[label]:
            pre = _drifted_weights(quantities[label], mkt, exit_date, navs[label])
            delta = {s: -w for s, w in pre.items()}
            abs_trade = sum(abs(v) for v in delta.values())
            state.turnovers.append(0.5 * abs_trade)
            state.total_abs_traded += abs_trade
            cost = cost_rate * abs_trade * navs[label]
            navs[label] -= cost
            state.trading_cost_pnl -= cost
            for s, dw in delta.items():
                state.asset_contrib[s] = state.asset_contrib.get(s, 0.0) - cost_rate * abs(dw) * navs[label]
            quantities[label] = {}
            if navs[label] <= 0:
                raise ExecutionInvalid("terminal cost exhausted NAV")
            # Fold terminal transaction cost into final daily return/NAV observation.
            if state.returns:
                prev_nav = state.nav[-2] if len(state.nav) >= 2 else 1.0
                state.nav[-1] = navs[label]
                state.returns[-1] = navs[label] / prev_nav - 1.0
    return c0, c1, c2, weekly_meta


def _compounded(xs: Sequence[float]) -> float:
    x = 1.0
    for r in xs:
        x *= 1.0 + r
    return x - 1.0


def _worst_window(xs: Sequence[float], width: int) -> float:
    if len(xs) < width:
        return math.nan
    return min(_compounded(xs[i:i+width]) for i in range(len(xs) - width + 1))


def economic_metrics(state: PathState) -> EconomicMetrics:
    xs = state.returns
    n = len(xs)
    if not xs:
        return EconomicMetrics(0, 0.0, math.nan, math.nan, math.nan, math.nan, 0.0, math.nan,
                               math.nan, math.nan, math.nan, math.nan, math.nan, math.nan)
    cumulative = _compounded(xs)
    years = n / 365.0
    cagr = (1.0 + cumulative) ** (1.0 / years) - 1.0 if years > 0 and 1.0 + cumulative > 0 else -1.0
    vol_daily = _sample_std(xs)
    vol = vol_daily * math.sqrt(365.0)
    mean = sum(xs) / n
    sharpe = mean / vol_daily * math.sqrt(365.0) if vol_daily > 0 else (math.inf if mean > 0 else 0.0)
    downside = [min(0.0, r) for r in xs]
    downside_dev = math.sqrt(sum(r * r for r in downside) / n) if n else 0.0
    sortino = mean / downside_dev * math.sqrt(365.0) if downside_dev > 0 else (math.inf if mean > 0 else 0.0)
    peak = 1.0
    nav = 1.0
    mdd = 0.0
    for r in xs:
        nav *= 1.0 + r
        peak = max(peak, nav)
        mdd = min(mdd, nav / peak - 1.0)
    calmar = cagr / abs(mdd) if mdd < 0 else (math.inf if cagr > 0 else 0.0)
    sorted_x = sorted(xs)
    k = max(1, math.ceil(0.05 * n))
    es = sum(sorted_x[:k]) / k
    return EconomicMetrics(
        n, cumulative, cagr, vol, sharpe, sortino, mdd, calmar,
        min(xs), _worst_window(xs, 5), _worst_window(xs, 7), _worst_window(xs, 10), _worst_window(xs, 20), es,
    )


def moving_block_bootstrap_means(values: Sequence[float]) -> list[float]:
    xs = [float(x) for x in values]
    if len(xs) < BLOCK_LENGTH or any(not math.isfinite(x) for x in xs):
        raise ExecutionInvalid("bootstrap input insufficient/nonfinite")
    rng = Random(BOOTSTRAP_SEED)
    n = len(xs)
    blocks = math.ceil(n / BLOCK_LENGTH)
    out = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sample: list[float] = []
        for _ in range(blocks):
            start = rng.randrange(n)
            sample.extend(xs[(start + k) % n] for k in range(BLOCK_LENGTH))
        sample = sample[:n]
        out.append(sum(sample) / n)
    return out


def _quantile(xs: Sequence[float], q: float) -> float:
    vals = sorted(xs)
    if not vals:
        raise ExecutionInvalid("empty quantile")
    pos = q * (len(vals) - 1)
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    w = pos - lo
    return vals[lo] * (1.0 - w) + vals[hi] * w


def bootstrap_inference(values: Sequence[float]) -> dict[str, float]:
    draws = moving_block_bootstrap_means(values)
    count = sum(v <= 0.0 for v in draws)
    return {
        "one_sided_b": (count + 1.0) / (BOOTSTRAP_REPLICATES + 1.0),
        "mean_ci_low": _quantile(draws, 0.025),
        "mean_ci_high": _quantile(draws, 0.975),
        "replicates": BOOTSTRAP_REPLICATES,
        "block_length": BLOCK_LENGTH,
        "seed": BOOTSTRAP_SEED,
    }


def _moments(values: Sequence[float]) -> tuple[float, float, float, float]:
    n = len(values)
    if n < 3:
        raise ExecutionInvalid("insufficient moments")
    mean = sum(values) / n
    centered = [x - mean for x in values]
    m2 = sum(x*x for x in centered) / n
    if m2 <= 0:
        return mean, 0.0, 0.0, 3.0
    m3 = sum(x**3 for x in centered) / n
    m4 = sum(x**4 for x in centered) / n
    skew = m3 / (m2 ** 1.5)
    kurt = m4 / (m2 * m2)
    return mean, math.sqrt(m2), skew, kurt


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def psr_dsr(values: Sequence[float]) -> tuple[float, float]:
    n = len(values)
    mean, std_pop, skew, kurt = _moments(values)
    if std_pop <= 0:
        p = 1.0 if mean > 0 else 0.5 if mean == 0 else 0.0
        return p, p
    sr = mean / std_pop
    denom2 = 1.0 - skew * sr + ((kurt - 1.0) / 4.0) * sr * sr
    if denom2 <= 0:
        raise ExecutionInvalid("PSR denominator undefined")
    z = sr * math.sqrt(max(1, n - 1)) / math.sqrt(denom2)
    psr = _normal_cdf(z)
    # Exactly one declared candidate => expected maximum null Sharpe is zero;
    # one-trial DSR reduces to the same probabilistic Sharpe benchmark.
    return psr, psr


def _expanding_median_labels(points: Sequence[tuple[date, float | None]]) -> dict[date, str]:
    hist: list[float] = []
    out: dict[date, str] = {}
    for d, v in sorted(points):
        if v is None or not math.isfinite(v):
            continue
        if hist:
            med = _median(hist)
            out[d] = "HIGH" if v > med else "LOW"
        hist.append(v)
    return out


def robustness(c1: PathState, weekly_meta: Sequence[Mapping[str, object]]) -> dict[str, object]:
    week_ret = dict(c1.weekly_returns)
    supported = [m for m in weekly_meta if bool(m["supported"]) and m["date"] in week_ret]
    years: dict[str, list[float]] = {}
    bull: list[float] = []; bear: list[float] = []
    for m in supported:
        d = m["date"]; r = week_ret[d]
        years.setdefault(str(d.year), []).append(r)
        tr = m.get("trend60")
        if tr is not None:
            (bull if float(tr) >= 0 else bear).append(r)
    vol_labels = _expanding_median_labels([(m["date"], m.get("rvol20")) for m in supported])
    liq_labels = _expanding_median_labels([(m["date"], m.get("liquidity")) for m in supported])
    vol = {"HIGH": [], "LOW": []}; liq = {"HIGH": [], "LOW": []}
    for m in supported:
        d = m["date"]; r = week_ret[d]
        if d in vol_labels: vol[vol_labels[d]].append(r)
        if d in liq_labels: liq[liq_labels[d]].append(r)
    supported_years = {y: rs for y, rs in years.items() if len(rs) >= MIN_YEAR_WEEKS}
    lyo: dict[str, dict[str, float]] = {}
    if len(supported_years) >= 3:
        for omit in sorted(supported_years):
            rs = [r for y, vals in supported_years.items() if y != omit for r in vals]
            lyo[omit] = {"cumulative_return": _compounded(rs), "sharpe": _weekly_sharpe(rs)}
    return {
        "years": {y: {"weeks": len(rs), "cumulative_return": _compounded(rs), "sharpe": _weekly_sharpe(rs)} for y, rs in sorted(years.items())},
        "supported_years": sorted(supported_years),
        "bull": {"weeks": len(bull), "cumulative_return": _compounded(bull) if bull else None},
        "bear": {"weeks": len(bear), "cumulative_return": _compounded(bear) if bear else None},
        "volatility": {k: {"weeks": len(v), "cumulative_return": _compounded(v) if v else None} for k, v in vol.items()},
        "liquidity": {k: {"weeks": len(v), "cumulative_return": _compounded(v) if v else None} for k, v in liq.items()},
        "leave_one_year_out": lyo,
        "theme_leave_out": "NOT_EVALUATED",
    }


def _weekly_sharpe(rs: Sequence[float]) -> float:
    if not rs:
        return math.nan
    sd = _sample_std(rs)
    mean = sum(rs) / len(rs)
    return mean / sd * math.sqrt(52.0) if sd > 0 else (math.inf if mean > 0 else 0.0)


def support_check(c1: PathState, weekly_meta: Sequence[Mapping[str, object]], rob: Mapping[str, object]) -> tuple[bool, dict[str, object]]:
    supported = [m for m in weekly_meta if bool(m["supported"])]
    med_n = _median([float(m["eligible_n"]) for m in supported]) if supported else 0.0
    med_long = _median([float(m["long_n"]) for m in supported]) if supported else 0.0
    med_short = _median([float(m["short_n"]) for m in supported]) if supported else 0.0
    years = rob["years"]
    supported_year_count = sum(1 for v in years.values() if int(v["weeks"]) >= MIN_YEAR_WEEKS)
    bull_weeks = int(rob["bull"]["weeks"]); bear_weeks = int(rob["bear"]["weeks"])
    details = {
        "daily_observations": len(c1.returns),
        "weekly_intervals": len(supported),
        "supported_year_count": supported_year_count,
        "median_eligible_universe": med_n,
        "median_long_count": med_long,
        "median_short_count": med_short,
        "bull_weeks": bull_weeks,
        "bear_weeks": bear_weeks,
    }
    ok = (
        len(c1.returns) >= MIN_DAILY_SUPPORT
        and len(supported) >= MIN_WEEKLY_SUPPORT
        and supported_year_count >= 3
        and med_n >= MIN_UNIVERSE
        and med_long >= MIN_LEG
        and med_short >= MIN_LEG
        and bull_weeks >= MIN_PARTITION_WEEKS
        and bear_weeks >= MIN_PARTITION_WEEKS
    )
    return ok, details


def capacity_concentration(state: PathState, metrics: EconomicMetrics) -> dict[str, object]:
    parts = sorted(x for x in state.participation if math.isfinite(x))
    p95 = _quantile(parts, 0.95) if parts else math.inf
    pmax = max(parts) if parts else math.inf
    abs_total = sum(abs(v) for v in state.asset_contrib.values())
    shares = {s: abs(v) / abs_total for s, v in state.asset_contrib.items()} if abs_total > 0 else {}
    max_share = max(shares.values()) if shares else math.inf
    largest = max(state.asset_contrib, key=lambda s: abs(state.asset_contrib[s])) if state.asset_contrib else None
    removed_cum = metrics.cumulative_return - (state.asset_contrib.get(largest, 0.0) if largest else 0.0)
    return {
        "participation_p95": p95,
        "participation_max": pmax,
        "max_abs_asset_contribution_share": max_share,
        "largest_abs_contributor": largest,
        "remove_largest_contributor_cumulative_return": removed_cum,
    }


def cost_break_even_multiplier(c0: PathState, c1: PathState) -> float:
    # C1 includes funding + 1x variable cost. Reconstruct cumulative before variable
    # cost in NAV-dollar units and divide by the observed 1x variable cost drag.
    if c1.total_abs_traded <= 0:
        return math.inf
    one_x_drag = abs(c1.trading_cost_pnl)
    if one_x_drag <= 0:
        return math.inf
    c1_final = c1.nav[-1] if c1.nav else 1.0
    before_variable = c1_final + one_x_drag
    available_profit = before_variable - 1.0
    return max(0.0, available_profit / one_x_drag)


def _metrics_dict(m: EconomicMetrics) -> dict[str, object]:
    d = asdict(m)
    return {k: (None if isinstance(v, float) and not math.isfinite(v) else v) for k, v in d.items()}


def evaluate_gates(
    c1m: EconomicMetrics,
    c2m: EconomicMetrics,
    inference: Mapping[str, object],
    rob: Mapping[str, object],
    cap: Mapping[str, object],
    c1: PathState,
    weekly_meta: Sequence[Mapping[str, object]],
    cost_be: float,
    execution_valid: bool,
) -> dict[str, bool]:
    years = [v for v in rob["years"].values() if int(v["weeks"]) >= MIN_YEAR_WEEKS]
    positive_year_frac = sum(float(v["cumulative_return"]) > 0 for v in years) / len(years) if years else 0.0
    bull = rob["bull"]; bear = rob["bear"]
    lyo = rob["leave_one_year_out"]
    lyo_ok = bool(lyo) and all(float(v["cumulative_return"]) > 0 for v in lyo.values())
    finite_lyo = [float(v["sharpe"]) for v in lyo.values() if math.isfinite(float(v["sharpe"]))]
    if finite_lyo:
        median_lyo_sharpe = _median(finite_lyo)
    elif lyo and all(float(v["sharpe"]) > 0 for v in lyo.values()):
        median_lyo_sharpe = math.inf
    else:
        median_lyo_sharpe = -math.inf
    traded_rebalances = [m for m in weekly_meta if bool(m.get("supported"))]
    neutrality_ok = bool(traded_rebalances) and all(
        abs(float(m["target_net"])) <= NEUTRAL_TOL
        and abs(float(m["target_beta"])) <= NEUTRAL_TOL
        and float(m["target_max_abs_weight"]) <= MAX_ABS_WEIGHT + 1e-12
        for m in traded_rebalances
    )
    g = {
        "G0": execution_valid,
        "G1": c1m.cagr > 0 and c1m.sharpe >= 0.50,
        "G2": float(inference["bootstrap"]["one_sided_b"]) <= 0.05 and float(inference["bootstrap"]["mean_ci_low"]) > 0,
        "G3": float(inference["psr"]) >= 0.95 and float(inference["dsr_one_trial"]) >= 0.95,
        "G4": c2m.cagr > 0 and c2m.sharpe > 0,
        "G5": cost_be >= 2.0,
        "G6": positive_year_frac >= 0.60 and int(bull["weeks"]) >= MIN_PARTITION_WEEKS and int(bear["weeks"]) >= MIN_PARTITION_WEEKS and float(bull["cumulative_return"]) > 0 and float(bear["cumulative_return"]) > 0,
        "G7": lyo_ok and median_lyo_sharpe >= 0.50 * c1m.sharpe,
        "G8": neutrality_ok and all(x <= 1.0 + 1e-8 for x in c1.gross_exposure),
        "G9": float(cap["participation_p95"]) <= 0.01 and float(cap["participation_max"]) <= 0.05,
        "G10": float(cap["max_abs_asset_contribution_share"]) <= 0.35 and float(cap["remove_largest_contributor_cumulative_return"]) > 0,
        "G11": c1m.max_drawdown > -0.50 and c1m.worst_7d > -0.25,
    }
    return g


def _invalid_result(ctx: ExecutionContext, authorized_count: int, reason: str) -> ResultBundle:
    gates = {f"G{i}": False for i in range(12)}
    return ResultBundle(
        research_id=RESEARCH_ID,
        classification="INVALID_EXECUTION",
        execution_valid=False,
        support_valid=False,
        gates=gates,
        c0={}, c1={}, c2={},
        inference={"invalid_reason": reason},
        robustness={},
        capacity_concentration={},
        execution={
            "candidate": CANDIDATE,
            "declared_candidates": 1,
            "actual_candidates_evaluated": 0,
            "scientific_engine_calls": ctx.scientific_engine_calls,
            "scientific_source_network_fetches": ctx.scientific_source_network_fetches,
            "authorized_objects": authorized_count,
            "controlled_object_reads": ctx.controlled_object_reads,
            "max_reads_per_object": ctx.max_reads_per_object,
            "read_ledger_valid": False,
            "invalid_reason": reason,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        },
    )


def run_scientific_engine(
    payloads: Mapping[str, bytes],
    authorized_hashes: Mapping[str, str],
    *,
    context: ExecutionContext | None = None,
) -> ResultBundle:
    """Exactly-one-call scientific entrypoint for Stage8.

    The caller is responsible only for loading each already-authorized object byte
    sequence after the durable attempt marker. No scientific transformation exists
    outside this entrypoint.
    """
    ctx = context if context is not None else ExecutionContext()
    ctx.enter_engine()
    try:
        bars, funding, ledger = decode_authorized_payloads(payloads, authorized_hashes, ctx)
        mkt = MarketState(bars, funding)
        targets = build_targets(mkt)
        c0, c1, c2, weekly_meta = simulate_paths(mkt, targets)
        c0m, c1m, c2m = economic_metrics(c0), economic_metrics(c1), economic_metrics(c2)
        rob = robustness(c1, weekly_meta)
        support_valid, support_details = support_check(c1, weekly_meta, rob)
        execution_valid = (
            ctx.scientific_engine_calls == 1
            and ctx.scientific_source_network_fetches == 0
            and ledger.validate()
            and len(ledger.read_counts) == len(authorized_hashes)
        )
        if not execution_valid:
            classification = "INVALID_EXECUTION"
            gates = {f"G{i}": False for i in range(12)}
            inf: dict[str, object] = {"support": support_details}
            cap = capacity_concentration(c1, c1m)
        elif not support_valid:
            classification = "INCONCLUSIVE_INSUFFICIENT_SUPPORT"
            gates = {f"G{i}": False for i in range(12)}
            gates["G0"] = True
            inf = {"support": support_details}
            cap = capacity_concentration(c1, c1m)
        else:
            boot = bootstrap_inference(c1.returns)
            psr, dsr = psr_dsr(c1.returns)
            inf = {"support": support_details, "bootstrap": boot, "psr": psr, "dsr_one_trial": dsr, "pbo": "NOT_EVALUATED_SINGLE_CANDIDATE"}
            cap = capacity_concentration(c1, c1m)
            be = cost_break_even_multiplier(c0, c1)
            gates = evaluate_gates(c1m, c2m, inf, rob, cap, c1, weekly_meta, be, execution_valid)
            classification = "PASS_CROSS_SECTIONAL_MOMENTUM_LS_BASELINE" if all(gates.values()) else "FAIL_NO_ROBUST_CROSS_SECTIONAL_MOMENTUM_LS_ECONOMICS"
        be = cost_break_even_multiplier(c0, c1)
        return ResultBundle(
            research_id=RESEARCH_ID,
            classification=classification,
            execution_valid=execution_valid,
            support_valid=support_valid,
            gates=gates,
            c0={**_metrics_dict(c0m), "funding_pnl": c0.funding_pnl, "trading_cost_pnl": c0.trading_cost_pnl},
            c1={**_metrics_dict(c1m), "funding_pnl": c1.funding_pnl, "trading_cost_pnl": c1.trading_cost_pnl, "total_abs_traded": c1.total_abs_traded, "cost_break_even_multiplier": be},
            c2={**_metrics_dict(c2m), "funding_pnl": c2.funding_pnl, "trading_cost_pnl": c2.trading_cost_pnl},
            inference=inf,
            robustness=rob,
            capacity_concentration=cap,
            execution={
                "candidate": CANDIDATE,
                "declared_candidates": 1,
                "actual_candidates_evaluated": 1,
                "scientific_engine_calls": ctx.scientific_engine_calls,
                "scientific_source_network_fetches": ctx.scientific_source_network_fetches,
                "authorized_objects": len(authorized_hashes),
                "controlled_object_reads": ctx.controlled_object_reads,
                "max_reads_per_object": ctx.max_reads_per_object,
                "read_ledger_valid": ledger.validate(),
                "production_authorized": False,
                "signature_authorized": False,
                "order_submission_authorized": False,
            },
        )
    except ExecutionInvalid as exc:
        return _invalid_result(ctx, len(authorized_hashes), str(exc))
    except Exception as exc:
        return _invalid_result(ctx, len(authorized_hashes), f"unhandled frozen-engine error: {type(exc).__name__}: {exc}")


def create_only_result_objects(result: ResultBundle, existing_paths: Iterable[str]) -> Mapping[str, bytes]:
    outputs = result.canonical_json_objects()
    existing = set(existing_paths)
    collisions = sorted(existing & set(outputs))
    if collisions:
        raise FileExistsError(f"create-only result collision: {collisions}")
    return outputs
