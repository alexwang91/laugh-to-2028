from datetime import datetime, timezone

import pytest

from beta_bot.data_contract import (
    DAY_MS,
    HOUR_MS,
    CANONICAL_ASSETS,
    STRATEGY_FEATURE_ASSETS,
    STRATEGY_SIGNAL_ASSETS,
    DataContractError,
    build_canonical_daily_dataset,
    canonical_decision_time,
    canonical_digest,
    canonicalize_basis_input,
    canonicalize_binance_daily_rows,
    canonicalize_funding_history,
    load_data_contract,
)
from beta_bot.model import build_signal


def kline(day: int, close: float):
    open_ms = day * DAY_MS
    return [
        open_ms,
        str(close - 1),
        str(close + 1),
        str(close - 2),
        str(close),
        "100",
        open_ms + DAY_MS - 1,
        "1000",
        10,
        "50",
        "500",
        "0",
    ]


def source_batches(days, *, reverse=False):
    policy = load_data_contract()
    output = {}
    bases = {"BTC": 30_000.0, "ETH": 2_000.0, "SOL": 100.0, "BNB": 300.0, "XRP": 0.5}
    for asset in STRATEGY_SIGNAL_ASSETS:
        rows = [kline(day, bases[asset] + day * 0.25) for day in days]
        if reverse:
            rows = list(reversed(rows))
        symbol = policy.source_symbol(asset, days[0] * DAY_MS)
        output[asset] = [(symbol, rows)]
    return output


def test_contract_freezes_target_feature_roles_source_utc_boundary_and_no_production_auth():
    policy = load_data_contract()
    assert policy.schema_version == 2
    assert policy.canonical_assets == CANONICAL_ASSETS
    assert policy.strategy_feature_assets == STRATEGY_FEATURE_ASSETS == ("XRP",)
    assert policy.strategy_signal_assets == STRATEGY_SIGNAL_ASSETS
    assert policy.strategy_source_id == "BINANCE_SPOT_KLINES_V1"
    assert policy.strategy_interval == "1d"
    assert policy.strategy_time_zone == "0"
    assert policy.expected_duration_ms == DAY_MS
    assert policy.source_symbol("BTC", 0) == "BTCUSDT"
    assert policy.source_symbol("ETH", 0) == "ETHUSDT"
    assert policy.source_symbol("SOL", 0) == "SOLUSDT"
    assert policy.source_symbol("BNB", 0) == "BNBUSDT"
    assert policy.source_symbol("XRP", 0) == "XRPUSDT"
    assert policy.authorization == "DATA_CONTRACT_ONLY_NO_TARGET_OR_PRODUCTION_AUTHORIZATION"


def test_daily_decision_boundary_is_exactly_midnight_utc():
    assert canonical_decision_time("2026-08-06T00:00:00Z") == datetime(
        2026, 8, 6, tzinfo=timezone.utc
    )
    with pytest.raises(DataContractError, match="exactly 00:00:00 UTC"):
        canonical_decision_time("2026-08-06T00:00:01Z")
    with pytest.raises(DataContractError, match="timezone-aware UTC"):
        canonical_decision_time("2026-08-06T00:00:00+02:00")


def test_in_progress_daily_candle_is_excluded_at_decision_boundary():
    policy = load_data_contract()
    parsed = canonicalize_binance_daily_rows(
        asset="XRP",
        source_symbol="XRPUSDT",
        rows=[kline(1, 1.0), kline(2, 1.1), kline(3, 999)],
        decision_timestamp=datetime.fromtimestamp(3 * DAY_MS / 1000, tz=timezone.utc),
        policy=policy,
    )
    assert [row.session_open_ms for row in parsed] == [DAY_MS, 2 * DAY_MS]
    assert [row.close for row in parsed] == [1.0, 1.1]


def test_daily_kline_must_have_midnight_open_expected_close_and_positive_price():
    policy = load_data_contract()
    decision = datetime.fromtimestamp(3 * DAY_MS / 1000, tz=timezone.utc)

    bad_open = kline(1, 100)
    bad_open[0] += 1
    with pytest.raises(DataContractError, match="Non-midnight"):
        canonicalize_binance_daily_rows(
            asset="BTC", source_symbol="BTCUSDT", rows=[bad_open], decision_timestamp=decision, policy=policy
        )

    bad_close_time = kline(1, 100)
    bad_close_time[6] -= 1
    with pytest.raises(DataContractError, match="close_time"):
        canonicalize_binance_daily_rows(
            asset="BTC", source_symbol="BTCUSDT", rows=[bad_close_time], decision_timestamp=decision, policy=policy
        )

    with pytest.raises(DataContractError, match="finite and positive"):
        canonicalize_binance_daily_rows(
            asset="BTC", source_symbol="BTCUSDT", rows=[kline(1, 0)], decision_timestamp=decision, policy=policy
        )


def test_source_mapping_is_explicit_and_wrong_symbol_fails_closed():
    policy = load_data_contract()
    decision = datetime.fromtimestamp(3 * DAY_MS / 1000, tz=timezone.utc)
    with pytest.raises(DataContractError, match="does not match canonical mapping"):
        canonicalize_binance_daily_rows(
            asset="XRP",
            source_symbol="XRPUSD",
            rows=[kline(1, 1.0)],
            decision_timestamp=decision,
            policy=policy,
        )


def test_strategy_dataset_requires_target_and_feature_only_series():
    policy = load_data_contract()
    days = list(range(1, 6))
    decision = datetime.fromtimestamp(6 * DAY_MS / 1000, tz=timezone.utc)
    batches = source_batches(days)
    del batches["XRP"]
    with pytest.raises(DataContractError, match="XRP feature-only series"):
        build_canonical_daily_dataset(
            source_batches=batches,
            decision_timestamp=decision,
            policy=policy,
        )


def test_common_dataset_requires_every_day_and_never_forward_fills():
    policy = load_data_contract()
    days = list(range(1, 6))
    decision = datetime.fromtimestamp(6 * DAY_MS / 1000, tz=timezone.utc)
    batches = source_batches(days)
    symbol, rows = batches["XRP"][0]
    batches["XRP"] = [(symbol, [row for row in rows if row[0] != 3 * DAY_MS])]
    with pytest.raises(DataContractError, match="forward-fill is forbidden"):
        build_canonical_daily_dataset(
            source_batches=batches,
            decision_timestamp=decision,
            policy=policy,
        )


def test_latest_required_session_must_exist_for_every_strategy_signal_asset():
    policy = load_data_contract()
    days = list(range(1, 6))
    decision = datetime.fromtimestamp(6 * DAY_MS / 1000, tz=timezone.utc)
    batches = source_batches(days)
    symbol, rows = batches["XRP"][0]
    batches["XRP"] = [(symbol, rows[:-1])]
    with pytest.raises(DataContractError, match="Latest required UTC session is missing"):
        build_canonical_daily_dataset(
            source_batches=batches,
            decision_timestamp=decision,
            policy=policy,
        )


def test_research_live_canonical_payload_is_order_independent_and_byte_reproducible():
    policy = load_data_contract()
    days = list(range(1, 245))
    decision = datetime.fromtimestamp(245 * DAY_MS / 1000, tz=timezone.utc)
    research = build_canonical_daily_dataset(
        source_batches=source_batches(days, reverse=False),
        decision_timestamp=decision,
        policy=policy,
    )
    live = build_canonical_daily_dataset(
        source_batches=source_batches(days, reverse=True),
        decision_timestamp=decision,
        policy=policy,
    )
    assert research.canonical_json() == live.canonical_json()
    assert research.digest() == live.digest()
    assert canonical_digest(research) == canonical_digest(live)
    assert research.to_dict()["target_assets"] == list(CANONICAL_ASSETS)
    assert research.to_dict()["feature_assets"] == ["XRP"]
    assert len(research.close_values("XRP")) == len(research.close_values("BTC"))

    research_signal = build_signal(research.close_values("BTC"), funding_apr=0.0)
    live_signal = build_signal(live.close_values("BTC"), funding_apr=0.0)
    assert research_signal.to_dict() == live_signal.to_dict()


def funding_records(as_of_ms: int, *, rate=0.00001):
    latest = ((as_of_ms - 1) // HOUR_MS) * HOUR_MS
    return [
        {"time": latest - offset * HOUR_MS, "fundingRate": str(rate + offset * 0.0000001)}
        for offset in range(24)
    ]


def test_funding_contract_uses_exact_completed_24h_slots_and_bps_per_hour():
    policy = load_data_contract()
    as_of = "2026-08-06T00:00:00Z"
    as_of_ms = int(datetime(2026, 8, 6, tzinfo=timezone.utc).timestamp() * 1000)
    records = funding_records(as_of_ms)
    records.append({"time": as_of_ms, "fundingRate": "0.99"})
    canonical = canonicalize_funding_history(
        asset="BTC", records=reversed(records), router_as_of=as_of, policy=policy
    )
    assert canonical.window_hours == 24
    assert len(canonical.rates_bps_per_hour) == 24
    assert canonical.rates_bps_per_hour[-1] == pytest.approx(0.1)
    assert canonical.average_bps_per_hour == pytest.approx(
        sum(canonical.rates_bps_per_hour) / 24
    )


def test_missing_funding_hour_fails_closed():
    policy = load_data_contract()
    as_of = datetime(2026, 8, 6, tzinfo=timezone.utc)
    as_of_ms = int(as_of.timestamp() * 1000)
    records = funding_records(as_of_ms)
    records.pop(7)
    with pytest.raises(DataContractError, match="Missing completed funding slot"):
        canonicalize_funding_history(
            asset="ETH", records=records, router_as_of=as_of, policy=policy
        )


def test_feature_only_xrp_is_never_router_eligible():
    policy = load_data_contract()
    as_of = datetime(2026, 8, 6, tzinfo=timezone.utc)
    as_of_ms = int(as_of.timestamp() * 1000)
    with pytest.raises(DataContractError, match="outside canonical BRRK universe"):
        canonicalize_funding_history(
            asset="XRP", records=funding_records(as_of_ms), router_as_of=as_of, policy=policy
        )
    with pytest.raises(DataContractError, match="outside canonical BRRK universe"):
        canonicalize_basis_input(
            asset="XRP",
            perp_mark_price=1.0,
            verified_spot_price=1.0,
            perp_observed_at_ms=as_of_ms,
            spot_observed_at_ms=as_of_ms,
            router_as_of=as_of,
        )


def test_basis_contract_is_deterministic_and_preserves_observation_skew():
    as_of = datetime(2026, 8, 6, tzinfo=timezone.utc)
    as_of_ms = int(as_of.timestamp() * 1000)
    canonical = canonicalize_basis_input(
        asset="SOL",
        perp_mark_price=101.0,
        verified_spot_price=100.0,
        perp_observed_at_ms=as_of_ms - 1200,
        spot_observed_at_ms=as_of_ms - 800,
        router_as_of=as_of,
    )
    assert canonical.basis_bps == pytest.approx(100.0)
    assert canonical.observation_skew_ms == 400

    with pytest.raises(DataContractError, match="after router_as_of"):
        canonicalize_basis_input(
            asset="SOL",
            perp_mark_price=101.0,
            verified_spot_price=100.0,
            perp_observed_at_ms=as_of_ms + 1,
            spot_observed_at_ms=as_of_ms,
            router_as_of=as_of,
        )
