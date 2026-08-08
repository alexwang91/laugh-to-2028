from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from research.stablecoin_liquidity_0001.capture_once import (
    CaptureGateError,
    CaptureMetadata,
    execute_first_history_capture,
    validate_capture_gate_contract,
)
from research.stablecoin_liquidity_0001.raw_vintage import HttpCapture, sha256_bytes


def _ts(value: datetime) -> str:
    return str(int(value.timestamp()))


def _payload(rows: list[tuple[datetime, float]]) -> bytes:
    return json.dumps(
        [
            {
                "date": _ts(timestamp),
                "totalCirculatingUSD": {"peggedUSD": value},
            }
            for timestamp, value in rows
        ],
        separators=(",", ":"),
    ).encode("utf-8")


def _capture(raw: bytes) -> HttpCapture:
    started = datetime(2026, 8, 8, 13, 30, 0, tzinfo=timezone.utc)
    return HttpCapture(
        raw_bytes=raw,
        retrieval_started_at=started,
        retrieved_at=started + timedelta(seconds=1),
        http_status=200,
        response_headers={"Content-Type": "application/json", "ETag": "fixture"},
    )


class CaptureGateTests(unittest.TestCase):
    def test_gate_contract_identity(self) -> None:
        validate_capture_gate_contract()

    def test_storage_root_inside_repo_is_rejected_before_fetch(self) -> None:
        calls = 0

        def fetcher() -> HttpCapture:
            nonlocal calls
            calls += 1
            return _capture(b"[]")

        repo_inside = Path(__file__).resolve().parent / "raw_vintage"
        with self.assertRaisesRegex(CaptureGateError, "outside the repository"):
            execute_first_history_capture(repo_inside, fetcher=fetcher)
        self.assertEqual(calls, 0)

    def test_first_capture_persists_verifies_then_emits_metadata_only(self) -> None:
        before = datetime(2026, 7, 19, tzinfo=timezone.utc)
        cutoff = datetime(2026, 8, 8, tzinfo=timezone.utc)
        after = datetime(2026, 8, 9, tzinfo=timezone.utc)
        raw = _payload([(after, 130.0), (before, 100.0), (cutoff, 120.0)])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            metadata = execute_first_history_capture(root, fetcher=lambda: _capture(raw))

            self.assertIsInstance(metadata, CaptureMetadata)
            self.assertEqual(metadata.raw_sha256, sha256_bytes(raw))
            self.assertEqual(metadata.raw_row_count, 3)
            self.assertEqual(metadata.historical_row_count, 2)
            self.assertEqual(metadata.historical_start, "2026-07-19T00:00:00Z")
            self.assertEqual(metadata.historical_end, "2026-08-08T00:00:00Z")
            self.assertEqual(metadata.research_result_status, "NO_RESEARCH_RESULT_CAPTURE_METADATA_ONLY")

            raw_path = root / metadata.raw_relative_path
            manifest_path = root / metadata.manifest_relative_path
            self.assertEqual(raw_path.read_bytes(), raw)
            self.assertTrue(manifest_path.exists())

            emitted = metadata.as_dict()
            self.assertEqual(set(emitted), set(CaptureMetadata.__dataclass_fields__))
            forbidden_fragments = {"values", "features", "predictions", "signals", "performance", "equity_curve"}
            self.assertTrue(forbidden_fragments.isdisjoint(emitted))

    def test_schema_failure_occurs_after_raw_and_manifest_are_preserved(self) -> None:
        invalid = json.dumps([{"date": "1786147200", "totalCirculatingUSD": {}}]).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with self.assertRaisesRegex(ValueError, "peggedUSD"):
                execute_first_history_capture(root, fetcher=lambda: _capture(invalid))
            files = [path for path in root.rglob("*") if path.is_file()]
            self.assertEqual(len(files), 2)
            self.assertTrue(any(path.name.endswith(".manifest.json") for path in files))

    def test_existing_capture_artifact_blocks_second_fetch(self) -> None:
        metric = datetime(2026, 8, 8, tzinfo=timezone.utc)
        raw = _payload([(metric, 100.0)])
        calls = 0

        def fetcher() -> HttpCapture:
            nonlocal calls
            calls += 1
            return _capture(raw)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            execute_first_history_capture(root, fetcher=fetcher)
            self.assertEqual(calls, 1)
            with self.assertRaisesRegex(CaptureGateError, "existing first-capture artifact"):
                execute_first_history_capture(root, fetcher=fetcher)
            self.assertEqual(calls, 1)

    def test_no_historical_rows_is_fail_closed_after_preservation(self) -> None:
        after = datetime(2026, 8, 9, tzinfo=timezone.utc)
        raw = _payload([(after, 100.0)])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with self.assertRaisesRegex(CaptureGateError, "no rows inside frozen historical coverage"):
                execute_first_history_capture(root, fetcher=lambda: _capture(raw))
            self.assertEqual(len([p for p in root.rglob("*") if p.is_file()]), 2)


if __name__ == "__main__":
    unittest.main()
