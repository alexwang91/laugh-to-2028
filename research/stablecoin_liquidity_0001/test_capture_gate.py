from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from research.stablecoin_liquidity_0001.capture_once import (
    CaptureGateError,
    CaptureMetadata,
    CaptureStagingMetadata,
    capture_and_persist_first_history,
    finalize_after_durable_copy,
    validate_capture_gate_contract,
    write_durability_receipt,
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


def _receipt(root: Path, staging: CaptureStagingMetadata) -> Path:
    path = root / "durability-receipt.json"
    return write_durability_receipt(
        path,
        staging,
        durable_backend="TEST_VERSIONED_STORE",
        durable_raw_ref="version://raw/1",
        durable_manifest_ref="version://manifest/1",
        archived_at="2026-08-08T13:31:00Z",
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
            capture_and_persist_first_history(repo_inside, fetcher=fetcher)
        self.assertEqual(calls, 0)

    def test_capture_stage_stops_before_parsing(self) -> None:
        invalid = json.dumps([{"date": "1786147200", "totalCirculatingUSD": {}}]).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            staging = capture_and_persist_first_history(root, fetcher=lambda: _capture(invalid))
            self.assertIsInstance(staging, CaptureStagingMetadata)
            self.assertEqual(staging.raw_sha256, sha256_bytes(invalid))
            self.assertEqual(staging.state, "PERSISTED_VERIFIED_AWAITING_DURABLE_RECEIPT")
            self.assertEqual(len([p for p in root.rglob("*") if p.is_file()]), 2)

    def test_finalize_requires_matching_durability_receipt_before_parse(self) -> None:
        invalid = json.dumps([{"date": "1786147200", "totalCirculatingUSD": {}}]).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            staging = capture_and_persist_first_history(root, fetcher=lambda: _capture(invalid))
            receipt_path = _receipt(root, staging)
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["raw_sha256"] = "0" * 64
            receipt_path.chmod(0o644)
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(CaptureGateError, "raw_sha256 mismatch"):
                finalize_after_durable_copy(root, staging, receipt_path)

    def test_valid_finalize_emits_metadata_only(self) -> None:
        before = datetime(2026, 7, 19, tzinfo=timezone.utc)
        cutoff = datetime(2026, 8, 8, tzinfo=timezone.utc)
        after = datetime(2026, 8, 9, tzinfo=timezone.utc)
        raw = _payload([(after, 130.0), (before, 100.0), (cutoff, 120.0)])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            staging = capture_and_persist_first_history(root, fetcher=lambda: _capture(raw))
            metadata = finalize_after_durable_copy(root, staging, _receipt(root, staging))

            self.assertIsInstance(metadata, CaptureMetadata)
            self.assertEqual(metadata.raw_sha256, sha256_bytes(raw))
            self.assertEqual(metadata.raw_row_count, 3)
            self.assertEqual(metadata.historical_row_count, 2)
            self.assertEqual(metadata.historical_start, "2026-07-19T00:00:00Z")
            self.assertEqual(metadata.historical_end, "2026-08-08T00:00:00Z")
            self.assertEqual(metadata.durable_backend, "TEST_VERSIONED_STORE")
            self.assertEqual(metadata.research_result_status, "NO_RESEARCH_RESULT_CAPTURE_METADATA_ONLY")

            emitted = metadata.as_dict()
            self.assertEqual(set(emitted), set(CaptureMetadata.__dataclass_fields__))
            forbidden_fragments = {"values", "features", "predictions", "signals", "performance", "equity_curve"}
            self.assertTrue(forbidden_fragments.isdisjoint(emitted))

    def test_schema_failure_happens_only_after_durable_receipt(self) -> None:
        invalid = json.dumps([{"date": "1786147200", "totalCirculatingUSD": {}}]).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            staging = capture_and_persist_first_history(root, fetcher=lambda: _capture(invalid))
            with self.assertRaisesRegex(ValueError, "peggedUSD"):
                finalize_after_durable_copy(root, staging, _receipt(root, staging))
            self.assertEqual(len([p for p in root.rglob("*") if p.is_file()]), 3)

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
            capture_and_persist_first_history(root, fetcher=fetcher)
            self.assertEqual(calls, 1)
            with self.assertRaisesRegex(CaptureGateError, "existing first-capture artifact"):
                capture_and_persist_first_history(root, fetcher=fetcher)
            self.assertEqual(calls, 1)

    def test_no_historical_rows_is_fail_closed_after_durable_receipt(self) -> None:
        after = datetime(2026, 8, 9, tzinfo=timezone.utc)
        raw = _payload([(after, 100.0)])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            staging = capture_and_persist_first_history(root, fetcher=lambda: _capture(raw))
            with self.assertRaisesRegex(CaptureGateError, "no rows inside frozen historical coverage"):
                finalize_after_durable_copy(root, staging, _receipt(root, staging))

    def test_receipt_is_create_only(self) -> None:
        metric = datetime(2026, 8, 8, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            staging = capture_and_persist_first_history(root, fetcher=lambda: _capture(_payload([(metric, 100.0)])))
            receipt_path = _receipt(root, staging)
            self.assertTrue(receipt_path.exists())
            with self.assertRaises(FileExistsError):
                _receipt(root, staging)


if __name__ == "__main__":
    unittest.main()
