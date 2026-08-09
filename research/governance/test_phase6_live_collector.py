from __future__ import annotations

import ast
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from research.governance.phase6_live_collector import (
    BACKEND_ID,
    RETENTION_DAYS,
    decision_slug,
    decision_timestamp_for_observation,
    finalize_receipt,
)


ROOT = Path(__file__).resolve().parents[2]


class Phase6LiveCollectorTests(unittest.TestCase):
    def test_observation_maps_to_same_day_utc_canonical_decision(self) -> None:
        observed = datetime(2026, 8, 10, 0, 17, 42, tzinfo=timezone.utc)
        decision = decision_timestamp_for_observation(observed)
        self.assertEqual(decision.isoformat(), "2026-08-10T00:00:00+00:00")
        self.assertEqual(decision_slug("2026-08-10T00:00:00Z"), "20260810T000000Z")

    def test_receipt_binds_evidence_artifact_and_required_phase6_digests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "evidence"
            evidence.mkdir()
            metadata = {
                "github_run_id": "123",
                "github_run_attempt": "1",
                "workflow_sha": "a" * 40,
                "decision_timestamp": "2026-08-10T00:00:00Z",
                "observed_at": "2026-08-10T00:17:00Z",
                "shadow_record_digest": "b" * 64,
                "input_provenance_digest": "c" * 64,
                "evidence_object_digest": "d" * 64,
                "scheduled_decision_credit_candidate": True,
                "emergency_drill_candidate": False,
            }
            (evidence / "evidence_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
            output = root / "receipt" / "receipt.json"
            receipt = finalize_receipt(
                evidence_dir=evidence,
                output_path=output,
                artifact_id="456",
                artifact_url="https://github.example/artifacts/456",
                artifact_digest="e" * 64,
            )
            self.assertEqual(receipt["backend_id"], BACKEND_ID)
            self.assertEqual(receipt["retention_days"], RETENTION_DAYS)
            self.assertEqual(receipt["evidence_artifact_id"], "456")
            self.assertTrue(receipt["scheduled_decision_credit_candidate"])
            self.assertTrue(receipt["credit_requires_this_receipt_artifact_upload_success"])
            self.assertFalse(receipt["production_authorized"])

    def test_collector_has_no_signer_executor_or_submission_import_path(self) -> None:
        path = ROOT / "research/governance/phase6_live_collector.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module or "")
        forbidden_imports = {
            "beta_bot.executor",
            "hyperliquid.exchange",
            "eth_account",
            "web3",
        }
        self.assertTrue(imports.isdisjoint(forbidden_imports), imports)
        source = path.read_text(encoding="utf-8")
        forbidden_calls = (
            "execute_target_position(",
            "submit_order(",
            "sign_order(",
            "withdraw(",
            "transfer(",
        )
        for fragment in forbidden_calls:
            self.assertNotIn(fragment, source)


if __name__ == "__main__":
    unittest.main()
