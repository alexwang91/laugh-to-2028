from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

CONTRACT_PATH = Path(__file__).with_name("DATA_CONTRACT.json")
HISTORICAL_CUTOFF_UTC = datetime(2026, 8, 8, 0, 0, 0, tzinfo=timezone.utc)
HISTORICAL_AVAILABILITY_LAG = timedelta(days=2)
DATASET_ID = "DEFILLAMA-STABLECOIN-ALL-CHARTS"
SOURCE_ID = "DEFILLAMA-STABLECOIN-ALL-CHARTS-V1"
PARSER_VERSION = "STABLECOIN-DATA-PARSER-V1"


@dataclass(frozen=True, order=True)
class SourcePoint:
    metric_timestamp: datetime
    value: float


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_frozen_contract(contract: dict[str, object] | None = None) -> None:
    contract = contract or load_contract()
    if contract.get("research_id") != "STABLECOIN-LIQUIDITY-0001":
        raise ValueError("unexpected research_id")
    if contract.get("production_authorized") is not False:
        raise ValueError("data contract cannot confer production authority")
    source = contract.get("source")
    if not isinstance(source, dict):
        raise ValueError("missing source contract")
    if source.get("source_id") != SOURCE_ID:
        raise ValueError("unexpected source_id")
    if source.get("url") != "https://stablecoins.llama.fi/stablecoincharts/all":
        raise ValueError("unexpected source URL")
    pit = contract.get("pit_publication_semantics")
    if not isinstance(pit, dict) or pit.get("historical_available_at_seconds") != 172800:
        raise ValueError("historical LAG_2D semantics changed")
    coverage = contract.get("coverage_contract")
    if not isinstance(coverage, dict) or coverage.get("historical_cutoff_utc") != "2026-08-08T00:00:00Z":
        raise ValueError("historical coverage cutoff changed")


def _parse_unix_string(value: object) -> datetime:
    if not isinstance(value, str) or not value.isdigit():
        raise ValueError("date must be an integer Unix timestamp encoded as string")
    seconds = int(value)
    if seconds < 0:
        raise ValueError("negative Unix timestamp")
    return datetime.fromtimestamp(seconds, tz=timezone.utc)


def _parse_value(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("peggedUSD must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0:
        raise ValueError("peggedUSD must be finite and non-negative")
    return numeric


def parse_source_payload(raw_bytes: bytes) -> list[SourcePoint]:
    try:
        payload = json.loads(raw_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid JSON payload") from exc
    if not isinstance(payload, list):
        raise ValueError("source payload root must be an array")

    points: list[SourcePoint] = []
    seen: set[datetime] = set()
    for index, row in enumerate(payload):
        if not isinstance(row, dict):
            raise ValueError(f"row {index} must be an object")
        timestamp = _parse_unix_string(row.get("date"))
        total_usd = row.get("totalCirculatingUSD")
        if not isinstance(total_usd, dict):
            raise ValueError(f"row {index} missing totalCirculatingUSD object")
        value = _parse_value(total_usd.get("peggedUSD"))
        if timestamp in seen:
            raise ValueError(f"duplicate metric timestamp: {timestamp.isoformat()}")
        seen.add(timestamp)
        points.append(SourcePoint(timestamp, value))
    return sorted(points)


def select_frozen_historical_coverage(points: list[SourcePoint]) -> list[SourcePoint]:
    return [point for point in points if point.metric_timestamp <= HISTORICAL_CUTOFF_UTC]


def historical_available_at(metric_timestamp: datetime) -> datetime:
    if metric_timestamp.tzinfo is None or metric_timestamp.utcoffset() is None:
        raise ValueError("metric_timestamp must be timezone-aware")
    return metric_timestamp.astimezone(timezone.utc) + HISTORICAL_AVAILABILITY_LAG


def exact_lag_value(points: list[SourcePoint], metric_timestamp: datetime, days: int) -> float | None:
    if days < 0:
        raise ValueError("days must be non-negative")
    if metric_timestamp.tzinfo is None or metric_timestamp.utcoffset() is None:
        raise ValueError("metric_timestamp must be timezone-aware")
    target = metric_timestamp.astimezone(timezone.utc) - timedelta(days=days)
    lookup = {point.metric_timestamp: point.value for point in points}
    return lookup.get(target)
