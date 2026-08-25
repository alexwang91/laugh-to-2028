from __future__ import annotations

"""Post-marker source adapter for BRRK-MULTI-HORIZON-TREND-VOL-TARGET-0085.

The common controlled runner owns source identity/hash verification, durable
RUN_ATTEMPT.marker ordering, exactly-once outer payload reads and engine-call
counting. This module runs only inside that already-marked engine invocation.
It converts the ARM-bound staged Binance perpetual 1d monthly ZIP bytes into
the UTF-8 daily JSON interface consumed by the frozen Trend engine.

No network access, source discovery, candidate selection, parameter search or
pre-marker payload inspection occurs here.
"""

from datetime import datetime, timezone
from io import BytesIO, StringIO
from typing import Any, Mapping
import csv
import json
import re
import zipfile

from .engine import TrendExecutionError, TrendVolTargetEngine, run_from_sources

ASSET_SYMBOLS = {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT"}
SYMBOL_ASSETS = {symbol: asset for asset, symbol in ASSET_SYMBOLS.items()}

# GitHub Actions artifacts flatten the uploaded `stage/` directory and expose
# its members as `payloads/...`, while the frozen parent staging manifest records
# `stage/payloads/...`. Both names identify the same hash/size-bound object. The
# common runner verifies the physical artifact member before this adapter sees it.
_KLINE_PATH = re.compile(
    r"^(?:stage/)?payloads/data__futures__um__monthly__klines__"
    r"(?P<symbol>BTCUSDT|ETHUSDT|SOLUSDT)__1d__"
    r"(?P=symbol)-1d-(?P<year>20\d{2})-(?P<month>0[1-9]|1[0-2])\.zip$"
)
OPTIONAL_JSON = {"cash_daily.json", "canonical_brrk_daily.json"}


def _utc_date_from_open_time(raw: str) -> str:
    try:
        stamp = int(raw)
    except (TypeError, ValueError) as exc:
        raise TrendExecutionError("INVALID_KLINE_OPEN_TIME") from exc

    magnitude = abs(stamp)
    if magnitude >= 10**14:
        seconds = stamp / 1_000_000.0
    elif magnitude >= 10**11:
        seconds = stamp / 1_000.0
    else:
        seconds = float(stamp)
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc).date().isoformat()
    except (OverflowError, OSError, ValueError) as exc:
        raise TrendExecutionError("INVALID_KLINE_OPEN_TIME") from exc


def _one_csv_member(raw_zip: bytes, source_name: str) -> bytes:
    """Read one inner CSV once; ZipExtFile read performs CRC validation."""
    try:
        with zipfile.ZipFile(BytesIO(raw_zip), "r") as archive:
            members = [info for info in archive.infolist() if not info.is_dir()]
            if len(members) != 1 or not members[0].filename.lower().endswith(".csv"):
                raise TrendExecutionError(f"INVALID_INNER_ZIP_MEMBERS:{source_name}")
            with archive.open(members[0], "r") as handle:
                return handle.read()
    except TrendExecutionError:
        raise
    except (zipfile.BadZipFile, RuntimeError, OSError, EOFError) as exc:
        raise TrendExecutionError(f"INVALID_INNER_ZIP:{source_name}") from exc


def _monthly_closes(raw_zip: bytes, source_name: str, expected_month: str) -> list[dict[str, Any]]:
    csv_bytes = _one_csv_member(raw_zip, source_name)
    try:
        text = csv_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise TrendExecutionError(f"INVALID_KLINE_ENCODING:{source_name}") from exc

    rows: list[dict[str, Any]] = []
    previous_date: str | None = None
    reader = csv.reader(StringIO(text))
    for fields in reader:
        if not fields or all(not value.strip() for value in fields):
            continue
        first = fields[0].strip()
        if not first.lstrip("-").isdigit():
            if not rows and first.lower() in {"open_time", "opentime"}:
                continue
            raise TrendExecutionError(f"INVALID_KLINE_ROW:{source_name}")
        if len(fields) < 5:
            raise TrendExecutionError(f"SHORT_KLINE_ROW:{source_name}")
        day = _utc_date_from_open_time(first)
        if day[:7] != expected_month:
            raise TrendExecutionError(f"KLINE_MONTH_MISMATCH:{source_name}:{day}")
        try:
            close = float(fields[4])
        except (TypeError, ValueError) as exc:
            raise TrendExecutionError(f"INVALID_KLINE_CLOSE:{source_name}") from exc
        if not (close > 0.0) or close == float("inf") or close == float("-inf") or close != close:
            raise TrendExecutionError(f"INVALID_KLINE_CLOSE:{source_name}")
        if previous_date is not None and day <= previous_date:
            raise TrendExecutionError(f"NON_INCREASING_KLINE_DATE:{source_name}")
        previous_date = day
        rows.append({"date": day, "close": close})

    if not rows:
        raise TrendExecutionError(f"EMPTY_KLINE_MONTH:{source_name}")
    return rows


def normalize_controlled_sources(sources: Mapping[str, bytes]) -> dict[str, bytes]:
    """Convert ARM-bound monthly kline ZIPs to the frozen daily JSON interface."""
    by_asset: dict[str, list[tuple[str, str, bytes]]] = {asset: [] for asset in ASSET_SYMBOLS}
    passthrough: dict[str, bytes] = {}

    for name, payload in sources.items():
        if name in OPTIONAL_JSON:
            passthrough[name] = payload
            continue
        match = _KLINE_PATH.fullmatch(name)
        if match is None:
            raise TrendExecutionError(f"UNKNOWN_CONTROLLED_SOURCE:{name}")
        symbol = match.group("symbol")
        month = f"{match.group('year')}-{match.group('month')}"
        by_asset[SYMBOL_ASSETS[symbol]].append((month, name, payload))

    normalized: dict[str, bytes] = dict(passthrough)
    for asset, symbol in ASSET_SYMBOLS.items():
        objects = sorted(by_asset[asset], key=lambda item: item[0])
        if not objects:
            raise TrendExecutionError(f"MISSING_KLINE_ASSET:{asset}")
        months = [month for month, _, _ in objects]
        if len(months) != len(set(months)):
            raise TrendExecutionError(f"DUPLICATE_KLINE_MONTH:{asset}")

        combined: list[dict[str, Any]] = []
        previous_date: str | None = None
        for month, source_name, payload in objects:
            for row in _monthly_closes(payload, source_name, month):
                day = str(row["date"])
                if previous_date is not None and day <= previous_date:
                    raise TrendExecutionError(f"NON_INCREASING_ASSET_DATE:{asset}:{day}")
                previous_date = day
                combined.append(row)

        normalized[f"{asset.lower()}_daily.json"] = json.dumps(
            combined, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")

    return normalized


class ControlledArchiveTrendEngine:
    """0085 engine interface for ARM-bound staged monthly ZIP objects.

    Adapter/runtime failures must propagate to CONTROLLED_RESEARCH_RUNNER_V1 so
    the common runner can seal them as non-admissible INVALID_EXECUTION. This
    adapter must never convert an execution failure into a result Mapping,
    because any Mapping is treated by the runner as a candidate scientific
    result after exactly one engine invocation.
    """

    def execute(self, context: Any) -> Mapping[str, Any]:
        normalized = normalize_controlled_sources(context.sources)
        return run_from_sources(normalized)


ARM_EXECUTION_ENGINE = ControlledArchiveTrendEngine
