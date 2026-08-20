from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("capture_wiring_0002_fixed", HERE / "capture_wiring_0002_fixed.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def _iso(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def test_validate_contract_uses_canonical_contract_id_without_network():
    plan = mod.base.validate_contract(git=False)
    assert plan["capture_request_id"] == mod.base.CID
    assert plan["network_object_count_total"] == 30


def test_spot_2026_microsecond_timestamp_is_decoded_as_microseconds():
    lo_us = 1782864000000000
    hi_us = 1782864060000000
    lo, hi = mod._timestamp_bounds([[str(lo_us)]], mod.SPOT_FAMILY)
    assert lo == _iso(lo_us / 1_000_000)
    assert hi == _iso(lo_us / 1_000_000)
    lo2, hi2 = mod._timestamp_bounds([[str(lo_us)], [str(hi_us)]], mod.SPOT_FAMILY)
    assert lo2 == _iso(lo_us / 1_000_000)
    assert hi2 == _iso(hi_us / 1_000_000)


def test_usdm_2026_timestamp_is_decoded_as_milliseconds():
    lo_ms = 1782864000000
    hi_ms = 1782864060000
    family = "futures/um/monthly/klines"
    lo, hi = mod._timestamp_bounds([[str(lo_ms)], [str(hi_ms)]], family)
    assert lo == _iso(lo_ms / 1_000)
    assert hi == _iso(hi_ms / 1_000)


def test_spot_millisecond_unit_fails_closed():
    try:
        mod._timestamp_bounds([["1782864000000"]], mod.SPOT_FAMILY)
    except mod.base.CaptureError as exc:
        assert str(exc) == "TIMESTAMP_UNIT_DRIFT"
    else:
        raise AssertionError("spot millisecond drift must fail closed")


def test_usdm_microsecond_unit_fails_closed():
    try:
        mod._timestamp_bounds([["1782864000000000"]], "futures/um/monthly/klines")
    except mod.base.CaptureError as exc:
        assert str(exc) == "TIMESTAMP_UNIT_DRIFT"
    else:
        raise AssertionError("USD-M microsecond drift must fail closed")


def test_no_stage8_or_researcher_read_budget_change():
    request = mod.base.load(HERE / "CAPTURE_REQUEST_0002.json")
    assert request["stage8_attempt_consumed"] == 0
    assert request["controlled_scientific_history_reads_to_researcher"] == 0
