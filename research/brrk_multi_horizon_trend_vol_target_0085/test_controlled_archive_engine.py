from __future__ import annotations

from datetime import date, timedelta
from io import BytesIO
from types import SimpleNamespace
import zipfile

import pytest

from research.brrk_multi_horizon_trend_vol_target_0085.controlled_archive_engine import (
    ControlledArchiveTrendEngine,
    normalize_controlled_sources,
)


def _monthly_zip(symbol: str, month: str, rows: list[tuple[date, float]]) -> bytes:
    csv_rows = ["open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore"]
    for day, close in rows:
        open_ms = int(day.strftime("%s")) * 1000
        csv_rows.append(f"{open_ms},{close},{close},{close},{close},1,{open_ms + 86399999},1,1,1,1,0")
    payload = ("\n".join(csv_rows) + "\n").encode("utf-8")
    out = BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{symbol}-1d-{month}.csv", payload)
    return out.getvalue()


def _source_name(symbol: str, month: str, *, artifact_member: bool = False) -> str:
    prefix = "payloads/" if artifact_member else "stage/payloads/"
    return (
        prefix
        + "data__futures__um__monthly__klines__"
        + f"{symbol}__1d__{symbol}-1d-{month}.zip"
    )


def _synthetic_sources(days: int = 1000, *, artifact_member: bool = False) -> dict[str, bytes]:
    start = date(2023, 1, 1)
    by_month: dict[str, list[date]] = {}
    for offset in range(days):
        day = start + timedelta(days=offset)
        by_month.setdefault(day.strftime("%Y-%m"), []).append(day)

    sources: dict[str, bytes] = {}
    for asset_i, symbol in enumerate(("BTCUSDT", "ETHUSDT", "SOLUSDT"), start=1):
        for month, month_days in by_month.items():
            rows = []
            for day in month_days:
                absolute = (day - start).days
                close = 100.0 * asset_i * (1.0 + 0.0008 * absolute + 0.002 * ((absolute + asset_i) % 11))
                rows.append((day, close))
            sources[_source_name(symbol, month, artifact_member=artifact_member)] = _monthly_zip(symbol, month, rows)
    return sources


def test_adapter_normalizes_exact_three_assets_and_runs_frozen_engine():
    sources = _synthetic_sources()
    normalized = normalize_controlled_sources(sources)
    assert set(normalized) == {"btc_daily.json", "eth_daily.json", "sol_daily.json"}

    result = ControlledArchiveTrendEngine().execute(SimpleNamespace(sources=sources))
    assert result["execution_valid"] is True
    assert result["classification"] in {
        "PASS_TREND_SLEEVE_DEVELOPMENT_SUPPORT",
        "FAIL_NO_ROBUST_TREND_SLEEVE_VALUE",
        "INCONCLUSIVE_INSUFFICIENT_SUPPORT",
    }
    assert result["support_sessions"] >= 730


def test_adapter_accepts_github_artifact_member_namespace():
    sources = _synthetic_sources(artifact_member=True)
    normalized = normalize_controlled_sources(sources)
    assert set(normalized) == {"btc_daily.json", "eth_daily.json", "sol_daily.json"}

    result = ControlledArchiveTrendEngine().execute(SimpleNamespace(sources=sources))
    assert result["execution_valid"] is True
    assert result["classification"] in {
        "PASS_TREND_SLEEVE_DEVELOPMENT_SUPPORT",
        "FAIL_NO_ROBUST_TREND_SLEEVE_VALUE",
        "INCONCLUSIVE_INSUFFICIENT_SUPPORT",
    }


def test_adapter_rejects_funding_or_unknown_source():
    sources = _synthetic_sources(days=10)
    sources[
        "stage/payloads/data__futures__um__monthly__fundingRate__BTCUSDT__BTCUSDT-fundingRate-2023-01.zip"
    ] = b"not-used"
    with pytest.raises(Exception, match="UNKNOWN_CONTROLLED_SOURCE"):
        normalize_controlled_sources(sources)


def test_adapter_rejects_corrupt_inner_zip():
    sources = _synthetic_sources(days=10)
    first = next(iter(sources))
    sources[first] = b"corrupt"
    with pytest.raises(Exception, match="INVALID_INNER_ZIP"):
        normalize_controlled_sources(sources)


def test_controlled_engine_propagates_adapter_failure_to_common_runner():
    sources = _synthetic_sources(days=10)
    first = next(iter(sources))
    sources[first] = b"corrupt"
    with pytest.raises(Exception, match="INVALID_INNER_ZIP"):
        ControlledArchiveTrendEngine().execute(SimpleNamespace(sources=sources))


def test_adapter_rejects_duplicate_asset_month_identity():
    sources = _synthetic_sources(days=10)
    original = _source_name("BTCUSDT", "2023-01")
    sources[original.replace("stage/payloads/", "alias/")] = sources[original]
    with pytest.raises(Exception, match="UNKNOWN_CONTROLLED_SOURCE"):
        normalize_controlled_sources(sources)


def test_adapter_rejects_duplicate_month_across_staging_and_artifact_namespaces():
    sources = _synthetic_sources(days=10)
    original = _source_name("BTCUSDT", "2023-01")
    sources[original.replace("stage/payloads/", "payloads/")] = sources[original]
    with pytest.raises(Exception, match="DUPLICATE_KLINE_MONTH"):
        normalize_controlled_sources(sources)


def test_adapter_rejects_month_mismatch_inside_zip():
    sources = _synthetic_sources(days=10)
    wrong_name = _source_name("BTCUSDT", "2023-01")
    sources[wrong_name] = _monthly_zip("BTCUSDT", "2023-01", [(date(2023, 2, 1), 100.0)])
    with pytest.raises(Exception, match="KLINE_MONTH_MISMATCH"):
        normalize_controlled_sources(sources)
