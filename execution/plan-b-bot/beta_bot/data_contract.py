from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_CONTRACT_PATH = REPO_ROOT / "config" / "data_contract.json"
DAY_MS = 86_400_000
HOUR_MS = 3_600_000
CANONICAL_ASSETS = ("BTC", "ETH", "SOL", "BNB")


class DataContractError(ValueError):
    """Raw observations do not satisfy the canonical P3.1 data contract."""


@dataclass(frozen=True)
class SourceMapping:
    asset: str
    source_symbol: str
    valid_from_ms: int | None
    valid_to_ms: int | None

    def contains(self, timestamp_ms: int) -> bool:
        return (self.valid_from_ms is None or timestamp_ms >= self.valid_from_ms) and (
            self.valid_to_ms is None or timestamp_ms < self.valid_to_ms
        )


@dataclass(frozen=True)
class DataContractPolicy:
    schema_version: int
    contract_id: str
    canonical_assets: tuple[str, ...]
    decision_timezone: str
    decision_time: str
    strategy_source_id: str
    strategy_endpoints: tuple[str, ...]
    strategy_interval: str
    strategy_time_zone: str
    expected_duration_ms: int
    source_mappings: dict[str, tuple[SourceMapping, ...]]
    funding_lookback_hours: int
    authorization: str

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "DataContractPolicy":
        boundary = raw["decision_boundary"]
        strategy = raw["strategy_daily_close"]
        funding = raw["router_market_inputs"]["funding"]
        mappings: dict[str, tuple[SourceMapping, ...]] = {}
        for asset, rows in strategy["source_mappings"].items():
            key = str(asset).upper()
            parsed: list[SourceMapping] = []
            for row in rows:
                parsed.append(
                    SourceMapping(
                        asset=key,
                        source_symbol=str(row["source_symbol"]).upper(),
                        valid_from_ms=_optional_midnight_ms(row.get("valid_from_utc")),
                        valid_to_ms=_optional_midnight_ms(row.get("valid_to_utc")),
                    )
                )
            mappings[key] = tuple(parsed)
        policy = cls(
            schema_version=int(raw["schema_version"]),
            contract_id=str(raw["contract_id"]),
            canonical_assets=tuple(str(x).upper() for x in raw["canonical_assets"]),
            decision_timezone=str(boundary["timezone"]),
            decision_time=str(boundary["time"]),
            strategy_source_id=str(strategy["source_id"]),
            strategy_endpoints=tuple(str(x) for x in strategy["endpoint_priority"]),
            strategy_interval=str(strategy["interval"]),
            strategy_time_zone=str(strategy["time_zone"]),
            expected_duration_ms=int(strategy["expected_duration_ms"]),
            source_mappings=mappings,
            funding_lookback_hours=int(funding["lookback_completed_hours"]),
            authorization=str(raw["authorization"]),
        )
        policy.validate()
        return policy

    def validate(self) -> None:
        if self.schema_version != 1:
            raise DataContractError("Unsupported data contract schema_version")
        if self.canonical_assets != CANONICAL_ASSETS:
            raise DataContractError("Canonical data assets must be BTC/ETH/SOL/BNB in order")
        if self.decision_timezone != "UTC" or self.decision_time != "00:00:00":
            raise DataContractError("Canonical daily boundary must be 00:00:00 UTC")
        if self.strategy_source_id != "BINANCE_SPOT_KLINES_V1":
            raise DataContractError("Frozen BRRK strategy source must remain Binance spot klines")
        if self.strategy_interval != "1d" or self.strategy_time_zone != "0":
            raise DataContractError("Strategy klines must be explicit UTC 1d candles")
        if self.expected_duration_ms != DAY_MS:
            raise DataContractError("Canonical daily candle duration must be 86400000 ms")
        if not self.strategy_endpoints:
            raise DataContractError("At least one strategy-data endpoint is required")
        if self.funding_lookback_hours <= 0:
            raise DataContractError("Funding lookback must be positive")
        if set(self.source_mappings) != set(CANONICAL_ASSETS):
            raise DataContractError("Every canonical asset requires an explicit source mapping")
        for asset in CANONICAL_ASSETS:
            mappings = self.source_mappings[asset]
            if not mappings:
                raise DataContractError(f"No source mappings for {asset}")
            ordered = sorted(
                mappings,
                key=lambda item: -10**30 if item.valid_from_ms is None else item.valid_from_ms,
            )
            for idx, mapping in enumerate(ordered):
                if not mapping.source_symbol:
                    raise DataContractError(f"Empty source symbol for {asset}")
                if (
                    mapping.valid_from_ms is not None
                    and mapping.valid_to_ms is not None
                    and mapping.valid_from_ms >= mapping.valid_to_ms
                ):
                    raise DataContractError(f"Invalid mapping interval for {asset}")
                if idx:
                    previous = ordered[idx - 1]
                    previous_end = previous.valid_to_ms
                    current_start = mapping.valid_from_ms
                    if previous_end is None or current_start is None or current_start < previous_end:
                        raise DataContractError(f"Overlapping source mappings for {asset}")
        if self.authorization != "DATA_CONTRACT_ONLY_NO_TARGET_OR_PRODUCTION_AUTHORIZATION":
            raise DataContractError("P3.1 contract must not authorize targets or production")

    def source_symbol(self, asset: str, session_open_ms: int) -> str:
        key = asset.upper()
        if key not in self.source_mappings:
            raise DataContractError(f"Asset {key} is outside canonical BRRK universe")
        matches = [item for item in self.source_mappings[key] if item.contains(int(session_open_ms))]
        if len(matches) != 1:
            raise DataContractError(
                f"Source mapping for {key} at {session_open_ms} must resolve exactly once"
            )
        return matches[0].source_symbol


@dataclass(frozen=True)
class DailyClose:
    asset: str
    source_symbol: str
    session_open_ms: int
    close_time_ms: int
    close: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CanonicalDailyDataset:
    schema_version: int
    contract_id: str
    decision_timestamp: str
    common_start_ms: int
    latest_session_open_ms: int
    closes_by_asset: dict[str, tuple[DailyClose, ...]]

    def close_values(self, asset: str) -> tuple[float, ...]:
        key = asset.upper()
        if key not in self.closes_by_asset:
            raise DataContractError(f"Missing canonical asset {key}")
        return tuple(row.close for row in self.closes_by_asset[key])

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "contract_id": self.contract_id,
            "decision_timestamp": self.decision_timestamp,
            "common_start_ms": self.common_start_ms,
            "latest_session_open_ms": self.latest_session_open_ms,
            "closes_by_asset": {
                asset: [row.to_dict() for row in self.closes_by_asset[asset]]
                for asset in CANONICAL_ASSETS
            },
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CanonicalFundingInput:
    asset: str
    router_as_of: str
    window_hours: int
    first_record_ms: int
    last_record_ms: int
    rates_bps_per_hour: tuple[float, ...]
    average_bps_per_hour: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CanonicalBasisInput:
    asset: str
    router_as_of: str
    perp_mark_price: float
    verified_spot_price: float
    perp_observed_at_ms: int
    spot_observed_at_ms: int
    observation_skew_ms: int
    basis_bps: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_data_contract(path: Path | None = None) -> DataContractPolicy:
    source = path or DEFAULT_DATA_CONTRACT_PATH
    return DataContractPolicy.from_mapping(json.loads(source.read_text(encoding="utf-8")))


def canonical_decision_time(value: str | datetime) -> datetime:
    dt = _parse_utc(value)
    if any((dt.hour, dt.minute, dt.second, dt.microsecond)):
        raise DataContractError("Daily decision timestamp must be exactly 00:00:00 UTC")
    return dt


def canonicalize_binance_daily_rows(
    *,
    asset: str,
    source_symbol: str,
    rows: Sequence[Sequence[Any]],
    decision_timestamp: str | datetime,
    policy: DataContractPolicy,
) -> tuple[DailyClose, ...]:
    decision = canonical_decision_time(decision_timestamp)
    decision_ms = _timestamp_ms(decision)
    key = asset.upper()
    symbol = source_symbol.upper()
    if key not in CANONICAL_ASSETS:
        raise DataContractError(f"Asset {key} is outside canonical BRRK universe")

    by_open: dict[int, DailyClose] = {}
    for raw in rows:
        if len(raw) < 7:
            raise DataContractError(f"Malformed Binance kline for {key}")
        try:
            open_ms = int(raw[0])
            close = float(raw[4])
            close_ms = int(raw[6])
        except (TypeError, ValueError) as exc:
            raise DataContractError(f"Malformed Binance kline values for {key}") from exc
        if open_ms % DAY_MS != 0:
            raise DataContractError(f"Non-midnight UTC daily kline for {key}")
        if close_ms != open_ms + policy.expected_duration_ms - 1:
            raise DataContractError(f"Unexpected daily close_time for {key}")
        if not isfinite(close) or close <= 0:
            raise DataContractError(f"Close must be finite and positive for {key}")
        expected_symbol = policy.source_symbol(key, open_ms)
        if symbol != expected_symbol:
            raise DataContractError(
                f"Source symbol {symbol} does not match canonical mapping {expected_symbol} for {key}"
            )
        # Current/in-progress/future daily candles are not canonical inputs yet.
        if close_ms >= decision_ms:
            continue
        if open_ms in by_open:
            raise DataContractError(f"Duplicate canonical day for {key}: {open_ms}")
        by_open[open_ms] = DailyClose(
            asset=key,
            source_symbol=symbol,
            session_open_ms=open_ms,
            close_time_ms=close_ms,
            close=close,
        )
    return tuple(by_open[key_ms] for key_ms in sorted(by_open))


def build_canonical_daily_dataset(
    *,
    source_batches: Mapping[str, Sequence[tuple[str, Sequence[Sequence[Any]]]]],
    decision_timestamp: str | datetime,
    policy: DataContractPolicy,
) -> CanonicalDailyDataset:
    decision = canonical_decision_time(decision_timestamp)
    decision_ms = _timestamp_ms(decision)
    latest_required = decision_ms - DAY_MS
    canonical: dict[str, dict[int, DailyClose]] = {}

    if set(asset.upper() for asset in source_batches) != set(CANONICAL_ASSETS):
        raise DataContractError("Canonical daily dataset requires BTC/ETH/SOL/BNB source batches")

    normalized_batches = {asset.upper(): batches for asset, batches in source_batches.items()}
    for asset in CANONICAL_ASSETS:
        rows_by_open: dict[int, DailyClose] = {}
        for source_symbol, raw_rows in normalized_batches[asset]:
            parsed = canonicalize_binance_daily_rows(
                asset=asset,
                source_symbol=source_symbol,
                rows=raw_rows,
                decision_timestamp=decision,
                policy=policy,
            )
            for row in parsed:
                if row.session_open_ms in rows_by_open:
                    raise DataContractError(
                        f"Duplicate canonical day across source batches for {asset}: {row.session_open_ms}"
                    )
                rows_by_open[row.session_open_ms] = row
        if not rows_by_open:
            raise DataContractError(f"No completed canonical daily closes for {asset}")
        if latest_required not in rows_by_open:
            raise DataContractError(f"Latest required UTC session is missing for {asset}")
        canonical[asset] = rows_by_open

    common_start = max(min(rows) for rows in canonical.values())
    if common_start > latest_required:
        raise DataContractError("No common canonical BRRK daily history")
    expected_days = range(common_start, latest_required + DAY_MS, DAY_MS)
    output: dict[str, tuple[DailyClose, ...]] = {}
    for asset in CANONICAL_ASSETS:
        missing = [day for day in expected_days if day not in canonical[asset]]
        if missing:
            raise DataContractError(
                f"Missing canonical UTC daily close for {asset} at {missing[0]}; forward-fill is forbidden"
            )
        output[asset] = tuple(canonical[asset][day] for day in expected_days)

    return CanonicalDailyDataset(
        schema_version=1,
        contract_id=policy.contract_id,
        decision_timestamp=_iso_z(decision),
        common_start_ms=common_start,
        latest_session_open_ms=latest_required,
        closes_by_asset=output,
    )


def canonicalize_funding_history(
    *,
    asset: str,
    records: Iterable[Mapping[str, Any]],
    router_as_of: str | datetime,
    policy: DataContractPolicy,
) -> CanonicalFundingInput:
    as_of = _parse_utc(router_as_of)
    as_of_ms = _timestamp_ms(as_of)
    key = asset.upper()
    if key not in CANONICAL_ASSETS:
        raise DataContractError(f"Asset {key} is outside canonical BRRK universe")

    rates_by_time: dict[int, float] = {}
    for record in records:
        try:
            time_ms = int(record["time"])
            decimal_rate = float(record["fundingRate"])
        except (KeyError, TypeError, ValueError) as exc:
            raise DataContractError(f"Malformed funding record for {key}") from exc
        if not isfinite(decimal_rate):
            raise DataContractError(f"Funding rate must be finite for {key}")
        if time_ms >= as_of_ms:
            continue
        if time_ms % HOUR_MS != 0:
            raise DataContractError(f"Funding record is not aligned to an hourly slot for {key}")
        if time_ms in rates_by_time:
            raise DataContractError(f"Duplicate funding slot for {key}: {time_ms}")
        rates_by_time[time_ms] = decimal_rate * 10_000.0

    latest_slot = ((as_of_ms - 1) // HOUR_MS) * HOUR_MS
    expected = [
        latest_slot - HOUR_MS * offset
        for offset in range(policy.funding_lookback_hours - 1, -1, -1)
    ]
    missing = [slot for slot in expected if slot not in rates_by_time]
    if missing:
        raise DataContractError(
            f"Missing completed funding slot for {key}: {missing[0]}"
        )
    rates = tuple(rates_by_time[slot] for slot in expected)
    return CanonicalFundingInput(
        asset=key,
        router_as_of=_iso_z(as_of),
        window_hours=policy.funding_lookback_hours,
        first_record_ms=expected[0],
        last_record_ms=expected[-1],
        rates_bps_per_hour=rates,
        average_bps_per_hour=sum(rates) / len(rates),
    )


def canonicalize_basis_input(
    *,
    asset: str,
    perp_mark_price: float,
    verified_spot_price: float,
    perp_observed_at_ms: int,
    spot_observed_at_ms: int,
    router_as_of: str | datetime,
) -> CanonicalBasisInput:
    as_of = _parse_utc(router_as_of)
    as_of_ms = _timestamp_ms(as_of)
    key = asset.upper()
    if key not in CANONICAL_ASSETS:
        raise DataContractError(f"Asset {key} is outside canonical BRRK universe")
    perp = float(perp_mark_price)
    spot = float(verified_spot_price)
    if not isfinite(perp) or not isfinite(spot) or perp <= 0 or spot <= 0:
        raise DataContractError("Basis prices must be finite and positive")
    perp_time = int(perp_observed_at_ms)
    spot_time = int(spot_observed_at_ms)
    if perp_time > as_of_ms or spot_time > as_of_ms:
        raise DataContractError("Basis observations cannot be after router_as_of")
    if perp_time < 0 or spot_time < 0:
        raise DataContractError("Basis observation timestamps cannot be negative")
    basis = (perp / spot - 1.0) * 10_000.0
    return CanonicalBasisInput(
        asset=key,
        router_as_of=_iso_z(as_of),
        perp_mark_price=perp,
        verified_spot_price=spot,
        perp_observed_at_ms=perp_time,
        spot_observed_at_ms=spot_time,
        observation_skew_ms=abs(perp_time - spot_time),
        basis_bps=basis,
    )


def canonical_digest(payload: Mapping[str, Any] | CanonicalDailyDataset) -> str:
    body = payload.to_dict() if isinstance(payload, CanonicalDailyDataset) else dict(payload)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _parse_utc(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as exc:
            raise DataContractError("Timestamp must be ISO-8601") from exc
    if dt.tzinfo is None or dt.utcoffset() != timezone.utc.utcoffset(dt):
        raise DataContractError("Timestamp must be timezone-aware UTC")
    return dt.astimezone(timezone.utc)


def _optional_midnight_ms(value: Any) -> int | None:
    if value is None:
        return None
    return _timestamp_ms(canonical_decision_time(str(value)))


def _timestamp_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def _iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
