from __future__ import annotations

import csv
import io
import re
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Mapping, Sequence

from research.brrk_cross_sectional_factor_atlas_0086.engine import _parse_month
from .engine import FactorLSExecutionError

KLINE_RE = re.compile(
    r"^(?:stage/)?payloads/data__futures__um__monthly__klines__"
    r"(?P<symbol>[^/]+USDT)__1d__(?P=symbol)-1d-"
    r"(?P<year>20\d{2})-(?P<month>0[1-9]|1[0-2])\.zip$"
)
FUNDING_RE = re.compile(
    r"^(?:stage/)?payloads/data__futures__um__monthly__fundingRate__"
    r"(?P<symbol>[^/]+USDT)__(?P=symbol)-fundingRate-"
    r"(?P<year>20\d{2})-(?P<month>0[1-9]|1[0-2])\.zip$"
)


def validate_source_keys(source_keys: Sequence[str]) -> None:
    """Metadata-only source-interface qualification; never opens payload bytes."""
    if not source_keys:
        raise FactorLSExecutionError("NO_SOURCE_KEYS")
    logical: set[tuple[str, str, str]] = set()
    families: set[str] = set()
    symbols: set[str] = set()
    for key in source_keys:
        km = KLINE_RE.fullmatch(key)
        fm = FUNDING_RE.fullmatch(key)
        if bool(km) == bool(fm):
            raise FactorLSExecutionError(f"UNKNOWN_SOURCE_KEY:{key}")
        match = km or fm
        assert match is not None
        family = "kline" if km else "funding"
        symbol = match.group("symbol")
        month = f"{match.group('year')}-{match.group('month')}"
        identity = (family, symbol, month)
        if identity in logical:
            raise FactorLSExecutionError(f"DUPLICATE_LOGICAL_OBJECT:{family}:{symbol}:{month}")
        logical.add(identity)
        families.add(family)
        symbols.add(symbol)
    if families != {"kline", "funding"}:
        raise FactorLSExecutionError("MISSING_REQUIRED_SOURCE_FAMILY")
    if "BTCUSDT" not in symbols:
        raise FactorLSExecutionError("MISSING_BTCUSDT_SOURCE")


def _parse_funding_month(raw_zip: bytes, source_name: str, expected_month: str) -> list[dict[str, Any]]:
    try:
        with zipfile.ZipFile(io.BytesIO(raw_zip), "r") as archive:
            members = [info for info in archive.infolist() if not info.is_dir()]
            if len(members) != 1 or not members[0].filename.lower().endswith(".csv"):
                raise FactorLSExecutionError(f"INVALID_INNER_FUNDING_ZIP_MEMBERS:{source_name}")
            with archive.open(members[0], "r") as handle:
                text = handle.read().decode("utf-8-sig")
    except FactorLSExecutionError:
        raise
    except (zipfile.BadZipFile, UnicodeDecodeError, RuntimeError, OSError, EOFError) as exc:
        raise FactorLSExecutionError(f"INVALID_INNER_FUNDING_ZIP:{source_name}") from exc

    rows = [row for row in csv.reader(io.StringIO(text)) if row and any(cell.strip() for cell in row)]
    if not rows:
        return []
    header = None
    first = rows[0][0].strip().lower()
    if not first.lstrip("-").isdigit():
        header = [cell.strip().lower() for cell in rows.pop(0)]
    out = []
    previous = None
    for row in rows:
        if header is None:
            if len(row) < 3:
                raise FactorLSExecutionError(f"SHORT_FUNDING_ROW:{source_name}")
            stamp_raw, rate_raw = row[0], row[2]
        else:
            index = {name: i for i, name in enumerate(header)}
            stamp_i = next((index[name] for name in ("calc_time", "fundingtime", "funding_time") if name in index), None)
            rate_i = next((index[name] for name in ("last_funding_rate", "fundingrate", "funding_rate") if name in index), None)
            if stamp_i is None or rate_i is None or stamp_i >= len(row) or rate_i >= len(row):
                raise FactorLSExecutionError(f"MISSING_FUNDING_COLUMN:{source_name}")
            stamp_raw, rate_raw = row[stamp_i], row[rate_i]
        try:
            stamp = int(float(str(stamp_raw).strip()))
            rate = float(rate_raw)
        except (TypeError, ValueError) as exc:
            raise FactorLSExecutionError(f"INVALID_FUNDING_VALUE:{source_name}") from exc
        if not isfinite(rate):
            raise FactorLSExecutionError(f"NONFINITE_FUNDING_RATE:{source_name}")
        seconds = stamp / (1_000_000.0 if abs(stamp) >= 10**14 else 1_000.0 if abs(stamp) >= 10**11 else 1.0)
        try:
            instant = datetime.fromtimestamp(seconds, tz=timezone.utc)
        except (OverflowError, OSError, ValueError) as exc:
            raise FactorLSExecutionError(f"INVALID_FUNDING_TIMESTAMP:{source_name}") from exc
        if instant.strftime("%Y-%m") != expected_month:
            raise FactorLSExecutionError(f"FUNDING_MONTH_MISMATCH:{source_name}")
        if previous is not None and instant <= previous:
            raise FactorLSExecutionError(f"NON_INCREASING_FUNDING_TIMESTAMP:{source_name}")
        previous = instant
        out.append({"timestamp": instant.isoformat().replace("+00:00", "Z"), "rate": rate})
    return out


def normalize_controlled_sources(sources: Mapping[str, bytes]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    """Post-marker parser. The common runner owns the single physical read budget."""
    validate_source_keys(tuple(sources))
    kline_months: dict[str, list[tuple[str, str, bytes]]] = defaultdict(list)
    funding_months: dict[str, list[tuple[str, str, bytes]]] = defaultdict(list)
    for key, payload in sources.items():
        km = KLINE_RE.fullmatch(key)
        fm = FUNDING_RE.fullmatch(key)
        match = km or fm
        assert match is not None
        month = f"{match.group('year')}-{match.group('month')}"
        item = (month, key, payload)
        (kline_months if km else funding_months)[match.group("symbol")].append(item)

    panel: dict[str, list[dict[str, Any]]] = {}
    for symbol, objects in kline_months.items():
        rows: list[dict[str, Any]] = []
        previous = None
        for month, key, payload in sorted(objects):
            for row in _parse_month(payload, key, month):
                day = str(row["date"])
                if previous is not None and day <= previous:
                    raise FactorLSExecutionError(f"NON_INCREASING_SYMBOL_DATE:{symbol}:{day}")
                previous = day
                rows.append(row)
        panel[symbol] = rows

    funding: dict[str, list[dict[str, Any]]] = {}
    for symbol, objects in funding_months.items():
        rows: list[dict[str, Any]] = []
        previous = None
        for month, key, payload in sorted(objects):
            for row in _parse_funding_month(payload, key, month):
                stamp = str(row["timestamp"])
                if previous is not None and stamp <= previous:
                    raise FactorLSExecutionError(f"NON_INCREASING_SYMBOL_FUNDING:{symbol}:{stamp}")
                previous = stamp
                rows.append(row)
        funding[symbol] = rows
    return panel, funding
