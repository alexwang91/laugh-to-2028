from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from research.stablecoin_liquidity_0001.data_contract import (
    HISTORICAL_CUTOFF_UTC,
    exact_lag_value,
    historical_available_at,
    parse_source_payload,
    select_frozen_historical_coverage,
    validate_frozen_contract,
)
from research.stablecoin_liquidity_0001.raw_vintage import (
    HttpCapture,
    verify_snapshot,
    write_snapshot,
)


def _ts(value: datetime) -> str:
    return str(int(value.timestamp()))


def _payload(rows: list[tuple[datetime, float]]) -> bytes:
    return json.dumps(
        [
            {
                "date": _ts(timestamp),
                "totalCirculating": {"peggedUSD": value},
                "totalCirculatingUSD": {"peggedUSD": value},
                "futureUnknownField": {"preservedOnlyInRaw": True},
            }
            for timestamp, value in rows
        ],
        separators=(",", ":"),
    ).encode("utf-8")


class DataContractTests(unittest.TestCase):
    def test_frozen_contract_identity(self) -> None:
        validate_frozen_contract()

    def test_parse_and_frozen_coverage_use_all_valid_rows_through_cutoff(self) -> None:
        before = HISTORICAL_CUTOFF_UTC - timedelta(days=20)
        at_cutoff = HISTORICAL_CUTOFF_UTC
        after = HISTORICAL_CUTOFF_UTC + timedelta(days=1)
        points = parse_source_payload(_payload([(after, 130.0), (before, 100.0), (at_cutoff, 120.0)]))
        selected = select_frozen_historical_coverage(points)
        self.assertEqual([p.metric_timestamp for p in selected], [before, at_cutoff])

    def test_historical_availability_is_exactly_lag_2d(self) -> None:
        metric = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(historical_available_at(metric), datetime(2026, 1, 3, tzinfo=timezone.utc))

    def test_duplicate_metric_timestamp_is_hard_failure(self) -> None:
        metric = datetime(2026, 1, 1, tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError, "duplicate metric timestamp"):
            parse_source_payload(_payload([(metric, 100.0), (metric, 101.0)]))

    def test_missing_primary_field_is_hard_failure(self) -> None:
        raw = json.dumps([{"date": "1767225600", "totalCirculatingUSD": {}}]).encode("utf-8")
        with self.assertRaisesRegex(ValueError, "peggedUSD"):
            parse_source_payload(raw)

    def test_exact_lag_does_not_interpolate(self) -> None:
        t = datetime(2026, 2, 10, tzinfo=timezone.utc)
        points = parse_source_payload(_payload([(t, 120.0), (t - timedelta(days=19), 100.0)]))
        self.assertIsNone(exact_lag_value(points, t, 20))

    def test_raw_snapshot_is_create_only_and_hash_verified(self) -> None:
        started = datetime(2026, 8, 8, 13, 0, 0, tzinfo=timezone.utc)
        retrieved = started + timedelta(seconds=1)
        capture = HttpCapture(
            raw_bytes=_payload([(datetime(2026, 8, 8, tzinfo=timezone.utc), 100.0)]),
            retrieval_started_at=started,
            retrieved_at=retrieved,
            http_status=200,
            response_headers={"Content-Type": "application/json", "ETag": "fixture-etag"},
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = write_snapshot(root, capture)
            manifest = verify_snapshot(paths)
            self.assertEqual(manifest["response_headers"]["etag"], "fixture-etag")
            with self.assertRaises(FileExistsError):
                write_snapshot(root, capture)

    def test_tampered_raw_snapshot_fails_verification(self) -> None:
        started = datetime(2026, 8, 8, 13, 0, 0, tzinfo=timezone.utc)
        capture = HttpCapture(
            raw_bytes=b"[]",
            retrieval_started_at=started,
            retrieved_at=started + timedelta(seconds=1),
            http_status=200,
            response_headers={"Content-Type": "application/json"},
        )
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_snapshot(Path(tmp), capture)
            paths.raw_path.chmod(0o644)
            paths.raw_path.write_bytes(b"[{}]")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                verify_snapshot(paths)

    def test_non_200_capture_cannot_be_persisted(self) -> None:
        started = datetime(2026, 8, 8, 13, 0, 0, tzinfo=timezone.utc)
        capture = HttpCapture(
            raw_bytes=b"{}",
            retrieval_started_at=started,
            retrieved_at=started,
            http_status=500,
            response_headers={},
        )
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "non-200"):
                write_snapshot(Path(tmp), capture)


if __name__ == "__main__":
    unittest.main()
